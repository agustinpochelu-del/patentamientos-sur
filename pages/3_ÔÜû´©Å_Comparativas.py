import pandas as pd
import plotly.express as px
import streamlit as st

from utils import ensure_data_loaded, sidebar_filters, fmt_int, COLOR_PROVINCIA

st.set_page_config(page_title="Comparativas", page_icon="⚖️", layout="wide")
st.title("⚖️ Comparativas")

df_pat, df_modelos, df_ciudades = ensure_data_loaded()
df = sidebar_filters(df_pat)

if df.empty:
    st.warning("No hay datos para los filtros seleccionados.")
    st.stop()

# --- Provincia x Tipo de vehículo ----------------------------------------
st.subheader("Provincia vs. tipo de vehículo")
piv = df.groupby(["provincia_label", "tipo"], as_index=False)["Valor"].sum()
fig = px.bar(
    piv, x="provincia_label", y="Valor", color="tipo", barmode="stack",
    text="Valor",
)
fig.update_traces(textposition="inside")
fig.update_layout(height=460, xaxis_title="", yaxis_title="Patentamientos", legend_title="Tipo")
st.plotly_chart(fig, use_container_width=True)

st.divider()

# --- Zonas dentro de cada provincia --------------------------------------
st.subheader("Zonas dentro de cada provincia")
by_zona = df.groupby(["provincia_label", "Zona"], as_index=False)["Valor"].sum()
fig2 = px.bar(
    by_zona, x="provincia_label", y="Valor", color="Zona", barmode="group",
    text="Valor",
)
fig2.update_traces(textposition="outside")
fig2.update_layout(height=440, xaxis_title="", yaxis_title="Patentamientos", legend_title="Zona")
st.plotly_chart(fig2, use_container_width=True)

st.divider()

# --- Treemap jerárquico ----------------------------------------------------
st.subheader("Composición jerárquica: Provincia → Tipo → Marca")
tree = df.groupby(["provincia_label", "tipo", "Marca"], as_index=False)["Valor"].sum()
tree = tree[tree["Valor"] > 0]  # treemap no admite negativos
fig3 = px.treemap(
    tree, path=["provincia_label", "tipo", "Marca"], values="Valor",
    color="provincia_label", color_discrete_map=COLOR_PROVINCIA,
)
fig3.update_layout(height=550)
st.plotly_chart(fig3, use_container_width=True)

st.divider()

# --- Market share por marca, comparado entre provincias ------------------
st.subheader("Participación de marcas por provincia (Top 8 + Otras)")
prov_sel = st.multiselect(
    "Provincias a comparar", sorted(df["provincia_label"].unique()),
    default=sorted(df["provincia_label"].unique()),
)
if prov_sel:
    sub = df[df["provincia_label"].isin(prov_sel)]
    cols = st.columns(len(prov_sel))
    for col, prov in zip(cols, prov_sel):
        d = sub[sub["provincia_label"] == prov]
        g = d.groupby("Marca", as_index=False)["Valor"].sum().sort_values("Valor", ascending=False)
        top8 = g.head(8).copy()
        otras = g["Valor"].iloc[8:].sum()
        if otras > 0:
            top8 = pd.concat([top8, pd.DataFrame([{"Marca": "Otras", "Valor": otras}])], ignore_index=True)
        fig_p = px.pie(top8, names="Marca", values="Valor", hole=0.4, title=prov)
        fig_p.update_traces(textinfo="percent")
        fig_p.update_layout(height=380, showlegend=True)
        col.plotly_chart(fig_p, use_container_width=True)

st.divider()

# --- Tabla pivote Provincia x Mes -----------------------------------------
st.subheader("Tabla: Provincia x Mes")
from utils import month_label
df["Mes"] = df["Periodo"].apply(month_label)
mes_order = df[["Periodo", "Mes"]].drop_duplicates().sort_values("Periodo")["Mes"].tolist()
pivot = df.pivot_table(
    index="provincia_label", columns="Mes", values="Valor", aggfunc="sum", fill_value=0
)[mes_order]
pivot["Total"] = pivot.sum(axis=1)
st.dataframe(pivot, use_container_width=True)
