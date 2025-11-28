"""
FUNCIONES AUXILIARES Y UTILITARIOS
"""

import pandas as pd
import numpy as np

def obtener_estadisticas_cooperativa(_datos, cooperativa):
    """
    Calcula estadísticas básicas para una cooperativa específica
    """
    valores = _datos[cooperativa].dropna()
    
    if len(valores) == 0:
        return None
    
    estadisticas = {
        'ultimo_valor': valores.iloc[-1],
        'promedio': valores.mean(),
        'maximo': valores.max(),
        'minimo': valores.min(),
        'desviacion': valores.std(),
        'cantidad_datos': len(valores),
        'tendencia': "↗️ ALTA" if valores.iloc[-1] > valores.mean() else "↘️ BAJA" if valores.iloc[-1] < valores.mean() else "➡️ ESTABLE"
    }
    
    return estadisticas

def clasificar_riesgo(valor_mora):
    """
    Clasifica el nivel de riesgo basado en el valor de mora
    """
    if valor_mora > 0.1:
        return "ALTO RIESGO", "#D32F2F", "🔴"
    elif valor_mora > 0.05:
        return "RIESGO MODERADO", "#FF9800", "🟡"
    else:
        return "BAJO RIESGO", "#388E3C", "🟢"