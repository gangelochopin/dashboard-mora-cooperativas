"""
ASFI - SISTEMA DE MONITOREO FINANCIERO
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
from visualization.charts import crear_grafico_evolucion_interactivo, crear_grafico_torta_interactivo
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
        "📈 Reporte Ejecutivo"
    ])
    
    with tab1:
        crear_metricas_principales(cooperativas, clasificacion_riesgo, datos)
        st.markdown("---")
        st.markdown("### 📈 Evolución del Índice de Mora por Cooperativa")
        
        # Gráficos matplotlib
        n_cols = 3
        n_rows = (len(cooperativas) + n_cols - 1) // n_cols
        height_per_row = 5.5
        fig, axes = plt.subplots(n_rows, n_cols, figsize=(22, height_per_row * n_rows))
        fig.patch.set_facecolor('#ffffff')
        axes = np.array(axes).reshape(-1)
        
        colores_corporativos = ['#0052A5', '#D32F2F', '#388E3C', '#FF9800', '#7B1FA2', '#0097A7']
        
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
            ax.plot(fechas_validas, valores_validos,
                    linewidth=1.6, color=color_serie, marker='o', markersize=4, alpha=0.85)
            
            # Media móvil
            if len(serie.dropna()) > 12:
                try:
                    ma = serie.rolling(window=12, min_periods=1).mean()
                    ma_valid = ma[mask]
                    ax.plot(fechas_validas, ma_valid, linewidth=2.0, color='#003366', alpha=0.8, linestyle='--')
                except Exception:
                    pass
            
            # Configuración del gráfico
            ax.set_facecolor('#ffffff')
            for spine in ax.spines.values():
                spine.set_color('#e0e0e0')
                spine.set_linewidth(0.8)
            
            mora_promedio = valores_validos.mean()
            color_titulo = '#D32F2F' if mora_promedio > 0.1 else '#FF9800' if mora_promedio > 0.05 else '#388E3C'
            ax.set_title(f'{cooperativa}', fontsize=12, fontweight='bold', color=color_titulo, pad=8)
            
            from matplotlib.dates import AutoDateLocator, ConciseDateFormatter
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