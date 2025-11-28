"""
FOOTER PREMIUM DEL DASHBOARD
"""

import streamlit as st
import datetime

def crear_footer_premium():
    st.markdown("""
    <div class="footer-premium">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <div style="text-align: left;">
                <p style="margin: 0; font-size: 0.9rem; font-weight: 300;">
                    Datos extraídos de los EEFF mensuales de ASFI
                </p>
            </div>
            <div style="text-align: right;">
                <p style="margin: 0; font-size: 0.9rem; font-weight: 500;">
                    Desarrollado por Gustavo Angelo Zabaleta
                </p>
                <p style="margin: 0.3rem 0 0 0; font-size: 0.8rem; opacity: 0.8;">
                    Actualizado: {fecha_actual}
                </p>
            </div>
        </div>
    </div>
    """.format(fecha_actual=datetime.datetime.now().strftime('%d/%m/%Y %H:%M')), 
    unsafe_allow_html=True)