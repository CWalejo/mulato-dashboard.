import streamlit as st
import pandas as pd
import psycopg2

# 1. Configuración
st.set_page_config(page_title="El Mulato - Sistema Inteligente", layout="wide")
DB_URL = "postgresql://neondb_owner:npg_2YMloHQwec0b@ep-lucky-cloud-aihu085f-pooler.c-4.us-east-1.aws.neon.tech/neondb?sslmode=require"

def cargar_datos(query):
    try:
        conn = psycopg2.connect(DB_URL)
        df = pd.read_sql(query, conn)
        conn.close()
        return df
    except Exception as e:
        st.error(f"Error al conectar con Neon: {e}")
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
opcion = st.sidebar.radio("Sección:", 
    ["📈 Historial", "🍳 Recetas", "📦 Inventario", "🚨 Tablero", "🔄 Soft Restaurant", "🤖 Copiloto IA"])

# --- 1. HISTORIAL (Solo jala de historial_ventas) ---
if opcion == "📈 Historial":
    st.header("📈 Historial de Ventas")
    # Query directa a historial_ventas. Sin JOINs, sin filtros.
    df = cargar_datos("SELECT producto, cantidad_vendida, fecha_inicio, fecha_fin FROM historial_ventas ORDER BY fecha_inicio DESC")
    
    if df is not None:
        st.success(f"✅ Se han cargado {len(df)} registros del Historial.")
        df['fecha_inicio'] = pd.to_datetime(df['fecha_inicio']).dt.date
        df['fecha_fin'] = pd.to_datetime(df['fecha_fin']).dt.date
        st.dataframe(df, use_container_width=True, hide_index=True, height=800)

# --- 2. INVENTARIO (Solo jala de maestro_insumos) ---
elif opcion == "📦 Inventario":
    st.header("📦 Gestión de Inventario (Maestro)")
    # Query directa a maestro_insumos. Aquí sí usamos la categoría que ya organizamos.
    df = cargar_datos("SELECT producto, categoria, stock_actual FROM maestro_insumos ORDER BY categoria ASC, producto ASC")
    
    if df is not None:
        st.info(f"📦 Total de productos en inventario: {len(df)}")
        st.dataframe(df, use_container_width=True, hide_index=True, height=600)

# --- 3. TABLERO DE CONTROL (Mantiene su lógica de alertas) ---
elif opcion == "🚨 Tablero":
    st.header("🚨 Tablero de Control")
    df = cargar_datos("SELECT * FROM tablero_control")
    if df is not None:
        st.dataframe(df, use_container_width=True, hide_index=True, height=800)

# --- 4. RECETAS ---
elif opcion == "🍳 Recetas":
    st.header("🍳 Recetas")
    df = cargar_datos("SELECT * FROM recetas")
    if df is not None:
        st.dataframe(df, use_container_width=True, hide_index=True)

# --- 5. SOFT RESTAURANT (Carga de archivos) ---
elif opcion == "🔄 Soft Restaurant":
    st.header("🔄 Carga de Datos Soft Restaurant")
    archivo = st.file_uploader("Sube el archivo de ventas", type=['csv', 'xlsx'])
    if archivo:
        st.success("Archivo listo para procesar.")

# --- 6. COPILOTO IA ---
elif opcion == "🤖 Copiloto IA":
    st.header("🤖 Copiloto IA")
    st.write("Espacio para análisis inteligente de datos.")
