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
        .login-box {
            background-color: #1f2937;
            padding: 30px;
            border-radius: 15px;
            border: 2px solid #f5c518;
            text-align: center;
        }
        </style>
        """, unsafe_allow_html=True
    )
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<div class='login-box'>", unsafe_allow_html=True)
        # Usamos un logo genérico de alta disponibilidad para asegurar que cargue
        st.image("https://www.gstatic.com/lamda/images/gemini_sparkle_v002_d473530437e35193457a.svg", width=100)
        st.markdown("<h2 style='color: #f5c518;'>Control El Mulato</h2>", unsafe_allow_html=True)
        
        pin = st.text_input("PIN de Acceso:", type="password")
        if st.button("Entrar"):
            if pin == "4321":
                st.session_state['autenticado'] = True
                st.rerun()
            else:
                st.error("PIN Incorrecto")
        st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# --- MENÚ ---
st.sidebar.title("Menú El Mulato")
opcion = st.sidebar.radio("Sección:", 
    ["📈 Historial", "🍳 Recetas", "📦 Inventario", "🚨 Tablero", "🔄 Soft Restaurant", "🤖 Copiloto IA"])

# --- PÁGINAS ---
if opcion == "📈 Historial":
    st.header("📈 Historial de Ventas")
    query_hist = "SELECT * FROM historial_ventas" # Simplificado para probar conexión
    df = cargar_datos(query_hist)
    if df is not None: st.dataframe(df, use_container_width=True, hide_index=True)

elif opcion == "🚨 Tablero":
    st.header("🚨 Tablero de Control")
    df = cargar_datos("SELECT * FROM tablero_control")
    if df is not None:
        st.dataframe(df, use_container_width=True, hide_index=True)

elif opcion == "🤖 Copiloto IA":
    st.info("🧠 Analizando patrones de movimiento...")
