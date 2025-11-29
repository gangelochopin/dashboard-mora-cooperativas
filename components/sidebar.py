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
    
# ---------------------------------------------------------
    # SECCIÓN DE CONTADOR DE VISITAS 
    # ---------------------------------------------------------
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🌐 Tráfico")
    
    import time
    
    # Obtenemos el tiempo actual para evitar la caché
    timestamp = int(time.time())
    
    # URL base de tu aplicación
    target_url = "https://dashboard-mora-cooperativas.streamlit.app"
    
    # Construimos la URL del contador con el truco anti-caché (&t=...)
    # Usamos otro proveedor (visitor-badge.laobi.io) que suele ser más rápido y fiable
    url_contador = f"https://visitor-badge.laobi.io/badge?page_id={target_url}&left_text=Visitas&right_color=%230052A5&left_bg_color=%23555555&t={timestamp}"
    
    st.sidebar.markdown(
        f"""
        <div style="display: flex; justify-content: center; margin-top: 10px;">
            <img src="{url_contador}" alt="Contador de Visitas">
        </div>
        <div style="text-align: center; font-size: 0.8em; color: gray; margin-top: 5px;">
            Monitor en tiempo real
        </div>
        """, 
        unsafe_allow_html=True
    )
    # ---------------------------------------------------------

    
    return cooperativa_seleccionada