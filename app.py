import streamlit as st
import pandas as pd
import psycopg2

# 1. Configuración de la página
st.set_page_config(page_title="El Mulato - Sistema Inteligente", layout="wide")

# URL de conexión (Asegúrate de que sea la correcta)
DB_URL = "postgresql://neondb_owner:npg_2YMloHQwec0b@ep-lucky-cloud-aihu085f-pooler.c-4.us-east-1.aws.neon.tech/neondb?sslmode=require"

# Función de carga directa (Sin caché)
def cargar_datos_directo(query):
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

# --- DEFINICIÓN DEL MENÚ (ESTO ES LO QUE FALTABA) ---
st.sidebar.title("Menú El Mulato")
opcion = st.sidebar.radio("Sección:", ["📈 Historial", "📦 Inventario", "🚨 Tablero", "🔄 Soft Restaurant", "🤖 Copiloto IA"])

# --- PÁGINA: HISTORIAL ---
if opcion == "📈 Historial":
    st.header("📈 Historial de Ventas")
    
    # BOTÓN DE BORRADO FÍSICO (Para limpiar los 9 registros intrusos)
    with st.expander("🚨 ZONA DE PELIGRO - LIMPIAR TABLA"):
        st.warning("Esto borrará físicamente los datos de 'historial_ventas' en Neon.")
        if st.button("CONFIRMAR: BORRAR TODO EL HISTORIAL"):
            try:
                conn = psycopg2.connect(DB_URL)
                cur = conn.cursor()
                cur.execute("TRUNCATE TABLE historial_ventas RESTART IDENTITY;")
                conn.commit()
                cur.close()
                conn.close()
                st.success("¡Tabla limpiada! Ahora está en 0.")
                st.rerun()
            except Exception as e:
                st.error(f"Error al borrar: {e}")

    # Mostrar datos
    df_hist = cargar_datos_directo("SELECT * FROM historial_ventas ORDER BY id ASC")
    if df_hist is not None:
        st.write(f"📊 Registros en vivo: {len(df_hist)}")
        st.dataframe(df_hist, use_container_width=True, hide_index=True, height=800)

# --- PÁGINA: INVENTARIO ---
elif opcion == "📦 Inventario":
    st.header("📦 Inventario (Maestro de Insumos)")
    df_inv = cargar_datos_directo("SELECT * FROM maestro_insumos ORDER BY categoria, producto")
    if df_inv is not None:
        st.dataframe(df_inv, use_container_width=True, hide_index=True, height=600)

# --- PÁGINA: TABLERO ---
elif opcion == "🚨 Tablero":
    st.header("🚨 Tablero de Control")
    df_tab = cargar_datos_directo("SELECT * FROM tablero_control")
    if df_tab is not None:
        st.dataframe(df_tab, use_container_width=True, hide_index=True)

# --- PÁGINA: SOFT RESTAURANT ---
elif opcion == "🔄 Soft Restaurant":
    st.header("🔄 Carga de Datos")
    st.info("Subir archivo para actualizar historial.")
    archivo = st.file_uploader("Subir reporte", type=['csv', 'xlsx'])

# --- PÁGINA: COPILOTO IA ---
elif opcion == "🤖 Copiloto IA":
    st.header("🤖 Copiloto IA")
    st.write("Análisis inteligente de tendencias.")
