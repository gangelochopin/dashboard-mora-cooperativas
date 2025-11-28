"""
ANÁLISIS DE RIESGO DE COOPERATIVAS
"""

import pandas as pd
import streamlit as st

def analizar_riesgo(_datos, cooperativas, meses_recientes=6):
    clasificacion = {
        "ALTO RIESGO": [], "RIESGO MODERADO": [], 
        "BAJO RIESGO": [], "INACTIVAS": []
    }
    
    try:
        fecha_limite = None
        if 'Fecha_Corte' in _datos.columns:
            fecha_mas_reciente = _datos['Fecha_Corte'].max()
            fecha_limite = fecha_mas_reciente - pd.DateOffset(months=meses_recientes)
        
        for cooperativa in cooperativas:
            if fecha_limite is not None:
                datos_recientes = _datos[_datos['Fecha_Corte'] >= fecha_limite]
                valores_recientes = datos_recientes[cooperativa].dropna()
            else:
                valores_recientes = _datos[cooperativa].dropna()
            
            if len(valores_recientes) > 0:
                ultima_mora = valores_recientes.iloc[-1]
                
                if ultima_mora > 0.1:
                    clasificacion["ALTO RIESGO"].append(cooperativa)
                elif ultima_mora > 0.05:
                    clasificacion["RIESGO MODERADO"].append(cooperativa)
                else:
                    clasificacion["BAJO RIESGO"].append(cooperativa)
            else:
                clasificacion["INACTIVAS"].append(cooperativa)
                
        return clasificacion
        
    except Exception as e:
        st.error(f"Error en análisis de riesgo: {e}")
        return clasificacion