import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium

# Configuración de la página en modo ancho
st.set_page_config(page_title="Mapa de Intervenciones", layout="wide")
st.title("📍 Distribución Geográfica de Intervenciones (Camión Vactor)")

# Archivo base por defecto
ARCHIVO_PREDETERMINADO = "datos_vactor.csv"

# =========================================================================
# CONTROLADOR DE CARGA DE DATOS (Opcional en Barra Lateral)
# =========================================================================
st.sidebar.header("📁 Gestión de Datos")
archivo_cargado = st.sidebar.file_uploader(
    "Cargar un set de datos alternativo (Opcional)", 
    type=["csv"],
    help="El archivo debe mantener las columnas 'Coordenada X', 'Coordenada Y' y los sectores."
)

df = None

# Definir qué archivo leer
if archivo_cargado is not None:
    try:
        df = pd.read_csv(archivo_cargado)
        st.sidebar.success("¡Set de datos externo cargado con éxito!")
    except Exception as e:
        st.sidebar.error(f"Error al leer el archivo cargado: {e}")
else:
    try:
        df = pd.read_csv(ARCHIVO_PREDETERMINADO)
    except FileNotFoundError:
        st.error(f"No se encontró el archivo base '{ARCHIVO_PREDETERMINADO}' en el repositorio. Por favor, sube un archivo en la barra lateral.")
        st.stop()

# =========================================================================
# PROCESAMIENTO Y RENDERIZADO DEL MAPA
# =========================================================================
if df is not None:
    try:
        # 1. Limpieza crítica: Eliminar filas vacías en las coordenadas
        df = df.dropna(subset=['Coordenada X', 'Coordenada Y'])
        
        # 2. Conversión de comas a puntos para procesar decimales correctamente
        df['Coordenada X'] = df['Coordenada X'].astype(str).str.replace(',', '.').astype(float)
        df['Coordenada Y'] = df['Coordenada Y'].astype(str).str.replace(',', '.').astype(float)
        
        if df.empty:
            st.error("El set de datos seleccionado no contiene registros con coordenadas válidas.")
            st.stop()

        # Selector interactivo de criterio
        criterio = st.selectbox(
            "Selecciona el criterio para clasificar los puntos en el mapa:",
            ["Unidad Vecinal", "Macrosector", "Microsector"]
        )

        # Paleta de colores de Folium
        colores_disponibles = [
            "red", "blue", "green", "purple", "orange", "darkred", "cadetblue", 
            "darkpurple", "pink", "darkblue", "darkgreen"
        ]

        categorias_unicas = df[criterio].dropna().unique()
        diccionario_colores = {}
        for i, cat in enumerate(categorias_unicas):
            diccionario_colores[cat] = colores_disponibles[i % len(colores_disponibles)]

        # Mapa base original de ArcGIS Online
        mapa = folium.Map(
            location=[-38.745, -72.615], 
            zoom_start=12, 
            tiles="https://server.arcgisonline.com/ArcGIS/rest/services/World_Topo_Map/MapServer/tile/{z}/{y}/{x}",
            attr="Esri / ArcGIS Online"
        )

        # Muestra el total de registros detectados en la interfaz
        st.caption(f"Visualizando un extracto optimizado de las {len(df)} intervenciones detectadas.")

        # Limitamos el renderizado a los primeros 2500 puntos para cuidar el rendimiento de la app si subes un archivo gigante
        df_render = df.head(2500)

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

        # Desplegar mapa de ArcGIS
        st_folium(mapa, width="100%", height=650)

        # =========================================================================
        # LEYENDA DINÁMICA (Soporta Modo Claro y Oscuro de forma nativa)
        # =========================================================================
        st.markdown("### 📊 Leyenda de Sectores Detectados")
        cols = st.columns(3)
        
        mapa_colores_st = {
            "red": "red", "blue": "blue", "green": "green", 
            "purple": "violet", "orange": "orange", "darkred": "red", 
            "cadetblue": "blue", "darkpurple": "violet", "pink": "rainbow", 
            "darkblue": "blue", "darkgreen": "green", "gray": "gray"
        }
        
        for i, (cat, col) in enumerate(diccionario_colores.items()):
            color_markdown = mapa_colores_st.get(col, "gray")
            with cols[i % 3]:
                st.markdown(f"**:{color_markdown}[●] {cat}**")

    except Exception as e:
        st.error(f"Ocurrió un error al procesar el archivo: {e}")
