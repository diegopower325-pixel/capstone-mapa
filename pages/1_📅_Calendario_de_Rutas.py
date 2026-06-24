
import streamlit as st
import calendar
import pandas as pd


st.markdown("""
<style>
.ruta-header {
    text-align: center;
    margin-bottom: 2rem;
}
.ruta-header h1 {
    font-size: 2.2rem;
    font-weight: 800;
    color:  #ffffff;
    margin: 0.5rem 0 0.2rem 0;
}
.ruta-header p {
    color: #ffffff;
    font-size: 1.1rem;
    margin: 0;
}
.semana-card {
    border-radius: 16px;
    padding: 1.4rem 1.6rem;
    background: white;
    box-shadow: 0 2px 12px rgba(0,0,0,0.08);
    margin-bottom: 1.2rem;
    border-left: 6px solid;
    min-height: 220px;
}
.card-header {
    display: flex;
    align-items: center;
    gap: 1rem;
    margin-bottom: 1rem;
    padding-bottom: 0.8rem;
    border-bottom: 1px solid #f0f0f0;
}
.cal-icon {
    width: 52px;
    height: 52px;
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.6rem;
    flex-shrink: 0;
}
.card-title {
    font-size: 1.25rem;
    font-weight: 700;
    margin: 0;
    line-height: 1.2;
}
.lugar-item {
    display: flex;
    align-items: center;
    gap: 0.6rem;
    padding: 0.3rem 0;
    font-size: 0.92rem;
    color: #374151;
}
.lugar-dot {
    width: 10px;
    height: 10px;
    border-radius: 50%;
    flex-shrink: 0;
}
.holgura-box {
    border-radius: 12px;
    padding: 1rem 1.5rem;
    margin-top: 1rem;
    display: flex;
    align-items: center;
    gap: 1rem;
    background: #fffbeb;
    border: 1px solid #f59e0b;
    color: #92400e;
    font-size: 0.95rem;
}
.aviso-box {
    border-radius: 12px;
    padding: 1rem 1.5rem;
    margin-top: 1rem;
    background: #f0fdf4;
    border: 1px solid #16a34a;
    color: #166534;
    font-size: 0.95rem;
}
.sin-datos {
    color: #9ca3af;
    font-style: italic;
    font-size: 0.9rem;
    padding: 0.5rem 0;
}
</style>
""", unsafe_allow_html=True)



df_valido = st.session_state['df']
TOTAL_AÑOS = 8  # 2018 a 2025


def generar_calendario(df_valido, mes_num, columna_sector):
    """
    Genera el diccionario de 4 semanas con los sectores asignados,
    filtrado por mes y columna (Microsector o Macrosector).
    Retorna: dict {1: [...], 2: [...], 3: [...], 4: [...]}
    Cada elemento es una tupla (nombre_sector, porcentaje).
    """
    df_mes = df_valido[df_valido['Mes_num'] == mes_num].copy()

    # Agrupar y contar años distintos por sector
    frecuencia = df_mes.groupby(columna_sector)['Año'].nunique().reset_index()
    frecuencia.columns = ['Sector', 'Años_presentes']

    # Solo sectores con incidencia en 2 o más años
    frecuencia = frecuencia[frecuencia['Años_presentes'] >= 2]

    if frecuencia.empty:
        return {i: [] for i in range(1, 5)}

    frecuencia['Porcentaje'] = (frecuencia['Años_presentes'] / TOTAL_AÑOS) * 100
    frecuencia = frecuencia.sort_values(by='Porcentaje', ascending=False).reset_index(drop=True)

    # Distribuir en 4 semanas de forma round-robin
    calendario = {i: [] for i in range(1, 5)}
    for idx, row in frecuencia.iterrows():
        semana = (idx % 4) + 1
        calendario[semana].append((row['Sector'], row['Porcentaje']))

    return calendario


st.sidebar.header("Filtros del Tablero")

meses = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
         "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
mes_seleccionado = st.sidebar.selectbox("Seleccione el Mes:", meses, index=4)
mes_num = meses.index(mes_seleccionado) + 1

nivel_territorial = st.sidebar.selectbox(
    "Nivel Territorial:",
    ["Microsector", "Macrosector","Unidad Vecinal"]
)


st.sidebar.divider()
st.sidebar.info("""
💡 **¿Cómo se genera el calendario?**

El sistema analiza el historial de intervenciones del camión Vactor entre **2018 y 2025** (8 años) y para el mes seleccionado:

1. **Cuenta** en cuántos años distintos cada sector requirió atención.
2. **Filtra** los sectores con incidencia en **2 o más años** (descarta casos aislados).
3. **Ordena** de mayor a menor frecuencia histórica.
4. **Distribuye** los sectores en las 4 semanas de forma rotativa: el más frecuente va a la Semana 1, el segundo a la Semana 2, y así sucesivamente.

**¿Qué significa el porcentaje?**
Indica en qué proporción de los 8 años históricos ese sector requirió intervención en este mes. Por ejemplo, un **75%** significa que en 6 de los 8 años registrados, ese sector necesitó mantención durante el mes seleccionado.
""")


calendario = generar_calendario(df_valido, mes_num, nivel_territorial)



st.markdown(f"""
<div class="ruta-header">
    <h1>🗺️ Ruta de Trabajo</h1>
    <p>{mes_seleccionado} &nbsp;·&nbsp; {nivel_territorial}</p>
</div>
""", unsafe_allow_html=True)



colores = [
    {"borde": "#1e3a5f", "fondo_icon": "#1e3a5f", "bullet": "#1e3a5f", "titulo": "#1e3a5f"},
    {"borde": "#0d9488", "fondo_icon": "#0d9488", "bullet": "#0d9488", "titulo": "#0d9488"},
    {"borde": "#16a34a", "fondo_icon": "#16a34a", "bullet": "#16a34a", "titulo": "#16a34a"},
    {"borde": "#ea580c", "fondo_icon": "#ea580c", "bullet": "#ea580c", "titulo": "#ea580c"},
]

fechas_semanas = [
    f"01 al 07 de {mes_seleccionado}",
    f"08 al 14 de {mes_seleccionado}",
    f"15 al 21 de {mes_seleccionado}",
    f"22 al 28 de {mes_seleccionado}",
]

fila1_col1, fila1_col2 = st.columns(2)
fila2_col1, fila2_col2 = st.columns(2)
columnas_grid = [fila1_col1, fila1_col2, fila2_col1, fila2_col2]

for i, col in enumerate(columnas_grid):
    c = colores[i]
    sectores_semana = calendario[i + 1]

    if sectores_semana:
        lugares_html = "".join([
            f"""<div class="lugar-item">
                  <div class="lugar-dot" style="background:{c['bullet']};"></div>
                  <span><b>{sector}</b> &nbsp;<span style="color:#9ca3af;font-size:0.82rem;">({pct:.0f}% años)</span></span>
                </div>"""
            for sector, pct in sectores_semana
        ])
    else:
        lugares_html = '<div class="sin-datos">Sin sectores prioritarios para este mes.</div>'

    card_html = f"""
    <div class="semana-card" style="border-left-color: {c['borde']};">
        <div class="card-header">
            <div class="cal-icon" style="background:{c['fondo_icon']}; color:white;">
                📅
            </div>
            <p class="card-title" style="color:{c['titulo']};">
                {fechas_semanas[i]}
            </p>
        </div>
        {lugares_html}
    </div>
    """
    with col:
        st.markdown(card_html, unsafe_allow_html=True)



st.divider()
dias_del_mes = calendar.monthrange(2026, mes_num)[1]

if dias_del_mes > 28:
    st.markdown(f"""
    <div class="holgura-box">
        <span style="font-size:1.5rem;"></span>
        <div>
            <strong>DÍAS DE HOLGURA: Del 29 al {dias_del_mes} de {mes_seleccionado}</strong><br>
            Reserva logística para atención de emergencias reactivas, retrasos climáticos y mantenimiento preventivo del camión Vactor.
        </div>
    </div>
    """, unsafe_allow_html=True)
else:
    st.markdown(f"""
    <div class="aviso-box">
         <strong>{mes_seleccionado}</strong> tiene exactamente 28 días. No hay días de holgura este mes.
    </div>
    """, unsafe_allow_html=True)