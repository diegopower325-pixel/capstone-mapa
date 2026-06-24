import streamlit as st
import pandas as pd
from PIL import Image

# ─────────────────────────────────────────────
# 1. CONFIGURACIÓN GLOBAL
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Tablero Vactor Temuco",
    page_icon="🚜",
    layout="wide"
)

# ─────────────────────────────────────────────
# 2. CSS PERSONALIZADO
# ─────────────────────────────────────────────
st.markdown("""
<style>
/* Ajuste general */
.block-container {
    padding-top: 1.5rem;
    padding-bottom: 2rem;
}

/* Estadísticas */
.stat-card {
    background: white;
    border-radius: 18px;
    padding: 1.4rem;
    text-align: center;
    box-shadow: 0 6px 18px rgba(0,0,0,0.08);
    border: 1px solid #e5e7eb;
}

.stat-number {
    font-size: 2rem;
    font-weight: 850;
    color: #003B73;
    margin-bottom: 0.2rem;
}

.stat-label {
    font-size: 0.95rem;
    color: #6b7280;
}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# 3. CARGAR DATOS
# ─────────────────────────────────────────────
@st.cache_data
def cargar_datos():
    df = pd.read_csv("datos_vactor.csv")
    df["Fecha_datetime"] = pd.to_datetime(df["Fecha_datetime"], errors="coerce")
    df = df.dropna(subset=["Fecha_datetime"])
    df["Año"] = df["Fecha_datetime"].dt.year
    df["Mes_num"] = df["Fecha_datetime"].dt.month
    df = df[(df["Año"] >= 2018) & (df["Año"] <= 2025)].copy()
    return df

if "df" not in st.session_state:
    st.session_state["df"] = cargar_datos()

df = st.session_state["df"]

total_intervenciones = len(df)
total_sectores = df["Microsector"].nunique()
años_analisis = f"{df['Año'].min()} - {df['Año'].max()}"

total_intervenciones_txt = f"{total_intervenciones:,}".replace(",", ".")
total_sectores_txt = f"{total_sectores:,}".replace(",", ".")

# ─────────────────────────────────────────────
# 4. LOGOS SUPERIORES
# ─────────────────────────────────────────────
col_logo1, col_centro, col_logo2 = st.columns([1.2, 0.3, 4])

with col_logo1:
    try:
        st.image("TemuLAB.jpg", width=115)
    except:
        st.markdown("### TemuLAB")

with col_logo2:
    try:
        st.image("ufro.webp", width=430)
    except:
        st.markdown("### Universidad de La Frontera")


# ─────────────────────────────────────────────
# 5. PORTADA PRINCIPAL
# ─────────────────────────────────────────────
st.markdown("")
st.markdown("#### Sistema de análisis territorial y mantenimiento preventivo")
st.title("Tablero de Planificación Preventiva Camión Vactor")
st.markdown("**Herramienta de apoyo para la planificación de rutas preventivas en la comuna de Temuco**")
st.markdown("")
st.markdown("---")

# ─────────────────────────────────────────────
# 6. ESTADÍSTICAS PRINCIPALES
# ─────────────────────────────────────────────
col_stat1, col_stat2, col_stat3 = st.columns(3)

with col_stat1:
    st.markdown(f"""
    <div class="stat-card">
        <div class="stat-number">{total_intervenciones_txt}</div>
        <div class="stat-label">Intervenciones analizadas</div>
    </div>
    """, unsafe_allow_html=True)

with col_stat2:
    st.markdown(f"""
    <div class="stat-card">
        <div class="stat-number">{total_sectores_txt}</div>
        <div class="stat-label">Sectores registrados</div>
    </div>
    """, unsafe_allow_html=True)

with col_stat3:
    st.markdown(f"""
    <div class="stat-card">
        <div class="stat-number">{años_analisis}</div>
        <div class="stat-label">Período histórico</div>
    </div>
    """, unsafe_allow_html=True)

# ─────────────────────────────────────────────
# 7. TARJETAS DE FUNCIONALIDADES
# ─────────────────────────────────────────────
st.markdown("### Funcionalidades del Sistema")
st.markdown("")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("#### Calendario de Rutas")
    st.markdown("""
    Planificación semanal de intervenciones preventivas por microsector, 
    macrosector o unidad vecinal, utilizando información histórica del período 2018-2025.
    """)

with col2:
    st.markdown("#### Análisis Estadístico")
    st.markdown("""
    Visualización de tendencias, frecuencias, distribución territorial y comportamiento 
    histórico de las intervenciones realizadas por el camión Vactor.
    """)

with col3:
    st.markdown("#### Registro de Intervenciones")
    st.markdown("""
    Sistema de ingreso de datos para nuevas intervenciones del camión Vactor. 
    Permite registrar y almacenar información detallada de cada operación realizada 
    para mantener un historial completo y actualizado.
    """)

# ─────────────────────────────────────────────
# 8. INSTRUCCIONES
# ─────────────────────────────────────────────
st.markdown("---")
st.markdown("### Cómo usar el sistema")

st.info("""
**Paso 1:** Selecciona una sección desde el menú lateral izquierdo.

**Paso 2:** Utiliza los filtros disponibles para ajustar la consulta por mes, año o nivel territorial.

**Paso 3:** Revisa las tablas, gráficos y calendario generados por el sistema.

**Paso 4:** Registra nuevas intervenciones usando el formulario de ingreso de datos.
""")

# ─────────────────────────────────────────────
# 9. FOOTER
# ─────────────────────────────────────────────
st.markdown("---")
st.markdown("")
st.markdown("""
<div style="text-align: center; color: #6b7280; padding: 1rem;">
<strong>Sistema desarrollado por:</strong> Universidad de La Frontera · TemuLAB · Municipalidad de Temuco<br>
Mantenimiento preventivo basado en análisis de datos históricos 2018-2025
</div>
""", unsafe_allow_html=True)
