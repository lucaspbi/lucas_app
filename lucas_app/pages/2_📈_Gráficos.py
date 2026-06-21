import streamlit as st
from utils import (
    NOME_EMPRESA, load_data, render_sidebar_usuario, saudacao,
    fig_pizza_churn, fig_categoria_churn, fig_motivos_especificos,
    fig_contrato, fig_tenure_hist, fig_monthly_box, fig_satisfacao,
    fig_internet_tipo, fig_servicos_adicionais, fig_genero,
    fig_faixa_etaria, fig_cltv_scatter,
)

st.set_page_config(
    page_title=f"{NOME_EMPRESA} — Gráficos",
    page_icon="📈",
    layout="wide",
)

with st.sidebar:
    render_sidebar_usuario()

df = load_data()
saudacao()

st.markdown("## 📈 Análise de Churn")
st.markdown(
    "Os gráficos abaixo são **interativos** (passe o mouse, dê zoom, filtre a "
    "legenda) e cobrem desde a visão geral do cancelamento até o perfil dos clientes."
)
st.markdown("---")

st.markdown("### 1. Proporção Geral de Churn")
st.plotly_chart(fig_pizza_churn(df), width='stretch')
st.divider()

st.markdown("### 2. Motivos de Cancelamento")
col1, col2 = st.columns(2)
with col1:
    st.plotly_chart(fig_categoria_churn(df), width='stretch')
with col2:
    st.plotly_chart(fig_motivos_especificos(df), width='stretch')
st.divider()

st.markdown("### 3. Churn por Tipo de Contrato")
st.plotly_chart(fig_contrato(df), width='stretch')
st.divider()

st.markdown("### 4. Tempo de Permanência e Cobrança Mensal")
col1, col2 = st.columns(2)
with col1:
    st.plotly_chart(fig_tenure_hist(df), width='stretch')
with col2:
    st.plotly_chart(fig_monthly_box(df), width='stretch')
st.divider()

st.markdown("### 5. Satisfação dos Clientes")
st.plotly_chart(fig_satisfacao(df), width='stretch')
st.divider()

st.markdown("### 6. Serviços e Churn")
col1, col2 = st.columns(2)
with col1:
    st.plotly_chart(fig_internet_tipo(df), width='stretch')
with col2:
    st.plotly_chart(fig_servicos_adicionais(df), width='stretch')
st.divider()

st.markdown("### 7. Perfil Demográfico dos Clientes que Cancelaram")
col1, col2 = st.columns(2)
with col1:
    st.plotly_chart(fig_genero(df), width='stretch')
with col2:
    st.plotly_chart(fig_faixa_etaria(df), width='stretch')
st.divider()

st.markdown("### 8. Valor de Vida do Cliente (CLTV)")
st.plotly_chart(fig_cltv_scatter(df), width='stretch')
