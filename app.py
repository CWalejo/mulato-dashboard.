import streamlit as st
import pandas as pd
import psycopg2
import plotly.express as px

# Configuración profesional
st.set_page_config(page_title="El Mulato - Gestión Real", layout="wide")

# Conexión Directa
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

# --- MENÚ LATERAL ---
st.sidebar.title("Menú El Mulato")
opcion = st.sidebar.radio("Ir a la tabla:", 
                         ["📈 Historial de Ventas", 
                          "📦 Maestro de Insumos", 
                          "🍳 Recetas", 
                          "🚨 Tablero de Control"])

# 1. PÁGINA: HISTORIAL DE VENTAS
if opcion == "📈 Historial de Ventas":
    st.header("Registro Histórico de Ventas")
    df = cargar_datos("SELECT * FROM historial_ventas")
    if df is not None:
        st.dataframe(df, use_container_width=True) # Muestra fecha, producto y cantidad_vendida

# 2. PÁGINA: MAESTRO DE INSUMOS
elif opcion == "📦 Maestro de Insumos":
    st.header("Inventario Maestro (Insumos)")
    df = cargar_datos("SELECT * FROM maestro_insumos")
    if df is not None:
        st.dataframe(df, use_container_width=True) # Muestra stock_actual, categoria, etc.

# 3. PÁGINA: RECETAS
elif opcion == "🍳 Recetas":
    st.header("Configuración de Recetas y Porciones")
    df = cargar_datos("SELECT * FROM recetas")
    if df is not None:
        st.dataframe(df, use_container_width=True) # Muestra nombre_plato, insumo, cantidad_gastada

# 4. PÁGINA: TABLERO DE CONTROL
elif opcion == "🚨 Tablero de Control":
    st.header("Estado de Alertas y Pedidos")
    df = cargar_datos("SELECT * FROM tablero_control")
    if df is not None:
        # Resaltamos en rojo las filas que están en CRÍTICO para que él lo note rápido
        def color_alertas(val):
            color = 'red' if val == 'CRÍTICO' else ('orange' if val == 'PEDIR' else 'white')
            return f'color: {color}'
        
        st.dataframe(df.style.applymap(color_alertas, subset=['alerta']), use_container_width=True)
