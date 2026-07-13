import pandas as pd
import plotly.express as px
import streamlit as st

from utils import ensure_data_loaded, sidebar_filters, month_label, COLOR_PROVINCIA

st.set_page_config(page_title="Evolución Temporal", page_icon="📈", layout="wide")
st.title("📈 Evolución Temporal")

df_pat, df_modelos, df_ciudades = ensure_data_loaded()
df = sidebar_filters(df_pat)

if df.empty:
    st.warning("No hay datos para los filtros seleccionados.")
    st.stop()

df["Mes"] = df["Periodo"].apply(month_label)
mes_order = (
    df[["Periodo", "Mes"]].drop_duplicates().sort_values("Periodo")["Mes"].tolist()
)

# --- Evolución total ----------------------------------------------------
st.subheader("Evolución mensual total")
monthly = df.groupby("Periodo", as_index=False)["Valor"].sum().sort_values("Periodo")
monthly["Mes"] = monthly["Periodo"].apply(month_label)
fig = px.line(monthly, x="Mes", y="Valor", markers=True, category_orders={"Mes": mes_order})
fig.update_traces(line_color="#1f77b4")
fig.update_layout(height=400, yaxis_title="Patentamientos", xaxis_title="")
st.plotly_chart(fig, use_container_width=True)

st.divider()

# --- Evolución por provincia ---------------------------------------------
st.subheader("Evolución por provincia")
by_prov = df.groupby(["Periodo", "provincia_label"], as_index=False)["Valor"].sum()
by_prov["Mes"] = by_prov["Periodo"].apply(month_label)
fig2 = px.line(
    by_prov, x="Mes", y="Valor", color="provincia_label", markers=True,
    category_orders={"Mes": mes_order}, color_discrete_map=COLOR_PROVINCIA,
)
fig2.update_layout(height=420, yaxis_title="Patentamientos", xaxis_title="", legend_title="Provincia")
st.plotly_chart(fig2, use_container_width=True)

st.divider()

# --- Evolución por tipo de vehículo --------------------------------------
st.subheader("Evolución por tipo de vehículo")
by_tipo = df.groupby(["Periodo", "tipo"], as_index=False)["Valor"].sum()
by_tipo["Mes"] = by_tipo["Periodo"].apply(month_label)
fig3 = px.line(
    by_tipo, x="Mes", y="Valor", color="tipo", markers=True,
    category_orders={"Mes": mes_order},
)
fig3.update_layout(height=420, yaxis_title="Patentamientos", xaxis_title="", legend_title="Tipo")
st.plotly_chart(fig3, use_container_width=True)

st.divider()

# --- Evolución de marcas/modelos seleccionados ----------------------------
st.subheader("Seguimiento de marcas o modelos específicos")
modo = st.radio("Comparar por:", ["Marca", "Modelo"], horizontal=True)
campo = "Marca" if modo == "Marca" else "Modelo"

opciones = df.groupby(campo)["Valor"].sum().sort_values(ascending=False).index.tolist()
default_sel = opciones[:5]
seleccion = st.multiselect(f"Elegí {modo.lower()}s a comparar", opciones, default=default_sel)

if seleccion:
    sub = df[df[campo].isin(seleccion)]
    by_sel = sub.groupby(["Periodo", campo], as_index=False)["Valor"].sum()
    by_sel["Mes"] = by_sel["Periodo"].apply(month_label)
    fig4 = px.line(
        by_sel, x="Mes", y="Valor", color=campo, markers=True,
        category_orders={"Mes": mes_order},
    )
    fig4.update_layout(height=440, yaxis_title="Patentamientos", xaxis_title="")
    st.plotly_chart(fig4, use_container_width=True)
else:
    st.info(f"Seleccioná al menos {'una marca' if modo == 'Marca' else 'un modelo'} para ver su evolución.")

st.divider()

# --- Comparación año contra año (si hay 2 años en el rango) --------------
df["Anio"] = df["Periodo"].dt.year
df["MesNum"] = df["Periodo"].dt.month
anios = sorted(df["Anio"].unique())

if len(anios) >= 2:
    st.subheader("Comparación interanual (mismos meses)")
    meses_comunes = sorted(
        set.intersection(*[set(df[df["Anio"] == a]["MesNum"]) for a in anios])
    )
    if meses_comunes:
        comp = df[df["MesNum"].isin(meses_comunes)]
        comp_g = comp.groupby(["Anio", "MesNum"], as_index=False)["Valor"].sum()
        comp_g["Mes"] = comp_g["MesNum"].apply(
            lambda m: ["ene","feb","mar","abr","may","jun","jul","ago","sep","oct","nov","dic"][m-1]
        )
        fig5 = px.bar(
            comp_g, x="Mes", y="Valor", color="Anio", barmode="group",
            category_orders={"Mes": ["ene","feb","mar","abr","may","jun","jul","ago","sep","oct","nov","dic"]},
        )
        fig5.update_layout(height=400, yaxis_title="Patentamientos", xaxis_title="")
        st.plotly_chart(fig5, use_container_width=True)
    else:
        st.info("No hay meses en común entre los años del rango seleccionado.")
else:
    st.caption("El rango de período seleccionado cubre un solo año — ampliá el rango para ver comparación interanual.")
