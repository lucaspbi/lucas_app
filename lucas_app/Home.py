import streamlit as st
from utils import (
    NOME_EMPRESA, ICONE_EMPRESA,
    load_data, render_sidebar_usuario,
)

st.set_page_config(
    page_title=f"{NOME_EMPRESA} — Início",
    page_icon=ICONE_EMPRESA,
    layout="wide",
    initial_sidebar_state="expanded",
)

with st.sidebar:
    render_sidebar_usuario()

df = load_data()

col1, col2 = st.columns([2, 1])

with col1:
    st.markdown(f"# {ICONE_EMPRESA} {NOME_EMPRESA}")
    st.markdown("### *Transformando dados em decisões*")
    st.markdown("---")
    st.markdown("#### Sobre a empresa")
    st.info(
        f"""
          **{NOME_EMPRESA}** é uma consultoria fictícia criada para este projeto de
          Data Visualization, especializada em diagnóstico de churn para empresas de
          telecomunicações.

          Combinamos visualização de dados e estatística aplicada para transformar
          números em decisões de retenção de clientes.
          """
    )
    st.markdown("---")
    st.markdown("#### 📂 Sobre a Base de Dados")

    total = len(df)
    cancelados = int((df["Churn Label"] == "Yes").sum())
    permaneceram = int((df["Churn Label"] == "No").sum())
    taxa = round(cancelados / total * 100, 1) if total else 0

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total de Clientes", f"{total:,}")
    c2.metric("Cancelamentos", f"{cancelados:,}")
    c3.metric("Taxa de Churn", f"{taxa}%")
    c4.metric("Clientes Retidos", f"{permaneceram:,}")

    st.markdown("---")
    st.markdown("####  O que você encontra neste painel")
    st.markdown(
        """
        - **Tabela de Dados** — visualização e filtragem da base de clientes.
        - **Gráficos** — análise visual completa dos fatores associados ao churn.
        - **Relatório** — análise geral com insights e recomendações, disponível para
          download em arquivo `.txt`.
        - **Enviar por E-mail** — envie um gráfico estático ou o relatório de insights
          diretamente para o seu e-mail.
        """
    )
