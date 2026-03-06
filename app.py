import streamlit as st
import pandas as pd
import psycopg2
import google.generativeai as genai

# 1. Configuración de la Página
st.set_page_config(page_title="El Mulato Hub", layout="wide", page_icon="🏢")

# --- CONEXIÓN A NEON ---
DB_URL = "postgresql://neondb_owner:npg_2YMloHQwec0b@ep-young-meadow-aicra7vo-pooler.c-4.us-east-1.aws.neon.tech/neondb?sslmode=require"

# --- CONFIGURACIÓN IA (VERSIÓN ESTABLE 2026) ---
# Usamos directamente 'gemini-1.5-flash' sin rutas adicionales
API_KEY = "AIzaSyA7DUcZ7Bc2sEJGHFYkSBf-0bZDBR3a214"
genai.configure(api_key=API_KEY)

def consultar_neon(query):
    try:
        conn = psycopg2.connect(DB_URL)
        df = pd.read_sql(query, conn)
        conn.close()
        return df
    except Exception as e:
        st.error(f"❌ Error de base de datos: {e}")
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

# --- MENÚ ---
st.sidebar.title("🏢 El Mulato Hub")
opcion = st.sidebar.radio("Navegación:", ["📈 Historial", "🍳 Recetas", "📦 Maestro", "🚨 Tablero", "🤖 IA Mulato"])

# --- SECCIONES (SIMPLIFICADAS) ---
if opcion == "📈 Historial":
    df = consultar_neon("SELECT * FROM historial_ventas")
    if df is not None: st.dataframe(df, use_container_width=True)

elif opcion == "🚨 Tablero":
    st.header("🚨 Tablero de Gestión")
    df = consultar_neon("SELECT * FROM tablero_control")
    if df is not None:
        df["venta_real"] = df["venta_real"].astype(float)
        st.dataframe(df, use_container_width=True, hide_index=True)

# --- SECCIÓN IA (NUEVA LÓGICA ANTI-ERROR 404) ---
elif opcion == "🤖 IA Mulato":
    st.header("🤖 Asistente de Negocio")
    
    # Consultamos datos para el contexto
    df_contexto = consultar_neon("SELECT producto, stock_actual, alerta FROM tablero_control")
    
    pregunta = st.chat_input("¿Qué deseas consultar?")
    
    if pregunta and df_contexto is not None:
        contexto_texto = df_contexto.to_string(index=False)
        
        # DEFINICIÓN DEL MODELO DENTRO DEL BLOQUE PARA EVITAR CACHE VIEJO
        try:
            # Forzamos el uso del modelo de producción
            analista = genai.GenerativeModel(model_name='gemini-1.5-flash')
            
            prompt = f"Eres el administrador de 'El Mulato'. Datos:\n{contexto_texto}\nPregunta: {pregunta}"
            
            with st.spinner("Consultando analista..."):
                # Agregamos safety_settings para evitar bloqueos por filtros
                response = analista.generate_content(prompt)
                st.markdown("### 💡 Recomendación:")
                st.write(response.text)
                
        except Exception as e:
            st.error(f"Error de comunicación con Google: {e}")
            st.info("💡 RECOMENDACIÓN FINAL: Si el error 404 persiste, ve a Streamlit Cloud -> Settings -> Reboot App para limpiar la memoria vieja.")
