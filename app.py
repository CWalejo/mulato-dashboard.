import streamlit as st
import pandas as pd
import psycopg2

# 1. Configuración de la página
st.set_page_config(page_title="El Mulato - Gestión Real", layout="wide")

# Credenciales de tu base de datos Neon
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

# Sidebar para navegación
st.sidebar.title("Menú de Control")
opcion = st.sidebar.radio("Ir a:", ["📈 Historial de Ventas", "🚨 Tablero de Control"])

# --- PÁGINA 1: HISTORIAL DE VENTAS ---
if opcion == "📈 Historial de Ventas":
    st.markdown("<h1 style='color: #D4AF37;'>📈 Ventas Acumuladas (Mes y Medio)</h1>", unsafe_allow_html=True)
    st.info("Periodo analizado: **01/01/2026 al 23/02/2026**")
    
    # Consulta a la tabla física con las nuevas columnas
    df_historial = cargar_datos("SELECT producto, cantidad_vendida, fecha_inicio, fecha_fin FROM historial_ventas ORDER BY cantidad_vendida DESC")
    
    if df_historial is not None:
        st.dataframe(df_historial, use_container_width=True)

# --- PÁGINA 2: TABLERO DE CONTROL (LA VISTA INTELIGENTE) ---
elif opcion == "🚨 Tablero de Control":
    st.markdown("<h1 style='color: #FF4B4B;'>🚨 Tablero de Alertas e Inventario</h1>", unsafe_allow_html=True)
    st.write("Cálculo basado en el **promedio diario real** del periodo seleccionado.")

    # Consulta a la VISTA que creamos en Neon
    df_tablero = cargar_datos("SELECT * FROM tablero_control ORDER BY promedio_venta_diario DESC")

    if df_tablero is not None:
        # Función para aplicar colores según la alerta
        def highlight_alertas(row):
            if row['alerta'] == 'CRÍTICO':
                return ['background-color: #ff4b4b; color: white'] * len(row)
            elif row['alerta'] == 'PEDIR':
                return ['background-color: #fca311; color: black'] * len(row)
            return [''] * len(row)

        # Mostrar métricas rápidas
        col1, col2 = st.columns(2)
        criticos = len(df_tablero[df_tablero['alerta'] == 'CRÍTICO'])
        pedir = len(df_tablero[df_tablero['alerta'] == 'PEDIR'])
        
        col1.metric("Productos en CRÍTICO", criticos)
        col2.metric("Productos para PEDIR", pedir)

        # Mostrar tabla con estilos
        st.dataframe(df_tablero.style.apply(highlight_alertas, axis=1), use_container_width=True)

---

### ¿Qué ganamos con este código?
1.  **Sincronización:** Ya no lee "fechas" genéricas, sino las columnas exactas `fecha_inicio` y `fecha_fin` que acabas de ver que funcionan en Neon.
2.  **Lógica Visual:** El jefe podrá ver de un vistazo qué productos están en rojo (CRÍTICO) porque su stock ya no aguanta el promedio diario triplicado.
3.  **Pedido Inteligente:** La columna `pedido_sugerido` ya mostrará cuántas botellas comprar para estar tranquilos los próximos 7 días.

**¿Quieres que le agregue un botón de "Descargar Reporte en PDF" para que el jefe pueda mandarlo por WhatsApp a los proveedores?** 
