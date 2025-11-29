"""
MONITOREO FINANCIERO DE MORA 
Dashboard de Índice de Mora - Cooperativas Supervisadas
Archivo Principal
"""

import streamlit as st
from config.config import configurar_aplicacion, cargar_estilos_premium
from components.header import crear_header_premium
from components.footer import crear_footer_premium
from components.sidebar import crear_sidebar
from components.metrics import crear_metricas_principales
from data.data_loader import cargar_datos, identificar_cooperativas
from analysis.risk_analysis import analizar_riesgo
from visualization.charts import (
    crear_grafico_evolucion_interactivo, 
    crear_grafico_torta_interactivo,
    crear_grafico_individual_elegante
)

import matplotlib.pyplot as plt
import numpy as np
from utils.device_detector import es_dispositivo_movil, obtener_configuracion_dispositivo

def main():
    # Configuración inicial
    configurar_aplicacion()
    cargar_estilos_premium()
    crear_header_premium()
    
    # Carga de datos
    datos = cargar_datos()
    if datos is None:
        st.error("Sistema temporalmente no disponible")
        return
    
    cooperativas = identificar_cooperativas(datos)
    if not cooperativas:
        st.warning("No se encontraron cooperativas para graficar.")
        return
    
    # DETECCIÓN DE DISPOSITIVO
    config_dispositivo = obtener_configuracion_dispositivo()
    es_movil = config_dispositivo['es_movil']
    
    # Mostrar info del dispositivo (opcional, para debug)
    if es_movil:
        st.sidebar.info("📱 Modo móvil detectado")
    
    # Análisis de riesgo
    clasificacion_riesgo = analizar_riesgo(datos, cooperativas)
    
    # Sidebar
    cooperativa_seleccionada = crear_sidebar(cooperativas, clasificacion_riesgo)
    
    # Tabs principales
    tab1, tab2, tab3 = st.tabs([
        "📊 Dashboard General", 
        "🔍 Análisis por Cooperativa", 
        "📈 Reporte Resumido"
    ])
    
    with tab1:
        crear_metricas_principales(cooperativas, clasificacion_riesgo, datos)
        st.markdown("---")
        st.markdown("### 📈 Evolución del Índice de Mora por Cooperativa")
        
        # SISTEMA DE PAGINACIÓN ELEGANTE
        # Configuración de paginación
        graficos_por_pagina = 4
        total_paginas = (len(cooperativas) + graficos_por_pagina - 1) // graficos_por_pagina
        
        # Estado de la página actual
        if 'pagina_actual' not in st.session_state:
            st.session_state.pagina_actual = 1
        
        # Controles de paginación elegantes
        st.markdown("""
        <style>
        .pagination-btn {
            background-color: #f8f9fa;
            border: 1px solid #dee2e6;
            border-radius: 5px;
            padding: 8px 16px;
            margin: 2px;
        }
        .pagination-btn:hover {
            background-color: #e9ecef;
        }
        </style>
        """, unsafe_allow_html=True)
        
        col1, col2, col3, col4, col5 = st.columns([2, 1, 1, 1, 2])
        
        with col2:
            if st.button("◀️ Anterior", use_container_width=True, key="prev_btn") and st.session_state.pagina_actual > 1:
                st.session_state.pagina_actual -= 1
                st.rerun()
        
        with col3:
            st.markdown(f"""
            <div style="text-align: center; padding: 8px; background: #f8f9fa; border-radius: 5px;">
                <strong>Página {st.session_state.pagina_actual} de {total_paginas}</strong>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            if st.button("Siguiente ▶️", use_container_width=True, key="next_btn") and st.session_state.pagina_actual < total_paginas:
                st.session_state.pagina_actual += 1
                st.rerun()
        
        st.markdown("---")
        
        # Calcular qué cooperativas mostrar en esta página
        inicio_idx = (st.session_state.pagina_actual - 1) * graficos_por_pagina
        fin_idx = inicio_idx + graficos_por_pagina
        cooperativas_pagina = cooperativas[inicio_idx:fin_idx]
        
        # Crear 2 columnas para los gráficos (2x2 grid)
        cols = st.columns(2)
        
        for i, cooperativa in enumerate(cooperativas_pagina):
            col_idx = i % 2
            with cols[col_idx]:
                # Crear contenedor elegante para cada gráfico
                with st.container():
                    # Header del gráfico con color de riesgo
                    serie = datos[cooperativa]
                    valores_validos = serie.dropna()
                    
                    if len(valores_validos) == 0:
                        st.error(f"⛔ {cooperativa} - Sin datos")
                        continue
                    
                    ultimo_valor = valores_validos.iloc[-1]
                    
                    # Determinar color del header según riesgo
                    if ultimo_valor > 0.1:
                        color_header = '#e74c3c'
                        icono_riesgo = '🔴'
                    elif ultimo_valor > 0.05:
                        color_header = '#f39c12'
                        icono_riesgo = '🟡'
                    else:
                        color_header = '#27ae60'
                        icono_riesgo = '🟢'
                    
                    st.markdown(f"""
                    <div style="background: {color_header}; color: white; padding: 8px 12px; 
                             border-radius: 5px 5px 0 0; margin-bottom: -10px;">
                        <strong>{icono_riesgo} {cooperativa}</strong>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Crear gráfico elegante usando la nueva función
                    fig = crear_grafico_individual_elegante(datos, cooperativa, es_movil)
                    
                    if fig:
                        # Mostrar el gráfico
                        st.plotly_chart(fig, use_container_width=True, config={
                            'displayModeBar': False  # Más elegante sin barra de herramientas
                        })
                        
                        # Métricas elegantes debajo del gráfico
                        promedio = valores_validos.mean()
                        max_valor = valores_validos.max()
                        tendencia = "↗️" if ultimo_valor > promedio else "↘️" if ultimo_valor < promedio else "➡️"
                        
                        col_met1, col_met2, col_met3 = st.columns(3)
                        with col_met1:
                            st.metric(
                                label="Actual", 
                                value=f"{ultimo_valor:.1%}",
                                delta=f"{tendencia}"
                            )
                        with col_met2:
                            st.metric(
                                label="Promedio", 
                                value=f"{promedio:.1%}"
                            )
                        with col_met3:
                            st.metric(
                                label="Máximo", 
                                value=f"{max_valor:.1%}"
                            )
                    else:
                        st.error("Error al generar el gráfico")
        
        # Navegación inferior 
        st.markdown("---")
        st.caption(f"📊 Mostrando cooperativas {inicio_idx + 1} a {min(fin_idx, len(cooperativas))} de {len(cooperativas)} totales")
        
        # Botones de navegación al final
        if total_paginas > 1:
            col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
            with col_btn1:
                if st.button("⏪ Primera", use_container_width=True, key="first_btn") and st.session_state.pagina_actual > 1:
                    st.session_state.pagina_actual = 1
                    st.rerun()
            with col_btn2:
                # Selector de página
                pagina_seleccionada = st.selectbox(
                    "Ir a página:",
                    options=range(1, total_paginas + 1),
                    index=st.session_state.pagina_actual - 1,
                    key="page_selector",
                    label_visibility="collapsed"
                )
                if pagina_seleccionada != st.session_state.pagina_actual:
                    st.session_state.pagina_actual = pagina_seleccionada
                    st.rerun()
            with col_btn3:
                if st.button("Última ⏩", use_container_width=True, key="last_btn") and st.session_state.pagina_actual < total_paginas:
                    st.session_state.pagina_actual = total_paginas
                    st.rerun()
    
    with tab2:
        st.markdown(f"### 🔍 Resultados individual: **{cooperativa_seleccionada}**")
        
        # Gráfico principal CON DETECCIÓN DE DISPOSITIVO
        fig_interactivo = crear_grafico_evolucion_interactivo(datos, cooperativa_seleccionada, es_movil)
        if fig_interactivo:
            st.plotly_chart(
                fig_interactivo, 
                use_container_width=True, 
                key="grafico_evolucion_principal",
                config={
                    'responsive': True,
                    'displayModeBar': True,
                    'displaylogo': False,
                    'modeBarButtonsToRemove': ['pan2d', 'lasso2d', 'select2d'] if es_movil else []
                }
            )
        else:
            st.warning("No hay datos disponibles para esta cooperativa")
        
        # Indicadores de mora
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
            
            # Información adicional
            with st.expander("📊 Estadísticas"):
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
        st.markdown("### 📈 Por aproximacion de riesgo")
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.markdown("#### 📊 Distribución del Riesgo")
            fig_torta = crear_grafico_torta_interactivo(clasificacion_riesgo, es_movil)
            st.plotly_chart(
                fig_torta, 
                use_container_width=True, 
                key="grafico_torta_principal"
            )
        
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
    main()