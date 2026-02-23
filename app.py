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

# --- SISTEMA DE SEGURIDAD ---
if 'autenticado' not in st.session_state:
    st.session_state['autenticado'] = False

if not st.session_state['autenticado']:
    st.markdown("<h2 style='text-align: center;'>🔐 Acceso Privado - El Mulato</h2>", unsafe_allow_html=True)
    pin_ingresado = st.text_input("Introduce el PIN de 4 dígitos:", type="password")
    if st.button("Ingresar"):
        if pin_ingresado == "4321":
            st.session_state['autenticado'] = True
            st.rerun()
        else:
            st.error("PIN Incorrecto.")
    st.stop()

# --- MENÚ ---
st.sidebar.title("Menú El Mulato")
opcion = st.sidebar.radio("Selecciona una sección:", 
    ["📈 Historial de Ventas", "🍳 Recetas y Costos", "📦 Inventario Real", "🚨 Tablero de Control"])

# --- PÁGINA 1: HISTORIAL ---
if opcion == "📈 Historial de Ventas":
    st.markdown("<h1 style='color: #D4AF37;'>📈 Historial de Ventas</h1>", unsafe_allow_html=True)
    query_historial = """
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
    df = cargar_datos(query_historial)
    if df is not None:
        st.dataframe(df.style.format(precision=2), use_container_width=True, hide_index=True)

# --- PÁGINA 2: RECETAS ---
elif opcion == "🍳 Recetas y Costos":
    st.header("🍳 Configuración de Recetas")
    df = cargar_datos("SELECT * FROM recetas")
    if df is not None:
        st.dataframe(df.style.format(precision=2), use_container_width=True)

# --- PÁGINA 3: INVENTARIO REAL ---
elif opcion == "📦 Inventario Real":
    st.header("📦 Gestión de Stock en Bodega")
    df_productos = cargar_datos("SELECT producto FROM maestro_insumos ORDER BY producto ASC")
    
    with st.expander("➕ Actualizar Stock (Coordinador)"):
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
                    st.success(f"¡{prod_sel} actualizado!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error: {e}")

    query_inventario = """
        SELECT producto, stock_actual FROM maestro_insumos 
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
    df_inv = cargar_datos(query_inventario)
    if df_inv is not None:
        st.dataframe(df_inv.style.format(precision=2), use_container_width=True, hide_index=True)

# --- PÁGINA 4: TABLERO DE CONTROL ---
elif opcion == "🚨 Tablero de Control":
    st.markdown("<h1 style='color: #FF4B4B;'>🚨 Tablero de Control y Pedidos</h1>", unsafe_allow_html=True)
    df = cargar_datos("SELECT * FROM tablero_control")
    
    if df is not None:
        totales_permitidos = [
            '>>> TOTAL PORCIÓN DE BOFE', 
            '>>> TOTAL PORCIÓN DE RELLENA', 
            '>>> TOTAL PORCIÓN DE CHORIZO', 
            '>>> TOTAL POLLO A LA PLANCHA', 
            '>>> TOTAL SOLOMITO DE CERDO'
        ]
        
        df_final = df[ (~df['producto'].str.contains('>>>', na=False)) | (df['producto'].isin(totales_permitidos)) ]

        columnas_visibles = ['producto', 'stock_actual', 'promedio_venta_diario', 'venta_real', 'alerta', 'pedido_sugerido']
        
        def aplicar_colores(row):
            if 'CRÍTICO' in str(row['alerta']): return ['background-color: #ff4b4b; color: white'] * len(row)
            elif 'PEDIR' in str(row['alerta']): return ['background-color: #fca311; color: black'] * len(row)
            return [''] * len(row)

        st.dataframe(
            df_final[columnas_visibles].style.format(precision=2, subset=['stock_actual', 'promedio_venta_diario', 'venta_real', 'pedido_sugerido'])
            .apply(aplicar_colores, axis=1), 
            use_container_width=True, hide_index=True
        )
        st.info("💡 El orden sigue la jerarquía del bar y termina con la Cocina.")
