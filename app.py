import streamlit as st
import pandas as pd
import psycopg2

# 1. Configuración de la página
st.set_page_config(page_title="El Mulato - Sistema Inteligente", layout="wide")

# URL de conexión única
DB_URL = "postgresql://neondb_owner:npg_2YMloHQwec0b@ep-lucky-cloud-aihu085f-pooler.c-4.us-east-1.aws.neon.tech/neondb?sslmode=require"

# FUNCIÓN SIN CACHÉ (Llamada directa al servidor)
def cargar_datos_directo(query):
    try:
        # Abrimos conexión
        conn = psycopg2.connect(DB_URL)
        # Cargamos los datos sin guardar nada en memoria (Cero caché)
        df = pd.read_sql(query, conn)
        # Cerramos conexión
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

# --- PÁGINA: HISTORIAL (EL CORAZÓN DEL PROBLEMA) ---
if opcion == "📈 Historial":
    st.header("📈 Historial de Ventas")
    
    # Este botón "limpia" la memoria de Streamlit por si acaso
    if st.sidebar.button("🧹 Limpiar Memoria App"):
        st.cache_data.clear()
        st.rerun()

    # TRAEMOS TODO LO QUE HAYA EN HISTORIAL_VENTAS
    # Sin filtros, sin JOINs, sin categorías. Solo lo que ves en Neon.
    df_hist = cargar_datos_directo("SELECT * FROM historial_ventas")
    
    if df_hist is not None:
        st.write(f"📊 **Datos detectados en Neon:** {len(df_hist)} registros.")
        
        # Formato de fechas
        if not df_hist.empty:
            df_hist['fecha_inicio'] = pd.to_datetime(df_hist['fecha_inicio']).dt.date
            df_hist['fecha_fin'] = pd.to_datetime(df_hist['fecha_fin']).dt.date
        
        st.dataframe(df_hist, use_container_width=True, hide_index=True, height=800)

# --- PÁGINA: INVENTARIO (MAESTRO) ---
elif opcion == "📦 Inventario":
    st.header("📦 Inventario (Maestro)")
    df_inv = cargar_datos_directo("SELECT * FROM maestro_insumos ORDER BY categoria, producto")
    if df_inv is not None:
        st.write(f"📦 Total productos: {len(df_inv)}")
        st.dataframe(df_inv, use_container_width=True, hide_index=True, height=600)

# --- PÁGINA: TABLERO ---
elif opcion == "🚨 Tablero":
    st.header("🚨 Tablero de Control")
    df_tab = cargar_datos_directo("SELECT * FROM tablero_control")
    if df_tab is not None:
        st.dataframe(df_tab, use_container_width=True, hide_index=True, height=800)

# --- LAS DEMÁS OPCIONES ---
elif opcion == "🔄 Soft Restaurant":
    st.header("🔄 Carga de Datos")
    st.file_uploader("Subir reporte")

elif opcion == "🤖 Copiloto IA":
    st.header("🤖 Copiloto IA")
    st.info("Listo para analizar los datos cargados.")
