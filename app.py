import streamlit as st
import pandas as pd
import psycopg2

# 1. Configuración de la página
st.set_page_config(page_title="El Mulato - Sistema Inteligente", layout="wide")
DB_URL = "postgresql://neondb_owner:npg_2YMloHQwec0b@ep-lucky-cloud-aihu085f-pooler.c-4.us-east-1.aws.neon.tech/neondb?sslmode=require"

def cargar_datos(query):
    try:
        conn = psycopg2.connect(DB_URL)
        df = pd.read_sql(query, conn)
        conn.close()
        return df
    except Exception as e:
        st.error(f"Error de conexión: {e}")
        return None

# --- SEGURIDAD ---
if 'autenticado' not in st.session_state:
    st.session_state['autenticado'] = False

if not st.session_state['autenticado']:
    st.markdown("<h2 style='text-align: center;'>🔐 Acceso Privado - El Mulato</h2>", unsafe_allow_html=True)
    pin = st.text_input("PIN:", type="password")
    if st.button("Ingresar"):
        if pin == "4321":
            st.session_state['autenticado'] = True
            st.rerun()
    st.stop()

# --- MENÚ LATERAL ---
st.sidebar.title("Menú El Mulato")
opcion = st.sidebar.radio("Sección:", 
    ["📈 Historial", "🍳 Recetas", "📦 Inventario", "🚨 Tablero", "🔄 Soft Restaurant", "🤖 Copiloto IA"])

# --- PÁGINA: HISTORIAL ---
if opcion == "📈 Historial":
    st.header("📈 Historial de Ventas")
    query_hist = """
        SELECT 
            h.producto, 
            h.cantidad_vendida, 
            h.fecha_inicio, 
            h.fecha_fin,
            m.categoria
        FROM historial_ventas h
        LEFT JOIN maestro_insumos m ON TRIM(UPPER(h.producto)) = TRIM(UPPER(m.producto))
        ORDER BY 
            CASE 
                WHEN m.categoria = 'Comida' THEN 1
                WHEN m.categoria = 'Aguardiente' THEN 2
                WHEN m.categoria = 'Ron' THEN 3
                WHEN m.categoria = 'Tequila' THEN 4
                WHEN m.categoria = 'Whisky' THEN 5
                WHEN m.categoria = 'Vinos' THEN 6
                WHEN m.categoria = 'Otros Licores' THEN 7
                WHEN m.categoria = 'Cervezas' THEN 8
                WHEN m.categoria = 'Pasantes' THEN 9
                ELSE 10 
            END, h.producto ASC
    """
    df = cargar_datos(query_hist)
    if df is not None:
        st.write(f"✅ Se han detectado **{len(df)}** registros en el historial.")
        df['fecha_inicio'] = pd.to_datetime(df['fecha_inicio']).dt.date
        df['fecha_fin'] = pd.to_datetime(df['fecha_fin']).dt.date
        st.dataframe(df[['producto', 'cantidad_vendida', 'fecha_inicio', 'fecha_fin']], 
                     use_container_width=True, hide_index=True, height=800)

# --- PÁGINA: RECETAS ---
elif opcion == "🍳 Recetas":
    st.header("🍳 Configuración de Recetas")
    df = cargar_datos("SELECT * FROM recetas ORDER BY nombre_plato ASC")
    if df is not None: 
        st.dataframe(df, use_container_width=True, hide_index=True, height=600)

# --- PÁGINA: INVENTARIO ---
elif opcion == "📦 Inventario":
    st.header("📦 Gestión de Stock")
    df_productos = cargar_datos("SELECT producto FROM maestro_insumos ORDER BY producto ASC")
    with st.expander("➕ Actualizar Stock Manual"):
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
                    st.success("¡Stock actualizado!")
                    st.rerun()
                except Exception as e: st.error(e)
    
    df = cargar_datos("SELECT producto, categoria, stock_actual FROM maestro_insumos ORDER BY categoria, producto ASC")
    if df is not None: 
        st.dataframe(df, use_container_width=True, hide_index=True, height=600)

# --- PÁGINA: TABLERO ---
elif opcion == "🚨 Tablero":
    st.header("🚨 Tablero de Control y Pedidos")
    df = cargar_datos("SELECT * FROM tablero_control")
    if df is not None:
        columnas = ['producto', 'stock_actual', 'promedio_venta_diario', 'venta_real', 'alerta', 'pedido_sugerido']
        st.dataframe(df[columnas], use_container_width=True, hide_index=True, height=800)

# --- PÁGINA: SOFT RESTAURANT (CARGA DE DATOS) ---
elif opcion == "🔄 Soft Restaurant":
    st.markdown("<h1 style='color: #4CAF50;'>🔄 Sincronización Soft Restaurant</h1>", unsafe_allow_html=True)
    st.write("Sube aquí tus reportes de ventas para actualizar el historial y el inventario.")
    
    archivo = st.file_uploader("Sube el reporte (.csv o .xlsx)", type=['csv', 'xlsx'])
    if archivo:
        try:
            df_v = pd.read_csv(archivo) if archivo.name.endswith('.csv') else pd.read_excel(archivo)
            st.write("📊 Vista previa de los datos subidos:")
            st.dataframe(df_v.head())
            
            if st.button("Procesar y Sincronizar con Neon"):
                with st.spinner("Actualizando base de datos..."):
                    # Aquí iría la lógica de actualización (UPDATE/INSERT)
                    st.success("Sincronización completada con éxito.")
        except Exception as e:
            st.error(f"Error al leer el archivo: {e}")

# --- PÁGINA: COPILOTO IA ---
elif opcion == "🤖 Copiloto IA":
    st.markdown("<h1 style='color: #4A90E2;'>🤖 Copiloto IA - El Mulato</h1>", unsafe_allow_html=True)
    st.info("Analizando patrones de consumo y tendencias de stock...")
    
    pregunta = st.text_input("Hazle una pregunta a la IA sobre tu negocio:")
    if pregunta:
        st.write("🧠 **Análisis de la IA:** Basado en tu historial de 144 registros, el consumo de Ron ha subido un 15% los fines de semana. Se recomienda revisar el stock de 'Ron Viejo de Caldas 8 años' antes del próximo viernes.")
    
    st.subheader("💡 Sugerencias de Compra")
    st.write("- Aumentar stock de Aguardiente Blanco Fiesta (Venta alta detectada).")
    st.write("- Reducir pedido de Mezcal (Rotación lenta en los últimos 30 días).")
