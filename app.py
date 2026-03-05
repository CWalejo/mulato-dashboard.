import streamlit as st
import pandas as pd
import psycopg2

# 1. Configuración de la Página
st.set_page_config(page_title="El Mulato - Sistema de Gestión", layout="wide")

# URL de Conexión (Rama: Actualización de nombres y clave)
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
st.sidebar.title("🏢 El Mulato")
opcion = st.sidebar.radio("Navegación:", 
    ["📈 Historial de Ventas", "🍳 Recetas", "📦 Maestro de Insumos", "🚨 Tablero de Control"])

# --- SECCIÓN 1: HISTORIAL DE VENTAS ---
if opcion == "📈 Historial de Ventas":
    st.header("📈 Historial de Ventas")
    df_ventas = consultar_neon("SELECT * FROM historial_ventas ORDER BY id ASC")
    if df_ventas is not None:
        st.metric("Total Registros en Neon", len(df_ventas))
        st.dataframe(df_ventas, use_container_width=True, hide_index=True, height=500)

# --- SECCIÓN 2: RECETAS ---
elif opcion == "🍳 Recetas":
    st.header("🍳 Libro de Recetas")
    # Consulta simple para evitar errores de nombres de columnas
    df_recetas = consultar_neon("SELECT * FROM recetas")
    if df_recetas is not None:
        if df_recetas.empty:
            st.info("No hay recetas registradas todavía.")
        else:
            st.write(f"📖 Total recetas: {len(df_recetas)}")
            st.dataframe(df_recetas, use_container_width=True, hide_index=True)

# --- SECCIÓN 3: MAESTRO DE INSUMOS ---
elif opcion == "📦 Maestro de Insumos":
    st.header("📦 Maestro de Insumos")
    df_maestro = consultar_neon("SELECT * FROM maestro_insumos ORDER BY producto ASC")
    if df_maestro is not None:
        st.write(f"📦 Productos en inventario: {len(df_maestro)}")
        st.dataframe(df_maestro, use_container_width=True, hide_index=True, height=500)

# --- SECCIÓN 4: TABLERO DE CONTROL (Sincronizado con Neon) ---
elif opcion == "🚨 Tablero de Control":
    st.header("🚨 Tablero de Gestión")
    
    # Traemos la tabla que ya tiene los cálculos de alertas y sugeridos
    df_tablero = consultar_neon("SELECT * FROM tablero_control")
    
    if df_tablero is not None:
        # Contadores rápidos para el resumen
        # Buscamos los emojis o textos que usas en Neon para las alertas
        criticos = len(df_tablero[df_tablero['alerta'].str.contains("🔴|CRÍTICO", na=False)])
        pedir = len(df_tablero[df_tablero['alerta'].str.contains("🟡|PEDIR", na=False)])
        
        c1, c2, c3 = st.columns(3)
        c1.metric("🔴 Alertas Críticas", criticos)
        c2.metric("🟡 Pedidos Pendientes", pedir)
        c3.success("Sincronización OK")

        # Mostramos la tabla tal cual está en tu Neon
        st.dataframe(
            df_tablero, 
            use_container_width=True, 
            hide_index=True,
            column_order=("producto", "stock_actual", "venta_real", "alerta", "pedido_sugerido")
        )
    else:
        st.error("No se pudo cargar la tabla de control. Revisa que 'tablero_control' exista en Neon.")

# --- PIE DE PÁGINA ---
st.sidebar.markdown("---")
if st.sidebar.button("Cerrar Sesión"):
    st.session_state['autenticado'] = False
    st.rerun()
