import streamlit as st
import pandas as pd
import psycopg2
import plotly.express as px

# 1. Configuración de la Página (Usa st.set_page_config de tu lista)
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

# --- SEGURIDAD (Usa st.session_state y st.text_input) ---
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

# --- MENÚ LATERAL (Usa st.sidebar) ---
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
    df = consultar_neon("SELECT * FROM maestro_insumos ORDER BY producto ASC")
    if df is not None:
        st.dataframe(df, use_container_width=True, hide_index=True)

elif opcion == "🚨 Tablero":
    st.header("🚨 Tablero de Gestión de Inventario")
    df_tablero = consultar_neon("SELECT * FROM tablero_control")
    
    if df_tablero is not None:
        # Limpieza de datos (usando pandas)
        df_tablero["venta_real"] = pd.to_numeric(df_tablero["venta_real"], errors='coerce').fillna(0)
        df_tablero["stock_actual"] = pd.to_numeric(df_tablero["stock_actual"], errors='coerce').fillna(0)

        # --- KPIs (Usa st.columns y st.metric) ---
        c1, c2, c3, c4 = st.columns(4)
        criticos = len(df_tablero[df_tablero['alerta'].str.contains("🔴|CRÍTICO", na=False)])
        pedir = len(df_tablero[df_tablero['alerta'].str.contains("🟡|PEDIR", na=False)])
        stock_total = df_tablero["stock_actual"].sum()
        
        c1.metric("🚨 CRÍTICOS", criticos, delta=f"{criticos} urgentes", delta_color="inverse")
        c2.metric("🟡 POR PEDIR", pedir)
        c3.metric("📦 STOCK TOTAL", int(stock_total))
        c4.success("✅ Sincronizado")

        st.divider() # Usa st.divider de tu lista

        # --- GRÁFICOS (Usa st.plotly_chart) ---
        col_izq, col_der = st.columns([1, 1])

        with col_izq:
            st.subheader("⚠️ Top 10 Stock Crítico")
            df_bajos = df_tablero.nsmallest(10, "stock_actual")
            fig_stock = px.bar(df_bajos, x="stock_actual", y="producto", orientation='h',
                              color="stock_actual", color_continuous_scale="Reds_r", text_auto=True)
            fig_stock.update_layout(showlegend=False, height=350)
            st.plotly_chart(fig_stock, use_container_width=True)

        with col_der:
            st.subheader("🔥 Movimiento de Ventas")
            df_ventas = df_tablero.nlargest(10, "venta_real")
            fig_ventas = px.pie(df_ventas, values="venta_real", names="producto", hole=0.4)
            fig_ventas.update_layout(height=350)
            st.plotly_chart(fig_ventas, use_container_width=True)

        # --- TABLA DETALLADA (Usa st.dataframe con column_config) ---
        st.markdown("### 📋 Detalle de Alertas")
        st.dataframe(
            df_tablero.sort_values(by="stock_actual"), 
            use_container_width=True, 
            hide_index=True,
            column_config={
                "stock_actual": st.column_config.NumberColumn("Stock", format="%d 📦"),
                "alerta": "Estado"
            },
            column_order=("alerta", "producto", "stock_actual", "venta_real", "pedido_sugerido")
        )

elif opcion == "📤 Carga de Datos":
    st.header("📤 Actualizar desde Soft")
    st.info("Configuraremos los 'INSERT' en Neon mañana para habilitar la memoria de la IA.")
    archivo = st.file_uploader("Subir reporte de Soft (CSV)", type=["csv"])
    if archivo:
        st.toast("Archivo recibido correctamente", icon="📥") # Usa st.toast de tu lista

elif opcion == "🤖 IA Mulato":
    st.header("🤖 Asistente de Negocio")
    st.warning("⚠️ Migrando motor a OpenAI para mayor estabilidad.")
    st.write("Mañana conectaremos la API Key para activar el análisis histórico.")
    st.chat_input("Deshabilitado temporalmente...", disabled=True)
