import streamlit as st
import pandas as pd
import psycopg2
import plotly.express as px

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
    df = consultar_neon("SELECT * FROM recetas")
    if df is not None:
        st.dataframe(df, use_container_width=True, hide_index=True)

elif opcion == "📦 Maestro":
    st.header("📦 Maestro de Insumos")
    df = consultar_neon("SELECT * FROM maestro_insumos")
    if df is not None:
        st.dataframe(df, use_container_width=True, hide_index=True)

elif opcion == "🚨 Tablero":
    st.header("🚨 Tablero de Gestión")
    
    df_tablero = consultar_neon("SELECT * FROM tablero_control")
    
    if df_tablero is not None:
        # Forzamos que sean números con decimales
        df_tablero["venta_real"] = pd.to_numeric(df_tablero["venta_real"], errors='coerce').fillna(0.0)
        df_tablero["stock_actual"] = pd.to_numeric(df_tablero["stock_actual"], errors='coerce').fillna(0.0)
        
        c1, c2, c3 = st.columns(3)
        criticos = len(df_tablero[df_tablero['alerta'].str.contains("🔴", na=False)])
        c1.metric("🔴 Alertas Críticas", criticos)
        c2.metric("📦 Stock Total", f"{df_tablero['stock_actual'].sum():.2f}")
        c3.success("Sincronización Neon OK")

        st.divider()

        # Categorías según el orden que establecimos
        categorias = ["Comida", "Aguardiente", "Ron", "Tequila", "Whisky", "Ginebra", "Vodka", "Vinos", "Otros Licores", "Cervezas", "Pasantes"]
        
        for cat in categorias:
            if 'categoria' in df_tablero.columns:
                df_cat = df_tablero[df_tablero['categoria'] == cat]
            else:
                # Si no existe la columna en tablero, mostramos todo
                df_cat = df_tablero
                if cat != "Comida": break # Evita repetir si no hay categorías

            if not df_cat.empty:
                with st.expander(f"📁 {cat.upper()}", expanded=True):
                    st.dataframe(
                        df_cat, 
                        use_container_width=True, 
                        hide_index=True,
                        column_order=("alerta", "producto", "stock_actual", "venta_real", "pedido_sugerido"),
                        column_config={
                            "alerta": "Estado",
                            "producto": "Insumo",
                            "stock_actual": st.column_config.NumberColumn("Stock", format="%.2f"),
                            "venta_real": st.column_config.NumberColumn("Venta Real (Shots/Und)", format="%.2f"),
                            "pedido_sugerido": "Sugerencia"
                        }
                    )

elif opcion == "📤 Carga de Datos":
    st.header("📤 Actualizar desde Soft")
    archivo = st.file_uploader("Subir reporte de Soft (CSV)", type=["csv"])
    if archivo:
        st.info("Archivo recibido. Mañana activaremos el procesamiento.")

elif opcion == "🤖 IA Mulato":
    st.header("🤖 Consultor Estratégico El Mulato")
    
    # Intentamos cargar la llave desde los Secrets seguros
    try:
        api_key_openai = st.secrets["OPENAI_API_KEY"]
    except:
        st.error("🔑 Error: No se encontró la OPENAI_API_KEY en los Secrets de Streamlit.")
        st.stop()

    # Traemos los datos de Neon (Recetas de 0.09 y Inventario)
    df_inv = consultar_neon("SELECT categoria, producto, stock_actual, venta_real, alerta FROM tablero_control")
    df_rec = consultar_neon("SELECT nombre_plato, insumo, cantidad_gastada FROM recetas")
    
    pregunta = st.chat_input("Ej: ¿Cuántos Gin Tonic puedo vender con lo que hay?")
    
    if pregunta:
        if df_inv is not None and df_rec is not None:
            contexto_ia = f"STOCK:\n{df_inv.to_string()}\n\nRECETAS:\n{df_rec.to_string()}"
            
            headers = {"Content-Type": "application/json", "Authorization": f"Bearer {api_key_openai}"}
            payload = {
                "model": "gpt-4o-mini",
                "messages": [
                    {"role": "system", "content": "Eres el socio analista de El Mulato. Usa los decimales 0.09 de las recetas para calcular ventas posibles."},
                    {"role": "user", "content": f"Datos:\n{contexto_ia}\n\nPregunta: {pregunta}"}
                ],
                "temperature": 0.2
            }
            
            with st.spinner("Analizando con IA..."):
                res = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
                if res.status_code == 200:
                    st.info(res.json()["choices"][0]["message"]["content"])
                else:
                    st.error("Revisa el saldo de tu cuenta de OpenAI (Billing).")
