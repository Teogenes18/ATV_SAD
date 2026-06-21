import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.figure_factory as ff

st.set_page_config(
    page_title="Students Performance Dashboard",
    page_icon="📚",
    layout="wide"
)

QUANT_COLS = ["math score", "reading score", "writing score"]


@st.cache_data
def carregar_dados():
    return pd.read_csv("StudentsPerformance.csv")


def tabela_frequencia(serie, nome_coluna):
    absoluta = serie.value_counts().rename("Frequência Absoluta")
    relativa = (serie.value_counts(normalize=True) * 100).round(2).rename("Frequência Relativa (%)")
    tabela = pd.concat([absoluta, relativa], axis=1).reset_index()
    tabela.columns = [nome_coluna, "Frequência Absoluta", "Frequência Relativa (%)"]
    return tabela


def lista_outliers(serie):
    q1, q3 = serie.quantile(0.25), serie.quantile(0.75)
    iqr = q3 - q1
    limite_inferior, limite_superior = q1 - 1.5 * iqr, q3 + 1.5 * iqr
    outliers = serie[(serie < limite_inferior) | (serie > limite_superior)]
    return sorted(outliers.tolist())


def stats_quant(serie):
    return {
        "Média": round(serie.mean(), 2),
        "Mediana": round(serie.median(), 2),
        "Mínimo": int(serie.min()),
        "Máximo": int(serie.max()),
        "Desvio Padrão": round(serie.std(), 2),
        "Qtd. Outliers (regra IQR)": len(lista_outliers(serie)),
    }


df = carregar_dados()

# ---------------------------------------------------------------------------
# Estatísticas fixas sobre a base completa (usadas nas respostas da atividade)
# ---------------------------------------------------------------------------
total_linhas, total_colunas = df.shape
qtd_ausentes = int(df.isnull().sum().sum())
qtd_duplicados = int(df.duplicated().sum())

freq_genero_full = tabela_frequencia(df["gender"], "Gênero")
freq_prep_full = tabela_frequencia(df["test preparation course"], "Curso Preparatório")

n_female = int((df["gender"] == "female").sum())
n_male = int((df["gender"] == "male").sum())
pct_female = n_female / total_linhas * 100
pct_male = n_male / total_linhas * 100

n_completed = int((df["test preparation course"] == "completed").sum())
n_none = int((df["test preparation course"] == "none").sum())
pct_completed = n_completed / total_linhas * 100
pct_none = n_none / total_linhas * 100

n_groupA = int((df["race/ethnicity"] == "group A").sum())
pct_groupA = n_groupA / total_linhas * 100
n_master = int((df["parental level of education"] == "master's degree").sum())
pct_master = n_master / total_linhas * 100

stats_full = pd.DataFrame({c: stats_quant(df[c]) for c in QUANT_COLS}).T
stats_full.index.name = "Variável"

outliers_math = lista_outliers(df["math score"])
outliers_reading = lista_outliers(df["reading score"])

corr_full = df[QUANT_COLS].corr().round(3)

media_prep_full = df.groupby("test preparation course")["math score"].mean().round(2)
media_lunch_full = df.groupby("lunch")[QUANT_COLS].mean().round(2)
media_pais_full = df.groupby("parental level of education")[QUANT_COLS].mean().round(2)
media_genero_full = df.groupby("gender")[QUANT_COLS].mean().round(2)

# ---------------------------------------------------------------------------
# Layout
# ---------------------------------------------------------------------------
st.title("Dashboard - Students Performance in Exams")

st.markdown("""
Este dashboard apresenta uma análise exploratória do dataset
**Students Performance in Exams**, permitindo identificar padrões,
comparar grupos de estudantes e apoiar decisões educacionais.
""")

st.sidebar.header("Filtros")

genero = st.sidebar.multiselect(
    "Gênero", options=df["gender"].unique(), default=df["gender"].unique()
)
raca = st.sidebar.multiselect(
    "Grupo (race/ethnicity)", options=df["race/ethnicity"].unique(), default=df["race/ethnicity"].unique()
)
escolaridade_pais = st.sidebar.multiselect(
    "Escolaridade dos Pais",
    options=df["parental level of education"].unique(),
    default=df["parental level of education"].unique(),
)
almoco = st.sidebar.multiselect(
    "Tipo de Almoço", options=df["lunch"].unique(), default=df["lunch"].unique()
)
curso = st.sidebar.multiselect(
    "Curso Preparatório",
    options=df["test preparation course"].unique(),
    default=df["test preparation course"].unique(),
)

df_filtrado = df[
    df["gender"].isin(genero)
    & df["race/ethnicity"].isin(raca)
    & df["parental level of education"].isin(escolaridade_pais)
    & df["lunch"].isin(almoco)
    & df["test preparation course"].isin(curso)
]

tab_dashboard, tab_respostas = st.tabs(["📊 Dashboard de Análise", "📝 Respostas da Atividade"])

# ===========================================================================
# ABA 1 — DASHBOARD
# ===========================================================================
with tab_dashboard:

    st.header("Visão Geral da Base")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Linhas (base completa)", total_linhas)
    col2.metric("Colunas", total_colunas)
    col3.metric("Valores Ausentes", qtd_ausentes)
    col4.metric("Registros Duplicados", qtd_duplicados)

    st.divider()

    if df_filtrado.empty:
        st.warning(
            "Nenhum estudante corresponde aos filtros selecionados. "
            "Ajuste os filtros na barra lateral para visualizar os gráficos."
        )
    else:
        st.header("Indicadores Gerais (dados filtrados)")

        media_math = df_filtrado["math score"].mean()
        media_reading = df_filtrado["reading score"].mean()
        media_writing = df_filtrado["writing score"].mean()
        total_alunos = len(df_filtrado)

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Média Matemática", f"{media_math:.2f}")
        col2.metric("Média Leitura", f"{media_reading:.2f}")
        col3.metric("Média Escrita", f"{media_writing:.2f}")
        col4.metric("Total de Alunos", total_alunos)

        st.divider()

        st.header("🔤 Análise de Variáveis Qualitativas")
        st.caption("Variáveis escolhidas: **gênero** e **curso preparatório**.")

        freq_genero_filt = tabela_frequencia(df_filtrado["gender"], "Gênero")
        freq_prep_filt = tabela_frequencia(df_filtrado["test preparation course"], "Curso Preparatório")

        colA, colB = st.columns(2)
        with colA:
            st.subheader("Gênero")
            st.dataframe(freq_genero_filt, width="stretch", hide_index=True)
            fig_genero_bar = px.bar(
                freq_genero_filt, x="Gênero", y="Frequência Absoluta",
                text="Frequência Absoluta", title="Frequência Absoluta por Gênero",
            )
            st.plotly_chart(fig_genero_bar, width="stretch")
            fig_genero_pie = px.pie(
                freq_genero_filt, names="Gênero", values="Frequência Absoluta",
                title="Frequência Relativa por Gênero",
            )
            st.plotly_chart(fig_genero_pie, width="stretch")

        with colB:
            st.subheader("Curso Preparatório")
            st.dataframe(freq_prep_filt, width="stretch", hide_index=True)
            fig_prep_bar = px.bar(
                freq_prep_filt, x="Curso Preparatório", y="Frequência Absoluta",
                text="Frequência Absoluta", title="Frequência Absoluta por Curso Preparatório",
            )
            st.plotly_chart(fig_prep_bar, width="stretch")
            fig_prep_pie = px.pie(
                freq_prep_filt, names="Curso Preparatório", values="Frequência Absoluta",
                title="Frequência Relativa por Curso Preparatório",
            )
            st.plotly_chart(fig_prep_pie, width="stretch")

        st.divider()

        st.header("🔢 Análise de Variáveis Quantitativas")
        st.caption("Variáveis escolhidas: **nota de matemática** e **nota de leitura** (escrita também exibida para comparação).")

        stats_filt = pd.DataFrame({c: stats_quant(df_filtrado[c]) for c in QUANT_COLS}).T
        stats_filt.index.name = "Variável"
        st.dataframe(stats_filt.reset_index(), width="stretch", hide_index=True)

        fig_hist_math = px.histogram(
            df_filtrado, x="math score", nbins=20,
            title="Distribuição das Notas de Matemática",
        )
        st.plotly_chart(fig_hist_math, width="stretch")

        melted = df_filtrado.melt(value_vars=QUANT_COLS, var_name="Prova", value_name="Nota")
        fig_box_all = px.box(
            melted, x="Prova", y="Nota", color="Prova",
            title="Distribuição e Outliers das Notas por Prova",
        )
        st.plotly_chart(fig_box_all, width="stretch")

        st.divider()

        st.header("🔗 Relação entre Variáveis")

        st.subheader("1️⃣ Curso Preparatório × Nota de Matemática")
        fig2 = px.box(
            df_filtrado, x="test preparation course", y="math score",
            color="test preparation course", title="Impacto do Curso Preparatório",
        )
        st.plotly_chart(fig2, width="stretch")
        st.caption(
            "A relação sugere que concluir o curso preparatório está associado a notas mais altas em matemática. "
            "Não é possível afirmar causalidade: estudantes mais motivados ou com mais recursos podem ser, ao mesmo tempo, "
            "os que fazem o curso e os que teriam notas melhores por outros fatores (variável de confusão)."
        )

        st.subheader("2️⃣ Escolaridade dos Pais × Desempenho")
        media_pais = (
            df_filtrado.groupby("parental level of education")[QUANT_COLS].mean().reset_index()
        )
        fig3 = px.bar(
            media_pais, x="parental level of education", y=QUANT_COLS,
            barmode="group", title="Média das Notas por Escolaridade dos Pais",
        )
        st.plotly_chart(fig3, width="stretch")
        st.caption(
            "Filhos de pais com maior escolaridade tendem a apresentar médias mais altas. "
            "Essa relação é uma associação, não uma prova de causa-efeito: escolaridade dos pais é proxy de um "
            "contexto socioeconômico e cultural mais amplo (acesso a livros, tempo de apoio aos estudos, recursos financeiros)."
        )

        st.subheader("3️⃣ Tipo de Almoço × Desempenho")
        media_lunch = df_filtrado.groupby("lunch")[QUANT_COLS].mean().reset_index()
        fig_lunch = px.bar(
            media_lunch, x="lunch", y=QUANT_COLS, barmode="group",
            title="Média das Notas por Tipo de Almoço (proxy socioeconômico)",
        )
        st.plotly_chart(fig_lunch, width="stretch")
        st.caption(
            "O tipo de almoço (padrão x gratuito/reduzido) é a variável com a maior disparidade de médias observada na base, "
            "reforçando a hipótese de que a condição socioeconômica está associada ao desempenho. Ainda assim, é uma associação "
            "observacional — não há controle experimental que permita afirmar causalidade direta."
        )

        st.subheader("4️⃣ Leitura × Escrita")
        fig4 = px.scatter(
            df_filtrado, x="reading score", y="writing score", color="gender",
            title="Leitura x Escrita",
        )
        st.plotly_chart(fig4, width="stretch")
        st.caption(
            "As notas de leitura e escrita variam fortemente juntas, sugerindo que medem habilidades verbais relacionadas. "
            "Correlação forte não implica causalidade entre as duas provas."
        )

        st.subheader("5️⃣ Desempenho Médio por Gênero")
        media_genero = df_filtrado.groupby("gender")[QUANT_COLS].mean().reset_index()
        fig5 = px.bar(
            media_genero, x="gender", y=QUANT_COLS, barmode="group",
            title="Notas Médias por Gênero",
        )
        st.plotly_chart(fig5, width="stretch")

        st.subheader("Correlação entre as Notas")
        corr = df_filtrado[QUANT_COLS].corr()
        heatmap = ff.create_annotated_heatmap(
            z=corr.values, x=list(corr.columns), y=list(corr.index),
            annotation_text=round(corr, 2).values, showscale=True,
        )
        st.plotly_chart(heatmap, width="stretch")
        st.markdown("""
**Interpretação:**

- Valores próximos de **1** indicam forte correlação positiva.
- Valores próximos de **0** indicam baixa correlação.
- Quanto maior a correlação, maior a tendência de as variáveis variarem juntas.
""")

        st.divider()

        st.header("🚦 Insights e Alertas para Tomada de Decisão")

        grupo_completou = df_filtrado[df_filtrado["test preparation course"] == "completed"]
        grupo_nao_completou = df_filtrado[df_filtrado["test preparation course"] == "none"]

        if len(grupo_completou) > 0 and len(grupo_nao_completou) > 0:
            curso_concluido = grupo_completou["math score"].mean()
            curso_nao = grupo_nao_completou["math score"].mean()

            st.info(f"""
            Média geral de Matemática: {media_math:.2f}

            Média de Matemática dos alunos que concluíram o curso preparatório: {curso_concluido:.2f}

            Média de Matemática dos alunos que não realizaram o curso: {curso_nao:.2f}
            """)

            if curso_concluido > curso_nao:
                st.success(
                    "Os dados sugerem que estudantes que concluíram o curso preparatório apresentam melhor "
                    "desempenho médio em matemática."
                )
            else:
                st.warning(
                    "Não foi observada vantagem clara para os estudantes que realizaram o curso preparatório."
                )
        else:
            st.info("Selecione as duas categorias de curso preparatório no filtro lateral para comparar o desempenho.")

        st.subheader("Exemplo de alerta automático — risco por condição socioeconômica")
        nota_corte = st.slider("Nota de corte para considerar risco em matemática", 0, 100, 60)

        grupo_reduzido = df_filtrado[df_filtrado["lunch"] == "free/reduced"]
        grupo_padrao = df_filtrado[df_filtrado["lunch"] == "standard"]

        if len(grupo_reduzido) > 0 and len(grupo_padrao) > 0:
            pct_risco_reduzido = (grupo_reduzido["math score"] < nota_corte).mean() * 100
            pct_risco_padrao = (grupo_padrao["math score"] < nota_corte).mean() * 100
            diferenca = pct_risco_reduzido - pct_risco_padrao

            if diferenca > 15:
                st.error(
                    f"⚠️ Alerta: {pct_risco_reduzido:.1f}% dos estudantes com almoço gratuito/reduzido estão abaixo de "
                    f"{nota_corte} pontos em matemática, contra {pct_risco_padrao:.1f}% dos estudantes com almoço padrão "
                    f"— uma diferença de {diferenca:.1f} pontos percentuais."
                )
            else:
                st.info(
                    f"Estudantes com almoço reduzido: {pct_risco_reduzido:.1f}% em risco. "
                    f"Estudantes com almoço padrão: {pct_risco_padrao:.1f}% em risco."
                )
        else:
            st.info("Selecione as duas categorias de almoço no filtro lateral para gerar o alerta.")

        st.markdown("""
### Possíveis Aplicações em Sistemas de Apoio à Decisão

- Identificação de grupos com maior risco de baixo desempenho;
- Avaliação da efetividade de cursos preparatórios;
- Planejamento de programas de reforço escolar;
- Monitoramento de indicadores acadêmicos;
- Apoio à formulação de políticas educacionais.
""")

        st.divider()

        st.header("Estatísticas Descritivas Completas")
        st.dataframe(df_filtrado.describe(), width="stretch")

        st.divider()

        st.header("Dados Filtrados")
        st.dataframe(df_filtrado, width="stretch")

    st.divider()

    st.header("Qualidade dos Dados (base completa)")

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Valores Ausentes")
        missing = df.isnull().sum().reset_index()
        missing.columns = ["Variável", "Valores Ausentes"]
        st.dataframe(missing, width="stretch", hide_index=True)
    with col2:
        st.subheader("Registros Duplicados")
        st.metric("Quantidade", qtd_duplicados)

    st.divider()
    st.caption("Dashboard desenvolvido para análise exploratória do dataset Students Performance in Exams.")

# ===========================================================================
# ABA 2 — RESPOSTAS DA ATIVIDADE
# ===========================================================================
with tab_respostas:

    st.markdown("""
As respostas abaixo se referem **à base completa** (sem os filtros da barra lateral),
pois representam a caracterização fixa do dataset usado na atividade.
""")

    with st.expander("1. Escolha e Contexto da Base", expanded=True):
        st.markdown(f"""
**1.1 Qual dataset foi escolhido?**
Students Performance in Exams (Kaggle, autor *spscientist*).

**1.2 Qual é o contexto da base de dados?**
A base reúne registros de **{total_linhas} estudantes** que realizaram três provas padronizadas
(matemática, leitura e escrita), junto com atributos demográficos e socioeconômicos: gênero, grupo
étnico anonimizado (race/ethnicity), nível de escolaridade dos responsáveis, tipo de almoço recebido
(proxy de condição socioeconômica) e participação em um curso preparatório para a prova.

**1.3 Que tipo de organização poderia usar esses dados?**
Secretarias e redes de ensino, escolas, ONGs educacionais, plataformas de tutoria e pesquisadores
da área de educação interessados em entender fatores associados ao desempenho escolar.

**1.4 Qual decisão poderia ser apoiada com esses dados?**
A priorização de investimentos em cursos preparatórios e programas de apoio pedagógico para os
grupos de estudantes com desempenho médio mais baixo (por exemplo, estudantes com almoço
gratuito/reduzido ou cujos responsáveis têm menor escolaridade).
""")

    with st.expander("2. Problema de Decisão"):
        st.markdown("""
**2.1 Qual é o problema de decisão que será analisado?**
Quais fatores demográficos e de preparo (curso preparatório, escolaridade dos pais, condição
socioeconômica aproximada pelo tipo de almoço) estão associados a um melhor ou pior desempenho nas
provas, e onde a escola/rede deveria concentrar esforços de apoio pedagógico?

**2.2 Quem seria o usuário interessado nessa análise?**
Coordenação pedagógica, direção escolar ou gestores de secretaria de educação responsáveis por
alocar recursos de reforço escolar e programas de apoio ao estudante.

**2.3 Qual pergunta inicial de análise pode ser formulada?**
"Estudantes que concluem o curso preparatório e/ou têm acesso a almoço padrão apresentam desempenho
significativamente superior nas provas de matemática, leitura e escrita?"

**2.4 A análise será mais descritiva, diagnóstica, preditiva ou prescritiva? Justifique.**
A análise é principalmente **descritiva** (resume o que ocorreu por meio de médias, distribuições e
frequências) e **diagnóstica** (investiga associações entre variáveis explicativas e o desempenho,
buscando entender possíveis razões para as diferenças entre grupos). Não é preditiva, pois não há um
modelo treinado para prever notas de novos estudantes; também não é prescritiva, pois a base não
recomenda automaticamente uma ação ótima — ela fornece evidências para apoiar uma decisão humana.
""")

    with st.expander("3. Conhecimento Inicial da Base"):
        st.markdown(f"""
**3.1 Quantas linhas a base possui?** {total_linhas} linhas.

**3.2 Quantas colunas a base possui?** {total_colunas} colunas.

**3.3 O que cada linha representa?** Um estudante que realizou as três provas (matemática, leitura
e escrita), com seus respectivos atributos demográficos e socioeconômicos.

**3.4 O que cada coluna representa?** Cinco colunas são atributos categóricos do estudante (gênero,
grupo étnico anonimizado, escolaridade dos pais, tipo de almoço e participação no curso preparatório)
e três colunas são as notas obtidas em cada prova.

**3.5 Qual é a unidade de investigação da base?** O estudante individual.

**3.6 Existe alguma variável identificadora? Qual?** Não há uma variável identificadora explícita
(sem número de matrícula ou ID). Cada estudante é identificado apenas pela posição (índice) no
arquivo.
""")

    with st.expander("4. Classificação das Variáveis"):
        st.markdown("""
Foram classificadas as 8 variáveis da base:

| Variável | Descrição | Classificação |
|---|---|---|
| `gender` | Sexo do estudante (feminino/masculino). | Qualitativa nominal |
| `race/ethnicity` | Grupo étnico/racial do estudante, anonimizado em categorias de A a E. | Qualitativa nominal |
| `parental level of education` | Nível de escolaridade dos responsáveis do estudante. | Qualitativa ordinal |
| `lunch` | Tipo de almoço recebido (padrão ou gratuito/reduzido); proxy de condição socioeconômica. | Qualitativa nominal |
| `test preparation course` | Indica se o estudante concluiu o curso preparatório para a prova. | Qualitativa nominal |
| `math score` | Nota obtida na prova de matemática (0 a 100). | Quantitativa discreta |
| `reading score` | Nota obtida na prova de leitura (0 a 100). | Quantitativa discreta |
| `writing score` | Nota obtida na prova de escrita (0 a 100). | Quantitativa discreta |
""")

    with st.expander("5. Qualidade dos Dados"):
        st.markdown(f"""
**5.1 Existem valores ausentes?** Não. Todas as colunas têm 0 valores ausentes
(total verificado: {qtd_ausentes}).

**5.2 Existem registros duplicados?** Não. Total de duplicados: {qtd_duplicados}.

**5.3 Existem variáveis com nomes pouco claros?** Sim. `race/ethnicity` usa categorias codificadas
("group A" a "group E") sem revelar o critério real usado — provavelmente anonimizado por motivos
éticos/privacidade, o que reduz a interpretabilidade da variável.

**5.4 Existem categorias inconsistentes?** Não foram encontradas grafias duplicadas ou inconsistências
nas colunas categóricas; cada uma possui um conjunto fixo e coerente de valores.

**5.5 Existem valores impossíveis ou suspeitos?** Sim. `math score` tem valor mínimo {int(df['math score'].min())},
enquanto `reading score` (mín. {int(df['reading score'].min())}) e `writing score`
(mín. {int(df['writing score'].min())}) nunca chegam a 0. Isso é suspeito: sugere uma possível
ausência/abandono da prova de matemática por aquele estudante, registrada como 0 em vez de dado
ausente.

**5.6 Existem colunas numéricas que, na verdade, representam códigos?** Não. As três colunas de nota
são, de fato, variáveis quantitativas. A única "codificação" está em `race/ethnicity`, mas já é
categórica (texto), não numérica.

**5.7 Existem datas? Elas estão em formato adequado?** Não há nenhuma variável temporal na base
(sem data da prova, ano escolar, etc.) — isso é uma limitação para qualquer análise de evolução no
tempo.

**Principais problemas encontrados:**

| Problema encontrado | Variável afetada | Possível tratamento |
|---|---|---|
| Categorias codificadas sem significado declarado | `race/ethnicity` | Documentar o significado real dos grupos A-E junto à fonte, ou tratá-los apenas como categoria anônima sem inferir etnia. |
| Valor possivelmente impossível/suspeito (nota mínima muito abaixo das demais provas) | `math score` (valor mínimo = 0) | Investigar se nota 0 indica ausência/abandono da prova; em caso afirmativo, tratar como valor ausente (NaN) em vez de 0. |
| Ausência de variável identificadora | (toda a base) | Criar um índice artificial (ID sequencial) ao carregar os dados, para permitir rastreabilidade em relatórios. |
| Ausência de variável temporal | (toda a base) | Documentar como limitação; impossibilita qualquer análise de evolução temporal do desempenho. |
| Nomenclatura binária pouco intuitiva | `test preparation course` | Renomear para algo como `curso_preparatorio_concluido` (booleano), tornando a leitura mais intuitiva. |
""")

    with st.expander("6. Análise de Variáveis Qualitativas"):
        st.markdown(f"""
**6.1 Quais variáveis foram escolhidas?** `gender` (gênero) e `test preparation course`
(curso preparatório).

**6.2 Qual é a frequência absoluta de cada categoria?**
Gênero: feminino = {n_female}, masculino = {n_male}.
Curso preparatório: none = {n_none}, completed = {n_completed}.

**6.3 Qual é a frequência relativa de cada categoria?**
Gênero: feminino = {pct_female:.1f}%, masculino = {pct_male:.1f}%.
Curso preparatório: none = {pct_none:.1f}%, completed = {pct_completed:.1f}%.

**6.4 Qual categoria aparece com maior frequência?**
Em gênero, **feminino**. Em curso preparatório, **none** — ou seja, a maioria dos estudantes não
realizou o curso preparatório.

**6.5 Há alguma categoria rara, inconsistente ou inesperada?**
Dentro de `race/ethnicity`, "group A" é a menos frequente ({n_groupA} estudantes, {pct_groupA:.1f}%).
Dentro de `parental level of education`, "master's degree" é a mais rara ({n_master} estudantes,
{pct_master:.1f}%). Nenhuma é inconsistente, apenas pouco representada na amostra.

**6.6 Que gráfico foi utilizado para representar a variável?**
Gráfico de barras (frequência absoluta) e gráfico de pizza (frequência relativa), disponíveis na
aba *Dashboard de Análise*.
""")
        colA, colB = st.columns(2)
        with colA:
            st.markdown("**Gênero**")
            st.dataframe(freq_genero_full, width="stretch", hide_index=True)
        with colB:
            st.markdown("**Curso Preparatório**")
            st.dataframe(freq_prep_full, width="stretch", hide_index=True)

    with st.expander("7. Análise de Variáveis Quantitativas"):
        st.markdown(f"""
**7.1 Quais variáveis foram escolhidas?** `math score` e `reading score`
(`writing score` também é exibida para comparação).

**7.2 Qual é a média de cada variável?**
Matemática = {stats_full.loc['math score', 'Média']}, Leitura = {stats_full.loc['reading score', 'Média']}.

**7.3 Qual é a mediana de cada variável?**
Matemática = {stats_full.loc['math score', 'Mediana']}, Leitura = {stats_full.loc['reading score', 'Mediana']}.

**7.4 Qual é o valor mínimo?**
Matemática = {stats_full.loc['math score', 'Mínimo']}, Leitura = {stats_full.loc['reading score', 'Mínimo']}.

**7.5 Qual é o valor máximo?**
Matemática = {stats_full.loc['math score', 'Máximo']}, Leitura = {stats_full.loc['reading score', 'Máximo']}.

**7.6 Qual é o desvio padrão?**
Matemática = {stats_full.loc['math score', 'Desvio Padrão']}, Leitura = {stats_full.loc['reading score', 'Desvio Padrão']}.

**7.7 Existem valores extremos?**
Sim, valores baixos identificados pela regra do IQR (1,5×). Em matemática: {outliers_math}.
Em leitura: {outliers_reading}. Não há outliers no topo, já que 100 é o teto da prova.

**7.8 A média e a mediana são parecidas? O que isso pode indicar?**
Sim, a diferença é menor que 1 ponto em ambas as variáveis, o que indica uma distribuição
aproximadamente simétrica. Mesmo havendo outliers baixos, eles não distorcem fortemente a média
porque representam uma pequena fração dos casos.

**7.9 Que gráficos foram utilizados?**
Histograma (distribuição da nota de matemática) e boxplot comparativo das três provas (para
visualizar dispersão e outliers), ambos na aba *Dashboard de Análise*.
""")
        st.dataframe(stats_full.reset_index(), width="stretch", hide_index=True)

    with st.expander("8. Relação entre Variáveis"):
        st.markdown(f"""
**Relação 1 — Curso preparatório × nota de matemática**
1. Variáveis comparadas: `test preparation course` e `math score`.
2. Gráfico: boxplot.
3. Estudantes que concluíram o curso têm média de matemática de {media_prep_full['completed']}, contra
{media_prep_full['none']} dos que não fizeram — uma diferença de cerca de
{media_prep_full['completed'] - media_prep_full['none']:.2f} pontos.
4. Pode apoiar a decisão de expandir a oferta/incentivo ao curso preparatório.
5. Não é possível afirmar causalidade: estudantes mais motivados ou com mais recursos podem ser,
ao mesmo tempo, os que fazem o curso e os que teriam notas melhores por outros motivos
(variável de confusão). É uma associação observacional, não um experimento controlado.

**Relação 2 — Escolaridade dos pais × desempenho médio**
1. Variáveis comparadas: `parental level of education` e as três notas.
2. Gráfico: barras agrupadas.
3. Filhos de pais com mestrado têm as maiores médias (matemática {media_pais_full.loc["master's degree","math score"]},
leitura {media_pais_full.loc["master's degree","reading score"]}, escrita {media_pais_full.loc["master's degree","writing score"]}),
enquanto filhos de pais que completaram apenas o ensino médio ("high school") têm as menores médias
(matemática {media_pais_full.loc["high school","math score"]}, leitura {media_pais_full.loc["high school","reading score"]},
escrita {media_pais_full.loc["high school","writing score"]}).
4. Pode apoiar a priorização de apoio extra para estudantes cujos responsáveis têm menor escolaridade.
5. Não se pode afirmar causalidade direta: escolaridade dos pais é proxy de um contexto socioeconômico
e cultural mais amplo (acesso a livros, tempo de apoio aos estudos, recursos financeiros).

**Relação 3 (extra) — Tipo de almoço × desempenho**
1. Variáveis comparadas: `lunch` e as três notas.
2. Gráfico: barras agrupadas.
3. A diferença é a maior observada na base: matemática {media_lunch_full.loc['free/reduced','math score']}
(almoço reduzido) vs {media_lunch_full.loc['standard','math score']} (almoço padrão) — quase
{media_lunch_full.loc['standard','math score'] - media_lunch_full.loc['free/reduced','math score']:.0f} pontos de diferença.
4. Reforça a hipótese de que a condição socioeconômica (aproximada pelo tipo de almoço) é o fator
mais associado ao desempenho nesta base, podendo apoiar políticas de apoio socioeconômico.
5. Mesma ressalva: associação, não causalidade comprovada — `lunch` é apenas um proxy indireto de
renda familiar.
""")

    with st.expander("9. Relação com Sistemas de Apoio à Decisão"):
        st.markdown("""
**9.1 Que decisão poderia ser apoiada com os resultados encontrados?**
Priorização de programas de reforço escolar e de oferta gratuita de cursos preparatórios para
grupos de estudantes com maior risco de baixo desempenho (ex.: almoço reduzido, pais com menor
escolaridade).

**9.2 Quem seria o usuário do sistema?**
Coordenadores pedagógicos, diretores escolares e gestores de secretarias de educação.

**9.3 Que indicadores deveriam aparecer em um painel de apoio à decisão?**
- Médias e medianas de cada prova, por turma/escola e por grupo socioeconômico;
- Percentual de estudantes abaixo de uma nota de corte (em risco);
- Taxa de adesão ao curso preparatório;
- Comparação de desempenho entre quem fez e quem não fez o curso preparatório;
- Disparidade de desempenho por tipo de almoço (indicador de equidade socioeconômica).

**9.4 Que alertas poderiam ser gerados?**
- Alerta quando a média de uma turma/grupo cair abaixo de um limiar definido;
- Alerta de baixa adesão ao curso preparatório em grupos mais vulneráveis;
- Alerta quando a disparidade de desempenho entre grupos socioeconômicos superar um percentual
  crítico (como demonstrado no exemplo interativo da aba *Dashboard*).

**9.5 Que cuidados éticos devem ser considerados?**
Evitar usar atributos sensíveis (gênero, grupo étnico, condição socioeconômica) para decisões
individuais discriminatórias; trabalhar com dados agregados; preservar a anonimização já presente
na base (grupos "A" a "E"); e não confundir correlação com causalidade ao comunicar resultados,
para não estigmatizar grupos específicos.

**9.6 Quais são as limitações da base de dados?**
A documentação pública do dataset não identifica a escola, rede de ensino, país ou ano de coleta,
o que sugere finalidade didática/exemplificativa; não há variável temporal; não há dados de
frequência escolar ou contexto curricular; a amostra de 1.000 estudantes pode não ser representativa
de outras populações; e os grupos de `race/ethnicity` são anônimos, sem significado declarado.
""")

    with st.expander("10. Conclusão"):
        st.markdown(f"""
**10.1 Quais foram os principais achados da análise?**
O curso preparatório, a escolaridade dos pais e, sobretudo, o tipo de almoço (proxy socioeconômico)
estão associados a diferenças relevantes nas notas de matemática, leitura e escrita. As notas de
leitura e escrita são fortemente correlacionadas entre si (r = {corr_full.loc['reading score','writing score']}),
enquanto a correlação com matemática é um pouco menor (r ≈ {corr_full.loc['math score','reading score']}).
Também há diferença por gênero: meninas têm médias mais altas em leitura e escrita
(reading {media_genero_full.loc['female','reading score']}, writing {media_genero_full.loc['female','writing score']})
e meninos em matemática (math {media_genero_full.loc['male','math score']}).

**10.2 Que evidências os dados apresentaram?**
Estatísticas descritivas (médias, medianas, desvios-padrão) e correlações consistentes, calculadas
diretamente sobre a base completa, sem nenhum teste de hipótese formal — portanto as evidências são
descritivas/diagnósticas, não inferenciais.

**10.3 Que recomendação poderia ser feita com base nos dados?**
Expandir o acesso ao curso preparatório, priorizando estudantes com almoço gratuito/reduzido e
responsáveis com menor escolaridade, que são os grupos com médias mais baixas na base.

**10.4 Quais cuidados devem ser tomados antes de usar essa análise para uma decisão real?**
A base não declara sua origem institucional, o que impede validar sua representatividade; as
relações encontradas são associações observacionais, não relações de causa e efeito; e qualquer
política pública baseada nesses achados deveria ser complementada com dados longitudinais, contexto
qualitativo e, idealmente, dados de uma população real e documentada antes de qualquer decisão.
""")
