# --- 6. IA MULATO (VERSIÓN ESTABLE SIN BETA) ---
elif opcion == "🤖 IA Mulato":
    st.header("🤖 Asistente de Negocio")
    st.write("Analizo tu inventario en tiempo real para darte recomendaciones.")

    # Forzamos la configuración limpia de la IA
    try:
        # Usamos el modelo 'gemini-1.5-flash' que es el actual de 2026
        # Si este falla, el código capturará el error sin tumbar la app
        model_final = genai.GenerativeModel('gemini-1.5-flash')
        
        df_contexto = consultar_neon("SELECT producto, stock_actual, alerta, venta_real FROM tablero_control")
        
        pregunta = st.chat_input("¿Qué deseas consultar sobre el inventario?")
        
        if pregunta and df_contexto is not None:
            # Resumen de datos para el prompt
            contexto_datos = df_contexto.to_string(index=False)
            
            prompt = f"""
            Eres el experto administrador del bar 'El Mulato'. 
            Analiza los siguientes datos de inventario y ventas:
            
            {contexto_datos}
            
            Responde a la pregunta del dueño de forma ejecutiva: {pregunta}
            """
            
            with st.spinner("Analizando con el cerebro de Google AI..."):
                # Intentamos la generación directa
                response = model_final.generate_content(prompt)
                st.markdown("### 💡 Recomendación:")
                st.write(response.text)
                
    except Exception as e:
        # Si vuelve a dar 404, es un problema de la región o la versión de la librería
        st.error(f"Error de comunicación: {e}")
        st.info("Verifica que en tu archivo requirements.txt diga: google-generativeai==0.8.3")
