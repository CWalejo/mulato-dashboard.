import streamlit as st
import pandas as pd
import psycopg2

# 1. Configuración de la página
st.set_page_config(page_title="El Mulato - Control Real", layout="wide")

# Credenciales de Neon
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

# Navegación
st.sidebar.title("Menú El Mulato")
opcion = st.sidebar.radio("Ir a:", ["📈 Historial de Ventas", "🚨 Tablero de Control"])

# --- PÁGINA 1: HISTORIAL ---
if opcion == "📈 Historial de Ventas":
    st.markdown("<h1 style='color: #D4AF37;'>📈 Ventas Acumuladas</h1>", unsafe_allow_html=True)
    st.info("Periodo: 01/01/2026 al 23/02/2026 (53 días)")
    
    df_h = cargar_datos("SELECT producto, cantidad_vendida, fecha_inicio, fecha_fin FROM historial_ventas ORDER BY cantidad_vendida DESC")
    if df_h is not None:
        st.dataframe(df_h, use_container_width=True)

# --- PÁGINA 2: TABLERO (PROMEDIOS DIARIOS) ---
elif opcion == "🚨 Tablero de Control":
    st.markdown("<h1 style='color: #FF4B4B;'>🚨 Estado de Alertas</h1>", unsafe_allow_html=True)
    
    df_t = cargar_datos("SELECT * FROM tablero_control ORDER BY promedio_venta_diario DESC")
    
    if df_t is not None:
        def estilo_alertas(row):
            if row['alerta'] == 'CRÍTICO':
                return ['background-color: #ff4b4b; color: white'] * len(row)
            elif row['alerta'] == 'PEDIR':
                return ['background-color: #fca311; color: black'] * len(row)
            return [''] * len(row)

        st.dataframe(df_t.style.apply(estilo_alertas, axis=1), use_container_width=True)
