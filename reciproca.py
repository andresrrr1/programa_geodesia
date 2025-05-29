import streamlit as st
import math

def gms_to_decimal(g, m, s):
    try:
        return abs(float(g)) + float(m) / 60 + float(s) / 3600
    except:
        return None

def calcular_radios(phi_deg, alpha_deg, a, f):
    try:
        phi_rad = math.radians(float(phi_deg))
        alpha_rad = math.radians(float(alpha_deg))
        e2 = 2 * f - f ** 2
        N = a / math.sqrt(1 - e2 * math.sin(phi_rad) ** 2)
        rho = (a * (1 - e2)) / (1 - e2 * math.sin(phi_rad) ** 2)**1.5
        rho_alpha = (N * rho) / (N * math.cos(alpha_rad) ** 2 + rho * math.sin(alpha_rad) ** 2)
        return N, rho, rho_alpha, e2
    except:
        return None, None, None, None

def correccion_refraccion(i, o, S):
    try:
        if S > 5000:
            sin_1seg = math.sin(math.radians(1 / 3600))
            return (i - o) / (S * sin_1seg)
        else:
            return i - o
    except:
        return None

def reciproca_interface():
    st.title("Nivelación Trigonométrica Recíproca")

    datum = st.selectbox("Selecciona el Datum", ["WGS84", "GRS80", "Internacional"])
    if datum == "WGS84":
        a, finv = 6378137.0, 298.2572223563
    elif datum == "GRS80":
        a, finv = 6378137.0, 298.257222101
    else:
        a, finv = 6378388.0, 297.0
    f = 1 / finv

    st.markdown("### Ángulo Cenital Z₁")
    colz1 = st.columns(3)
    z1_g = colz1[0].text_input("Grados Z₁", value="")
    z1_m = colz1[1].text_input("Minutos Z₁", value="")
    z1_s = colz1[2].text_input("Segundos Z₁", value="")

    st.markdown("### Ángulo Cenital Z₂")
    colz2 = st.columns(3)
    z2_g = colz2[0].text_input("Grados Z₂", value="")
    z2_m = colz2[1].text_input("Minutos Z₂", value="")
    z2_s = colz2[2].text_input("Segundos Z₂", value="")

    st.markdown("### Latitud Geodésica φ")
    colf = st.columns(4)
    f_g = colf[0].text_input("Grados φ", value="")
    f_m = colf[1].text_input("Minutos φ", value="")
    f_s = colf[2].text_input("Segundos φ", value="")
    direccion_phi = colf[3].radio("Hemisferio", ["N", "S"])

    st.markdown("### Distancia S")
    tipo_S = st.radio("Forma de ingreso de la distancia:", ["Manual", "Desde coordenadas"])
    dE = dN = S = None

    if tipo_S == "Manual":
        S_input = st.text_input("Distancia S (m)", value="")
        if S_input.strip():
            try:
                S = float(S_input)
            except:
                st.warning("Distancia inválida")
    else:
        col_coords = st.columns(4)
        N1 = col_coords[0].text_input("Norte punto 1", value="")
        E1 = col_coords[1].text_input("Este punto 1", value="")
        N2 = col_coords[2].text_input("Norte punto 2", value="")
        E2 = col_coords[3].text_input("Este punto 2", value="")

        if all(x.strip() for x in [N1, E1, N2, E2]):
            try:
                N1, E1, N2, E2 = float(N1), float(E1), float(N2), float(E2)
                dN = N2 - N1
                dE = E2 - E1
                S = math.sqrt(dN**2 + dE**2)
                st.info(f"Distancia S calculada: {S:.4f} m")
                st.markdown(f"**ΔE:** {dE:.4f} m   **ΔN:** {dN:.4f} m")
            except:
                st.warning("Error en coordenadas")

    st.markdown("### Azimut α")
    tipo_alpha = st.radio("Forma de ingreso del azimut:", ["Manual", "Desde coordenadas"])
    alpha = None

    if tipo_alpha == "Manual":
        col_alpha = st.columns(3)
        a_g = col_alpha[0].text_input("Grados α", value="")
        a_m = col_alpha[1].text_input("Minutos α", value="")
        a_s = col_alpha[2].text_input("Segundos α", value="")
        if all(x.strip() for x in [a_g, a_m, a_s]):
            alpha = gms_to_decimal(a_g, a_m, a_s)
    else:
        if dE is not None and dN is not None:
            alpha = math.degrees(math.atan2(dE, dN))
            st.info(f"Ángulo α calculado automáticamente: {alpha:.6f} °")
        else:
            st.warning("Para calcular el azimut automáticamente, ingresa las coordenadas.")

    st.markdown("### Alturas y cota")
    H1 = st.text_input("Cota conocida H₁ (m)", value="")
    i1 = st.text_input("Altura instrumental en punto 1 (i₁)", value="")
    o2 = st.text_input("Altura de señal en punto 2 (o₂)", value="")
    i2 = st.text_input("Altura instrumental en punto 2 (i₂)", value="")
    o1 = st.text_input("Altura de señal en punto 1 (o₁)", value="")

    if st.button("🔍 Calcular cota H₂", type="primary"):
        try:
            Z1 = gms_to_decimal(z1_g, z1_m, z1_s)
            Z2 = gms_to_decimal(z2_g, z2_m, z2_s)
            phi = gms_to_decimal(f_g, f_m, f_s)
            if direccion_phi == "S":
                phi = -phi

            H1 = float(H1)
            i1 = float(i1)
            o2 = float(o2)
            i2 = float(i2)
            o1 = float(o1)

            C1_pp_seg = correccion_refraccion(i1, o2, S)
            C2_pp_seg = correccion_refraccion(i2, o1, S)

            C1_pp_deg = C1_pp_seg / 3600
            C2_pp_deg = C2_pp_seg / 3600

            Z1_corr = Z1 - abs(C1_pp_deg)
            Z2_corr = Z2 - abs(C2_pp_deg)
            alpha_corr = (Z2_corr - Z1_corr) / 2

            N, rho_m, rho_alpha, e2 = calcular_radios(phi, alpha, a, f)

            A = 1 + H1 / rho_alpha
            B = 1 + (S / (2 * rho_alpha)) * math.tan(math.radians(alpha_corr))
            C = 1 + (S ** 2) / (12 * rho_alpha ** 2)

            deltaH = S * math.tan(math.radians(alpha_corr)) * A * B * C
            H2 = H1 + deltaH + i1

            st.success(f"Cota final del punto H₂: {H2:.5f} m")
            st.write(f"ΔH: {deltaH:.5f} m")

            with st.expander("Detalles del cálculo"):
                st.markdown(f"**N** = {N:.6f} m")
                st.markdown(f"**ρₘ** = {rho_m:.6f} m")
                st.markdown(f"**ρₐ** = {rho_alpha:.6f} m")
                st.markdown(f"**Corrección A** = {A:.9f}")
                st.markdown(f"**Corrección B** = {B:.9f}")
                st.markdown(f"**Corrección C** = {C:.9f}")
                st.markdown(f"**C₁'' (segundos)** = {C1_pp_seg:.6f}")
                st.markdown(f"**C₂'' (segundos)** = {C2_pp_seg:.6f}")
        except:
            st.error("Verifique que todos los campos estén llenos.")

if __name__ == "__main__":
    reciproca_interface()
