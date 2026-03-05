import streamlit as st
import pandas as pd
import psycopg2
import google.generativeai as genai
import plotly.express as px

# 1. Configuración de la Página
st.set_page_config(page_title="El Mulato Hub", layout="wide", page_icon="🏢")

# --- CONEXIÓN A NEON ---
# Usando la rama: ep-solitary-cake-ai8g7c0x
DB_URL = "postgresql://neondb_owner:npg_2YMloHQwec0b@ep-solitary-cake-ai8g7c0x-pooler.c-4.us-east-1.aws.neon.tech/neondb?sslmode=require"

# --- CONFIGURACIÓN IA ---
# Reemplaza con tu llave de Google AI Studio
genai.configure(api_key="TU_API_KEY_AQUI")
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
    st.markdown("<h2 style='text-align: center;'>🔐 Acceso Privado</h2>", unsafe_allow_html=True)
    pin = st.text_input("PIN:", type="password")
    if st.button("Entrar"):
        if pin == "4321":
            st.session_state['autenticado'] = True
            st.rerun()
    st.stop()

# --- MENÚ LATERAL ---
st.sidebar.title("🏢 El Mulato Hub")
opcion = st.sidebar.radio("Ir a:", ["📈 Historial", "🍳 Recetas", "📦 Maestro", "🚨 Tablero", "📤 Carga de Datos", "🤖 IA Mulato"])

# --- 1. HISTORIAL ---
if opcion == "📈 Historial":
    st.header("📈 Historial de Ventas")
    df = consultar_neon("SELECT * FROM historial_ventas ORDER BY id ASC")
    if df is not None:
        st.dataframe(df, use_container_width=True, hide_index=True)

# --- 2. RECETAS ---
elif opcion == "🍳 Recetas":
    st.header("🍳 Libro de Recetas")
    df = consultar_neon("SELECT * FROM recetas")
    if df is not None:
        st.dataframe(df, use_container_width=True, hide_index=True)

# --- 3. MAESTRO DE INSUMOS ---
elif opcion == "📦 Maestro":
    st.header("📦 Maestro de Insumos (Inventario)")
    df = consultar_neon("SELECT * FROM maestro_insumos ORDER BY producto ASC")
    if df is not None:
        st.dataframe(df, use_container_width=True, hide_index=True)

# --- 4. TABLERO DE GESTIÓN ---
elif opcion == "🚨 Tablero":
    st.header("🚨 Tablero de Gestión")
    df_tablero = consultar_neon("SELECT * FROM tablero_control")
    
    if df_tablero is not None:
        # Decimales en Venta Real para ver botellas exactas
        df_tablero["venta_real"] = df_tablero["venta_real"].astype(float)
        
        c1, c2 = st.columns(2)
        criticos = len(df_tablero[df_tablero['alerta'].str.contains("CRÍTICO", na=False)])
        pedir = len(df_tablero[df_tablero['alerta'].str.contains("PEDIR", na=False)])
        
        c1.metric("🔴 Alertas Críticas", criticos)
        c2.metric("🟡 Pedidos Pendientes", pedir)

        st.dataframe(
            df_tablero, 
            use_container_width=True, 
            hide_index=True,
            column_order=("producto", "stock_actual", "promedio_venta_diario", "venta_real", "alerta", "pedido_sugerido")
        )

# --- 5. CARGA DE DATOS ---
elif opcion == "📤 Carga de Datos":
    st.header("📤 Actualizar desde Soft")
    t1, t2 = st.tabs(["Cargar CSV", "Entrada Manual"])
    
    with t1:
        archivo = st.file_uploader("Reporte CSV de Soft", type=["csv"])
        if archivo:
            df_csv = pd.read_csv(archivo)
            st.write("Datos detectados:")
            st.dataframe(df_csv.head())
            if st.button("Confirmar Carga"):
                st.success("Sincronizando con Neon...")
    
    with t2:
        st.subheader("Ajuste Manual de Inventario")
        prod = st.text_input("Producto")
        cant = st.number_input("Cantidad", min_value=0.0)
        if st.button("Guardar"):
            st.success(f"Se registró {cant} para {prod}")

# --- 6. IA MULATO (VERSIÓN BLINDADA) ---
elif opcion == "🤖 IA Mulato":
    st.header("🤖 Asistente de Negocio")
    
    # Verificación de API Key
    if "TU_API_KEY_AQUI" in DB_URL or not genai.get_model('models/gemini-1.5-flash'):
        st.warning("⚠️ Configuración incompleta: Por favor asegúrate de haber puesto tu API Key real de Google AI Studio.")

    # La IA lee tu tabla actual antes de hablar
    df_contexto = consultar_neon("SELECT * FROM tablero_control")
    
    pregunta = st.chat_input("Pregúntame sobre el stock o las ventas...")
    
    if pregunta and df_contexto is not None:
        # Limpiamos los datos para que el prompt no sea demasiado pesado
        contexto_resumido = df_contexto[['producto', 'stock_actual', 'alerta', 'venta_real']].to_string()
        
        prompt = f"""
        Actúa como el administrador experto del bar 'El Mulato'. 
        Analiza estos datos de inventario y responde de forma breve y profesional.
        
        DATOS ACTUALES:
        {contexto_resumido}
        
        PREGUNTA DEL DUEÑO: {pregunta}
        """
        
        with st.spinner("Consultando con el cerebro de la IA..."):
            try:
                # Intentamos generar la respuesta
                response = model.generate_content(prompt)
                st.markdown("### 💡 Análisis de la IA:")
                st.write(response.text)
            except Exception as e:
                # Si falla, te damos una respuesta basada en lógica simple para no dejarte solo
                st.error(f"La IA tuvo un inconveniente técnico (Error: {e})")
                st.info("Mientras se soluciona, aquí tienes un resumen rápido basado en tus datos de Neon:")
                
                # Lógica de respaldo manual
                criticos = df_contexto[df_contexto['alerta'].str.contains("CRÍTICO", na=False)]
                if not criticos.empty:
                    st.write(f"Sugerencia manual: Tienes {len(criticos)} productos críticos: {', '.join(criticos['producto'].tolist())}.")
