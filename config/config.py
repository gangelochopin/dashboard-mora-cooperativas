"""
CONFIGURACIÓN Y ESTILOS DEL DASHBOARD ASFI
"""

import streamlit as st

def configurar_aplicacion():
    st.set_page_config(
        page_title="ASFI - Monitor Financiero Avanzado",
        page_icon="🏛️",
        layout="wide",
        initial_sidebar_state="expanded"
    )

def cargar_estilos_premium():
    st.markdown("""
    <style>
        .main {
            background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }
        
        .header-premium {
            background: linear-gradient(135deg, #0052A5 0%, #003366 100%);
            padding: 2.5rem 2rem;
            color: white;
            border-radius: 0 0 25px 25px;
            margin: -1rem -1rem 2rem -1rem;
            box-shadow: 0 8px 25px rgba(0, 82, 165, 0.3);
        }
        
        .metric-card {
            background: rgba(255, 255, 255, 0.95);
            padding: 1.8rem 1.2rem;
            border-radius: 12px;
            border-left: 5px solid #0052A5;
            box-shadow: 0 6px 20px rgba(0, 0, 0, 0.08);
            margin: 0.8rem 0;
            text-align: center;
            transition: all 0.3s ease;
        }
        
        .metric-card:hover {
            transform: translateY(-3px);
            box-shadow: 0 8px 25px rgba(0, 0, 0, 0.12);
        }
        
        .metric-high-risk { border-left-color: #D32F2F; }
        .metric-moderate-risk { border-left-color: #FF9800; }
        .metric-low-risk { border-left-color: #388E3C; }
        
        .stButton>button {
            background: linear-gradient(135deg, #0052A5 0%, #003366 100%);
            color: white;
            border: none;
            border-radius: 8px;
            padding: 12px 28px;
            font-weight: 600;
            transition: all 0.3s ease;
        }
        
        .footer-premium {
            background: linear-gradient(135deg, #003366 0%, #002244 100%);
            color: white;
            padding: 1.5rem;
            text-align: center;
            margin-top: 4rem;
            border-radius: 15px 15px 0 0;
        }
    </style>
    """, unsafe_allow_html=True)