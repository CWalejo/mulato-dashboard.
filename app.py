import streamlit as st
import pandas as pd
import psycopg2

# 1. Configuración de la Página
st.set_page_config(page_title="El Mulato - Gestión Total", layout="wide")

# URL de Conexión (Rama: ep-solitary-cake-ai8g7c0x)
DB_URL = "postgresql://neondb_owner:npg_2YMloHQwec0b@ep-solitary-cake-ai8g7c0x-pooler.c-4.us-east-1.aws.neon.tech/neondb?sslmode=require"

def consultar_neon(query):
    try:
        conn = psycopg2.connect(DB_URL)
        df = pd.read_sql(query, conn)
        conn.close()
        return df
    except Exception as e:
        st.error(f"❌ Error de conexión: {e}")
        return None

# --- SEGURIDAD ---
if 'autenticado' not in st.session_state:
    st.session_state['autenticado'] = False

if not st.session_state['autenticado']:
    st.markdown("<h2 style='text-align: center;'>🔐 Acceso Privado - El Mulato</h2>", unsafe_allow_html=True)
    pin = st.text_input("PIN de Acceso:", type="password")
    if st.button("Ingresar"):
        if pin == "4321":
            st.session_state['autenticado'] = True
            st.rerun()
    st.stop()

# --- MENÚ LATERAL ---
st.sidebar.title("🏢 Menú El Mulato")
opcion = st.sidebar.radio("Navegación:", 
    ["📈 Historial de Ventas", "🍳 Recetas", "📦 Maestro de Insumos", "🚨 Tablero de Control"])

# --- 1. HISTORIAL ---
if opcion == "📈 Historial de Ventas":
    st.header("📈 Historial de Ventas")
    df_ventas = consultar_neon("SELECT * FROM historial_ventas ORDER BY id ASC")
    if df_ventas is not None:
        st.metric("Registros Totales", len(df_ventas))
        st.dataframe(df_ventas, use_container_width=True, hide_index=True)

# --- 2. RECETAS ---
elif opcion == "🍳 Recetas":
    st.header("🍳 Libro de Recetas")
    df_recetas = consultar_neon("SELECT * FROM recetas")
    if df_recetas is not None:
        st.dataframe(df_recetas, use_container_width=True, hide_index=True)

# --- 3. MAESTRO DE INSUMOS ---
elif opcion == "📦 Maestro de Insumos":
    st.header("📦 Maestro de Insumos")
    df_maestro = consultar_neon("SELECT * FROM maestro_insumos ORDER BY producto ASC")
    if df_maestro is not None:
        st.dataframe(df_maestro, use_container_width=True, hide_index=True)

# --- 4. TABLERO DE CONTROL (CON PROMEDIO DIARIO) ---
elif opcion == "🚨 Tablero de Control":
    st.header("🚨 Tablero de Gestión")
    
    # Traemos la tabla completa de Neon
    df_tablero = consultar_neon("SELECT * FROM tablero_control")
    
    if df_tablero is not None:
        # Métricas de resumen basadas en la columna 'alerta'
        criticos = len(df_tablero[df_tablero['alerta'].str.contains("CRÍTICO", na=False)])
        pedir = len(df_tablero[df_tablero['alerta'].str.contains("PEDIR", na=False)])
        
        c1, c2, c3 = st.columns(3)
        c1.metric("🔴 Alertas Críticas", criticos)
        c2.metric("🟡 Pedidos Pendientes", pedir)
        c3.success("Sincronización OK")

        # Mostramos la tabla con la columna de promedio diario incluida
        st.dataframe(
            df_tablero, 
            use_container_width=True, 
            hide_index=True,
            column_order=(
                "producto", 
                "stock_actual", 
                "promedio_venta_diario", # <--- Columna agregada
                "venta_real", 
                "alerta", 
                "pedido_sugerido"
            )
        )
    else:
        st.error("No se pudo cargar la tabla 'tablero_control'.")

# --- CIERRE ---
st.sidebar.markdown("---")
if st.sidebar.button("Cerrar Sesión"):
    st.session_state['autenticado'] = False
    st.rerun()
