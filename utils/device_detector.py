"""
DETECCIÓN DE DISPOSITIVOS MÓVILES
"""

import streamlit as st

def es_dispositivo_movil():
    """
    Detecta si el usuario accede desde un dispositivo móvil
    """
    try:
        # Método 1: Usando el contexto de Streamlit
        from streamlit.runtime.scriptrunner import get_script_run_ctx
        
        ctx = get_script_run_ctx()
        if ctx and hasattr(ctx, 'request'):
            user_agent = ctx.request.headers.get('User-Agent', '').lower()
            
            # Palabras clave que indican dispositivo móvil
            mobile_keywords = [
                'mobile', 'android', 'iphone', 'ipad', 'ipod', 
                'blackberry', 'webos', 'windows phone', 'kindle',
                'samsung', 'nokia', 'lg', 'sony', 'motorola'
            ]
            
            return any(keyword in user_agent for keyword in mobile_keywords)
    
    except Exception as e:
        # Si falla la detección, asumimos que no es móvil
        pass
    
    return False

def obtener_configuracion_dispositivo():
    """
    Retorna configuración específica según el dispositivo
    """
    es_movil = es_dispositivo_movil()
    
    config = {
        'es_movil': es_movil,
        'columnas_metricas': 2 if es_movil else 4,
        'altura_grafico': 400 if es_movil else 550,
        'tamano_fuente': 10 if es_movil else 12,
        'mostrar_leyenda_completa': not es_movil
    }
    
    return config