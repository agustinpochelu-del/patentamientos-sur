# Patentamientos Sur — Streamlit App

Dashboard de análisis de patentamientos de vehículos en Chubut, Río Negro y
Santa Cruz, a partir del Excel "SUR por localidad y por modelo".

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

Se abre en el navegador (por defecto `http://localhost:8501`).

## Uso

1. En la barra lateral, subí el archivo Excel (**mismo formato** que el
   original: debe contener la hoja *Tabla Pat* con la Tabla de Excel
   `PaT_Ciudad`, y la hoja *auxiliares* con las Tablas `Modelos` y
   `Ciudades`). El nombre del archivo puede cambiar — lo que importa es que
   esas 3 Tablas de Excel conserven sus nombres.
2. Ajustá los filtros (período, provincia, zona, tipo, marca, localidad,
   estado del registro). Se mantienen al navegar entre páginas.
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
├── app.py                          # Página de inicio
├── utils.py                        # Carga de datos, limpieza, filtros compartidos
├── pages/
│   ├── 1_📈_Evolucion_Temporal.py
│   ├── 2_🏆_Rankings.py
│   ├── 3_⚖️_Comparativas.py
│   └── 4_🔍_Detalle.py
├── .streamlit/config.toml          # Tema visual
└── requirements.txt
```
