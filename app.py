
import streamlit as st
import pandas as pd
import os
import unicodedata
import re

st.set_page_config(
    page_title="Recetas para disfrutar",
    page_icon="🍓",
    layout="wide"
)

def normalizar(texto):
    texto = str(texto).lower().strip()
    texto = unicodedata.normalize("NFD", texto)
    return "".join(
        c for c in texto
        if unicodedata.category(c) != "Mn"
    )

def cargar_datos():
    archivos = [
        "Base_de_datos(2).csv",
        "Base_de_datos.csv",
        "Base de datos 2(1).xlsx",
        "Base de datos 2.xlsx"
    ]

    for archivo in archivos:
        if os.path.exists(archivo):
            try:
                if archivo.endswith(".csv"):
                    datos = pd.read_csv(
                        archivo,
                        header=1,
                        encoding="utf-8-sig"
                    )
                else:
                    datos = pd.read_excel(
                        archivo,
                        header=1
                    )

                datos.columns = [
                    str(c).strip()
                    for c in datos.columns
                ]

                datos = datos.loc[
                    :,
                    ~datos.columns.str.contains("^Unnamed")
                ]

                columnas = {
                    normalizar(c): c
                    for c in datos.columns
                }

                requeridas = [
                    "grupo",
                    "receta",
                    "ingredientes",
                    "proceso",
                    "fecha"
                ]

                if not all(c in columnas for c in requeridas):
                    continue

                datos = datos.rename(columns={
                    columnas["grupo"]: "Grupo",
                    columnas["receta"]: "Receta",
                    columnas["ingredientes"]: "Ingredientes",
                    columnas["proceso"]: "Proceso",
                    columnas["fecha"]: "Fecha"
                })

                datos = datos.dropna(subset=["Receta"])

                datos["Fecha"] = pd.to_datetime(
                    datos["Fecha"],
                    errors="coerce"
                )

                return datos

            except Exception:
                continue

    st.error("No se pudo encontrar o leer la base de datos.")
    st.stop()


procedimientos = {
    "reses saludables": [
        "Prepara todos los ingredientes.",
        "Tritura los dátiles hasta obtener una pasta.",
        "Agrega la crema de cacahuate y mezcla.",
        "Incorpora el chocolate previamente derretido.",
        "Forma pequeñas porciones.",
        "Refrigera durante 30 minutos antes de servir."
    ],

    "rice cakes dulces": [
        "Coloca las rice cakes en un plato.",
        "Unta el ingrediente que prefieras.",
        "Corta la fruta en trozos pequeños.",
        "Agrega los toppings sobre las rice cakes.",
        "Sirve inmediatamente."
    ],

    "volcan de chocolate": [
        "Precalienta el horno a 180 °C.",
        "Derrite el chocolate a baño María.",
        "Bate el huevo y agrega el yogurt griego.",
        "Incorpora el cacao y la harina.",
        "Agrega el chocolate derretido y mezcla.",
        "Coloca la preparación en moldes individuales.",
        "Hornea aproximadamente de 8 a 12 minutos.",
        "Deja reposar y sirve."
    ],

    "sopa de tomate": [
        "Lava y corta los tomates.",
        "Pica la cebolla y el ajo.",
        "Calienta un poco de aceite en una olla.",
        "Sofríe la cebolla y el ajo.",
        "Agrega los tomates y el romero.",
        "Cocina hasta que los tomates estén suaves.",
        "Licúa hasta conseguir una textura cremosa.",
        "Regresa la sopa a la olla, calienta y sirve."
    ],

    "panecillos de leche": [
        "Mezcla la harina de avena con la levadura.",
        "Agrega la leche, el yogurt griego, la sal y la miel.",
        "Integra hasta obtener una masa homogénea.",
        "Deja reposar hasta que aumente su volumen.",
        "Forma pequeños panecillos.",
        "Colócalos en una bandeja.",
        "Hornea a 180 °C hasta que estén cocidos.",
        "Deja enfriar antes de servir."
    ],

    "boniato asado": [
        "Lava muy bien el boniato.",
        "Córtalo en rodajas o cubos.",
        "Colócalo en una bandeja para hornear.",
        "Agrega aceite o mantequilla y una pizca de sal.",
        "Hornea a 200 °C durante 25 a 35 minutos.",
        "Comprueba que esté suave y sirve."
    ],

    "pancakes con avena": [
        "Coloca la avena en una licuadora.",
        "Agrega huevo, leche y plátano.",
        "Licúa hasta conseguir una mezcla uniforme.",
        "Calienta una sartén antiadherente.",
        "Vierte pequeñas porciones de la mezcla.",
        "Cocina por ambos lados hasta que estén dorados.",
        "Sirve con fruta fresca."
    ],

    "brownies de cacao": [
        "Precalienta el horno a 180 °C.",
        "Mezcla el cacao con la harina de avena.",
        "Agrega huevo, plátano triturado y leche.",
        "Mezcla hasta conseguir una preparación homogénea.",
        "Vierte la mezcla en un molde.",
        "Hornea aproximadamente de 20 a 25 minutos.",
        "Deja enfriar antes de cortar."
    ]
}


recetas_extra = pd.DataFrame([
    {
        "Grupo": "Receta 7",
        "Receta": "Pancakes con avena",
        "Ingredientes": "Avena, huevo, leche, plátano y miel",
        "Proceso": "Preparación casera",
        "Fecha": pd.Timestamp("2024-03-01")
    },
    {
        "Grupo": "Receta 8",
        "Receta": "Brownies de cacao",
        "Ingredientes": "Cacao, harina de avena, huevo, plátano y leche",
        "Proceso": "Preparación casera",
        "Fecha": pd.Timestamp("2025-06-01")
    }
])


def preparar_datos():
    datos = cargar_datos()

    nombres = [
        normalizar(nombre)
        for nombre in datos["Receta"]
    ]

    for _, receta in recetas_extra.iterrows():
        if normalizar(receta["Receta"]) not in nombres:
            datos = pd.concat(
                [datos, receta.to_frame().T],
                ignore_index=True
            )

    datos = datos.drop_duplicates(
        subset=["Receta"],
        keep="first"
    ).reset_index(drop=True)

    datos["Fecha"] = pd.to_datetime(
        datos["Fecha"],
        errors="coerce"
    )

    datos["Ingredientes"] = datos["Ingredientes"].fillna(
        "Ingredientes no registrados"
    )

    return datos


def categoria(nombre):
    nombre = normalizar(nombre)

    if any(x in nombre for x in [
        "pancake", "rice cake", "panecillo", "bowl"
    ]):
        return "Desayuno"

    if any(x in nombre for x in [
        "pasta", "sopa"
    ]):
        return "Comida"

    if any(x in nombre for x in [
        "chocolate", "brownie", "boniato", "reses"
    ]):
        return "Postre"

    return "Otros"


def descripcion(nombre):
    nombre = normalizar(nombre)

    descripciones = {
        "reses saludables": "Pequeños bocados dulces con chocolate, dátiles y crema de cacahuate.",
        "rice cakes dulces": "Una opción crujiente acompañada de diferentes toppings.",
        "volcan de chocolate": "Un postre de chocolate con un centro suave.",
        "sopa de tomate": "Una preparación caliente de tomate con cebolla, ajo y romero.",
        "panecillos de leche": "Panecillos suaves elaborados con harina de avena.",
        "boniato asado": "Una preparación sencilla de boniato horneado.",
        "pancakes con avena": "Pancakes preparados con avena y plátano.",
        "brownies de cacao": "Brownies caseros preparados con cacao y harina de avena."
    }

    return descripciones.get(
        nombre,
        "Una receta sencilla para disfrutar."
    )


datos = preparar_datos()

datos["Categoria"] = datos["Receta"].apply(categoria)
datos["Descripcion"] = datos["Receta"].apply(descripcion)
datos["Popular"] = datos.index < 3


if "seleccionada" not in st.session_state:
    st.session_state.seleccionada = None


st.title("Recetas para disfrutar")

st.write(
    "Descubre recetas deliciosas, sencillas y saludables. "
    "Encuentra nuevas ideas para preparar tus platillos favoritos."
)

st.divider()

st.header("Recetas para disfrutar")

col1, col2 = st.columns([2, 1])

with col1:
    busqueda = st.text_input(
        "Buscar por nombre",
        placeholder="Ej. pancakes o brownies"
    )

with col2:
    categoria_filtro = st.selectbox(
        "Categoría",
        [
            "Todas las categorías",
            "Desayuno",
            "Comida",
            "Postre",
            "Otros"
        ]
    )

col3, col4 = st.columns(2)

with col3:
    populares = st.checkbox("Solo populares")

with col4:
    if st.button("Limpiar filtros"):
        st.session_state.seleccionada = None
        st.rerun()


filtradas = datos.copy()

if busqueda:
    filtradas = filtradas[
        filtradas["Receta"].apply(
            lambda x: normalizar(busqueda) in normalizar(x)
        )
    ]

if categoria_filtro != "Todas las categorías":
    filtradas = filtradas[
        filtradas["Categoria"] == categoria_filtro
    ]

if populares:
    filtradas = filtradas[
        filtradas["Popular"]
    ]


st.write(f"**{len(filtradas)} recetas disponibles**")


for inicio in range(0, len(filtradas), 4):

    columnas = st.columns(4)

    grupo = filtradas.iloc[inicio:inicio + 4]

    for posicion, (_, receta) in enumerate(grupo.iterrows()):

        with columnas[posicion]:

            with st.container(border=True):

                st.caption(
                    receta["Categoria"].upper()
                    + (" · POPULAR" if receta["Popular"] else "")
                )

                st.subheader(receta["Receta"])

                st.write(receta["Descripcion"])

                if st.button(
                    "Ver receta ↗",
                    key=f"receta_{normalizar(receta['Receta'])}"
                ):
                    st.session_state.seleccionada = receta["Receta"]
                    st.rerun()


if st.session_state.seleccionada is not None:

    seleccion = datos[
        datos["Receta"] == st.session_state.seleccionada
    ]

    if not seleccion.empty:

        receta = seleccion.iloc[0]

        st.divider()

        with st.container(border=True):

            st.title(receta["Receta"])

            st.write(receta["Descripcion"])

            if pd.notna(receta["Fecha"]):
                st.caption(
                    "Fecha: " + receta["Fecha"].strftime("%d/%m/%Y")
                )

            ingredientes_col, proceso_col = st.columns(2)

            with ingredientes_col:

                st.subheader("Ingredientes")

                ingredientes = re.split(
                    r",|;|\n",
                    str(receta["Ingredientes"])
                )

                for ingrediente in ingredientes:
                    if ingrediente.strip():
                        st.write("- " + ingrediente.strip())

            with proceso_col:

                st.subheader("Preparación")

                pasos = procedimientos.get(
                    normalizar(receta["Receta"]),
                    [
                        "Organiza los ingredientes.",
                        "Mezcla los ingredientes.",
                        "Prepara hasta obtener la textura deseada.",
                        "Sirve y disfruta."
                    ]
                )

                for numero, paso in enumerate(pasos, start=1):
                    st.write(f"{numero}. {paso}")

            if st.button("Cerrar receta"):
                st.session_state.seleccionada = None
                st.rerun()


st.divider()

st.header("Buscar recetas por fecha")

st.write(
    "Selecciona un año y un mes para encontrar las recetas "
    "registradas durante ese periodo."
)

col_anio, col_mes = st.columns(2)

anios = sorted(
    datos["Fecha"].dropna().dt.year.unique().tolist(),
    reverse=True
)

if not anios:
    anios = [2026]

meses = {
    1: "Enero",
    2: "Febrero",
    3: "Marzo",
    4: "Abril",
    5: "Mayo",
    6: "Junio",
    7: "Julio",
    8: "Agosto",
    9: "Septiembre",
    10: "Octubre",
    11: "Noviembre",
    12: "Diciembre"
}

with col_anio:
    anio = st.selectbox(
        "Selecciona el año",
        anios
    )

with col_mes:
    mes = st.selectbox(
        "Selecciona el mes",
        list(meses.keys()),
        format_func=lambda x: meses[x]
    )


if st.button("Buscar recetas por fecha"):

    resultados = datos[
        (datos["Fecha"].dt.year == anio) &
        (datos["Fecha"].dt.month == mes)
    ]

    st.divider()

    st.subheader(
        f"Resultados de {meses[mes]} de {anio}"
    )

    if resultados.empty:

        st.warning(
            "No se encontraron recetas para esta fecha. "
            "Intenta seleccionar otro mes o año."
        )

    else:

        st.success(
            f"Se encontraron {len(resultados)} recetas."
        )

        for _, receta in resultados.iterrows():

            with st.expander(receta["Receta"]):

                st.write(receta["Descripcion"])

                st.markdown("**Ingredientes**")

                for ingrediente in re.split(
                    r",|;|\n",
                    str(receta["Ingredientes"])
                ):
                    if ingrediente.strip():
                        st.write("- " + ingrediente.strip())

                st.markdown("**Preparación**")

                pasos = procedimientos.get(
                    normalizar(receta["Receta"]),
                    [
                        "Organiza todos los ingredientes.",
                        "Mezcla los ingredientes.",
                        "Prepara la receta.",
                        "Sirve y disfruta."
                    ]
                )

                for numero, paso in enumerate(pasos, start=1):
                    st.write(f"{numero}. {paso}")


st.divider()

st.title("Recetas para disfrutar")

st.caption(
    "Descubre, prepara y disfruta nuevas recetas."
)
