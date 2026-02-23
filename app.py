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
    df = cargar_datos("SELECT producto, cantidad_vendida, fecha_inicio, fecha_fin FROM historial_ventas ORDER BY cantidad_vendida DESC")
    if df is not None:
        # Formateo a 2 decimales para que no confunda al coordinador
        st.dataframe(df.style.format(precision=2), use_container_width=True)

# --- PÁGINA 2: RECETAS ---
elif opcion == "🍳 Recetas y Costos":
    st.header("🍳 Configuración de Recetas")
    df = cargar_datos("SELECT * FROM recetas")
    if df is not None:
        st.dataframe(df.style.format(precision=2), use_container_width=True)

# --- PÁGINA 3: INVENTARIO ---
elif opcion == "📦 Inventario Real":
    st.header("📦 Gestión de Stock en Bodega")
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
                    st.success(f"¡{prod_sel} actualizado!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error: {e}")
    df = cargar_datos("SELECT producto, stock_actual FROM maestro_insumos ORDER BY producto ASC")
    if df is not None:
        st.dataframe(df.style.format(precision=2), use_container_width=True)

# --- PÁGINA 4: TABLERO DE CONTROL (ORDENADO Y LIMPIO) ---
elif opcion == "🚨 Tablero de Control":
    st.markdown("<h1 style='color: #FF4B4B;'>🚨 Tablero de Control y Pedidos</h1>", unsafe_allow_html=True)
    
    # Traemos la data de Neon (Ya viene con alerta antes que pedido y el orden correcto)
    df = cargar_datos("SELECT * FROM tablero_control")
    
    if df is not None:
        # 1. FILTRO DE "REGUERO": Solo dejamos los totales de comida que importan
        totales_permitidos = [
            '>>> TOTAL PORCIÓN DE BOFE', 
            '>>> TOTAL PORCIÓN DE RELLENA', 
            '>>> TOTAL PORCIÓN DE CHORIZO', 
            '>>> TOTAL POLLO A LA PLANCHA', 
            '>>> TOTAL SOLOMITO DE CERDO'
        ]
        
        # Filtramos para no ver >>> TOTAL en licores, solo en lo que definimos arriba
        df_final = df[ (~df['producto'].str.contains('>>>', na=False)) | (df['producto'].isin(totales_permitidos)) ]

        # 2. DEFINICIÓN DE COLUMNAS VISIBLES (Ocultamos 'bloque' y 'orden_barra')
        # Aquí definimos el orden de izquierda a derecha para el usuario
        columnas_visibles = [
            'producto', 
            'stock_actual', 
            'promedio_venta_diario', 
            'venta_real', 
            'alerta',           # Semáforo primero
            'pedido_sugerido'   # Cálculo del Excel después
        ]
        
        # 3. FUNCIÓN DE COLORES (Para resaltar filas Críticas y de Pedir)
        def aplicar_colores(row):
            if 'CRÍTICO' in str(row['alerta']):
                return ['background-color: #ff4b4b; color: white'] * len(row)
            elif 'PEDIR' in str(row['alerta']):
                return ['background-color: #fca311; color: black'] * len(row)
            return [''] * len(row)

        # 4. RENDERIZADO FINAL SIN COLUMNAS TÉCNICAS
        st.dataframe(
            df_final[columnas_visibles].style.format(precision=2, subset=['stock_actual', 'promedio_venta_diario', 'venta_real', 'pedido_sugerido'])
            .apply(aplicar_colores, axis=1), 
            use_container_width=True,
            hide_index=True  # Quita los números de la izquierda
        )
        
        st.info("💡 El orden sigue la jerarquía del bar (Aguardientes, Rones, Tequilas...) y termina con la Cocina.")
