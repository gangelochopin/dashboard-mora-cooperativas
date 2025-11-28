"""
HEADER DEL DASHBOARD
"""

import streamlit as st  
import datetime

def crear_header_premium():
    # Ajustamos las proporciones para logo más grande
    col1, col2, col3 = st.columns([1.5, 3, 1])
    
    with col1:
        try:
            # Logo significativamente más grande
            st.image("assets/logo.png", width=180)
        except:
            st.markdown("""
            <div style='width: 150px; height: 150px; background: linear-gradient(135deg, #1a5276, #2980b9); 
                      border-radius: 12px; display: flex; align-items: center; justify-content: center; 
                      color: white; font-weight: bold; font-size: 16px; margin: 0 auto; 
                      text-align: center; line-height: 1.3; border: 2px solid #1a5276;'>
                🔍<br>ASFI<br>MONITOREO
            </div>
            """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div style='text-align: center; padding: 1rem 0;'>
            <h1 style='margin: 0; font-size: 2.3rem; font-weight: 700; color: #2c3e50; font-family: "Times New Roman", serif; line-height: 1.1;'>
                SISTEMA DE MONITOREO<br>DE INDICADORES DE MORA
            </h1>
            <h3 style='margin: 1rem 0 0 0; font-size: 1.4rem; color: #7f8c8d; font-weight: 400;'>
                Análisis del Sector Cooperativo Supervisado
            </h3>
            <div style='height: 4px; background: linear-gradient(90deg, #1a5276, #3498db); margin: 1.2rem auto; width: 300px; border-radius: 2px;'></div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        fecha_actual = datetime.datetime.now().strftime("%d %B %Y")
        st.markdown(f"""
        <div style='text-align: right; padding-top: 1rem;'>
            <div style='background: #f8f9fa; padding: 0.8rem; border-radius: 8px; border-left: 4px solid #1a5276;'>
                <p style='margin: 0; font-size: 1rem; color: #2c3e50; font-weight: 600;'>
                    {fecha_actual}
                </p>
                <p style='margin: 0.5rem 0 0 0; font-size: 0.9rem; color: #7f8c8d;'>
                    Reporte Mensual
                </p>
            </div>
        </div>
        """, unsafe_allow_html=True)