import streamlit as st
import math


def gms_to_decimal(g, m, s, direccion):
    decimal = abs(g) + m / 60 + s / 3600
    return decimal if direccion == "N" else -decimal


def calcular_palpha(a, finv, lat_rad, azimut_rad):
    f = 1 / finv
    e2 = 2 * f - f ** 2
    sin_lat = math.sin(lat_rad)
    W = math.sqrt(1 - e2 * sin_lat ** 2)

    N = a / W
    M = a * (1 - e2) / (W ** 3)

    denominador = (N * math.cos(azimut_rad) ** 2) + (M * math.sin(azimut_rad) ** 2)
    palpha = (M * N) / denominador

    return palpha, N, M, e2


def calcular_nivelacion(Z1, S, H1, i, a, finv, latitud, azimut, metodo_k="fijo"):
    phi_rad = math.radians(latitud)
    alpha_rad = math.radians(azimut)
    rho, N, M, e2 = calcular_palpha(a, finv, phi_rad, alpha_rad)

    m = 0.071
    if metodo_k == "geom_completo":
        sen_1seg = math.sin(math.radians(1 / 3600))
        k = (S * (0.5 - m)) / (rho * sen_1seg)
    else:
        k = 0.429

    Z_corregido = 90 + k - Z1
    angulo_rad = math.radians(Z_corregido)

    A = 1 + H1 / rho
    B1 = 1 + (S / (2 * rho)) * math.tan(angulo_rad)
    C = 1 + (S ** 2) / (12 * rho ** 2)

    deltaH = S * math.tan(angulo_rad) * A * B1 * C
    H2 = H1 + deltaH + i
    return H2, deltaH, Z_corregido, rho, A, B1, C, k


def no_reciproca_interface():
    st.title("Nivelación Trigonométrica No Recíproca")

    datum = st.selectbox("Selecciona el Datum", ["WGS84", "GRS80", "Internacional"])
    if datum == "WGS84":
        a, finv = 6378137.0, 298.257223563
    elif datum == "GRS80":
        a, finv = 6378137.0, 298.257222101
    else:
        a, finv = 6378388.0, 297.0

    st.markdown("### Ángulo Cenital Z₁")
    colz1 = st.columns(3)
    z1_g = colz1[0].text_input("Grados:")
    z1_m = colz1[1].text_input("Minutos:")
    z1_s = colz1[2].text_input("Segundos:")

    st.markdown("### Latitud Geodésica ϕ")
    colf = st.columns(4)
    phi_g = colf[0].text_input("Grados ϕ:")
    phi_m = colf[1].text_input("Minutos ϕ:")
    phi_s = colf[2].text_input("Segundos ϕ:")
    direccion_phi = colf[3].radio("Hemisferio", ["N", "S"])

    st.markdown("### Azimut de visada α")
    cola = st.columns(3)
    alpha_g = cola[0].text_input("Grados α:")
    alpha_m = cola[1].text_input("Minutos α:")
    alpha_s = cola[2].text_input("Segundos α:")

    H1_str = st.text_input("Cota conocida H₁ (m):")
    i_str = st.text_input("Altura instrumental i (m):")

    tipo_S = st.radio("Forma de ingreso de la distancia:", ["Manual", "Desde coordenadas"])
    S = None
    if tipo_S == "Manual":
        S_str = st.text_input("Distancia horizontal S (m):")
        try:
            S = float(S_str)
        except:
            st.error("Ingresa una distancia válida.")
            return
    else:
        col_utm = st.columns(4)
        N1 = col_utm[0].text_input("Norte punto 1:")
        E1 = col_utm[1].text_input("Este punto 1:")
        N2 = col_utm[2].text_input("Norte punto 2:")
        E2 = col_utm[3].text_input("Este punto 2:")
        try:
            S = math.sqrt((float(N2) - float(N1)) ** 2 + (float(E2) - float(E1)) ** 2)
            st.info(f"Distancia calculada: {S:.4f} m")
        except:
            st.error("Verifica que todos los campos UTM estén correctamente llenos.")
            return

    o_opcion = st.radio("¿Altura del objetivo conocida?", ["No", "Sí"])
    o_str = None
    if o_opcion == "Sí":
        o_str = st.text_input("Altura del objetivo o (m):")

    opciones_k = {
        "fijo": "Corrección fija (k=0.429)",
        "geom_completo": "Corrección geométrica completa (k = S(0.5-m)/(ρₐ·sen(1''))"
    }
    metodo_k = st.radio("Método para corrección angular:", 
        options=list(opciones_k.keys()),
        format_func=lambda x: opciones_k[x])

    if st.button("🔍 Calcular cota H₂", type="primary"):
        try:
            Z1 = gms_to_decimal(float(z1_g), float(z1_m), float(z1_s), "N")
            phi = gms_to_decimal(float(phi_g), float(phi_m), float(phi_s), direccion_phi)
            azimut = float(alpha_g) + float(alpha_m)/60 + float(alpha_s)/3600
            H1 = float(H1_str)
            i = float(i_str)

            if o_opcion == "Sí" and o_str and S:
                o = float(o_str)
                if S > 5000:
                    sen_1seg = math.sin(math.radians(1 / 3600))
                    Cpp = abs((i - o) / (S * sen_1seg))
                else:
                    Cpp = abs(i - o)
               
                z1_total_seg = float(z1_g) * 3600 + float(z1_m) * 60 + float(z1_s)
                z1_corregido_seg = z1_total_seg - Cpp
                z1_g_corr = int(z1_corregido_seg // 3600)
                z1_m_corr = int((z1_corregido_seg % 3600) // 60)
                z1_s_corr = z1_corregido_seg % 60
                Z1 = gms_to_decimal(z1_g_corr, z1_m_corr, z1_s_corr, "N")
                st.info(f"Z₁ corregido: {z1_g_corr}° {z1_m_corr}′ {z1_s_corr:.3f}″")

            H2, deltaH, Z_corregido, rho, A, B1, C, k = calcular_nivelacion(Z1, S, H1, i, a, finv, phi, azimut, metodo_k)
            _, N, M, e2 = calcular_palpha(a, finv, math.radians(phi), math.radians(azimut))

            st.success(f"Cota final del punto H₂: {H2:.5f} m")
            st.write(f"ΔH (sin i): {deltaH:.5f} m")

            with st.expander("Detalles del cálculo"):
                st.markdown(f"**N (radio primer vertical)** = {N:.6f} m")
                st.markdown(f"**M (radio meridiano)** = {M:.6f} m")
                st.markdown(f"**ρₐ (radio de curvatura)** = {rho:.6f} m")
                st.markdown(f"**Corrección A** = {A:.9f}")
                st.markdown(f"**Corrección B₁** = {B1:.9f}")
                st.markdown(f"**Corrección C** = {C:.9f}")
        except:
            st.error("Verifica todos los campos ingresados.")

   
