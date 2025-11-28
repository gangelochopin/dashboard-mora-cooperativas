"""
HEADER PREMIUM DEL DASHBOARD
"""

import streamlit as st
import datetime

def crear_header_premium():
    st.markdown("""
    <div class="header-premium">
        <div style="display: flex; align-items: center; justify-content: space-between;">
            <div>
                <h1 style="margin: 0; font-size: 2.5rem; font-weight: 700;text-align: center;">
                    🏛️ AUTOMATIZACION INDICADORES DE MORA
                </h1>
                <p style="margin: 0.5rem 0 0 0; font-size: 1.3rem; opacity: 0.95;">
                    Sistema de Monitoreo por cooperativas
                </p>
            </div>
            <div style="text-align: right;">
                <p style="margin: 0; font-size: 1rem; opacity: 0.9; font-weight: 500;">
                    Indice de Mora – Cooperativas Supervisadas
                </p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)