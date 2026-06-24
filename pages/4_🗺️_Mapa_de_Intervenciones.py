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
# 1. CONTROLADOR DE CARGA DE DATOS (Barra Lateral)
# =========================================================================
st.sidebar.header("📁 Gestión de Datos")
archivo_cargado = st.sidebar.file_uploader(
    "Cargar un set de datos alternativo (Opcional)", 
    type=["csv"],
    help="El archivo debe mantener las columnas 'Coordenada X', 'Coordenada Y' y los sectores."
)

# Inicializar el DataFrame vacío
df = pd.DataFrame()

# Cargar el archivo correspondiente
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

# =========================================================================
# 2. CREACIÓN FIJA DEL MAPA BASE (ArcGIS)
# =========================================================================
mapa = folium.Map(
    location=[-38.745, -72.615], 
    zoom_start=12, 
    tiles="https://server.arcgisonline.com/ArcGIS/rest/services/World_Topo_Map/MapServer/tile/{z}/{y}/{x}",
    attr="Esri / ArcGIS Online"
)

# =========================================================================
# 3. PROCESAMIENTO DE PUNTOS (Si hay datos disponibles)
# =========================================================================
diccionario_colores = {}

if df is not None and not df.empty:
    try:
        # Limpieza crítica de coordenadas
        df = df.dropna(subset=['Coordenada X', 'Coordenada Y'])
        df['Coordenada X'] = df['Coordenada X'].astype(str).str.replace(',', '.').astype(float)
        df['Coordenada Y'] = df['Coordenada Y'].astype(str).str.replace(',', '.').astype(float)
        
        # Selector interactivo de criterio
        criterio = st.selectbox(
            "Selecciona el criterio para clasificar los puntos en el mapa:",
            ["Unidad Vecinal", "Macrosector", "Microsector"]
        )

        # Configuración de la paleta de colores
        colores_disponibles = [
            "red", "blue", "green", "purple", "orange", "darkred", "cadetblue", 
            "darkpurple", "pink", "darkblue", "darkgreen"
        ]

        categorias_unicas = df[criterio].dropna().unique()
        for i, cat in enumerate(categorias_unicas):
            diccionario_colores[cat] = colores_disponibles[i % len(colores_disponibles)]

        st.caption(f"Visualizando un extracto optimizado de las {len(df)} intervenciones detectadas.")

        # Dibujar los puntos sobre el objeto 'mapa'
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
    except Exception as e:
        st.error(f"Error al procesar los puntos del mapa: {e}")

# =========================================================================
# 4. RENDERIZADO FINAL DEL MAPA EN LA PÁGINA
# =========================================================================
# Al dejar esta función afuera de cualquier "if", el mapa se dibuja sí o sí
st_folium(mapa, width="100%", height=650)

# =========================================================================
# 5. LEYENDA DINÁMICA
# =========================================================================
if diccionario_colores:
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
