import streamlit as st
import numpy as np
import plotly.graph_objects as go
import plotly.express as px


def obtener_parametros_elipsoide(nombre_elipsoide):
    if nombre_elipsoide == 'WGS84':
        a = 6378137.0
        f = 1 / 298.2572223563
    elif nombre_elipsoide == 'GRS 1980':
        a = 6378137.0
        f = 1 / 298.257222101
    elif nombre_elipsoide == 'Internacional':
        a = 6378388.0
        f = 1 / 297.0
    else: 
        a = 0.0
        f = 0.0
    return a, f

def gms_a_decimales(g, m, s):
    """Convierte grados, minutos, segundos a grados decimales."""
    if s >= 59.999999999:
        s = 0.0
        m += 1
    if m == 60:
        m = 0
        g += 1
    return abs(g) + m / 60 + s / 3600

def decimales_a_gms(decimal):
    signo = -1 if decimal < 0 else 1
    decimal = abs(decimal)
    g = int(decimal)
    m = int((decimal - g) * 60)
    s = (decimal - g - m / 60) * 3600

    if s >= 59.999999999:
        s = 0.0
        m += 1
    if m == 60:
        m = 0
        g += 1
    return signo * g, m, s

def calcular_coeficientes_serie(e2_val):
    E0_coeff = 1 + (3/4)*e2_val + (45/64)*e2_val**2 + (175/256)*e2_val**3 + \
               (11025/16384)*e2_val**4 + (43659/65536)*e2_val**5

    E2_coeff = (3/8)*e2_val + (15/32)*e2_val**2 + (525/1024)*e2_val**3 + \
               (2205/4096)*e2_val**4 + (72765/65536)*e2_val**5

    E4_coeff = (15/256)*e2_val**2 + (105/1024)*e2_val**3 + (2205/4096)*e2_val**4 + \
               (10395/16384)*e2_val**5

    E6_coeff = (35/3072)*e2_val**3 + (315/12288)*e2_val**4 + (31185/131072)*e2_val**5

    E8_coeff = (315/131072)*e2_val**4 + (3465/524288)*e2_val**5

    E10_coeff = (693/131072)*e2_val**5

    return E0_coeff, E2_coeff, E4_coeff, E6_coeff, E8_coeff, E10_coeff

def calcular_S_phi(phi_rad, a, e2, E0, E2, E4, E6, E8, E10):
    longitud = a * (1 - e2) * (
        E0 * phi_rad
        - E2 * np.sin(2 * phi_rad)
        + E4 * np.sin(4 * phi_rad)
        - E6 * np.sin(6 * phi_rad)
        + E8 * np.sin(8 * phi_rad)
        - E10 * np.sin(10 * phi_rad)
    )
    return longitud

def calcular_longitud_arco_paralelo(phi_deg, lambda1_deg, lambda2_deg, a, e2):
    phi_rad = np.radians(phi_deg)
    N = a / np.sqrt(1 - e2 * np.sin(phi_rad)**2)
    delta_lambda_rad = np.radians(abs(lambda2_deg - lambda1_deg))
    longitud = N * np.cos(phi_rad) * delta_lambda_rad
    return longitud

def lat_lon_a_cartesiano(lat_deg, lon_deg, a, b):
    """Convierte coordenadas geográficas a cartesianas en el elipsoide"""
    lat_rad = np.radians(lat_deg)
    lon_rad = np.radians(lon_deg)
    
    
    e2 = 1 - (b**2 / a**2)
    N = a / np.sqrt(1 - e2 * np.sin(lat_rad)**2)
    
    x = N * np.cos(lat_rad) * np.cos(lon_rad)
    y = N * np.cos(lat_rad) * np.sin(lon_rad)
    z = N * (1 - e2) * np.sin(lat_rad)
    
    return x, y, z

def crear_meridianos_paralelos(a, b, num_meridianos=24, num_paralelos=18):
    """Crea las líneas de meridianos y paralelos del elipsoide"""
    meridianos = []
    paralelos = []
    
    
    longitudes = np.linspace(-180, 180, num_meridianos, endpoint=False)
    latitudes_meridiano = np.linspace(-90, 90, 100)
    
    for lon in longitudes:
        x_coords = []
        y_coords = []
        z_coords = []
        for lat in latitudes_meridiano:
            x, y, z = lat_lon_a_cartesiano(lat, lon, a, b)
            x_coords.append(x)
            y_coords.append(y)
            z_coords.append(z)
        meridianos.append((np.array(x_coords), np.array(y_coords), np.array(z_coords)))
    
    
    latitudes = np.linspace(-75, 75, num_paralelos)  
    longitudes_paralelo = np.linspace(-180, 180, 100)
    
    for lat in latitudes:
        x_coords = []
        y_coords = []
        z_coords = []
        for lon in longitudes_paralelo:
            x, y, z = lat_lon_a_cartesiano(lat, lon, a, b)
            x_coords.append(x)
            y_coords.append(y)
            z_coords.append(z)
        paralelos.append((np.array(x_coords), np.array(y_coords), np.array(z_coords)))
    
    return meridianos, paralelos

def crear_arco_meridiano(lat1_deg, lat2_deg, lon_deg, a, b, num_puntos=100):
    """Crea puntos para el arco de meridiano"""
    latitudes = np.linspace(lat1_deg, lat2_deg, num_puntos)
    longitudes = np.full(num_puntos, lon_deg)
    
    x_coords = []
    y_coords = []
    z_coords = []
    
    for lat in latitudes:
        x, y, z = lat_lon_a_cartesiano(lat, lon_deg, a, b)
        x_coords.append(x)
        y_coords.append(y)
        z_coords.append(z)
    
    return np.array(x_coords), np.array(y_coords), np.array(z_coords)

def crear_arco_paralelo(lat_deg, lon1_deg, lon2_deg, a, b, num_puntos=100):
    """Crea puntos para el arco de paralelo"""
    longitudes = np.linspace(lon1_deg, lon2_deg, num_puntos)
    latitudes = np.full(num_puntos, lat_deg)
    
    x_coords = []
    y_coords = []
    z_coords = []
    
    for lon in longitudes:
        x, y, z = lat_lon_a_cartesiano(lat_deg, lon, a, b)
        x_coords.append(x)
        y_coords.append(y)
        z_coords.append(z)
    
    return np.array(x_coords), np.array(y_coords), np.array(z_coords)

def calcular_zoom_automatico(lat1, lat2, lon1, lon2):
    """Calcula el zoom basado en la distancia entre puntos"""
    diferencia_lat = abs(lat2 - lat1)
    diferencia_lon = abs(lon2 - lon1)
    
    distancia_max = max(diferencia_lat, diferencia_lon)
    
    if distancia_max < 0.01:  
        return dict(x=0.3, y=0.3, z=0.2)  
    elif distancia_max < 0.1:  
        return dict(x=0.8, y=0.8, z=0.5) 
    else:
        return dict(x=1.8, y=1.8, z=1.2)  


def crear_grafica_3d(a, b, puntos_principales=None, arco_coords=None, tipo_arco="meridiano", 
                     titulo="Elipsoide Terrestre", ancho_arco=10, color_arco=None, zoom_eye=None):
    
    fig = go.Figure()

    fig.add_trace(go.Scatter3d(
    x=[0], y=[0], z=[b],  
    mode='markers+text',
    marker=dict(size=8, color='darkblue'),
    text=['Polo N'],
    textposition="top center",
    textfont=dict(size=12, color='darkblue', family="Arial Black"),
    name="Polo Norte",
    showlegend=False,
    hoverinfo='skip'
 ))

    fig.add_trace(go.Scatter3d(
    x=[0], y=[0], z=[-b],  
    mode='markers+text',
    marker=dict(size=8, color='darkblue'),
    text=['Polo S'],
    textposition="bottom center",
    textfont=dict(size=12, color='darkblue', family="Arial Black"),
    name="Polo Sur",
    showlegend=False,
    hoverinfo='skip'
 ))
    meridianos, paralelos = crear_meridianos_paralelos(a, b)
    
    for i, (x_mer, y_mer, z_mer) in enumerate(meridianos):
        fig.add_trace(go.Scatter3d(
            x=x_mer, y=y_mer, z=z_mer,
            mode='lines',
            line=dict(color='lightblue', width=2),
            name="Meridianos" if i == 0 else "",
            showlegend=True if i == 0 else False,
            hoverinfo='skip'
        ))

    for i, (x_par, y_par, z_par) in enumerate(paralelos):
        fig.add_trace(go.Scatter3d(
            x=x_par, y=y_par, z=z_par,
            mode='lines',
            line=dict(color='lightgreen', width=2),
            name="Paralelos" if i == 0 else "",
            showlegend=True if i == 0 else False,
            hoverinfo='skip'
        ))
    
    longitudes_ecuador = np.linspace(-180, 180, 100)
    x_ecuador = []
    y_ecuador = []
    z_ecuador = []
    for lon in longitudes_ecuador:
        x, y, z = lat_lon_a_cartesiano(0, lon, a, b)
        x_ecuador.append(x)
        y_ecuador.append(y)
        z_ecuador.append(z)
    
    fig.add_trace(go.Scatter3d(
        x=x_ecuador, y=y_ecuador, z=z_ecuador,
        mode='lines',
        line=dict(color='red', width=4),
        name="Ecuador",
        hoverinfo='skip'
    ))
    
    
    latitudes_greenwich = np.linspace(-90, 90, 100)


    x_greenwich_0 = []
    y_greenwich_0 = []
    z_greenwich_0 = []
    for lat in latitudes_greenwich:
     x, y, z = lat_lon_a_cartesiano(lat, 0, a, b)
     x_greenwich_0.append(x)
     y_greenwich_0.append(y)
     z_greenwich_0.append(z)

    x_greenwich_180 = []
    y_greenwich_180 = []
    z_greenwich_180 = []
    for lat in latitudes_greenwich:
     x, y, z = lat_lon_a_cartesiano(lat, 180, a, b)
     x_greenwich_180.append(x)
     y_greenwich_180.append(y)
     z_greenwich_180.append(z)

    fig.add_trace(go.Scatter3d(
     x=x_greenwich_0, y=y_greenwich_0, z=z_greenwich_0,
     mode='lines',
     line=dict(color='red', width=4),
     name="Meridiano 0°",
     hoverinfo='skip'
    ))

    fig.add_trace(go.Scatter3d(
     x=x_greenwich_180, y=y_greenwich_180, z=z_greenwich_180,
     mode='lines',
     line=dict(color='red', width=4),
     name="Meridiano 180°",
     showlegend=False,
     hoverinfo='skip'
    ))
  


    if puntos_principales:
        for i, (nombre, lat, lon) in enumerate(puntos_principales):
           x, y, z = lat_lon_a_cartesiano(lat, lon, a, b)
        
        
           g_lat, m_lat, s_lat = decimales_a_gms(lat)
        
        
           etiqueta_gms = f"P{i+1} ({g_lat:+.0f}°{m_lat:02.0f}'{s_lat:04.2f}\")"
        
           fig.add_trace(go.Scatter3d(
             x=[x], y=[y], z=[z],
             mode='markers+text',
             marker=dict(size=6, color=['orange', 'purple'][i], 
                       line=dict(width=1, color='white')),
             text=[etiqueta_gms],
             textposition="top center",
             textfont=dict(size=10, color='black'),
             name=etiqueta_gms,
             hovertemplate=f"<b>{etiqueta_gms}</b><extra></extra>"
            ))
    
    
    if arco_coords:
        x_arco, y_arco, z_arco = arco_coords
        color_arco = 'gold' if tipo_arco == "meridiano" else 'magenta'
        nombre_arco = f"Arco de {tipo_arco.title()}"
        
        fig.add_trace(go.Scatter3d(
            x=x_arco, y=y_arco, z=z_arco,
            mode='lines',
            line=dict(color=color_arco, width=10),
            name=nombre_arco,
            hoverinfo='skip'
        ))
    
    
    fig.update_layout(
        title=dict(
            text=titulo,
            x=0.5,
            font=dict(size=16, color='darkblue')
        ),
        scene=dict(
            xaxis=dict(
                title="X (metros)",
                showgrid=False,
                showticklabels=False,
                showline=False,
                zeroline=False
            ),
            yaxis=dict(
                title="Y (metros)",
                showgrid=False,
                showticklabels=False,
                showline=False,
                zeroline=False
            ),
            zaxis=dict(
                title="Z (metros)",
                showgrid=False,
                showticklabels=False,
                showline=False,
                zeroline=False
            ),
            aspectmode='data',
            camera=dict(
                eye=dict(x=1.8, y=1.8, z=1.2)
            ),
            bgcolor='rgba(240,248,255,0.8)'
        ),
        width=900,
        height=700,
        margin=dict(l=0, r=0, t=40, b=0),
        legend=dict(
            x=0.02,
            y=0.98,
            bgcolor="rgba(255,255,255,0.8)"
        )
    )
    
    return fig

def calcular_longitud_arco_interface():
    st.header("Cálculo de Longitud de Arco con Visualización 3D")
    st.markdown("---")

    tipo_arco = st.radio(
        "Selecciona el tipo de arco a calcular:",
        ["Arco de Meridiano", "Arco de Paralelo"],
        key="tipo_arco_selector"
    )

    st.subheader("Parámetros del Elipsoide")
    elipsoide_seleccionado = st.selectbox(
        "Selecciona el Elipsoide:",
        ['WGS84', 'GRS 1980', 'Internacional', 'Manual'],
        key="elipsoide_selector_lam"
    )

    a_elipsoide, f_elipsoide = 0.0, 0.0
    e2_elipsoide = 0.0

    if elipsoide_seleccionado == 'Manual':
        col1, col2 = st.columns(2)
        a_str = col1.text_input("Semieje mayor a (m):", value="", key="a_manual_lam")
        f_inv_str = col2.text_input("Achatamiento (1/f):", value="", key="f_inv_manual_lam")

        try:
            a_elipsoide = float(a_str)
            f_inv = float(f_inv_str)
            if f_inv == 0:
                st.error("El valor de 1/f no puede ser cero.")
                return
            f_elipsoide = 1 / f_inv
            e2_elipsoide = 2 * f_elipsoide - f_elipsoide**2

        except ValueError:
            st.warning("Ingrese valores numéricos válidos para 'a' y '1/f'.")
            return
    else:
        a_elipsoide, f_elipsoide = obtener_parametros_elipsoide(elipsoide_seleccionado)
        e2_elipsoide = 2 * f_elipsoide - f_elipsoide**2

    
    b_elipsoide = a_elipsoide * np.sqrt(1 - e2_elipsoide)

    st.markdown("---")

    if tipo_arco == "Arco de Meridiano":
        col_dir1, col_dir2 = st.columns(2)
        direccion_phi1 = col_dir1.radio("Dirección φ₁:", ['Norte (N)', 'Sur (S)'], key="dir_phi1_lam_mer")
        direccion_phi2 = col_dir2.radio("Dirección φ₂:", ['Norte (N)', 'Sur (S)'], key="dir_phi2_lam_mer")

        signo_phi1 = 1 if direccion_phi1.startswith('N') else -1
        signo_phi2 = 1 if direccion_phi2.startswith('N') else -1

        formato_entrada_mer = st.radio("Formato de entrada:", ['GMS', 'Decimal'], key="formato_lat_lam_mer")

        phi1_deg_abs = 0.0
        phi2_deg_abs = 0.0

        if formato_entrada_mer == 'Decimal':
            col1, col2 = st.columns(2)
            phi1_str = col1.text_input("Valor absoluto φ₁ (decimal):", value="", key="phi1_dec_lam_mer")
            phi2_str = col2.text_input("Valor absoluto φ₂ (decimal):", value="", key="phi2_dec_lam_mer")

            try:
                phi1_deg_abs = float(phi1_str)
                phi2_deg_abs = float(phi2_str)

                if not (0 <= phi1_deg_abs <= 90) or not (0 <= phi2_deg_abs <= 90):
                    st.error("Las latitudes deben estar entre 0 y 90 grados para el valor absoluto.")
                    return

            except ValueError:
                st.warning("Ingrese valores numéricos válidos para las latitudes decimales.")
                return

        else: 
            st.markdown("**Latitud inicial φ₁**")
            col1, col2, col3 = st.columns(3)
            g1_str = col1.text_input("Grados φ₁:", value="", key="g1_lam_mer")
            m1_str = col2.text_input("Minutos φ₁:", value="", key="m1_lam_mer")
            s1_str = col3.text_input("Segundos φ₁:", value="", key="s1_lam_mer")

            st.markdown("**Latitud final φ₂**")
            col4, col5, col6 = st.columns(3)
            g2_str = col4.text_input("Grados φ₂:", value="", key="g2_lam_mer")
            m2_str = col5.text_input("Minutos φ₂:", value="", key="m2_lam_mer")
            s2_str = col6.text_input("Segundos φ₂:", value="", key="s2_lam_mer")

            try:
                g1 = int(g1_str) if g1_str else 0
                m1 = int(m1_str) if m1_str else 0
                s1 = float(s1_str) if s1_str else 0.0

                g2 = int(g2_str) if g2_str else 0
                m2 = int(m2_str) if m2_str else 0
                s2 = float(s2_str) if s2_str else 0.0

                phi1_deg_abs = gms_a_decimales(g1, m1, s1)
                phi2_deg_abs = gms_a_decimales(g2, m2, s2)

                if not (0 <= g1 <= 90 and 0 <= m1 < 60 and 0 <= s1 < 60) or \
                   not (0 <= g2 <= 90 and 0 <= m2 < 60 and 0 <= s2 < 60):
                    st.error("Valores GMS inválidos. Grados deben ser 0-90, minutos y segundos 0-59.999...")
                    return

            except ValueError:
                st.warning("Ingrese valores numéricos válidos para grados, minutos y segundos.")
                return

        phi1_final_deg = signo_phi1 * phi1_deg_abs
        phi2_final_deg = signo_phi2 * phi2_deg_abs

       
        lon_meridiano = 0.0

        st.markdown("---")

        if st.button("🔍 Calcular Longitud", type="primary"):
            if phi1_final_deg == phi2_final_deg:
                st.warning("Las latitudes inicial y final son iguales. La longitud del arco será cero.")
                st.info("Longitud del arco de meridiano: 0.00000000 metros (0.00000000 kilómetros)")
                return

            E0, E2, E4, E6, E8, E10 = calcular_coeficientes_serie(e2_elipsoide)

            phi1_rad = np.radians(phi1_final_deg)
            phi2_rad = np.radians(phi2_final_deg)

            S1 = calcular_S_phi(phi1_rad, a_elipsoide, e2_elipsoide, E0, E2, E4, E6, E8, E10)
            S2 = calcular_S_phi(phi2_rad, a_elipsoide, e2_elipsoide, E0, E2, E4, E6, E8, E10)

            longitud_calculada = abs(S2 - S1)

            st.success(
            f"**Longitud del arco de meridiano:**\n\n"
            f" **{longitud_calculada:.8f} metros**\n\n"
            f" **{longitud_calculada/1000:.8f} kilómetros**"
           )
            
            st.subheader("🌍 Visualización 3D")
            
            puntos_principales = [
                (f"P1 (φ₁={phi1_final_deg:.3f}°)", phi1_final_deg, lon_meridiano),
                (f"P2 (φ₂={phi2_final_deg:.3f}°)", phi2_final_deg, lon_meridiano)
            ]
            
            arco_coords = crear_arco_meridiano(phi1_final_deg, phi2_final_deg, lon_meridiano, a_elipsoide, b_elipsoide)
            
            diferencia_lat = abs(phi2_final_deg - phi1_final_deg)
            if diferencia_lat < 2.0:  
              ancho_linea = 15
              color_arco = 'yellow'
            else:
              ancho_linea = 10
              color_arco = 'gold'
            
            fig = crear_grafica_3d(
                a_elipsoide, b_elipsoide, 
                puntos_principales, 
                arco_coords, 
                "meridiano",
                f"Arco de Meridiano - {elipsoide_seleccionado}"
            )
            
            st.plotly_chart(fig, use_container_width=True)

            with st.expander("Ver Coeficientes de la Serie"):
                st.markdown(f"**E₀ =** {E0:.15f}")
                st.markdown(f"**E₂ =** {E2:.15f}")
                st.markdown(f"**E₄ =** {E4:.15f}")
                st.markdown(f"**E₆ =** {E6:.15f}")
                st.markdown(f"**E₈ =** {E8:.15f}")
                st.markdown(f"**E₁₀ =** {E10:.15f}")

    elif tipo_arco == "Arco de Paralelo":
        col_lon_dir1, col_lon_dir2, col_lat = st.columns(3)
        direccion_lambda1 = col_lon_dir1.radio("Dirección λ₁:", ['Este (E)', 'Oeste (O)'], key="dir_lon1_par")
        direccion_lambda2 = col_lon_dir2.radio("Dirección λ₂:", ['Este (E)', 'Oeste (O)'], key="dir_lon2_par")
        direccion_phi_par = col_lat.radio("Dirección φ:", ['Norte (N)', 'Sur (S)'], key="dir_phi_par")
        signo_phi_par = 1 if direccion_phi_par.startswith('N') else -1

        formato_entrada_par = st.radio("Formato de entrada:", ['GMS', 'Decimal'], key="formato_lat_lon_par")

        phi_deg_abs_par = 0.0
        lambda1_deg_abs_par = 0.0
        lambda2_deg_abs_par = 0.0

        if formato_entrada_par == 'Decimal':
            col1, col2, col3 = st.columns(3)
            phi_str_par = col1.text_input("Valor absoluto φ (decimal):", value="", key="phi_dec_par")
            lambda1_str_par = col2.text_input("Valor absoluto λ₁ (decimal):", value="", key="lambda1_dec_par")
            lambda2_str_par = col3.text_input("Valor absoluto λ₂ (decimal):", value="", key="lambda2_dec_par")

            try:
                phi_deg_abs_par = float(phi_str_par)
                lambda1_deg_abs_par = float(lambda1_str_par)
                lambda2_deg_abs_par = float(lambda2_str_par)

                if not (0 <= phi_deg_abs_par <= 90) or not (0 <= lambda1_deg_abs_par <= 180) or not (0 <= lambda2_deg_abs_par <= 180):
                    st.error("Valores decimales inválidos. Latitud 0-90, Longitud 0-180 (valor absoluto).")
                    return

            except ValueError:
                st.warning("Ingrese valores numéricos válidos para las latitudes/longitudes decimales.")
                return

        else: 
            st.markdown("**Latitud φ**")
            col1, col2, col3 = st.columns(3)
            g_par_str = col1.text_input("Grados φ:", value="", key="g_par")
            m_par_str = col2.text_input("Minutos φ:", value="", key="m_par")
            s_par_str = col3.text_input("Segundos φ:", value="", key="s_par")

            st.markdown("**Longitud λ₁**")
            col4, col5, col6 = st.columns(3)
            gl1_par_str = col4.text_input("Grados λ₁:", value="", key="gl1_par")
            ml1_par_str = col5.text_input("Minutos λ₁:", value="", key="ml1_par")
            sl1_par_str = col6.text_input("Segundos λ₁:", value="", key="sl1_par")

            st.markdown("**Longitud λ₂**")
            col7, col8, col9 = st.columns(3)
            gl2_par_str = col7.text_input("Grados λ₂:", value="", key="gl2_par")
            ml2_par_str = col8.text_input("Minutos λ₂:", value="", key="ml2_par")
            sl2_par_str = col9.text_input("Segundos λ₂:", value="", key="sl2_par")

            try:
                g_par = int(g_par_str) if g_par_str else 0
                m_par = int(m_par_str) if m_par_str else 0
                s_par = float(s_par_str) if s_par_str else 0.0

                gl1_par = int(gl1_par_str) if gl1_par_str else 0
                ml1_par = int(ml1_par_str) if ml1_par_str else 0
                sl1_par = float(sl1_par_str) if sl1_par_str else 0.0

                gl2_par = int(gl2_par_str) if gl2_par_str else 0
                ml2_par = int(ml2_par_str) if ml2_par_str else 0
                sl2_par = float(sl2_par_str) if sl2_par_str else 0.0

                phi_deg_abs_par = gms_a_decimales(g_par, m_par, s_par)
                lambda1_deg_abs_par = gms_a_decimales(gl1_par, ml1_par, sl1_par)
                lambda2_deg_abs_par = gms_a_decimales(gl2_par, ml2_par, sl2_par)

                if not (0 <= g_par <= 90 and 0 <= m_par < 60 and 0 <= s_par < 60) or \
                   not (0 <= gl1_par <= 180 and 0 <= ml1_par < 60 and 0 <= sl1_par < 60) or \
                   not (0 <= gl2_par <= 180 and 0 <= ml2_par < 60 and 0 <= sl2_par < 60):
                    st.error("Valores GMS inválidos. Latitud Grados 0-90, Longitud Grados 0-180, minutos y segundos 0-59.999...")
                    return

            except ValueError:
                st.warning("Ingrese valores numéricos válidos para grados, minutos y segundos.")
                return

        phi_final_deg_par = signo_phi_par * phi_deg_abs_par

        signo_lambda1 = 1 if direccion_lambda1.startswith('E') else -1
        signo_lambda2 = 1 if direccion_lambda2.startswith('E') else -1

        lambda1_final_deg_par = signo_lambda1 * lambda1_deg_abs_par
        lambda2_final_deg_par = signo_lambda2 * lambda2_deg_abs_par

        st.markdown("---")

        if st.button("🔍 Calcular Longitud", type="primary"):
            if phi_final_deg_par == 90 or phi_final_deg_par == -90:
                st.warning("En los polos (latitud ±90°), la longitud de un arco de paralelo es cero.")
                st.info("Longitud del arco de paralelo: 0.00000000 metros (0.00000000 kilómetros)")
                return

            if lambda1_final_deg_par == lambda2_final_deg_par:
                st.warning("Las longitudes inicial y final son iguales. La longitud del arco será cero.")
                st.info("Longitud del arco de paralelo: 0.00000000 metros (0.00000000 kilómetros)")
                return

            longitud_calculada_par = calcular_longitud_arco_paralelo(
                phi_final_deg_par, lambda1_final_deg_par, lambda2_final_deg_par, a_elipsoide, e2_elipsoide
            )

            st.success(
                f"**Longitud del arco de paralelo:**\n\n"
                f" **{longitud_calculada_par:.8f} metros**\n\n"
                f" **{longitud_calculada_par/1000:.8f} kilómetros**"
            )

           
            st.subheader("🌍 Visualización 3D")
            
            puntos_principales = [
                (f"P1 (λ₁={lambda1_final_deg_par:.3f}°)", phi_final_deg_par, lambda1_final_deg_par),
                (f"P2 (λ₂={lambda2_final_deg_par:.3f}°)", phi_final_deg_par, lambda2_final_deg_par)
            ]
            
            arco_coords = crear_arco_paralelo(phi_final_deg_par, lambda1_final_deg_par, lambda2_final_deg_par, a_elipsoide, b_elipsoide)
            
            fig = crear_grafica_3d(
                a_elipsoide, b_elipsoide, 
                puntos_principales, 
                arco_coords, 
                "paralelo",
                f"Arco de Paralelo - {elipsoide_seleccionado}"
            )
            
            st.plotly_chart(fig, use_container_width=True)

if __name__ == "__main__":
    st.set_page_config(
        page_title="Calculadora de Arcos Geodésicos",
        page_icon="🌍",
        layout="wide"
    )
    calcular_longitud_arco_interface()
