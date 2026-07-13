import pandas as pd
import plotly.express as px
import streamlit as st

from utils import ensure_data_loaded, sidebar_filters, fmt_int, month_label, COLOR_PROVINCIA

st.set_page_config(
    page_title="Patentamientos Sur",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("🚗 Patentamientos — Chubut, Río Negro y Santa Cruz")
st.caption("Panel de análisis de patentamientos por localidad y modelo — región Sur")

df_pat, df_modelos, df_ciudades = ensure_data_loaded()
df = sidebar_filters(df_pat)

if df.empty:
    st.warning("No hay datos para los filtros seleccionados.")
    st.stop()

# --- KPIs -------------------------------------------------------------
total = df["Valor"].sum()
n_localidades = df["Localidad"].nunique()
n_modelos = df["Modelo"].nunique()
marca_lider = df.groupby("Marca")["Valor"].sum().idxmax()
prov_lider = df.groupby("provincia_label")["Valor"].sum().idxmax()

c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Patentamientos totales", fmt_int(total))
c2.metric("Localidades activas", n_localidades)
c3.metric("Modelos distintos", n_modelos)
c4.metric("Marca líder", marca_lider)
c5.metric("Provincia líder", prov_lider)

st.divider()

# --- Evolución mensual + participación por provincia -------------------
left, right = st.columns([2, 1])

with left:
    st.subheader("Evolución mensual")
    monthly = df.groupby("Periodo", as_index=False)["Valor"].sum().sort_values("Periodo")
    monthly["Mes"] = monthly["Periodo"].apply(month_label)
    fig = px.bar(monthly, x="Mes", y="Valor", text="Valor")
    fig.update_traces(marker_color="#1f77b4", textposition="outside")
    fig.update_layout(yaxis_title="Patentamientos", xaxis_title="", height=420)
    st.plotly_chart(fig, use_container_width=True)

with right:
    st.subheader("Participación por provincia")
    by_prov = df.groupby("provincia_label", as_index=False)["Valor"].sum()
    fig2 = px.pie(
        by_prov, names="provincia_label", values="Valor", hole=0.45,
        color="provincia_label", color_discrete_map=COLOR_PROVINCIA,
    )
    fig2.update_traces(textinfo="percent+label")
    fig2.update_layout(height=420, showlegend=False)
    st.plotly_chart(fig2, use_container_width=True)

st.divider()

# --- Top 10 localidades y top 10 modelos -------------------------------
col1, col2 = st.columns(2)

with col1:
    st.subheader("Top 10 localidades")
    top_loc = (
        df.groupby("Localidad", as_index=False)["Valor"].sum()
        .sort_values("Valor", ascending=False).head(10)
    )
    fig3 = px.bar(top_loc.sort_values("Valor"), x="Valor", y="Localidad", orientation="h")
    fig3.update_traces(marker_color="#2ca02c")
    fig3.update_layout(height=380, xaxis_title="Patentamientos", yaxis_title="")
    st.plotly_chart(fig3, use_container_width=True)

with col2:
    st.subheader("Top 10 modelos")
    top_mod = (
        df.groupby("Modelo", as_index=False)["Valor"].sum()
        .sort_values("Valor", ascending=False).head(10)
    )
    fig4 = px.bar(top_mod.sort_values("Valor"), x="Valor", y="Modelo", orientation="h")
    fig4.update_traces(marker_color="#ff7f0e")
    fig4.update_layout(height=380, xaxis_title="Patentamientos", yaxis_title="")
    st.plotly_chart(fig4, use_container_width=True)

st.divider()
st.markdown(
    "Usá el menú de la izquierda (**Evolución temporal**, **Rankings**, "
    "**Comparativas**, **Detalle**) para profundizar el análisis. "
    "Los filtros del sidebar se mantienen entre páginas."
)
