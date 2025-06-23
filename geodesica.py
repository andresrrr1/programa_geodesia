import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np

def calcular_por_sube_baja(data):
    cotas = []
    dist_acum = []
    dist_total = 0
    ultima_cota_util = None
    ultima_vmas_util = None

    for i, fila in data.iterrows():
        punto = fila['Punto Visado']
        es_intermedia = "(Intermedia)" in str(punto)
        sube = fila['Sube']
        baja = fila['Baja']

        if i == 0:
            cota = fila['Cota Inicial']
            ultima_cota_util = cota
            ultima_vmas_util = fila['V+']
        elif es_intermedia:
            cota = ultima_cota_util + ultima_vmas_util - fila['V-']
        else:
            cota = ultima_cota_util + ultima_vmas_util - fila['V-']
            ultima_cota_util = cota
            ultima_vmas_util = fila['V+']

        dist_total += fila['Distancia']
        dist_acum.append(dist_total)
        cotas.append(cota)

    data['Cota por S/B'] = cotas
    data['Distancia Acum'] = dist_acum
    return data


def calcular_por_hi(data):
    hi_list = []
    cotas_hi = []
    hi_actual = None
    cota_util = None
    ultima_vmas_util = None

    for i in range(len(data)):
        punto = data.loc[i, 'Punto Visado']
        es_intermedia = "(Intermedia)" in str(punto)

        if i == 0:
            cota = data.loc[i, 'Cota Inicial']
            hi = cota + data.loc[i, 'V+']
            cota_util = cota
            ultima_vmas_util = data.loc[i, 'V+']
        elif es_intermedia:
            hi = hi_actual  
            cota = hi - data.loc[i, 'V-']
        else:
            cota = cota_util + ultima_vmas_util - data.loc[i, 'V-']
            hi = cota + data.loc[i, 'V+']
            cota_util = cota
            ultima_vmas_util = data.loc[i, 'V+']

        hi_actual = hi
        hi_list.append(np.nan if es_intermedia else round(hi, 3))
        cotas_hi.append(cota)

    hi_list[-1] = 0.0
    data['HI'] = hi_list
    data['Cota por HI'] = cotas_hi
    return data


def mostrar_perfil(data):
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=data['Distancia Acum'],
        y=data['Cota por S/B'],
        mode='lines+markers',
        marker=dict(color='green', size=8),
        line=dict(color='green', width=2),
        name="Cota S/B"
    ))
    fig.add_trace(go.Scatter(
        x=data['Distancia Acum'],
        y=data['Cota por HI'],
        mode='lines+markers',
        marker=dict(color='blue', size=8),
        line=dict(color='blue', width=2),
        name="Cota HI"
    ))
    for i, row in data.iterrows():
        fig.add_annotation(
            x=row['Distancia Acum'],
            y=row['Cota por HI'],
            text=row['Punto Visado'],
            showarrow=False,
            font=dict(size=10),
            align="right",
            opacity=0.8
        )
    fig.update_layout(
        title="Perfil de Cotas",
        xaxis_title="Distancia acumulada (m)",
        yaxis_title="Cota (m)",
        showlegend=True,
        template="plotly_white",
        margin=dict(l=40, r=40, t=40, b=40)
    )
    st.plotly_chart(fig, use_container_width=True)


def nivelacion_geodesica_streamlit():
    st.header("Nivelación Geodésica")
    st.markdown("### Ingreso de Datos por Estación")

    with st.form("form_datos"):
        num_estaciones = st.number_input("Número de estaciones", min_value=1, step=1, format="%d")
        data = []

        for i in range(num_estaciones):
            st.markdown(f"#### Estación {i+1}")
            cols = st.columns([1])
            with cols[0]:
                estacion = st.text_input("Estación", key=f"est_{i}")

            st.markdown("##### Puntos Visados")
            max_visados = 1   
            for j in range(max_visados):
                st.write(f"**Punto Visado {j+1}**")
                visado_cols = st.columns([6, 6, 6, 6, 6, 1, 1])
                punto_visado = visado_cols[0].text_input("Nombre", key=f"pv_{i}_{j}")
                vmas = visado_cols[1].text_input("V+", key=f"vmas_{i}_{j}")
                vmenos = visado_cols[2].text_input("V-", key=f"vmenos_{i}_{j}")
                distancia = visado_cols[3].text_input("Distancia (m)", key=f"dist_{i}_{j}")
                if i == 0 and j == 0:
                    cota_ini = visado_cols[4].text_input("Cota Inicial", key=f"cota_{i}_{j}")
                else:
                    cota_ini = None
                intermedia = st.checkbox("¿Vista Intermedia?", key=f"intermedia_{i}_{j}")

                
                if punto_visado.strip() == "":
                    continue

                if intermedia:
                    data.append({
                        "Estación": estacion,
                        "Punto Visado": punto_visado + " (Intermedia)",
                        "V+": vmas,
                        "V-": vmenos,
                        "Distancia": distancia,
                        "Cota Inicial": None
                    })
                    continue
                data.append({
                    "Estación": estacion,
                    "Punto Visado": punto_visado,
                    "V+": vmas,
                    "V-": vmenos,
                    "Distancia": distancia,
                    "Cota Inicial": cota_ini
                })
        submitted = st.form_submit_button("Calcular")

    if submitted:
        if not data:
            st.warning("Por favor, ingresa al menos un punto visado con todos los datos requeridos.")
            return

        df = pd.DataFrame(data)
        columnas_float = ["V+", "V-", "Distancia", "Cota Inicial"]
        for col in columnas_float:
            if col not in df.columns:
                st.error(f"Falta la columna '{col}' en los datos ingresados.")
                return
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0.0)
        if df['Cota Inicial'].astype(bool).sum() > 1:
            st.error("Solo se permite una cota inicial en el primer punto de la primera estación.")
            return

       
        subes = []
        bajas = []
        for i in range(len(df)):
            punto = df.loc[i, 'Punto Visado']
            es_intermedia = "(Intermedia)" in str(punto)
            if i == 0:
                subes.append(df.loc[i, 'V+'])
                bajas.append(0.0)
                ultima_vmas_util = df.loc[i, 'V+']
            elif es_intermedia:
                diferencia = ultima_vmas_util - df.loc[i, 'V-']
                if diferencia > 0:
                    subes.append(diferencia)
                    bajas.append(0.0)
                elif diferencia < 0:
                    subes.append(0.0)
                    bajas.append(abs(diferencia))
                else:
                    subes.append(0.0)
                    bajas.append(0.0)
            else:
                diferencia = ultima_vmas_util - df.loc[i, 'V-']
                if diferencia > 0:
                    subes.append(diferencia)
                    bajas.append(0.0)
                elif diferencia < 0:
                    subes.append(0.0)
                    bajas.append(abs(diferencia))
                else:
                    subes.append(0.0)
                    bajas.append(0.0)
                ultima_vmas_util = df.loc[i, 'V+']


        df['Sube'] = [np.nan if s == 0.0 else s for s in subes]
        df['Baja'] = [np.nan if b == 0.0 else b for b in bajas]

        df = calcular_por_sube_baja(df)
        df = calcular_por_hi(df)

        columnas_ordenadas = [
        "Estación", "Punto Visado", "V+", "V-", "HI", "Cota por HI",
        "Sube", "Baja", "Cota por S/B", "Distancia", "Distancia Acum"
        ]
        st.dataframe(df[columnas_ordenadas].style.format({
        "V+": "{:.2f}",
        "V-": "{:.2f}",
        "HI": "{:.2f}",
        "Cota por HI": "{:.2f}",
        "Sube": "{:.2f}",
        "Baja": "{:.2f}",
        "Cota por S/B": "{:.2f}",
        "Distancia": "{:.2f}",
        "Distancia Acum": "{:.1f}"
       }))

        st.subheader("Perfil de Cotas")
        mostrar_perfil(df)


if __name__ == "__main__":
    nivelacion_geodesica_streamlit()
