import streamlit as st
import pandas as pd
import psycopg2
import plotly.express as px

# Estilo visual de El Mulato
st.set_page_config(page_title="El Mulato - Predicciones", layout="wide")
st.markdown("<h1 style='text-align: center; color: #D4AF37;'>🏆 Tablero de Control y Predicciones</h1>", unsafe_allow_html=True)

# Conexión directa a tu Neon
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

# --- SECCIÓN 1: ALERTAS DE STOCK ---
st.subheader("🚨 Alertas de Stock (Desde Neon)")
df_control = cargar_datos("SELECT * FROM tablero_control")

if df_control is not None and not df_control.empty:
    # Filtramos por los estados que tienes en tu imagen: PEDIR y CRÍTICO
    alertas = df_control[df_control['alerta'].isin(['PEDIR', 'CRÍTICO'])]
    if not alertas.empty:
        st.dataframe(alertas, use_container_width=True)
    else:
        st.success("✅ Todo el stock está en niveles óptimos (OK).")

st.divider()

# --- SECCIÓN 2: ANÁLISIS DE VENTAS ---
st.subheader("📈 Análisis de Ventas Pasadas")
# Usamos 'cantidad_vendida' que es el nombre real en tu tabla historial_ventas
df_ventas = cargar_datos("SELECT fecha, cantidad_vendida FROM historial_ventas")

if df_ventas is not None and not df_ventas.empty:
    # Convertimos fecha a formato tiempo para la gráfica
    df_ventas['fecha'] = pd.to_datetime(df_ventas['fecha'])
    
    # Agrupamos por fecha para sumar las ventas del día
    ventas_diarias = df_ventas.groupby('fecha')['cantidad_vendida'].sum().reset_index()
    
    fig = px.line(ventas_diarias, x='fecha', y='cantidad_vendida', 
                 title='Tendencia de Ventas (Cantidades totales por día)',
                 color_discrete_sequence=['#D4AF37'])
    st.plotly_chart(fig, use_container_width=True)
else:
    st.warning("No hay datos suficientes en 'historial_ventas' para mostrar la gráfica.")
