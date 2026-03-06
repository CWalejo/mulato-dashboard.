import streamlit as st
import pandas as pd
import psycopg2
import google.generativeai as genai
import plotly.express as px
import os

# 1. Configuración de la Página
st.set_page_config(page_title="El Mulato Hub", layout="wide", page_icon="🏢")

# --- CONEXIÓN A NEON (RAMA: PRUEBAS) ---
DB_URL = "postgresql://neondb_owner:npg_2YMloHQwec0b@ep-young-meadow-aicra7vo-pooler.c-4.us-east-1.aws.neon.tech/neondb?sslmode=require"

# --- CONFIGURACIÓN IA (SOLUCIÓN DEFINITIVA) ---
# El transport='rest' obliga a la librería a usar la vía estable de producción
API_KEY = "AIzaSyA7DUcZ7Bc2sEJGHFYkSBf-0bZDBR3a214"
genai.configure(api_key=API_KEY, transport='rest')

# Definimos el modelo de forma global para mayor estabilidad
model = genai.GenerativeModel('gemini-1.5-flash')

def consultar_neon(query):
    try:
        conn = psycopg2.connect(DB_URL)
        df = pd.read_sql(query, conn)
        conn.close()
        return df
    except Exception as e:
        st.error(f"❌ Error de conexión: {e}")
        return None

# --- SEGURIDAD ---
if 'autenticado' not in st.session_state:
    st.session_state['autenticado'] = False

if not st.session_state['autenticado']:
    st.markdown("<h2 style='text-align: center
