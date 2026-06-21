import streamlit as st
from utils import NOME_EMPRESA, ICONE_EMPRESA, load_data, render_sidebar_usuario, saudacao, get_nome_usuario

st.set_page_config(
    page_title=f"{NOME_EMPRESA} — Tabela de Dados",
    page_icon="📊",
    layout="wide",
)

with st.sidebar:
    render_sidebar_usuario()

df = load_data()
saudacao()
get_nome_usuario()

st.markdown("## 📊 Tabela de Dados")
st.markdown("Visualize e filtre os dados dos clientes.")
st.markdown("---")

# ── Filtros ──────────────────────────────────────────────────────────────
col1, col2, col3 = st.columns(3)
with col1:
    filtro_churn = st.selectbox("Filtrar por Churn", ["Todos", "Yes", "No"])
with col2:
    filtro_contrato = st.selectbox(
        "Filtrar por Contrato",
        ["Todos"] + sorted(df["Contract"].dropna().unique().tolist()),
    )
with col3:
    filtro_internet = st.selectbox(
        "Filtrar por Internet",
        ["Todos"] + sorted(df["Internet Service"].dropna().unique().tolist()),
    )

df_filtrado = df.copy()
if filtro_churn != "Todos":
    df_filtrado = df_filtrado[df_filtrado["Churn Label"] == filtro_churn]
if filtro_contrato != "Todos":
    df_filtrado = df_filtrado[df_filtrado["Contract"] == filtro_contrato]
if filtro_internet != "Todos":
    df_filtrado = df_filtrado[df_filtrado["Internet Service"] == filtro_internet]

st.markdown(f"**{len(df_filtrado):,} registros encontrados**")

colunas_disponiveis = [
    "Customer ID", "Gender", "Age", "Senior Citizen", "Married",
    "Contract", "Tenure in Months", "Monthly Charge", "Total Charges",
    "Internet Service", "Churn Label", "Churn Category", "Churn Reason",
    "Satisfaction Score", "Customer Status",
]
colunas_exibir = [c for c in colunas_disponiveis if c in df_filtrado.columns]

# ── Paginação (mantém a tabela sempre estática, mesmo com muitas linhas) ──
TAMANHO_PAGINA = 25
total_paginas = max((len(df_filtrado) - 1) // TAMANHO_PAGINA + 1, 1)

col_pag, _ = st.columns([1, 4])
with col_pag:
    pagina_atual = st.number_input(
        "Página", min_value=1, max_value=total_paginas, value=1, step=1
    )

inicio = (pagina_atual - 1) * TAMANHO_PAGINA
fim = inicio + TAMANHO_PAGINA
df_pagina = df_filtrado[colunas_exibir].iloc[inicio:fim].reset_index(drop=True)

st.caption(f"Exibindo registros {inicio + 1} a {min(fim, len(df_filtrado))} de {len(df_filtrado):,} "
           f"(página {pagina_atual} de {total_paginas})")

st.table(df_pagina)