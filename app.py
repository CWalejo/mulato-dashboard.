import streamlit as st
import pandas as pd
import psycopg2

# 1. Configuración de la página
st.set_page_config(page_title="El Mulato - Sistema Oficial", layout="wide")

# Credenciales de Neon
DB_URL = "postgresql://neondb_owner:npg_2YMloHQwec0b@ep-lucky-cloud-aihu085f-pooler.c-4.us-east-1.aws.neon.tech/neondb?sslmode=require"

def cargar_datos(query):
    try:
        conn = psycopg2.connect(DB_URL)
        df = pd.read_sql(query, conn)
        conn.close()
        return df
    except Exception as e:
        return None

# --- SISTEMA DE SEGURIDAD (PIN) ---
if 'autenticado' not in st.session_state:
    st.session_state['autenticado'] = False

if not st.session_state['autenticado']:
    st.markdown("<h2 style='text-align: center;'>🔐 Acceso Privado - El Mulato</h2>", unsafe_allow_html=True)
    pin_ingresado = st.text_input("Introduce el PIN de 4 dígitos:", type="password")
    if st.button("Ingresar"):
        if pin_ingresado == "1234":  # <--- AQUÍ CAMBIAS EL PIN
            st.session_state['autenticado'] = True
            st.rerun()
        else:
            st.error("PIN Incorrecto. Intenta de nuevo.")
    st.stop()

# --- SI ESTÁ AUTENTICADO, MUESTRA EL MENÚ ---
st.sidebar.title("Menú El Mulato")
opcion = st.sidebar.radio("Selecciona una sección:", 
    ["📈 Historial de Ventas", "🍳 Recetas y Costos", "📦 Inventario Real", "🚨 Tablero de Control"])

# --- PÁGINA 1: HISTORIAL ---
if opcion == "📈 Historial de Ventas":
    st.markdown("<h1 style='color: #D4AF37;'>📈 Ventas Acumuladas</h1>", unsafe_allow_html=True)
    df = cargar_datos("SELECT producto, cantidad_vendida, fecha_inicio, fecha_fin FROM historial_ventas ORDER BY cantidad_vendida DESC")
    if df is not None:
        st.dataframe(df, use_container_width=True)

# --- PÁGINA 2: RECETAS ---
elif opcion == "🍳 Recetas y Costos":
    st.header("🍳 Configuración de Recetas")
    df = cargar_datos("SELECT * FROM recetas")
    if df is not None:
        st.dataframe(df, use_container_width=True)

# --- PÁGINA 3: INVENTARIO (CON ACTUALIZADOR) ---
elif opcion == "📦 Inventario Real":
    st.header("📦 Gestión de Stock en Bodega")
    
    # Formulario para actualizar stock
    with st.expander("➕ Actualizar Stock (Coordinador)"):
        df_productos = cargar_datos("SELECT producto FROM maestro_insumos ORDER BY producto ASC")
        if df_productos is not None:
            prod_sel = st.selectbox("Selecciona el producto:", df_productos['producto'])
            nuevo_stock = st.number_input("Nuevo Stock Físico:", min_value=0.0)
            if st.button("Guardar Cambios"):
                try:
                    conn = psycopg2.connect(DB_URL)
                    cur = conn.cursor()
                    cur.execute("UPDATE maestro_insumos SET stock_actual = %s WHERE producto = %s", (nuevo_stock, prod_sel))
                    conn.commit()
                    cur.close()
                    conn.close()
                    st.success(f"¡{prod_sel} actualizado a {nuevo_stock} unidades!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error al actualizar: {e}")

    df = cargar_datos("SELECT producto, stock_actual FROM maestro_insumos ORDER BY producto ASC")
    if df is not None:
        st.dataframe(df, use_container_width=True)

# --- PÁGINA 4: TABLERO (ALERTAS) ---
elif opcion == "🚨 Tablero de Control":
    st.markdown("<h1 style='color: #FF4B4B;'>🚨 Alertas de Reabastecimiento</h1>", unsafe_allow_html=True)
    df = cargar_datos("SELECT * FROM tablero_control ORDER BY promedio_venta_diario DESC")
    if df is not None:
        def color_alertas(row):
            if row['alerta'] == 'CRÍTICO': return ['background-color: #ff4b4b; color: white'] * len(row)
            elif row['alerta'] == 'PEDIR': return ['background-color: #fca311; color: black'] * len(row)
            return [''] * len(row)
        st.dataframe(df.style.apply(color_alertas, axis=1), use_container_width=True)
