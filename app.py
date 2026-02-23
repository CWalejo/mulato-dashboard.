import streamlit as st
import pandas as pd
import psycopg2

# 1. Configuración de la página
st.set_page_config(page_title="El Mulato - Sistema Integral", layout="wide")

# Credenciales de Neon
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

# Sidebar - Menú con todas tus páginas restauradas
st.sidebar.title("Menú El Mulato")
opcion = st.sidebar.radio("Selecciona una sección:", 
    ["📈 Historial de Ventas", "🚨 Tablero de Control", "📦 Inventario Real", "🍳 Recetas y Costos"])

# --- PÁGINA 1: HISTORIAL (Mes y Medio) ---
if opcion == "📈 Historial de Ventas":
    st.markdown("<h1 style='color: #D4AF37;'>📈 Ventas Acumuladas</h1>", unsafe_allow_html=True)
    st.info("Visualizando datos del periodo: **01/01/2026 al 23/02/2026**")
    df = cargar_datos("SELECT producto, cantidad_vendida, fecha_inicio, fecha_fin FROM historial_ventas ORDER BY cantidad_vendida DESC")
    if df is not None:
        st.dataframe(df, use_container_width=True)

# --- PÁGINA 2: TABLERO (Alertas Inteligentes) ---
elif opcion == "🚨 Tablero de Control":
    st.markdown("<h1 style='color: #FF4B4B;'>🚨 Alertas de Reabastecimiento</h1>", unsafe_allow_html=True)
    df = cargar_datos("SELECT * FROM tablero_control ORDER BY promedio_venta_diario DESC")
    if df is not None:
        def color_alertas(row):
            if row['alerta'] == 'CRÍTICO': return ['background-color: #ff4b4b; color: white'] * len(row)
            elif row['alerta'] == 'PEDIR': return ['background-color: #fca311; color: black'] * len(row)
            return [''] * len(row)
        st.dataframe(df.style.apply(color_alertas, axis=1), use_container_width=True)

# --- PÁGINA 3: INVENTARIO (Stock Físico) ---
elif opcion == "📦 Inventario Real":
    st.header("📦 Gestión de Stock en Bodega")
    df = cargar_datos("SELECT producto, stock_actual FROM maestro_insumos ORDER BY producto ASC")
    if df is not None:
        st.write("Estado actual de botellas e insumos:")
        st.dataframe(df, use_container_width=True)

# --- PÁGINA 4: RECETAS (Costos y Preparación) ---
elif opcion == "🍳 Recetas y Costos":
    st.header("🍳 Configuración de Recetas")
    df = cargar_datos("SELECT * FROM recetas ORDER BY plato ASC")
    if df is not None:
        st.dataframe(df, use_container_width=True)
