import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt

# Caminho do arquivo (ajuste conforme necessário)
caminho_arquivo = 'DEMANDAS JANEIRO 2024 - QUITADOS.csv'

df = pd.read_csv(caminho_arquivo, header=1)
df.columns = df.columns.str.upper()
df['DIRETOR'] = df['DIRETOR'].astype(str).str.strip().str.upper()

df['DESCONTO'] = df['DESCONTO'].replace('[R\$\s]', '', regex=True).replace(',', '.', regex=True)
df['SALDO DEVEDOR'] = df['SALDO DEVEDOR'].replace('[R\$\s]', '', regex=True).replace(',', '.', regex=True)

def corrigir_valor(valor):
    if isinstance(valor, str):
        partes = valor.split('.')
        if len(partes) > 2:
            return ''.join(partes[:-1]) + '.' + partes[-1]
    return valor

df['DESCONTO'] = df['DESCONTO'].apply(corrigir_valor).astype(float)
df['SALDO DEVEDOR'] = df['SALDO DEVEDOR'].apply(corrigir_valor).astype(float)
df['DESCONTO'] = df['DESCONTO'].round(2)
df['SALDO DEVEDOR'] = df['SALDO DEVEDOR'].round(2)

# Criar a coluna ECONOMIA
df['ECONOMIA'] = df['SALDO DEVEDOR'] - df['DESCONTO']

# Converter coluna BANCO para string, remover espaços e transformar em maiúsculas
df['BANCO'] = df['BANCO'].astype(str).str.strip().str.upper()

# Criando filtros na barra lateral
diretores = ['TODOS'] + sorted(df['DIRETOR'].drop_duplicates().tolist())
diretor_selecionado = st.sidebar.selectbox('Selecione o Diretor', diretores)

escritorios = ['TODOS'] + list(df['ESCRITÓRIO'].unique())
escritorio_selecionado = st.sidebar.selectbox('Selecione o Escritório', escritorios)

ufs = ['TODOS'] + list(df['UF'].unique())
uf_selecionado = st.sidebar.selectbox('Selecione a UF', ufs)

consultores = ['TODOS'] + list(df['CONSULTOR'].unique())
consultor_selecionado = st.sidebar.selectbox('Selecione o Consultor', consultores)

# Criar a lista suspensa para filtro de Banco
bancos = ['TODOS'] + sorted(df['BANCO'].dropna().unique().tolist())
banco_selecionado = st.sidebar.selectbox('Selecione o Banco', bancos)

# Aplicação dos filtros
filtros = [
    (df['DIRETOR'] == diretor_selecionado) if diretor_selecionado != 'TODOS' else pd.Series([True] * len(df)),
    (df['ESCRITÓRIO'] == escritorio_selecionado) if escritorio_selecionado != 'TODOS' else pd.Series([True] * len(df)),
    (df['UF'] == uf_selecionado) if uf_selecionado != 'TODOS' else pd.Series([True] * len(df)),
    (df['CONSULTOR'] == consultor_selecionado) if consultor_selecionado != 'TODOS' else pd.Series([True] * len(df)),
    (df['BANCO'] == banco_selecionado) if banco_selecionado != 'TODOS' else pd.Series([True] * len(df))
]

df_filtrado = df[filtros[0] & filtros[1] & filtros[2] & filtros[3] & filtros[4]]

# Cálculo das métricas
soma_ctt_filtrada = df_filtrado['CTT'].count()
soma_descontos_filtrada = df_filtrado['DESCONTO'].sum()
soma_saldo_devedor_filtrada = df_filtrado['SALDO DEVEDOR'].sum()
soma_economia_filtrada = df_filtrado['ECONOMIA'].sum()

def formatar_moeda(valor):
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

soma_descontos_filtrada_formatada = formatar_moeda(soma_descontos_filtrada)
soma_saldo_devedor_filtrada_formatada = formatar_moeda(soma_saldo_devedor_filtrada)
soma_economia_filtrada_formatada = formatar_moeda(soma_economia_filtrada)

# Exibição das métricas
col1, col2, col3, col4 = st.columns(4)

col1.metric(label="Total de Contratos", value=soma_ctt_filtrada, delta=None)
col2.metric(label="Total de Descontos", value=soma_descontos_filtrada_formatada, delta=None)
col3.metric(label="Total de Saldo Devedor", value=soma_saldo_devedor_filtrada_formatada, delta=None)
col4.metric(label="Total de Economia", value=soma_economia_filtrada_formatada, delta=None)

st.markdown("""
    <style>
        div[data-testid="stMetric"] > label {
            font-size: 14px;
        }
        div[data-testid="stMetric"] > div {
            font-size: 18px;
        }
    </style>
    """, unsafe_allow_html=True)

# Exibição dos gráficos
if not df_filtrado.empty:
    quantidade_ctt_por_responsavel = df_filtrado.groupby('RESPONSAVEL')['CTT'].count()
    plt.figure(figsize=(9, 6))
    ax = quantidade_ctt_por_responsavel.plot(kind='bar')
    plt.xlabel('RESPONSAVEL')
    plt.ylabel('Quantidade de CTT')
    plt.title(f'Quantidade de CTT por Responsável - Janeiro 2024 (Diretor: {diretor_selecionado})')
    plt.grid(False)
    for p in ax.patches:
        ax.annotate(str(p.get_height()), (p.get_x() * 1.015, p.get_height() * 1.015))
    st.pyplot(plt)

    quantidade_ctt_por_banco = df_filtrado.groupby('BANCO')['CTT'].count()
    plt.figure(figsize=(9, 6))
    ax = quantidade_ctt_por_banco.plot(kind='bar')
    plt.xlabel('BANCO')
    plt.ylabel('Quantidade de CTT')
    plt.title(f'Quantidade de CTT por Banco - Janeiro 2024')
    plt.grid(False)
    for p in ax.patches:
        ax.annotate(str(p.get_height()), (p.get_x() * 1.015, p.get_height() * 1.015))
    st.pyplot(plt)
else:
    st.write("Nenhum dado encontrado para os filtros selecionados.")
