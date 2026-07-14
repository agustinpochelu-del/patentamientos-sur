# Patentamientos Sur — Streamlit App

Dashboard de análisis de patentamientos de vehículos en Chubut, Río Negro y
Santa Cruz, a partir del Excel "SUR por localidad y por modelo".

## ⚠️ Si ya tenías una versión anterior en GitHub (con carpeta `pages/`)

Esta versión cambió de arquitectura para que los **filtros del sidebar se
mantengan siempre, en todas las páginas** (antes se reseteaban al navegar —
es una limitación conocida de la carpeta `pages/` de Streamlit). Para
actualizar tu repositorio:

1. **Borrá la carpeta `pages/`** completa de tu repo en GitHub, y también
   `__pycache__/` si quedó subida por error.
2. Subí la **carpeta `views/`** completa (reemplaza a `pages/`).
3. Reemplazá `app.py`, `utils.py` y `requirements.txt` por los de esta versión.
4. Subí el `.gitignore` (evita que se vuelvan a colar `__pycache__` o tu
   futura API key).
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
   y el selector de **Volumen** Global/Real). **Se mantienen siempre, en cualquier página del
   menú**, porque se definen en el archivo de entrada (`app.py`), que
   actúa como marco común alrededor de todas las páginas.
3. Recorré las páginas del menú lateral:
   - **Inicio**: KPIs generales, resumen escrito automático, y análisis
     opcional con IA.
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

## 🤖 Análisis con IA (opcional)

En la página **Inicio** hay dos niveles de resumen escrito:

1. **Resumen automático**: siempre visible, se genera con lógica de Python
   a partir de los números filtrados. Gratis, instantáneo, no necesita
   configuración.
2. **Análisis más profundo con IA**: un párrafo más elaborado, generado por
   un modelo de lenguaje. Es opcional y necesita tu propia API key.
   Podés usar **Claude (Anthropic)**, **Gemini (Google)**, o configurar
   ambas keys y elegir cuál usar cada vez desde la app.

### Cómo activarlo

**Claude (Anthropic)**
1. Conseguí una API key en [console.anthropic.com](https://console.anthropic.com)
   (sección *API Keys*).
2. En Streamlit Community Cloud: tu app → **⋮ → Settings → Secrets**:
   ```toml
   ANTHROPIC_API_KEY = "sk-ant-tu-key-aca"
   ```

**Gemini (Google)**
1. Conseguí una API key en [aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey).
2. En Streamlit Community Cloud: tu app → **⋮ → Settings → Secrets**:
   ```toml
   GEMINI_API_KEY = "tu-key-aca"
   ```

En ambos casos, guardá y la app se reinicia sola. Si configurás las dos,
la app te deja elegir con un selector cada vez que generás un análisis.

**Para probarlo en tu computadora**: creá el archivo
`.streamlit/secrets.toml` con la(s) misma(s) línea(s) de arriba. **Nunca lo
subas a GitHub** — ya está excluido en el `.gitignore` del proyecto para
evitarlo por error.

Si no configurás ninguna API key, esa sección simplemente muestra las
instrucciones para conseguirlas — el resto de la app funciona igual.

Modelos usados por defecto: `claude-sonnet-5` y `gemini-3.5-flash`. Se
pueden cambiar editando los parámetros `model=` en `utils.py`
(`generate_ai_analysis` / `generate_ai_analysis_gemini`) por una versión
más económica si preferís reducir el costo por análisis.

## 💰 Volumen Global vs. Real (efecto Hertz)

Desde marzo/abril de 2025, Hertz patenta vehículos en la provincia bajo un
régimen que le resulta beneficioso, pero la mayoría de esos autos no
circula realmente en la provincia. Esos patentamientos se registran en el
Excel como `-HERZT` (valores negativos), y la app los trata así:

- **Selector "Volumen" en el sidebar**: elegís si todos los análisis
  (Rankings, Comparativas, Evolución, Detalle) usan el volumen **Global
  (bruto)** o el **Real (neto de Hertz)**. Se mantiene al navegar entre
  páginas, como el resto de los filtros.
- **En Inicio**: además del volumen elegido, siempre se muestra la
  comparación completa (Global, Real y el Ajuste por Hertz), sin importar
  qué esté seleccionado en el sidebar.
- **En Evolución Temporal**: un gráfico dedicado compara ambas series mes
  a mes — ahí se ve claramente cuándo arrancó el efecto (marzo/abril 2025)
  y su magnitud.
- **En el resumen escrito y en el análisis con IA**: ambos mencionan
  explícitamente el ajuste por Hertz, para que no se confunda con demanda
  genuina del mercado.

> 🔜 Pendiente para más adelante: una funcionalidad para detectar
> automáticamente los "picos" del mes recién incorporado (patentamientos
> que se salen del volumen normal), tomando como referencia que los meses
> anteriores ya están neteados. La vamos a diseñar cuando la retomes.

## Notas sobre los datos

- Se normalizan inconsistencias menores de mayúsculas/minúsculas en la
  columna `tipo` (ej. "autos" → "Autos").
- Las columnas sin nombre que aparecían sueltas en la hoja *Tabla Pat*
  (cálculos auxiliares de la planilla original) se descartan automáticamente.

## Estructura del proyecto

```
streamlit_app/
├── app.py                          # Entrada: carga de datos, filtros (marco común), navegación
├── utils.py                        # Carga de datos, limpieza, filtros, resumen y análisis IA
├── views/
│   ├── inicio.py
│   ├── evolucion.py
│   ├── rankings.py
│   ├── comparativas.py
│   └── detalle.py
├── .streamlit/config.toml          # Tema visual
├── .gitignore
└── requirements.txt
```
