import streamlit as st
from PIL import Image

# Configuración de página
st.set_page_config(
    page_title="Transformaciones Geodésicas",
    layout="wide",
    page_icon="🌍",
    initial_sidebar_state="expanded"
)

# Estilos CSS personalizados
st.markdown("""
<style>
    .main {
        background-color: #f8f9fa;
    }
    .sidebar .sidebar-content {
        background-color: #2c3e50;
        color: white;
    }
    .stRadio > div {
        flex-direction: column;
        gap: 0.5rem;
    }
    .stButton>button {
        background-color: #2980b9;
        color: white;
        border-radius: 8px;
        padding: 0.5rem 1rem;
    }
    .card {
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        margin-bottom: 1rem;
        background: white;
    }
    .header {
        color: #2c3e50;
        border-bottom: 2px solid #2980b9;
        padding-bottom: 0.5rem;
    }
    .feature-icon {
        font-size: 2rem;
        margin-bottom: 0.5rem;
        color: #16a085;
    }
</style>
""", unsafe_allow_html=True)

# Importación de módulos (asegúrate de tener estos archivos)
from Latitudes import latitudes_interface
from Directo import directas_interface
from Inverso import inversas_interface
from no_reciproca import no_reciproca_interface
from biseccion_triseccion import biseccion_interface, triseccion_interface
from reciproca import reciproca_interface
from geodesica import nivelacion_geodesica_streamlit
from lon_arco import calcular_longitud_arco_interface
from area_cuadrilatero import area_cuadrilatero_interface


with st.sidebar:
    
    col1, col2 = st.columns([1, 3])
    with col1:
        st.image("https://cdn-icons-png.flaticon.com/512/44/44386.png", width=50)
    with col2:
        st.markdown("<h2 style='color:Black; margin-top:10px;'>GeodesiaPro</h2>", unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Menú de navegación con iconos
    opcion = st.radio(
        "**NAVEGACIÓN**",
        options=[
            "🏠 Inicio",
            "📏 Latitudes Meridianas",
            "📍 Coordenadas Directas",
            "↩️ Coordenadas Inversas",
            "📊 Nivelación Geodésica",
            "🔢 Métodos Numéricos",
            "🔄 Nivelación No Recíproca",
            "⚖️ Nivelación Recíproca",
            "🌐 Arcos Meridiano/Paralelo",
            "⬜ Área Cuadrilátero"
        ],
        index=0
    )
    
    st.markdown("---")
    st.markdown("""
    <div style='color:white; font-size:small;'>
    <b>Desarrollado por:</b><br>
    Ricardo Romero<br>
    <b>Versión:</b> 1.1.0
    </div>
    """, unsafe_allow_html=True)


if opcion == "🏠 Inicio":
    
    st.markdown("""
    <div style='background-image: url(https://imgur.com/0DjOzwt.jpg);
                background-size: cover;
                background-position: center;
                height: 250px;
                border-radius: 10px;
                display: flex;
                align-items: center;
                justify-content: center;
                margin-bottom: 2rem;'>
        <h1 style='color: white; text-align: center;'>Geodesia Geométrica</h1>
    </div>
    """, unsafe_allow_html=True)

    
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class='card'>
            <div class='feature-icon'>🌐</div>
            <h3 class='header'>Transformaciones</h3>
            <p>Conversión entre sistemas de coordenadas geodésicas y cartesianas</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class='card'>
            <div class='feature-icon'>📐</div>
            <h3 class='header'>Cálculos Precisos</h3>
            <p>Algoritmos de alta precisión para cálculos geodésicos</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class='card'>
            <div class='feature-icon'>📊</div>
            <h3 class='header'>Visualización</h3>
            <p>Resultados gráficos</p>
        </div>
        """, unsafe_allow_html=True)
    
   
    st.markdown("""
    <div class='card'>
        <h2 class='header'>¿Cómo usar esta aplicación?</h2>
        <ol>
            <li>Selecciona el módulo deseado en el menú lateral</li>
            <li>Ingresa los parámetros requeridos</li>
            <li>Visualiza los resultados</li>
            <li>Exporta los datos si es necesario</li>
        </ol>
    </div>
    """, unsafe_allow_html=True)

elif opcion == "📏 Latitudes Meridianas":
    latitudes_interface()

elif opcion == "📍 Coordenadas Directas":
    directas_interface()

elif opcion == "↩️ Coordenadas Inversas":
    inversas_interface()

elif opcion == "🔄 Nivelación No Recíproca":
    no_reciproca_interface()

elif opcion == "⚖️ Nivelación Recíproca":
    reciproca_interface()

elif opcion == "🔢 Métodos Numéricos":
    metodo = st.radio("**Selecciona método numérico:**", ["Bisección", "Trisección"], horizontal=True)
    if metodo == "Bisección":
        biseccion_interface()
    else:
        triseccion_interface()

elif opcion == "📊 Nivelación Geodésica":
    nivelacion_geodesica_streamlit()

elif opcion == "🌐 Arcos Meridiano/Paralelo":
    calcular_longitud_arco_interface()

elif opcion == "⬜ Área Cuadrilátero":
    area_cuadrilatero_interface()

st.markdown("""
---
<div style='text-align:center; color: #888; font-size: 0.9em;'>
    © 2025 | Geodesia App | Desarrollado con Streamlit
</div>
""", unsafe_allow_html=True)
