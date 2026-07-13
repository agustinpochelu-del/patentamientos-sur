# Patentamientos Sur — Streamlit App

Dashboard de análisis de patentamientos de vehículos en Chubut, Río Negro y
Santa Cruz, a partir del Excel "SUR por localidad y por modelo".

## ⚠️ Si ya tenías la versión anterior en GitHub (con carpeta `pages/`)

Esta versión cambió de arquitectura para que los **filtros del sidebar se
mantengan siempre, en todas las páginas** (antes se reseteaban al navegar —
es una limitación conocida de la carpeta `pages/` de Streamlit). Para
actualizar tu repositorio:

1. **Borrá la carpeta `pages/`** completa de tu repo en GitHub (entrá a la
   carpeta, y en cada archivo usá el ícono de tacho de basura, o borrala
   desde GitHub Desktop / línea de comandos).
2. Subí la **carpeta `views/`** completa (reemplaza a `pages/`).
3. Reemplazá `app.py` y `utils.py` por los de esta versión.
4. Reemplazá `requirements.txt` (subió la versión mínima de Streamlit
   necesaria para la nueva navegación).
5. Hacé "Reboot app" en Streamlit Community Cloud si no se actualiza sola.

Los nombres de archivo ya no llevan emoji (los íconos del menú ahora se
definen por código, no por nombre de archivo), así que no hay riesgo de
que se rompan al subirlos por el navegador.

## Instalación

```bash
cd streamlit_app
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Ejecutar

```bash
streamlit run app.py
```
(en Windows, si `streamlit` no se reconoce como comando, usá
`python -m streamlit run app.py`)

Se abre en el navegador (por defecto `http://localhost:8501`).

## Uso

1. En la barra lateral, subí el archivo Excel (**mismo formato** que el
   original: debe contener la hoja *Tabla Pat* con la Tabla de Excel
   `PaT_Ciudad`, y la hoja *auxiliares* con las Tablas `Modelos` y
   `Ciudades`). El nombre del archivo puede cambiar — lo que importa es que
   esas 3 Tablas de Excel conserven sus nombres.
2. Ajustá los filtros (período, provincia, zona, tipo, marca, localidad,
   estado del registro). **Se mantienen siempre, en cualquier página del
   menú**, porque ahora se definen en el archivo de entrada (`app.py`),
   que actúa como marco común alrededor de todas las páginas.
3. Recorré las páginas del menú lateral:
   - **Inicio**: KPIs generales y resumen.
   - **Evolución Temporal**: series mensuales, por provincia, por tipo,
     seguimiento de marcas/modelos puntuales, comparación interanual.
   - **Rankings**: top localidades, modelos, marcas y tipos de vehículo.
   - **Comparativas**: provincia vs. tipo, zonas, treemap jerárquico,
     participación de marcas, tabla provincia x mes.
   - **Detalle**: tabla filtrable con búsqueda y exportación a CSV,
     constructor de tablas dinámicas, y chequeo de calidad de datos
     (localidades/modelos sin match contra las tablas auxiliares).

Nota: algunos controles son intencionalmente **locales de cada página**
(no filtros globales), porque ajustan un gráfico puntual: el "Top N" en
Rankings, el selector de marcas/modelos a comparar en Evolución Temporal,
las provincias a comparar en el gráfico de torta de Comparativas, y el
buscador de texto en Detalle.

## Notas sobre los datos

- **Estado del registro** (`Total` vs `-HERZT`): la mayoría de los
  registros son `Total` (patentamientos brutos). Existe un pequeño grupo
  de registros `-HERZT` con valores negativos que representan ajustes o
  bajas. Por defecto la app usa solo `Total`; podés agregar `-HERZT` en el
  filtro "Estado del registro" del sidebar para ver el neto.
- Se normalizan inconsistencias menores de mayúsculas/minúsculas en la
  columna `tipo` (ej. "autos" → "Autos").
- Las columnas sin nombre que aparecían sueltas en la hoja *Tabla Pat*
  (cálculos auxiliares de la planilla original) se descartan automáticamente.

## Estructura del proyecto

```
streamlit_app/
├── app.py                          # Entrada: carga de datos, filtros (marco común), navegación
├── utils.py                        # Carga de datos, limpieza, filtros compartidos
├── views/
│   ├── inicio.py
│   ├── evolucion.py
│   ├── rankings.py
│   ├── comparativas.py
│   └── detalle.py
├── .streamlit/config.toml          # Tema visual
└── requirements.txt
```
