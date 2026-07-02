"""
utils.py
Funções e dados compartilhados entre todas as páginas do app.
Mantendo essa lógica centralizada aqui, cada página (arquivo) fica curta e
focada apenas na exibição.
"""

import io
import smtplib
from pathlib import Path
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.io as pio
import matplotlib
matplotlib.use("Agg")  # backend sem interface gráfica, necessário no servidor
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns

sns.set_theme(style="whitegrid")

NOME_EMPRESA = "Lucas Coltri Analytics"
ICONE_EMPRESA = "📈"
CORES = {
    "sim": "#EF553B",   # Cancelou
    "nao": "#00CC96",   # Permaneceu
    "primaria": "#636EFA",
    "seq_vermelho": "RdYlGn",
    "seq_laranja": "OrRd",
}



@st.cache_data
def load_data(caminho: str = None) -> pd.DataFrame:
    if caminho is None:
        # Resolve o caminho relativo à pasta onde este arquivo (utils.py) está,
        # assim funciona em qualquer máquina/sistema, desde que telco.csv
        # esteja na mesma pasta do projeto (junto com Home.py e utils.py).
        caminho = Path(__file__).resolve().parent / "telco.csv"
    df = pd.read_csv(caminho)

    # Faixa etária, usada em mais de uma página
    if "Age" in df.columns:
        df["Faixa Etária"] = pd.cut(
            df["Age"], bins=[0, 30, 45, 60, 120],
            labels=["<30", "30-45", "45-60", "60+"]
        )
    return df


# ---------------------------------------------------------------------------
# 2. SIDEBAR / SESSÃO / SAUDAÇÃO
# ---------------------------------------------------------------------------
def render_sidebar_usuario():
    st.markdown(f"## {ICONE_EMPRESA} {NOME_EMPRESA}")
    st.markdown("---")
    if "nome_usuario" not in st.session_state:
        st.session_state["nome_usuario"] = st.query_params.get("nome", "")

    st.text_input(
        "Seu nome",
        placeholder="Digite seu nome...",
        key="nome_usuario",
        on_change=_salvar_nome_na_url,
    )
    st.markdown("---")


def _salvar_nome_na_url():
    nome = st.session_state.get("nome_usuario", "").strip()
    if nome:
        st.query_params["nome"] = nome
    elif "nome" in st.query_params:
        del st.query_params["nome"]


def saudacao() -> str:
    nome = st.session_state.get("nome_usuario", "").strip()
    if nome:
        st.markdown(f"### Olá, **{nome}**!")
    else:
        st.markdown("### Olá!")
        st.caption("Dica: digite seu nome na barra lateral para uma experiência personalizada.")
    return nome


def get_nome_usuario() -> str:
    return st.session_state.get("nome_usuario", "").strip()


# 3. GRÁFICOS (funções reutilizadas na página de Gráficos e na página de E-mail,
#    que precisa gerar a versão estática/PNG dos mesmos gráficos)
# ---------------------------------------------------------------------------
def fig_pizza_churn(df):
    contagem = df["Churn Label"].value_counts().reset_index()
    contagem.columns = ["Status", "Quantidade"]
    fig = px.pie(
        contagem, names="Status", values="Quantidade", color="Status",
        color_discrete_map={"Yes": CORES["sim"], "No": CORES["nao"]},
        hole=0.45, title="Clientes que cancelaram vs. permaneceram",
    )
    fig.update_traces(textinfo="percent+label+value")
    fig.update_layout(legend_title_text="Churn")
    return fig


def fig_categoria_churn(df):
    cat = df[df["Churn Label"] == "Yes"]["Churn Category"].value_counts().reset_index()
    cat.columns = ["Categoria", "Quantidade"]
    fig = px.bar(
        cat, x="Quantidade", y="Categoria", orientation="h",
        color="Quantidade", color_continuous_scale=CORES["seq_vermelho"],
        title="Categorias de Motivo de Cancelamento",
    )
    fig.update_layout(yaxis_title="", xaxis_title="Nº de Cancelamentos", coloraxis_showscale=False)
    return fig


def fig_motivos_especificos(df):
    motivo = df[df["Churn Label"] == "Yes"]["Churn Reason"].value_counts().head(10).reset_index()
    motivo.columns = ["Motivo", "Quantidade"]
    fig = px.bar(
        motivo, x="Quantidade", y="Motivo", orientation="h",
        color="Quantidade", color_continuous_scale=CORES["seq_laranja"],
        title="Top 10 Razões Específicas de Cancelamento",
    )
    fig.update_layout(yaxis_title="", xaxis_title="Nº de Cancelamentos", coloraxis_showscale=False)
    return fig


def fig_contrato(df):
    contrato = df.groupby(["Contract", "Churn Label"]).size().reset_index(name="Quantidade")
    fig = px.bar(
        contrato, x="Contract", y="Quantidade", color="Churn Label", barmode="group",
        color_discrete_map={"Yes": CORES["sim"], "No": CORES["nao"]},
        title="Churn por Tipo de Contrato",
        labels={"Contract": "Tipo de Contrato", "Quantidade": "Nº de Clientes", "Churn Label": "Churn"},
    )
    return fig


def fig_tenure_hist(df):
    fig = px.histogram(
        df, x="Tenure in Months", color="Churn Label",
        color_discrete_map={"Yes": CORES["sim"], "No": CORES["nao"]},
        nbins=40, barmode="overlay", opacity=0.7,
        title="Distribuição do Tempo de Permanência",
        labels={"Tenure in Months": "Meses na empresa", "Churn Label": "Churn"},
    )
    return fig


def fig_monthly_box(df):
    fig = px.box(
        df, x="Churn Label", y="Monthly Charge", color="Churn Label",
        color_discrete_map={"Yes": CORES["sim"], "No": CORES["nao"]},
        title="Cobrança Mensal por Status de Churn",
        labels={"Churn Label": "Churn", "Monthly Charge": "Cobrança Mensal (USD)"},
    )
    return fig


def fig_satisfacao(df):
    sat = df.groupby(["Satisfaction Score", "Churn Label"]).size().reset_index(name="Quantidade")
    fig = px.bar(
        sat, x="Satisfaction Score", y="Quantidade", color="Churn Label", barmode="group",
        color_discrete_map={"Yes": CORES["sim"], "No": CORES["nao"]},
        title="Churn por Nível de Satisfação (1=Muito Insatisfeito, 5=Muito Satisfeito)",
        labels={"Satisfaction Score": "Nota de Satisfação", "Churn Label": "Churn"},
    )
    return fig


def fig_internet_tipo(df):
    internet = df[df["Internet Service"] == "Yes"].groupby(
        ["Internet Type", "Churn Label"]
    ).size().reset_index(name="Quantidade")
    fig = px.bar(
        internet, x="Internet Type", y="Quantidade", color="Churn Label", barmode="group",
        color_discrete_map={"Yes": CORES["sim"], "No": CORES["nao"]},
        title="Churn por Tipo de Internet",
        labels={"Internet Type": "Tipo de Internet", "Churn Label": "Churn"},
    )
    return fig


def fig_servicos_adicionais(df):
    servicos = ["Online Security", "Online Backup", "Device Protection Plan", "Premium Tech Support"]
    taxas = []
    for s in servicos:
        total_s = len(df[df[s] == "Yes"])
        churn_s = len(df[(df[s] == "Yes") & (df["Churn Label"] == "Yes")])
        taxa_s = round(churn_s / total_s * 100, 1) if total_s > 0 else 0
        taxas.append({"Serviço": s, "Taxa Churn (%)": taxa_s})
    df_serv = pd.DataFrame(taxas)
    fig = px.bar(
        df_serv, x="Serviço", y="Taxa Churn (%)", color="Taxa Churn (%)",
        color_continuous_scale=CORES["seq_vermelho"],
        title="Taxa de Churn por Serviço Adicional Contratado",
    )
    fig.update_layout(coloraxis_showscale=False)
    return fig


def fig_genero(df):
    gen = df[df["Churn Label"] == "Yes"]["Gender"].value_counts().reset_index()
    gen.columns = ["Gênero", "Quantidade"]
    fig = px.pie(
        gen, names="Gênero", values="Quantidade",
        title="Gênero dos Clientes que Cancelaram", hole=0.4,
    )
    return fig


def fig_faixa_etaria(df):
    faixa = df.groupby(["Faixa Etária", "Churn Label"], observed=True).size().reset_index(name="Quantidade")
    fig = px.bar(
        faixa, x="Faixa Etária", y="Quantidade", color="Churn Label", barmode="group",
        color_discrete_map={"Yes": CORES["sim"], "No": CORES["nao"]},
        title="Churn por Faixa Etária",
        labels={"Faixa Etária": "Faixa Etária", "Churn Label": "Churn"},
    )
    return fig


def fig_cltv_scatter(df):
    fig = px.scatter(
        df, x="CLTV", y="Monthly Charge", color="Churn Label",
        color_discrete_map={"Yes": CORES["sim"], "No": CORES["nao"]},
        opacity=0.5,
        title="CLTV vs. Cobrança Mensal por Status de Churn",
        labels={"CLTV": "CLTV (USD)", "Monthly Charge": "Cobrança Mensal (USD)", "Churn Label": "Churn"},
    )
    return fig


# Catálogo usado na página de Gráficos (interativos, Plotly)
GRAFICOS_DISPONIVEIS = {
    "Proporção Geral de Churn": fig_pizza_churn,
    "Categorias de Motivo de Cancelamento": fig_categoria_churn,
    "Top 10 Razões Específicas de Cancelamento": fig_motivos_especificos,
    "Churn por Tipo de Contrato": fig_contrato,
    "Churn por Nível de Satisfação": fig_satisfacao,
}


# ---------------------------------------------------------------------------
# 3b. GRÁFICOS ESTÁTICOS (matplotlib/seaborn) — usados na página de E-mail
#     Substituem o Plotly + Kaleido nessa página porque o Streamlit Cloud não
#     tem Chrome instalado, e o Kaleido depende dele para exportar PNG.
#     matplotlib/seaborn geram o PNG nativamente, sem precisar de navegador.
# ---------------------------------------------------------------------------
CORES_MPL = {"sim": "#EF553B", "nao": "#00CC96"}


def _fig_base(figsize=(9, 5.5)):
    fig, ax = plt.subplots(figsize=figsize)
    return fig, ax


def fig_mpl_pizza_churn(df):
    contagem = df["Churn Label"].value_counts()
    cores = [CORES_MPL["nao"] if s == "No" else CORES_MPL["sim"] for s in contagem.index]
    fig, ax = _fig_base()
    ax.pie(
        contagem.values,
        labels=contagem.index,
        autopct=lambda p: f"{p:.1f}%\n({int(p/100*contagem.sum())})",
        colors=cores,
        startangle=90,
        wedgeprops={"width": 0.55},
    )
    ax.set_title("Clientes que cancelaram vs. permaneceram")
    fig.tight_layout()
    return fig


def fig_mpl_categoria_churn(df):
    cat = df[df["Churn Label"] == "Yes"]["Churn Category"].value_counts().reset_index()
    cat.columns = ["Categoria", "Quantidade"]
    fig, ax = _fig_base()
    sns.barplot(data=cat, x="Quantidade", y="Categoria", hue="Categoria",
                palette="OrRd", legend=False, ax=ax)
    ax.set_title("Categorias de Motivo de Cancelamento")
    ax.set_xlabel("Nº de Cancelamentos")
    ax.set_ylabel("")
    fig.tight_layout()
    return fig


def fig_mpl_motivos_especificos(df):
    motivo = df[df["Churn Label"] == "Yes"]["Churn Reason"].value_counts().head(10).reset_index()
    motivo.columns = ["Motivo", "Quantidade"]
    fig, ax = _fig_base()
    sns.barplot(data=motivo, x="Quantidade", y="Motivo", hue="Motivo",
                palette="OrRd", legend=False, ax=ax)
    ax.set_title("Top 10 Razões Específicas de Cancelamento")
    ax.set_xlabel("Nº de Cancelamentos")
    ax.set_ylabel("")
    fig.tight_layout()
    return fig


def fig_mpl_contrato(df):
    fig, ax = _fig_base()
    sns.countplot(
        data=df, x="Contract", hue="Churn Label",
        palette={"Yes": CORES_MPL["sim"], "No": CORES_MPL["nao"]}, ax=ax,
    )
    ax.set_title("Churn por Tipo de Contrato")
    ax.set_xlabel("Tipo de Contrato")
    ax.set_ylabel("Nº de Clientes")
    ax.legend(title="Churn")
    fig.tight_layout()
    return fig


def fig_mpl_satisfacao(df):
    fig, ax = _fig_base()
    sns.countplot(
        data=df, x="Satisfaction Score", hue="Churn Label",
        palette={"Yes": CORES_MPL["sim"], "No": CORES_MPL["nao"]}, ax=ax,
    )
    ax.set_title("Churn por Nível de Satisfação (1=Muito Insatisfeito, 5=Muito Satisfeito)")
    ax.set_xlabel("Nota de Satisfação")
    ax.set_ylabel("Nº de Clientes")
    ax.legend(title="Churn")
    fig.tight_layout()
    return fig


# Catálogo usado na página de e-mail (gráficos estáticos matplotlib/seaborn)
GRAFICOS_DISPONIVEIS_ESTATICOS = {
    "Proporção Geral de Churn": fig_mpl_pizza_churn,
    "Categorias de Motivo de Cancelamento": fig_mpl_categoria_churn,
    "Top 10 Razões Específicas de Cancelamento": fig_mpl_motivos_especificos,
    "Churn por Tipo de Contrato": fig_mpl_contrato,
    "Churn por Nível de Satisfação": fig_mpl_satisfacao,
}


def gerar_png_bytes(fig) -> bytes:
    """Converte uma figura matplotlib em PNG estático (bytes) para anexar no e-mail."""
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=200, bbox_inches="tight")
    plt.close(fig)  # libera memória — importante em apps que geram vários gráficos
    buf.seek(0)
    return buf.getvalue()


# ---------------------------------------------------------------------------
# 4. RELATÓRIO DE INSIGHTS (análise geral, não gráfico a gráfico)
# ---------------------------------------------------------------------------
def gerar_relatorio_insights(df: pd.DataFrame) -> str:
    """Monta o relatório textual com números calculados a partir dos dados
    carregados (em vez de valores fixos), para o relatório sempre refletir
    o dataset que está realmente sendo usado."""

    total = len(df)
    cancelados = int((df["Churn Label"] == "Yes").sum())
    taxa_churn = round(cancelados / total * 100, 1) if total else 0

    categoria_top = (
        df[df["Churn Label"] == "Yes"]["Churn Category"].value_counts().idxmax()
        if cancelados else "N/D"
    )
    categoria_top_pct = (
        round(
            df[df["Churn Label"] == "Yes"]["Churn Category"].value_counts(normalize=True).max() * 100, 1
        ) if cancelados else 0
    )

    media_tenure_churn = round(df[df["Churn Label"] == "Yes"]["Tenure in Months"].mean(), 1) if cancelados else 0
    media_tenure_ok = round(df[df["Churn Label"] == "No"]["Tenure in Months"].mean(), 1)

    media_mensal_churn = round(df[df["Churn Label"] == "Yes"]["Monthly Charge"].mean(), 2) if cancelados else 0
    media_mensal_ok = round(df[df["Churn Label"] == "No"]["Monthly Charge"].mean(), 2)

    contrato_mes_a_mes_pct = round(
        (df[(df["Contract"] == "Month-to-Month") & (df["Churn Label"] == "Yes")].shape[0]
         / max(df[df["Contract"] == "Month-to-Month"].shape[0], 1)) * 100, 1
    )
    contrato_dois_anos_pct = round(
        (df[(df["Contract"] == "Two Year") & (df["Churn Label"] == "Yes")].shape[0]
         / max(df[df["Contract"] == "Two Year"].shape[0], 1)) * 100, 1
    )

    baixa_satisfacao_pct = round(
        (df[(df["Satisfaction Score"] <= 2) & (df["Churn Label"] == "Yes")].shape[0]
         / max(df[df["Satisfaction Score"] <= 2].shape[0], 1)) * 100, 1
    ) if "Satisfaction Score" in df.columns else None

    texto = f"""RELATÓRIO DE ANÁLISE DE CHURN — {NOME_EMPRESA}

─────────────────────────────────────────────────────────────

RESUMO EXECUTIVO

A base analisada contém {total:,} clientes, dos quais {cancelados:,} cancelaram o
serviço no período analisado — uma taxa de churn de {taxa_churn}%, nível que merece
atenção da diretoria e da área de retenção.

─────────────────────────────────────────────────────────────

PRINCIPAIS ACHADOS

1. CATEGORIA DE MOTIVO MAIS FREQUENTE: {categoria_top.upper()}
   Cerca de {categoria_top_pct}% dos cancelamentos se enquadram nessa categoria.
   Isso direciona onde a empresa deve concentrar esforços de retenção.

2. CONTRATOS MENSAIS SÃO O MAIOR RISCO
   {contrato_mes_a_mes_pct}% dos clientes com contrato Mês a Mês cancelam, contra
   apenas {contrato_dois_anos_pct}% dos clientes com contrato de Dois Anos. Contratos
   mais longos têm um efeito claro de retenção.

3. TEMPO DE PERMANÊNCIA IMPORTA
   Clientes que cancelaram ficaram, em média, {media_tenure_churn} meses na empresa,
   contra {media_tenure_ok} meses dos que permaneceram. O período inicial do
   relacionamento é o mais crítico para a retenção.

4. PREÇO PESA NA DECISÃO DE SAÍDA
   A cobrança mensal média de quem cancelou foi de USD {media_mensal_churn}, frente a
   USD {media_mensal_ok} de quem ficou. Diferenças de preço percebido podem estar
   empurrando clientes para a concorrência.

5. SATISFAÇÃO É UM ALERTA ANTECIPADO
   {f"Entre os clientes com nota de satisfação 1 ou 2, {baixa_satisfacao_pct}% cancelaram." if baixa_satisfacao_pct is not None else "Notas baixas de satisfação estão fortemente associadas ao cancelamento."}
   Monitorar essa métrica permite agir antes do cliente decidir sair.

6. SERVIÇOS ADICIONAIS AUMENTAM A RETENÇÃO
   Clientes com serviços como Segurança Online, Suporte Técnico Premium ou Plano de
   Proteção de Dispositivo tendem a cancelar menos. Esses serviços criam uma
   sensação de valor agregado que reduz a propensão à saída.

─────────────────────────────────────────────────────────────

RECOMENDAÇÕES BASEADAS EM DADOS

→ Programa de boas-vindas nos primeiros meses: oferecer suporte dedicado e
  benefícios progressivos para clientes novos, já que é nesse período que o
  risco de cancelamento é maior.

→ Incentivar migração para contratos anuais ou bianuais, com desconto real,
  reduzindo a exposição da base ao contrato mês a mês.

→ Criar um alerta automático de retenção para clientes com satisfação baixa
  (nota 1 ou 2), antes que o cancelamento aconteça.

→ Revisar a política de preços e comparar com a concorrência nos planos onde a
  cobrança mensal está associada a maior churn.

→ Usar serviços adicionais (segurança, backup, suporte premium) como
  estratégia de upsell e retenção, não apenas de receita.

─────────────────────────────────────────────────────────────

Atenciosamente,
{NOME_EMPRESA}
"""
    return texto


# ---------------------------------------------------------------------------
# 5. ENVIO DE E-MAIL
# ---------------------------------------------------------------------------
def obter_config_smtp_padrao():

    try:
        smtp = st.secrets["smtp"]
        return (
            smtp.get("host", "smtp.gmail.com"),
            int(smtp.get("port", 587)),
            smtp.get("remetente"),
            smtp.get("senha"),
        )
    except Exception:
        return None, None, None, None


def enviar_email(smtp_host, smtp_port, remetente, senha, destinatario,
                  assunto, corpo, anexo_bytes=None, anexo_nome=None):

    try:
        msg = MIMEMultipart()
        msg["From"] = remetente
        msg["To"] = destinatario
        msg["Subject"] = assunto
        msg.attach(MIMEText(corpo, "plain", "utf-8"))

        if anexo_bytes is not None:
            part = MIMEBase("application", "octet-stream")
            part.set_payload(anexo_bytes)
            encoders.encode_base64(part)
            part.add_header("Content-Disposition", f'attachment; filename="{anexo_nome}"')
            msg.attach(part)

        with smtplib.SMTP(smtp_host, int(smtp_port)) as server:
            server.starttls()
            server.login(remetente, senha)
            server.sendmail(remetente, destinatario, msg.as_string())

        return True, f"E-mail enviado com sucesso para {destinatario}!"
    except Exception as e:
        return False, f"Erro ao enviar e-mail: {e}"
