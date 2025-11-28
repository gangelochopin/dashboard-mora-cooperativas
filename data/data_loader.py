"""
CARGA Y PROCESAMIENTO DE DATOS
"""

import pandas as pd
import numpy as np
import streamlit as st

@st.cache_data(ttl=3600)
def cargar_datos():
    try:
        datos = pd.read_csv('indice_mora.csv')
        
        # Normalizar columna de fecha
        if 'Fecha_Corte' in datos.columns:
            datos['Fecha_Corte'] = pd.to_datetime(datos['Fecha_Corte'])
        else:
            columnas_fecha = [col for col in datos.columns if 'fecha' in col.lower() or 'date' in col.lower()]
            if columnas_fecha:
                datos['Fecha_Corte'] = pd.to_datetime(datos[columnas_fecha[0]])
            else:
                # Si no existe ninguna columna fecha, crear índice numérico con advertencia
                st.warning("No se detectó columna de fecha. Se usará índice numérico como fecha.")
                datos['Fecha_Corte'] = pd.RangeIndex(start=0, stop=len(datos), step=1)
        
        # Asegurar orden por fecha
        datos = datos.sort_values('Fecha_Corte').reset_index(drop=True)
        return datos
        
    except Exception as e:
        st.error(f"Error en la carga de datos: {str(e)}")
        return None

def identificar_cooperativas(_datos):
    try:
        # Seleccionar columnas numéricas excluyendo Fecha_Corte
        columnas_numericas = _datos.select_dtypes(include=[np.number]).columns.tolist()
        cooperativas = [col for col in columnas_numericas if col != 'Fecha_Corte']
        return cooperativas if cooperativas else []
    except Exception as e:
        st.error(f"Error identificando cooperativas: {e}")
        return []