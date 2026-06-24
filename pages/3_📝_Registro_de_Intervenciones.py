import streamlit as st
import pandas as pd
from datetime import datetime, date
import os


st.markdown("""
<style>
.block-container {
    padding-top: 1.5rem;
    padding-bottom: 2rem;
}
</style>
""", unsafe_allow_html=True)


df = st.session_state['df']



# Crear diccionario de direcciones con sus coordenadas
direcciones_coords = {}
for _, row in df.iterrows():
    direccion = row['Dirección de la Orden de Trabajo de Workforce']
    if pd.notna(direccion) and pd.notna(row['Coordenada X']) and pd.notna(row['Coordenada Y']):
        if direccion not in direcciones_coords:
            direcciones_coords[direccion] = {
                'coord_x': row['Coordenada X'],
                'coord_y': row['Coordenada Y']
            }

# Obtener valores únicos para listas desplegables
direcciones_unicas = sorted(list(direcciones_coords.keys()))
macrosectores_unicos = sorted(df['Macrosector'].dropna().unique().tolist())
unidades_vecinales_unicas = sorted(df['Unidad Vecinal'].dropna().unique().tolist())
microsectores_unicos = sorted(df['Microsector'].dropna().unique().tolist())

# Calcular rangos máximos para variables numéricas
max_km_inicio = int(df['Km Inicio'].max()) if not df['Km Inicio'].isna().all() else 10000
max_km_termino = int(df['Km Termino'].max()) if not df['Km Termino'].isna().all() else 10000
max_rejillas = int(df['N° Rejillas'].max()) if not df['N° Rejillas'].isna().all() else 10
max_camaras = int(df['N° Cámaras'].max()) if not df['N° Cámaras'].isna().all() else 10
max_ductos = int(df['N° Ductos'].max()) if not df['N° Ductos'].isna().all() else 10
max_cargas_agua = int(df['N° de cargas de agua'].max()) if not df['N° de cargas de agua'].isna().all() else 10
max_capacidad_agua = int(df['Capacidad de agua estanque (Lt)'].max()) if not df['Capacidad de agua estanque (Lt)'].isna().all() else 10000
max_agua_utilizada = int(df['Total de agua utilizada (Lt)'].max()) if not df['Total de agua utilizada (Lt)'].isna().all() else 50000
max_descargas = int(df['N° de descargas de sedimentos'].max()) if not df['N° de descargas de sedimentos'].isna().all() else 10
max_sedimentos = int(df['Cantidad total de sedimentos (Lt)'].max()) if not df['Cantidad total de sedimentos (Lt)'].isna().all() else 50000

# Rangos de coordenadas (con más precisión)
min_coord_x = float(df['Coordenada X'].min()) if not df['Coordenada X'].isna().all() else -73.0
max_coord_x = float(df['Coordenada X'].max()) if not df['Coordenada X'].isna().all() else -72.0
min_coord_y = float(df['Coordenada Y'].min()) if not df['Coordenada Y'].isna().all() else -39.0
max_coord_y = float(df['Coordenada Y'].max()) if not df['Coordenada Y'].isna().all() else -38.0


st.title("Registro de Intervenciones")
st.markdown("**Sistema de ingreso de datos para nuevas intervenciones del Camión Vactor**")
st.markdown("")

st.info("Complete todos los campos del formulario. Los valores se calculan automáticamente según el historial de intervenciones.")
st.markdown("---")



with st.form("formulario_intervencion", clear_on_submit=True):
    
    # SECCIÓN 1: FECHAS
    st.markdown("#### Fechas")
    
    col1, col2 = st.columns(2)
    with col1:
        fecha_reclamo = st.date_input("Fecha del Reclamo", value=date.today())
    with col2:
        fecha_intervencion = st.date_input("Fecha de la Intervención", value=date.today())
    
    st.markdown("")
    
    
    # SECCIÓN 2: UBICACIÓN E IDENTIFICACIÓN
    st.markdown("#### Ubicación e Identificación")
    
    direccion = st.selectbox(
        "Dirección de la Intervención",
        options=["Seleccione una dirección..."] + direcciones_unicas + ["Otra (nueva dirección)"]
    )
    
    if direccion == "Otra (nueva dirección)":
        direccion_nueva = st.text_input("Ingrese la nueva dirección")
        direccion_final = direccion_nueva
    elif direccion != "Seleccione una dirección...":
        direccion_final = direccion
    else:
        direccion_final = None
    
    # SECCIÓN 3: UBICACIÓN GEOGRÁFICA
    st.markdown("#### Sectores")
    
    col1, col2 = st.columns(2)
    with col1:
        macrosector = st.selectbox("Macrosector", options=["Seleccione..."] + macrosectores_unicos)
        microsector = st.selectbox("Microsector", options=["Seleccione..."] + microsectores_unicos)
    
    with col2:
        unidad_vecinal = st.selectbox("Unidad Vecinal", options=["Seleccione..."] + unidades_vecinales_unicas)
    
    st.markdown("")
    
    
    # SECCIÓN 4: DATOS DEL VEHÍCULO
    st.markdown("#### Datos del Vehículo")
    
    col1, col2 = st.columns(2)
    with col1:
        km_inicio = st.selectbox("Km Inicio", options=list(range(0, max_km_inicio + 1000, 10)))
    with col2:
        km_termino = st.selectbox("Km Término", options=list(range(0, max_km_termino + 1000, 10)))
    
    st.markdown("")
    
    
    # SECCIÓN 5: TRABAJO REALIZADO
    st.markdown("#### Trabajo Realizado")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        num_rejillas = st.selectbox("N° de Rejillas Limpiadas", options=list(range(0, max_rejillas + 5)))
        num_camaras = st.selectbox("N° de Cámaras Limpiadas", options=list(range(0, max_camaras + 5)))
    
    with col2:
        num_ductos = st.selectbox("N° de Ductos Limpiados", options=list(range(0, max_ductos + 5)))
        num_cargas = st.selectbox("N° de Cargas de Agua", options=list(range(0, max_cargas_agua + 5)))
    
    with col3:
        capacidad_estanque = st.selectbox("Capacidad Estanque (Lt)", options=list(range(0, max_capacidad_agua + 1000, 500)))
        agua_utilizada = st.selectbox("Total Agua Utilizada (Lt)", options=list(range(0, max_agua_utilizada + 5000, 500)))
    
    st.markdown("")
    
    
    # SECCIÓN 6: SEDIMENTOS
    st.markdown("#### Gestión de Sedimentos")
    
    col1, col2 = st.columns(2)
    with col1:
        num_descargas = st.selectbox("N° de Descargas de Sedimentos", options=list(range(0, max_descargas + 5)))
    with col2:
        cantidad_sedimentos = st.selectbox("Cantidad Total de Sedimentos (Lt)", options=list(range(0, max_sedimentos + 5000, 500)))
    
    st.markdown("")
    
    
    # SECCIÓN 7: NOTAS ADICIONALES
    st.markdown("#### Observaciones")
    
    notas = st.text_area(
        "Notas u Observaciones de la Intervención",
        placeholder="Ingrese cualquier observación relevante sobre la intervención (opcional)...",
        height=100
    )
    
    
    # BOTÓN DE ENVÍO
    st.markdown("")
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        submitted = st.form_submit_button("Guardar Intervención", use_container_width=True)

if submitted:
    # Validar campos obligatorios
    if not direccion_final or macrosector == "Seleccione..." or microsector == "Seleccione..." or unidad_vecinal == "Seleccione...":
        st.error("Por favor complete todos los campos obligatorios (Dirección, Macrosector, Microsector, Unidad Vecinal)")
    else:
        # Calcular diferencia de km
        diferencia_km = km_termino - km_inicio
        
        # Obtener coordenadas automáticamente de la base de datos (no se guardan en el CSV)
        if direccion_final in direcciones_coords:
            coord_x = direcciones_coords[direccion_final]['coord_x']
            coord_y = direcciones_coords[direccion_final]['coord_y']
        else:
            # Si es una dirección nueva, usar valores por defecto (centro aproximado)
            coord_x = (min_coord_x + max_coord_x) / 2
            coord_y = (min_coord_y + max_coord_y) / 2
        
        # Obtener mes y año de la fecha
        mes_nombre = fecha_intervencion.strftime("%B")
        meses_es = {
            "January": "Enero", "February": "Febrero", "March": "Marzo",
            "April": "Abril", "May": "Mayo", "June": "Junio",
            "July": "Julio", "August": "Agosto", "September": "Septiembre",
            "October": "Octubre", "November": "Noviembre", "December": "Diciembre"
        }
        mes_final = meses_es.get(mes_nombre, mes_nombre)
        
        # Crear diccionario con los datos (SIN Fecha_datetime, Coordenada X, Coordenada Y)
        nueva_intervencion = {
            "Fecha Reclamo": fecha_reclamo.strftime("%Y-%m-%d"),
            "Fecha Intervención": fecha_intervencion.strftime("%Y-%m-%d"),
            "Dirección de la Orden de Trabajo de Workforce": direccion_final,
            "Km Inicio": km_inicio,
            "Km Termino": km_termino,
            "Diferencia Km": diferencia_km,
            "N° Rejillas": num_rejillas,
            "N° Cámaras": num_camaras,
            "N° Ductos": num_ductos,
            "N° de cargas de agua": num_cargas,
            "Capacidad de agua estanque (Lt)": capacidad_estanque,
            "Total de agua utilizada (Lt)": agua_utilizada,
            "N° de descargas de sedimentos": num_descargas,
            "Cantidad total de sedimentos (Lt)": cantidad_sedimentos,
            "Macrosector": macrosector,
            "Unidad Vecinal": unidad_vecinal,
            "Microsector": microsector,
            "Mes": mes_final,
            "Notas": notas
        }
        
        # Crear DataFrame con la nueva intervención
        df_nuevo = pd.DataFrame([nueva_intervencion])
        
        # Ruta del archivo CSV de nuevas intervenciones
        archivo_nuevas = "intervenciones_registradas.csv"
        
        # Guardar en CSV
        if os.path.exists(archivo_nuevas):
            # Si existe, agregar al final
            df_existente = pd.read_csv(archivo_nuevas)
            df_final = pd.concat([df_existente, df_nuevo], ignore_index=True)
            df_final.to_csv(archivo_nuevas, index=False)
        else:
            # Si no existe, crear nuevo
            df_nuevo.to_csv(archivo_nuevas, index=False)
        
        # Mensaje de éxito
        st.success("Intervención registrada exitosamente")
        st.info(f"Los datos se han guardado en: **{archivo_nuevas}**")
        


st.markdown("---")
st.markdown("### Historial de Intervenciones Registradas")

archivo_nuevas = "intervenciones_registradas.csv"
if os.path.exists(archivo_nuevas):
    df_registradas = pd.read_csv(archivo_nuevas)
    st.info(f"Total de intervenciones registradas: **{len(df_registradas)}**")
    
    # Mostrar últimas 10 intervenciones
    st.dataframe(
        df_registradas[['Fecha Reclamo', 'Fecha Intervención', 'Dirección de la Orden de Trabajo de Workforce', 
                        'Macrosector', 'Microsector', 'N° Rejillas', 'N° Cámaras', 'N° Ductos']].tail(10),
        use_container_width=True,
        hide_index=True
    )
    
    # Botón para descargar
    csv_download = df_registradas.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="Descargar Todas las Intervenciones (CSV)",
        data=csv_download,
        file_name="intervenciones_registradas.csv",
        mime="text/csv"
    )
else:
    st.info("No hay intervenciones registradas aún. Complete el formulario para agregar la primera.")
