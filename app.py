import streamlit as st
import pandas as pd
import psycopg2
import google.generativeai as genai
import plotly.express as px

# 1. Configuración de la Página
st.set_page_config(page_title="El Mulato Hub", layout="wide", page_icon="🏢")

# --- CONEXIÓN A NEON ---
# Usando la rama Primary (Lucky Cloud) para asegurar que carguen tus 144 registros
DB_URL = "postgresql://neondb_owner:npg_2YMloHQwec0b@ep-lucky-cloud-aihu085f-pooler.c-4.us-east-1.aws.neon.tech/neondb?sslmode=require"

# --- CONFIGURACIÓN IA ---
# Configuración directa para evitar el error de InvalidArgument
genai.configure(api_key="TU_API_KEY_AQUI")
model = genai.GenerativeModel('gemini-1.5-flash')

def consultar_neon(query):
    try:
        conn = psycopg2.connect(DB_URL)
        df = pd.read_sql(query, conn)
        conn.close()
        return df
    except Exception as e:
        st.error(f"❌ Error de conexión con Neon: {e}")
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
st.sidebar.title("🏢 El Mulato Hub")
opcion = st.sidebar.radio("Navegación:", ["📈 Historial", "🍳 Recetas", "📦 Maestro", "🚨 Tablero", "📤 Carga de Datos", "🤖 IA Mulato"])

# --- 1. HISTORIAL ---
if opcion == "📈 Historial":
    st.header("📈 Historial de Ventas")
    df = consultar_neon("SELECT * FROM historial_ventas ORDER BY id ASC")
    if df is not None:
        st.metric("Registros Cargados", len(df))
        st.dataframe(df, use_container_width=True, hide_index=True)

# --- 2. RECETAS ---
elif opcion == "🍳 Recetas":
    st.header("🍳 Libro de Recetas")
    df = consultar_neon("SELECT * FROM recetas")
    if df is not None:
        st.dataframe(df, use_container_width=True, hide_index=True)

# --- 3. MAESTRO DE INSUMOS ---
elif opcion == "📦 Maestro":
    st.header("📦 Maestro de Insumos (Inventario)")
    df = consultar_neon("SELECT * FROM maestro_insumos ORDER BY producto ASC")
    if df is not None:
        st.dataframe(df, use_container_width=True, hide_index=True)

# --- 4. TABLERO DE GESTIÓN ---
elif opcion == "🚨 Tablero":
    st.header("🚨 Tablero de Gestión")
    df_tablero = consultar_neon("SELECT * FROM tablero_control")
    
    if df_tablero is not None:
        # Aseguramos decimales para ver el gasto real de botellas
        df_tablero["venta_real"] = df_tablero["venta_real"].astype(float)
        
        c1, c2, c3 = st.columns(3)
        criticos = len(df_tablero[df_tablero['alerta'].str.contains("CRÍTICO", na=False)])
        pedir = len(df_tablero[df_tablero['alerta'].str.contains("PEDIR", na=False)])
        
        c1.metric("🔴 Alertas Críticas", criticos)
        c2.metric("🟡 Pedidos Pendientes", pedir)
        c3.success("Datos en tiempo real")

        st.dataframe(
            df_tablero, 
            use_container_width=True, 
            hide_index=True,
            column_order=("producto", "stock_actual", "promedio_venta_diario", "venta_real", "alerta", "pedido
