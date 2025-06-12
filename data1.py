import streamlit as st
import plotly.express as px
import pandas as pd

# Título de la app
st.title("Análisis Interactivo de Películas")

# Cargar datos
@st.cache_data
def load_data():
    df = pd.read_csv("movies_metadata.csv", low_memory=False)
    df = df.copy()
    for col in ["budget", "revenue", "popularity", "vote_average", "runtime"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    df["belongs_to_collection"] = df["belongs_to_collection"].notnull()
    df["has_slogan"] = df["tagline"].notnull() & (df["tagline"].str.strip() != "")
    return df.dropna(subset=["budget", "revenue", "popularity", "vote_average", "runtime"])

df = load_data()

# Análisis 1: Presupuesto vs Ganancias
if st.toggle("¿Películas con mayor presupuesto tienen mayores ganancias?"):
    st.subheader("Presupuesto vs Ganancias")
    fig = px.scatter(df, x="budget", y="revenue", hover_data=["original_title"])
    st.plotly_chart(fig)

    fig2 = px.histogram(df, x="budget", nbins=50, title="Distribución de Presupuesto")
    st.plotly_chart(fig2)

    fig3 = px.histogram(df, x="revenue", nbins=50, title="Distribución de Ganancias")
    st.plotly_chart(fig3)

    st.write("Matriz de correlación:")
    st.dataframe(df[["budget", "revenue"]].corr())

    st.markdown("**Conclusión:** En general, aunque hay cierta relación entre el presupuesto y las ganancias, no siempre un mayor presupuesto garantiza un mayor éxito en taquilla. La dispersión en los datos sugiere que otros factores también influyen")


# Análisis 2: Duración por Idioma
if st.toggle("Comparar duración promedio por idioma"):
    st.subheader("Duración por Idioma")
    df_filtrado = df[df["runtime"] < 300]
    idiomas = df_filtrado["original_language"].value_counts().nlargest(8).index
    fig = px.box(df_filtrado[df_filtrado["original_language"].isin(idiomas)],
                 x="original_language", y="runtime", title="Boxplot de duración por idioma")
    st.plotly_chart(fig)
    st.markdown("**Conclusión:** Las películas varían bastante en duración según el idioma. Idiomas con más producción tienden a tener una mayor variedad de duraciones, lo que puede reflejar diferencias culturales o de industria")


# Análisis 3: Popularidad y Slogan
if st.toggle("¿Películas con slogan son más populares?"):
    st.subheader("Popularidad vs Slogan")
    fig = px.box(df, x="has_slogan", y="popularity",
                 labels={"has_slogan": "¿Tiene slogan?", "popularity": "Popularidad"})
    st.plotly_chart(fig)

    fig2 = px.histogram(df, x="popularity", color="has_slogan",
                        barmode="overlay", nbins=50, title="Distribución de popularidad")
    st.plotly_chart(fig2)
    st.markdown("**Conclusión:** Las películas que tienen slogan tienden a ser ligeramente más populares. Esto puede deberse a que un buen slogan mejora el impacto de la pelicula con ayuda del marketing")


# Análisis 4: Calificación por Idioma o País
if st.toggle("¿Idioma o país influye en la calificación promedio?"):
    st.subheader("Idioma vs Calificación")
    df = df.copy()
    df['production_country'] = df['production_countries'].astype(str).str.extract(r"'name': '([^']+)'")
    idiomas = df['original_language'].value_counts().nlargest(6).index
    fig1 = px.box(df[df["original_language"].isin(idiomas)],
                  x="original_language", y="vote_average",
                  title="Boxplot: Calificación por idioma")
    st.plotly_chart(fig1)

    paises = df['production_country'].value_counts().nlargest(6).index
    fig2 = px.box(df[df["production_country"].isin(paises)],
                  x="production_country", y="vote_average",
                  title="Boxplot: Calificación por país")
    st.plotly_chart(fig2)
    st.markdown("**Conclusión:** Hay diferencias notables en la calificación promedio dependiendo del idioma y del país. Esto podría deberse a estilos narrativos, preferencias culturales o calidad de producción")


# Análisis 5: Colección vs Ganancias
if st.toggle("¿Pertenecer a una colección influye en las ganancias?"):
    st.subheader("Ganancias vs Colección")
    df_filtrado = df[df["revenue"] < 1e9]
    fig = px.box(df_filtrado, x="belongs_to_collection", y="revenue",
                 labels={"belongs_to_collection": "¿Pertenece a colección?"})
    st.plotly_chart(fig)

    fig2 = px.histogram(df_filtrado, x="revenue", color="belongs_to_collection",
                        nbins=50, barmode="overlay", title="Distribución de ganancias")
    st.plotly_chart(fig2)
    st.markdown("**Conclusión:** Las películas que pertenecen a una colección suelen tener mejores ganancias, lo cual tiene sentido ya que forman parte de franquicias o sagas conocidas por el público")



# Pruebas de normalidad

import streamlit as st
from scipy.stats import shapiro, kruskal

st.subheader("Pruebas de Normalidad y Comparación")

# Resultados de Shapiro
stat_shapiro = 0.3681
p_shapiro = 0.0000

st.subheader("Resultado: Prueba de Normalidad (Shapiro-Wilk)")
st.markdown(f"- **Estadístico:** {stat_shapiro:.4f}")
st.markdown(f"- **p-valor:** {p_shapiro:.4f}")

if p_shapiro < 0.05:
    st.error("🔴 Los datos **NO** parecen seguir una distribución normal.")
    st.markdown("**Conclusión:** Como los datos no son normales, se recomienda usar pruebas estadísticas no paramétricas para comparaciones entre grupos.")
else:
    st.success("🟢 Los datos parecen seguir una distribución normal.")
    st.markdown("**Conclusión:** Dado que los datos son normales, pueden utilizarse métodos paramétricos como ANOVA o regresión.")

# Resultados de Kruskal-Wallis
stat_kruskal = 63.5410
p_kruskal = 0.0000

st.subheader("Resultado: Prueba de Comparación (Kruskal-Wallis)")
st.markdown(f"- **Estadístico:** {stat_kruskal:.4f}")
st.markdown(f"- **p-valor:** {p_kruskal:.4f}")

if p_kruskal < 0.05:
    st.warning("🟡 Hay diferencias **significativas** entre idiomas.")
    st.markdown("**Conclusión:** Existen diferencias estadísticamente significativas en la variable analizada entre los distintos idiomas.")
else:
    st.success("🟢 No hay diferencias significativas entre idiomas.")
    st.markdown("**Conclusión:** No se detectaron diferencias importantes entre los idiomas con respecto a la variable evaluada.")

""
import streamlit as st

sentiment_mapping = ["one", "two", "three", "four", "five"]
selected = st.feedback("faces")
if selected is not None:
    st.markdown(f"You selected {sentiment_mapping[selected]} star(s).")