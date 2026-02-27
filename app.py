import streamlit as st
import pandas as pd
import psycopg2

# 1. Configuración de la App
st.set_page_config(page_title="El Mulato - Sistema Inteligente", layout="wide")
DB_URL = "postgresql://neondb_owner:npg_2YMloHQwec0b@ep-lucky-cloud-aihu085f-pooler.c-4.us-east-1.aws.neon.tech/neondb?sslmode=require"

# --- DISEÑO GLOBAL: EL MULATO EN TODO LUGAR ---
def aplicar_estilo_mulato():
    st.markdown(
        """
        <style>
        /* Fondo con la silueta del Mulato fija en el centro */
        .stApp {
            background-image: url("https://raw.githubusercontent.com/fabiomatav/img/main/mulato_logo.png");
            background-attachment: fixed;
            background-size: 600px; /* Ajusta el tamaño de la silueta aquí */
            background-position: center;
            background-repeat: no-repeat;
            background-color: #0e1117; /* Fondo oscuro base */
        }
        
        /* Capa oscura para que el texto se lea bien sobre la imagen */
        .stApp::before {
            content: "";
            position: fixed;
            top: 0; left: 0; width: 100%; height: 100%;
            background-color: rgba(14, 17, 23, 0.85); /* Oscurece el fondo */
            z-index: -1;
        }

        /* Estilo para tablas y contenedores para que resalten */
        .stDataFrame, .stMarkdown, div[data-testid="stExpander"] {
            background-color: rgba(30, 30, 30, 0.9) !important;
            padding: 10px;
            border-radius: 10px;
            border: 1px solid #f5c518;
        }

        /* Títulos en dorado Mulato */
        h1, h2, h3 {
            color: #f5c518 !important;
        }
        
        /* Botones personalizados */
        .stButton button {
            background-color: #f5c518 !important;
            color: black !important;
            font-weight: bold;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

aplicar_estilo_mulato()

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
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<br><br><h2 style='text-align: center;'>🔐 Acceso El Mulato</h2>", unsafe_allow_html=True)
        pin = st.text_input("PIN:", type="password")
        if st.button("Ingresar"):
            if pin == "4321":
                st.session_state['autenticado'] = True
                st.rerun()
            else:
                st.error("PIN Incorrecto")
    st.stop()

# --- MENÚ ---
st.sidebar.title("Menú Principal")
opcion = st.sidebar.radio("Ir a:", ["🚨 Tablero", "📦 Inventario", "📈 Historial", "🤖 Copiloto IA"])

# --- TABLERO (Restaurado con tu lógica de colores) ---
if opcion == "🚨 Tablero":
    st.header("🚨 Tablero de Control y Pedidos")
    query = """
        SELECT * FROM tablero_control 
        ORDER BY 
            CASE 
                WHEN producto LIKE 'Aguardiente%' THEN 1
                WHEN producto LIKE 'Ron %' THEN 2
                WHEN categoria = 'Licor' THEN 5
                ELSE 9 
            END, producto ASC
    """
    df = cargar_datos(query)
    if df is not None:
        def aplicar_colores(row):
            if 'CRÍTICO' in str(row['alerta']):
                return ['background-color: #ff4b4b; color: white'] * len(row)
            elif 'PEDIR' in str(row['alerta']):
                return ['background-color: #fca311; color: black'] * len(row)
            return [''] * len(row)

        st.dataframe(
            df[['producto', 'stock_actual', 'promedio_venta_diario', 'venta_real', 'alerta', 'pedido_sugerido']]
            .style.apply(aplicar_colores, axis=1), 
            use_container_width=True, hide_index=True
        )

# --- INVENTARIO ---
elif opcion == "📦 Inventario":
    st.header("📦 Gestión de Stock")
    df = cargar_datos("SELECT producto, stock_actual FROM maestro_insumos ORDER BY producto ASC")
    if df is not None:
        st.dataframe(df, use_container_width=True, hide_index=True)

# --- RESTO DE PÁGINAS ---
else:
    st.info(f"Sección {opcion} cargada. La silueta del Mulato te acompaña de fondo.")
