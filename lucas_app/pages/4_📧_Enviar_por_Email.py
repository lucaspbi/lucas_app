import streamlit as st
from utils import (
    NOME_EMPRESA, load_data, render_sidebar_usuario, saudacao,
    GRAFICOS_DISPONIVEIS, gerar_png_bytes,
    obter_config_smtp_padrao, enviar_email,
)

st.set_page_config(
    page_title=f"{NOME_EMPRESA} — Enviar por E-mail",
    page_icon="📧",
    layout="wide",
)

with st.sidebar:
    render_sidebar_usuario()

df = load_data()
saudacao()

st.markdown("## 📧 Enviar por E-mail")
st.markdown(
    "Escolha o gráfico, informe o destinatário e envie clicando no botão abaixo."
)
st.markdown("---")

# ── Credenciais de envio (sempre vindas dos secrets do Streamlit) ──────────
smtp_host, smtp_port, remetente, senha = obter_config_smtp_padrao()

if remetente is None:
    st.error(
        "⚠️ Nenhuma credencial de e-mail configurada. Configure os secrets "
        "(host, porta, e-mail remetente e senha de App Password) no painel do "
        "Streamlit Cloud, em Settings → Secrets, antes de usar esta página."
    )
    st.stop()

# ── 1. Escolha do gráfico ───────────────────────────────────────────────────
grafico_escolhido = st.selectbox(
    "1️⃣ Escolha o gráfico que deseja enviar", list(GRAFICOS_DISPONIVEIS.keys())
)
fig_preview = GRAFICOS_DISPONIVEIS[grafico_escolhido](df)
st.plotly_chart(fig_preview, width='stretch')

st.markdown("---")

# ── 2. Destinatário ──────────────────────────────────────────────────────────
destinatario = st.text_input(
    "2️⃣ E-mail do destinatário",
    placeholder="Ex: lucas@analytics.com",
)

# ── 3. Assunto ───────────────────────────────────────────────────────────────
assunto = st.text_input(
    "3️⃣ Assunto",
    placeholder=f" Ex: {NOME_EMPRESA} — Gráfico de Churn: {grafico_escolhido}",
)

# ── 4. Corpo do e-mail ───────────────────────────────────────────────────────

corpo = st.text_area(
"4️⃣ Corpo do e-mail",
    placeholder="Digite seu texto",
    height=180
)

st.markdown("---")

# ── 5. Enviar (botão compacto) ───────────────────────────────────────────────
enviar_clicado = st.button(
"📤 Enviar",
    type="primary",
    width='content'
)

if enviar_clicado:
    if not destinatario:
        st.error("Preencha o e-mail do destinatário antes de enviar.")
    else:
        with st.spinner("Gerando gráfico..."):
            png_bytes = gerar_png_bytes(fig_preview)

        with st.spinner("Enviando e-mail..."):
            sucesso, mensagem = enviar_email(
                smtp_host, smtp_port, remetente, senha, destinatario,
                assunto, corpo,
                anexo_bytes=png_bytes, anexo_nome="grafico_churn.png",
            )

        if sucesso:
            st.success(f"✅ {mensagem}")
        else:
            st.error(f"❌ {mensagem}")
