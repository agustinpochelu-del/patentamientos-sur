import pandas as pd
import streamlit as st


def render(df, df_pat, df_modelos, df_ciudades):
    st.title("🔍 Detalle y exploración")

    if df.empty:
        st.warning("No hay datos para los filtros seleccionados.")
        return

    tab_tabla, tab_pivot, tab_calidad = st.tabs(
        ["📋 Tabla filtrada", "🧮 Tabla dinámica", "🩺 Calidad de datos"]
    )

    with tab_tabla:
        st.caption(f"{len(df):,} registros".replace(",", "."))
        busqueda = st.text_input("Buscar (localidad, modelo o marca)")
        view = df.copy()
        if busqueda:
            mask = (
                view["Localidad"].str.contains(busqueda, case=False, na=False)
                | view["Modelo"].str.contains(busqueda, case=False, na=False)
                | view["Marca"].str.contains(busqueda, case=False, na=False)
            )
            view = view[mask]

        cols_show = ["Periodo", "provincia_label", "Zona", "Localidad", "Marca", "Modelo", "tipo", "estado", "Valor"]
        view_display = view[cols_show].rename(columns={"provincia_label": "Provincia", "tipo": "Tipo"})
        view_display = view_display.sort_values("Periodo")
        st.dataframe(view_display, hide_index=True, use_container_width=True, height=480)

        csv = view_display.to_csv(index=False).encode("utf-8-sig")
        st.download_button(
            "⬇️ Descargar CSV filtrado", csv, "patentamientos_filtrado.csv", "text/csv"
        )

    with tab_pivot:
        st.markdown("Armá tu propia tabla cruzando dos dimensiones.")
        dims = {
            "Localidad": "Localidad", "Modelo": "Modelo", "Marca": "Marca",
            "Tipo": "tipo", "Provincia": "provincia_label", "Zona": "Zona",
            "Mes": "Periodo",
        }
        c1, c2 = st.columns(2)
        fila = c1.selectbox("Filas", list(dims.keys()), index=0)
        colu = c2.selectbox("Columnas", list(dims.keys()), index=6)

        if fila == colu:
            st.warning("Elegí dos dimensiones distintas.")
        else:
            d = df.copy()
            d["Filas"] = d["Periodo"].dt.strftime("%Y-%m") if dims[fila] == "Periodo" else d[dims[fila]]
            d["Columnas"] = d["Periodo"].dt.strftime("%Y-%m") if dims[colu] == "Periodo" else d[dims[colu]]

            pivot = d.pivot_table(
                index="Filas", columns="Columnas", values="Valor", aggfunc="sum", fill_value=0
            )
            pivot["Total"] = pivot.sum(axis=1)
            pivot = pivot.sort_values("Total", ascending=False)
            st.dataframe(pivot, use_container_width=True)

            csv_p = pivot.to_csv().encode("utf-8-sig")
            st.download_button("⬇️ Descargar tabla dinámica (CSV)", csv_p, "tabla_dinamica.csv", "text/csv")

    with tab_calidad:
        st.markdown(
            "Cruce contra las tablas auxiliares (`Modelos` y `Ciudades`) para "
            "detectar localidades o modelos que aparecen en *Tabla Pat* pero no "
            "están dados de alta en las tablas maestras."
        )

        loc_pat = set(df_pat["Localidad"].unique())
        loc_aux = set(df_ciudades["Localidad"].unique())
        loc_sin_match = sorted(loc_pat - loc_aux)

        mod_pat = set(df_pat["Modelo"].unique())
        mod_aux = set(df_modelos["Modelo"].unique())
        mod_sin_match = sorted(mod_pat - mod_aux)

        c1, c2 = st.columns(2)
        with c1:
            st.metric("Localidades sin match en 'Ciudades'", len(loc_sin_match))
            if loc_sin_match:
                st.dataframe(pd.DataFrame({"Localidad": loc_sin_match}), hide_index=True, use_container_width=True)
            else:
                st.success("Todas las localidades de Tabla Pat están en la tabla Ciudades. ✅")

        with c2:
            st.metric("Modelos sin match en 'Modelos'", len(mod_sin_match))
            if mod_sin_match:
                st.dataframe(pd.DataFrame({"Modelo": mod_sin_match[:200]}), hide_index=True, use_container_width=True)
                if len(mod_sin_match) > 200:
                    st.caption(f"... y {len(mod_sin_match) - 200} más.")
            else:
                st.success("Todos los modelos de Tabla Pat están en la tabla Modelos. ✅")

        st.divider()
        st.markdown("**Registros con valores negativos (ajustes / bajas):**")
        negativos = df_pat[df_pat["Valor"] < 0][
            ["Periodo", "Localidad", "Modelo", "Marca", "estado", "Valor"]
        ].sort_values("Periodo")
        st.dataframe(negativos, hide_index=True, use_container_width=True)
