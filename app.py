import streamlit as st
import pandas as pd
import psycopg2

# 1. Configuración de la Página
st.set_page_config(page_title="El Mulato - Gestión Real", layout="wide")

# URL de Conexión (Asegúrate de usar la de tu rama nueva si quieres probar el respaldo)
DB_URL = "postgresql://neondb_owner:npg_2YMloHQwec0b@ep-lucky-cloud-aihu085f-pooler.c-4.us-east-1.aws.neon.tech/neondb?sslmode=require"

# Función de conexión directa (Sin caché para evitar los "fantasmas")
def consultar_neon(query):
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
    pin = st.text_input("PIN de Acceso:", type="password")
    if st.button("Entrar"):
        if pin == "4321":
            st.session_state['autenticado'] = True
            st.rerun()
    st.stop()

# --- MENÚ LATERAL ---
st.sidebar.title("🏢 Menú Principal")
opcion = st.sidebar.radio("Ir a:", ["📈 Historial de Ventas", "🍳 Recetas", "📦 Maestro de Insumos", "🚨 Tablero de Control"])

# --- SECCIÓN 1: HISTORIAL DE VENTAS ---
if opcion == "📈 Historial de Ventas":
    st.header("📈 Historial de Ventas (Desde Neon)")
    
    # Consulta específica para historial
    df_ventas = consultar_neon("SELECT * FROM historial_ventas ORDER BY id ASC")
    
    if df_ventas is not None:
        st.metric("Total Registros Cargados", len(df_ventas))
        st.dataframe(df_ventas, use_container_width=True, hide_index=True, height=600)
    else:
        st.warning("No se encontraron datos en la tabla historial_ventas.")

# --- SECCIÓN 2: RECETAS ---
elif opcion == "🍳 Recetas":
    st.header("🍳 Libro de Recetas")
    
    # Consulta específica para recetas
    df_recetas = consultar_neon("SELECT * FROM recetas ORDER BY nombre_receta ASC")
    
    if df_recetas is not None:
        st.write(f"📖 Mostrando {len(df_recetas)} recetas configuradas.")
        st.dataframe(df_recetas, use_container_width=True, hide_index=True)
    else:
        st.info("La tabla de recetas está vacía en Neon.")

# --- SECCIÓN 3: MAESTRO DE INSUMOS ---
elif opcion == "📦 Maestro de Insumos":
    st.header("📦 Maestro de Insumos (Inventario)")
    
    # Consulta específica para el maestro
    df_maestro = consultar_neon("SELECT producto, categoria, stock_actual FROM maestro_insumos ORDER BY categoria, producto")
    
    if df_maestro is not None:
        st.write(f"📦 Total productos en inventario: {len(df_maestro)}")
        st.dataframe(df_maestro, use_container_width=True, hide_index=True, height=600)

# --- SECCIÓN 4: TABLERO DE CONTROL ---
elif opcion == "🚨 Tablero de Control":
    st.header("🚨 Alertas y Estados")
    # Aquí puedes poner la lógica de cruce de datos más adelante
    st.info("Tablero listo para procesar alertas de stock.")
