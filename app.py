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
    
    # Traemos los datos. Usamos COALESCE para evitar errores si falta la columna categoria en alguna tabla
    df_tablero = consultar_neon("SELECT * FROM tablero_control")
    
    if df_tablero is not None:
        df_tablero["venta_real"] = pd.to_numeric(df_tablero["venta_real"], errors='coerce').fillna(0.0)
        df_tablero["stock_actual"] = pd.to_numeric(df_tablero["stock_actual"], errors='coerce').fillna(0.0)
        
        c1, c2, c3 = st.columns(3)
        criticos = len(df_tablero[df_tablero['alerta'].str.contains("🔴|CRÍTICO", na=False)])
        c1.metric("🔴 Alertas Críticas", criticos)
        c2.metric("📦 Stock Total", f"{df_tablero['stock_actual'].sum():.2f}")
        c3.success("Sincronización Neon OK")

        st.divider()

        # Categorías exactamente como las tenías
        categorias = ["Comida", "Aguardiente", "Ron", "Tequila", "Whisky", "Ginebra", "Vodka", "Vinos", "Otros Licores", "Cervezas", "Pasantes"]
        
        # Obtenemos las categorías reales del maestro para cruzar
        df_maestro = consultar_neon("SELECT producto, categoria FROM maestro_insumos")
        
        if df_maestro is not None:
            # Unimos para recuperar las categorías que se perdieron en el tablero
            df_tablero = df_tablero.drop(columns=['categoria'], errors='ignore').merge(df_maestro, on='producto', how='left')

        for cat in categorias:
            df_cat = df_tablero[df_tablero['categoria'] == cat]

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
    st.header("📤 Actualizar desde Soft (Carga Acumulativa)")
    st.write("Subir el reporte de ventas permite que la IA aprenda el comportamiento histórico.")
    
    archivo = st.file_uploader("Subir reporte de Soft (CSV)", type=["csv"])
    
    if archivo:
        try:
            # 1. Leer el CSV
            df_nuevo = pd.read_csv(archivo)
            
            # Limpieza básica de columnas (ajustar nombres según tu CSV de Soft)
            # Suponemos que el CSV tiene: producto, cantidad_vendida, fecha_inicio, fecha_fin
            
            st.write("预览 datos a cargar:", df_nuevo.head())
            
            if st.button("Confirmar Carga al Historial"):
                # 2. Conexión para insertar
                from sqlalchemy import create_engine
                engine = create_engine(DB_URL)
                
                # 3. CARGA ACUMULATIVA (if_exists='append')
                # Esto es lo que permite que el sistema "tenga memoria"
                df_nuevo.to_sql('historial_ventas', engine, if_exists='append', index=False)
                
                st.success("✅ Datos integrados al historial exitosamente. ¡La IA ahora es más inteligente!")
                st.balloons()
                
        except Exception as e:
            st.error(f"❌ Error al procesar el CSV: {e}")

elif opcion == "🤖 IA Mulato":
    st.header("🤖 Consultor Estratégico El Mulato")
    
    try:
        api_key_openai = st.secrets["OPENAI_API_KEY"]
    except:
        st.error("🔑 Error: No se encontró la OPENAI_API_KEY en los Secrets.")
        st.stop()

    # Traemos datos del TABLERO (Hoy) + HISTORIAL (Pasado) para que la IA analice
    df_inv = consultar_neon("SELECT producto, stock_actual, promedio_venta_diario, alerta, pedido_sugerido FROM tablero_control")
    df_historial = consultar_neon("SELECT producto, SUM(cantidad_vendida) as total_historico FROM historial_ventas GROUP BY producto")
    
    pregunta = st.chat_input("Pregúntame sobre tendencias, qué comprar o cuánto durará el stock...")
    
    if pregunta and df_inv is not None:
        # Creamos un contexto donde la IA sabe qué hay y qué ha pasado
        contexto_ia = f"SITUACIÓN ACTUAL:\n{df_inv.to_string()}\n\nRESUMEN HISTÓRICO:\n{df_historial.to_string()}"
        
        headers = {"Content-Type": "application/json", "Authorization": f"Bearer {api_key_openai}"}
        payload = {
            "model": "gpt-4o-mini",
            "messages": [
                {"role": "system", "content": """Eres el Director de Operaciones de El Mulato. 
                Tu objetivo es evitar que se queden sin stock y optimizar compras.
                Analiza el historial para detectar qué días se vende más.
                Si te preguntan 'qué comprar', prioriza los productos en alerta 🔴 y usa el pedido_sugerido."""},
                {"role": "user", "content": f"Datos del Negocio:\n{contexto_ia}\n\nPregunta del dueño: {pregunta}"}
            ],
            "temperature": 0.3
        }
        
        with st.spinner("Consultando con el cerebro del negocio..."):
            res = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
            if res.status_code == 200:
                respuesta = res.json()["choices"][0]["message"]["content"]
                st.info(respuesta)
            else:
                st.error("Error al conectar con el cerebro de la IA.")
