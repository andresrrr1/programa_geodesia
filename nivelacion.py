import streamlit as st
import math

def gms_to_decimal(grados, minutos, segundos):
    return grados + minutos / 60 + segundos / 3600

def calcular_altura(Z1, Z2, S, H1, rho=6371000, i=None, o=None):
    delta_Z = math.radians((Z2 - Z1) / 2)
    A = 1 + H1 / rho
    B = 1 + (S / (2 * rho)) * math.tan(delta_Z)
    C = 1 + (S**2 / (12 * rho**2))

    C_refrac = (i - o) / (S * math.sin(math.radians(1/3600))) if i is not None and o is not None else 0
    delta_H = S * math.tan(delta_Z) * A * B * C + C_refrac
    H2 = H1 + delta_H

    return round(H2, 4), round(delta_H, 4)

def nivelacion_interface():
    st.header("📏 Nivelación Trigonométrica Recíproca")
    st.markdown("Esta herramienta permite calcular la cota de un punto usando ángulos cenitales o verticales.")

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Ángulo desde Estación 1")
        tipo1 = st.radio("Tipo de ángulo:", ["Cenital (Z1)", "Vertical (V1)"], key="z1_tipo")
        g1 = st.number_input("Grados", key="g1")
        m1 = st.number_input("Minutos", key="m1")
        s1 = st.number_input("Segundos", key="s1")
        Z1 = gms_to_decimal(g1, m1, s1)
        if tipo1 == "Vertical (V1)":
            Z1 = 90 - Z1

    with col2:
        st.subheader("Ángulo desde Estación 2")
        tipo2 = st.radio("Tipo de ángulo:", ["Cenital (Z2)", "Vertical (V2)"], key="z2_tipo")
        g2 = st.number_input("Grados", key="g2")
        m2 = st.number_input("Minutos", key="m2")
        s2 = st.number_input("Segundos", key="s2")
        Z2 = gms_to_decimal(g2, m2, s2)
        if tipo2 == "Vertical (V2)":
            Z2 = 90 - Z2

    st.markdown("---")
    S = st.number_input("Distancia horizontal S (m)", min_value=0.0)
    H1 = st.number_input("Cota conocida H1 (m)", min_value=0.0)
    rho = st.number_input("Radio de curvatura ρ (m)", value=6371000.0)

    st.markdown("**Corrección por refracción (opcional):**")
    i = st.number_input("Altura instrumental (i)", value=0.0)
    o = st.number_input("Altura del objetivo (o)", value=0.0)

    if st.button("Calcular altura H2"):
        H2, delta_H = calcular_altura(Z1, Z2, S, H1, rho, i, o)
        st.success(f"Altura del punto H2 = {H2} m")
        st.info(f"Diferencia de altura = {delta_H} m")
