import streamlit as st

from utils import ensure_data_loaded, sidebar_filters
from views import inicio, evolucion, rankings, comparativas, detalle

st.set_page_config(
    page_title="Patentamientos Sur",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Este script (app.py) es el "marco" común: se ejecuta en CADA rerun,
# incluso al navegar entre páginas. Por eso los filtros definidos acá
# mantienen su valor sin importar qué página esté activa.
df_pat, df_modelos, df_ciudades = ensure_data_loaded()
df, df_bruto, df_neto = sidebar_filters(df_pat)

pages = [
    st.Page(lambda: inicio.render(df, df_bruto, df_neto, df_modelos, df_ciudades),
            title="Inicio", icon="🏠", url_path="inicio", default=True),
    st.Page(lambda: evolucion.render(df, df_bruto, df_neto),
            title="Evolución Temporal", icon="📈", url_path="evolucion"),
    st.Page(lambda: rankings.render(df),
            title="Rankings", icon="🏆", url_path="rankings"),
    st.Page(lambda: comparativas.render(df),
            title="Comparativas", icon="⚖️", url_path="comparativas"),
    st.Page(lambda: detalle.render(df, df_pat, df_modelos, df_ciudades),
            title="Detalle", icon="🔍", url_path="detalle"),
]

pg = st.navigation(pages)
pg.run()
