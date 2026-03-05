import streamlit as st
import pandas as pd
import psycopg2

# 1. Configuración de la Página
st.set_page_config(page_title="El Mulato - Sistema Real", layout="wide")

# --- LA NUEVA CLAVE QUE ME PASASTE ---
DB_URL = "postgresql://neondb_owner:npg_2YMloHQwec0b@ep-solitary-cake-ai8g7c0x-pooler.c-4.us-east-1.aws.neon.tech/neondb?sslmode=require"

def consultar_neon(query):
    try:
        # Usamos la nueva URL para conectar
        conn = psycopg2.connect(DB_URL)
        df = pd.read_sql(query, conn)
        conn.close()
        return df
    except Exception as e:
        st.error(f"❌ Error de conexión con la nueva clave: {e}")
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
opcion = st.sidebar.radio("Ir a:", ["📈 Historial de Ventas", "🍳 Recetas", "📦 Maestro de Insumos", "🚨 Tablero"])

# --- 1. HISTORIAL ---
if opcion == "📈 Historial de Ventas":
    st.header("📈 Historial de Ventas")
    # Traemos todo de la tabla historial_ventas
    df_ventas = consultar_neon("SELECT * FROM historial_ventas")
    if df_ventas is not None:
        st.metric("Total Registros", len(df_ventas))
        st.dataframe(df_ventas, use_container_width=True, hide_index=True)

# --- 2. RECETAS ---
elif opcion == "🍳 Recetas":
    st.header("🍳 Libro de Recetas")
    df_recetas = consultar_neon("SELECT * FROM recetas")
    if df_recetas is not None:
        st.write(f"📖 Recetas cargadas: {len(df_recetas)}")
        st.dataframe(df_recetas, use_container_width=True, hide_index=True)

# --- 3. MAESTRO DE INSUMOS ---
elif opcion == "📦 Maestro de Insumos":
    st.header("📦 Maestro de Insumos")
    df_inv = consultar_neon("SELECT * FROM maestro_insumos")
    if df_inv is not None:
        st.write(f"📦 Ítems en inventario: {len(df_inv)}")
        st.dataframe(df_inv, use_container_width=True, hide_index=True)

# --- 4. TABLERO ---
elif opcion == "🚨 Tablero":
    st.header("🚨 Tablero de Control")
    st.info("Conexión establecida. Listo para procesar alertas.")
