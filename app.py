import streamlit as st
import pandas as pd
import psycopg2
import plotly.express as px
import requests

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
        df_tablero["venta_real"] = pd.to_numeric(df_tablero["venta_real"], errors='coerce').fillna(0.0)
        df_tablero["stock_actual"] = pd.to_numeric(df_tablero["stock_actual"], errors='coerce').fillna(0.0)
        df_tablero["promedio_venta_diario"] = pd.to_numeric(df_tablero["promedio_venta_diario"], errors='coerce').fillna(0.0)
        
        c1, c2, c3 = st.columns(3)
        criticos = len(df_tablero[df_tablero['alerta'].str.contains("🔴|CRÍTICO", na=False)])
        c1.metric("🔴 Alertas Críticas", criticos)
        c2.metric("📦 Stock Total", f"{df_tablero['stock_actual'].sum():.2f}")
        c3.success("Sincronización Neon OK")

        st.divider()

        categorias = ["Comida", "Aguardiente", "Ron", "Tequila", "Whisky", "Ginebra", "Vodka", "Vinos", "Otros Licores", "Cervezas", "Pasantes"]
        
        df_maestro = consultar_neon("SELECT producto, categoria FROM maestro_insumos")
        
        if df_maestro is not None:
            df_tablero = df_tablero.drop(columns=['categoria'], errors='ignore').merge(df_maestro, on='producto', how='left')

        for cat in categorias:
            df_cat = df_tablero[df_tablero['categoria'] == cat]

            if not df_cat.empty:
                with st.expander(f"📁 {cat.upper()}", expanded=True):
                    st.dataframe(
                        df_cat, 
                        use_container_width=True, 
                        hide_index=True,
                        column_order=("alerta", "producto", "stock_actual", "venta_real", "promedio_venta_diario", "pedido_sugerido"),
                        column_config={
                            "alerta": "Estado",
                            "producto": "Insumo",
                            "stock_actual": st.column_config.NumberColumn("Stock", format="%.2f"),
                            "venta_real": st.column_config.NumberColumn("Venta Real (Shots/Und)", format="%.2f"),
                            "promedio_venta_diario": st.column_config.NumberColumn("Promedio Diario", format="%.2f"),
                            "pedido_sugerido": "Sugerencia"
                        }
                    )

elif opcion == "📤 Carga de Datos":
    st.header("📤 Actualizar desde Soft (Carga Acumulativa)")
    st.write("Subir el reporte de ventas permite que la IA aprenda el comportamiento histórico.")
    
    archivo = st.file_uploader("Subir reporte de Soft (CSV)", type=["csv"])
    
    if archivo:
        try:
            df_nuevo = pd.read_csv(archivo)
            st.write("Vista previa de datos a cargar:", df_nuevo.head())
            
            if st.button("Confirmar Carga al Historial"):
                from sqlalchemy import create_engine
                engine = create_engine(DB_URL)
                df_nuevo.to_sql('historial_ventas', engine, if_exists='append', index=False)
                st.success("✅ Datos integrados al historial exitosamente.")
                st.balloons()
                
        except Exception as e:
            st.error(f"❌ Error al procesar el CSV: {e}")

elif opcion == "🤖 IA Mulato":
    st.header("🧠 Consultor Estratégico El Mulato")
    
    try:
        api_key_openai = st.secrets["OPENAI_API_KEY"]
    except:
        st.error("🔑 Error: No se encontró la OPENAI_API_KEY en los Secrets.")
        st.stop()

    df_inv = consultar_neon("SELECT producto, stock_actual, promedio_venta_diario, alerta, pedido_sugerido FROM tablero_control")
    df_historial = consultar_neon("SELECT producto, SUM(cantidad_vendida) as total_historico FROM historial_ventas GROUP BY producto")
    
    pregunta = st.chat_input("Pregúntame sobre tendencias, qué comprar o cuánto durará el stock...")
    
    if pregunta and df_inv is not None:
        contexto_ia = f"SITUACIÓN ACTUAL:\n{df_inv.to_string()}\n\nRESUMEN HISTÓRICO:\n{df_historial.to_string()}"
        
        headers = {"Content-Type": "application/json", "Authorization": f"Bearer {api_key_openai}"}
        
        payload = {
            "model": "gpt-4o-mini",
            "messages": [
                {
                    "role": "system", 
                    "content": """Eres el Director de Operaciones de El Mulato Cabaret, un gastrobar de alto volumen en Cali. 
                    Tu enfoque no es el de un restaurante familiar, sino el de un centro de espectáculos y rumba.
                    
                    REGLAS DE ANÁLISIS:
                    1. Prioriza el inventario de licores (botellas, medias, shots) y pasantes (tónica, soda), que son el motor del negocio.
                    2. Entiende que los picos de venta son extremos durante los shows y fines de semana.
                    3. Si el stock de un licor líder (como Aguardiente o Tequila) está bajo, sé enfático en la alerta.
                    4. Tus recomendaciones deben ser estratégicas: optimizar compras para eventos masivos y evitar quiebres de stock en plena rumba."""
                },
                {"role": "user", "content": f"Datos del Negocio:\n{contexto_ia}\n\nPregunta: {pregunta}"}
            ],
            "temperature": 0.4
        }
        
        with st.spinner("🧠 El cerebro de El Mulato está analizando los datos..."):
            try:
                res = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload, timeout=60)
                
                if res.status_code == 200:
                    st.info(res.json()["choices"][0]["message"]["content"])
                elif res.status_code == 401:
                    st.error("🚫 Error 401: La API Key no sirve. Revisa los Secrets.")
                elif res.status_code == 429:
                    st.error("💸 Error 429: Sin saldo en OpenAI. ¡Verifica el dashboard!")
                elif res.status_code == 500:
                    st.error("🏢 Error 500: Servidores de OpenAI saturados.")
                else:
                    st.error(f"⚠️ Error {res.status_code}: {res.text}")
                    
            except requests.exceptions.Timeout:
                st.error("⏳ El cerebro se tomó más de 1 minuto. Intenta ser más específico.")
            except Exception as e:
                st.error(f"☢️ Error de conexión: {e}")
