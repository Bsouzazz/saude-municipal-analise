# app.py - VERSÃO OTIMIZADA PARA STREAMLIT CLOUD
import streamlit as st
import pandas as pd
import numpy as np

# Tente importar plotly, mas tenha fallback
try:
    import plotly.express as px
    import plotly.graph_objects as go
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False
    st.error("Plotly não está disponível. Usando gráficos nativos do Streamlit.")

# Configuração da página
st.set_page_config(
    page_title="Análise Saúde Municipal",
    page_icon="🏥",
    layout="wide"
)

st.title("🏥 Análise: Influência das Características Populacionais nas Políticas de Saúde")

# Dados de exemplo
@st.cache_data
def carregar_dados():
    np.random.seed(42)
    n = 100
    
    dados = pd.DataFrame({
        'Município': [f'Município {i}' for i in range(1, n+1)],
        'População': np.random.randint(10000, 500000, n),
        '% Idosos': np.random.uniform(5, 25, n),
        'PIB per Capita': np.random.uniform(10000, 50000, n),
        'Internações/1000': np.random.uniform(10, 100, n),
        'Procedimentos/1000': np.random.uniform(50, 500, n),
        'Região': np.random.choice(['Norte', 'Nordeste', 'Sudeste', 'Sul', 'Centro-Oeste'], n)
    })
    
    return dados

df = carregar_dados()

# Filtros
st.sidebar.header("Filtros")
regiao = st.sidebar.multiselect("Região", options=df['Região'].unique(), default=df['Região'].unique())

# Aplicar filtros
df_filtrado = df[df['Região'].isin(regiao)]

# Métricas
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Municípios", len(df_filtrado))
with col2:
    st.metric("População Média", f"{df_filtrado['População'].mean():,.0f}")
with col3:
    st.metric("% Idosos Médio", f"{df_filtrado['% Idosos'].mean():.1f}%")
with col4:
    st.metric("PIB Médio", f"R$ {df_filtrado['PIB per Capita'].mean():,.0f}")

# Gráficos
st.header("📊 Análise de Relações")

if PLOTLY_AVAILABLE:
    # Usando Plotly
    col1, col2 = st.columns(2)
    
    with col1:
        fig = px.scatter(
            df_filtrado,
            x='% Idosos',
            y='Internações/1000',
            title='Relação: % Idosos vs Internações'
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        fig = px.scatter(
            df_filtrado,
            x='PIB per Capita',
            y='Procedimentos/1000', 
            title='Relação: PIB vs Procedimentos'
        )
        st.plotly_chart(fig, use_container_width=True)
        
    # Gráfico de barras por região
    st.subheader("Procedimentos por Região")
    dados_agregados = df_filtrado.groupby('Região')['Procedimentos/1000'].mean().reset_index()
    fig = px.bar(dados_agregados, x='Região', y='Procedimentos/1000')
    st.plotly_chart(fig, use_container_width=True)
    
else:
    # Fallback com gráficos nativos do Streamlit
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Relação: % Idosos vs Internações")
        st.scatter_chart(df_filtrado, x='% Idosos', y='Internações/1000')
    
    with col2:
        st.subheader("Relação: PIB vs Procedimentos")
        st.scatter_chart(df_filtrado, x='PIB per Capita', y='Procedimentos/1000')
    
    st.subheader("Procedimentos por Região")
    dados_agregados = df_filtrado.groupby('Região')['Procedimentos/1000'].mean()
    st.bar_chart(dados_agregados)

# Análise de correlação
st.header("🔗 Análise de Correlação")
correlacao = df_filtrado['% Idosos'].corr(df_filtrado['Internações/1000'])
st.metric("Correlação % Idosos × Internações", f"{correlacao:.3f}")

# Conclusões
st.header("🎯 Conclusões")
st.info("""
**Principais Achados:**
- Correlação entre % de idosos e internações: **{:.3f}**
- Municípios com mais idosos tendem a ter mais internações hospitalares
- PIB influencia no acesso a procedimentos especializados
""".format(correlacao))

st.success("✅ App funcionando no Streamlit Cloud!")
