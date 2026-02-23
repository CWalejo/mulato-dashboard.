app.py
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

# --- INVENTARIO CRÍTICO ---
st.subheader("🚨 Alertas de Stock (Desde Neon)")
df_control = cargar_datos("SELECT * FROM tablero_control")

if df_control is not None:
    # Filtramos por los estados que tienes en tu imagen: PEDIR y CRÍTICO
    alertas = df_control[df_control['alerta'].isin(['PEDIR', 'CRÍTICO'])]
    st.dataframe(alertas, use_container_width=True)

# --- PREDICCIÓN DE VENTAS ---
st.divider()
st.subheader("📈 Análisis de Ventas Pasadas")
df_ventas = cargar_datos("SELECT * FROM historial_ventas")

if df_ventas is not None and not df_ventas.empty:
    # Si tienes una columna de fecha, creamos la gráfica
    if 'fecha' in df_ventas.columns:
        df_ventas['fecha'] = pd.to_datetime(df_ventas['fecha'])
        fig = px.line(df_ventas, x='fecha', y='cantidad', title='Tendencia de Ventas', color_discrete_sequence=['#D4AF37'])
        st.plotly_chart(fig, use_container_width=True)
        
        # Predicción simple: Promedio de lo vendido anteriormente
        prediccion = df_ventas['cantidad'].mean()
        st.success(f"💡 Basado en semanas pasadas, deberías tener stock para vender aprox: **{int(prediccion)} unidades** el próximo periodo.")
else:
    st.info("Aún no hay datos en 'historial_ventas' para generar una gráfica de predicción.")
