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
    st.header("🚨 Tablero de Gestión - Control de Merma")
    
    # 1. Traemos los datos base
    df_maestro = consultar_neon("SELECT producto, stock_actual, promedio_venta_diario, alerta FROM tablero_control")
    df_recetas = consultar_neon("SELECT nombre_plato, insumo, cantidad_gastada FROM recetas")
    df_ventas = consultar_neon("SELECT producto, cantidad_vendida FROM historial_ventas")
    
    if df_maestro is not None and df_recetas is not None and df_ventas is not None:
        # 2. CALCULAMOS LA VENTA REAL EN DECIMALES (MERMA)
        # Unimos ventas con recetas para saber cuánto de cada insumo se gastó
        ventas_con_receta = df_ventas.merge(df_recetas, left_on='producto', right_on='nombre_plato')
        ventas_con_receta['merma_total'] = ventas_con_receta['cantidad_vendida'] * ventas_con_receta['cantidad_gastada']
        
        # Agrupamos por insumo para tener el total gastado por botella
        resumen_merma = ventas_con_receta.groupby('insumo')['merma_total'].sum().reset_index()
        
        # 3. UNIMOS AL TABLERO PRINCIPAL
        df_final = df_maestro.merge(resumen_merma, left_on='producto', right_on='insumo', how='left')
        df_final['venta_real'] = df_final['merma_total'].fillna(0.0)
        
        # 4. Cálculo de pedido sugerido basado en tu promedio diario
        df_final['pedido_sugerido'] = (df_final['promedio_venta_diario'] * 7) - df_final['stock_actual']
        df_final.loc[df_final['pedido_sugerido'] < 0, 'pedido_sugerido'] = 0

        # KPIs superiores
        c1, c2, c3 = st.columns(3)
        criticos = len(df_final[df_final['alerta'].str.contains("CRÍTICO|🔴", na=False)])
        c1.metric("🔴 Alertas Críticas", criticos)
        c2.metric("📦 Stock Total", f"{df_final['stock_actual'].sum():.2f}")
        c3.success("Merma calculada (0.09/shot)")

        st.divider()

        # Mostramos la tabla con los decimales correctos
        st.dataframe(
            df_final,
            use_container_width=True,
            hide_index=True,
            column_order=("alerta", "producto", "stock_actual", "venta_real", "pedido_sugerido"),
            column_config={
                "alerta": "Estado",
                "producto": "Insumo",
                "stock_actual": st.column_config.NumberColumn("Stock Actual", format="%.2f"),
                "venta_real": st.column_config.NumberColumn("Merma (Botellas)", format="%.2f"),
                "pedido_sugerido": st.column_config.NumberColumn("Sugerido", format="%.2f")
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
