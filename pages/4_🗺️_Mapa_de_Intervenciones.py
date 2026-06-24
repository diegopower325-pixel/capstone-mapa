import streamlit as st
import pandas as pd
import folium
from streamlit_folium import folium_static
from folium.plugins import ScaleControl

# Configuración de la página en modo ancho
st.set_page_config(page_title="Mapa de Intervenciones", layout="wide")

# Mensaje de control para saber si Streamlit leyó el código nuevo
st.sidebar.success("✅ Versión del código: V3 (Con Escala y Norte)")

st.title("📍 Distribución Geográfica de Intervenciones (Camión Vactor)")
st.write("Visualización técnica para la comuna de Temuco.")

# Nombre de tu archivo en el repositorio
ARCHIVO_DATOS = "datos_vactor.csv"

try:
    df = pd.read_csv(ARCHIVO_DATOS)
    df = df.dropna(subset=['Coordenada X', 'Coordenada Y'])
    
    df['Coordenada X'] = df['Coordenada X'].astype(str).str.replace(',', '.').astype(float)
    df['Coordenada Y'] = df['Coordenada Y'].astype(str).str.replace(',', '.').astype(float)
    
    if df.empty:
        st.error("El archivo CSV no contiene registros con coordenadas válidas.")
        st.stop()

    # Layout de control arriba del mapa
    col_sel, col_norte = st.columns([4, 1])
    
    with col_sel:
        criterio = st.selectbox(
            "Selecciona el criterio para clasificar los puntos en el mapa:",
            ["Unidad Vecinal", "Macrosector", "Microsector"]
        )
    
    with col_norte:
        # Colocamos el Norte directamente en la interfaz de Streamlit para asegurar su visibilidad
        st.markdown(
            """
            <div style="text-align: center; margin-top: 5px;">
                <img src="https://i.imgur.com/83pL6gC.png" width="45px" style="margin-bottom: 2px;"><br>
                <span style="font-size: 11px; font-weight: bold; color: #555;">NORTE</span>
            </div>
            """, 
            unsafe_allow_html=True
        )

    # Paleta de colores
    colores_disponibles = ["red", "blue", "green", "purple", "orange", "darkred", "cadetblue", "darkpurple", "pink", "darkblue", "darkgreen"]
    categorias_unicas = df[criterio].dropna().unique()
    diccionario_colores = {cat: colores_disponibles[i % len(colores_disponibles)] for i, cat in enumerate(categorias_unicas)}

    # Crear el mapa base centrado en Temuco
    mapa = folium.Map(
        location=[-38.745, -72.615], 
        zoom_start=12, 
        tiles="https://server.arcgisonline.com/ArcGIS/rest/services/World_Topo_Map/MapServer/tile/{z}/{y}/{x}",
        attr="Esri / ArcGIS Online"
    )

    # ESCALA GRÁFICA NATIVA (Esta se dibuja directo en el mapa)
    ScaleControl(position='bottomleft', imperial=False, metric=True).add_to(mapa)

    # Renderizar puntos
    df_render = df.head(1200)
    for index, fila in df_render.iterrows():
        try:
            lat = float(fila['Coordenada Y'])
            lon = float(fila['Coordenada X'])
            categoria_actual = fila[criterio]
            color_punto = diccionario_colores.get(categoria_actual, "gray")
                
            info_popup = f"""
            <b>Dirección:</b> {fila.get('Dirección de la Orden de Trabajo de Workforce', 'No registrada')}<br>
            <b>{criterio}:</b> {categoria_actual}<br>
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

    # Desplegar mapa estático robusto
    folium_static(mapa, width=1050, height=580)

    # Leyenda Dinámica
    st.markdown("### 📊 Leyenda de Sectores Detectados")
    cols = st.columns(3)
    for i, (cat, col) in enumerate(diccionario_colores.items()):
        mapa_colores_hex = {"red": "#E74C3C", "blue": "#3498DB", "green": "#2ECC71", "purple": "#9B59B6", "orange": "#E67E22", "darkred": "#943126", "cadetblue": "#5D6D7E", "darkpurple": "#4A235A", "pink": "#F48FB1", "darkblue": "#1B4F72", "darkgreen": "#1E8449", "gray": "#7F8C8D"}
        color_hex = mapa_colores_hex.get(col, "#7F8C8D")
        with cols[i % 3]:
            st.markdown(f'<div style="display: flex; align-items: center; margin-bottom: 8px;"><span style="display: inline-block; width: 14px; height: 14px; background-color: {color_hex}; border-radius: 50%; margin-right: 10px; border: 1px solid #555;"></span><span style="font-weight: bold; font-size: 14px;">{cat}</span></div>', unsafe_allow_html=True)

except FileNotFoundError:
    st.error(f"No se pudo encontrar el archivo '{ARCHIVO_DATOS}'.")
except Exception as e:
    st.error(f"Error: {e}")
