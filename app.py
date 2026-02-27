import streamlit as st
import pandas as pd
import psycopg2

# 1. Configuración de la App
st.set_page_config(page_title="El Mulato - Sistema Inteligente", layout="wide")
DB_URL = "postgresql://neondb_owner:npg_2YMloHQwec0b@ep-lucky-cloud-aihu085f-pooler.c-4.us-east-1.aws.neon.tech/neondb?sslmode=require"

def cargar_datos(query):
    try:
        conn = psycopg2.connect(DB_URL)
        df = pd.read_sql(query, conn)
        conn.close()
        return df
    except Exception as e:
        return None

# --- SEGURIDAD ---
if 'autenticado' not in st.session_state:
    st.session_state['autenticado'] = False

if not st.session_state['autenticado']:
    st.markdown(
        """
        <style>
        .stApp { background-color: #0e1117; }
        .login-container { display: flex; flex-direction: column; align-items: center; justify-content: center; padding-top: 50px; }
        .stButton button { width: 100%; background-color: #f5c518; color: black; font-weight: bold; border: none; height: 3em; }
        .stButton button:hover { background-color: #ffdb4d; color: black; }
        </style>
        """, 
        unsafe_allow_html=True
    )
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<div class='login-container'>", unsafe_allow_html=True)
        # SILUETA LUIS EDUARDO - Link de respaldo estable
        st.image("https://raw.githubusercontent.com/fabiomatav/img/main/mulato_logo.png", width=280)
        st.markdown("<h2 style='text-align: center; color: #f5c518;'>Control de Inventario</h2>", unsafe_allow_html=True)
        
        pin = st.text_input("Ingresa el PIN de acceso:", type="password")
        if st.button("Ingresar al Sistema"):
            if pin == "4321":
                st.session_state['autenticado'] = True
                st.rerun()
            else:
                st.error("PIN Incorrecto")
        st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# --- MENÚ LATERAL ---
st.sidebar.title("Menú El Mulato")
opcion = st.sidebar.radio("Sección:", 
    ["📈 Historial", "🍳 Recetas", "📦 Inventario", "🚨 Tablero", "🔄 Soft Restaurant", "🤖 Copiloto IA"])

# --- PÁGINAS ---
if opcion == "🚨 Tablero":
    st.markdown("<h1 style='color: #FF4B4B;'>🚨 Tablero de Control y Pedidos</h1>", unsafe_allow_html=True)
    
    # Query con el orden jerárquico que necesitas (Aguardientes y Rones primero)
    query_tablero = """
        SELECT * FROM tablero_control 
        ORDER BY 
            CASE 
                WHEN producto LIKE 'Aguardiente%' THEN 1
                WHEN producto LIKE 'Ron %' THEN 2
                WHEN producto LIKE 'Tequila %' THEN 3
                WHEN categoria = 'Licor' THEN 5
                WHEN categoria = 'Pasantes' THEN 7
                WHEN categoria = 'Comida' THEN 8
                ELSE 9 
            END, producto ASC
    """
    df = cargar_datos(query_tablero)
    
    if df is not None:
        # Definimos las columnas exactas de tu tablero funcional
        columnas_visibles = ['producto', 'stock_actual', 'promedio_venta_diario', 'venta_real', 'alerta', 'pedido_sugerido']
        
        # Lógica de colores según el estado de la alerta
        def aplicar_colores(row):
            if 'CRÍTICO' in str(row['alerta']):
                return ['background-color: #ff4b4b; color: white'] * len(row)
            elif 'PEDIR' in str(row['alerta']):
                return ['background-color: #fca311; color: black'] * len(row)
            return [''] * len(row)

        st.dataframe(
            df[columnas_visibles].style.format(precision=2, subset=['stock_actual', 'promedio_venta_diario', 'venta_real', 'pedido_sugerido'])
            .apply(aplicar_colores, axis=1), 
            use_container_width=True, hide_index=True
        )

elif opcion == "📈 Historial":
    st.header("📈 Historial de Ventas")
    query_hist = """
        SELECT h.producto, h.cantidad_vendida, h.fecha_inicio, h.fecha_fin 
        FROM historial_ventas h
        JOIN maestro_insumos m ON TRIM(UPPER(h.producto)) = TRIM(UPPER(m.producto))
        ORDER BY h.fecha_inicio DESC
    """
    df = cargar_datos(query_hist)
    if df is not None: st.dataframe(df, use_container_width=True, hide_index=True)

elif opcion == "📦 Inventario":
    st.header("📦 Gestión de Stock")
    df = cargar_datos("SELECT producto, stock_actual FROM maestro_insumos ORDER BY producto ASC")
    if df is not None: st.dataframe(df, use_container_width=True, hide_index=True)

elif opcion == "🤖 Copiloto IA":
    st.markdown("<h1 style='color: #4A90E2;'>🤖 Copiloto IA - El Mulato</h1>", unsafe_allow_html=True)
    st.info("🧠 El sistema está analizando los datos para optimizar los pedidos sugeridos.")
