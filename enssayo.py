import streamlit as st
import numpy as np
import math

# Parámetros comunes de elipsoides con a, b y 1/f
ELIPSOIDES = {
    "WGS84": {"a": 6378137.0, "b": 6356752.3142, "inv_f": 298.257223563},
    "GRS80": {"a": 6378137.0, "b": 6356752.3141, "inv_f": 298.257222101},
    "Internacional": {"a": 6378388.0, "b": 6356911.9462, "inv_f": 297.0},
}

def dms_a_grados(d, m, s, hemisferio):
    signo = -1 if hemisferio in ('S', 'W') else 1
    return signo * (abs(d) + m / 60 + s / 3600)

def calcular_area_exacta(phi1, phi2, lambda1, lambda2, b, e):
    if phi2 < phi1:
        phi1, phi2 = phi2, phi1
    if lambda2 < lambda1:
        lambda1, lambda2 = lambda2, lambda1

    term1_phi1 = math.sin(phi1) / (1 - e**2 * math.sin(phi1)**2)
    term1_phi2 = math.sin(phi2) / (1 - e**2 * math.sin(phi2)**2)

    term2_phi1 = (1 / (2 * e)) * math.log((1 + e * math.sin(phi1)) / (1 - e * math.sin(phi1)))
    term2_phi2 = (1 / (2 * e)) * math.log((1 + e * math.sin(phi2)) / (1 - e * math.sin(phi2)))

    integral = (term1_phi2 + term2_phi2) - (term1_phi1 + term2_phi1)
    delta_lambda = lambda2 - lambda1
    area = 0.5 * abs(delta_lambda) * (b ** 2) * integral
    return abs(area)

def calcular_area_serie(phi1, phi2, lambda1, lambda2, b, e, n=10):
    def serie(phi):
        suma = 0
        for k in range(n):
            coef = (k + 1) / (2 * k + 1)
            suma += coef * (e ** (2 * k)) * (math.sin(phi) ** (2 * k + 1))
        return suma

    if phi2 < phi1:
        phi1, phi2 = phi2, phi1
    if lambda2 < lambda1:
        lambda1, lambda2 = lambda2, lambda1

    delta_lambda = lambda2 - lambda1
    integral = serie(phi2) - serie(phi1)
    area = b ** 2 * abs(delta_lambda) * integral
    return abs(area)

def calcular_area_total_elipsoide(b, e, n=10):
    suma = sum(((k + 1) / (2 * k + 1)) * e**(2 * k) for k in range(n))
    area_total = 4 * math.pi * b**2 * suma
    return area_total

def area_cuadrilatero_interface():
    st.header("Área de Cuadrilátero Geodésico")

    st.subheader("Parámetros del Elipsoide")
    elipsoide = st.selectbox("Selecciona el elipsoide", list(ELIPSOIDES.keys()))
    a = ELIPSOIDES[elipsoide]["a"]
    b = ELIPSOIDES[elipsoide]["b"]
    inv_f = ELIPSOIDES[elipsoide]["inv_f"]
    f = 1 / inv_f
    e2 = f * (2 - f)
    e = math.sqrt(e2)

    col1, col2 = st.columns(2)
    with col1:
        st.write(f"a: {a} m")
        st.write(f"b: {b} m")
    with col2:
        st.write(f"1/f: {inv_f}")
        st.write(f"e²: {e2:.12f}")

    if st.button("Calcular Área Total del Elipsoide"):
        area_total = calcular_area_total_elipsoide(b, e)
        st.success(f"Área total del elipsoide: {area_total:.6f} m²")
        st.info(f"Área total ≈ {area_total / 1e6:.6f} km²")

    st.subheader("Coordenadas del Cuadrilátero (Formato GMS)")

    def ingresar_gms(nombre):
        col1, col2, col3, col4 = st.columns([1, 1, 1, 1])
        with col1:
            g = st.text_input(f"Grados {nombre}", value="")
        with col2:
            m = st.text_input(f"Minutos {nombre}", value="")
        with col3:
            s = st.text_input(f"Segundos {nombre}", value="")
        with col4:
            h = st.selectbox(f"Hemisferio {nombre}", options=["N", "S"] if "Lat" in nombre else ["E", "W"])

        try:
            g = float(g)
            m = float(m)
            s = float(s)
            return dms_a_grados(g, m, s, h)
        except ValueError:
            return None

    st.markdown("**Latitud inferior**")
    phi1_deg = ingresar_gms("Lat1")
    st.markdown("**Latitud superior**")
    phi2_deg = ingresar_gms("Lat2")

    st.markdown("**Longitud occidental**")
    lambda1_deg = ingresar_gms("Lon1")
    st.markdown("**Longitud oriental**")
    lambda2_deg = ingresar_gms("Lon2")

    metodo = st.selectbox("Método de cálculo:", ["Exacto", "Serie"])

    if st.button("🔍 Calcular Área", type="primary"):
        if None in [phi1_deg, phi2_deg, lambda1_deg, lambda2_deg]:
            st.error("Por favor completa todas las coordenadas correctamente.")
        else:
            try:
                phi1 = math.radians(phi1_deg)
                phi2 = math.radians(phi2_deg)
                lambda1 = math.radians(lambda1_deg)
                lambda2 = math.radians(lambda2_deg)

                if metodo == "Exacto":
                    area = calcular_area_exacta(phi1, phi2, lambda1, lambda2, b, e)
                else:
                    area = calcular_area_serie(phi1, phi2, lambda1, lambda2, b, e)
                st.info(f"**Área del cuadrilátero:**\n\n"
                       f" {area:.6f} m² \n\n"
                       f" {area / 1e6:.6f} km²")
            except Exception as e:
                st.error(f"Error: {e}")

if __name__ == "__main__":
    area_cuadrilatero_interface()