import streamlit as st
import pandas as pd
import psycopg2
import plotly.express as px
import requests
import json

# 1. Configuración de la Página
st.set_page_config(page_title="El Mulato Hub", layout="wide", page_icon="🏢")

# --- CONEXIÓN A NEON ---
DB_URL = "postgresql://neondb_owner:npg_2YMloHQwec0b@ep-young-meadow-aicra7vo-pooler.c-4.us-east-1.aws.neon.tech/neondb?sslmode=require"

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
st.sidebar.title("🏢 El Mulato Hub")
opcion = st.sidebar.radio("Navegación:", 
    ["📈 Historial", "🍳 Recetas", "📦 Maestro", "🚨 Tablero", "📤 Carga de Datos", "🤖 IA Mulato"])

# --- SECCIONES ---
if opcion == "📈 Historial":
    st.header("📈 Historial de Ventas")
    df = consultar_neon("SELECT * FROM historial_ventas ORDER BY id ASC")
    if df is not None:
        st.metric("Total Registros", len(df))
        st.dataframe(df, use_container_width=True, hide_index=True)

elif opcion == "🍳 Recetas":
    st.header("🍳 Libro de Recetas")
    df = consultar_neon("SELECT * FROM recetas")
    if df is not None:
        st.dataframe(df, use_container_width=True, hide_index=True)

elif opcion == "📦 Maestro":
    st.header("📦 Maestro de Insumos")
    df = consultar_neon("SELECT * FROM maestro_insumos")
    if df is not None:
        st.dataframe(df, use_container_width=True, hide_index=True)

elif opcion == "🚨 Tablero":
    st.header("🚨 Tablero de Gestión")
    
    # Traemos los datos uniendo con las categorías del maestro si es necesario, 
    # o simplemente ordenando si ya están en tablero_control.
    df_tablero = consultar_neon("SELECT * FROM tablero_control")
    
    if df_tablero is not None:
        # Aseguramos que los números funcionen
        df_tablero["venta_real"] = pd.to_numeric(df_tablero["venta_real"], errors='coerce').fillna(0)
        df_tablero["stock_actual"] = pd.to_numeric(df_tablero["stock_actual"], errors='coerce').fillna(0)
        
        # KPIs de cabecera
        c1, c2, c3 = st.columns(3)
        criticos = len(df_tablero[df_tablero['alerta'].str.contains("🔴", na=False)])
        c1.metric("🔴 Alertas Críticas", criticos)
        c2.metric("📦 Stock Total", int(df_tablero["stock_actual"].sum()))
        c3.success("Sincronización Neon OK")

        st.divider()

        # --- MOSTRAR POR CATEGORÍAS (Usando la columna 'categoria' de tu Neon) ---
        # Si tu tabla de Neon tiene la columna 'categoria', la usamos para agrupar:
        if 'categoria' in df_tablero.columns:
            categorias = ["Comida", "Aguardiente", "Ron", "Tequila", "Whisky", "Ginebra", "Vodka", "Vinos", "Otros Licores", "Cervezas", "Pasantes"]
            
            for cat in categorias:
                df_cat = df_tablero[df_tablero['categoria'] == cat]
                if not df_cat.empty:
                    with st.expander(f"📁 {cat.upper()}", expanded=True):
                        st.dataframe(
                            df_cat, 
                            use_container_width=True, 
                            hide_index=True,
                            column_order=("alerta", "producto", "stock_actual", "venta_real", "pedido_sugerido")
                        )
        else:
            # Si no hay columna categoria en el tablero, lo mostramos plano pero ordenado
            st.dataframe(
                df_tablero, 
                use_container_width=True, 
                hide_index=True,
                column_order=("producto", "stock_actual", "venta_real", "alerta", "pedido_sugerido")
            )

elif opcion == "📤 Carga de Datos":
    st.header("📤 Actualizar desde Soft")
    archivo = st.file_uploader("Subir reporte de Soft (CSV)", type=["csv"])
    if archivo:
        st.info("Archivo recibido. Mañana activaremos la carga a Neon.")

elif opcion == "🤖 IA Mulato":
    st.header("🤖 Asistente de Negocio")
    st.warning("⚠️ Mantenimiento: Activaremos SistemAI mañana.")
