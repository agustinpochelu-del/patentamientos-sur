import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from utils import month_label, COLOR_PROVINCIA


def render(df, df_bruto=None, df_neto=None):
    st.title("📈 Evolución Temporal")

    if df.empty:
        st.warning("No hay datos para los filtros seleccionados.")
        return

    df = df.copy()
    df["Mes"] = df["Periodo"].apply(month_label)
    mes_order = df[["Periodo", "Mes"]].drop_duplicates().sort_values("Periodo")["Mes"].tolist()

    st.subheader("Evolución mensual total")
    monthly = df.groupby("Periodo", as_index=False)["Valor"].sum().sort_values("Periodo")
    monthly["Mes"] = monthly["Periodo"].apply(month_label)
    fig = px.line(monthly, x="Mes", y="Valor", markers=True, category_orders={"Mes": mes_order})
    fig.update_traces(line_color="#1f77b4")
    fig.update_layout(height=400, yaxis_title="Patentamientos", xaxis_title="")
    st.plotly_chart(fig, use_container_width=True)

    st.divider()

    # --- Volumen Global vs. Real (efecto Hertz) ----------------------------
    if df_bruto is not None and df_neto is not None and not df_bruto.empty:
        st.subheader("Volumen Global vs. Real (efecto Hertz)")
        st.caption(
            "Desde marzo/abril de 2025, Hertz patenta vehículos bajo un régimen "
            "provincial favorable que en su mayoría no circula en la provincia. "
            "Este gráfico compara el volumen tal cual se registra (bruto) contra "
            "el volumen neteando ese efecto (real)."
        )
        b = df_bruto.groupby("Periodo", as_index=False)["Valor"].sum().sort_values("Periodo")
        n = df_neto.groupby("Periodo", as_index=False)["Valor"].sum().sort_values("Periodo")
        b["Mes"] = b["Periodo"].apply(month_label)
        n["Mes"] = n["Periodo"].apply(month_label)
        mes_order_hz = b[["Periodo", "Mes"]].drop_duplicates().sort_values("Periodo")["Mes"].tolist()

        fig_hz = go.Figure()
        fig_hz.add_trace(go.Scatter(x=b["Mes"], y=b["Valor"], mode="lines+markers",
                                     name="Global (bruto)", line=dict(color="#d62728")))
        fig_hz.add_trace(go.Scatter(x=n["Mes"], y=n["Valor"], mode="lines+markers",
                                     name="Real (neto de Hertz)", line=dict(color="#1f77b4")))
        fig_hz.update_layout(
            height=420, yaxis_title="Patentamientos", xaxis_title="",
            xaxis=dict(categoryorder="array", categoryarray=mes_order_hz),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        )
        st.plotly_chart(fig_hz, use_container_width=True)

        st.divider()

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
