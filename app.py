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
        st.dataframe(df, use_container_width=True, hide_index=True)

elif opcion == "🍳 Recetas":
    st.header("🍳 Libro de Recetas")
    # Ajustado a tus nombres de columna en Neon: nombre_plato, insumo, cantidad_gastada
    df = consultar_neon("SELECT nombre_plato, insumo, cantidad_gastada FROM recetas")
    if df is not None:
        st.dataframe(df, use_container_width=True, hide_index=True)

elif opcion == "📦 Maestro":
    st.header("📦 Maestro de Insumos")
    df = consultar_neon("SELECT * FROM maestro_insumos")
    if df is not None:
        st.dataframe(df, use_container_width=True, hide_index=True)

elif opcion == "🚨 Tablero":
    st.header("🚨 Tablero de Gestión")
    
    # Consulta con tus columnas reales incluyendo promedio_venta_diario
    df_tablero = consultar_neon("SELECT producto, stock_actual, promedio_venta_diario, venta_real, alerta, pedido_sugerido FROM tablero_control")
    
    if df_tablero is not None:
        # Forzamos decimales para precisión de shots (0.09)
        df_tablero["venta_real"] = pd.to_numeric(df_tablero["venta_real"], errors='coerce').fillna(0.0)
        df_tablero["stock_actual"] = pd.to_numeric(df_tablero["stock_actual"], errors='coerce').fillna(0.0)
        df_tablero["promedio_venta_diario"] = pd.to_numeric(df_tablero["promedio_venta_diario"], errors='coerce').fillna(0.0)
        
        # KPIs Superiores
        c1, c2 = st.columns(2)
        # Filtramos alertas críticas basándonos en tu columna 'alerta'
        criticos = len(df_tablero[df_tablero['alerta'].str.contains("CRÍTICO|🔴", na=False)])
        
        c1.metric("🔴 Alertas Críticas", criticos)
        c2.metric("📦 Stock Total", f"{df_tablero['stock_actual'].sum():.2f}")

        st.divider()

        # Tabla única organizada (sin el error de categoría)
        st.dataframe(
            df_tablero, 
            use_container_width=True, 
            hide_index=True,
            column_order=("alerta", "producto", "stock_actual", "promedio_venta_diario", "venta_real", "pedido_sugerido"),
            column_config={
                "alerta": "Estado",
                "producto": "Insumo",
                "stock_actual": st.column_config.NumberColumn("Stock (Bodega+Barra)", format="%.2f"),
                "promedio_venta_diario": st.column_config.NumberColumn("Prom. Diario", format="%.2f"),
                "venta_real": st.column_config.NumberColumn("Venta Real", format="%.2f"),
                "pedido_sugerido": "Sugerencia"
            }
        )

elif opcion == "📤 Carga de Datos":
    st.header("📤 Actualizar desde Soft")
    archivo = st.file_uploader("Subir reporte de Soft (CSV)", type=["csv"])
    if archivo:
        st.info("Archivo recibido. Sistema listo para procesar.")

elif opcion == "🤖 IA Mulato":
    st.header("🤖 Consultor Estratégico El Mulato")
    
    try:
        api_key_openai = st.secrets["OPENAI_API_KEY"]
    except:
        st.error("🔑 Error: No se encontró la OPENAI_API_KEY en los Secrets de Streamlit.")
        st.stop()

    # Traemos los datos de Neon con las columnas correctas
    df_inv = consultar_neon("SELECT producto, stock_actual, promedio_venta_diario, venta_real, alerta FROM tablero_control")
    df_rec = consultar_neon("SELECT nombre_plato, insumo, cantidad_gastada FROM recetas")
    
    pregunta = st.chat_input("Ej: ¿Para cuántos cocteles me alcanza el ron actual?")
    
    if pregunta:
        if df_inv is not None and df_rec is not None:
            contexto_ia = f"STOCK ACTUAL:\n{df_inv.to_string()}\n\nRECETARIO (Gasto por shot/unidad):\n{df_rec.to_string()}"
            
            headers = {"Content-Type": "application/json", "Authorization": f"Bearer {api_key_openai}"}
            payload = {
                "model": "gpt-4o-mini",
                "messages": [
                    {"role": "system", "content": "Eres el socio analista de El Mulato. Calcula disponibilidad basándote en el gasto de 0.09 por shot de las recetas. Sé breve y directo."},
                    {"role": "user", "content": f"Datos del bar:\n{contexto_ia}\n\nPregunta: {pregunta}"}
                ],
                "temperature": 0.2
            }
            
            with st.spinner("Analizando con IA..."):
                res = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
                if res.status_code == 200:
                    st.info(res.json()["choices"][0]["message"]["content"])
                else:
                    st.error("Error: Revisa el saldo en OpenAI Billing ($5 USD min).")
