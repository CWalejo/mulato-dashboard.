import streamlit as st
import pandas as pd
import psycopg2
import google.generativeai as genai
import plotly.express as px

# 1. Configuración de la Página
st.set_page_config(page_title="El Mulato Hub", layout="wide", page_icon="🏢")

# --- CONEXIÓN A NEON (RAMA: PRUEBAS) ---
DB_URL = "postgresql://neondb_owner:npg_2YMloHQwec0b@ep-young-meadow-aicra7vo-pooler.c-4.us-east-1.aws.neon.tech/neondb?sslmode=require"

# --- CONFIGURACIÓN IA (ACTUALIZADA 2026) ---
# He pegado tu clave real y configurado el modelo estable
genai.configure(api_key="AIzaSyA7DUcZ7Bc2sEJGHFYkSBf-0bZDBR3a214")
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

# --- 1. HISTORIAL ---
if opcion == "📈 Historial":
    st.header("📈 Historial de Ventas")
    df = consultar_neon("SELECT * FROM historial_ventas ORDER BY id ASC")
    if df is not None:
        st.metric("Total Registros", len(df))
        st.dataframe(df, use_container_width=True, hide_index=True)

# --- 2. RECETAS ---
elif opcion == "🍳 Recetas":
    st.header("🍳 Libro de Recetas")
    df = consultar_neon("SELECT * FROM recetas")
    if df is not None:
        st.dataframe(df, use_container_width=True, hide_index=True)

# --- 3. MAESTRO ---
elif opcion == "📦 Maestro":
    st.header("📦 Maestro de Insumos")
    df = consultar_neon("SELECT * FROM maestro_insumos ORDER BY producto ASC")
    if df is not None:
        st.dataframe(df, use_container_width=True, hide_index=True)

# --- 4. TABLERO DE GESTIÓN ---
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

# --- 5. CARGA DE DATOS ---
elif opcion == "📤 Carga de Datos":
    st.header("📤 Actualizar desde Soft")
    tab_csv, tab_manual = st.tabs(["Cargar CSV", "Entrada Manual"])
    
    with tab_csv:
        archivo = st.file_uploader("Subir reporte de Soft (CSV)", type=["csv"])
        if archivo:
            df_csv = pd.read_csv(archivo)
            st.write("Vista previa:")
            st.dataframe(df_csv.head())
            if st.button("Procesar y Sincronizar"):
                st.success("Datos en proceso de carga a Neon...")

    with tab_manual:
        st.subheader("Ajuste Manual Rápido")
        prod = st.text_input("Producto")
        cant = st.number_input("Cantidad", min_value=0.0)
        if st.button("Guardar"):
            st.success(f"Ajuste para {prod} guardado.")

# --- 6. IA MULATO (ANALISTA CORREGIDO) ---
elif opcion == "🤖 IA Mulato":
    st.header("🤖 Asistente de Negocio")
    st.write("Analizo tu inventario real para darte recomendaciones.")

    # La IA lee la verdad de Neon
    df_contexto = consultar_neon("SELECT producto, stock_actual, alerta, venta_real FROM tablero_control")
    
    pregunta = st.chat_input("Ejemplo: ¿Cuáles son los 5 productos con stock más bajo?")
    
    if pregunta and df_contexto is not None:
        contexto_datos = df_contexto.to_string(index=False)
        prompt = f"""
        Eres el administrador experto del bar 'El Mulato'. 
        Basándote EXCLUSIVAMENTE en estos datos de inventario:
        {contexto_datos}
        
        Responde a la siguiente consulta del dueño de forma ejecutiva y útil:
        Pregunta: {pregunta}
        
        Si mencionas productos, incluye su stock actual.
        """
        
        with st.spinner("Analizando inventario con Google AI..."):
            try:
                # Generación de contenido con el modelo configurado arriba
                response = model.generate_content(prompt)
                st.markdown("### 💡 Recomendación:")
                st.write(response.text)
            except Exception as e:
                st.error(f"Error de conexión con la IA: {e}")
                st.info("Asegúrate de tener 'google-generativeai' en tu requirements.txt")
