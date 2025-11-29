"""
GRÁFICOS INTERACTIVOS Y VISUALIZACIONES ELEGANTES
Optimizado para Móviles (Leyenda Inferior)
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
    
    # Cálculos básicos
    promedio = valores_validos.mean()
    
    # Paleta de colores
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
    
    # --- AJUSTE RESPONSIVO ---
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
    """Gráfico de torta/donas"""
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
        hole=0.5,
        marker=dict(colors=colores),
        textinfo='percent' if es_movil else 'label+percent',
        hovertemplate='<b>%{label}</b><br>%{value} Coop.<br>%{percent}',
        textfont=dict(size=12, family='Arial')
    )])
    
    if es_movil:
        # Leyenda abajo
        fig.update_layout(
            title={'text': 'Distribución de Riesgo', 'x': 0.5, 'xanchor': 'center'},
            showlegend=True,
            height=400,
            margin=dict(t=50, b=20, l=10, r=10),
            legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5)
        )
    else:
        fig.update_layout(
            title={'text': 'Distribución por Riesgo', 'x': 0.5, 'xanchor': 'center'},
            showlegend=True,
            height=400,
            margin=dict(t=80, b=80, l=80, r=80)
        )
    
    return fig

# --- 3. GRÁFICO DETALLADO (CORREGIDO LEYENDA INFERIOR) ---
def crear_grafico_evolucion_interactivo(datos, cooperativa, es_movil=False):
    """Gráfico principal grande con Media Móvil"""
    try:
        serie = datos[cooperativa]
        valores = serie.dropna()
        if len(valores) == 0:
            return None

        # Gestión de fechas
        if 'Fecha_Corte' in datos.columns:
            fechas = datos.loc[valores.index, 'Fecha_Corte']
        else:
            fechas = valores.index

        # OPTIMIZACIÓN MÓVIL
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
        
        # Color dinámico
        paleta = ['#0052A5', '#D32F2F', '#388E3C', '#F57C00', '#5D4037']
        color_p = paleta[hash(cooperativa) % len(paleta)]
        
        # 1. Línea Principal
        fig.add_trace(go.Scatter(
            x=fechas, y=valores,
            mode='lines+markers',
            name='Mora',
            line=dict(color=color_p, width=2.5 if es_movil else 2.2, shape='spline'),
            marker=dict(size=6 if es_movil else 5, color=color_p, line=dict(width=1, color='white')),
            hovertemplate='<b>%{x|%b %Y}</b><br>%{y:.2%}<extra></extra>'
        ))

        # 2. Media Móvil (Tendencia)
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
        
        # --- CONFIGURACIÓN DE ESTILO ---
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
            # === CONFIGURACIÓN MÓVIL CORREGIDA ===
            fig.update_layout(
                **layout_args,
                title=None, # SIN TÍTULO (Para ganar espacio arriba)
                height=450, # Altura generosa
                # MARGENES: Aumentamos 'b' (bottom) a 100px para que quepa la leyenda
                margin=dict(l=10, r=10, t=10, b=100), 
                showlegend=True,
                legend=dict(
                    orientation="h",       # Horizontal
                    yanchor="top",         # Anclar desde arriba de la caja...
                    y=-0.25,               # ...hacia ABAJO del eje X (negativo)
                    xanchor="center",
                    x=0.5,
                    bgcolor='rgba(255,255,255,0)'
                )
            )
        else:
            # === CONFIGURACIÓN ESCRITORIO ===
            fig.update_layout(
                **layout_args,
                title=dict(text=f'Evolución: {cooperativa}', font=dict(size=18), x=0.5, xanchor='center'),
                height=500,
                margin=dict(l=60, r=60, t=80, b=80),
                showlegend=True,
                legend=dict(orientation="v")
            )
        
        # Grid y Ejes
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