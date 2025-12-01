"""
COMPONENTES DE MÉTRICAS PRINCIPALES
"""

import streamlit as st
import numpy as np

def crear_metricas_principales(_cooperativas, _clasificacion_riesgo, _datos):
    st.markdown("### 📈 Panorama Sistema Cooperativo")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <h3 style="color: #0052A5; margin: 0; font-size: 2rem;">🏛️</h3>
            <h2 style="color: #003366; margin: 0.5rem 0; font-size: 2.2rem;">{len(_cooperativas)}</h2>
            <p style="color: #666; margin: 0; font-weight: 500;">Cooperativas Supervisadas</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        cooperativas_activas = len(_cooperativas) - len(_clasificacion_riesgo["INACTIVAS"])
        st.markdown(f"""
        <div class="metric-card metric-low-risk">
            <h3 style="color: #388E3C; margin: 0; font-size: 2rem;">📈</h3>
            <h2 style="color: #003366; margin: 0.5rem 0; font-size: 2.2rem;">{cooperativas_activas}</h2>
            <p style="color: #666; margin: 0; font-weight: 500;">Cooperativas Activas</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-card metric-high-risk">
            <h3 style="color: #D32F2F; margin: 0; font-size: 2rem;">⚠️</h3>
            <h2 style="color: #003366; margin: 0.5rem 0; font-size: 2.2rem;">{len(_clasificacion_riesgo['ALTO RIESGO'])}</h2>
            <p style="color: #666; margin: 0; font-weight: 500;">Alto Riesgo</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        moras_activas = []
        for coop in _cooperativas:
            if coop not in _clasificacion_riesgo['INACTIVAS']:
                valores = _datos[coop].dropna()
                if len(valores) > 0:
                    moras_activas.append(valores.iloc[-1])
        
        mora_promedio = np.mean(moras_activas) if moras_activas else 0
        st.markdown(f"""
        <div class="metric-card">
            <h3 style="color: #0052A5; margin: 0; font-size: 2rem;">📊</h3>
            <h2 style="color: #003366; margin: 0.5rem 0; font-size: 2.2rem;">{mora_promedio*100:.2f}%</h2>
            <p style="color: #666; margin: 0; font-weight: 500;">Mora Promedio</p>
        </div>
        """, unsafe_allow_html=True)