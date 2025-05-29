import streamlit as st

st.set_page_config(page_title="Transformaciones Geodésicas", layout="centered")

from Latitudes import latitudes_interface
from Directo import directas_interface
from Inverso import inversas_interface
from no_reciproca import no_reciproca_interface
from biseccion_triseccion import biseccion_interface, triseccion_interface
from reciproca import reciproca_interface
from geodesica import altura_instrumental_streamlit
from lon_arco import calcular_longitud_arco_interface
from area_cuadrilatero import area_cuadrilatero_interface  # Nuevo módulo

st.title("Programas Geodésia Geometrica")
st.markdown("---")

opcion = st.sidebar.radio(
    "Selecciona un módulo:",
    [
        "Inicio",
        "Latitudes Meridianas",
        "Coordenadas Geocéntricas Directas",
        "Coordenadas Geocéntricas Inversas",
        "Nivelación Geodésica",
        "Métodos Numéricos",
        "Nivelación No Recíproca",
        "Nivelación Recíproca",
        "Arco de meridiano y paralelo",
        "Área de Cuadrilátero Geodésico" 
    ]
)

if opcion == "Inicio":
    st.subheader("Bienvenido al programa de transformaciones geodésicas")
    st.markdown("Selecciona un módulo en el menú lateral para comenzar.")

elif opcion == "Latitudes Meridianas":
    latitudes_interface()

elif opcion == "Coordenadas Geocéntricas Directas":
    directas_interface()

elif opcion == "Coordenadas Geocéntricas Inversas":
    inversas_interface()

elif opcion == "Nivelación No Recíproca":
    no_reciproca_interface()

elif opcion == "Nivelación Recíproca":
    reciproca_interface()

elif opcion == "Métodos Numéricos":
    metodo = st.sidebar.radio("Elige un método:", ["Bisección", "Trisección"])
    if metodo == "Bisección":
        biseccion_interface()
    else:
        triseccion_interface()

elif opcion == "Nivelación Geodésica":
    altura_instrumental_streamlit()

elif opcion == "Arco de meridiano y paralelo":
    calcular_longitud_arco_interface()

elif opcion == "Área de Cuadrilátero Geodésico":  
    area_cuadrilatero_interface()
