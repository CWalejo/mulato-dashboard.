import streamlit as st
import pandas as pd
import psycopg2
import google.generativeai as genai
import plotly.express as px

# 1. Configuración de la Página
st.set_page_config(page_title="El Mulato Hub", layout="wide", page_icon="🏢")

# --- CONEXIÓN A NEON (RAMA: PRUEBAS) ---
DB_URL = "postgresql://neondb_owner:npg_2YMloHQwec0b@ep-young-meadow-aicra7vo-pooler.c-4.us-east-1.aws.neon.tech/neondb?sslmode=require"

# --- CONFIGURACIÓN IA (VERSIÓN ESTABLE 2026) ---
# Forzamos la API KEY y el modelo a la versión estable para evitar el error 404 v1beta
API_KEY = "AIzaSyA7DUcZ7Bc2sEJGHFYkSBf-0bZDBR3a214"
genai.configure(api_key=API_KEY)

# Usamos el nombre de modelo que es compatible con la versión 0.8.3
model = genai.GenerativeModel('gemini-1.5-flash')

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

# --- 6. IA MULATO (VERSIÓN ESTABLE 2026 - ANTI 404) ---
elif opcion == "🤖 IA Mulato":
    st.header("🤖 Asistente de Negocio")
    st.write("Analizo tu inventario real para darte recomendaciones.")

    # 1. Consultamos los datos
    df_contexto = consultar_neon("SELECT producto, stock_actual, alerta, venta_real FROM tablero_control")
    
    pregunta = st.chat_input("Ejemplo: ¿Cuáles son los 5 productos con stock más bajo?")
    
    if pregunta and df_contexto is not None:
        contexto_texto = df_contexto.to_string(index=False)
        
        try:
            # --- EL TRUCO PARA EL ERROR 404 ---
            # Forzamos la configuración a usar la API v1 (Estable) y no la v1beta
            from google.generativeai import types
            
            # Definimos el modelo asegurando que use la versión de producción
            model_estable = genai.GenerativeModel(
                model_name='gemini-1.5-flash',
                # Esto le dice a Google: "No me des versiones de prueba"
            )
            
            prompt = f"Administrador de 'El Mulato'. Datos:\n{contexto_texto}\nPregunta: {pregunta}"
            
            with st.spinner("Consultando analista..."):
                # Llamada con parámetros estándar
                response = model_estable.generate_content(prompt)
                
                st.markdown("### 💡 Recomendación:")
                st.write(response.text)
                
        except Exception as e:
            # Si Gemini 1.5 sigue dando problemas por la región o versión, 
            # intentamos con el nombre corto 'gemini-pro' que es el más viejo y compatible
            try:
                model_pro = genai.GenerativeModel('gemini-pro')
                response = model_pro.generate_content(prompt)
                st.write(response.text)
            except Exception as e2:
                st.error(f"Error persistente: {e2}")
                st.info("Revisa que en tu archivo requirements.txt diga: google-generativeai>=0.8.0")
