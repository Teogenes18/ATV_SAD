import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.figure_factory as ff

st.set_page_config(
    page_title="Students Performance Dashboard",
    page_icon="📚",
    layout="wide"
)

@st.cache_data
def carregar_dados():
    return pd.read_csv("StudentsPerformance.csv")

df = carregar_dados()

st.title("Dashboard - Students Performance in Exams")

st.markdown("""
Este dashboard apresenta uma análise exploratória do dataset
**Students Performance in Exams**, permitindo identificar padrões,
comparar grupos de estudantes e apoiar decisões educacionais.
""")

st.sidebar.header("Filtros")

genero = st.sidebar.multiselect(
    "Gênero",
    options=df["gender"].unique(),
    default=df["gender"].unique()
)

curso = st.sidebar.multiselect(
    "Curso Preparatório",
    options=df["test preparation course"].unique(),
    default=df["test preparation course"].unique()
)

df_filtrado = df[
    (df["gender"].isin(genero))
    &
    (df["test preparation course"].isin(curso))
]

st.header("Indicadores Gerais")

media_math = df_filtrado["math score"].mean()
media_reading = df_filtrado["reading score"].mean()
media_writing = df_filtrado["writing score"].mean()

total_alunos = len(df_filtrado)

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Média Matemática",
    f"{media_math:.2f}"
)

col2.metric(
    "Média Leitura",
    f"{media_reading:.2f}"
)

col3.metric(
    "Média Escrita",
    f"{media_writing:.2f}"
)

col4.metric(
    "Total de Alunos",
    total_alunos
)

st.divider()

st.subheader("1️⃣ Distribuição das Notas de Matemática")

fig1 = px.histogram(
    df_filtrado,
    x="math score",
    nbins=20,
    title="Distribuição das Notas de Matemática"
)

st.plotly_chart(fig1, use_container_width=True)

st.subheader("2️⃣ Curso Preparatório x Nota de Matemática")

fig2 = px.box(
    df_filtrado,
    x="test preparation course",
    y="math score",
    color="test preparation course",
    title="Impacto do Curso Preparatório"
)

st.plotly_chart(fig2, use_container_width=True)

st.subheader("3️⃣ Escolaridade dos Pais x Desempenho")

media_pais = (
    df_filtrado
    .groupby("parental level of education")
    [["math score", "reading score", "writing score"]]
    .mean()
    .reset_index()
)

fig3 = px.bar(
    media_pais,
    x="parental level of education",
    y=["math score", "reading score", "writing score"],
    barmode="group",
    title="Média das Notas por Escolaridade dos Pais"
)

st.plotly_chart(fig3, use_container_width=True)

st.subheader("4️⃣ Relação entre Leitura e Escrita")

fig4 = px.scatter(
    df_filtrado,
    x="reading score",
    y="writing score",
    color="gender",
    title="Leitura x Escrita"
)

st.plotly_chart(fig4, use_container_width=True)

st.subheader("5️⃣ Desempenho Médio por Gênero")

media_genero = (
    df_filtrado
    .groupby("gender")
    [["math score", "reading score", "writing score"]]
    .mean()
    .reset_index()
)

fig5 = px.bar(
    media_genero,
    x="gender",
    y=["math score", "reading score", "writing score"],
    barmode="group",
    title="Notas Médias por Gênero"
)

st.plotly_chart(fig5, use_container_width=True)

st.header("Correlação entre as Notas")

corr = df_filtrado[
    ["math score", "reading score", "writing score"]
].corr()

heatmap = ff.create_annotated_heatmap(
    z=corr.values,
    x=list(corr.columns),
    y=list(corr.index),
    annotation_text=round(corr, 2).values,
    showscale=True
)

st.plotly_chart(
    heatmap,
    use_container_width=True
)

st.markdown("""
**Interpretação:**

- Valores próximos de **1** indicam forte correlação positiva.
- Valores próximos de **0** indicam baixa correlação.
- Quanto maior a correlação, maior a tendência de as variáveis variarem juntas.
""")

st.divider()

st.header("Qualidade dos Dados")

col1, col2 = st.columns(2)

with col1:

    st.subheader("Valores Ausentes")

    missing = (
        df.isnull()
        .sum()
        .reset_index()
    )

    missing.columns = [
        "Variável",
        "Valores Ausentes"
    ]

    st.dataframe(
        missing,
        use_container_width=True
    )

with col2:

    st.subheader("Registros Duplicados")

    duplicados = df.duplicated().sum()

    st.metric(
        "Quantidade",
        duplicados
    )

st.divider()

st.header("Estatísticas Descritivas")

st.dataframe(
    df_filtrado.describe(),
    use_container_width=True
)

st.divider()

st.header("Dados Filtrados")

st.dataframe(
    df_filtrado,
    use_container_width=True
)

st.divider()

st.header("Insights para Tomada de Decisão")

curso_concluido = df_filtrado[
    df_filtrado["test preparation course"] == "completed"
]["math score"].mean()

curso_nao = df_filtrado[
    df_filtrado["test preparation course"] == "none"
]["math score"].mean()

st.info(
    f"""
    Média geral de Matemática: {media_math:.2f}

    Média de Matemática dos alunos que concluíram o curso preparatório:
    {curso_concluido:.2f}

    Média de Matemática dos alunos que não realizaram o curso:
    {curso_nao:.2f}
    """
)

if curso_concluido > curso_nao:
    st.success(
        "Os dados sugerem que estudantes que concluíram o curso preparatório apresentam melhor desempenho médio em matemática."
    )
else:
    st.warning(
        "Não foi observada vantagem clara para os estudantes que realizaram o curso preparatório."
    )

st.markdown("""
### Possíveis Aplicações em Sistemas de Apoio à Decisão

- Identificação de grupos com maior risco de baixo desempenho;
- Avaliação da efetividade de cursos preparatórios;
- Planejamento de programas de reforço escolar;
- Monitoramento de indicadores acadêmicos;
- Apoio à formulação de políticas educacionais.
""")

st.divider()

st.caption(
    "Dashboard desenvolvido para análise exploratória do dataset Students Performance in Exams."
)