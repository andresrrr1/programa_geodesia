import streamlit as st
import pandas as pd
import plotly.graph_objects as go

def calcular_altura_instrumental(data):
    cotas = []
    cotas_hi = []
    dist_acum = []

    ultima_hi = None
    dist_total = 0

    for i, fila in data.iterrows():
        estacion = fila['Estación']
        punto_visado = fila['Punto Visado']
        vmas = fila['V+']
        vmenos = fila['V-']
        distancia = fila['Distancia']

        if i == 0:
            hi = float(fila['Cota Inicial'])
        else:
            hi = cotas[-1] + vmas - vmenos

        cota = hi - vmenos
        ultima_hi = hi
        dist_total += distancia

        cotas_hi.append(hi)
        cotas.append(cota)
        dist_acum.append(dist_total)

    data['Cota HI'] = cotas_hi
    data['Cota'] = cotas
    data['Distancia Acum'] = dist_acum

    return data


def mostrar_perfil(data):
    # Crear figura de Plotly
    fig = go.Figure()

    # Agregar trazado de línea
    fig.add_trace(go.Scatter(
        x=data['Distancia Acum'],
        y=data['Cota'],
        mode='lines+markers',
        marker=dict(color='blue', size=8),
        line=dict(color='blue', width=2),
        name="Perfil de Cotas"
    ))

    # Agregar etiquetas de puntos
    for i, row in data.iterrows():
        fig.add_annotation(
            x=row['Distancia Acum'],
            y=row['Cota'],
            text=row['Punto Visado'],
            showarrow=False,
            font=dict(size=10),
            align="right",
            opacity=0.8
        )

    # Configurar layout
    fig.update_layout(
        title="Perfil de Cotas - Altura Instrumental",
        xaxis_title="Distancia acumulada (m)",
        yaxis_title="Cota (m)",
        showlegend=True,
        template="plotly_white",
        margin=dict(l=40, r=40, t=40, b=40)
    )

    # Mostrar gráfico en Streamlit
    st.plotly_chart(fig, use_container_width=True)

def altura_instrumental_streamlit():
    st.title("Nivelación Geodésica")
    st.markdown("### Ingreso de Datos por Estación")

    with st.form("form_datos"):
        num_puntos = st.number_input("Número de estaciones (puntos visados)", min_value=1, step=1, format="%d")
        data = []

        for i in range(num_puntos):
            st.markdown(f"#### Estación {i+1}")
            cols = st.columns(6)
            estacion = cols[0].text_input("Estación", key=f"est_{i}")
            punto_visado = cols[1].text_input("Punto Visado", key=f"pv_{i}")
            vmas = cols[2].number_input("V+", step=0.01, key=f"vmas_{i}")
            vmenos = cols[3].number_input("V-", step=0.01, key=f"vmenos_{i}")
            distancia = cols[4].number_input("Distancia (m)", step=0.1, key=f"dist_{i}")
            cota_ini = cols[5].number_input("Cota Inicial", step=0.01, key=f"cota_{i}") if i == 0 else None

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
        df = pd.DataFrame(data)
        df_calculado = calcular_altura_instrumental(df)
        st.subheader("📋 Cartera de Cálculos")
        st.dataframe(df_calculado)

        st.subheader("📈 Perfil de Cotas")
        mostrar_perfil(df_calculado)

# Ejecutar el módulo
if __name__ == "__main__":
    altura_instrumental_streamlit()
