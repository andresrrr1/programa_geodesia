import streamlit as st
import numpy as np
import math
import matplotlib.pyplot as plt

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

def graficar_segmento(phi1_deg, phi2_deg, lambda1_deg, lambda2_deg, a, b):
    import plotly.graph_objects as go

    # Generar malla de elipsoide
    u = np.linspace(0, 2 * np.pi, 100)
    v = np.linspace(-np.pi / 2, np.pi / 2, 100)
    u, v = np.meshgrid(u, v)
    x = a * np.cos(v) * np.cos(u)
    y = a * np.cos(v) * np.sin(u)
    z = b * np.sin(v)

    elipsoide = go.Surface(x=x, y=y, z=z, colorscale='Greys', opacity=0.3, showscale=False)

    # Coordenadas de las esquinas del cuadrilátero
    latitudes = np.radians([phi1_deg, phi2_deg])
    longitudes = np.radians([lambda1_deg, lambda2_deg])

    corners = [
        (latitudes[0], longitudes[0]),
        (latitudes[0], longitudes[1]),
        (latitudes[1], longitudes[1]),
        (latitudes[1], longitudes[0]),
        (latitudes[0], longitudes[0]),
    ]

    xs, ys, zs = [], [], []
    for phi, lamb in corners:
        x = a * np.cos(phi) * np.cos(lamb)
        y = a * np.cos(phi) * np.sin(lamb)
        z = b * np.sin(phi)
        xs.append(x)
        ys.append(y)
        zs.append(z)

    cuadrilatero = go.Scatter3d(x=xs, y=ys, z=zs, mode='lines+markers', line=dict(color='blue', width=4), marker=dict(size=4, color='red'))

    layout = go.Layout(
        title="Cuadrilátero sobre el elipsoide (interactivo)",
        scene=dict(
            xaxis_title='X (m)',
            yaxis_title='Y (m)',
            zaxis_title='Z (m)',
            aspectmode='data'
        ),
        margin=dict(l=0, r=0, b=0, t=30)
    )

        # Trazar el ecuador
    eq_lons = np.linspace(0, 2 * np.pi, 200)
    eq_x = a * np.cos(eq_lons)
    eq_y = a * np.sin(eq_lons)
    eq_z = np.zeros_like(eq_lons)

    ecuador = go.Scatter3d(x=eq_x, y=eq_y, z=eq_z, mode='lines', line=dict(color='red', width=3), name='Ecuador')

        # Trazar Greenwich
    green_lats = np.linspace(-np.pi, np.pi, 400)
    green_x = a * np.cos(green_lats)
    green_y = np.zeros_like(green_lats)
    green_z = b * np.sin(green_lats)

    greenwich = go.Scatter3d(x=green_x, y=green_y, z=green_z, mode='lines', line=dict(color='green', width=3), name='Greenwich')

        # Etiquetas de lat/lon ingresadas
    etiquetas = []
    latitudes_graficas = [phi1_deg, phi2_deg]
    longitudes_graficas = [lambda1_deg, lambda2_deg]
    labels = ['Lat1-Lon1', 'Lat1-Lon2', 'Lat2-Lon2', 'Lat2-Lon1']

    for i, (lat, lon) in enumerate([
        (latitudes_graficas[0], longitudes_graficas[0]),
        (latitudes_graficas[0], longitudes_graficas[1]),
        (latitudes_graficas[1], longitudes_graficas[1]),
        (latitudes_graficas[1], longitudes_graficas[0])
    ]):
        phi = math.radians(lat)
        lamb = math.radians(lon)
        x = a * math.cos(phi) * math.cos(lamb)
        y = a * math.cos(phi) * math.sin(lamb)
        z = b * math.sin(phi)
        etiquetas.append(go.Scatter3d(x=[x], y=[y], z=[z], mode='text', text=[labels[i]], textposition='top center', showlegend=False))

        # Mostrar puntos en la latitud ingresada desde el ecuador
    puntos_latitud = []
    for lat, lon in [(phi1_deg, lambda1_deg), (phi2_deg, lambda2_deg)]:
        phi = math.radians(lat)
        lamb = math.radians(lon)
        x = a * math.cos(phi) * math.cos(lamb)
        y = a * math.cos(phi) * math.sin(lamb)
        z = b * math.sin(phi)
        puntos_latitud.append(go.Scatter3d(x=[x], y=[y], z=[z], mode='markers+text',
            marker=dict(size=6, color='orange'),
            text=[f"φ={lat}°, λ={lon}°"], textposition="top center", showlegend=False))

    # Agregar líneas de paralelo a las latitudes ingresadas
    paralelos = []
    for lat in [phi1_deg, phi2_deg]:
        lons = np.linspace(0, 2 * np.pi, 200)
        phi = math.radians(lat)
        x = a * np.cos(phi) * np.cos(lons)
        y = a * np.cos(phi) * np.sin(lons)
        z = np.full_like(lons, b * np.sin(phi))
        paralelos.append(go.Scatter3d(x=x, y=y, z=z, mode='lines', line=dict(color='purple', width=2), showlegend=False))

    # Agregar líneas de meridiano a las longitudes ingresadas
    meridianos = []
    for lon in [lambda1_deg, lambda2_deg]:
        lats = np.linspace(-np.pi / 2, np.pi / 2, 200)
        lamb = math.radians(lon)
        x = a * np.cos(lats) * np.cos(lamb)
        y = a * np.cos(lats) * np.sin(lamb)
        z = b * np.sin(lats)
        meridianos.append(go.Scatter3d(x=x, y=y, z=z, mode='lines', line=dict(color='orange', width=2), showlegend=False))

    fig = go.Figure(data=[elipsoide, ecuador, greenwich] + etiquetas + puntos_latitud + paralelos + meridianos, layout=layout)
    st.plotly_chart(fig, use_container_width=True)

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
        st.success(f"Área total del elipsoide: {area_total:,.6f} m²")
        st.info(f"Área total ≈ {area_total / 1e6:,.6f} km²")

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

    metodo = st.selectbox("Método de cálculo:", ["Exacto (ec. 3.129)", "Serie (ec. 3.133)"])

    if st.button("Calcular Área del Cuadrilátero"):
        if None in [phi1_deg, phi2_deg, lambda1_deg, lambda2_deg]:
            st.error("Por favor completa todas las coordenadas correctamente.")
        else:
            try:
                phi1 = math.radians(phi1_deg)
                phi2 = math.radians(phi2_deg)
                lambda1 = math.radians(lambda1_deg)
                lambda2 = math.radians(lambda2_deg)

                if metodo == "Exacto (ec. 3.129)":
                    area = calcular_area_exacta(phi1, phi2, lambda1, lambda2, b, e)
                else:
                    area = calcular_area_serie(phi1, phi2, lambda1, lambda2, b, e)
                st.info(f"**Área del cuadrilátero:**\n\n"
                       f" {area:.6f} m² \n\n"
                       f" {area / 1e6:.6f} km²")
                graficar_segmento(phi1_deg, phi2_deg, lambda1_deg, lambda2_deg, a, b)
            except Exception as e:
                st.error(f"Error: {e}")

if __name__ == "__main__":
    area_cuadrilatero_interface()
