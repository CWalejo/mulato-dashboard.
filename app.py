# ... (Manten el resto del código igual: imports, DB_URL, seguridad) ...

if opcion == "📈 Historial":
    st.header("📈 Historial de Ventas")
    
    # --- BOTÓN DE BORRADO REAL ---
    with st.expander("🚨 ZONA DE PELIGRO - LIMPIEZA DE TABLA"):
        st.warning("Esto borrará los datos que ves en la tabla de abajo para que quede limpia.")
        if st.button("CONFIRMAR: BORRAR DATOS DE HISTORIAL"):
            try:
                conn = psycopg2.connect(DB_URL)
                cur = conn.cursor()
                # Esto borra físicamente los datos de la tabla historial_ventas
                cur.execute("TRUNCATE TABLE historial_ventas RESTART IDENTITY;")
                conn.commit()
                cur.close()
                conn.close()
                st.success("¡Tabla limpiada con éxito! Ahora debería estar en 0.")
                st.rerun()
            except Exception as e:
                st.error(f"Error al borrar: {e}")

    # --- LECTURA DE DATOS ---
    df_hist = cargar_datos_directo("SELECT * FROM historial_ventas ORDER BY id ASC")
    
    if df_hist is not None:
        st.write(f"📊 **Datos detectados en Neon:** {len(df_hist)} registros.")
        st.dataframe(df_hist, use_container_width=True, hide_index=True, height=800)

# ... (Manten el resto de secciones igual) ...
