import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium

# 1. Configuración de la página en modo ancho para que el mapa se vea gigante
st.set_page_config(page_title="Mapa de Intervenciones", layout="wide")
st.title("📍 Distribución Geográfica de Intervenciones (Camión Vactor)")
st.write("Visualización interactiva con mapas base de ArcGIS Online para la comuna de Temuco.")

# Nombre exacto de tu archivo del repositorio
ARCHIVO_DATOS = "datos_vactor.csv"

try:
    # 2. Cargar datos asegurando que no se alteren los decimales
    df = pd.read_csv(ARCHIVO_DATOS)
    
    # 3. Limpieza crítica: Filtrar y eliminar filas donde las coordenadas vengan vacías
    df = df.dropna(subset=['Coordenada X', 'Coordenada Y'])
    
    if df.empty:
        st.error("El archivo CSV no contiene registros con coordenadas válidas.")
        st.stop()

    # 4. Selector interactivo con los nombres exactos de tus columnas de clasificación
    criterio = st.selectbox(
        "Selecciona el criterio para clasificar los puntos en el mapa:",
        ["Unidad Vecinal", "Macrosector", "Microsector"]
    )

    # 5. Paleta de colores para pintar los puntos de forma dinámica estilo QGIS
    colores_disponibles = [
        "red", "blue", "green", "purple", "orange", "darkred", "cadetblue", 
        "darkpurple", "pink", "darkblue", "darkgreen"
    ]

    # Obtener las categorías únicas de la columna seleccionada (ej: ESTADIO, ACCESO NORTE, etc.)
    categorias_unicas = df[criterio].dropna().unique()
    diccionario_colores = {}
    for i, cat in enumerate(categorias_unicas):
        diccionario_colores[cat] = colores_disponibles[i % len(colores_disponibles)]

    # 6. Crear el mapa base centrado en Temuco consumiendo el Servidor Oficial de ArcGIS
    mapa = folium.Map(
        location=[-38.745, -72.615], 
        zoom_start=12, 
        tiles="https://server.arcgisonline.com/ArcGIS/rest/services/World_Topo_Map/MapServer/tile/{z}/{y}/{x}",
        attr="Esri / ArcGIS Online"
    )

    # 7. Dibujar los marcadores en el mapa uno a uno
    for index, fila in df.iterrows():
        lat = float(fila['Coordenada Y'])
        lon = float(fila['Coordenada X'])
        
        categoria_actual = fila[criterio]
        
        # Asignar color según la categoría (gris si está vacío)
        color_punto = diccionario_colores.get(categoria_actual, "gray")
            
        # Crear etiqueta flotante para cuando pinchen el círculo
        info_popup = f"""
        <b>Dirección:</b> {fila.get('Dirección de la Orden de Trabajo de Workforce', 'No registrada')}<br>
        <b>Unidad Vecinal:</b> {fila.get('Unidad Vecinal', 'N/A')}<br>
        <b>Macrosector:</b> {fila.get('Macrosector', 'N/A')}<br>
        <b>Microsector:</b> {fila.get('Microsector', 'N/A')}<br>
        <b>Coordenadas:</b> {lat}, {lon}
        """
        
        # Añadir marcadores circulares limpios para que no se amontonen
        folium.CircleMarker(
            location=[lat, lon],
            radius=6,
            popup=folium.Popup(info_popup, max_width=300),
            color=color_punto,
            fill=True,
            fill_color=color_punto,
            fill_opacity=0.7
        ).add_to(mapa)

    # 8. Renderizar el mapa en la aplicación de Streamlit
    st_folium(mapa, width="100%", height=650)

    # 9. Mostrar la leyenda dinámica ordenadamente en 3 columnas abajo del mapa
    st.markdown("### 📊 Leyenda de Sectores Detectados")
    cols = st.columns(3)
    for i, (cat, col) in enumerate(diccionario_colores.items()):
        with cols[i % 3]:
            st.markdown(f"🟢 **{cat}**")

except FileNotFoundError:
    st.error(f"No se pudo encontrar el archivo '{ARCHIVO_DATOS}' en la raíz del proyecto.")
except Exception as e:
    st.error(f"Ocurrió un error inesperado al procesar el mapa: {e}")
