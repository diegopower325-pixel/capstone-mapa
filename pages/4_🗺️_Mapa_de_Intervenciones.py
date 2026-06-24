import streamlit as st
import pandas as pd
import folium
from streamlit_folium import folium_static  # Cambiamos a la función estática para asegurar plugins
from folium.plugins import FloatImage, ScaleControl, MousePosition

# Configuración de la página en modo ancho
st.set_page_config(page_title="Mapa de Intervenciones", layout="wide")
st.title("📍 Distribución Geográfica de Intervenciones (Camión Vactor)")
st.write("Visualización técnica con coordenadas de referencia, escala y norte magnético.")

# Nombre exacto de tu archivo en la raíz del repositorio
ARCHIVO_DATOS = "datos_vactor.csv"

try:
    # 1. Cargar datos desde el CSV
    df = pd.read_csv(ARCHIVO_DATOS)
    
    # 2. Limpieza crítica: Eliminar filas vacías
    df = df.dropna(subset=['Coordenada X', 'Coordenada Y'])
    
    # 3. Conversión de comas a puntos para procesar decimales
    df['Coordenada X'] = df['Coordenada X'].astype(str).str.replace(',', '.').astype(float)
    df['Coordenada Y'] = df['Coordenada Y'].astype(str).str.replace(',', '.').astype(float)
    
    if df.empty:
        st.error("El archivo CSV no contiene registros con coordenadas válidas.")
        st.stop()

    # Selector interactivo
    criterio = st.selectbox(
        "Selecciona el criterio para clasificar los puntos en el mapa:",
        ["Unidad Vecinal", "Macrosector", "Microsector"]
    )

    # Paleta de colores dinámicos
    colores_disponibles = [
        "red", "blue", "green", "purple", "orange", "darkred", "cadetblue", 
        "darkpurple", "pink", "darkblue", "darkgreen"
    ]

    categorias_unicas = df[criterio].dropna().unique()
    diccionario_colores = {}
    for i, cat in enumerate(categorias_unicas):
        diccionario_colores[cat] = colores_disponibles[i % len(colores_disponibles)]

    # =========================================================================
    # CONFIGURACIÓN DEL MAPA CON MÉTODOS CARTOGRÁFICOS ALTERNATIVOS
    # =========================================================================
    mapa = folium.Map(
        location=[-38.745, -72.615], 
        zoom_start=12, 
        tiles="https://server.arcgisonline.com/ArcGIS/rest/services/World_Topo_Map/MapServer/tile/{z}/{y}/{x}",
        attr="Esri / ArcGIS Online"
    )

    # A. AÑADIR ESCALA GRÁFICA (Forzada en la esquina inferior izquierda)
    ScaleControl(position='bottomleft', imperial=False, metric=True).add_to(mapa)

    # B. AÑADIR NORTE CARTOGRÁFICO
    # Usamos una URL alternativa muy estable de una flecha de norte limpia
    url_norte = "https://i.imgur.com/83pL6gC.png"  # Flecha de norte estándar de alta visibilidad
    FloatImage(url_norte, bottom=85, left=90, width="40px").add_to(mapa)

    # C. RECUADRO DE COORDENADAS DINÁMICAS (Esquina superior derecha)
    MousePosition(
        position='topright',
        separator=' | Y: ',
        empty_string='Fuera del mapa',
        lng_first=True,  # X (Longitud) primero, luego Y (Latitud)
        prefix='X: '
    ).add_to(mapa)

    # =========================================================================
    # RENDERIZADO DE PUNTOS
    # =========================================================================
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

    # NUEVO MÉTODO: Forzar el renderizado completo del mapa con folium_static
    folium_static(mapa, width=1100, height=600)

    # =========================================================================
    # LEYENDA DINÁMICA CON COLORES REALES
    # =========================================================================
    st.markdown("### 📊 Leyenda de Sectores Detectados")
    cols = st.columns(3)
    
    for i, (cat, col) in enumerate(diccionario_colores.items()):
        mapa_colores_hex = {
            "red": "#E74C3C", "blue": "#3498DB", "green": "#2ECC71", 
            "purple": "#9B59B6", "orange": "#E67E22", "darkred": "#943126", 
            "cadetblue": "#5D6D7E", "darkpurple": "#4A235A", "pink": "#F48FB1", 
            "darkblue": "#1B4F72", "darkgreen": "#1E8449", "gray": "#7F8C8D"
        }
        color_hex = mapa_colores_hex.get(col, "#7F8C8D")
        
        with cols[i % 3]:
            st.markdown(
                f"""
                <div style="display: flex; align-items: center; margin-bottom: 8px; font-family: sans-serif;">
                    <span style="
                        display: inline-block; 
                        width: 14px; 
                        height: 14px; 
                        background-color: {color_hex}; 
                        border-radius: 50%; 
                        margin-right: 10px;
                        border: 1px solid #555;
                    "></span>
                    <span style="font-weight: bold; color: #333; font-size: 14px;">{cat}</span>
                </div>
                """, 
                unsafe_allow_html=True
            )

except FileNotFoundError:
    st.error(f"No se pudo encontrar el archivo '{ARCHIVO_DATOS}' en tu repositorio.")
except Exception as e:
    st.error(f"Ocurrió un error al procesar el mapa: {e}")
