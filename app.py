import streamlit as st
import pandas as pd
import psycopg2

# 1. Configuración de la página
st.set_page_config(page_title="El Mulato - Sistema Inteligente", layout="wide")
DB_URL = "postgresql://neondb_owner:npg_2YMloHQwec0b@ep-lucky-cloud-aihu085f-pooler.c-4.us-east-1.aws.neon.tech/neondb?sslmode=require"

def cargar_datos(query):
    try:
        conn = psycopg2.connect(DB_URL)
        df = pd.read_sql(query, conn)
        conn.close()
        return df
    except Exception as e:
        st.error(f"Error: {e}")
        return None

# --- SEGURIDAD ---
if 'autenticado' not in st.session_state:
    st.session_state['autenticado'] = False

if not st.session_state['autenticado']:
    st.markdown("<h2 style='text-align: center;'>🔐 Acceso Privado - El Mulato</h2>", unsafe_allow_html=True)
    pin = st.text_input("PIN:", type="password")
    if st.button("Ingresar"):
        if pin == "4321":
            st.session_state['autenticado'] = True
            st.rerun()
    st.stop()

# --- MENÚ ---
st.sidebar.title("Menú El Mulato")
opcion = st.sidebar.radio("Sección:", ["📈 Historial", "🍳 Recetas", "📦 Inventario", "🚨 Tablero", "🔄 Soft Restaurant", "🤖 Copiloto IA"])

# --- PÁGINA: HISTORIAL (CARGA TOTAL) ---
if opcion == "📈 Historial":
    st.header("📈 Historial de Ventas")
    
    # Esta consulta no tiene filtros, trae los 144 productos de Neon
    query_hist = "SELECT producto, cantidad_vendida, fecha_inicio, fecha_fin FROM historial_ventas ORDER BY producto ASC"
    
    df = cargar_datos(query_hist)
    
    if df is not None:
        st.success(f"✅ Se han cargado los **{len(df)}** registros encontrados en la base de datos.")
        
        # Limpieza de fechas para que no se vea el "None" feo
        df['fecha_inicio'] = pd.to_datetime(df['fecha_inicio']).dt.date
        df['fecha_fin'] = pd.to_datetime(df['fecha_fin'], errors='coerce').dt.date
        
        # Tabla con scroll para ver los 144
        st.dataframe(df, use_container_width=True, hide_index=True, height=800)

# --- PÁGINA: INVENTARIO (CORREGIDO) ---
elif opcion == "📦 Inventario":
    st.header("📦 Gestión de Stock")
    
    # Cargamos el maestro completo
    df = cargar_datos("SELECT producto, categoria, stock_actual FROM maestro_insumos ORDER BY categoria, producto ASC")
    
    if df is not None:
        st.info(f"Mostrando {len(df)} productos en el maestro.")
        st.dataframe(df, use_container_width=True, hide_index=True, height=600)

# --- LAS DEMÁS PÁGINAS (SOFT RESTAURANT E IA) ---
elif opcion == "🔄 Soft Restaurant":
    st.header("🔄 Sincronización")
    st.write("Sube aquí el archivo de Soft Restaurant para actualizar los 144 registros.")
    archivo = st.file_uploader("Archivo Excel/CSV", type=['csv', 'xlsx'])

elif opcion == "🤖 Copiloto IA":
    st.header("🤖 Copiloto IA")
    st.warning("Análisis real en preparación. Por ahora, los datos están cargados correctamente en el historial.")
