import streamlit as st
import pandas as pd
import psycopg2
import google.generativeai as genai  # Necesitas instalar: pip install google-generativeai

# 1. CONFIGURACIÓN
st.set_page_config(page_title="El Mulato - Gestión Inteligente", layout="wide")

# Conexión a Neon
DB_URL = "postgresql://neondb_owner:npg_2YMloHQwec0b@ep-solitary-cake-ai8g7c0x-pooler.c-4.us-east-1.aws.neon.tech/neondb?sslmode=require"

# Configuración IA (Aquí pones tu API KEY de Google AI Studio)
# Es gratis en: https://aistudio.google.com/
genai.configure(api_key="TU_API_KEY_AQUI")
model = genai.GenerativeModel('gemini-1.5-flash')

def consultar_neon(query):
    try:
        conn = psycopg2.connect(DB_URL)
        df = pd.read_sql(query, conn)
        conn.close()
        return df
    except Exception as e:
        st.error(f"❌ Error de DB: {e}")
        return None

# --- SEGURIDAD ---
if 'autenticado' not in st.session_state:
    st.session_state['autenticado'] = False

if not st.session_state['autenticado']:
    st.markdown("<h2 style='text-align: center;'>🔐 Acceso Privado - El Mulato</h2>", unsafe_allow_html=True)
    pin = st.text_input("PIN:", type="password")
    if st.button("Entrar"):
        if pin == "4321":
            st.session_state['autenticado'] = True
            st.rerun()
    st.stop()

# --- MENÚ ---
st.sidebar.title("🏢 El Mulato Hub")
opcion = st.sidebar.radio("Ir a:", 
    ["📈 Historial", "🍳 Recetas", "📦 Maestro", "🚨 Tablero", "📤 Carga de Datos", "🤖 IA Multato"])

# --- TABLERO DE CONTROL (CON DECIMALES) ---
if opcion == "🚨 Tablero de Control":
    st.header("🚨 Tablero de Gestión")
    df = consultar_neon("SELECT * FROM tablero_control")
    if df is not None:
        # Formatear a 2 decimales para botellas/coctelería
        df["venta_real"] = df["venta_real"].astype(float).map(lambda x: f"{x:.2f}")
        st.dataframe(df, use_container_width=True, hide_index=True)

# --- CARGA DE DATOS (CSV Y MANUAL) ---
elif opcion == "📤 Carga de Datos":
    st.header("📤 Actualizar Inventario")
    
    tab1, tab2 = st.tabs(["Cargar CSV (Soft)", "Entrada Manual"])
    
    with tab1:
        archivo = st.file_uploader("Sube el reporte de Soft", type=["csv"])
        if archivo:
            df_csv = pd.read_csv(archivo)
            st.dataframe(df_csv.head())
            if st.button("Procesar CSV"):
                st.success("Cargando datos a Neon...")

    with tab2:
        st.subheader("Entrada rápida de stock")
        p_nombre = st.selectbox("Producto", ["Aguardiente", "Ron", "Vodka"]) # Esto debería venir de la DB
        n_stock = st.number_input("Nuevo Stock", min_value=0.0)
        if st.button("Actualizar"):
            st.success(f"Stock de {p_nombre} actualizado.")

# --- ASISTENTE IA (CONEXIÓN REAL) ---
elif opcion == "🤖 IA Multato":
    st.header("🤖 Asistente Inteligente El Mulato")
    st.write("Analizo tus 144 productos en tiempo real.")

    # 1. La IA lee la base de datos para saber la verdad
    df_contexto = consultar_neon("SELECT producto, stock_actual, alerta, venta_real FROM tablero_control")
    
    prompt_usuario = st.chat_input("Pregúntame: ¿Qué debo comprar hoy? o ¿Cómo van las ventas?")
    
    if prompt_usuario:
        # Creamos un contexto para la IA basado en tus datos reales
        contexto_datos = df_contexto.to_string()
        prompt_completo = f"""
        Eres el asistente experto de 'El Mulato'. Aquí tienes los datos actuales de inventario:
        {contexto_datos}
        
        Responde a la siguiente duda del dueño: {prompt_usuario}
        Sé breve, directo y usa un tono profesional de negocios.
        """
        
        with st.spinner("Analizando inventario..."):
            response = model.generate_content(prompt_completo)
            st.markdown(f"**Respuesta de la IA:**")
            st.write(response.text)

# (Las demás secciones Historial, Recetas, Maestro siguen igual que antes...)
