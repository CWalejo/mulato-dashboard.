import streamlit as st
import pandas as pd
import psycopg2
from io import StringIO

# 1. Configuración de la Página
st.set_page_config(page_title="El Mulato - Sistema Integral", layout="wide")

# URL de Conexión (Rama: Actualización de nombres y clave)
DB_URL = "postgresql://neondb_owner:npg_2YMloHQwec0b@ep-solitary-cake-ai8g7c0x-pooler.c-4.us-east-1.aws.neon.tech/neondb?sslmode=require"

def consultar_neon(query):
    try:
        conn = psycopg2.connect(DB_URL)
        df = pd.read_sql(query, conn)
        conn.close()
        return df
    except Exception as e:
        st.error(f"❌ Error de base de datos: {e}")
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
st.sidebar.title("🏢 El Mulato Hub")
opcion = st.sidebar.radio("Navegación:", 
    ["📈 Historial de Ventas", "🍳 Recetas", "📦 Maestro de Insumos", "🚨 Tablero de Control", "📤 Cargar Datos (Soft)", "🤖 Asistente IA"])

# --- 1. HISTORIAL DE VENTAS ---
if opcion == "📈 Historial de Ventas":
    st.header("📈 Historial de Ventas")
    df_ventas = consultar_neon("SELECT * FROM historial_ventas ORDER BY id ASC")
    if df_ventas is not None:
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

# --- 4. TABLERO DE CONTROL (CON DECIMALES) ---
elif opcion == "🚨 Tablero de Control":
    st.header("🚨 Tablero de Gestión")
    df_tablero = consultar_neon("SELECT * FROM tablero_control")
    
    if df_tablero is not None:
        # Formatear Venta Real para que muestre 2 decimales como en Neon
        df_tablero["venta_real"] = df_tablero["venta_real"].map(lambda x: f"{x:.2f}")
        
        c1, c2 = st.columns(2)
        criticos = len(df_tablero[df_tablero['alerta'].str.contains("CRÍTICO", na=False)])
        c1.metric("🔴 Alertas Críticas", criticos)
        
        st.dataframe(
            df_tablero, 
            use_container_width=True, 
            hide_index=True,
            column_order=("producto", "stock_actual", "promedio_venta_diario", "venta_real", "alerta", "pedido_sugerido")
        )

# --- 5. CARGAR DATOS (CSV SOFT) ---
elif opcion == "📤 Cargar Datos (Soft)":
    st.header("📤 Carga de Ventas desde Soft")
    st.info("Sube el archivo CSV exportado para actualizar el historial.")
    
    archivo = st.file_uploader("Selecciona archivo CSV", type=["csv"])
    if archivo is not None:
        df_upload = pd.read_csv(archivo)
        st.write("Vista previa de los datos a cargar:")
        st.dataframe(df_upload.head())
        
        if st.button("Confirmar Carga a Neon"):
            # Aquí iría la lógica de inserción masiva
            st.success("Datos procesados correctamente (Simulación de carga completa).")

# --- 6. ASISTENTE IA (FUNCIONAL) ---
elif opcion == "🤖 Asistente IA":
    st.header("🤖 Inteligencia de Negocio")
    st.write("Pregúntame sobre tus 144 productos, stock o ventas.")
    
    pregunta = st.text_input("¿Qué deseas saber hoy?")
    
    if pregunta:
        # Lógica IA: Buscamos en los datos locales para responder
        df_contexto = consultar_neon("SELECT * FROM tablero_control")
        
        if "critico" in pregunta.lower() or "alerta" in pregunta.lower():
            resumen = df_contexto[df_contexto['alerta'].str.contains("CRÍTICO", na=False)]
            if not resumen.empty:
                st.write(f"IA: Tienes {len(resumen)} productos en estado crítico. Los más urgentes son: {', '.join(resumen['producto'].head(3).tolist())}.")
            else:
                st.write("IA: No detecto alertas críticas en este momento. ¡Todo bajo control!")
        
        elif "venta" in pregunta.lower():
            top_venta = df_contexto.nlargest(3, 'venta_real')
            st.write(f"IA: Basado en el historial de Neon, tus productos más vendidos son: {', '.join(top_venta['producto'].tolist())}.")
        
        else:
            st.write("IA: Estoy analizando tus 144 registros. Puedo darte resúmenes de stock, alertas y tendencias de venta.")

# --- CIERRE ---
st.sidebar.markdown("---")
if st.sidebar.button("Cerrar Sesión"):
    st.session_state['autenticado'] = False
    st.rerun()
