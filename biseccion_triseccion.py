
import streamlit as st
import math

def gms_to_decimal(g, m, s):
    return g + m/60 + s/3600


def rad_to_gms(theta_rad):
    deg_total = math.degrees(theta_rad)
    d = int(deg_total)
    m = int((deg_total - d) * 60)
    s = (deg_total - d - m/60) * 3600
    return d, m, s


def biseccion_interface():
    st.header("Bisección Geodésica")
    st.markdown("---")
    
    # — Entradas —
    NA_str  = st.text_input("NA (Norte de A)")
    EA_str  = st.text_input("EA (Este de A)")
    NB_str  = st.text_input("NB (Norte de B)")
    EB_str  = st.text_input("EB (Este de B)")
    
    st.markdown("∠ α en A ")
    c1, c2, c3 = st.columns(3)
    with c1:
        ag = st.text_input("Grados", key="ag")
    with c2:
        am = st.text_input("Minutos", key="am")
    with c3:
        as_ = st.text_input("Segundos", key="as")
        
    st.markdown("∠ β en B ")
    d1, d2, d3 = st.columns(3)
    with d1:
        bg = st.text_input("Grados", key="bg")
    with d2:
        bm = st.text_input("Minutos", key="bm")
    with d3:
        bs = st.text_input("Segundos", key="bs")
    
    if st.button("🔍 Calcular P"):
        # — Validación y conversión —
        campos = {
            "NA": NA_str, "EA": EA_str,
            "NB": NB_str, "EB": EB_str,
            "α gr": ag, "α min": am, "α seg": as_,
            "β gr": bg, "β min": bm, "β seg": bs
        }
        errores = [k for k,v in campos.items() if v.strip()=="" or not v.replace(".","",1).isdigit()]
        if errores:
            st.error(f"Faltan o no son numéricos: {', '.join(errores)}")
            return
        
        NA = float(NA_str); EA = float(EA_str)
        NB = float(NB_str); EB = float(EB_str)
        alpha = gms_to_decimal(float(ag), float(am), float(as_))
        beta  = gms_to_decimal(float(bg), float(bm), float(bs))
        
        # — Conversión a radianes —
        alpha_rad = math.radians(alpha)
        beta_rad  = math.radians(beta)
        rho_rad   = math.pi - (alpha_rad + beta_rad)
        
        if abs(math.sin(rho_rad)) < 1e-8:
            st.error("ρ ≈ 0°: α + β ≈ 180°, la bisección no es válida.")
            return
        
        # — Cálculo —
        dN   = NB - NA
        dE   = EB - EA
        AB   = math.hypot(dN, dE)
        azAB = math.atan2(dE, dN)
        
        AP   = (math.sin(beta_rad) / math.sin(rho_rad)) * AB
        azAP = azAB - alpha_rad
        
        NP = NA + AP * math.cos(azAP)
        EP = EA + AP * math.sin(azAP)
        
        st.markdown("Coordenadas de P")
        st.write(f"Nᴾ = **{NP:.8f}** m")
        st.write(f"Eᴾ = **{EP:.8f}** m")

    if st.button("🔙 Volver"):
        st.experimental_rerun()




def triseccion_interface():
    st.header(" Trisección Geodésica")
    st.markdown("---")

    metodo = st.radio("Elige variante:", ["Método A", "Método B"])

    NA_str = st.text_input("NA (Norte de A)", key="t_NA")
    EA_str = st.text_input("EA (Este de A)", key="t_EA")
    NB_str = st.text_input("NB (Norte de B)", key="t_NB")
    EB_str = st.text_input("EB (Este de B)", key="t_EB")
    NC_str = st.text_input("NC (Norte de C)", key="t_NC")
    EC_str = st.text_input("EC (Este de C)", key="t_EC")

    st.markdown("∠BPC = x")
    d1, d2, d3 = st.columns(3)
    with d1: g2 = st.text_input("Grados", key="p2g")
    with d2: m2 = st.text_input("Minutos", key="p2m")
    with d3: s2 = st.text_input("Segundos", key="p2s")

    st.markdown("∠CPA = y")
    b1, b2, b3 = st.columns(3)
    with b1: g3 = st.text_input("Grados", key="p3g")
    with b2: m3 = st.text_input("Minutos", key="p3m")
    with b3: s3 = st.text_input("Segundos", key="p3s")

    st.markdown("∠APB = z")
    c1, c2, c3 = st.columns(3)
    with c1: g1 = st.text_input("Grados", key="p1g")
    with c2: m1 = st.text_input("Minutos", key="p1m")
    with c3: s1 = st.text_input("Segundos", key="p1s")

    if not st.button("🔍 Calcular P"):
        return

    # Validación de entradas
    for k, v in {
        "NA": NA_str, "EA": EA_str, "NB": NB_str, "EB": EB_str,
        "NC": NC_str, "EC": EC_str,
        "x gr": g2, "x min": m2, "x seg": s2,
        "y gr": g3, "y min": m3, "y seg": s3,
        "z gr": g1, "z min": m1, "z seg": s1
    }.items():
        if v.strip() == "" or not v.replace(".", "", 1).replace("-", "", 1).isdigit():
            st.error(f"Falta o no es numérico: {k}")
            return

    NA, EA = float(NA_str), float(EA_str)
    NB, EB = float(NB_str), float(EB_str)
    NC, EC = float(NC_str), float(EC_str)
    # Ángulos en grados decimales y radianes
    x = gms_to_decimal(float(g2), float(m2), float(s2))
    y = gms_to_decimal(float(g3), float(m3), float(s3))
    z = gms_to_decimal(float(g1), float(m1), float(s1))
    xr, yr, zr = map(math.radians, (x, y, z))

    # Lados de ABC
    AB = math.hypot(NB - NA, EB - EA)
    BC = math.hypot(NC - NB, EC - EB)
    CA = math.hypot(NC - NA, EC - EA)

    if metodo == "Método A":
        # 1) Ángulo total en P entre A y C
        p_hat = z + x
        pr = math.radians(p_hat)

        # 2) Ángulos interiores de △ABC usando ley de cosenos
        A_hat = math.acos((AB**2 + CA**2 - BC**2) / (2 * AB * CA))
        B_hat = math.acos((AB**2 + BC**2 - CA**2) / (2 * AB * BC))
        C_hat = math.pi - (A_hat + B_hat)

        # 3) Constante k = (senÂ · BC) / (senĈ · AB)
        k = (math.sin(A_hat) * BC) / (math.sin(C_hat) * AB)

        # 4) Calcular p̂₂ usando: p̂₂ = arctan [sen(p̂) / (k + cos(p̂))]
        p2_hat = math.atan2(math.sin(pr), k + math.cos(pr))

        # 5) Calcular p̂₁ = p̂ − p̂₂
        p1_hat = pr - p2_hat

        # 6) Longitud AP por Ley de Senos en △ABP:
        # AP / sin(B̂) = AB / sin(p̂₁)  ->  AP = (sin(B̂) / sin(p̂₁)) * AB
        AP = (math.sin(B_hat) / math.sin(p1_hat)) * AB

        # 7) Azimut de A→B y dirección A→P
        azAB = math.atan2(EB - EA, NB - NA)
        azAP = azAB - A_hat

        # 8) Desplazamientos en N y E
        dNP = AP * math.cos(azAP)
        dEP = AP * math.sin(azAP)

        # 9) Coordenadas finales de P
        NP = NA + dNP
        EP = EA + dEP

        # 10) Mostrar ángulos p̂₁ y p̂₂ en G·M·S
        a1_g, a1_m, a1_s = rad_to_gms(p1_hat)
        a2_g, a2_m, a2_s = rad_to_gms(p2_hat)
        st.write(f"p̂₁ = {math.degrees(p1_hat):.6f}° = {a1_g}°{a1_m}′{a1_s:.2f}″")
        st.write(f"p̂₂ = {math.degrees(p2_hat):.6f}° = {a2_g}°{a2_m}′{a2_s:.2f}″")
        st.write(f"AP = **{AP:.6f}** m")

    else:
        # Tu código de Método B queda igual aquí (no lo reescribo)
        a = math.atan((EC - EA)/(NC - NA)) - math.atan((EB - EA)/(NB - NA))
        b = math.atan((EA - EB)/(NA - NB)) - math.atan((EC - EB)/(NC - NB))
        c = math.atan((EB - EC)/(NB - NC)) - math.atan((EA - EC)/(NA - NC))
        K1 = 1.0/(1/math.tan(a) - 1/math.tan(xr))
        K2 = 1.0/(1/math.tan(b) - 1/math.tan(yr))
        K3 = 1.0/(1/math.tan(c) - 1/math.tan(zr))
        Ksum = K1 + K2 + K3
        NP = (K1*NA + K2*NB + K3*NC)/Ksum
        EP = (K1*EA + K2*EB + K3*EC)/Ksum

    # Salida común
    st.markdown("### 📍 Coordenadas de P")
    st.write(f"Nᴾ = **{NP:.6f}** m     Eᴾ = **{EP:.6f}** m")

    if st.button("🔙 Volver"):
        st.experimental_rerun()







