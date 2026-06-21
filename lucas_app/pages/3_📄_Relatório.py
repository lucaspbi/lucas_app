import streamlit as st
from utils import NOME_EMPRESA, load_data, render_sidebar_usuario, saudacao, gerar_relatorio_insights

st.set_page_config(
    page_title=f"{NOME_EMPRESA} — Relatório",
    page_icon="📄",
    layout="wide",
)

with st.sidebar:
    render_sidebar_usuario()

df = load_data()
saudacao()

st.markdown("## 📄 Relatório de Insights")
st.markdown(
    "Análise geral da base de clientes, com os principais motivos de cancelamento "
    "encontrados nos dados e recomendações baseadas em dados para a empresa."
)
st.markdown("---")

relatorio = gerar_relatorio_insights(df)

st.text(relatorio)

st.markdown("---")
st.markdown("### ⬇️ Download")
st.markdown("Baixe este relatório completo em um arquivo de texto (`.txt`):")

st.download_button(
    label="⬇️ Baixar Relatório (.txt)",
    data=relatorio.encode("utf-8"),
    file_name="relatorio_churn.txt",
    mime="text/plain",
    width='content',
)
