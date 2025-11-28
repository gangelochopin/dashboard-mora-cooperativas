"""
GRÁFICOS INTERACTIVOS Y VISUALIZACIONES ELEGANTES
"""

import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
import plotly.io as pio

# Configuración de tema elegante
def configurar_tema_elegante():
    """Configura tema elegante para todos los gráficos"""
    pio.templates.default = "plotly_white"
    
    # Personalizar colores y estilos
    tema_personalizado = {
        'layout': {
            'font': {'family': 'Arial, sans-serif', 'size': 12},
            'plot_bgcolor': 'white',
            'paper_bgcolor': 'white',
            'margin': dict(l=50, r=50, t=60, b=50),
            'hoverlabel': {
                'bgcolor': 'white',
                'font_size': 11,
                'font_family': 'Arial'
            }
        }
    }
    return tema_personalizado

def crear_grafico_individual_elegante(datos, cooperativa, es_movil=False):
    """Crea gráfico individual elegante para el sistema de paginación"""
    
    serie = datos[cooperativa]
    mask = serie.notna()
    fechas_validas = datos.loc[mask, 'Fecha_Corte']
    valores_validos = serie[mask]
    
    if len(valores_validos) == 0:
        return None
    
    # Crear figura
    fig = go.Figure()
    
    # Calcular métricas para colores
    ultimo_valor = valores_validos.iloc[-1]
    promedio = valores_validos.mean()
    
    # PALETA DE COLORES MEJORADA Y VARIADA
    paleta_colores = [
        '#0052A5',  # Azul Fondo Monetario
        '#D32F2F',  # Rojo intenso
        '#7B1FA2',  # Guindo/Morado
        '#388E3C',  # Verde financiero
        '#F57C00',  # Naranja
        '#5D4037',  # Marrón oscuro
        '#0288D1',  # Azul claro
        '#C2185B',  # Rosa fuerte
        '#00796B',  # Verde azulado
        '#512DA8',  # Púrpura oscuro
        '#303F9F',  # Azul índigo
        '#689F38',  # Verde lima
        '#E64A19',  # Naranja rojizo
        '#5D4037',  # Café
        '#1976D2',  # Azul medio
    ]
    
    # Asignar color único basado en el nombre de la cooperativa (hash)
    color_index = hash(cooperativa) % len(paleta_colores)
    color_principal = paleta_colores[color_index]
    
    # Determinar color secundario según riesgo
    if ultimo_valor > 0.1:
        color_secundario = '#e74c3c'  # Rojo para alto riesgo
    elif ultimo_valor > 0.05:
        color_secundario = '#f39c12'  # Naranja para riesgo moderado
    else:
        color_secundario = '#27ae60'  # Verde para bajo riesgo
    
    # Línea principal - GROSOR AUMENTADO y elegante
    fig.add_trace(go.Scatter(
        x=fechas_validas,
        y=valores_validos,
        mode='lines+markers',
        line=dict(
            width=2.2,  # GROSOR AUMENTADO (antes 1.5)
            color=color_principal,
            shape='spline'  # Línea suave
        ),
        marker=dict(
            size=5,  # Marcadores ligeramente más grandes
            color=color_principal,
            line=dict(width=1, color='white')  # Borde blanco para elegancia
        ),
        name='Mora',
        hovertemplate=(
            '<b>%{x|%b %Y}</b><br>'
            'Mora: <b>%{y:.2%}</b><br>'
            '<extra></extra>'
        )
    ))
    
    # Línea de promedio - estilo sutil
    fig.add_trace(go.Scatter(
        x=[fechas_validas.min(), fechas_validas.max()],
        y=[promedio, promedio],
        mode='lines',
        line=dict(
            width=1.2,  # Grosor ligeramente aumentado
            color='#2c3e50',  # Gris oscuro elegante
            dash='dash'
        ),
        name=f'Promedio: {promedio:.2%}',
        hovertemplate='Promedio: <b>%{y:.2%}</b><extra></extra>'
    ))
    
    # Media móvil solo si hay suficientes datos y es relevante
    if len(serie.dropna()) > 24:  # Solo si hay 2+ años de datos
        try:
            ma = serie.rolling(window=12, min_periods=1).mean()
            ma_valid = ma[mask]
            fig.add_trace(go.Scatter(
                x=fechas_validas,
                y=ma_valid,
                mode='lines',
                line=dict(
                    width=1.2,  # Grosor ligeramente aumentado
                    color='#7f8c8d',  # Gris neutro
                    dash='dot'
                ),
                name='Tendencia (MM 12)',
                hovertemplate='Tendencia: <b>%{y:.2%}</b><extra></extra>'
            ))
        except Exception:
            pass
    
    # Configuración elegante del layout
    altura = 280 if es_movil else 320
    
    fig.update_layout(
        height=altura,
        margin=dict(l=50, r=30, t=50, b=70),
        showlegend=False,
        paper_bgcolor='white',
        plot_bgcolor='white',
        font=dict(size=11, family='Arial'),
        xaxis=dict(
            tickformat='%b %Y',
            tickangle=45,
            gridcolor='rgba(220, 220, 220, 0.5)',
            linecolor='rgba(200, 200, 200, 0.5)',
            tickfont=dict(size=10)
        ),
        yaxis=dict(
            tickformat=".0%",
            gridcolor='rgba(220, 220, 220, 0.5)',
            linecolor='rgba(200, 200, 200, 0.5)',
            tickfont=dict(size=10),
            zerolinecolor='rgba(200, 200, 200, 0.3)'
        ),
        hovermode='x unified'
    )
    
    return fig

def crear_grafico_torta_interactivo(clasificacion_riesgo, es_movil=False):
    """Gráfico de torta con estilo elegante"""
    categorias = ['Alto Riesgo', 'Riesgo Moderado', 'Bajo Riesgo', 'Inactivas']
    valores = [
        len(clasificacion_riesgo['ALTO RIESGO']),
        len(clasificacion_riesgo['RIESGO MODERADO']),
        len(clasificacion_riesgo['BAJO RIESGO']),
        len(clasificacion_riesgo['INACTIVAS'])
    ]
    
    # Colores más elegantes
    colores = ['#e74c3c', '#f39c12', '#27ae60', '#95a5a6']
    
    fig = go.Figure(data=[go.Pie(
        labels=categorias,
        values=valores,
        hole=0.5,  # Donut más elegante
        marker=dict(colors=colores),
        textinfo='label+percent',
        hovertemplate='<b>%{label}</b><br>Cooperativas: %{value}<br>Porcentaje: %{percent}',
        pull=[0.03, 0.02, 0.02, 0.02],  # Efecto sutil
        textfont=dict(size=12, family='Arial')
    )])
    
    # Configuración elegante
    if es_movil:
        fig.update_layout(
            title={
                'text': '📊 Distribución de Riesgo',
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 14, 'color': '#2c3e50', 'family': 'Arial'}
            },
            showlegend=True,
            height=350,
            margin=dict(t=60, b=60, l=60, r=60),
            font=dict(size=11, family='Arial'),
            legend=dict(
                font=dict(size=10, family='Arial'),
                orientation="v"
            )
        )
    else:
        fig.update_layout(
            title={
                'text': '📊 Distribución de Cooperativas por Nivel de Riesgo',
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 16, 'color': '#2c3e50', 'family': 'Arial'}
            },
            showlegend=True,
            height=400,
            margin=dict(t=80, b=80, l=80, r=80),
            font=dict(size=12, family='Arial')
        )
    
    return fig

def crear_grafico_evolucion_interactivo(datos, cooperativa, es_movil=False):
    """Gráfico detallado para análisis individual con estilo elegante"""
    try:
        serie = datos[cooperativa]
        valores = serie.dropna()
        if len(valores) == 0:
            return None

        # Fechas alineadas con la serie
        if 'Fecha_Corte' in datos.columns:
            fechas = datos.loc[valores.index, 'Fecha_Corte']
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
        
        # PALETA DE COLORES MEJORADA
        paleta_colores = [
            '#0052A5',  # Azul Fondo Monetario
            '#D32F2F',  # Rojo intenso
            '#7B1FA2',  # Guindo/Morado
            '#388E3C',  # Verde financiero
            '#F57C00',  # Naranja
            '#5D4037',  # Marrón oscuro
            '#0288D1',  # Azul claro
        ]
        
        # Asignar color único basado en el nombre de la cooperativa
        color_index = hash(cooperativa) % len(paleta_colores)
        color_principal = paleta_colores[color_index]
        
        # LÍNEAS CON GROSOR AUMENTADO
        line_width = 2.5 if es_movil else 2.2  # GROSOR AUMENTADO
        marker_size = 6 if es_movil else 5
        
        fig.add_trace(
            go.Scatter(
                x=fechas, y=valores,
                mode='lines+markers',
                name='Mora Contable',
                line=dict(color=color_principal, width=line_width, shape='spline'),
                marker=dict(size=marker_size, color=color_principal, line=dict(width=1, color='white')),
                hovertemplate='<b>%{x|%b %Y}</b><br>Mora: <b>%{y:.2%}</b><extra></extra>'
            ),
            secondary_y=False
        )
        
        # Media móvil con estilo sutil
        if len(serie.dropna()) > 12:
            media_movil = serie.rolling(window=12, min_periods=1).mean()
            if es_movil and len(fechas) > 24:
                media_movil = media_movil.iloc[mask]
            else:
                media_movil = media_movil.loc[valores.index]
                
            fig.add_trace(
                go.Scatter(
                    x=fechas, y=media_movil,
                    mode='lines',
                    name='Tendencia (MM 12)',
                    line=dict(color='#2c3e50', width=1.8, dash='dot'),  # Grosor aumentado
                    hovertemplate='<b>%{x|%b %Y}</b><br>Tendencia: <b>%{y:.2%}</b><extra></extra>'
                ),
                secondary_y=False
            )
        
        # CONFIGURACIÓN ELEGANTE
        if es_movil:
            fig.update_layout(
                title={
                    'text': f'📈 {cooperativa}',
                    'x': 0.5,
                    'xanchor': 'center',
                    'font': {'size': 16, 'color': '#2c3e50', 'family': 'Arial'}
                },
                xaxis_title='Fecha',
                yaxis_title='Índice de Mora',
                yaxis_tickformat=".0%",
                hovermode='x unified',
                height=450,
                showlegend=True,
                plot_bgcolor='white',
                paper_bgcolor='white',
                font=dict(color='#2c3e50', size=12, family='Arial'),
                margin=dict(l=60, r=40, t=80, b=80),
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="center",
                    x=0.5,
                    font=dict(size=11),
                    bgcolor='rgba(255,255,255,0.9)'
                )
            )
        else:
            fig.update_layout(
                title={
                    'text': f'📈 Evolución del Índice de Mora - {cooperativa}',
                    'x': 0.5,
                    'xanchor': 'center',
                    'font': {'size': 18, 'color': '#2c3e50', 'family': 'Arial'}
                },
                xaxis_title='Fecha',
                yaxis_title='Índice de Mora',
                yaxis_tickformat=".0%",
                hovermode='x unified',
                height=500,
                showlegend=True,
                plot_bgcolor='white',
                paper_bgcolor='white',
                font=dict(color='#2c3e50', size=13, family='Arial'),
                margin=dict(l=60, r=60, t=80, b=80)
            )
        
        # Configuración elegante de ejes
        fig.update_xaxes(
            gridcolor='rgba(220, 220, 220, 0.5)',
            linecolor='rgba(200, 200, 200, 0.5)',
            tickfont=dict(size=11, family='Arial')
        )
        fig.update_yaxes(
            gridcolor='rgba(220, 220, 220, 0.5)',
            linecolor='rgba(200, 200, 200, 0.5)',
            tickfont=dict(size=11, family='Arial'),
            zerolinecolor='rgba(200, 200, 200, 0.3)'
        )
        
        if tickvals is not None:
            fig.update_xaxes(
                tickvals=tickvals, 
                ticktext=ticktext, 
                tickangle=45
            )
        
        return fig
        
    except Exception as e:
        import streamlit as st
        st.error(f"Error creando gráfico interactivo: {e}")
        return None