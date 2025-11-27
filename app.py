"""
ASFI - SISTEMA DE MONITOREO FINANCIERO
Dashboard de Índice de Mora - Cooperativas Supervisadas

Desarrollado por: Gustavo Angelo Zabaleta
"""

import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import datetime
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# =============================================================================
# CONFIGURACIÓN INICIAL
# =============================================================================
def configurar_aplicacion():
    st.set_page_config(
        page_title="ASFI - Monitor Financiero Avanzado",
        page_icon="🏛️",
        layout="wide",
        initial_sidebar_state="expanded"
    )

# =============================================================================
# ESTILOS CSS PERSONALIZADOS
# =============================================================================
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

# =============================================================================
# CARGA Y PROCESAMIENTO DE DATOS
# =============================================================================
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

# =============================================================================
# ANÁLISIS DE MORA
# =============================================================================
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

# =============================================================================
# COMPONENTES DE VISUALIZACIÓN
# =============================================================================
def crear_grafico_torta_interactivo(clasificacion_riesgo):
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

def crear_grafico_evolucion_interactivo(_datos, cooperativa):
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

        # Elegir hasta 8 ticks distribuidos uniformemente
        tickvals, ticktext = None, None
        if len(fechas) > 1:
            n_ticks = min(8, len(fechas))
            idxs = np.linspace(0, len(fechas) - 1, n_ticks, dtype=int)
            tickvals = [fechas.iloc[i] for i in idxs]
            ticktext = [pd.to_datetime(d).strftime('%b %Y') for d in tickvals]

        fig = make_subplots(specs=[[{"secondary_y": False}]])
        
        fig.add_trace(
            go.Scatter(
                x=fechas, y=valores,
                mode='lines+markers',
                name='Mora Contable',
                line=dict(color='#0052A5', width=3),
                marker=dict(size=6, color='#0052A5'),
                hovertemplate='<b>%{x|%b %Y}</b><br>Mora: %{y:.3f}<extra></extra>'
            ),
            secondary_y=False
        )
        
        if len(serie.dropna()) > 12:
            media_movil = serie.rolling(window=12, min_periods=1).mean().loc[valores.index]
            fig.add_trace(
                go.Scatter(
                    x=fechas, y=media_movil,
                    mode='lines',
                    name='Media Móvil (12M)',
                    line=dict(color='#D32F2F', width=2, dash='dash'),
                    hovertemplate='<b>%{x|%b %Y}</b><br>Media Móvil: %{y:.3f}<extra></extra>'
                ),
                secondary_y=False
            )
        
        fig.update_layout(
            title=f'📈 Evolución del Índice de Mora - {cooperativa}',
            xaxis_title='Fecha',
            yaxis_title='Índice de Mora',
            hovermode='x unified',
            height=550,
            width=1150,
            showlegend=True,
            plot_bgcolor='rgba(248,249,250,0.8)',
            paper_bgcolor='rgba(255,255,255,0.9)',
            font=dict(color='#003366'),
            margin=dict(l=50, r=50, t=80, b=80)
        )
        
        if tickvals is not None:
            fig.update_xaxes(tickvals=tickvals, ticktext=ticktext, tickangle=45)
        
        return fig
        
    except Exception as e:
        st.error(f"Error creando gráfico interactivo: {e}")
        return None

# =============================================================================
# COMPONENTES DE INTERFAZ
# =============================================================================
def crear_header_premium():
    st.markdown("""
    <div class="header-premium">
        <div style="display: flex; align-items: center; justify-content: space-between;">
            <div>
                <h1 style="margin: 0; font-size: 2.5rem; font-weight: 700;text-align: center;">
                    🏛️ AUTOMATIZACION INDICADORES DE MORA
                </h1>
                <p style="margin: 0.5rem 0 0 0; font-size: 1.3rem; opacity: 0.95;">
                    Sistema de Monitoreo por cooperativas
                </p>
            </div>
            <div style="text-align: right;">
                <p style="margin: 0; font-size: 1rem; opacity: 0.9; font-weight: 500;">
                    Indice de Mora – Cooperativas Supervisadas
                </p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def crear_sidebar(_cooperativas, _clasificacion_riesgo):
    st.sidebar.markdown("### 🎛️ Panel de Control")
    
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
    with st.sidebar.expander("ℹ️ Información del Sistema"):
        st.write(f"**Cooperativas monitoreadas:** {len(_cooperativas)}")
        st.write(f"**Cooperativas activas:** {len(_cooperativas) - len(_clasificacion_riesgo['INACTIVAS'])}")
        st.write(f"**Última actualización:** {datetime.datetime.now().strftime('%d/%m/%Y')}")
    
    return cooperativa_seleccionada

def crear_metricas_principales(_cooperativas, _clasificacion_riesgo, _datos):
    st.markdown("### 📈 Panorama General del Sistema Financiero")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <h3 style="color: #0052A5; margin: 0; font-size: 2rem;">🏛️</h3>
            <h2 style="color: #003366; margin: 0.5rem 0; font-size: 2.2rem;">{len(_cooperativas)}</h2>
            <p style="color: #666; margin: 0; font-weight: 500;">Cooperativas Supervisadas</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        cooperativas_activas = len(_cooperativas) - len(_clasificacion_riesgo["INACTIVAS"])
        st.markdown(f"""
        <div class="metric-card metric-low-risk">
            <h3 style="color: #388E3C; margin: 0; font-size: 2rem;">📈</h3>
            <h2 style="color: #003366; margin: 0.5rem 0; font-size: 2.2rem;">{cooperativas_activas}</h2>
            <p style="color: #666; margin: 0; font-weight: 500;">Cooperativas Activas</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-card metric-high-risk">
            <h3 style="color: #D32F2F; margin: 0; font-size: 2rem;">⚠️</h3>
            <h2 style="color: #003366; margin: 0.5rem 0; font-size: 2.2rem;">{len(_clasificacion_riesgo['ALTO RIESGO'])}</h2>
            <p style="color: #666; margin: 0; font-weight: 500;">Alto Riesgo</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        moras_activas = []
        for coop in _cooperativas:
            if coop not in _clasificacion_riesgo['INACTIVAS']:
                valores = _datos[coop].dropna()
                if len(valores) > 0:
                    moras_activas.append(valores.iloc[-1])
        
        mora_promedio = np.mean(moras_activas) if moras_activas else 0
        st.markdown(f"""
        <div class="metric-card">
            <h3 style="color: #0052A5; margin: 0; font-size: 2rem;">📊</h3>
            <h2 style="color: #003366; margin: 0.5rem 0; font-size: 2.2rem;">{mora_promedio*100:.2f}%</h2>
            <p style="color: #666; margin: 0; font-weight: 500;">Mora Promedio</p>
        </div>
        """, unsafe_allow_html=True)

def crear_footer_premium():
    st.markdown("""
    <div class="footer-premium">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <div style="text-align: left;">
                <p style="margin: 0; font-size: 0.9rem; font-weight: 300;">
                    Datos extraídos de los EEFF mensuales de ASFI
                </p>
            </div>
            <div style="text-align: right;">
                <p style="margin: 0; font-size: 0.9rem; font-weight: 500;">
                    Desarrollado por Gustavo Angelo Zabaleta
                </p>
                <p style="margin: 0.3rem 0 0 0; font-size: 0.8rem; opacity: 0.8;">
                    Actualizado: {fecha_actual}
                </p>
            </div>
        </div>
    </div>
    """.format(fecha_actual=datetime.datetime.now().strftime('%d/%m/%Y %H:%M')), 
    unsafe_allow_html=True)

# =============================================================================
# FUNCIÓN PRINCIPAL
# =============================================================================
def main():
    configurar_aplicacion()
    cargar_estilos_premium()
    crear_header_premium()
    
    datos = cargar_datos()
    if datos is None:
        st.error("Sistema temporalmente no disponible")
        return
    
    cooperativas = identificar_cooperativas(datos)
    if not cooperativas:
        st.warning("No se encontraron cooperativas para graficar.")
        return
    
    clasificacion_riesgo = analizar_riesgo(datos, cooperativas)
    
    cooperativa_seleccionada = crear_sidebar(cooperativas, clasificacion_riesgo)
    
    tab1, tab2, tab3 = st.tabs([
        "📊 Dashboard General", 
        "🔍 Análisis por Cooperativa", 
        "📈 Reporte Ejecutivo"
    ])
    
    with tab1:
        crear_metricas_principales(cooperativas, clasificacion_riesgo, datos)
        st.markdown("---")
        st.markdown("### 📈 Evolución del Índice de Mora por Cooperativa")
        
        # === Bloque de plotting (reemplaza el anterior) ===
        n_cols = 3
        n_rows = (len(cooperativas) + n_cols - 1) // n_cols
        height_per_row = 5.5
        fig, axes = plt.subplots(n_rows, n_cols, figsize=(22, height_per_row * n_rows))
        fig.patch.set_facecolor('#ffffff')
        
        # Aplanar axes a vector 1D
        axes = np.array(axes).reshape(-1)
        
        colores_corporativos = ['#0052A5', '#D32F2F', '#388E3C', '#FF9800', '#7B1FA2', '#0097A7']
        
        # Asegurar 'Fecha_Corte' datetime y orden (ya hecho en cargar_datos, pero por seguridad)
        if 'Fecha_Corte' in datos.columns:
            if not np.issubdtype(datos['Fecha_Corte'].dtype, np.datetime64):
                datos['Fecha_Corte'] = pd.to_datetime(datos['Fecha_Corte'])
            datos = datos.sort_values('Fecha_Corte').reset_index(drop=True)
        
        from matplotlib.dates import AutoDateLocator, ConciseDateFormatter
        
        for i, cooperativa in enumerate(cooperativas):
            ax = axes[i]
            
            serie = datos[cooperativa]
            mask = serie.notna()
            fechas_validas = datos.loc[mask, 'Fecha_Corte']
            valores_validos = serie[mask]
            
            if len(valores_validos) == 0:
                ax.text(0.5, 0.5, 'SIN DATOS', transform=ax.transAxes,
                        ha='center', va='center', fontsize=12, color='#999')
                ax.set_title(f'{cooperativa}', fontsize=11, fontweight='bold', color='#666')
                ax.set_facecolor('#f8f9fa')
                ax.set_ylim(0, 0.2)
                continue
            
            color_serie = colores_corporativos[i % len(colores_corporativos)]
            
            # Graficar solo valores válidos
            ax.plot(fechas_validas, valores_validos,
                    linewidth=1.6,
                    color=color_serie,
                    marker='o',
                    markersize=4,
                    alpha=0.85)
            
            # Media móvil (alineada a fechas válidas)
            if len(serie.dropna()) > 12:
                try:
                    ma = serie.rolling(window=12, min_periods=1).mean()
                    ma_valid = ma[mask]
                    ax.plot(fechas_validas, ma_valid,
                            linewidth=2.0,
                            color='#003366',
                            alpha=0.8,
                            linestyle='--')
                except Exception:
                    pass
            
            # Estética
            ax.set_facecolor('#ffffff')
            for spine in ax.spines.values():
                spine.set_color('#e0e0e0')
                spine.set_linewidth(0.8)
            
            mora_promedio = valores_validos.mean()
            color_titulo = '#D32F2F' if mora_promedio > 0.1 else '#FF9800' if mora_promedio > 0.05 else '#388E3C'
            ax.set_title(f'{cooperativa}', fontsize=12, fontweight='bold', color=color_titulo, pad=8)
            
            # Locator y formatter adaptativos
            locator = AutoDateLocator(minticks=4, maxticks=8)
            formatter = ConciseDateFormatter(locator)
            ax.xaxis.set_major_locator(locator)
            ax.xaxis.set_major_formatter(formatter)
            ax.tick_params(axis='x', rotation=30, labelsize=9, colors='#666')
            ax.tick_params(axis='y', labelsize=9, colors='#666')
            ax.grid(True, alpha=0.28, color='#e0e0e0', linestyle='-', linewidth=0.5)
            ax.set_ylim(bottom=0)
        
        # Ocultar axes sobrantes
        for j in range(len(cooperativas), len(axes)):
            axes[j].set_visible(False)
        
        plt.suptitle('EVOLUCIÓN DEL ÍNDICE DE MORA - PANORAMA DEL SISTEMA',
                     fontsize=16, fontweight='bold', color='#003366', y=0.98)
        plt.tight_layout()
        plt.subplots_adjust(top=0.93, bottom=0.05)
        st.pyplot(fig)
        # === Fin bloque de plotting ===
    
    with tab2:
        st.markdown(f"### 🔍 Resultados individual: **{cooperativa_seleccionada}**")
        
        # GRÁFICO PRINCIPAL - AHORA OCUPA TODO EL ANCHO
        fig_interactivo = crear_grafico_evolucion_interactivo(datos, cooperativa_seleccionada)
        if fig_interactivo:
            st.plotly_chart(fig_interactivo, use_container_width=True, key="grafico_principal")
        else:
            st.warning("No hay datos disponibles para esta cooperativa")
        
        # INDICADORES DE MORA - AHORA EN LA PARTE INFERIOR
        st.markdown("---")
        st.markdown("#### 📋 Indicadores de Mora")
        
        valores = datos[cooperativa_seleccionada].dropna()
        if len(valores) > 0:
            ultimo_valor = valores.iloc[-1]
            promedio = valores.mean()
            max_valor = valores.max()
            min_valor = valores.min()
            desviacion = valores.std()
            tendencia = "↗️ ALTA" if ultimo_valor > promedio else "↘️ BAJA" if ultimo_valor < promedio else "➡️ ESTABLE"
            
            # Crear 4 columnas para los indicadores principales
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.markdown(f"""
                <div class="metric-card">
                    <h4 style="color: #003366; margin: 0;">Último Dato</h4>
                    <h2 style="color: #0052A5; margin: 0.5rem 0; font-size: 1.8rem;">{ultimo_valor*100:.2f}%</h2>
                    <p style="color: #666; margin: 0; font-size: 0.9rem;">Tendencia: {tendencia}</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"""
                <div class="metric-card">
                    <h4 style="color: #003366; margin: 0;">Promedio Histórico</h4>
                    <h2 style="color: #0052A5; margin: 0.5rem 0; font-size: 1.8rem;">{promedio*100:.2f}%</h2>
                    <p style="color: #666; margin: 0; font-size: 0.9rem;">{len(valores)} meses</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col3:
                riesgo_color = "#D32F2F" if ultimo_valor > 0.1 else "#FF9800" if ultimo_valor > 0.05 else "#388E3C"
                riesgo_texto = "ALTO RIESGO" if ultimo_valor > 0.1 else "RIESGO MODERADO" if ultimo_valor > 0.05 else "BAJO RIESGO"
                riesgo_icon = "🔴" if ultimo_valor > 0.1 else "🟡" if ultimo_valor > 0.05 else "🟢"
                
                st.markdown(f"""
                <div class="metric-card" style="border-left: 5px solid {riesgo_color};">
                    <h4 style="color: #003366; margin: 0;">Nivel de Riesgo</h4>
                    <h3 style="color: {riesgo_color}; margin: 0.5rem 0; font-size: 1.4rem;">{riesgo_icon} {riesgo_texto}</h3>
                </div>
                """, unsafe_allow_html=True)
            
            with col4:
                st.markdown(f"""
                <div class="metric-card">
                    <h4 style="color: #003366; margin: 0;">Variabilidad</h4>
                    <h2 style="color: #0052A5; margin: 0.5rem 0; font-size: 1.8rem;">{desviacion*100:.2f}%</h2>
                    <p style="color: #666; margin: 0; font-size: 0.9rem;">Desviación estándar</p>
                </div>
                """, unsafe_allow_html=True)
            
            # Información adicional en un expander
            with st.expander("📊 Estadísticas Detalladas"):
                col5, col6, col7 = st.columns(3)
                with col5:
                    st.metric("Valor Máximo Histórico", f"{max_valor*100:.2f}%")
                with col6:
                    st.metric("Valor Mínimo Histórico", f"{min_valor*100:.2f}%")
                with col7:
                    st.metric("Rango de Variación", f"{(max_valor-min_valor)*100:.2f}%")
        else:
            st.warning("No hay datos disponibles para el análisis")
    
    with tab3:
        st.markdown("### 📈 Reporte Ejecutivo del Sistema")
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.markdown("#### 📊 Distribución del Riesgo")
            fig_torta = crear_grafico_torta_interactivo(clasificacion_riesgo)
            st.plotly_chart(fig_torta, use_container_width=True, key="grafico_torta")
        
        with col2:
            st.markdown("#### 📈 Tendencias del Sistema")
            
            moras_activas = []
            for coop in cooperativas:
                if coop not in clasificacion_riesgo['INACTIVAS']:
                    valores = datos[coop].dropna()
                    if len(valores) > 0:
                        moras_activas.append(valores.iloc[-1])
            
            if moras_activas:
                st.markdown(f"""
                <div class="metric-card">
                    <h4 style="color: #003366; margin: 0;">Mora Promedio del Sistema</h4>
                    <h2 style="color: #0052A5; margin: 0.5rem 0; font-size: 2rem;">{np.mean(moras_activas)*100:.2f}%</h2>
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown(f"""
                <div class="metric-card metric-high-risk">
                    <h4 style="color: #003366; margin: 0;">Mora Máxima Registrada</h4>
                    <h2 style="color: #D32F2F; margin: 0.5rem 0; font-size: 2rem;">{np.max(moras_activas)*100:.2f}%</h2>
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown(f"""
                <div class="metric-card metric-low-risk">
                    <h4 style="color: #003366; margin: 0;">Mora Mínima Registrada</h4>
                    <h2 style="color: #388E3C; margin: 0.5rem 0; font-size: 2rem;">{np.min(moras_activas)*100:.2f}%</h2>
                </div>
                """, unsafe_allow_html=True)
    
    crear_footer_premium()

if __name__ == "__main__":
    main()streamlit run app.py