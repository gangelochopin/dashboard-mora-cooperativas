"""
GRÁFICOS INTERACTIVOS Y VISUALIZACIONES
Optimizado para Móviles y Escritorio
"""

import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
import plotly.io as pio

# --- CONFIGURACIÓN GENERAL ---
def configurar_tema_elegante():
    """Configura tema base para Plotly"""
    pio.templates.default = "plotly_white"
    return {
        'layout': {
            'font': {'family': 'Arial, sans-serif', 'size': 12},
            'plot_bgcolor': 'white',
            'paper_bgcolor': 'white',
            'margin': dict(l=50, r=50, t=60, b=50),
        }
    }

# --- 1. GRÁFICO INDIVIDUAL (Cajas pequeñas en la paginación) ---
def crear_grafico_individual_elegante(datos, cooperativa, es_movil=False):
    """Crea gráfico pequeño para el grid de resultados"""
    
    serie = datos[cooperativa]
    mask = serie.notna()
    fechas_validas = datos.loc[mask, 'Fecha_Corte']
    valores_validos = serie[mask]
    
    if len(valores_validos) == 0:
        return None
    
    fig = go.Figure()
    
    promedio = valores_validos.mean()
    
    paleta_colores = [
        '#0052A5', '#D32F2F', '#7B1FA2', '#388E3C', '#F57C00', 
        '#5D4037', '#0288D1', '#C2185B', '#00796B', '#512DA8'
    ]
    color_principal = paleta_colores[hash(cooperativa) % len(paleta_colores)]
    
    # Traza: Mora
    fig.add_trace(go.Scatter(
        x=fechas_validas,
        y=valores_validos,
        mode='lines+markers',
        line=dict(width=2.2, color=color_principal, shape='spline'),
        marker=dict(size=6 if es_movil else 5, color=color_principal, line=dict(width=1, color='white')),
        name='Mora',
        hovertemplate='<b>%{x|%b %Y}</b><br>Mora: <b>%{y:.2%}</b><extra></extra>'
    ))
    
    # Traza: Promedio
    fig.add_trace(go.Scatter(
        x=[fechas_validas.min(), fechas_validas.max()],
        y=[promedio, promedio],
        mode='lines',
        line=dict(width=1.2, color='#2c3e50', dash='dash'),
        name='Promedio',
        hovertemplate='Promedio: <b>%{y:.2%}</b><extra></extra>'
    ))
    
    altura = 380 if es_movil else 320 
    margenes = dict(l=10, r=10, t=30, b=40) if es_movil else dict(l=50, r=30, t=50, b=70)
    
    fig.update_layout(
        height=altura,
        margin=margenes,
        showlegend=False,
        paper_bgcolor='white',
        plot_bgcolor='white',
        font=dict(size=10 if es_movil else 11, family='Arial'),
        xaxis=dict(
            tickformat='%b %y' if es_movil else '%b %Y',
            tickangle=45,
            gridcolor='rgba(220, 220, 220, 0.5)',
            linecolor='rgba(200, 200, 200, 0.5)'
        ),
        yaxis=dict(
            tickformat=".0%",
            gridcolor='rgba(220, 220, 220, 0.5)',
            linecolor='rgba(200, 200, 200, 0.5)'
        ),
        hovermode='x unified'
    )
    
    return fig

# --- 2. GRÁFICO DE TORTA (Distribución) ---
def crear_grafico_torta_interactivo(clasificacion_riesgo, es_movil=False):
    """Gráfico de torta/donas con diseño consistente para móvil y escritorio"""

    categorias = ['Alto Riesgo', 'Riesgo Moderado', 'Bajo Riesgo', 'Inactivas']
    valores = [
        len(clasificacion_riesgo.get('ALTO RIESGO', [])),
        len(clasificacion_riesgo.get('RIESGO MODERADO', [])),
        len(clasificacion_riesgo.get('BAJO RIESGO', [])),
        len(clasificacion_riesgo.get('INACTIVAS', []))
    ]
    
    colores = ['#e74c3c', '#f39c12', '#27ae60', '#95a5a6']

    fig = go.Figure(data=[go.Pie(
        labels=categorias,
        values=valores,
        hole=0.52,
        marker=dict(colors=colores),
        textinfo='percent' if es_movil else 'label+percent',
        hovertemplate='<b>%{label}</b><br>%{value} Coop.<br>%{percent}',
        textfont=dict(size=12, family='Arial')
    )])

    if es_movil:
        fig.update_layout(
            title=dict(text='Distribución de Riesgo', x=0.5, xanchor='center'),
            showlegend=True,
            height=380,
            margin=dict(t=40, b=40, l=10, r=10),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=-0.22,
                xanchor="center",
                x=0.5,
                font=dict(size=11)
            )
        )

    else:
        fig.update_layout(
            title=dict(text='Distribución de Riesgo', x=0.5, xanchor='center'),
            showlegend=True,
            height=420,
            margin=dict(t=60, b=60, l=60, r=60),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=-0.28,
                xanchor="center",
                x=0.5,
                font=dict(size=12)
            )
        )

    return fig

# --- 3. GRÁFICO DETALLADO ---
def crear_grafico_evolucion_interactivo(datos, cooperativa, es_movil=False):
    """Gráfico principal grande con Media Móvil"""
    try:
        serie = datos[cooperativa]
        valores = serie.dropna()
        if len(valores) == 0:
            return None

        fechas = datos['Fecha_Corte'].loc[valores.index] if 'Fecha_Corte' in datos.columns else valores.index

        # Optimización móvil
        step = 1
        if es_movil and len(fechas) > 30:
            step = 2
            fechas = fechas.iloc[::step]
            valores = valores.iloc[::step]

        # Configuración de ticks
        tickvals = None
        if len(fechas) > 1:
            n_ticks = 5 if es_movil else 10
            idxs = np.linspace(0, len(fechas) - 1, n_ticks, dtype=int)
            tickvals = [fechas.iloc[i] for i in idxs]

        fig = make_subplots(specs=[[{"secondary_y": False}]])

        paleta = ['#0052A5', '#D32F2F', '#388E3C', '#F57C00', '#5D4037']
        color_p = paleta[hash(cooperativa) % len(paleta)]

        # Línea principal
        fig.add_trace(go.Scatter(
            x=fechas, y=valores,
            mode='lines+markers',
            name='Mora',
            line=dict(color=color_p, width=2.5 if es_movil else 2.2, shape='spline'),
            marker=dict(size=6 if es_movil else 5, color=color_p, line=dict(width=1, color='white')),
            hovertemplate='<b>%{x|%b %Y}</b><br>%{y:.2%}<extra></extra>'
        ))

        # Media móvil
        if len(serie.dropna()) > 12:
            media_movil = serie.rolling(window=12, min_periods=1).mean()
            if es_movil and len(fechas) > 30:
                media_movil = media_movil.iloc[::step]
            else:
                media_movil = media_movil.loc[valores.index]

            fig.add_trace(go.Scatter(
                x=fechas, y=media_movil,
                mode='lines',
                name='Tendencia (12M)',
                line=dict(color='#2c3e50', width=1.8, dash='dot'),
                hovertemplate='Tendencia: %{y:.2%}<extra></extra>'
            ))

        layout_args = dict(
            xaxis_title='', 
            yaxis_title='Índice de Mora' if not es_movil else '',
            yaxis_tickformat=".0%",
            hovermode='x unified',
            plot_bgcolor='white',
            paper_bgcolor='white',
            font=dict(color='#2c3e50', size=11, family='Arial'),
        )

        if es_movil:
            fig.update_layout(
                **layout_args,
                title=None,
                height=450,
                margin=dict(l=10, r=10, t=10, b=100),
                showlegend=True,
                legend=dict(
                    orientation="h",
                    yanchor="top",
                    y=-0.25,
                    xanchor="center",
                    x=0.5,
                    bgcolor='rgba(255,255,255,0)'
                )
            )
        else:
            fig.update_layout(
                **layout_args,
                title=dict(text=f'Evolución: {cooperativa}', font=dict(size=18), x=0.5, xanchor='center'),
                height=500,
                margin=dict(l=60, r=60, t=80, b=80),
                showlegend=True,
                legend=dict(orientation="v")
            )

        # Grid y ejes
        fig.update_xaxes(
            gridcolor='rgba(220, 220, 220, 0.5)', 
            tickfont=dict(size=10),
            tickangle=45
        )
        fig.update_yaxes(
            gridcolor='rgba(220, 220, 220, 0.5)', 
            zerolinecolor='rgba(200, 200, 200, 0.3)'
        )

        if tickvals is not None:
            fig.update_xaxes(
                tickvals=tickvals,
                tickformat='%b %y' if es_movil else '%b %Y'
            )

        return fig

    except Exception as e:
        import streamlit as st
        st.error(f"Error gráfico: {e}")
        return None
