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
        st.error(f"Error de conexión: {e}")
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

# --- 📈 HISTORIAL (SIN FILTROS - LOS 144 PRODUCTOS) ---
if opcion == "📈 Historial":
    st.header("📈 Historial de Ventas")
    # Leemos directo de la tabla de historial sin cruzar con nada para que no se pierdan datos
    df = cargar_datos("SELECT producto, cantidad_vendida, fecha_inicio, fecha_fin FROM historial_ventas ORDER BY producto ASC")
    
    if df is not None:
        st.success(f"✅ Se han cargado {len(df)} productos correctamente.")
        # Limpieza de visualización
        df['fecha_inicio'] = pd.to_datetime(df['fecha_inicio']).dt.date
        df['fecha_fin'] = pd.to_datetime(df['fecha_fin']).dt.date
        st.dataframe(df, use_container_width=True, hide_index=True, height=800)

# --- 📦 INVENTARIO (MAESTRO DE INSUMOS) ---
elif opcion == "📦 Inventario":
    st.header("📦 Gestión de Stock")
    # Aquí es donde SÍ usamos categorías porque la tabla maestro_insumos las tiene
    df = cargar_datos("SELECT producto, categoria, stock_actual FROM maestro_insumos ORDER BY categoria, producto ASC")
    if df is not None:
        st.dataframe(df, use_container_width=True, hide_index=True, height=600)

# --- 🚨 TABLERO DE CONTROL (RESTAURADO) ---
elif opcion == "🚨 Tablero":
    st.header("🚨 Tablero de Control y Pedidos")
    # El tablero debe mostrar todo lo que la vista 'tablero_control' de Neon ya calculó
    df = cargar_datos("SELECT * FROM tablero_control")
    if df is not None:
        st.dataframe(df, use_container_width=True, hide_index=True, height=800)

# --- 🔄 CARGAR DATOS (SOFT RESTAURANT) ---
elif opcion == "🔄 Soft Restaurant":
    st.header("🔄 Sincronización Soft Restaurant")
    archivo = st.file_uploader("Sube el reporte para actualizar los 144 registros", type=['csv', 'xlsx'])
    if archivo:
        st.info("Archivo detectado. Listo para procesar.")

# --- 🤖 COPILOTO IA ---
elif opcion == "🤖 Copiloto IA":
    st.header("🤖 Copiloto IA")
    st.write("Análisis inteligente basado en los 144 registros del historial.")
