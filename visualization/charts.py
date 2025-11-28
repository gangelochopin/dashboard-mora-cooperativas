"""
GRÁFICOS INTERACTIVOS Y VISUALIZACIONES
"""

import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np

def crear_grafico_torta_interactivo(clasificacion_riesgo, es_movil=False):
    categorias = ['Alto Riesgo', 'Riesgo Moderado', 'Bajo Riesgo', 'Inactivas']
    valores = [
        len(clasificacion_riesgo['ALTO RIESGO']),
        len(clasificacion_riesgo['RIESGO MODERADO']),
        len(clasificacion_riesgo['BAJO RIESGO']),
        len(clasificacion_riesgo['INACTIVAS'])
    ]
    
    colores = ['#D32F2F', '#FF9800', '#388E3C', '#9E9E9E']
    
    fig = go.Figure(data=[go.Pie(
        labels=categorias,
        values=valores,
        hole=0.4,
        marker=dict(colors=colores),
        textinfo='label+percent',
        hovertemplate='<b>%{label}</b><br>Cooperativas: %{value}<br>Porcentaje: %{percent}',
        pull=[0.05, 0.02, 0.02, 0.02]
    )])
    
    # Configuración responsive
    if es_movil:
        fig.update_layout(
            title={
                'text': '📊 Distribución de Riesgo',
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 14, 'color': '#003366'}
            },
            showlegend=True,
            height=350,
            margin=dict(t=60, b=60, l=60, r=60),
            font=dict(size=10)
        )
    else:
        fig.update_layout(
            title={
                'text': '📊 Distribución de Cooperativas por Nivel de Riesgo',
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 16, 'color': '#003366'}
            },
            showlegend=True,
            height=400,
            margin=dict(t=80, b=80, l=80, r=150)
        )
    
    return fig

def crear_grafico_evolucion_interactivo(_datos, cooperativa, es_movil=False):
    try:
        serie = _datos[cooperativa]
        valores = serie.dropna()
        if len(valores) == 0:
            return None

        # Fechas alineadas con la serie
        if 'Fecha_Corte' in _datos.columns:
            fechas = _datos.loc[valores.index, 'Fecha_Corte']
        else:
            fechas = valores.index

        # OPTIMIZACIÓN PARA MÓVIL: Menos puntos para mejor performance
        if es_movil and len(fechas) > 24:
            step = max(1, len(fechas) // 12)  # Máximo 12 puntos en móvil
            mask = np.arange(0, len(fechas), step)
            fechas = fechas.iloc[mask]
            valores = valores.iloc[mask]

        # Configuración de ticks según dispositivo
        tickvals, ticktext = None, None
        if len(fechas) > 1:
            n_ticks = min(6 if es_movil else 8, len(fechas))
            idxs = np.linspace(0, len(fechas) - 1, n_ticks, dtype=int)
            tickvals = [fechas.iloc[i] for i in idxs]
            ticktext = [pd.to_datetime(d).strftime('%b %Y') for d in tickvals]

        fig = make_subplots(specs=[[{"secondary_y": False}]])
        
        # LÍNEAS MÁS GRUESAS Y MARKERS MÁS GRANDES EN MÓVIL
        line_width = 4 if es_movil else 3
        marker_size = 8 if es_movil else 6
        
        fig.add_trace(
            go.Scatter(
                x=fechas, y=valores,
                mode='lines+markers',
                name='Mora Contable',
                line=dict(color='#0052A5', width=line_width),
                marker=dict(size=marker_size, color='#0052A5'),
                hovertemplate='<b>%{x|%b %Y}</b><br>Mora: %{y:.3f}<extra></extra>'
            ),
            secondary_y=False
        )
        
        if len(serie.dropna()) > 12:
            media_movil = serie.rolling(window=12, min_periods=1).mean()
            # Aplicar el mismo filtro para media móvil
            if es_movil and len(fechas) > 24:
                media_movil = media_movil.iloc[mask]
            else:
                media_movil = media_movil.loc[valores.index]
                
            fig.add_trace(
                go.Scatter(
                    x=fechas, y=media_movil,
                    mode='lines',
                    name='Media Móvil (12M)',
                    line=dict(color='#D32F2F', width=3 if not es_movil else 2.5, dash='dash'),
                    hovertemplate='<b>%{x|%b %Y}</b><br>Media Móvil: %{y:.3f}<extra></extra>'
                ),
                secondary_y=False
            )
        
        # CONFIGURACIÓN MEJORADA PARA MÓVIL
        if es_movil:
            fig.update_layout(
                title=f'📈 {cooperativa}',
                xaxis_title='Fecha',
                yaxis_title='Índice de Mora',
                hovermode='x unified',
                height=500,  # MÁS ALTO para móvil
                showlegend=True,
                plot_bgcolor='rgba(248,249,250,0.8)',
                paper_bgcolor='rgba(255,255,255,0.9)',
                font=dict(color='#003366', size=12),  # FUENTE MÁS GRANDE
                margin=dict(l=60, r=40, t=80, b=80),  # MÁRGENES MÁS GRANDES
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="center",
                    x=0.5,
                    font=dict(size=12),  # LEYENDA MÁS GRANDE
                    bgcolor='rgba(255,255,255,0.8)'  # FONDO PARA MEJOR LEGIBILIDAD
                )
            )
            
            # TOOLTIPS MÁS LEGIBLES EN MÓVIL
            fig.update_traces(
                hovertemplate='<b>%{x|%b %Y}</b><br>Valor: %{y:.3f}<extra></extra>'
            )
        else:
            fig.update_layout(
                title=f'📈 Evolución del Índice de Mora - {cooperativa}',
                xaxis_title='Fecha',
                yaxis_title='Índice de Mora',
                hovermode='x unified',
                height=550,
                showlegend=True,
                plot_bgcolor='rgba(248,249,250,0.8)',
                paper_bgcolor='rgba(255,255,255,0.9)',
                font=dict(color='#003366', size=12),
                margin=dict(l=50, r=50, t=80, b=80)
            )
        
        if tickvals is not None:
            fig.update_xaxes(
                tickvals=tickvals, 
                ticktext=ticktext, 
                tickangle=45 if not es_movil else 90
            )
        
        return fig
        
    except Exception as e:
        import streamlit as st
        st.error(f"Error creando gráfico interactivo: {e}")
        return None