import streamlit as st
import pandas as pd
import psycopg2
import google.generativeai as genai
import plotly.express as px
import requests
import json

# 1. Configuración de la Página
st.set_page_config(page_title="El Mulato Hub", layout="wide", page_icon="🏢")

# --- CONEXIÓN A NEON ---
DB_URL = "postgresql://neondb_owner:npg_2YMloHQwec0b@ep-young-meadow-aicra7vo-pooler.c-4.us-east-1.aws.neon.tech/neondb?sslmode=require"

# --- CONFIGURACIÓN IA ---
API_KEY = "AIzaSyCqwFemPJ1Ip6Ry7bULmjEZ6fM9Pl6t8x8"

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
    df = consultar_neon("SELECT * FROM maestro_insumos ORDER BY producto ASC")
    if df is not None:
        st.dataframe(df, use_container_width=True, hide_index=True)

elif opcion == "🚨 Tablero":
    st.header("🚨 Tablero de Gestión")
    df_tablero = consultar_neon("SELECT * FROM tablero_control")
    
    if df_tablero is not None:
        df_tablero["venta_real"] = df_tablero["venta_real"].astype(float)
        
        c1, c2, c3 = st.columns(3)
        criticos = len(df_tablero[df_tablero['alerta'].str.contains("🔴|CRÍTICO", na=False)])
        pedir = len(df_tablero[df_tablero['alerta'].str.contains("🟡|PEDIR", na=False)])
        
        c1.metric("🔴 Alertas Críticas", criticos)
        c2.metric("🟡 Pedidos Pendientes", pedir)
        c3.success("Sincronización Neon OK")

        st.dataframe(
            df_tablero, 
            use_container_width=True, 
            hide_index=True,
            column_order=("producto", "stock_actual", "promedio_venta_diario", "venta_real", "alerta", "pedido_sugerido")
        )

elif opcion == "📤 Carga de Datos":
    st.header("📤 Actualizar desde Soft")
    archivo = st.file_uploader("Subir reporte de Soft (CSV)", type=["csv"])
    if archivo:
        st.info("Archivo detectado. Procesando integración...")

# --- 6. IA MULATO (CAMINO A: GEMINI-PRO) ---
elif opcion == "🤖 IA Mulato":
    st.header("🤖 Asistente de Negocio")
    st.write("Analizo tu inventario real para darte recomendaciones.")

    df_contexto = consultar_neon("SELECT producto, stock_actual, alerta, venta_real FROM tablero_control")
    
    pregunta = st.chat_input("¿Qué quieres saber de tu inventario?")
    
    if pregunta and df_contexto is not None:
        contexto_datos = df_contexto.to_string(index=False)
        
        # CAMBIO CLAVE: Usamos gemini-pro en lugar de gemini-1.5-flash
        url = f"https://generativelanguage.googleapis.com/v1/models/gemini-pro:generateContent?key={API_KEY}"
        
        payload = {
            "contents": [{
                "parts": [{
                    "text": f"Eres el administrador del bar 'El Mulato'. Datos de inventario:\n{contexto_datos}\nPregunta: {pregunta}"
                }]
            }]
        }
        
        headers = {'Content-Type': 'application/json'}
        
        try:
            with st.spinner("Consultando al analista (Vía Gemini-Pro)..."):
                response = requests.post(url, headers=headers, data=json.dumps(payload))
                res_json = response.json()
                
                if "candidates" in res_json:
                    texto_respuesta = res_json["candidates"][0]["content"]["parts"][0]["text"]
                    st.markdown("### 💡 Recomendación:")
                    st.write(texto_respuesta)
                else:
                    error_msg = res_json.get('error', {}).get('message', 'Error desconocido')
                    st.error(f"Error de Google: {error_msg}")
                    
        except Exception as e:
            st.error(f"Error de red: {e}")
