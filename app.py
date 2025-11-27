# app.py
import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import datetime
import os

# Configuración de la página
st.set_page_config(
    page_title="Dashboard Índice de Mora - ASFI",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Título principal
st.title("📊 EVOLUCIÓN DEL ÍNDICE DE MORA")
st.subheader("Sistema Financiero - Cooperativo")

# CARGAR DATOS DESDE ARCHIVO CSV
@st.cache_data
def load_data():
    """Cargar datos desde archivo CSV de forma segura"""
    try:
        # Cargar directamente sin mostrar información interna
        indice_mora = pd.read_csv('indice_mora.csv')
        
        # Convertir Fecha_Corte a datetime si existe
        if 'Fecha_Corte' in indice_mora.columns:
            indice_mora['Fecha_Corte'] = pd.to_datetime(indice_mora['Fecha_Corte'])
        elif 'Fecha' in indice_mora.columns:
            indice_mora['Fecha_Corte'] = pd.to_datetime(indice_mora['Fecha'])
        
        return indice_mora
        
    except Exception as e:
        st.error("❌ Error al cargar los datos del sistema")
        return None

# Cargar datos
indice_mora = load_data()

# VERIFICAR DATOS
if indice_mora is None:
    st.error("""
    ❌ **No se pudieron cargar los datos del sistema.**
    
    Por favor, contacte al administrador del sistema.
    """)
    st.stop()

# Identificar cooperativas (columnas numéricas excluyendo Fecha_Corte)
columnas_numericas = indice_mora.select_dtypes(include=[np.number]).columns.tolist()

# Si no hay Fecha_Corte, usar la primera columna no numérica como fecha
if 'Fecha_Corte' not in indice_mora.columns:
    columnas_no_numericas = indice_mora.select_dtypes(exclude=[np.number]).columns.tolist()
    if columnas_no_numericas:
        indice_mora['Fecha_Corte'] = pd.to_datetime(indice_mora[columnas_no_numericas[0]])

coops_a_graficar = [col for col in columnas_numericas if col != 'Fecha_Corte']

if not coops_a_graficar:
    st.error("❌ Configuración incorrecta del sistema")
    st.stop()

# SIDEBAR CONTROLES (limpio y profesional)
st.sidebar.header("🎛️ Controles de Visualización")

# Selector de cooperativa
coop_seleccionada = st.sidebar.selectbox(
    "🔍 Seleccionar Cooperativa:",
    options=coops_a_graficar
)

# Filtro por rango de fechas (solo si hay fechas)
if 'Fecha_Corte' in indice_mora.columns:
    fecha_min = indice_mora['Fecha_Corte'].min()
    fecha_max = indice_mora['Fecha_Corte'].max()
    
    rango_fechas = st.sidebar.date_input(
        "📅 Rango de Fechas:",
        value=(fecha_min, fecha_max),
        min_value=fecha_min,
        max_value=fecha_max
    )

# ANÁLISIS DE RIESGO (sin información interna)
st.sidebar.header("📈 Indicadores de Mora")

if 'Fecha_Corte' in indice_mora.columns:
    fecha_mas_reciente = indice_mora['Fecha_Corte'].max()
    fecha_limite = fecha_mas_reciente - pd.DateOffset(months=6)
else:
    fecha_limite = indice_mora.index.min()

coops_por_mora = {"ALTO RIESGO": [], "RIESGO MODERADO": [], "BAJO RIESGO": [], "SIN DATOS RECIENTES": []}

for cooperativa in coops_a_graficar:
    if 'Fecha_Corte' in indice_mora.columns:
        datos_recientes = indice_mora[indice_mora['Fecha_Corte'] >= fecha_limite]
        valores_recientes = datos_recientes[cooperativa].dropna()
    else:
        valores_recientes = indice_mora[cooperativa].dropna()
    
    if len(valores_recientes) > 0:
        ultima_mora = valores_recientes.iloc[-1]
        if ultima_mora > 0.1:
            coops_por_mora["ALTO RIESGO"].append(cooperativa)
        elif ultima_mora > 0.05:
            coops_por_mora["RIESGO MODERADO"].append(cooperativa)
        else:
            coops_por_mora["BAJO RIESGO"].append(cooperativa)
    else:
        coops_por_mora["SIN DATOS RECIENTES"].append(cooperativa)

# Métricas de riesgo en sidebar (limpias)
st.sidebar.metric("🔴 Alto Riesgo", len(coops_por_mora["ALTO RIESGO"]))
st.sidebar.metric("🟡 Riesgo Moderado", len(coops_por_mora["RIESGO MODERADO"]))
st.sidebar.metric("🟢 Bajo Riesgo", len(coops_por_mora["BAJO RIESGO"]))
st.sidebar.metric("⚫ Inactivas", len(coops_por_mora["SIN DATOS RECIENTES"]))

# Información del sistema (discreta)
with st.sidebar.expander("ℹ️ Información del Sistema"):
    st.write(f"**Cooperativas monitoreadas:** {len(coops_a_graficar)}")
    if 'Fecha_Corte' in indice_mora.columns:
        st.write(f"**Período analizado:** {indice_mora['Fecha_Corte'].min().strftime('%Y')}-{indice_mora['Fecha_Corte'].max().strftime('%Y')}")
    st.write(f"**Última actualización:** {datetime.datetime.now().strftime('%d/%m/%Y')}")

# MAIN CONTENT - PESTAÑAS
tab1, tab2, tab3 = st.tabs(["📈 Vista General", "🔍 Análisis Individual", "📊 Resumen Ejecutivo"])

with tab1:
    st.header("Mora Contable > a 30 dias")
    
    # Crear el dashboard principal
    colores_corporativos = [
        '#2E86AB', '#A23B72', '#F18F01', '#C73E1D', '#3B1F2B',
        '#6B8E23', '#8B1E3F', '#2A9D8F', '#E76F51', '#264653'
    ]
    
    n_cols = 4
    n_rows = (len(coops_a_graficar) + n_cols - 1) // n_cols
    
    fig, axes = plt.subplots(n_rows, n_cols, figsize=(20, 5 * n_rows))
    fig.patch.set_facecolor('#f8f9fa')
    
    if n_rows > 1:
        axes = axes.flatten()
    else:
        axes = [axes] if n_cols == 1 else list(axes.flat) if hasattr(axes, 'flat') else [axes]
    
    for i, cooperativa in enumerate(coops_a_graficar):
        if i >= len(axes):
            continue
            
        ax = axes[i]
        
        if 'Fecha_Corte' in indice_mora.columns:
            fechas = indice_mora['Fecha_Corte']
        else:
            fechas = range(len(indice_mora))
            
        valores = indice_mora[cooperativa]
        valores_validos = valores.dropna()
        
        if len(valores_validos) == 0:
            ax.text(0.5, 0.5, 'SIN DATOS', transform=ax.transAxes, 
                    ha='center', va='center', fontsize=12, color='red')
            ax.set_title(f'{cooperativa}', fontsize=10, fontweight='bold')
            continue
        
        color_serie = colores_corporativos[i % len(colores_corporativos)]
        
        # Gráfico principal
        ax.plot(fechas, valores, 
                linewidth=2.0,
                color=color_serie,
                marker='o',
                markersize=2,
                markerfacecolor=color_serie,
                markeredgecolor='white',
                markeredgewidth=0.5,
                alpha=0.8)
        
        # Media móvil
        if len(valores_validos) > 12:
            try:
                media_movil = valores.rolling(window=12, min_periods=1).mean()
                ax.plot(fechas, media_movil, 
                        linewidth=2.5,
                        color='#2c3e50',
                        alpha=0.8,
                        linestyle='--')
            except Exception:
                pass
        
        ax.set_facecolor('#ffffff')
        for spine in ax.spines.values():
            spine.set_color('#d1d1d1')
            spine.set_linewidth(0.5)
        
        mora_promedio = valores_validos.mean()
        color_titulo = '#e74c3c' if mora_promedio > 0.1 else '#f39c12' if mora_promedio > 0.05 else '#27ae60'
        
        simbolo_riesgo = '●' if mora_promedio > 0.1 else '▲' if mora_promedio > 0.05 else '■'
        
        ax.set_title(f'{simbolo_riesgo} {cooperativa}', 
                    fontsize=11, 
                    fontweight='bold', 
                    color=color_titulo,
                    pad=10)
        
        ax.tick_params(axis='x', rotation=45, labelsize=8, colors='#555555')
        ax.tick_params(axis='y', labelsize=8, colors='#555555')
        ax.grid(True, alpha=0.2, color='#d1d1d1', linestyle='-', linewidth=0.5)
        ax.set_ylim(bottom=0)
        
        ultimo_valor = valores_validos.iloc[-1]
        primer_valor = valores_validos.iloc[0]
        
        if primer_valor > 0:
            variacion = ((ultimo_valor - primer_valor) / primer_valor * 100)
        else:
            variacion = 0
        
        info_text = f"Ult: {ultimo_valor:.3f}\nVar: {variacion:+.1f}%\nDatos: {len(valores_validos)}"
        
        ax.text(0.02, 0.98, info_text, transform=ax.transAxes, fontsize=7,
                verticalalignment='top',
                bbox=dict(boxstyle='round', facecolor='#f8f9fa', 
                         edgecolor='#d1d1d1', alpha=0.9),
                fontweight='bold',
                color='#2c3e50')
    
    for i in range(len(coops_a_graficar), len(axes)):
        axes[i].set_visible(False)
    
    plt.suptitle('EVOLUCIÓN DEL ÍNDICE DE MORA POR COOPERATIVA', 
                 fontsize=16, 
                 fontweight='bold', 
                 color='#2c3e50',
                 y=0.98)
    
    plt.tight_layout()
    plt.subplots_adjust(top=0.94, bottom=0.03)
    
    st.pyplot(fig)

with tab2:
    st.header("Análisis Individual Detallado")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader(f"📈 {coop_seleccionada}")
        
        # Filtrar por fecha si se seleccionó un rango
        if 'Fecha_Corte' in indice_mora.columns and len(rango_fechas) == 2:
            fecha_inicio, fecha_fin = rango_fechas
            datos_filtrados = indice_mora[
                (indice_mora['Fecha_Corte'] >= pd.to_datetime(fecha_inicio)) & 
                (indice_mora['Fecha_Corte'] <= pd.to_datetime(fecha_fin))
            ]
        else:
            datos_filtrados = indice_mora
        
        # Crear gráfico individual
        fig_individual, ax_individual = plt.subplots(figsize=(12, 6))
        
        if 'Fecha_Corte' in datos_filtrados.columns:
            fechas = datos_filtrados['Fecha_Corte']
        else:
            fechas = range(len(datos_filtrados))
            
        valores = datos_filtrados[coop_seleccionada]
        valores_validos = valores.dropna()
        
        if len(valores_validos) > 0:
            color_idx = coops_a_graficar.index(coop_seleccionada) % len(colores_corporativos)
            color_serie = colores_corporativos[color_idx]
            
            # Gráfico principal
            ax_individual.plot(fechas, valores, 
                              linewidth=2.5, 
                              color=color_serie,
                              marker='o',
                              markersize=4,
                              alpha=0.9,
                              label='Mora Contable')
            
            # Media móvil
            if len(valores_validos) > 12:
                media_movil = valores.rolling(window=12, min_periods=1).mean()
                ax_individual.plot(fechas, media_movil, 
                                  linewidth=3, 
                                  color='#2c3e50', 
                                  alpha=0.7,
                                  linestyle='--',
                                  label='Media Móvil 12M')
            
            ax_individual.set_title(f'Índice de Mora - {coop_seleccionada}', fontsize=16, fontweight='bold')
            ax_individual.set_xlabel('Fecha', fontsize=12)
            ax_individual.set_ylabel('Índice de Mora', fontsize=12)
            ax_individual.grid(True, alpha=0.3)
            ax_individual.legend(fontsize=10)
            if 'Fecha_Corte' in datos_filtrados.columns:
                ax_individual.tick_params(axis='x', rotation=45)
            
            # Estadísticas
            ultimo_valor = valores_validos.iloc[-1]
            max_valor = valores_validos.max()
            min_valor = valores_validos.min()
            promedio = valores_validos.mean()
            
            stats_text = f"Último: {ultimo_valor:.3f}\nMáximo: {max_valor:.3f}\nMínimo: {min_valor:.3f}\nPromedio: {promedio:.3f}"
            ax_individual.text(0.02, 0.98, stats_text, transform=ax_individual.transAxes, fontsize=10,
                              verticalalignment='top',
                              bbox=dict(boxstyle='round', facecolor='white', edgecolor='gray', alpha=0.8))
        
        st.pyplot(fig_individual)
    
    with col2:
        st.subheader("📋 Indicadores Clave")
        
        if len(valores_validos) > 0:
            col_met1, col_met2 = st.columns(2)
            
            with col_met1:
                st.metric("Último Valor", f"{ultimo_valor:.3f}")
                st.metric("Valor Máximo", f"{max_valor:.3f}")
            
            with col_met2:
                st.metric("Valor Mínimo", f"{min_valor:.3f}")
                st.metric("Promedio Histórico", f"{promedio:.3f}")
            
            # Información adicional
            st.info(f"""
            **Información de la Serie:**
            - Período analizado: {len(valores_validos)} meses
            - Tasa de completitud: {len(valores_validos)/len(valores)*100:.1f}%
            """)
            
            # Nivel de riesgo actual
            if ultimo_valor > 0.1:
                st.error(f"🔴 ALTO RIESGO: {ultimo_valor:.1%}")
            elif ultimo_valor > 0.05:
                st.warning(f"🟡 RIESGO MODERADO: {ultimo_valor:.1%}")
            else:
                st.success(f"🟢 BAJO RIESGO: {ultimo_valor:.1%}")
        
        else:
            st.warning("⚠️ No hay datos disponibles para el análisis")

with tab3:
    st.header("Resumen Ejecutivo del Sistema")
    
    # Métricas generales
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Entidades", len(coops_a_graficar))
    
    with col2:
        cooperativas_activas = len(coops_a_graficar) - len(coops_por_mora["SIN DATOS RECIENTES"])
        st.metric("Entidades Activas", cooperativas_activas)
    
    with col3:
        if 'Fecha_Corte' in indice_mora.columns:
            periodo = f"{indice_mora['Fecha_Corte'].min().strftime('%Y')}-{indice_mora['Fecha_Corte'].max().strftime('%Y')}"
        else:
            periodo = "Período completo"
        st.metric("Horizonte Analítico", periodo)
    
    with col4:
        st.metric("Tasa de Actividad", f"{(cooperativas_activas/len(coops_a_graficar))*100:.1f}%")
    
    # Distribución de riesgo
    st.subheader("Distribución por Nivel de Riesgo")
    
    col_riesgo1, col_riesgo2, col_riesgo3, col_riesgo4 = st.columns(4)
    
    with col_riesgo1:
        with st.container():
            st.markdown("### 🔴")
            st.markdown(f"**Alto Riesgo**\n\n**{len(coops_por_mora['ALTO RIESGO'])}** entidades")
    
    with col_riesgo2:
        with st.container():
            st.markdown("### 🟡")
            st.markdown(f"**Riesgo Moderado**\n\n**{len(coops_por_mora['RIESGO MODERADO'])}** entidades")
    
    with col_riesgo3:
        with st.container():
            st.markdown("### 🟢")
            st.markdown(f"**Bajo Riesgo**\n\n**{len(coops_por_mora['BAJO RIESGO'])}** entidades")
    
    with col_riesgo4:
        with st.container():
            st.markdown("### ⚫")
            st.markdown(f"**Inactivas**\n\n**{len(coops_por_mora['SIN DATOS RECIENTES'])}** entidades")

# Footer profesional
st.markdown("---")
st.caption(f"Sistema de Monitoreo Financiero • ASFI • Actualizado: {datetime.datetime.now().strftime('%d/%m/%Y')}")