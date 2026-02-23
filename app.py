import streamlit as st
import pandas as pd
import psycopg2
import plotly.express as px

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="El Mulato - Sistema de Control", layout="wide")

# Conexión a Neon
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

# --- MENÚ LATERAL ---
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/3703/3703377.png", width=100)
st.sidebar.title("Navegación")
opcion = st.sidebar.radio("Selecciona una Vista:", 
                         ["🚨 Tablero de Control", 
                          "📦 Inventario Actual", 
                          "📈 Historial de Ventas", 
                          "🔮 Predicciones de Compra"])

# --- PÁGINA 1: TABLERO DE CONTROL (ALERTAS) ---
if opcion == "🚨 Tablero de Control":
    st.markdown("<h1 style='color: #D4AF37;'>🚨 Alertas Urgentes</h1>", unsafe_allow_html=True)
    df = cargar_datos("SELECT * FROM tablero_control")
    if df is not None:
        alertas = df[df['alerta'].isin(['PEDIR', 'CRÍTICO'])]
        if not alertas.empty:
            st.warning(f"Hay {len(alertas)} productos que requieren atención.")
            st.dataframe(alertas.style.background_gradient(cmap='Reds', subset=['pedido_sugerido']), use_container_width=True)
        else:
            st.success("✅ Todo está bajo control.")

# --- PÁGINA 2: INVENTARIO ACTUAL (DETALLE PRODUCTO POR PRODUCTO) ---
elif opcion == "📦 Inventario Actual":
    st.markdown("<h1 style='color: #D4AF37;'>📦 Detalle de Inventario</h1>", unsafe_allow_html=True)
    df = cargar_datos("SELECT * FROM inventario") # Asegúrate que la tabla se llame así en Neon
    if df is not None:
        st.write("Usa el buscador para filtrar un producto específico:")
        search = st.text_input("Buscar producto...")
        if search:
            df = df[df['nombre_producto'].str.contains(search, case=False)]
        st.table(df) # Formato tabla para ver detalle a detalle

# --- PÁGINA 3: HISTORIAL DE VENTAS ---
elif opcion == "📈 Historial de Ventas":
    st.markdown("<h1 style='color: #D4AF37;'>📈 Registro de Ventas</h1>", unsafe_allow_html=True)
    df = cargar_datos("SELECT * FROM historial_ventas")
    if df is not None:
        col1, col2 = st.columns([1, 2])
        with col1:
            st.write("Datos Crudos:")
            st.dataframe(df)
        with col2:
            df['fecha'] = pd.to_datetime(df['fecha'])
            ventas_diarias = df.groupby('fecha')['cantidad_vendida'].sum().reset_index()
            fig = px.bar(ventas_diarias, x='fecha', y='cantidad_vendida', title="Ventas por Día", color_discrete_sequence=['#D4AF37'])
            st.plotly_chart(fig, use_container_width=True)

# --- PÁGINA 4: PREDICCIONES (MATEMÁTICA) ---
elif opcion == "🔮 Predicciones de Compra":
    st.markdown("<h1 style='color: #D4AF37;'>🔮 Predicción Inteligente</h1>", unsafe_allow_html=True)
    df = cargar_datos("SELECT producto, promedio_venta_diario, stock_actual, pedido_sugerido FROM tablero_control")
    if df is not None:
        st.info("Este cálculo se basa en el promedio de ventas diario vs tu stock actual.")
        fig = px.scatter(df, x="stock_actual", y="pedido_sugerido", text="producto", size="promedio_venta_diario", title="Relación Stock vs Pedido")
        st.plotly_chart(fig, use_container_width=True)
