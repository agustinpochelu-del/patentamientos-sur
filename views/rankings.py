import pandas as pd
import plotly.express as px
import streamlit as st


def render(df):
    st.title("🏆 Rankings")

    if df.empty:
        st.warning("No hay datos para los filtros seleccionados.")
        return

    top_n = st.slider("Cantidad a mostrar (Top N)", 5, 30, 10)

    tab_loc, tab_mod, tab_marca, tab_tipo = st.tabs(
        ["📍 Localidades", "🚙 Modelos", "🏷️ Marcas", "🚚 Tipo de vehículo"]
    )

    def ranking_bar(data: pd.DataFrame, campo: str, color: str):
        g = (
            data.groupby(campo, as_index=False)["Valor"].sum()
            .sort_values("Valor", ascending=False).head(top_n)
        )
        g["Ranking"] = range(1, len(g) + 1)
        fig = px.bar(
            g.sort_values("Valor"), x="Valor", y=campo, orientation="h",
            text="Valor",
        )
        fig.update_traces(marker_color=color, textposition="outside")
        fig.update_layout(height=max(350, 28 * len(g)), xaxis_title="Patentamientos", yaxis_title="")
        st.plotly_chart(fig, use_container_width=True)
        st.dataframe(
            g[["Ranking", campo, "Valor"]].rename(columns={"Valor": "Patentamientos"}),
            hide_index=True, use_container_width=True,
        )

    with tab_loc:
        st.subheader(f"Top {top_n} localidades")
        ranking_bar(df, "Localidad", "#1f77b4")

    with tab_mod:
        st.subheader(f"Top {top_n} modelos")
        ranking_bar(df, "Modelo", "#ff7f0e")

    with tab_marca:
        st.subheader(f"Top {top_n} marcas")
        ranking_bar(df, "Marca", "#2ca02c")

    with tab_tipo:
        st.subheader("Distribución por tipo de vehículo")
        g = df.groupby("tipo", as_index=False)["Valor"].sum().sort_values("Valor", ascending=False)
        fig = px.bar(g, x="tipo", y="Valor", text="Valor", color="tipo")
        fig.update_traces(textposition="outside")
        fig.update_layout(height=420, xaxis_title="", yaxis_title="Patentamientos", showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
        st.dataframe(
            g.rename(columns={"tipo": "Tipo", "Valor": "Patentamientos"}),
            hide_index=True, use_container_width=True,
        )

    st.divider()

    st.subheader("Modelo más patentado en cada localidad")
    top_por_loc = (
        df.groupby(["Localidad", "Modelo"], as_index=False)["Valor"].sum()
        .sort_values(["Localidad", "Valor"], ascending=[True, False])
        .groupby("Localidad").head(1)
        .sort_values("Valor", ascending=False)
        .rename(columns={"Valor": "Patentamientos"})
    )
    st.dataframe(top_por_loc, hide_index=True, use_container_width=True)
