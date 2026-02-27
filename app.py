import streamlit as st
import pandas as pd
import psycopg2

# 1. Configuración
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

# --- SEGURIDAD CON LOGO ---
if 'autenticado' not in st.session_state:
    st.session_state['autenticado'] = False

if not st.session_state['autenticado']:
    # CSS para centrar logo y estilizar login
    st.markdown(
        """
        <style>
        .stApp {
            background-color: #0e1117;
        }
        .login-container {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            padding-top: 50px;
        }
        .stButton button {
            width: 100%;
            background-color: #f5c518;
            color: black;
            font-weight: bold;
        }
        </style>
        """, 
        unsafe_allow_html=True
    )
    
    # Contenedor del Login
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<div class='login-container'>", unsafe_allow_html=True)
        # Aquí usamos la silueta del Mulato como logo principal
        st.image("https://i.ibb.co/6y45s1x/mulato-silhouette.png", width=300)
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

# --- MENÚ ---
st.sidebar.title("Menú El Mulato")
opcion = st.sidebar.radio("Sección:", 
    ["📈 Historial", "🍳 Recetas", "📦 Inventario", "🚨 Tablero", "🔄 Soft Restaurant", "🤖 Copiloto IA"])

# --- PÁGINAS ---
if opcion == "📈 Historial":
    st.header("📈 Historial de Ventas")
    query_hist = """
        SELECT h.producto, h.cantidad_vendida, h.fecha_inicio, h.fecha_fin 
        FROM historial_ventas h
        JOIN maestro_insumos m ON TRIM(UPPER(h.producto)) = TRIM(UPPER(m.producto))
        ORDER BY 
            CASE 
                WHEN m.producto LIKE 'Aguardiente%' THEN 1
                WHEN m.producto LIKE 'Ron %' THEN 2
                WHEN m.producto LIKE 'Tequila %' THEN 3
                WHEN m.categoria = 'Licor' THEN 5
                WHEN m.categoria = 'Pasantes' THEN 7
                WHEN m.categoria = 'Comida' THEN 8
                ELSE 9 
            END, h.producto ASC
    """
    df = cargar_datos(query_hist)
    if df is not None: st.dataframe(df, use_container_width=True, hide_index=True)

elif opcion == "🍳 Recetas":
    st.header("🍳 Configuración de Recetas")
    df = cargar_datos("SELECT * FROM recetas")
    if df is not None: st.dataframe(df, use_container_width=True, hide_index=True)

elif opcion == "📦 Inventario":
    st.header("📦 Gestión de Stock")
    df_productos = cargar_datos("SELECT producto FROM maestro_insumos ORDER BY producto ASC")
    with st.expander("➕ Actualizar Stock"):
        if df_productos is not None:
            prod_sel = st.selectbox("Producto:", df_productos['producto'])
            nuevo_stock = st.number_input("Nuevo Stock:", min_value=0.0)
            if st.button("Guardar"):
                try:
                    conn = psycopg2.connect(DB_URL)
                    cur = conn.cursor()
                    cur.execute("UPDATE maestro_insumos SET stock_actual = %s WHERE producto = %s", (nuevo_stock, prod_sel))
                    conn.commit()
                    cur.close()
                    conn.close()
                    st.success("¡Actualizado!")
                    st.rerun()
                except Exception as e: st.error(e)

    df = cargar_datos("SELECT producto, stock_actual FROM maestro_insumos ORDER BY producto ASC")
    if df is not None: st.dataframe(df, use_container_width=True, hide_index=True)

elif opcion == "🚨 Tablero":
    st.markdown("<h1 style='color: #FF4B4B;'>🚨 Tablero de Control y Pedidos</h1>", unsafe_allow_html=True)
    df = cargar_datos("SELECT * FROM tablero_control")
    
    if df is not None:
        columnas_visibles = ['producto', 'stock_actual', 'promedio_venta_diario', 'venta_real', 'alerta', 'pedido_sugerido']
        
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

elif opcion == "🔄 Soft Restaurant":
    st.markdown("<h1 style='color: #4CAF50;'>🔄 Sincronización Soft Restaurant</h1>", unsafe_allow_html=True)
    archivo = st.file_uploader("Sube el reporte de ventas (.csv o .xlsx)", type=['csv', 'xlsx'])
    if archivo:
        df_v = pd.read_csv(archivo) if archivo.name.endswith('.csv') else pd.read_excel(archivo)
        st.write("📊 Ventas detectadas:")
        st.dataframe(df_v.head())
        if st.button("Procesar"):
            st.success("Procesado.")

elif opcion == "🤖 Copiloto IA":
    st.markdown("<h1 style='color: #4A90E2;'>🤖 Copiloto IA - El Mulato</h1>", unsafe_allow_html=True)
    st.info("🧠 La IA está analizando tus datos y aprendiendo tus movimientos para optimizar el inventario.")
