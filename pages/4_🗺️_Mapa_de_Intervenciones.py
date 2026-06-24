import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium

# Configuración de la página en modo ancho
st.set_page_config(page_title="Mapa de Intervenciones", layout="wide")
st.title("📍 Distribución Geográfica de Intervenciones (Camión Vactor)")
st.write("Visualización interactiva con mapas base de ArcGIS Online para la comuna de Temuco.")

# Nombre exacto de tu archivo en la raíz del repositorio
ARCHIVO_DATOS = "datos_vactor.csv"

try:
    # 1. Cargar datos desde el CSV
    df = pd.read_csv(ARCHIVO_DATOS)
    
    # 2. Limpieza crítica: Eliminar filas donde las coordenadas vengan vacías por completo
    df = df.dropna(subset=['Coordenada X', 'Coordenada Y'])
    
    # 3. Conversión de comas a puntos para procesar las coordenadas correctamente
    df['Coordenada X'] = df['Coordenada X'].astype(str).str.replace(',', '.').astype(float)
    df['Coordenada Y'] = df['Coordenada Y'].astype(str).str.replace(',', '.').astype(float)
    
    if df.empty:
        st.error("El archivo CSV no contiene registros con coordenadas válidas.")
        st.stop()

    # Selector interactivo con los nombres de clasificación del CSV
    criterio = st.selectbox(
        "Selecciona el criterio para clasificar los puntos en el mapa:",
        ["Unidad Vecinal", "Macrosector", "Microsector"]
    )

    # Paleta de colores para pintar los puntos de forma dinámica
    colores_disponibles = [
        "red", "blue", "green", "purple", "orange", "darkred", "cadetblue", 
        "darkpurple", "pink", "darkblue", "darkgreen"
    ]

    # Obtener las categorías únicas de la columna seleccionada
    categorias_unicas = df[criterio].dropna().unique()
    diccionario_colores = {}
    for i, cat in enumerate(categorias_unicas):
        diccionario_colores[cat] = colores_disponibles[i % len(colores_disponibles)]

    # Crear el mapa base centrado en Temuco consumiendo el Servidor de ArcGIS
    mapa = folium.Map(
        location=[-38.745, -72.615], 
        zoom_start=12, 
        tiles="https://server.arcgisonline.com/ArcGIS/rest/services/World_Topo_Map/MapServer/tile/{z}/{y}/{x}",
        attr="Esri / ArcGIS Online"
    )

    # Dibujar marcadores circulares limpios limitando a las primeras 1200 filas para agilizar
    df_render = df.head(1200)

    for index, fila in df_render.iterrows():
        try:
            lat = float(fila['Coordenada Y'])
            lon = float(fila['Coordenada X'])
            
            categoria_actual = fila[criterio]
            color_punto = diccionario_colores.get(categoria_actual, "gray")
                
            info_popup = f"""
            <b>Dirección:</b> {fila.get('Dirección de la Orden de Trabajo de Workforce', 'No registrada')}<br>
            <b>Unidad Vecinal:</b> {fila.get('Unidad Vecinal', 'N/A')}<br>
            <b>Macrosector:</b> {fila.get('Macrosector', 'N/A')}<br>
            <b>Microsector:</b> {fila.get('Microsector', 'N/A')}<br>
            <b>Coordenadas:</b> {lat}, {lon}
            """
            
            folium.CircleMarker(
                location=[lat, lon],
                radius=5,
                popup=folium.Popup(info_popup, max_width=250),
                color=color_punto,
                fill=True,
                fill_color=color_punto,
                fill_opacity=0.7
            ).add_to(mapa)
        except:
            continue

    # Renderizar el mapa en la app de Streamlit
    st_folium(mapa, width="100%", height=650)

    # Mostrar la leyenda dinámica ordenadamente abajo
    st.markdown("### 📊 Leyenda de Sectores Detectados")
    cols = st.columns(3)
    for i, (cat, col) in enumerate(diccionario_colores.items()):
        with cols[i % 3]:
            st.markdown(f"🟢 **{cat}**")

except FileNotFoundError:
    st.error(f"No se pudo encontrar el archivo '{ARCHIVO_DATOS}' en la raíz del proyecto.")
except Exception as e:
    st.error(f"Ocurrió un error al procesar el mapa: {e}")
