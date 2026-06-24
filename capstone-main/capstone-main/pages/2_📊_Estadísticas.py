import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go



st.markdown("""
<style>
.stats-header {
    text-align: center;
    margin-bottom: 2rem;
}
.stats-header h1 {
    font-size: 2.2rem;
    font-weight: 800;
    color: #1e3a5f;
    margin: 0.5rem 0 0.2rem 0;
}
.stats-header p {
    color: #6b7280;
    font-size: 1.1rem;
    margin: 0;
}
.metric-card {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    border-radius: 16px;
    padding: 1.5rem;
    color: white;
    text-align: center;
    box-shadow: 0 4px 12px rgba(0,0,0,0.15);
}
.metric-value {
    font-size: 2.5rem;
    font-weight: 800;
    margin: 0.5rem 0;
}
.metric-label {
    font-size: 0.95rem;
    opacity: 0.9;
    text-transform: uppercase;
    letter-spacing: 1px;
}
</style>
""", unsafe_allow_html=True)


df = st.session_state['df']

st.markdown("""
<div class="stats-header">
    <h1> Análisis Estadístico</h1>
    <p>Intervenciones del Camión Vactor · 2018-2025</p>
</div>
""", unsafe_allow_html=True)


st.sidebar.header("Filtros de Visualización")

# Lista de años disponibles
años_disponibles = sorted(df['Año'].unique())
opciones_año = ["Todos los años (Promedio)"] + [str(año) for año in años_disponibles]

año_seleccionado = st.sidebar.selectbox(
    "Seleccione el Año:",
    opciones_año,
    index=0
)

# Filtro de nivel territorial
nivel_territorial = st.sidebar.selectbox(
    "Nivel Territorial:",
    ["Microsector", "Macrosector", "Unidad Vecinal"]
)

st.sidebar.divider()
st.sidebar.info("""
💡 **Acerca de las estadísticas:**

- **Visitas por Mes**: Cantidad total de intervenciones realizadas cada mes.
- **Promedio**: Cuando se selecciona "Todos los años", se muestra el promedio de visitas por mes considerando los 8 años de historial (2018-2025).
- **Año Específico**: Al seleccionar un año, se muestran las visitas reales de ese período.
""")


meses_orden = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
               'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']

if año_seleccionado == "Todos los años (Promedio)":
    # Calcular total y promedio de visitas por mes a través de todos los años
    df_agrupado = df.groupby('Mes').size().reset_index(name='Visitas')
    
    # Guardar el total para la suma
    num_años = len(años_disponibles)
    df_agrupado['Promedio'] = (df_agrupado['Visitas'] / num_años).round(1)
    
    titulo_grafico = "Promedio de Visitas Mensuales (2018-2025)"
    titulo_metrica = "Total Histórico"
    total_visitas = df_agrupado['Visitas'].sum()
    
    # Para el gráfico usamos el promedio
    df_agrupado['Visitas_Grafico'] = df_agrupado['Promedio']
    
else:
    # Filtrar por año específico
    año_num = int(año_seleccionado)
    df_año = df[df['Año'] == año_num]
    df_agrupado = df_año.groupby('Mes').size().reset_index(name='Visitas')
    
    titulo_grafico = f"Visitas Mensuales en {año_seleccionado}"
    titulo_metrica = f"Total {año_seleccionado}"
    total_visitas = df_agrupado['Visitas'].sum()
    
    # Para el gráfico usamos las visitas directas
    df_agrupado['Visitas_Grafico'] = df_agrupado['Visitas']

# Asegurar que todos los meses estén presentes (incluso con 0 visitas)
df_completo = pd.DataFrame({'Mes': meses_orden})
df_agrupado = df_completo.merge(df_agrupado, on='Mes', how='left').fillna(0)

# Agregar número de mes para ordenar correctamente
df_agrupado['Mes_num'] = df_agrupado['Mes'].apply(lambda x: meses_orden.index(x) + 1)
df_agrupado = df_agrupado.sort_values('Mes_num')



col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(f"""
    <div class="metric-card" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);">
        <div class="metric-label">Visitas Totales</div>
        <div class="metric-value">{total_visitas:,.0f}</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    if año_seleccionado == "Todos los años (Promedio)":
        mes_mas_visitado = df_agrupado.loc[df_agrupado['Promedio'].idxmax(), 'Mes']
        max_visitas = df_agrupado['Promedio'].max()
        label_visitas = f"{max_visitas:,.1f} promedio"
    else:
        mes_mas_visitado = df_agrupado.loc[df_agrupado['Visitas'].idxmax(), 'Mes']
        max_visitas = df_agrupado['Visitas'].max()
        label_visitas = f"{max_visitas:,.0f} visitas"
    st.markdown(f"""
    <div class="metric-card" style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);">
        <div class="metric-label">Mes con Más Visitas</div>
        <div class="metric-value">{mes_mas_visitado}</div>
        <div style="font-size: 0.9rem; opacity: 0.9;">{label_visitas}</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    if año_seleccionado == "Todos los años (Promedio)":
        promedio_mensual = df_agrupado['Promedio'].mean()
    else:
        promedio_mensual = df_agrupado['Visitas'].mean()
    st.markdown(f"""
    <div class="metric-card" style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);">
        <div class="metric-label">Promedio Mensual</div>
        <div class="metric-value">{promedio_mensual:,.1f}</div>
    </div>
    """, unsafe_allow_html=True)

st.divider()


st.subheader(titulo_grafico)

fig_barras = px.bar(
    df_agrupado,
    x='Mes',
    y='Visitas_Grafico',
    text='Visitas_Grafico',
    color='Visitas_Grafico',
    color_continuous_scale='Blues',
    labels={'Visitas_Grafico': 'Cantidad de Visitas', 'Mes': 'Mes del Año'}
)

fig_barras.update_traces(
    texttemplate='%{text:.1f}',
    textposition='outside',
    marker_line_color='rgb(8,48,107)',
    marker_line_width=1.5
)

fig_barras.update_layout(
    showlegend=False,
    height=500,
    xaxis_title="",
    yaxis_title="Cantidad de Visitas",
    font=dict(size=12),
    plot_bgcolor='rgba(0,0,0,0)',
    paper_bgcolor='rgba(0,0,0,0)',
    xaxis=dict(
        showgrid=False,
        tickangle=-45
    ),
    yaxis=dict(
        showgrid=True,
        gridcolor='rgba(128,128,128,0.2)'
    )
)

st.plotly_chart(fig_barras, use_container_width=True)


st.divider()
st.subheader("Tendencia Mensual")

fig_linea = go.Figure()

if año_seleccionado == "Todos los años (Promedio)":
    # Calcular mínimo y máximo por mes a través de los años
    df_min_max = df.groupby(['Mes', 'Año']).size().reset_index(name='Visitas')
    df_stats = df_min_max.groupby('Mes')['Visitas'].agg(['min', 'max']).reset_index()
    
    # Combinar con df_agrupado
    df_agrupado = df_agrupado.merge(df_stats, on='Mes', how='left')
    
    # Asegurar el orden correcto
    df_agrupado['Mes_num'] = df_agrupado['Mes'].apply(lambda x: meses_orden.index(x) + 1)
    df_agrupado = df_agrupado.sort_values('Mes_num')
    
    # Área sombreada para el rango (mínimo-máximo)
    fig_linea.add_trace(go.Scatter(
        x=df_agrupado['Mes'],
        y=df_agrupado['max'],
        mode='lines',
        name='Máximo',
        line=dict(color='rgba(102, 126, 234, 0.3)', width=0),
        showlegend=False,
        hoverinfo='skip'
    ))
    
    fig_linea.add_trace(go.Scatter(
        x=df_agrupado['Mes'],
        y=df_agrupado['min'],
        mode='lines',
        name='Mínimo',
        line=dict(color='rgba(102, 126, 234, 0.3)', width=0),
        fill='tonexty',
        fillcolor='rgba(102, 126, 234, 0.15)',
        showlegend=False,
        hoverinfo='skip'
    ))
    
    # Línea de promedio
    fig_linea.add_trace(go.Scatter(
        x=df_agrupado['Mes'],
        y=df_agrupado['Visitas_Grafico'],
        mode='lines+markers',
        name='Promedio',
        line=dict(color='#667eea', width=3),
        marker=dict(size=10, color='#764ba2', line=dict(width=2, color='white')),
        hovertemplate='<b>%{x}</b><br>Promedio: %{y:.1f}<extra></extra>'
    ))
    
    # Agregar líneas para máximo y mínimo con marcadores más pequeños
    fig_linea.add_trace(go.Scatter(
        x=df_agrupado['Mes'],
        y=df_agrupado['max'],
        mode='lines+markers',
        name='Máximo',
        line=dict(color='#ff6b6b', width=2, dash='dot'),
        marker=dict(size=6, color='#ff6b6b'),
        hovertemplate='<b>%{x}</b><br>Máximo: %{y:.0f}<extra></extra>'
    ))
    
    fig_linea.add_trace(go.Scatter(
        x=df_agrupado['Mes'],
        y=df_agrupado['min'],
        mode='lines+markers',
        name='Mínimo',
        line=dict(color='#51cf66', width=2, dash='dot'),
        marker=dict(size=6, color='#51cf66'),
        hovertemplate='<b>%{x}</b><br>Mínimo: %{y:.0f}<extra></extra>'
    ))
    
else:
    # Para un año específico, solo mostrar la línea simple sin relleno
    fig_linea.add_trace(go.Scatter(
        x=df_agrupado['Mes'],
        y=df_agrupado['Visitas_Grafico'],
        mode='lines+markers',
        name='Visitas',
        line=dict(color='#667eea', width=3),
        marker=dict(size=10, color='#764ba2', line=dict(width=2, color='white')),
        hovertemplate='<b>%{x}</b><br>Visitas: %{y:.0f}<extra></extra>'
    ))

fig_linea.update_layout(
    height=400,
    xaxis_title="",
    yaxis_title="Cantidad de Visitas",
    font=dict(size=12),
    plot_bgcolor='rgba(0,0,0,0)',
    paper_bgcolor='rgba(0,0,0,0)',
    showlegend=(año_seleccionado == "Todos los años (Promedio)"),
    legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="right",
        x=1
    ),
    xaxis=dict(
        showgrid=False,
        tickangle=-45
    ),
    yaxis=dict(
        showgrid=True,
        gridcolor='rgba(128,128,128,0.2)'
    )
)

st.plotly_chart(fig_linea, use_container_width=True)



st.divider()
if año_seleccionado == "Todos los años (Promedio)":
    st.subheader(f"Top 10 {nivel_territorial}s Más Visitados (Total Histórico)")
else:
    st.subheader(f"Top 10 {nivel_territorial}s Más Visitados")

if año_seleccionado == "Todos los años (Promedio)":
    df_territorio = df.groupby(nivel_territorial).size().reset_index(name='Visitas')
else:
    año_num = int(año_seleccionado)
    df_año = df[df['Año'] == año_num]
    df_territorio = df_año.groupby(nivel_territorial).size().reset_index(name='Visitas')

# Top 10
df_top10 = df_territorio.nlargest(10, 'Visitas').sort_values('Visitas', ascending=True)

fig_horizontal = px.bar(
    df_top10,
    x='Visitas',
    y=nivel_territorial,
    orientation='h',
    text='Visitas',
    color='Visitas',
    color_continuous_scale='Viridis',
    labels={'Visitas': 'Cantidad de Visitas', nivel_territorial: ''}
)

fig_horizontal.update_traces(
    texttemplate='%{text:.0f}',
    textposition='outside'
)

fig_horizontal.update_layout(
    showlegend=False,
    height=500,
    xaxis_title="Cantidad de Visitas",
    yaxis_title="",
    font=dict(size=11),
    plot_bgcolor='rgba(0,0,0,0)',
    paper_bgcolor='rgba(0,0,0,0)',
    xaxis=dict(
        showgrid=True,
        gridcolor='rgba(128,128,128,0.2)'
    ),
    yaxis=dict(
        showgrid=False
    )
)

st.plotly_chart(fig_horizontal, use_container_width=True)



st.divider()
with st.expander("Ver Datos Detallados por Mes"):
    if año_seleccionado == "Todos los años (Promedio)":
        df_tabla = df_agrupado[['Mes', 'Visitas', 'Promedio']].copy()
        df_tabla.columns = ['Mes', 'Total Histórico', 'Promedio por Año']
        df_tabla['Total Histórico'] = df_tabla['Total Histórico'].apply(lambda x: f"{x:,.0f}")
        df_tabla['Promedio por Año'] = df_tabla['Promedio por Año'].apply(lambda x: f"{x:,.1f}")
    else:
        df_tabla = df_agrupado[['Mes', 'Visitas']].copy()
        df_tabla['Visitas'] = df_tabla['Visitas'].apply(lambda x: f"{x:,.0f}")
    st.dataframe(df_tabla, use_container_width=True, hide_index=True)
