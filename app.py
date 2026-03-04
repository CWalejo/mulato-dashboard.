import streamlit as st
import pandas as pd
import psycopg2
import random

# 1. Configuración
st.set_page_config(page_title="El Mulato - Sistema Inteligente", layout="wide")

# URL de conexión (La misma que tienes)
DB_URL = "postgresql://neondb_owner:npg_2YMloHQwec0b@ep-lucky-cloud-aihu085f-pooler.c-4.us-east-1.aws.neon.tech/neondb?sslmode=require"

# FUNCIÓN CON "ROMPE-CACHÉ"
def cargar_datos_forzado(query):
    try:
        # Añadimos un parámetro aleatorio interno para que la conexión sea única
        conn = psycopg2.connect(DB_URL)
        # Forzamos a pandas a no usar caché
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
    st.markdown("<h2 style='text-align: center;'>🔐 Acceso Privado</h2>", unsafe_allow_html=True)
    pin = st.text_input("PIN:", type="password")
    if st.button("Ingresar"):
        if pin == "4321":
            st.session_state['autenticado'] = True
            st.rerun()
    st.stop()

# --- MENÚ ---
st.sidebar.title("Menú El Mulato")
opcion = st.sidebar.radio("Sección:", ["📈 Historial", "📦 Inventario", "🚨 Tablero", "🔄 Soft Restaurant", "🤖 Copiloto IA"])

# --- PÁGINA: HISTORIAL ---
if opcion == "📈 Historial":
    st.header("📈 Historial de Ventas")
    
    # BOTÓN PARA FORZAR RECARGA MANUAL
    if st.button("🔄 Forzar Sincronización Real con Neon"):
        st.cache_data.clear()
        st.rerun()

    # Query ultra simple
    df = cargar_datos_forzado("SELECT * FROM historial_ventas")
    
    if df is not None:
        cantidad = len(df)
        if cantidad <= 10:
            st.warning(f"⚠️ ¡Atención! La App solo detecta {cantidad} filas. Esto significa que la tabla en Neon que esta URL está leyendo solo tiene {cantidad} datos.")
        else:
            st.success(f"✅ ¡Éxito! Se detectaron {cantidad} registros.")
        
        st.dataframe(df, use_container_width=True, hide_index=True, height=800)

# --- PÁGINA: INVENTARIO ---
elif opcion == "📦 Inventario":
    st.header("📦 Inventario (Maestro)")
    df = cargar_datos_forzado("SELECT * FROM maestro_insumos ORDER BY categoria ASC")
    if df is not None:
        st.write(f"Total en Maestro: {len(df)}")
        st.dataframe(df, use_container_width=True, hide_index=True, height=600)

# --- PÁGINA: TABLERO ---
elif opcion == "🚨 Tablero":
    st.header("🚨 Tablero")
    df = cargar_datos_forzado("SELECT * FROM tablero_control")
    if df is not None:
        st.dataframe(df, use_container_width=True, hide_index=True)

# --- LAS OTRAS SECCIONES ---
elif opcion == "🔄 Soft Restaurant":
    st.header("🔄 Carga de Datos")
    st.file_uploader("Subir reporte")

elif opcion == "🤖 Copiloto IA":
    st.header("🤖 Copiloto IA")
    st.write("Análisis en pausa hasta confirmar carga de datos.")
