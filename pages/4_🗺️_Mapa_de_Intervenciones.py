import streamlit as st
import pandas as pd

# 1. Configuración de la página en modo ancho para máxima visualización
st.set_page_config(page_title="Mapa de Intervenciones", layout="wide")

st.title("📍 Distribución Geográfica de Intervenciones (Camión Vactor)")
st.write("Visualización técnica optimizada para la comuna de Temuco utilizando el motor nativo de Streamlit.")

# Nombre exacto de tu archivo en la raíz del repositorio
ARCHIVO_DATOS = "datos_vactor.csv"

try:
    # 2. Cargar datos desde el CSV
    df = pd.read_csv(ARCHIVO_DATOS)
    
    # 3. Limpieza crítica de filas vacías
    df = df.dropna(subset=['Coordenada X', 'Coordenada Y'])
    
    # 4. Conversión de comas a puntos para decimales correctos
    df['longitude'] = df['Coordenada X'].astype(str).str.replace(',', '.').astype(float)
    df['latitude'] = df['Coordenada Y'].astype(str).str.replace(',', '.').astype(float)
    
    if df.empty:
        st.error("El archivo CSV no contiene registros con coordenadas válidas.")
        st.stop()

    # 5. Selector interactivo de criterios
    criterio = st.selectbox(
        "Selecciona el criterio para clasificar los puntos en el mapa:",
        ["Unidad Vecinal", "Macrosector", "Microsector"]
    )

    # 6. Asignación de colores en formato HEX (Compatibles con el motor nativo)
    colores_hex = [
        "#FF5733", "#33FF57", "#3357FF", "#F39C12", "#9B59B6", 
        "#1ABC9C", "#2C3E50", "#D35400", "#C0392B", "#27AE60"
    ]
    
    categorias_unicas = df[criterio].dropna().unique()
    diccionario_colores = {}
    for i, cat in enumerate(categorias_unicas):
        diccionario_colores[cat] = colores_hex[i % len(colores_hex)]
        
    # Crear columna de color por cada fila según el criterio seleccionado
    df['color'] = df[criterio].map(diccionario_colores).fillna("#7F8C8D")

    # 7. DESPLIEGUE DEL MAPA NATIVO (Escala y compatibilidad garantizada)
    st.map(
        df,
        latitude='latitude',
        longitude='longitude',
        color='color',
        size=20,  # Tamaño ideal para que los puntos sean visibles pero no tapen las calles
        use_container_width=True
    )

    # 8. LEYENDA TÉCNICA EN 3 COLUMNAS
    st.markdown("### 📊 Leyenda de Sectores Detectados")
    cols = st.columns(3)
    
    for i, (cat, col) in enumerate(diccionario_colores.items()):
        with cols[i % 3]:
            st.markdown(
                f"""
                <div style="display: flex; align-items: center; margin-bottom: 8px; font-family: sans-serif;">
                    <span style="
                        display: inline-block; 
                        width: 14px; 
                        height: 14px; 
                        background-color: {col}; 
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
    st.error(f"No se pudo encontrar el archivo '{ARCHIVO_DATOS}' en la raíz del proyecto.")
except Exception as e:
    st.error(f"Ocurrió un error al procesar el mapa nativo: {e}")
