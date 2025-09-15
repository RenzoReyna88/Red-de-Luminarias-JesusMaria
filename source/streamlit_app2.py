import streamlit as st
import geopandas as gpd
import pydeck as pdk
from streamlit.components.v1 import html as st_html





# Configurar la página más ancha
st.set_page_config(layout="wide")

@st.cache_data
def cargar_geojson_local(ruta_geojson):
    gdf = gpd.read_file(ruta_geojson)
    gdf = gdf.to_crs(epsg=4326)

    # Opcional: seleccionar solo columnas útiles
    columnas_necesarias = ["id", "tipo", "geometry"]  # adaptá según lo que tenés
    existentes = [c for c in columnas_necesarias if c in gdf.columns]
    gdf = gdf[existentes]

    # Añadir columnas de lat / lon
    gdf["lon"] = gdf.geometry.x
    gdf["lat"] = gdf.geometry.y
    return gdf

def crear_mapa(gdf, filtros=None):
    if filtros:
        # aplicá filtros si existen
        if "tipo" in filtros:
            gdf = gdf[gdf["tipo"].isin(filtros["tipo"])]


    # Definir colores manuales para cada tipo
    color_map = {
        "sodio": [255, 130, 0, 255],          # naranja translúcido
        "led": [0, 100, 255, 255],             # azul‑claro
        "postacion sin alumbrado": [200, 0, 0, 255]  # gris
    }

    # Si alguna fila tiene tipo no especificado, definís un color por defecto
    color_default = [0, 0, 0, 100]  # negro translúcido

    # Crear columna color en el data frame
    def tipo_a_color(tipo):
        return color_map.get(tipo.lower(), color_default)

    # Asumimos que valores en gdf["tipo"] están bien escritos; si no podés homogenizar (lower, trim)
    gdf["color"] = gdf["tipo"].apply(lambda t: tipo_a_color(t))

    # preparar vista inicial
    lat0 = float(gdf["lat"].mean())
    lon0 = float(gdf["lon"].mean())

    view_state= pdk.ViewState(
        latitude=lat0,
        longitude=lon0,
        zoom=12,
        pitch=51,
        bearing=30
    )

    scatter = pdk.Layer(
        "ScatterplotLayer",
        data=gdf,
        get_position=["lon", "lat"],
        pickable=True,
        get_radius=5,  # ajustá según escala
        get_fill_color="color",
        get_stroke_color=[0, 0, 0, 0],
        stroked=True,
        filled=True,
        radius_min_pixels=3,
        radius_max_pixels=18,
    )

    deck = pdk.Deck(
        initial_view_state=view_state,
        layers=[scatter],
        tooltip={"text": "ID: {id}\nTipo luminaria: {tipo}"},
    )

    return deck


def main():

    # Configuración del estilo del logo
    import base64
    with open("source/assets/logo/logo-personal-white.jpg", "rb") as logo:
        data = logo.read()
        encoded = base64.b64encode(data).decode()

    st.markdown(
        f"""
        <div style='display: flex; align-items: center;'>
            <img src='data:image/png;base64,{encoded}'style='border-radius: 50%; hiegth:90; width: 90px;'/>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.title("Mapa de Luminarias de la Ciudad de Jesús María")

    # Ruta o URL del geojson
    ruta = "cuadernos/datos-iluminaria/Jesus_Maria_Luminarias_Postacion.geojson"  
    
    # Cargar datos
    gdf = cargar_geojson_local(ruta)

    # Filtros en sidebar si los querés
    filtros = {}
    if "tipo" in gdf.columns:
        tipos = gdf["tipo"].unique().tolist()
        seleccion = st.sidebar.multiselect("Tipo de luminaria", tipos, default=tipos)
        filtros["tipo"] = seleccion


    # Crear mapa
    deck = crear_mapa(gdf, filtros)

    st.markdown(
        """
        <div style="display: inline-flex; gap:9px; align-items: start;">
        <span>🟠</span>SODIO  
        <span>🔵</span>LED  
        <span>🔴</span>POSTACIÓN SIN ALUMBRADO
        </div>
        """,
        unsafe_allow_html=True
    )

    # Mostrar mapa (usar HTML embebido si mejora performance)
    html_string = deck.to_html(as_string=True, notebook_display=False)
    st_html(html_string, height=500)

 
    col1, col2, col3 = st.columns(3)

    col1.metric("🟠 SODIO:", "1733")
    col2.metric("🔵 LED:", "1507")
    col3.metric("🔴 POSTACIÓN SIN ALUMBRADO:", "66")


    st.markdown(
        """
        ### 🌐 Interfaz de luminarias: clave para la planificación energética sostenible

        Contar con una interfaz que integre datos sobre los **tipos** y **cantidad de luminarias** del sistema energético permite transformar la gestión territorial en una práctica más **eficiente, transparente y orientada al futuro**.

        - 📊 **Tipología de luminarias** (LED, sodio, halógenas, etc.) revela el grado de modernización y eficiencia energética del sistema.
        - 🗺️ **Distribución geográfica** permite detectar zonas con déficit de alumbrado, sobrecarga o potencial de mejora.
        - ♻️ **Planificación sostenible**: facilita decisiones basadas en consumo, emisiones y mantenimiento, alineadas con objetivos ambientales.
        - 💡 **Gestión inteligente**: habilita el monitoreo dinámico, la priorización de inversiones y la participación ciudadana.
        - 🔌 **Integración con otros recursos**: al vincularse con datos de consumo, infraestructura y seguridad, potencia una visión sistémica del territorio.

        Esta interfaz no solo simplifica el acceso a la información, también convierte los datos en **herramientas de transformación territorial**, donde cada luminaria cuenta una historia de desarrollo, equidad y sostenibilidad.
        """,
        unsafe_allow_html=False
    )


    st.markdown("Fuente de datos IDECOR: https://idecor-ws.mapascordoba.gob.ar/geoserver/idecor/Jesus_Maria_Luminarias_Red/wms?request=GetCapabilities")

    st.markdown("---")

    st.markdown("### Contacto")
    st.markdown("Teléfono: +54 3252 62-0842")
    st.markdown("Email: reynarenzo.88@gmail.com")
    st.markdown("Domicilio: INDEPENDENCIA 0, SARMIENTO, CÓRDOBA, ARGENTINA")

    st.markdown("---")

    st.markdown("""
                <div style='text-align: center;'>
                    © 2025 Renzo Gerardo Reyna - Análisis de datos / Desarrollo en Python
                 </div>""",
                 unsafe_allow_html=True
                 )
if __name__ == "__main__":
    main()

