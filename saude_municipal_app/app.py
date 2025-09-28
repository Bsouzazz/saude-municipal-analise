# app.py - VERSÃO COMPLETA COM DASHBOARDS INTERATIVOS
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import matplotlib.pyplot as plt
import seaborn as sns

# Configuração da página
st.set_page_config(
    page_title="Análise Saúde Municipal - PNAHP & PNAES",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personalizado
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #1f77b4;
    }
</style>
""", unsafe_allow_html=True)

# Título principal
st.markdown('<h1 class="main-header">🏥 Análise: Influência das Características Populacionais nas Políticas PNAHP e PNAES</h1>', unsafe_allow_html=True)

# Sidebar com informações da pesquisa
with st.sidebar:
    st.header("🎯 Objetivo da Pesquisa")
    st.info("""
    **Questão:** Qual a influência das características populacionais 
    nas políticas PNAHP (Hospitalar) e PNAES (Especializada) dos 
    municípios brasileiros?
    
    **Objetivo:** Explorar e descrever esta influência através 
    de análise de dados.
    """)
    
    st.header("📋 Legenda dos Indicadores")
    st.write("""
    **PNAHP:** Política Nacional de Atenção Hospitalar
    - Internações hospitalares
    - Leitos disponíveis
    - Gastos hospitalares
    
    **PNAES:** Política Nacional de Atenção Especializada  
    - Procedimentos ambulatoriais
    - Consultas especializadas
    - Exames e terapias
    """)

# Carregar dados de exemplo (substituir por dados reais depois)
@st.cache_data
def carregar_dados_completos():
    """Carrega dados completos para análise"""
    np.random.seed(42)
    n_municipios = 200
    
    # Criar dados mais realistas
    dados = pd.DataFrame({
        'codigo_ibge': range(100000, 100000 + n_municipios),
        'municipio': [f'Município {i}' for i in range(1, n_municipios + 1)],
        'populacao_total': np.random.randint(10000, 800000, n_municipios),
        'populacao_60_mais': np.random.randint(1000, 150000, n_municipios),
        'pib_per_capita': np.random.uniform(8000, 45000, n_municipios),
        'idh': np.random.uniform(0.5, 0.9, n_municipios),
        'regiao': np.random.choice(['Norte', 'Nordeste', 'Sudeste', 'Sul', 'Centro-Oeste'], n_municipios),
        'densidade_demografica': np.random.uniform(10, 500, n_municipios)
    })
    
    # Calcular percentuais
    dados['percentual_idosos'] = (dados['populacao_60_mais'] / dados['populacao_total']) * 100
    
    # Criar indicadores de saúde (com relações realistas)
    # Relação positiva com % de idosos
    dados['internacoes_por_1000'] = (
        dados['percentual_idosos'] * 2 + 
        np.random.normal(0, 10, n_municipios) +
        dados['pib_per_capita'] / 1000
    )
    
    # Relação com PIB
    dados['procedimentos_por_1000'] = (
        dados['pib_per_capita'] / 200 + 
        np.random.normal(0, 20, n_municipios) +
        dados['percentual_idosos'] * 1.5
    )
    
    # Gastos hospitalares
    dados['gasto_internacao_per_capita'] = (
        dados['internacoes_por_1000'] * 50 + 
        np.random.normal(0, 100, n_municipios)
    )
    
    # Tipos de procedimentos
    dados['procedimentos_alta_complexidade'] = (
        dados['pib_per_capita'] / 300 + 
        dados['percentual_idosos'] * 2
    )
    
    return dados

# Carregar dados
with st.spinner('Carregando dados para análise...'):
    df = carregar_dados_completos()

# Filtros interativos
st.sidebar.header("🎛️ Filtros")

regioes = st.sidebar.multiselect(
    "Regiões",
    options=df['regiao'].unique(),
    default=df['regiao'].unique()
)

faixa_idosos = st.sidebar.slider(
    "Faixa de % Idosos",
    min_value=float(df['percentual_idosos'].min()),
    max_value=float(df['percentual_idosos'].max()),
    value=(5.0, 25.0)
)

faixa_pib = st.sidebar.slider(
    "Faixa de PIB per Capita (R$)",
    min_value=float(df['pib_per_capita'].min()),
    max_value=float(df['pib_per_capita'].max()),
    value=(10000.0, 40000.0)
)

# Aplicar filtros
df_filtrado = df[
    (df['regiao'].isin(regioes)) &
    (df['percentual_idosos'] >= faixa_idosos[0]) &
    (df['percentual_idosos'] <= faixa_idosos[1]) &
    (df['pib_per_capita'] >= faixa_pib[0]) &
    (df['pib_per_capita'] <= faixa_pib[1])
]

# METRICAS PRINCIPAIS
st.header("📊 Visão Geral dos Municípios")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Municípios Analisados", 
        f"{len(df_filtrado):,}".replace(",", "."),
        delta=f"{len(df_filtrado) - len(df)}" if len(df_filtrado) != len(df) else None
    )

with col2:
    st.metric(
        "População Média", 
        f"{df_filtrado['populacao_total'].mean():,.0f}".replace(",", ".")
    )

with col3:
    percentual_idosos_medio = df_filtrado['percentual_idosos'].mean()
    st.metric(
        "% Idosos Médio", 
        f"{percentual_idosos_medio:.1f}%"
    )

with col4:
    st.metric(
        "PIB per Capita Médio", 
        f"R$ {df_filtrado['pib_per_capita'].mean():,.0f}".replace(",", ".")
    )

# DASHBOARD 1: ANÁLISE DA PNAHP (ATENÇÃO HOSPITALAR)
st.header("🏥 DASHBOARD 1: Análise PNAHP - Atenção Hospitalar")

tab1, tab2, tab3 = st.tabs(["Relação com Características Populacionais", "Análise por Região", "Indicadores Hospitalares"])

with tab1:
    col1, col2 = st.columns(2)
    
    with col1:
        # Gráfico 1: Relação Idosos vs Internações
        fig = px.scatter(
            df_filtrado,
            x='percentual_idosos',
            y='internacoes_por_1000',
            size='populacao_total',
            color='pib_per_capita',
            hover_data=['municipio', 'regiao'],
            title='<b>Relação: % Idosos vs Internações Hospitalares</b><br><i>PNAHP - Política Nacional de Atenção Hospitalar</i>',
            labels={
                'percentual_idosos': '% População com 60+ anos',
                'internacoes_por_1000': 'Internações por 1000 habitantes',
                'pib_per_capita': 'PIB per Capita (R$)',
                'populacao_total': 'População Total'
            },
            trendline="lowess"
        )
        fig.update_layout(height=500)
        st.plotly_chart(fig, use_container_width=True)
        
        # Estatística de correlação
        correlacao = df_filtrado['percentual_idosos'].corr(df_filtrado['internacoes_por_1000'])
        st.metric("Correlação % Idosos × Internações", f"{correlacao:.3f}")

    with col2:
        # Gráfico 2: PIB vs Gastos Hospitalares
        fig = px.scatter(
            df_filtrado,
            x='pib_per_capita',
            y='gasto_internacao_per_capita',
            size='populacao_total',
            color='percentual_idosos',
            hover_data=['municipio', 'regiao'],
            title='<b>Relação: PIB vs Gastos com Internações</b>',
            labels={
                'pib_per_capita': 'PIB per Capita (R$)',
                'gasto_internacao_per_capita': 'Gasto com Internações per Capita (R$)',
                'percentual_idosos': '% Idosos'
            },
            trendline="ols"
        )
        fig.update_layout(height=500)
        st.plotly_chart(fig, use_container_width=True)

with tab2:
    col1, col2 = st.columns(2)
    
    with col1:
        # Boxplot por região - Internações
        fig = px.box(
            df_filtrado,
            x='regiao',
            y='internacoes_por_1000',
            color='regiao',
            title='<b>Distribuição de Internações por Região</b>',
            labels={'internacoes_por_1000': 'Internações por 1000 hab.', 'regiao': 'Região'}
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Mapa de calor de correlações
        variaveis_correlacao = ['percentual_idosos', 'pib_per_capita', 'idh', 'densidade_demografica', 'internacoes_por_1000', 'gasto_internacao_per_capita']
        corr_matrix = df_filtrado[variaveis_correlacao].corr()
        
        fig = px.imshow(
            corr_matrix,
            text_auto=True,
            aspect="auto",
            color_continuous_scale='RdBu',
            title='<b>Matriz de Correlação - PNAHP</b>'
        )
        st.plotly_chart(fig, use_container_width=True)

# DASHBOARD 2: ANÁLISE DA PNAES (ATENÇÃO ESPECIALIZADA)
st.header("👨‍⚕️ DASHBOARD 2: Análise PNAES - Atenção Especializada")

tab4, tab5, tab6 = st.tabs(["Acesso a Serviços Especializados", "Análise por Porte Populacional", "Eficiência dos Serviços"])

with tab4:
    col1, col2 = st.columns(2)
    
    with col1:
        # Gráfico: PIB vs Procedimentos
        fig = px.scatter(
            df_filtrado,
            x='pib_per_capita',
            y='procedimentos_por_1000',
            size='populacao_total',
            color='percentual_idosos',
            hover_data=['municipio', 'regiao'],
            title='<b>Relação: PIB vs Procedimentos Ambulatoriais</b><br><i>PNAES - Política Nacional de Atenção Especializada</i>',
            labels={
                'pib_per_capita': 'PIB per Capita (R$)',
                'procedimentos_por_1000': 'Procedimentos por 1000 habitantes',
                'percentual_idosos': '% Idosos'
            },
            trendline="lowess"
        )
        fig.update_layout(height=500)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        # Gráfico: Idosos vs Procedimentos de Alta Complexidade
        fig = px.scatter(
            df_filtrado,
            x='percentual_idosos',
            y='procedimentos_alta_complexidade',
            size='pib_per_capita',
            color='regiao',
            hover_data=['municipio'],
            title='<b>Relação: % Idosos vs Procedimentos de Alta Complexidade</b>',
            labels={
                'percentual_idosos': '% População com 60+ anos',
                'procedimentos_alta_complexidade': 'Procedimentos Alta Complexidade',
                'pib_per_capita': 'PIB per Capita (R$)'
            }
        )
        fig.update_layout(height=500)
        st.plotly_chart(fig, use_container_width=True)

with tab5:
    # Classificar municípios por porte
    df_filtrado['porte'] = pd.cut(
        df_filtrado['populacao_total'],
        bins=[0, 20000, 100000, 500000, float('inf')],
        labels=['Pequeno', 'Médio', 'Grande', 'Metrópole']
    )
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig = px.box(
            df_filtrado,
            x='porte',
            y='procedimentos_por_1000',
            color='porte',
            title='<b>Procedimentos Ambulatoriais por Porte do Município</b>'
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Gráfico de barras agrupadas
        agg_data = df_filtrado.groupby(['porte', 'regiao']).agg({
            'procedimentos_por_1000': 'mean',
            'procedimentos_alta_complexidade': 'mean'
        }).reset_index()
        
        fig = px.bar(
            agg_data,
            x='porte',
            y='procedimentos_por_1000',
            color='regiao',
            barmode='group',
            title='<b>Procedimentos por Porte e Região</b>'
        )
        st.plotly_chart(fig, use_container_width=True)

# DASHBOARD 3: ANÁLISE COMPARATIVA E INSIGHTS
st.header("📈 DASHBOARD 3: Análise Comparativa e Insights")

col1, col2 = st.columns(2)

with col1:
    # Comparação entre extremos de % idosos
    st.subheader("📊 Comparação: Municípios com Alto vs Baixo % de Idosos")
    
    limite_alto = df_filtrado['percentual_idosos'].quantile(0.75)
    limite_baixo = df_filtrado['percentual_idosos'].quantile(0.25)
    
    alto_idosos = df_filtrado[df_filtrado['percentual_idosos'] >= limite_alto]
    baixo_idosos = df_filtrado[df_filtrado['percentual_idosos'] <= limite_baixo]
    
    comparacao_data = pd.DataFrame({
        'Grupo': ['Alto % Idosos', 'Baixo % Idosos'],
        'Internações/1000': [
            alto_idosos['internacoes_por_1000'].mean(),
            baixo_idosos['internacoes_por_1000'].mean()
        ],
        'Procedimentos/1000': [
            alto_idosos['procedimentos_por_1000'].mean(),
            baixo_idosos['procedimentos_por_1000'].mean()
        ],
        'Gasto Internação per Capita': [
            alto_idosos['gasto_internacao_per_capita'].mean(),
            baixo_idosos['gasto_internacao_per_capita'].mean()
        ]
    })
    
    fig = go.Figure()
    fig.add_trace(go.Bar(
        name='Internações/1000', 
        x=comparacao_data['Grupo'], 
        y=comparacao_data['Internações/1000']
    ))
    fig.add_trace(go.Bar(
        name='Procedimentos/1000', 
        x=comparacao_data['Grupo'], 
        y=comparacao_data['Procedimentos/1000']
    ))
    fig.add_trace(go.Bar(
        name='Gasto per Capita (R$)', 
        x=comparacao_data['Grupo'], 
        y=comparacao_data['Gasto Internação per Capita']
    ))
    
    fig.update_layout(
        title='Comparação de Indicadores de Saúde',
        barmode='group',
        height=400
    )
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("🎯 Insights e Correlações")
    
    # Calcular correlações
    correl_idosos_intern = df_filtrado['percentual_idosos'].corr(df_filtrado['internacoes_por_1000'])
    correl_pib_proced = df_filtrado['pib_per_capita'].corr(df_filtrado['procedimentos_por_1000'])
    correl_idosos_complexo = df_filtrado['percentual_idosos'].corr(df_filtrado['procedimentos_alta_complexidade'])
    
    # Exibir insights
    st.info(f"""
    **📋 Principais Achados:**
    
    🏥 **PNAHP (Hospitalar):**
    - Correlação Idosos-Internações: **{correl_idosos_intern:.3f}**
    - {f"✅ Forte influência positiva" if correl_idosos_intern > 0.5 else f"📊 Moderada influência" if correl_idosos_intern > 0.3 else f"📉 Fraca influência"}
    
    👨‍⚕️ **PNAES (Especializada):**
    - Correlação PIB-Procedimentos: **{correl_pib_proced:.3f}**
    - {f"💰 Municípios mais ricos têm mais acesso" if correl_pib_proced > 0.3 else f"⚖️ Pouca relação com riqueza"}
    - Correlação Idosos-Alta Complexidade: **{correl_idosos_complexo:.3f}**
    
    📈 **Diferença entre extremos:**
    - Municípios com muitos idosos têm **{alto_idosos['internacoes_por_1000'].mean()/baixo_idosos['internacoes_por_1000'].mean():.1f}x** mais internações
    - E **{alto_idosos['gasto_internacao_per_capita'].mean()/baixo_idosos['gasto_internacao_per_capita'].mean():.1f}x** mais gastos hospitalares
    """)

# CONCLUSÕES FINAIS
st.header("🎓 Conclusões para as Políticas Públicas")

col1, col2 = st.columns(2)

with col1:
    st.subheader("🏥 Implicações para a PNAHP")
    st.write("""
    1. **Municípios com população idosa** necessitam de mais recursos hospitalares
    2. **Investimento em leitos** deve considerar o perfil demográfico
    3. **Hospitais regionais** são essenciais para municípios menores
    4. **Planejamento baseado em projeções** do envelhecimento populacional
    """)

with col2:
    st.subheader("👨‍⚕️ Implicações para a PNAES")
    st.write("""
    1. **Distribuição desigual** de serviços especializados
    2. **Foco em regiões** com menor PIB per capita
    3. **Expansão de telemedicina** para áreas remotas
    4. **Capacitação profissional** em geriatria e doenças crônicas
    """)

# RECOMENDAÇÕES
st.header("💡 Recomendações para Gestores")

st.success("""
**🎯 Ações Prioritárias:**
1. **Alocação de recursos** baseada em perfil demográfico e socioeconômico
2. **Políticas regionais** considerando envelhecimento populacional
3. **Integração entre PNAHP e PNAES** para cuidado contínuo
4. **Monitoramento contínuo** através de dashboards como este
""")

# Rodapé
st.markdown("---")
st.markdown("**Desenvolvido para análise da influência populacional nas políticas PNAHP e PNAES** • Dados: Exemplo ilustrativo")

# Botão para expandir dados
with st.expander("📋 Visualizar Dados Completos"):
    st.dataframe(df_filtrado, use_container_width=True)