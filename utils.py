"""
Funciones compartidas por toda la app: lectura del Excel (por tablas
nombradas, para que funcione con archivos actualizados del mismo formato),
limpieza de datos y filtros de sidebar reutilizables entre páginas.
"""

import io
import openpyxl
import pandas as pd
import streamlit as st

# ---------------------------------------------------------------------------
# Constantes
# ---------------------------------------------------------------------------

PROVINCIA_LABELS = {
    "Chubut": "Chubut",
    "Rio negro": "Río Negro",
    "Santa Cruz": "Santa Cruz",
}

TIPO_FIX = {
    "autos": "Autos",
    "PIck-Up": "Pick-Up",
}

COLOR_PROVINCIA = {
    "Chubut": "#1f77b4",
    "Río Negro": "#ff7f0e",
    "Santa Cruz": "#2ca02c",
}


# ---------------------------------------------------------------------------
# Lectura del Excel por tabla nombrada (robusto a filas/columnas agregadas)
# ---------------------------------------------------------------------------

def _read_named_table(wb: openpyxl.Workbook, table_name: str) -> pd.DataFrame | None:
    """Busca una Tabla de Excel por su nombre en todas las hojas y la
    devuelve como DataFrame, usando la primera fila del rango como header."""
    for ws in wb.worksheets:
        if table_name in ws.tables:
            ref = ws.tables[table_name].ref
            data = ws[ref]
            rows = [[cell.value for cell in row] for row in data]
            if not rows:
                return None
            header, body = rows[0], rows[1:]
            return pd.DataFrame(body, columns=header)
    return None


def _clean_pat(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.columns = [str(c).strip() for c in df.columns]

    for col in ["Localidad", "Modelo", "Marca", "tipo", "provincia", "Zona", "estado"]:
        df[col] = df[col].astype(str).str.strip()

    df["tipo"] = df["tipo"].replace(TIPO_FIX)
    df["provincia_label"] = df["provincia"].map(PROVINCIA_LABELS).fillna(df["provincia"])
    df["Periodo"] = pd.to_datetime(df["Periodo"], errors="coerce")
    df["Valor"] = pd.to_numeric(df["Valor"], errors="coerce").fillna(0).astype(int)
    df = df.dropna(subset=["Periodo"])
    return df


def _clean_aux(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.columns = [str(c).strip() for c in df.columns]
    for col in df.columns:
        if df[col].dtype == object:
            df[col] = df[col].astype(str).str.strip()
    return df


@st.cache_data(show_spinner=False)
def load_workbook_data(file_bytes: bytes):
    """Carga y limpia las 3 tablas de interés a partir de los bytes del
    archivo subido. Cacheado por contenido del archivo."""
    wb = openpyxl.load_workbook(io.BytesIO(file_bytes), data_only=True)

    df_pat = _read_named_table(wb, "PaT_Ciudad")
    df_modelos = _read_named_table(wb, "Modelos")
    df_ciudades = _read_named_table(wb, "Ciudades")

    missing = [n for n, d in [("PaT_Ciudad", df_pat), ("Modelos", df_modelos),
                               ("Ciudades", df_ciudades)] if d is None]
    if missing:
        raise ValueError(
            "No encontré la(s) tabla(s) nombrada(s): " + ", ".join(missing) +
            ". Verificá que el archivo tenga el mismo formato (mismos nombres "
            "de Tabla de Excel: PaT_Ciudad, Modelos, Ciudades)."
        )

    df_pat = _clean_pat(df_pat)
    df_modelos = _clean_aux(df_modelos)
    df_ciudades = _clean_aux(df_ciudades)

    return df_pat, df_modelos, df_ciudades


def ensure_data_loaded():
    """Muestra el file_uploader en el sidebar (si hace falta) y garantiza
    que los dataframes estén en session_state. Para usar al principio de
    cada página. Devuelve (df_pat, df_modelos, df_ciudades)."""

    with st.sidebar:
        st.markdown("### 📁 Datos")
        uploaded = st.file_uploader(
            "Excel de patentamientos (mismo formato)",
            type=["xlsx"],
            key="uploader",
            help="Debe contener las tablas 'PaT_Ciudad' (hoja Tabla Pat) y "
                 "'Modelos' / 'Ciudades' (hoja auxiliares).",
        )
        if uploaded is not None:
            try:
                file_bytes = uploaded.getvalue()
                if st.session_state.get("_file_hash") != hash(file_bytes):
                    df_pat, df_modelos, df_ciudades = load_workbook_data(file_bytes)
                    st.session_state["df_pat"] = df_pat
                    st.session_state["df_modelos"] = df_modelos
                    st.session_state["df_ciudades"] = df_ciudades
                    st.session_state["_file_hash"] = hash(file_bytes)
                    st.session_state["file_name"] = uploaded.name
                st.success(f"✅ {st.session_state.get('file_name', 'Archivo')} cargado")
            except Exception as e:
                st.error(f"Error al leer el archivo: {e}")

    if "df_pat" not in st.session_state:
        st.info("👈 Subí el Excel de patentamientos en la barra lateral para empezar.")
        st.stop()

    return (
        st.session_state["df_pat"],
        st.session_state["df_modelos"],
        st.session_state["df_ciudades"],
    )


# ---------------------------------------------------------------------------
# Filtros de sidebar reutilizables (comparten estado entre páginas)
# ---------------------------------------------------------------------------

def sidebar_filters(df: pd.DataFrame) -> pd.DataFrame:
    st.sidebar.markdown("### 🔎 Filtros")

    min_p, max_p = df["Periodo"].min(), df["Periodo"].max()
    periodos = sorted(df["Periodo"].unique())
    periodo_labels = [pd.Timestamp(p).strftime("%Y-%m") for p in periodos]
    label_to_ts = dict(zip(periodo_labels, periodos))

    sel_labels = st.sidebar.select_slider(
        "Período",
        options=periodo_labels,
        value=(periodo_labels[0], periodo_labels[-1]),
        key="f_periodo",
    )
    p_ini, p_fin = label_to_ts[sel_labels[0]], label_to_ts[sel_labels[1]]

    provincias = sorted(df["provincia_label"].unique())
    sel_prov = st.sidebar.multiselect("Provincia", provincias, default=provincias, key="f_prov")

    zonas = sorted(df["Zona"].unique())
    sel_zona = st.sidebar.multiselect("Zona", zonas, default=zonas, key="f_zona")

    tipos = sorted(df["tipo"].unique())
    sel_tipo = st.sidebar.multiselect("Tipo de vehículo", tipos, default=tipos, key="f_tipo")

    marcas = sorted(df["Marca"].unique())
    sel_marca = st.sidebar.multiselect(
        "Marca (vacío = todas)", marcas, default=[], key="f_marca"
    )

    localidades = sorted(df[df["provincia_label"].isin(sel_prov)]["Localidad"].unique())
    sel_loc = st.sidebar.multiselect(
        "Localidad (vacío = todas)", localidades, default=[], key="f_loc"
    )

    estados = sorted(df["estado"].unique())
    default_estado = ["Total"] if "Total" in estados else estados[:1]
    sel_estado = st.sidebar.multiselect(
        "Estado del registro", estados, default=default_estado, key="f_estado",
        help="'Total' = patentamientos brutos. '-HERZT' = ajustes/bajas "
             "(valores negativos). Elegí ambos para ver el neto.",
    )

    out = df[
        (df["Periodo"] >= p_ini) & (df["Periodo"] <= p_fin)
        & (df["provincia_label"].isin(sel_prov))
        & (df["Zona"].isin(sel_zona))
        & (df["tipo"].isin(sel_tipo))
        & (df["estado"].isin(sel_estado))
    ]
    if sel_marca:
        out = out[out["Marca"].isin(sel_marca)]
    if sel_loc:
        out = out[out["Localidad"].isin(sel_loc)]

    st.sidebar.caption(f"{len(out):,} registros filtrados de {len(df):,} totales".replace(",", "."))

    return out


# ---------------------------------------------------------------------------
# Helpers de formato
# ---------------------------------------------------------------------------

def fmt_int(n) -> str:
    return f"{int(n):,}".replace(",", ".")


def month_label(ts) -> str:
    meses = ["ene", "feb", "mar", "abr", "may", "jun", "jul", "ago", "sep", "oct", "nov", "dic"]
    ts = pd.Timestamp(ts)
    return f"{meses[ts.month - 1]}-{str(ts.year)[2:]}"
