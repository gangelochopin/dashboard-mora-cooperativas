import streamlit as st
import datetime

def crear_sidebar(_cooperativas, _clasificacion_riesgo):
    st.sidebar.markdown("### 🎛️ Panel de Seleccion")
    
    # Selector de cooperativa 
    cooperativa_seleccionada = st.sidebar.selectbox(
        "🔍 Seleccionar Cooperativa:",
        options=_cooperativas,
        index=0
    )
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📊 Métricas del Sistema")
    
    col_sb1, col_sb2 = st.sidebar.columns(2)
    with col_sb1:
        st.metric("🔴 Alto Riesgo", len(_clasificacion_riesgo['ALTO RIESGO']))
        st.metric("🟢 Bajo Riego", len(_clasificacion_riesgo['BAJO RIESGO']))
    with col_sb2:
        st.metric("🟡 Riesgo Moderado", len(_clasificacion_riesgo['RIESGO MODERADO']))
        st.metric("⚫ Inactivas", len(_clasificacion_riesgo['INACTIVAS']))
    
    # Información del sistema
    with st.sidebar.expander("ℹ️ Información De 2005 a 2025"):
        st.write(f"**Cooperativas monitoreadas:** {len(_cooperativas)}")
        st.write(f"**Cooperativas activas:** {len(_cooperativas) - len(_clasificacion_riesgo['INACTIVAS'])}")
        st.write(f"**Última actualización:** {datetime.datetime.now().strftime('%d/%m/%Y')}")
    
    
    return cooperativa_seleccionada