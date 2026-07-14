import plotly.express as px
import streamlit as st

from utils import (
    fmt_int, month_label, COLOR_PROVINCIA,
    generar_resumen_reglas, get_anthropic_api_key, generate_ai_analysis,
    get_gemini_api_key, generate_ai_analysis_gemini,
)


def render(df, df_bruto, df_neto, df_modelos, df_ciudades):
    st.title("🚗 Patentamientos — Chubut, Río Negro y Santa Cruz")
    st.caption("Panel de análisis de patentamientos por localidad y modelo — región Sur")

    if df.empty:
        st.warning("No hay datos para los filtros seleccionados.")
        return

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

    # --- Volumen Global vs. Real (efecto Hertz) ---------------------------
    bruto_total = df_bruto["Valor"].sum() if not df_bruto.empty else 0
    neto_total = df_neto["Valor"].sum() if not df_neto.empty else 0
    ajuste = bruto_total - neto_total
    if ajuste > 0:
        st.caption(
            "💰 **Volumen Global vs. Real** — desde marzo/abril 2025, Hertz patenta "
            "vehículos bajo un régimen provincial favorable que en su mayoría no "
            "circula en la provincia. El panel usa el volumen que elegiste en el "
            "sidebar; acá va la comparación completa:"
        )
        h1, h2, h3 = st.columns(3)
        h1.metric("Volumen Global (bruto)", fmt_int(bruto_total))
        h2.metric("Volumen Real (neto)", fmt_int(neto_total))
        h3.metric(
            "Ajuste por Hertz", f"-{fmt_int(ajuste)}",
            delta=f"-{ajuste / bruto_total * 100:.0f}% del bruto" if bruto_total else None,
            delta_color="inverse",
        )

    st.divider()

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

    # --- Resumen narrativo automático (siempre disponible, sin costo) -----
    st.subheader("📝 Resumen")
    st.markdown(generar_resumen_reglas(df, df_bruto, df_neto))

    # --- Análisis más profundo con IA (opcional, requiere API key propia) --
    with st.expander("🤖 Análisis más profundo con IA"):
        claude_key = get_anthropic_api_key()
        gemini_key = get_gemini_api_key()

        if not claude_key and not gemini_key:
            st.info(
                "Para usar esta función necesitás tu propia API key de alguno de "
                "estos proveedores (o de ambos, para poder elegir):\n\n"
                "**Claude (Anthropic)**\n"
                "1. Conseguila en [console.anthropic.com](https://console.anthropic.com).\n"
                "2. En Streamlit Cloud → **⋮ → Settings → Secrets**:\n"
                "```toml\nANTHROPIC_API_KEY = \"tu-key-aca\"\n```\n\n"
                "**Gemini (Google)**\n"
                "1. Conseguila en [aistudio.google.com/app/apikey]"
                "(https://aistudio.google.com/app/apikey).\n"
                "2. En Streamlit Cloud → **⋮ → Settings → Secrets**:\n"
                "```toml\nGEMINI_API_KEY = \"tu-key-aca\"\n```\n\n"
                "Guardá — la app se reinicia sola. Para probarlo en tu computadora, "
                "agregá la(s) misma(s) línea(s) a `.streamlit/secrets.toml` "
                "(nunca lo subas a GitHub — ya está excluido en el `.gitignore`)."
            )
        else:
            opciones = []
            if claude_key:
                opciones.append("Claude (Anthropic)")
            if gemini_key:
                opciones.append("Gemini (Google)")

            if len(opciones) > 1:
                proveedor = st.radio("Proveedor de IA", opciones, horizontal=True, key="f_proveedor_ia")
            else:
                proveedor = opciones[0]
                st.caption(f"Usando **{proveedor}** (es el único con API key configurada).")

            if st.button("Generar análisis con IA"):
                with st.spinner(f"Analizando los datos con {proveedor.split(' ')[0]}..."):
                    try:
                        if proveedor.startswith("Claude"):
                            texto = generate_ai_analysis(df, claude_key, df_bruto, df_neto)
                        else:
                            texto = generate_ai_analysis_gemini(df, gemini_key, df_bruto, df_neto)
                        st.session_state["ai_analysis"] = texto
                        st.session_state["ai_analysis_n"] = len(df)
                        st.session_state["ai_analysis_provider"] = proveedor
                    except Exception as e:
                        st.error(f"No se pudo generar el análisis: {e}")

            if "ai_analysis" in st.session_state:
                if st.session_state.get("ai_analysis_n") != len(df):
                    st.caption(
                        "⚠️ Cambiaste los filtros desde que se generó este análisis — "
                        "puede no reflejar la vista actual. Generalo de nuevo si querés."
                    )
                st.caption(f"Generado con {st.session_state.get('ai_analysis_provider', '')}")
                st.markdown(st.session_state["ai_analysis"])

    st.divider()
    st.markdown(
        "Usá el menú de la izquierda (**Evolución Temporal**, **Rankings**, "
        "**Comparativas**, **Detalle**) para profundizar el análisis. "
        "Los filtros del sidebar se mantienen siempre, en todas las páginas."
    )
