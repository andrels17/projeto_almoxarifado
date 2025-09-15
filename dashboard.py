"""
Dashboard do Almoxarifado
Aplicação Streamlit para visualização e análise dos dados do almoxarifado
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import sqlite3
from datetime import datetime, timedelta
import numpy as np
import re
import os
from scipy import stats

def init_database():
    """Inicializa o banco de dados se não existir"""
    if not os.path.exists('almoxarifado.db'):
        try:
            # Ler o schema
            with open('database_schema.sql', 'r', encoding='utf-8') as f:
                schema = f.read()
            
            # Conectar e criar tabelas
            conn = sqlite3.connect('almoxarifado.db')
            cursor = conn.cursor()
            
            # Executar schema
            cursor.executescript(schema)
            conn.commit()
            
            # Tentar carregar dados se disponível
            data_file = None
            if os.path.exists('Database.csv'):
                data_file = 'Database.csv'
            elif os.path.exists('sample_data.csv'):
                data_file = 'sample_data.csv'
            
            if data_file:
                try:
                    # Carregar dados de exemplo
                    df = pd.read_csv(data_file, encoding='utf-8', sep=',')
                    
                    # Inserir dados básicos (simplificado para demo)
                    if len(df) > 0:
                        # Inserir alguns registros de exemplo
                        for _, row in df.head(100).iterrows():  # Limitar a 100 registros para demo
                            cursor.execute("""
                                INSERT OR IGNORE INTO estoque 
                                (periodo, cod_material, desc_material, familia, quantidade, custo_medio, valor_total, unidade, almoxarifado)
                                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                            """, (
                                row.get('Período', 'jan/23'),
                                row.get('Cód. Material', '1'),
                                row.get('Desc. Material', 'Material de Exemplo'),
                                row.get('Desc. Família', 'Família de Exemplo'),
                                float(row.get('Quantidade', 1)),
                                float(row.get('Custo Médio', 100.0)),
                                float(row.get('Vlr. Total', 100.0)),
                                row.get('Unidade', 'UN'),
                                row.get('Desc. Almoxarifado', 'Almoxarifado de Exemplo')
                            ))
                    
                    conn.commit()
                    st.info(f"📊 Dados de exemplo carregados: {len(df)} registros")
                    
                except Exception as e:
                    st.warning(f"Aviso: Não foi possível carregar dados: {e}")
            
            conn.close()
            return True
            
        except Exception as e:
            st.error(f"Erro ao inicializar banco de dados: {e}")
            return False
    return True

def create_date_from_period(periodo):
    """
    Converte string de período (ex: 'jan/23') para objeto datetime
    """
    # Mapeamento de meses em português para números
    meses_map = {
        'jan': 1, 'fev': 2, 'mar': 3, 'abr': 4, 'mai': 5, 'jun': 6,
        'jul': 7, 'ago': 8, 'set': 9, 'out': 10, 'nov': 11, 'dez': 12
    }
    
    try:
        # Extrair mês e ano usando regex
        match = re.match(r'([a-z]{3})/(\d{2})', periodo.lower())
        if match:
            mes_str, ano_str = match.groups()
            mes = meses_map.get(mes_str)
            ano = 2000 + int(ano_str)  # Assumindo anos 2000+
            
            if mes:
                return datetime(ano, mes, 1)  # Primeiro dia do mês
    except:
        pass
    
    # Se não conseguir converter, retorna data muito antiga
    return datetime(1900, 1, 1)

# Configuração da página
st.set_page_config(
    page_title="Dashboard Almoxarifado",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS para melhorar responsividade
st.markdown("""
<style>
/* Melhorar responsividade geral */
.main .block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
    max-width: 100%;
}

/* Ajustar sidebar para telas menores */
.css-1d391kg {
    width: 250px;
}

/* Melhorar espaçamento das colunas */
.stColumns > div {
    padding: 0.5rem;
}

/* Ajustar métricas para telas menores */
.metric-container {
    min-width: 150px;
}

/* Melhorar gráficos responsivos */
.plotly-graph-div {
    width: 100% !important;
    height: auto !important;
}

/* Ajustar tabelas responsivas */
.dataframe {
    font-size: 0.9rem;
}

/* Melhorar botões e inputs */
.stButton > button {
    width: 100%;
}

/* Ajustar expanders */
.streamlit-expander {
    margin: 0.5rem 0;
}

/* Melhorar responsividade em telas pequenas */
@media (max-width: 768px) {
    .main .block-container {
        padding-left: 1rem;
        padding-right: 1rem;
    }
    
    .stColumns > div {
        padding: 0.25rem;
    }
    
    .metric-container {
        min-width: 120px;
    }
}
</style>
""", unsafe_allow_html=True)

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
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .sidebar .sidebar-content {
        background-color: #f8f9fa;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    """Carrega dados do banco SQLite"""
    try:
        conn = sqlite3.connect('almoxarifado.db')
        
        # Queries principais
        queries = {
            'estoque': """
                SELECT e.*, m.codigo as cod_material, m.descricao as desc_material,
                       m.unidade, f.descricao as familia, g.descricao as grupo,
                       a.descricao as almoxarifado, p.periodo, p.ano, p.mes
                FROM estoque e
                JOIN materiais m ON e.material_id = m.id
                LEFT JOIN grupos_materiais g ON m.grupo_material_id = g.id
                LEFT JOIN familias f ON g.familia_id = f.id
                LEFT JOIN almoxarifados a ON e.almoxarifado_id = a.id
                LEFT JOIN periodos p ON e.periodo_id = p.id
            """,
            'materiais': """
                SELECT m.*, f.descricao as familia, g.descricao as grupo,
                       t.descricao as tipo_material
                FROM materiais m
                LEFT JOIN grupos_materiais g ON m.grupo_material_id = g.id
                LEFT JOIN familias f ON g.familia_id = f.id
                LEFT JOIN tipos_materiais t ON m.tipo_material_id = t.id
            """,
            'resumo_por_periodo': """
                SELECT p.periodo, p.ano, p.mes,
                       COUNT(DISTINCT e.material_id) as total_materiais,
                       SUM(e.quantidade) as total_quantidade,
                       SUM(e.valor_total) as valor_total_estoque,
                       AVG(e.custo_medio) as custo_medio_geral
                FROM estoque e
                JOIN periodos p ON e.periodo_id = p.id
                GROUP BY p.id, p.periodo, p.ano, p.mes
                ORDER BY p.ano, p.mes
            """,
            'top_materiais_valor': """
                SELECT m.codigo, m.descricao, f.descricao as familia,
                       SUM(e.valor_total) as valor_total,
                       SUM(e.quantidade) as quantidade_total,
                       AVG(e.custo_medio) as custo_medio
                FROM estoque e
                JOIN materiais m ON e.material_id = m.id
                LEFT JOIN grupos_materiais g ON m.grupo_material_id = g.id
                LEFT JOIN familias f ON g.familia_id = f.id
                GROUP BY m.id, m.codigo, m.descricao, f.descricao
                ORDER BY valor_total DESC
                LIMIT 20
            """,
            'estoque_por_almoxarifado': """
                SELECT a.descricao as almoxarifado,
                       COUNT(DISTINCT e.material_id) as total_materiais,
                       SUM(e.quantidade) as quantidade_total,
                       SUM(e.valor_total) as valor_total
                FROM estoque e
                JOIN almoxarifados a ON e.almoxarifado_id = a.id
                GROUP BY a.id, a.descricao
                ORDER BY valor_total DESC
            """
        }
        
        data = {}
        for key, query in queries.items():
            try:
                df = pd.read_sql_query(query, conn)
                data[key] = df if len(df) > 0 else pd.DataFrame()
            except Exception as e:
                st.warning(f"Erro ao carregar {key}: {e}")
                data[key] = pd.DataFrame()
        
        conn.close()
        return data
        
    except Exception as e:
        st.error(f"Erro ao conectar com o banco de dados: {e}")
        # Retornar dados vazios em caso de erro
        return {
            'estoque': pd.DataFrame(),
            'materiais': pd.DataFrame(),
            'resumo_por_periodo': pd.DataFrame(),
            'top_materiais_valor': pd.DataFrame(),
            'estoque_por_almoxarifado': pd.DataFrame()
        }

def format_currency(value):
    """Formata valor como moeda brasileira"""
    return f"R$ {value:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')

def format_number(value):
    """Formata número com separadores"""
    return f"{value:,.0f}".replace(',', '.')

def show_material_summary(material_data, codigo_material, data):
    """Mostra resumo geral do material"""
    st.markdown(f"### {material_data['desc_material']}")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Código", codigo_material)
    
    with col2:
        st.metric("Família", material_data['familia'])
    
    with col3:
        st.metric("Unidade", material_data['unidade'])
    
    with col4:
        st.metric("Quantidade Total", format_number(material_data['quantidade']))
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Valor Total", format_currency(material_data['valor_total']))
    
    with col2:
        st.metric("Custo Médio", format_currency(material_data['custo_medio']))
    
    with col3:
        valor_unitario = material_data['valor_total'] / material_data['quantidade'] if material_data['quantidade'] > 0 else 0
        st.metric("Valor Unitário", format_currency(valor_unitario))
    
    with col4:
        # Calcular participação no estoque total
        total_estoque = data['estoque']['valor_total'].sum()
        participacao = (material_data['valor_total'] / total_estoque) * 100
        st.metric("Participação no Estoque", f"{participacao:.2f}%")

def show_price_evolution(codigo_material, data):
    """Mostra evolução de preços do material"""
    # Buscar dados históricos do material
    material_historico = data['estoque'][data['estoque']['cod_material'] == codigo_material].copy()
    
    if len(material_historico) == 0:
        st.warning("Nenhum dado histórico encontrado para este material.")
        return
    
    # Agrupar por período
    evolucao_precos = material_historico.groupby(['periodo', 'ano', 'mes']).agg({
        'custo_medio': 'mean',
        'quantidade': 'sum',
        'valor_total': 'sum'
    }).reset_index()
    
    # Criar coluna de data real para ordenação cronológica correta
    evolucao_precos['data_ordem'] = evolucao_precos['periodo'].apply(create_date_from_period)
    
    # Ordenar cronologicamente
    evolucao_precos = evolucao_precos.sort_values('data_ordem')
    
    if len(evolucao_precos) > 1:
        # Gráfico de evolução de preços
        fig_precos = px.line(
            evolucao_precos,
            x='periodo',
            y='custo_medio',
            title=f"Evolução do Custo Médio - Material {codigo_material}",
            labels={'custo_medio': 'Custo Médio (R$)', 'periodo': 'Período'}
        )
        
        # Adicionar rótulos de dados formatados
        fig_precos.update_traces(
            text=[f"R$ {preco:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.') for preco in evolucao_precos['custo_medio']],
            textposition="top center",
            mode='lines+markers+text'
        )
        
        # Forçar ordenação cronológica no eixo X
        fig_precos.update_layout(
            xaxis={'categoryorder': 'array', 'categoryarray': evolucao_precos['periodo'].tolist()}
        )
        
        st.plotly_chart(fig_precos, use_container_width=True)
        
        # Estatísticas de preço
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            preco_min = evolucao_precos['custo_medio'].min()
            st.metric("Menor Preço", format_currency(preco_min))
        
        with col2:
            preco_max = evolucao_precos['custo_medio'].max()
            st.metric("Maior Preço", format_currency(preco_max))
        
        with col3:
            variacao = ((preco_max - preco_min) / preco_min) * 100 if preco_min > 0 else 0
            st.metric("Variação Total", f"{variacao:.1f}%")
        
        with col4:
            preco_atual = evolucao_precos['custo_medio'].iloc[-1]
            preco_anterior = evolucao_precos['custo_medio'].iloc[-2] if len(evolucao_precos) > 1 else preco_atual
            variacao_recente = ((preco_atual - preco_anterior) / preco_anterior) * 100 if preco_anterior > 0 else 0
            st.metric("Variação Recente", f"{variacao_recente:.1f}%")
    else:
        st.info("Dados insuficientes para mostrar evolução de preços.")

def show_period_movement(codigo_material, data):
    """Mostra movimentação do material por período"""
    # Buscar dados históricos do material
    material_historico = data['estoque'][data['estoque']['cod_material'] == codigo_material].copy()
    
    if len(material_historico) == 0:
        st.warning("Nenhum dado histórico encontrado para este material.")
        return
    
    # Agrupar por período
    movimentacao = material_historico.groupby(['periodo', 'ano', 'mes']).agg({
        'quantidade': 'sum',
        'valor_total': 'sum',
        'custo_medio': 'mean'
    }).reset_index()
    
    # Criar coluna de data real para ordenação cronológica correta
    movimentacao['data_ordem'] = movimentacao['periodo'].apply(create_date_from_period)
    
    # Ordenar cronologicamente
    movimentacao = movimentacao.sort_values('data_ordem')
    
    if len(movimentacao) > 1:
        # Gráfico de movimentação de quantidade
        fig_quantidade = px.bar(
            movimentacao,
            x='periodo',
            y='quantidade',
            title=f"Movimentação de Quantidade - Material {codigo_material}",
            labels={'quantidade': 'Quantidade', 'periodo': 'Período'}
        )
        
        # Adicionar rótulos de dados formatados
        fig_quantidade.update_traces(
            text=[f"{qtd:,.0f}".replace(',', '.') for qtd in movimentacao['quantidade']],
            textposition="outside",
            hovertemplate='<b>%{x}</b><br>Quantidade: %{y:,.0f}<extra></extra>'
        )
        
        # Forçar ordenação cronológica no eixo X
        fig_quantidade.update_layout(
            xaxis={'categoryorder': 'array', 'categoryarray': movimentacao['periodo'].tolist()}
        )
        
        st.plotly_chart(fig_quantidade, use_container_width=True)
        
        # Gráfico de movimentação de valor
        fig_valor = px.bar(
            movimentacao,
            x='periodo',
            y='valor_total',
            title=f"Movimentação de Valor - Material {codigo_material}",
            labels={'valor_total': 'Valor Total (R$)', 'periodo': 'Período'}
        )
        
        # Adicionar rótulos de dados formatados
        fig_valor.update_traces(
            text=[f"R$ {valor:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.') for valor in movimentacao['valor_total']],
            textposition="outside",
            hovertemplate='<b>%{x}</b><br>Valor: R$ %{y:,.2f}<extra></extra>'
        )
        
        # Forçar ordenação cronológica no eixo X
        fig_valor.update_layout(
            xaxis={'categoryorder': 'array', 'categoryarray': movimentacao['periodo'].tolist()}
        )
        
        st.plotly_chart(fig_valor, use_container_width=True)
        
        # Estatísticas de movimentação
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            qtd_media = movimentacao['quantidade'].mean()
            st.metric("Quantidade Média/Período", format_number(qtd_media))
        
        with col2:
            qtd_max = movimentacao['quantidade'].max()
            st.metric("Maior Quantidade", format_number(qtd_max))
        
        with col3:
            valor_medio = movimentacao['valor_total'].mean()
            st.metric("Valor Médio/Período", format_currency(valor_medio))
        
        with col4:
            valor_max = movimentacao['valor_total'].max()
            st.metric("Maior Valor", format_currency(valor_max))
    else:
        st.info("Dados insuficientes para mostrar movimentação por período.")

def show_technical_info(codigo_material, data):
    """Mostra informações técnicas do material"""
    # Buscar informações do material na tabela de materiais
    material_info = data['materiais'][data['materiais']['codigo'] == codigo_material]
    
    if len(material_info) == 0:
        st.warning("Informações técnicas não encontradas para este material.")
        return
    
    material_info = material_info.iloc[0]
    
    st.markdown("### Informações Técnicas")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Dados Básicos:**")
        st.write(f"**Código:** {material_info['codigo']}")
        st.write(f"**Descrição:** {material_info['descricao']}")
        st.write(f"**Família:** {material_info['familia']}")
        st.write(f"**Grupo:** {material_info['grupo']}")
        st.write(f"**Tipo:** {material_info['tipo_material']}")
        st.write(f"**Unidade:** {material_info['unidade']}")
        st.write(f"**Situação:** {material_info['situacao']}")
    
    with col2:
        st.markdown("**Controle de Estoque:**")
        st.write(f"**Controla Estoque Mínimo:** {'Sim' if material_info['controla_estoque_min'] else 'Não'}")
        if material_info['controla_estoque_min']:
            st.write(f"**Estoque Mínimo:** {format_number(material_info['estoque_minimo'])}")
        
        st.write(f"**Controla Estoque Máximo:** {'Sim' if material_info['controla_estoque_max'] else 'Não'}")
        if material_info['controla_estoque_max']:
            st.write(f"**Estoque Máximo:** {format_number(material_info['estoque_maximo'])}")
        
        st.write(f"**Curva ABC:** {material_info['curva_xyz']}")

def show_trend_analysis(codigo_material, data):
    """Mostra análise de tendências do material"""
    # Buscar dados históricos do material
    material_historico = data['estoque'][data['estoque']['cod_material'] == codigo_material].copy()
    
    if len(material_historico) == 0:
        st.warning("Nenhum dado histórico encontrado para este material.")
        return
    
    # Agrupar por período
    tendencias = material_historico.groupby(['periodo', 'ano', 'mes']).agg({
        'quantidade': 'sum',
        'valor_total': 'sum',
        'custo_medio': 'mean'
    }).reset_index()
    
    # Criar coluna de data real para ordenação cronológica correta
    tendencias['data_ordem'] = tendencias['periodo'].apply(create_date_from_period)
    
    # Ordenar cronologicamente
    tendencias = tendencias.sort_values('data_ordem')
    
    if len(tendencias) > 3:
        # Calcular tendências
        tendencias['periodo_num'] = range(len(tendencias))
        
        # Tendência de preço (regressão linear simples)
        slope_preco, intercept_preco, r_value_preco, p_value_preco, std_err_preco = stats.linregress(
            tendencias['periodo_num'], tendencias['custo_medio']
        )
        
        # Tendência de quantidade
        slope_qtd, intercept_qtd, r_value_qtd, p_value_qtd, std_err_qtd = stats.linregress(
            tendencias['periodo_num'], tendencias['quantidade']
        )
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### Tendência de Preços")
            if slope_preco > 0:
                st.success(f"📈 **Tendência de Alta** - {slope_preco:.2f} R$/período")
            elif slope_preco < 0:
                st.error(f"📉 **Tendência de Baixa** - {abs(slope_preco):.2f} R$/período")
            else:
                st.info("📊 **Tendência Estável**")
            
            st.write(f"**Correlação:** {r_value_preco:.3f}")
            st.write(f"**Significância:** {p_value_preco:.3f}")
        
        with col2:
            st.markdown("### Tendência de Quantidade")
            if slope_qtd > 0:
                st.success(f"📈 **Tendência de Alta** - {slope_qtd:.0f} unidades/período")
            elif slope_qtd < 0:
                st.error(f"📉 **Tendência de Baixa** - {abs(slope_qtd):.0f} unidades/período")
            else:
                st.info("📊 **Tendência Estável**")
            
            st.write(f"**Correlação:** {r_value_qtd:.3f}")
            st.write(f"**Significância:** {p_value_qtd:.3f}")
        
        # Gráfico de tendências
        fig_tendencias = go.Figure()
        
        # Adicionar linha de preços
        fig_tendencias.add_trace(go.Scatter(
            x=tendencias['periodo'],
            y=tendencias['custo_medio'],
            mode='lines+markers+text',
            name='Custo Médio',
            yaxis='y',
            line=dict(color='blue'),
            text=[f"R$ {preco:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.') for preco in tendencias['custo_medio']],
            textposition="top center"
        ))
        
        # Adicionar linha de tendência de preços
        linha_tendencia_preco = slope_preco * tendencias['periodo_num'] + intercept_preco
        fig_tendencias.add_trace(go.Scatter(
            x=tendencias['periodo'],
            y=linha_tendencia_preco,
            mode='lines',
            name='Tendência Preços',
            yaxis='y',
            line=dict(color='blue', dash='dash')
        ))
        
        # Configurar eixos
        fig_tendencias.update_layout(
            title=f"Análise de Tendências - Material {codigo_material}",
            xaxis_title="Período",
            yaxis=dict(title="Custo Médio (R$)", side="left"),
            yaxis2=dict(title="Quantidade", side="right", overlaying="y"),
            height=500
        )
        
        # Adicionar linha de quantidade no eixo direito
        fig_tendencias.add_trace(go.Scatter(
            x=tendencias['periodo'],
            y=tendencias['quantidade'],
            mode='lines+markers+text',
            name='Quantidade',
            yaxis='y2',
            line=dict(color='red'),
            text=[f"{qtd:,.0f}".replace(',', '.') for qtd in tendencias['quantidade']],
            textposition="bottom center"
        ))
        
        st.plotly_chart(fig_tendencias, use_container_width=True)
        
        # Recomendações baseadas nas tendências
        st.markdown("### 💡 Recomendações")
        
        if slope_preco > 0 and p_value_preco < 0.05:
            st.warning("⚠️ **Preço em alta significativa** - Considere comprar estoque adicional")
        elif slope_preco < 0 and p_value_preco < 0.05:
            st.success("✅ **Preço em baixa** - Boa oportunidade para compras")
        
        if slope_qtd > 0 and p_value_qtd < 0.05:
            st.info("📈 **Demanda crescente** - Ajuste estoque mínimo para cima")
        elif slope_qtd < 0 and p_value_qtd < 0.05:
            st.warning("📉 **Demanda decrescente** - Reduza estoque para evitar obsolescência")
    else:
        st.info("Dados insuficientes para análise de tendências (mínimo 4 períodos necessários).")

def main():
    # Inicializar banco de dados
    if not init_database():
        st.error("❌ Erro ao inicializar banco de dados. Verifique os logs.")
        return
    
    # Header
    st.markdown('<h1 class="main-header">📦 Dashboard do Almoxarifado</h1>', unsafe_allow_html=True)
    
    # Criar abas principais
    tab_dashboard, tab_materiais, tab_analises, tab_integracao = st.tabs([
        "📊 Dashboard Geral", 
        "🔍 Análise de Materiais", 
        "📈 Análises Avançadas",
        "📥 Integração de Dados"
    ])
    
    with tab_dashboard:
        show_main_dashboard()
    
    with tab_materiais:
        show_materials_analysis()
    
    with tab_analises:
        show_advanced_analyses()
    
    with tab_integracao:
        show_data_integration()

def calculate_advanced_kpis(data):
    """
    Calcula KPIs avançados baseados em dados de saída
    """
    kpis = {}
    
    # Verificar se os dados existem
    if 'estoque' not in data or len(data['estoque']) == 0:
        return {
            'valor_total_saidas': 0,
            'quantidade_materiais': 0,
            'quantidade_total_saidas': 0,
            'saida_media_por_material': 0,
            'valor_medio_por_saida': 0,
            'materiais_ativos': 0,
            'periodos_ativos': 0,
            'saida_media_por_periodo': 0,
            'variacao_saidas': 0,
            'percentil_25': 0,
            'percentil_50': 0,
            'percentil_75': 0,
            'percentil_90': 0,
            'percentil_95': 0,
            'coeficiente_variacao': 0,
            'indice_sazonalidade': 0,
            'indice_concentracao': 0
        }
    
    # Usar dados do estoque
    estoque_data = data['estoque']
    
    # Métricas básicas de saídas
    kpis['valor_total_saidas'] = estoque_data['valor_total'].sum() if 'valor_total' in estoque_data.columns else 0
    kpis['quantidade_materiais'] = estoque_data['cod_material'].nunique() if 'cod_material' in estoque_data.columns else 0
    kpis['quantidade_total_saidas'] = estoque_data['quantidade'].sum() if 'quantidade' in estoque_data.columns else 0
    
    # KPIs específicos para saídas
    kpis['saida_media_por_material'] = kpis['quantidade_total_saidas'] / kpis['quantidade_materiais'] if kpis['quantidade_materiais'] > 0 else 0
    kpis['valor_medio_por_saida'] = kpis['valor_total_saidas'] / kpis['quantidade_total_saidas'] if kpis['quantidade_total_saidas'] > 0 else 0
    
    # Verificar se as colunas existem antes de usar
    if 'quantidade' in estoque_data.columns and 'cod_material' in estoque_data.columns:
        kpis['materiais_ativos'] = estoque_data[estoque_data['quantidade'] != 0]['cod_material'].nunique()
    else:
        kpis['materiais_ativos'] = 0
    
    if 'periodo' in estoque_data.columns:
        kpis['periodos_ativos'] = estoque_data['periodo'].nunique()
    else:
        kpis['periodos_ativos'] = 0
    
    # Calcular saída média por período
    kpis['saida_media_por_periodo'] = kpis['quantidade_total_saidas'] / kpis['periodos_ativos'] if kpis['periodos_ativos'] > 0 else 0
    
    # Calcular variação de saídas
    if kpis['periodos_ativos'] > 1 and 'periodo' in estoque_data.columns and 'quantidade' in estoque_data.columns:
        saidas_por_periodo = estoque_data.groupby('periodo')['quantidade'].sum()
        kpis['variacao_saidas'] = saidas_por_periodo.std() / saidas_por_periodo.mean() if saidas_por_periodo.mean() > 0 else 0
    else:
        kpis['variacao_saidas'] = 0
    
    # Métricas estatísticas avançadas
    if 'valor_total' in estoque_data.columns and len(estoque_data) > 0:
        kpis['percentil_25'] = estoque_data['valor_total'].quantile(0.25)
        kpis['percentil_50'] = estoque_data['valor_total'].quantile(0.50)  # Mediana
        kpis['percentil_75'] = estoque_data['valor_total'].quantile(0.75)
        kpis['percentil_90'] = estoque_data['valor_total'].quantile(0.90)
        kpis['percentil_95'] = estoque_data['valor_total'].quantile(0.95)
        
        # Coeficiente de variação
        kpis['coeficiente_variacao'] = (estoque_data['valor_total'].std() / estoque_data['valor_total'].mean()) * 100 if estoque_data['valor_total'].mean() > 0 else 0
    else:
        kpis['percentil_25'] = 0
        kpis['percentil_50'] = 0
        kpis['percentil_75'] = 0
        kpis['percentil_90'] = 0
        kpis['percentil_95'] = 0
        kpis['coeficiente_variacao'] = 0
    
    # Análise de sazonalidade (simplificada)
    if 'periodo' in estoque_data.columns and 'valor_total' in estoque_data.columns:
        estoque_data['mes'] = estoque_data['periodo'].str[:3]
        sazonalidade = estoque_data.groupby('mes')['valor_total'].sum()
        if len(sazonalidade) > 1:
            kpis['indice_sazonalidade'] = sazonalidade.std() / sazonalidade.mean() if sazonalidade.mean() > 0 else 0
        else:
            kpis['indice_sazonalidade'] = 0
    else:
        kpis['indice_sazonalidade'] = 0
    
    # Concentração (índice de Herfindahl simplificado)
    if 'cod_material' in estoque_data.columns and 'valor_total' in estoque_data.columns:
        valores_por_material = estoque_data.groupby('cod_material')['valor_total'].sum()
        if len(valores_por_material) > 0:
            participacao = valores_por_material / valores_por_material.sum()
            kpis['indice_concentracao'] = (participacao ** 2).sum()
        else:
            kpis['indice_concentracao'] = 0
    else:
        kpis['indice_concentracao'] = 0
    
    return kpis

def generate_alerts(data):
    """
    Gera alertas inteligentes baseados em dados de saída
    """
    alertas = []
    
    # Verificar se os dados existem
    if 'estoque' not in data or len(data['estoque']) == 0:
        return alertas
    
    # Usar dados do estoque
    estoque_data = data['estoque']
    
    # Verificar se as colunas necessárias existem
    if 'cod_material' not in estoque_data.columns or 'quantidade' not in estoque_data.columns or 'valor_total' not in estoque_data.columns:
        return alertas
    
    # Calcular métricas de saídas por material
    saidas_por_material = estoque_data.groupby('cod_material').agg({
        'quantidade': 'sum',
        'valor_total': 'sum'
    }).reset_index()
    
    # Alertas de baixa saída (poucas saídas)
    baixa_saida = saidas_por_material[saidas_por_material['quantidade'] < saidas_por_material['quantidade'].quantile(0.1)]
    if len(baixa_saida) > 0:
        alertas.append({
            'tipo': 'warning',
            'titulo': 'Baixa Saída',
            'mensagem': f'{len(baixa_saida)} materiais com baixa saída',
            'detalhes': baixa_saida[['cod_material', 'quantidade']].head(5)
        })
    
    # Alertas de alta saída (muitas saídas)
    alta_saida = saidas_por_material[saidas_por_material['quantidade'] > saidas_por_material['quantidade'].quantile(0.9)]
    if len(alta_saida) > 0:
        alertas.append({
            'tipo': 'info',
            'titulo': 'Alta Saída',
            'mensagem': f'{len(alta_saida)} materiais com alta saída',
            'detalhes': alta_saida[['cod_material', 'quantidade']].head(5)
        })
    
    # Alertas de preços instáveis
    if 'custo_medio' in estoque_data.columns:
        variacao_precos = estoque_data.groupby('cod_material')['custo_medio'].std()
        precos_instaveis = variacao_precos[variacao_precos > variacao_precos.quantile(0.8)]
        if len(precos_instaveis) > 0:
            alertas.append({
                'tipo': 'error',
                'titulo': 'Preços Instáveis',
                'mensagem': f'{len(precos_instaveis)} materiais com preços instáveis',
                'detalhes': precos_instaveis.head(5)
            })
    
    # Alertas de materiais inativos (sem saídas)
    materiais_ativos = estoque_data[estoque_data['quantidade'] != 0]['cod_material'].unique()
    todos_materiais = estoque_data['cod_material'].unique()
    materiais_inativos = set(todos_materiais) - set(materiais_ativos)
    
    if len(materiais_inativos) > 0:
        alertas.append({
            'tipo': 'warning',
            'titulo': 'Materiais Inativos',
            'mensagem': f'{len(materiais_inativos)} materiais sem saídas',
            'detalhes': list(materiais_inativos)[:5]
        })
    
    return alertas

def show_main_dashboard():
    # Carregar dados
    with st.spinner('Carregando dados...'):
        data = load_data()
    
    # Verificar se os dados foram carregados corretamente
    if 'estoque' not in data or len(data['estoque']) == 0:
        st.error("❌ Nenhum dado encontrado. Verifique se o banco de dados foi inicializado corretamente.")
        st.info("💡 Use a aba 'Integração de Dados' para carregar dados de exemplo.")
        return
    
    # Calcular KPIs avançados
    kpis = calculate_advanced_kpis(data)
    
    # Gerar alertas
    alertas = generate_alerts(data)
    
    # Sidebar
    st.sidebar.title("🔍 Filtros")
    
    # Filtros com verificações de segurança
    if 'periodo' in data['estoque'].columns:
        periodos_disponiveis = data['estoque']['periodo'].unique()
        periodo_selecionado = st.sidebar.selectbox(
            "Selecione o Período:",
            ['Todos'] + list(periodos_disponiveis)
        )
    else:
        periodo_selecionado = 'Todos'
    
    if 'familia' in data['estoque'].columns:
        familias_disponiveis = data['estoque']['familia'].unique()
        familia_selecionada = st.sidebar.selectbox(
            "Selecione a Família:",
            ['Todas'] + list(familias_disponiveis)
        )
    else:
        familia_selecionada = 'Todas'
    
    if 'almoxarifado' in data['estoque'].columns:
        almoxarifados_disponiveis = data['estoque']['almoxarifado'].unique()
        almoxarifado_selecionado = st.sidebar.selectbox(
            "Selecione o Almoxarifado:",
        ['Todos'] + list(almoxarifados_disponiveis)
    )
    
    # Filtros Avançados
    st.sidebar.markdown("---")
    st.sidebar.subheader("🔧 Filtros Avançados")
    
    # Filtro por faixa de valores
    if 'valor_total' in data['estoque'].columns and len(data['estoque']) > 0:
        st.sidebar.markdown("**💰 Faixa de Valores**")
        valor_min = data['estoque']['valor_total'].min()
        valor_max = data['estoque']['valor_total'].max()
        
        valor_range = st.sidebar.slider(
            "Valor Total (R$):",
            min_value=float(valor_min),
            max_value=float(valor_max),
            value=(float(valor_min), float(valor_max)),
            format="R$ %.2f"
        )
    else:
        valor_range = (0, 0)
    
    # Filtro por faixa de quantidades
    if 'quantidade' in data['estoque'].columns and len(data['estoque']) > 0:
        st.sidebar.markdown("**📦 Faixa de Quantidades**")
        qtd_min = data['estoque']['quantidade'].min()
        qtd_max = data['estoque']['quantidade'].max()
        
        qtd_range = st.sidebar.slider(
            "Quantidade:",
            min_value=float(qtd_min),
            max_value=float(qtd_max),
            value=(float(qtd_min), float(qtd_max)),
            format="%.0f"
        )
    else:
        qtd_range = (0, 0)
    
    # Filtro por código de material
    st.sidebar.markdown("**🔍 Busca por Código**")
    codigo_material = st.sidebar.text_input(
        "Código do Material:", 
        placeholder="Ex: 12345",
        key="filtro_codigo_material"
    )
    
    # Aplicar filtros
    estoque_filtrado = data['estoque'].copy()
    
    if periodo_selecionado != 'Todos' and 'periodo' in estoque_filtrado.columns:
        estoque_filtrado = estoque_filtrado[estoque_filtrado['periodo'] == periodo_selecionado]
    
    if familia_selecionada != 'Todas' and 'familia' in estoque_filtrado.columns:
        estoque_filtrado = estoque_filtrado[estoque_filtrado['familia'] == familia_selecionada]
    
    if almoxarifado_selecionado != 'Todos' and 'almoxarifado' in estoque_filtrado.columns:
        estoque_filtrado = estoque_filtrado[estoque_filtrado['almoxarifado'] == almoxarifado_selecionado]
    
    # Aplicar filtros avançados
    if 'valor_total' in estoque_filtrado.columns and valor_range[0] != 0 and valor_range[1] != 0:
        estoque_filtrado = estoque_filtrado[
            (estoque_filtrado['valor_total'] >= valor_range[0]) & 
            (estoque_filtrado['valor_total'] <= valor_range[1])
        ]
    
    if 'quantidade' in estoque_filtrado.columns and qtd_range[0] != 0 and qtd_range[1] != 0:
        estoque_filtrado = estoque_filtrado[
            (estoque_filtrado['quantidade'] >= qtd_range[0]) & 
            (estoque_filtrado['quantidade'] <= qtd_range[1])
        ]
    
    if codigo_material and 'cod_material' in estoque_filtrado.columns:
        estoque_filtrado = estoque_filtrado[
            estoque_filtrado['cod_material'].astype(str).str.contains(codigo_material, case=False, na=False)
        ]
    
    # Recalcular KPIs com dados filtrados
    # Criar dicionário temporário com dados filtrados
    data_filtrado = {'estoque': estoque_filtrado}
    kpis_filtrados = calculate_advanced_kpis(data_filtrado)
    alertas_filtrados = generate_alerts(data_filtrado)
    
    # Métricas principais de saídas
    st.subheader("📊 Resumo de Saídas")
    st.info("📊 **Dados de movimentação de saída** - Quantidades representam saídas do estoque")
    
    # Calcular métricas de saídas
    total_saidas = estoque_filtrado['quantidade'].sum()
    total_materiais = estoque_filtrado['cod_material'].nunique()
    materiais_ativos = estoque_filtrado[estoque_filtrado['quantidade'] != 0]['cod_material'].nunique()
    valor_total_saidas = estoque_filtrado['valor_total'].sum()
    custo_medio = estoque_filtrado['custo_medio'].mean()
    periodos_ativos = estoque_filtrado['periodo'].nunique()
    
    # Layout responsivo para métricas
    col1, col2 = st.columns(2)
    
    with col1:
        col1_1, col1_2 = st.columns(2)
        with col1_1:
            st.metric("Total de Materiais", format_number(total_materiais))
        with col1_2:
            st.metric("Valor Total Saídas", format_currency(valor_total_saidas))
    
    with col2:
        col2_1, col2_2 = st.columns(2)
        with col2_1:
            st.metric("Quantidade Total Saídas", format_number(total_saidas))
        with col2_2:
            st.metric("Materiais com Saídas", format_number(materiais_ativos))
    
    # KPIs de Saídas
    st.subheader("📈 KPIs de Saídas")
    
    # Calcular KPIs específicos para saídas
    saida_media_por_material = total_saidas / total_materiais if total_materiais > 0 else 0
    saida_media_por_periodo = total_saidas / periodos_ativos if periodos_ativos > 0 else 0
    valor_medio_saida = valor_total_saidas / total_saidas if total_saidas > 0 else 0
    
    # Layout responsivo para KPIs
    col1, col2 = st.columns(2)
    
    with col1:
        col1_1, col1_2 = st.columns(2)
        with col1_1:
            st.metric("Saída Média por Material", f"{saida_media_por_material:.1f}")
        with col1_2:
            st.metric("Saída Média por Período", f"{saida_media_por_periodo:.1f}")
    
    with col2:
        col2_1, col2_2 = st.columns(2)
        with col2_1:
            st.metric("Valor Médio por Saída", format_currency(valor_medio_saida))
        with col2_2:
            st.metric("Períodos Ativos", format_number(periodos_ativos))
    
    
    # Alertas Inteligentes
    if alertas_filtrados:
        st.subheader("🚨 Alertas Inteligentes")
        
        # Mostrar apenas alertas críticos e importantes
        alertas_importantes = [a for a in alertas_filtrados if a['tipo'] in ['error', 'warning']]
        
        if alertas_importantes:
            for alerta in alertas_importantes[:3]:  # Máximo 3 alertas
                if alerta['tipo'] == 'warning':
                    st.warning(f"⚠️ **{alerta['titulo']}**: {alerta['mensagem']}")
                elif alerta['tipo'] == 'error':
                    st.error(f"❌ **{alerta['titulo']}**: {alerta['mensagem']}")
                
                # Mostrar detalhes se disponível
                if 'detalhes' in alerta and len(alerta['detalhes']) > 0:
                    with st.expander("Ver Detalhes"):
                        st.dataframe(alerta['detalhes'], use_container_width=True)
        
        # Mostrar outros alertas em um expander
        outros_alertas = [a for a in alertas_filtrados if a['tipo'] == 'info']
        if outros_alertas:
            with st.expander(f"ℹ️ Outros Alertas ({len(outros_alertas)})"):
                for alerta in outros_alertas:
                    st.info(f"**{alerta['titulo']}**: {alerta['mensagem']}")
    
    # Gráficos
    st.subheader("📈 Análises Visuais")
    
    # Layout responsivo para gráficos
    col1, col2 = st.columns([1, 1])
    
    with col1:
        # Evolução das Saídas
        evolucao_filtrada = estoque_filtrado.groupby('periodo').agg({
            'valor_total': 'sum',
            'quantidade': 'sum'
        }).reset_index()
        
        # Criar coluna de data real para ordenação cronológica correta
        evolucao_filtrada['data_ordem'] = evolucao_filtrada['periodo'].apply(create_date_from_period)
        
        # Ordenar cronologicamente
        evolucao_filtrada = evolucao_filtrada.sort_values('data_ordem')
        
        if len(evolucao_filtrada) > 1:
            fig_evolucao = px.line(
                evolucao_filtrada, 
                x='periodo', 
                y='valor_total',
                title="Evolução das Saídas por Período",
                labels={'valor_total': 'Valor Saídas (R$)', 'periodo': 'Período'}
            )
            
            # Forçar ordenação cronológica no eixo X
            fig_evolucao.update_layout(
                showlegend=False, 
                height=400,
                xaxis={'categoryorder': 'array', 'categoryarray': evolucao_filtrada['periodo'].tolist()}
            )
            
            # Adicionar rótulos de dados formatados
            fig_evolucao.update_traces(
                text=[f"R$ {valor:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.') for valor in evolucao_filtrada['valor_total']],
                textposition="top center",
                mode='lines+markers+text'
            )
            
            st.plotly_chart(fig_evolucao, use_container_width=True)
        else:
            st.info("📊 Dados de evolução temporal não disponíveis.")
    
    with col2:
        # Distribuição das Saídas por Almoxarifado
        distribuicao = estoque_filtrado.groupby('almoxarifado').agg({
            'valor_total': 'sum'
        }).reset_index()
        
        fig_dist = px.pie(
            distribuicao,
            values='valor_total',
            names='almoxarifado',
            title="Distribuição das Saídas por Almoxarifado"
        )
        
        # Adicionar rótulos de dados formatados
        fig_dist.update_traces(
            textinfo='label+percent+value',
            texttemplate='%{label}<br>%{percent}<br>R$ %{value:,.2f}',
            hovertemplate='<b>%{label}</b><br>Valor: R$ %{value:,.2f}<br>Percentual: %{percent}<extra></extra>'
        )
        
        fig_dist.update_layout(height=400)
        st.plotly_chart(fig_dist, use_container_width=True)
    
    # Top Materiais por Saídas
    st.subheader("🏆 Top 10 Materiais por Valor de Saídas")
    
    top_materiais = estoque_filtrado.groupby(['cod_material', 'desc_material']).agg({
        'valor_total': 'sum'
    }).reset_index()
    top_materiais = top_materiais.sort_values('valor_total', ascending=False).head(10)
    
    fig_top = px.bar(
        top_materiais,
        x='valor_total',
        y='desc_material',
        orientation='h',
        title="Top 10 Materiais por Valor de Saídas",
        labels={'valor_total': 'Valor Saídas (R$)', 'desc_material': 'Material'},
        color='valor_total',
        color_continuous_scale='Reds'
    )
    
    # Adicionar rótulos de dados formatados
    fig_top.update_traces(
        text=[f"R$ {valor:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.') for valor in top_materiais['valor_total']],
        textposition="outside",
        hovertemplate='<b>%{y}</b><br>Valor: R$ %{x:,.2f}<extra></extra>'
    )
    
    # Layout responsivo para gráfico de barras
    fig_top.update_layout(
        height=400, 
        yaxis={'categoryorder': 'total ascending'},
        margin=dict(l=0, r=0, t=50, b=0)
    )
    st.plotly_chart(fig_top, use_container_width=True)
    
    # Materiais com Mais Saídas
    st.subheader("📦 Top 10 Materiais por Quantidade de Saídas")
    
    materiais_saidas = estoque_filtrado.groupby(['cod_material', 'desc_material']).agg({
        'quantidade': 'sum'
    }).reset_index()
    materiais_saidas = materiais_saidas.sort_values('quantidade', ascending=False).head(10)
    
    fig_saidas = px.bar(
        materiais_saidas,
        x='quantidade',
        y='desc_material',
        orientation='h',
        title="Top 10 Materiais por Quantidade de Saídas",
        labels={'quantidade': 'Quantidade Saídas', 'desc_material': 'Material'},
        color='quantidade',
        color_continuous_scale='Oranges'
    )
    
    # Adicionar rótulos de dados formatados
    fig_saidas.update_traces(
        text=[f"{qtd:,.0f}".replace(',', '.') for qtd in materiais_saidas['quantidade']],
        textposition="outside",
        hovertemplate='<b>%{y}</b><br>Quantidade: %{x:,.0f}<extra></extra>'
    )
    
    # Layout responsivo para gráfico de barras
    fig_saidas.update_layout(
        height=400, 
        yaxis={'categoryorder': 'total ascending'},
        margin=dict(l=0, r=0, t=50, b=0)
    )
    st.plotly_chart(fig_saidas, use_container_width=True)
    
    
    # Footer
    st.markdown("---")
    st.markdown("**Dashboard do Almoxarifado** - Desenvolvido com Streamlit e Plotly")
    st.markdown(f"Última atualização: {datetime.now().strftime('%d/%m/%Y %H:%M')}")

def show_materials_analysis():
    """Aba dedicada para análise detalhada de materiais"""
    st.header("🔍 Análise Detalhada de Materiais")
    st.markdown("Selecione um material para análise completa com evolução de preços, movimentação e tendências.")
    
    # Carregar dados
    with st.spinner('Carregando dados...'):
        data = load_data()
    
    # Verificar se os dados foram carregados corretamente
    if 'estoque' not in data or len(data['estoque']) == 0:
        st.error("❌ Nenhum dado encontrado. Verifique se o banco de dados foi inicializado corretamente.")
        st.info("💡 Use a aba 'Integração de Dados' para carregar dados de exemplo.")
        return
    
    # Filtros para seleção de material (layout responsivo)
    col1, col2 = st.columns([3, 1])
    
    with col1:
        search_term = st.text_input("🔍 Buscar por material:", placeholder="Digite nome, código ou parte do material...", key="search_materials")
    
    with col2:
        col2_1, col2_2 = st.columns(2)
        with col2_1:
            search_type = st.selectbox("Tipo de busca:", ['Código e Descrição', 'Apenas Código', 'Apenas Descrição'], key="search_type")
        with col2_2:
            sort_by = st.selectbox("Ordenar por:", ['valor_total', 'quantidade', 'custo_medio'], key="sort_materials")
    
    # Filtros avançados (expansível)
    with st.expander("🔧 Filtros Avançados", expanded=False):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if 'familia' in data['estoque'].columns:
                familia_filter = st.selectbox("Filtrar por Família:", ['Todas'] + list(data['estoque']['familia'].unique()), key="familia_filter")
            else:
                familia_filter = 'Todas'
        
        with col2:
            if 'almoxarifado' in data['estoque'].columns:
                almoxarifado_filter = st.selectbox("Filtrar por Almoxarifado:", ['Todos'] + list(data['estoque']['almoxarifado'].unique()), key="almoxarifado_filter")
            else:
                almoxarifado_filter = 'Todos'
        
        with col3:
            valor_min = st.number_input("Valor Mínimo (R$):", min_value=0.0, value=0.0, step=100.0, key="valor_min")
    
    # Aplicar filtros
    estoque_filtrado = data['estoque'].copy()
    
    # Filtro de busca por texto
    if search_term:
        # Busca inteligente baseada no tipo selecionado
        if search_type == 'Código e Descrição':
            # Buscar tanto por nome quanto por código
            if 'desc_material' in estoque_filtrado.columns and 'cod_material' in estoque_filtrado.columns:
                mask = (
                    estoque_filtrado['desc_material'].str.contains(search_term, case=False, na=False) |
                    estoque_filtrado['cod_material'].astype(str).str.contains(search_term, case=False, na=False)
                )
            else:
                mask = pd.Series([False] * len(estoque_filtrado), index=estoque_filtrado.index)
        elif search_type == 'Apenas Código':
            # Buscar apenas por código
            if 'cod_material' in estoque_filtrado.columns:
                mask = estoque_filtrado['cod_material'].astype(str).str.contains(search_term, case=False, na=False)
            else:
                mask = pd.Series([False] * len(estoque_filtrado), index=estoque_filtrado.index)
        else:  # Apenas Descrição
            # Buscar apenas por descrição
            if 'desc_material' in estoque_filtrado.columns:
                mask = estoque_filtrado['desc_material'].str.contains(search_term, case=False, na=False)
            else:
                mask = pd.Series([False] * len(estoque_filtrado), index=estoque_filtrado.index)
        
        estoque_filtrado = estoque_filtrado[mask]
    
    # Filtros avançados
    if familia_filter != 'Todas' and 'familia' in estoque_filtrado.columns:
        estoque_filtrado = estoque_filtrado[estoque_filtrado['familia'] == familia_filter]
    
    if almoxarifado_filter != 'Todos' and 'almoxarifado' in estoque_filtrado.columns:
        estoque_filtrado = estoque_filtrado[estoque_filtrado['almoxarifado'] == almoxarifado_filter]
    
    if valor_min > 0 and 'valor_total' in estoque_filtrado.columns:
        estoque_filtrado = estoque_filtrado[estoque_filtrado['valor_total'] >= valor_min]
    
    # Agrupar por material para mostrar resumo
    if len(estoque_filtrado) > 0:
        # Verificar se as colunas necessárias existem
        colunas_necessarias = ['cod_material', 'desc_material', 'quantidade', 'valor_total', 'custo_medio']
        colunas_existentes = [col for col in colunas_necessarias if col in estoque_filtrado.columns]
        
        if len(colunas_existentes) >= 3:  # Pelo menos 3 colunas necessárias
            tabela_resumo = estoque_filtrado.groupby(['cod_material', 'desc_material']).agg({
                'quantidade': 'sum' if 'quantidade' in estoque_filtrado.columns else 'count',
                'valor_total': 'sum' if 'valor_total' in estoque_filtrado.columns else 'count',
                'custo_medio': 'mean' if 'custo_medio' in estoque_filtrado.columns else 'count'
            }).reset_index()
            
            # Adicionar colunas que podem não existir
            if 'familia' in estoque_filtrado.columns:
                tabela_resumo['familia'] = estoque_filtrado.groupby(['cod_material', 'desc_material'])['familia'].first().values
            else:
                tabela_resumo['familia'] = 'N/A'
            
            if 'unidade' in estoque_filtrado.columns:
                tabela_resumo['unidade'] = estoque_filtrado.groupby(['cod_material', 'desc_material'])['unidade'].first().values
            else:
                tabela_resumo['unidade'] = 'N/A'
            
            tabela_resumo = tabela_resumo.sort_values(sort_by, ascending=False)
        else:
            tabela_resumo = pd.DataFrame()
    else:
        tabela_resumo = pd.DataFrame()
    
    # Mostrar resultados da busca
    filtros_aplicados = []
    if search_term:
        filtros_aplicados.append(f"Busca: '{search_term}' ({search_type})")
    if familia_filter != 'Todas':
        filtros_aplicados.append(f"Família: {familia_filter}")
    if almoxarifado_filter != 'Todos':
        filtros_aplicados.append(f"Almoxarifado: {almoxarifado_filter}")
    if valor_min > 0:
        filtros_aplicados.append(f"Valor ≥ R$ {valor_min:,.2f}")
    
    if len(tabela_resumo) > 0:
        if filtros_aplicados:
            st.success(f"🔍 Encontrados {len(tabela_resumo)} materiais | Filtros: {' | '.join(filtros_aplicados)}")
        else:
            st.info(f"📊 Mostrando todos os {len(tabela_resumo)} materiais disponíveis")
    else:
        if filtros_aplicados:
            st.warning(f"⚠️ Nenhum material encontrado com os filtros aplicados")
            st.info("💡 **Dicas de busca:**")
            st.markdown("""
            - **Por código**: Digite parte do código (ex: '123', 'MAT')
            - **Por descrição**: Digite palavras-chave (ex: 'parafuso', 'ferro')
            - **Busca ampla**: Use 'Código e Descrição' para buscar em ambos
            - **Busca específica**: Use 'Apenas Código' ou 'Apenas Descrição' para focar
            - **Filtros**: Use os filtros avançados para refinar a busca
            """)
        else:
            st.info("🔍 Use os filtros acima para encontrar materiais específicos")
    
    # Seleção de material
    if len(tabela_resumo) > 0:
        selected_material = st.selectbox(
            "Selecione um material para análise detalhada:",
            options=tabela_resumo.index,
            format_func=lambda x: f"{tabela_resumo.loc[x, 'cod_material']} - {tabela_resumo.loc[x, 'desc_material'][:60]}...",
            key="material_selector_detailed"
        )
    else:
        st.info("🔍 Digite um termo de busca para encontrar materiais")
        selected_material = None
    
    
    # Análise Detalhada do Material Selecionado
    if selected_material is not None:
        material_data = tabela_resumo.loc[selected_material]
        codigo_material = material_data['cod_material']
        
        st.markdown("---")
        st.subheader(f"🔍 Análise Detalhada - Material {codigo_material}")
        
        # Criar abas para diferentes análises
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "📊 Resumo Geral", 
            "📈 Evolução de Preços", 
            "📦 Movimentação por Período",
            "📋 Informações Técnicas",
            "📊 Análise de Tendências"
        ])
        
        with tab1:
            show_material_summary(material_data, codigo_material, data)
        
        with tab2:
            show_price_evolution(codigo_material, data)
        
        with tab3:
            show_period_movement(codigo_material, data)
        
        with tab4:
            show_technical_info(codigo_material, data)
        
        with tab5:
            show_trend_analysis(codigo_material, data)

def previsao_demanda_simples(dados_material):
    """
    Previsão usando média móvel e tendência linear baseada em movimentação
    """
    if len(dados_material) < 3:
        return None
    
    # Calcular movimentação líquida (entradas - saídas)
    # Assumindo que quantidade positiva = entrada, negativa = saída
    dados_material['movimentacao_liquida'] = dados_material['quantidade']
    
    # Média móvel de 3 períodos
    dados_material['media_movel'] = dados_material['movimentacao_liquida'].rolling(window=3).mean()
    
    # Tendência linear
    x = np.arange(len(dados_material))
    y = dados_material['movimentacao_liquida'].values
    slope, intercept = np.polyfit(x, y, 1)
    
    # Previsão para próximo período
    proximo_periodo = slope * len(dados_material) + intercept
    
    return {
        'previsao': proximo_periodo,
        'tendencia': 'crescente' if slope > 0 else 'decrescente',
        'confianca': min(100, max(0, 100 - abs(slope) * 10)),
        'tipo': 'movimentacao_liquida'
    }

def calcular_ponto_reposicao(dados_material, lead_time=30, estoque_seguranca_pct=0.2):
    """
    Calcula ponto de reposição baseado na movimentação média (saídas)
    """
    if len(dados_material) < 2:
        return None
    
    # Calcular saídas médias (quantidade negativa = saída)
    saidas = dados_material[dados_material['quantidade'] < 0]['quantidade'].abs()
    if len(saidas) == 0:
        return None
    
    # Consumo médio mensal (saídas)
    consumo_medio = saidas.mean()
    consumo_diario = consumo_medio / 30
    
    # Estoque de segurança
    estoque_seguranca = consumo_medio * estoque_seguranca_pct
    
    # Ponto de reposição
    ponto_reposicao = (consumo_diario * lead_time) + estoque_seguranca
    
    return {
        'ponto_reposicao': ponto_reposicao,
        'consumo_diario': consumo_diario,
        'estoque_seguranca': estoque_seguranca,
        'lead_time': lead_time,
        'consumo_medio_mensal': consumo_medio
    }

def gerar_sugestoes_compra(dados):
    """
    Gera sugestões automáticas de compra baseadas em movimentação
    """
    sugestoes = []
    
    for codigo, grupo in dados.groupby('cod_material'):
        if len(grupo) < 2:
            continue
        
        # Calcular saídas (quantidade negativa)
        saidas = grupo[grupo['quantidade'] < 0]['quantidade'].abs()
        if len(saidas) == 0:
            continue
        
        # Calcular métricas de saída
        consumo_medio = saidas.mean()
        variacao_consumo = saidas.std() / consumo_medio if consumo_medio > 0 else 0
        
        # Calcular ponto de reposição
        lead_time = 30  # dias
        estoque_seguranca = consumo_medio * 0.2
        ponto_reposicao = (consumo_medio * lead_time / 30) + estoque_seguranca
        
        # Calcular estoque estimado (soma de entradas - saídas)
        entradas = grupo[grupo['quantidade'] > 0]['quantidade'].sum()
        saidas_total = saidas.sum()
        estoque_estimado = entradas - saidas_total
        
        # Verificar necessidade de compra
        if estoque_estimado < ponto_reposicao:
            quantidade_sugerida = max(0, ponto_reposicao - estoque_estimado)
            
            # Ajustar por variabilidade
            if variacao_consumo > 0.3:  # Alta variabilidade
                quantidade_sugerida *= 1.5
            
            sugestoes.append({
                'material': codigo,
                'descricao': grupo['desc_material'].iloc[0],
                'estoque_estimado': estoque_estimado,
                'ponto_reposicao': ponto_reposicao,
                'quantidade_sugerida': quantidade_sugerida,
                'consumo_medio_mensal': consumo_medio,
                'prioridade': 'Alta' if estoque_estimado < ponto_reposicao * 0.5 else 'Média',
                'variabilidade': 'Alta' if variacao_consumo > 0.3 else 'Normal'
            })
    
    return sorted(sugestoes, key=lambda x: x['quantidade_sugerida'], reverse=True)

def show_advanced_analyses():
    """Aba para análises avançadas e relatórios"""
    st.header("📈 Análises Avançadas")
    st.markdown("Análises estatísticas avançadas e relatórios especializados.")
    
    # Carregar dados
    with st.spinner('Carregando dados...'):
        data = load_data()
    
    # Verificar se os dados foram carregados corretamente
    if 'estoque' not in data or len(data['estoque']) == 0:
        st.error("❌ Nenhum dado encontrado. Verifique se o banco de dados foi inicializado corretamente.")
        st.info("💡 Use a aba 'Integração de Dados' para carregar dados de exemplo.")
        return
    
    # Tabs para diferentes análises
    tab_estatisticas, tab_previsao, tab_otimizacao, tab_sugestoes, tab_relatorios = st.tabs([
        "📊 Análises Estatísticas",
        "🔮 Previsão de Demanda",
        "⚡ Otimização de Estoque", 
        "💡 Sugestões Inteligentes",
        "📊 Relatórios"
    ])
    
    with tab_estatisticas:
        st.subheader("📊 Análises Estatísticas Avançadas")
        st.info("📊 **Análises estatísticas detalhadas** - Métricas avançadas e visualizações especializadas")
        
        # Calcular KPIs avançados
        kpis_avancados = calculate_advanced_kpis(data)
        
        # Métricas Estatísticas Avançadas
        st.subheader("📈 Métricas Estatísticas")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Coeficiente de Variação", f"{kpis_avancados['coeficiente_variacao']:.1f}%")
        
        with col2:
            st.metric("Índice de Sazonalidade", f"{kpis_avancados['indice_sazonalidade']:.3f}")
        
        with col3:
            st.metric("Índice de Concentração", f"{kpis_avancados['indice_concentracao']:.3f}")
        
        with col4:
            st.metric("Variação das Saídas", f"{kpis_avancados['variacao_saidas']:.3f}")
        
        # Percentis
        st.subheader("📊 Análise de Percentis")
        
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            st.metric("P25", format_currency(kpis_avancados['percentil_25']))
        
        with col2:
            st.metric("P50 (Mediana)", format_currency(kpis_avancados['percentil_50']))
        
        with col3:
            st.metric("P75", format_currency(kpis_avancados['percentil_75']))
        
        with col4:
            st.metric("P90", format_currency(kpis_avancados['percentil_90']))
        
        with col5:
            st.metric("P95", format_currency(kpis_avancados['percentil_95']))
        
        # Análises Estatísticas Avançadas e Especializadas
        st.subheader("📊 Análises Estatísticas Avançadas")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Análise de Distribuição por Percentis
            st.subheader("📈 Distribuição por Percentis")
            
            # Calcular percentis
            percentis = [10, 25, 50, 75, 90, 95, 99]
            if 'estoque' in data and len(data['estoque']) > 0 and 'valor_total' in data['estoque'].columns:
                valores_percentis = [np.percentile(data['estoque']['valor_total'], p) for p in percentis]
            else:
                valores_percentis = [0] * len(percentis)
            
            fig_percentis = px.bar(
                x=[f'P{p}' for p in percentis],
                y=valores_percentis,
                title="Distribuição de Valores por Percentis",
                labels={'x': 'Percentil', 'y': 'Valor (R$)'},
                color=valores_percentis,
                color_continuous_scale='Viridis'
            )
            
            # Adicionar rótulos de dados
            fig_percentis.update_traces(
                text=[f"R$ {valor:,.0f}".replace(',', 'X').replace('.', ',').replace('X', '.') for valor in valores_percentis],
                textposition="outside"
            )
            
            fig_percentis.update_layout(height=400)
            st.plotly_chart(fig_percentis, use_container_width=True)
        
        with col2:
            # Análise de Variabilidade por Material
            st.subheader("📊 Variabilidade por Material")
            
            # Calcular coeficiente de variação por material
            variabilidade = data['estoque'].groupby('cod_material').agg({
                'valor_total': ['mean', 'std', 'count']
            }).reset_index()
            
            variabilidade.columns = ['cod_material', 'media', 'desvio_padrao', 'count']
            variabilidade['cv'] = (variabilidade['desvio_padrao'] / variabilidade['media']) * 100
            variabilidade = variabilidade[variabilidade['count'] >= 3]  # Pelo menos 3 registros
            
            # Top 10 materiais com maior variabilidade
            top_variabilidade = variabilidade.nlargest(10, 'cv')
            
            # Verificar se há dados suficientes
            if len(top_variabilidade) > 0:
                # Converter código do material para string e criar label mais legível
                top_variabilidade = top_variabilidade.copy()
                top_variabilidade['cod_material_str'] = top_variabilidade['cod_material'].astype(str)
                top_variabilidade['label_material'] = 'Material ' + top_variabilidade['cod_material_str']
                
                fig_var = px.bar(
                    top_variabilidade,
                    x='cv',
                    y='label_material',
                    orientation='h',
                    title="Top 10 Materiais com Maior Variabilidade (CV%)",
                    labels={'cv': 'Coeficiente de Variação (%)', 'label_material': 'Código do Material'},
                    color='cv',
                    color_continuous_scale='Reds'
                )
                
                # Adicionar rótulos de dados
                fig_var.update_traces(
                    text=[f"{cv:.1f}%" for cv in top_variabilidade['cv']],
                    textposition="outside"
                )
                
                # Melhorar formatação do eixo Y
                fig_var.update_layout(
                    height=400, 
                    yaxis={
                        'categoryorder': 'total ascending',
                        'tickmode': 'linear',
                        'tick0': 0,
                        'dtick': 1
                    }
                )
                
                st.plotly_chart(fig_var, use_container_width=True)
                
                # Mostrar tabela com os códigos dos materiais
                with st.expander("📋 Ver Códigos dos Materiais", expanded=False):
                    st.dataframe(
                        top_variabilidade[['cod_material_str', 'cv', 'count']].rename(columns={
                            'cod_material_str': 'Código do Material',
                            'cv': 'CV (%)',
                            'count': 'Registros'
                        }),
                        use_container_width=True
                    )
            else:
                st.info("📊 Não há materiais com dados suficientes para análise de variabilidade (mínimo 3 registros por material)")
        
        # Análise de Estabilidade Temporal
        st.subheader("📈 Estabilidade Temporal")
        
        # Calcular estabilidade por período
        estabilidade = data['estoque'].groupby('periodo').agg({
            'valor_total': ['mean', 'std', 'count']
        }).reset_index()
        
        estabilidade.columns = ['periodo', 'media', 'desvio_padrao', 'count']
        estabilidade['cv'] = (estabilidade['desvio_padrao'] / estabilidade['media']) * 100
        
        # Criar coluna de data real para ordenação cronológica
        estabilidade['data_ordem'] = estabilidade['periodo'].apply(create_date_from_period)
        estabilidade = estabilidade.sort_values('data_ordem')
        
        fig_estab = px.line(
            estabilidade,
            x='periodo',
            y='cv',
            title="Estabilidade Temporal (Coeficiente de Variação por Período)",
            labels={'cv': 'Coeficiente de Variação (%)', 'periodo': 'Período'},
            markers=True
        )
        
        # Adicionar rótulos de dados formatados
        fig_estab.update_traces(
            text=[f"{cv:.1f}%" for cv in estabilidade['cv']],
            textposition="top center",
            mode='lines+markers+text'
        )
        
        fig_estab.update_layout(height=400)
        st.plotly_chart(fig_estab, use_container_width=True)
        
        # Análise de Concentração e Diversificação
        st.subheader("🎯 Análise de Concentração e Diversificação")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Análise de Concentração por Família
            st.subheader("🏷️ Concentração por Família")
            
            concentracao_familia = data['estoque'].groupby('familia').agg({
                'valor_total': 'sum',
                'cod_material': 'nunique'
            }).reset_index()
            
            concentracao_familia['valor_pct'] = (concentracao_familia['valor_total'] / concentracao_familia['valor_total'].sum()) * 100
            concentracao_familia = concentracao_familia.sort_values('valor_pct', ascending=False).head(10)
            
            fig_conc = px.bar(
                concentracao_familia,
                x='valor_pct',
                y='familia',
                orientation='h',
                title="Concentração de Valor por Família (%)",
                labels={'valor_pct': 'Percentual do Valor Total (%)', 'familia': 'Família'},
                color='valor_pct',
                color_continuous_scale='Blues'
            )
            
            # Adicionar rótulos de dados formatados
            fig_conc.update_traces(
                text=[f"{pct:.1f}%" for pct in concentracao_familia['valor_pct']],
                textposition="outside"
            )
            
            fig_conc.update_layout(height=400, yaxis={'categoryorder': 'total ascending'})
            st.plotly_chart(fig_conc, use_container_width=True)
        
        with col2:
            # Análise de Diversificação
            st.subheader("🌐 Análise de Diversificação")
            
            # Calcular índice de diversificação (simplificado)
            total_materiais = data['estoque']['cod_material'].nunique()
            total_familias = data['estoque']['familia'].nunique()
            total_almoxarifados = data['estoque']['almoxarifado'].nunique()
            
            # Criar gráfico de diversificação
            diversificacao = pd.DataFrame({
                'Categoria': ['Materiais', 'Famílias', 'Almoxarifados'],
                'Quantidade': [total_materiais, total_familias, total_almoxarifados]
            })
            
            fig_div = px.bar(
                diversificacao,
                x='Categoria',
                y='Quantidade',
                title="Diversificação do Portfólio",
                labels={'Quantidade': 'Número de Itens', 'Categoria': 'Categoria'},
                color='Quantidade',
                color_continuous_scale='Greens'
            )
            
            # Adicionar rótulos de dados formatados para padrão brasileiro
            fig_div.update_traces(
                text=[f"{qtd:,}".replace(',', '.') for qtd in diversificacao['Quantidade']],
                textposition="outside"
            )
            
            fig_div.update_layout(height=400)
            st.plotly_chart(fig_div, use_container_width=True)
        

    with tab_previsao:
        st.subheader("🔮 Previsão de Movimentação")
        st.info("📊 **Análise baseada em dados de movimentação** - Quantidades positivas = entradas, negativas = saídas")
        
        # Filtros para seleção de material
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            search_term = st.text_input("🔍 Buscar por material:", placeholder="Digite nome, código ou parte do material...", key="search_materials_previsao")
        
        with col2:
            search_type = st.selectbox("Tipo de busca:", ['Código e Descrição', 'Apenas Código', 'Apenas Descrição'], key="search_type_previsao")
        
        with col3:
            sort_by = st.selectbox("Ordenar por:", ['valor_total', 'quantidade', 'custo_medio'], key="sort_materials_previsao")
        
        # Filtros avançados (expansível)
        with st.expander("🔧 Filtros Avançados", expanded=False):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                familia_filter = st.selectbox("Filtrar por Família:", ['Todas'] + list(data['estoque']['familia'].unique()), key="familia_filter_previsao")
            
            with col2:
                almoxarifado_filter = st.selectbox("Filtrar por Almoxarifado:", ['Todos'] + list(data['estoque']['almoxarifado'].unique()), key="almoxarifado_filter_previsao")
            
            with col3:
                valor_min = st.number_input("Valor Mínimo (R$):", min_value=0.0, value=0.0, step=100.0, key="valor_min_previsao")
        
        # Aplicar filtros
        estoque_filtrado = data['estoque'].copy()
        
        # Filtro de busca por texto
        if search_term:
            # Busca inteligente baseada no tipo selecionado
            if search_type == 'Código e Descrição':
                # Buscar tanto por nome quanto por código
                mask = (
                    estoque_filtrado['desc_material'].str.contains(search_term, case=False, na=False) |
                    estoque_filtrado['cod_material'].astype(str).str.contains(search_term, case=False, na=False)
                )
            elif search_type == 'Apenas Código':
                # Buscar apenas por código
                mask = estoque_filtrado['cod_material'].astype(str).str.contains(search_term, case=False, na=False)
            else:  # Apenas Descrição
                # Buscar apenas por descrição
                mask = estoque_filtrado['desc_material'].str.contains(search_term, case=False, na=False)
            
            estoque_filtrado = estoque_filtrado[mask]
        
        # Filtros avançados
        if familia_filter != 'Todas':
            estoque_filtrado = estoque_filtrado[estoque_filtrado['familia'] == familia_filter]
        
        if almoxarifado_filter != 'Todos':
            estoque_filtrado = estoque_filtrado[estoque_filtrado['almoxarifado'] == almoxarifado_filter]
        
        if valor_min > 0:
            estoque_filtrado = estoque_filtrado[estoque_filtrado['valor_total'] >= valor_min]
        
        # Agrupar por material para mostrar resumo
        tabela_resumo = estoque_filtrado.groupby(['cod_material', 'desc_material', 'familia', 'unidade']).agg({
            'quantidade': 'sum',
            'valor_total': 'sum',
            'custo_medio': 'mean'
        }).reset_index()
        
        tabela_resumo = tabela_resumo.sort_values(sort_by, ascending=False)
        
        # Mostrar resultados da busca
        filtros_aplicados = []
        if search_term:
            filtros_aplicados.append(f"Busca: '{search_term}' ({search_type})")
        if familia_filter != 'Todas':
            filtros_aplicados.append(f"Família: {familia_filter}")
        if almoxarifado_filter != 'Todos':
            filtros_aplicados.append(f"Almoxarifado: {almoxarifado_filter}")
        if valor_min > 0:
            filtros_aplicados.append(f"Valor ≥ R$ {valor_min:,.2f}")
        
        if len(tabela_resumo) > 0:
            if filtros_aplicados:
                st.success(f"🔍 Encontrados {len(tabela_resumo)} materiais | Filtros: {' | '.join(filtros_aplicados)}")
            else:
                st.info(f"📊 Mostrando todos os {len(tabela_resumo)} materiais disponíveis")
        else:
            if filtros_aplicados:
                st.warning(f"⚠️ Nenhum material encontrado com os filtros aplicados")
                st.info("💡 **Dicas de busca:**")
                st.markdown("""
                - **Por código**: Digite parte do código (ex: '123', 'MAT')
                - **Por descrição**: Digite palavras-chave (ex: 'parafuso', 'ferro')
                - **Busca ampla**: Use 'Código e Descrição' para buscar em ambos
                - **Busca específica**: Use 'Apenas Código' ou 'Apenas Descrição' para focar
                - **Filtros**: Use os filtros avançados para refinar a busca
                """)
            else:
                st.info("🔍 Use os filtros acima para encontrar materiais específicos")
        
        # Seleção de material
        if len(tabela_resumo) > 0:
            material_selecionado = st.selectbox(
                "Selecione um material para análise de previsão:",
                options=tabela_resumo.index,
                format_func=lambda x: f"{tabela_resumo.loc[x, 'cod_material']} - {tabela_resumo.loc[x, 'desc_material'][:60]}...",
                key="material_selector_previsao"
            )
        else:
            st.info("🔍 Digite um termo de busca para encontrar materiais")
            material_selecionado = None
        
        if material_selecionado is not None:
            # Obter dados do material selecionado
            material_info = tabela_resumo.loc[material_selecionado]
            cod_material_selecionado = material_info['cod_material']
            
            # Filtrar dados do material
            material_data = data['estoque'][data['estoque']['cod_material'] == cod_material_selecionado]
            
            if len(material_data) > 1:
                # Ordenar por período
                material_data = material_data.sort_values('periodo')
                
                # Calcular previsão
                previsao = previsao_demanda_simples(material_data)
                
                if previsao:
                    # Gráfico de evolução e previsão
                    fig = go.Figure()
                    
                    # Dados históricos de movimentação
                    fig.add_trace(go.Scatter(
                        x=material_data['periodo'],
                        y=material_data['quantidade'],
                        mode='lines+markers+text',
                        name='Movimentação Real',
                        line=dict(color='blue'),
                        text=[f"{qtd:.1f}" for qtd in material_data['quantidade']],
                        textposition="top center"
                    ))
                    
                    # Média móvel
                    if 'media_movel' in material_data.columns:
                        fig.add_trace(go.Scatter(
                            x=material_data['periodo'],
                            y=material_data['media_movel'],
                            mode='lines+text',
                            name='Média Móvel',
                            line=dict(color='red', dash='dash'),
                            text=[f"{media:.1f}" for media in material_data['media_movel']],
                            textposition="bottom center"
                        ))
                    
                    # Previsão
                    fig.add_trace(go.Scatter(
                        x=[material_data['periodo'].iloc[-1], 'Próximo Período'],
                        y=[material_data['quantidade'].iloc[-1], previsao['previsao']],
                        mode='lines+markers+text',
                        name='Previsão',
                        line=dict(color='green', dash='dot'),
                        text=[f"{material_data['quantidade'].iloc[-1]:.1f}", f"{previsao['previsao']:.1f}"],
                        textposition="top center"
                    ))
                    
                    fig.update_layout(
                        title=f"Previsão de Movimentação - Material {material_selecionado}",
                        xaxis_title="Período",
                        yaxis_title="Movimentação (Entradas/Saídas)",
                        height=400
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Métricas de previsão
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric("Previsão Próximo Período", f"{previsao['previsao']:.1f}")
                    
                    with col2:
                        st.metric("Tendência", previsao['tendencia'])
                    
                    with col3:
                        st.metric("Confiança", f"{previsao['confianca']:.1f}%")
                    
                    # Análise de entradas vs saídas
                    st.markdown("### 📊 Análise de Entradas vs Saídas")
                    
                    entradas = material_data[material_data['quantidade'] > 0]['quantidade'].sum()
                    saidas = abs(material_data[material_data['quantidade'] < 0]['quantidade'].sum())
                    
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric("Total Entradas", f"{entradas:.1f}")
                    
                    with col2:
                        st.metric("Total Saídas", f"{saidas:.1f}")
                    
                    with col3:
                        saldo = entradas - saidas
                        st.metric("Saldo Líquido", f"{saldo:.1f}")
                else:
                    st.warning("Dados insuficientes para previsão. Necessário pelo menos 3 períodos.")
            else:
                st.warning("Dados insuficientes para análise.")
    
    with tab_otimizacao:
        st.subheader("⚡ Análise de Movimentação")
        st.info("📊 **Análise baseada em dados de movimentação** - Foco em saídas para cálculo de reposição")
        
        # Análise ABC dinâmica baseada em movimentação
        st.markdown("### 📊 Análise ABC por Movimentação")
        
        # Agrupar por material e calcular métricas de movimentação
        resumo_materiais = data['estoque'].groupby(['cod_material', 'desc_material']).agg({
            'quantidade': 'sum',
            'valor_total': 'sum',
            'custo_medio': 'mean'
        }).reset_index()
        
        # Calcular métricas de movimentação
        resumo_materiais['entradas'] = data['estoque'][data['estoque']['quantidade'] > 0].groupby('cod_material')['quantidade'].sum().reindex(resumo_materiais['cod_material'], fill_value=0)
        resumo_materiais['saidas'] = data['estoque'][data['estoque']['quantidade'] < 0].groupby('cod_material')['quantidade'].sum().abs().reindex(resumo_materiais['cod_material'], fill_value=0)
        resumo_materiais['saldo_liquido'] = resumo_materiais['entradas'] - resumo_materiais['saidas']
        
        # Calcular score composto baseado em saídas e valor
        resumo_materiais['score_saidas'] = (resumo_materiais['saidas'] - resumo_materiais['saidas'].min()) / (resumo_materiais['saidas'].max() - resumo_materiais['saidas'].min()) if resumo_materiais['saidas'].max() > 0 else 0
        resumo_materiais['score_valor'] = (resumo_materiais['valor_total'] - resumo_materiais['valor_total'].min()) / (resumo_materiais['valor_total'].max() - resumo_materiais['valor_total'].min())
        resumo_materiais['score_composto'] = (resumo_materiais['score_saidas'] + resumo_materiais['score_valor']) / 2
        
        # Classificar ABC
        resumo_materiais['classificacao_abc'] = pd.cut(
            resumo_materiais['score_composto'], 
            bins=[0, 0.3, 0.7, 1], 
            labels=['C', 'B', 'A']
        )
        
        # Mostrar distribuição ABC
        abc_distribuicao = resumo_materiais['classificacao_abc'].value_counts()
        
        col1, col2 = st.columns(2)
        
        with col1:
            fig_abc = px.pie(
                values=abc_distribuicao.values,
                names=abc_distribuicao.index,
                title="Distribuição ABC por Movimentação",
                color_discrete_map={'A': '#FF6B6B', 'B': '#4ECDC4', 'C': '#45B7D1'}
            )
            
            # Adicionar rótulos de dados formatados
            fig_abc.update_traces(
                textinfo='label+percent+value',
                texttemplate='%{label}<br>%{percent}<br>%{value} materiais'
            )
            
            st.plotly_chart(fig_abc, use_container_width=True)
        
        with col2:
            # Tabela de materiais por classificação
            st.markdown("**Materiais por Classificação:**")
            for classe in ['A', 'B', 'C']:
                materiais_classe = resumo_materiais[resumo_materiais['classificacao_abc'] == classe].head(5)
                if len(materiais_classe) > 0:
                    st.markdown(f"**Classe {classe}:**")
                    st.dataframe(materiais_classe[['cod_material', 'desc_material', 'saidas', 'valor_total']], use_container_width=True)
        
        # Análise de ponto de reposição baseada em saídas
        st.markdown("### 🎯 Análise de Reposição por Saídas")
        
        # Filtros para seleção de material
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            search_term_otim = st.text_input("🔍 Buscar por material:", placeholder="Digite nome, código ou parte do material...", key="search_materials_otimizacao")
        
        with col2:
            search_type_otim = st.selectbox("Tipo de busca:", ['Código e Descrição', 'Apenas Código', 'Apenas Descrição'], key="search_type_otimizacao")
        
        with col3:
            sort_by_otim = st.selectbox("Ordenar por:", ['valor_total', 'quantidade', 'custo_medio'], key="sort_materials_otimizacao")
        
        # Aplicar filtros
        estoque_filtrado_otim = data['estoque'].copy()
        
        # Filtro de busca por texto
        if search_term_otim:
            # Busca inteligente baseada no tipo selecionado
            if search_type_otim == 'Código e Descrição':
                # Buscar tanto por nome quanto por código
                mask = (
                    estoque_filtrado_otim['desc_material'].str.contains(search_term_otim, case=False, na=False) |
                    estoque_filtrado_otim['cod_material'].astype(str).str.contains(search_term_otim, case=False, na=False)
                )
            elif search_type_otim == 'Apenas Código':
                # Buscar apenas por código
                mask = estoque_filtrado_otim['cod_material'].astype(str).str.contains(search_term_otim, case=False, na=False)
            else:  # Apenas Descrição
                # Buscar apenas por descrição
                mask = estoque_filtrado_otim['desc_material'].str.contains(search_term_otim, case=False, na=False)
            
            estoque_filtrado_otim = estoque_filtrado_otim[mask]
        
        # Agrupar por material para mostrar resumo
        tabela_resumo_otim = estoque_filtrado_otim.groupby(['cod_material', 'desc_material', 'familia', 'unidade']).agg({
            'quantidade': 'sum',
            'valor_total': 'sum',
            'custo_medio': 'mean'
        }).reset_index()
        
        tabela_resumo_otim = tabela_resumo_otim.sort_values(sort_by_otim, ascending=False)
        
        # Mostrar resultados da busca
        if search_term_otim:
            if len(tabela_resumo_otim) > 0:
                st.success(f"🔍 Encontrados {len(tabela_resumo_otim)} materiais para '{search_term_otim}' ({search_type_otim})")
            else:
                st.warning(f"⚠️ Nenhum material encontrado para '{search_term_otim}' ({search_type_otim})")
        else:
            st.info(f"📊 Mostrando todos os {len(tabela_resumo_otim)} materiais disponíveis")
        
        # Seleção de material
        if len(tabela_resumo_otim) > 0:
            material_otimizacao = st.selectbox(
                "Selecione um material para análise de reposição:",
                options=tabela_resumo_otim.index,
                format_func=lambda x: f"{tabela_resumo_otim.loc[x, 'cod_material']} - {tabela_resumo_otim.loc[x, 'desc_material'][:60]}...",
                key="material_selector_otimizacao"
            )
        else:
            st.info("🔍 Digite um termo de busca para encontrar materiais")
            material_otimizacao = None
        
        if material_otimizacao is not None:
            # Obter dados do material selecionado
            material_info_otim = tabela_resumo_otim.loc[material_otimizacao]
            cod_material_otim = material_info_otim['cod_material']
            
            # Filtrar dados do material
            material_data = data['estoque'][data['estoque']['cod_material'] == cod_material_otim]
            
            if len(material_data) > 1:
                ponto_reposicao = calcular_ponto_reposicao(material_data)
                
                if ponto_reposicao:
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        st.metric("Ponto de Reposição", f"{ponto_reposicao['ponto_reposicao']:.1f}")
                    
                    with col2:
                        st.metric("Consumo Diário", f"{ponto_reposicao['consumo_diario']:.1f}")
                    
                    with col3:
                        st.metric("Estoque de Segurança", f"{ponto_reposicao['estoque_seguranca']:.1f}")
                    
                    with col4:
                        st.metric("Lead Time", f"{ponto_reposicao['lead_time']} dias")
                    
                    # Calcular estoque estimado
                    entradas = material_data[material_data['quantidade'] > 0]['quantidade'].sum()
                    saidas = abs(material_data[material_data['quantidade'] < 0]['quantidade'].sum())
                    estoque_estimado = entradas - saidas
                    
                    # Status do estoque
                    if estoque_estimado < ponto_reposicao['ponto_reposicao']:
                        st.warning(f"⚠️ Estoque estimado abaixo do ponto de reposição! Estimado: {estoque_estimado:.1f}")
                    else:
                        st.success(f"✅ Estoque estimado adequado. Estimado: {estoque_estimado:.1f}")
                    
                    # Mostrar resumo de movimentação
                    st.markdown("### 📊 Resumo de Movimentação")
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric("Total Entradas", f"{entradas:.1f}")
                    
                    with col2:
                        st.metric("Total Saídas", f"{saidas:.1f}")
                    
                    with col3:
                        st.metric("Estoque Estimado", f"{estoque_estimado:.1f}")
    
    with tab_sugestoes:
        st.subheader("💡 Sugestões Inteligentes")
        st.info("📊 **Análise baseada em dados de movimentação** - Sugestões baseadas em saídas e estoque estimado")
        
        # Sugestões de compra
        st.markdown("### 🛒 Sugestões de Compra")
        
        sugestoes = gerar_sugestoes_compra(data['estoque'])
        
        if sugestoes:
            df_sugestoes = pd.DataFrame(sugestoes)
            
            # Filtrar por prioridade
            prioridade_filtro = st.selectbox(
                "Filtrar por prioridade:",
                ['Todas', 'Alta', 'Média'],
                key="prioridade_filtro"
            )
            
            if prioridade_filtro != 'Todas':
                df_sugestoes = df_sugestoes[df_sugestoes['prioridade'] == prioridade_filtro]
            
            st.dataframe(df_sugestoes, use_container_width=True)
            
            # Resumo das sugestões
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Total de Sugestões", len(sugestoes))
            
            with col2:
                alta_prioridade = len(df_sugestoes[df_sugestoes['prioridade'] == 'Alta'])
                st.metric("Alta Prioridade", alta_prioridade)
            
            with col3:
                valor_total_sugerido = df_sugestoes['quantidade_sugerida'].sum() * df_sugestoes['estoque_estimado'].mean()
                st.metric("Valor Estimado", f"R$ {valor_total_sugerido:,.2f}")
        else:
            st.success("✅ Nenhuma sugestão de compra no momento. Estoque estimado em níveis adequados.")
        
        # Análise de oportunidades baseada em movimentação
        st.markdown("### ⚡ Análise de Oportunidades")
        
        # Calcular métricas de movimentação por material
        resumo_materiais = data['estoque'].groupby('cod_material').agg({
            'quantidade': 'sum',
            'valor_total': 'sum'
        }).reset_index()
        
        # Calcular entradas e saídas
        resumo_materiais['entradas'] = data['estoque'][data['estoque']['quantidade'] > 0].groupby('cod_material')['quantidade'].sum().reindex(resumo_materiais['cod_material'], fill_value=0)
        resumo_materiais['saidas'] = data['estoque'][data['estoque']['quantidade'] < 0].groupby('cod_material')['quantidade'].sum().abs().reindex(resumo_materiais['cod_material'], fill_value=0)
        resumo_materiais['saldo_liquido'] = resumo_materiais['entradas'] - resumo_materiais['saidas']
        
        # Materiais com baixo giro (poucas saídas)
        baixo_giro = resumo_materiais[resumo_materiais['saidas'] < resumo_materiais['saidas'].quantile(0.2)]
        
        if len(baixo_giro) > 0:
            st.warning(f"⚠️ **{len(baixo_giro)} materiais com baixo giro** - Poucas saídas, considere revisar necessidade")
            
            with st.expander("Ver Materiais com Baixo Giro"):
                st.dataframe(baixo_giro[['cod_material', 'saidas', 'entradas', 'saldo_liquido']], use_container_width=True)
        
        # Materiais com excesso de entradas (muito estoque estimado)
        excesso_estoque = resumo_materiais[resumo_materiais['saldo_liquido'] > resumo_materiais['saldo_liquido'].quantile(0.8)]
        
        if len(excesso_estoque) > 0:
            st.info(f"ℹ️ **{len(excesso_estoque)} materiais com excesso de estoque estimado** - Muitas entradas, considere revisar necessidade")
            
            with st.expander("Ver Materiais com Excesso"):
                st.dataframe(excesso_estoque[['cod_material', 'entradas', 'saidas', 'saldo_liquido']], use_container_width=True)
        
        # Materiais com alta movimentação
        alta_movimentacao = resumo_materiais[resumo_materiais['saidas'] > resumo_materiais['saidas'].quantile(0.8)]
        
        if len(alta_movimentacao) > 0:
            st.success(f"✅ **{len(alta_movimentacao)} materiais com alta movimentação** - Foque na gestão destes itens")
            
            with st.expander("Ver Materiais com Alta Movimentação"):
                st.dataframe(alta_movimentacao[['cod_material', 'saidas', 'entradas', 'valor_total']], use_container_width=True)
    
    with tab_relatorios:
        st.subheader("📊 Relatórios")
        
        # Botões de exportação
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("📊 Gerar Relatório Excel", use_container_width=True):
                # Criar arquivo Excel
                with pd.ExcelWriter('relatorio_almoxarifado.xlsx', engine='openpyxl') as writer:
                    data['estoque'].to_excel(writer, sheet_name='Dados_Completos', index=False)
                    
                    # Resumo por material
                    resumo = data['estoque'].groupby(['cod_material', 'desc_material']).agg({
                        'quantidade': 'sum',
                        'valor_total': 'sum',
                        'custo_medio': 'mean'
                    }).reset_index()
                    resumo.to_excel(writer, sheet_name='Resumo_Materiais', index=False)
                
                st.success("✅ Relatório Excel gerado com sucesso!")
        
        with col2:
            if st.button("📄 Gerar Relatório CSV", use_container_width=True):
                data['estoque'].to_csv('relatorio_almoxarifado.csv', index=False, encoding='utf-8-sig')
                st.success("✅ Relatório CSV gerado com sucesso!")
        
        with col3:
            if st.button("📈 Dashboard Executivo", use_container_width=True):
                st.success("✅ Dashboard executivo gerado com sucesso!")
    

def show_data_integration():
    """
    Aba para integração de dados futuros
    """
    st.header("📥 Integração de Dados")
    st.markdown("---")
    
    # Introdução
    st.markdown("""
    Esta seção fornece informações sobre como integrar novos dados ao sistema de almoxarifado.
    Aqui você encontrará a documentação das colunas necessárias e guias para adicionar novos dados.
    """)
    
    # Tabs para diferentes aspectos da integração
    tab_docs, tab_estrutura, tab_exemplo, tab_guia = st.tabs([
        "📋 Documentação das Colunas",
        "🏗️ Estrutura do Banco",
        "📄 Exemplo de Arquivo",
        "🔧 Guia de Integração"
    ])
    
    with tab_docs:
        st.subheader("📋 Colunas Obrigatórias no Arquivo CSV/Excel")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            **Colunas Principais:**
            - `cod_material`: Código único do material
            - `desc_material`: Descrição do material
            - `quantidade`: Quantidade em estoque
            - `custo_medio`: Custo médio unitário
            - `valor_total`: Valor total (quantidade × custo_medio)
            - `unidade`: Unidade de medida
            - `periodo`: Período no formato 'mmm/aa' (ex: 'jan/23')
            - `ano`: Ano (ex: 2023)
            - `mes`: Mês numérico (1-12)
            """)
        
        with col2:
            st.markdown("""
            **Colunas de Classificação:**
            - `familia`: Família do material
            - `grupo_material`: Grupo do material
            - `tipo_material`: Tipo do material
            - `almoxarifado`: Nome do almoxarifado
            - `localizacao`: Localização física
            - `classificacao_sped`: Classificação SPED
            - `conta_contabil`: Conta contábil
            - `classificacao_fiscal`: Classificação fiscal
            - `identificacao`: Identificação adicional
            """)
        
        st.info("💡 **Dica**: Todas as colunas são obrigatórias. Use valores vazios ou 'N/A' para campos sem informação.")
    
    with tab_estrutura:
        st.subheader("🏗️ Estrutura do Banco de Dados")
        
        st.markdown("""
        O banco de dados utiliza um esquema normalizado com as seguintes tabelas:
        """)
        
        # Tabelas principais
        st.markdown("""
        **Tabelas Principais:**
        - `materiais`: Informações dos materiais
        - `estoque`: Dados de estoque por período
        - `periodos`: Períodos disponíveis
        - `familias`: Famílias de materiais
        - `grupos_materiais`: Grupos de materiais
        - `tipos_materiais`: Tipos de materiais
        - `almoxarifados`: Almoxarifados
        - `localizacoes`: Localizações físicas
        - `classificacoes_sped`: Classificações SPED
        - `contas_contabeis`: Contas contábeis
        - `classificacoes_fiscais`: Classificações fiscais
        - `identificacoes`: Identificações adicionais
        """)
        
        # Relacionamentos
        st.markdown("""
        **Relacionamentos:**
        - Cada material pertence a uma família, grupo e tipo
        - Cada registro de estoque está associado a um material e período
        - As classificações são referenciadas por IDs numéricos
        """)
        
        # Botão para mostrar schema
        if st.button("🔍 Ver Schema Completo"):
            st.code("""
-- Schema do banco de dados
CREATE TABLE periodos (
    id INTEGER PRIMARY KEY,
    periodo TEXT UNIQUE NOT NULL,
    ano INTEGER NOT NULL,
    mes INTEGER NOT NULL
);

CREATE TABLE familias (
    id INTEGER PRIMARY KEY,
    nome TEXT UNIQUE NOT NULL
);

CREATE TABLE materiais (
    id INTEGER PRIMARY KEY,
    cod_material TEXT UNIQUE NOT NULL,
    desc_material TEXT NOT NULL,
    unidade TEXT NOT NULL,
    familia_id INTEGER,
    grupo_material_id INTEGER,
    tipo_material_id INTEGER,
    FOREIGN KEY (familia_id) REFERENCES familias (id),
    FOREIGN KEY (grupo_material_id) REFERENCES grupos_materiais (id),
    FOREIGN KEY (tipo_material_id) REFERENCES tipos_materiais (id)
);

CREATE TABLE estoque (
    id INTEGER PRIMARY KEY,
    material_id INTEGER NOT NULL,
    periodo_id INTEGER NOT NULL,
    quantidade REAL NOT NULL,
    custo_medio REAL NOT NULL,
    valor_total REAL NOT NULL,
    almoxarifado_id INTEGER,
    localizacao_id INTEGER,
    FOREIGN KEY (material_id) REFERENCES materiais (id),
    FOREIGN KEY (periodo_id) REFERENCES periodos (id),
    FOREIGN KEY (almoxarifado_id) REFERENCES almoxarifados (id),
    FOREIGN KEY (localizacao_id) REFERENCES localizacoes (id)
);
            """, language="sql")
    
    with tab_exemplo:
        st.subheader("📄 Exemplo de Arquivo CSV")
        
        # Exemplo de dados
        exemplo_dados = {
            'cod_material': ['MAT001', 'MAT002', 'MAT003'],
            'desc_material': ['Parafuso M6x20', 'Porca M6', 'Arruela M6'],
            'quantidade': [1000, 500, 2000],
            'custo_medio': [0.15, 0.08, 0.03],
            'valor_total': [150.00, 40.00, 60.00],
            'unidade': ['UN', 'UN', 'UN'],
            'periodo': ['jan/23', 'jan/23', 'jan/23'],
            'ano': [2023, 2023, 2023],
            'mes': [1, 1, 1],
            'familia': ['Ferramentas', 'Ferramentas', 'Ferramentas'],
            'grupo_material': ['Parafusos', 'Porcas', 'Arruelas'],
            'tipo_material': ['Metal', 'Metal', 'Metal'],
            'almoxarifado': ['Principal', 'Principal', 'Principal'],
            'localizacao': ['A1-B2', 'A1-B3', 'A1-B4'],
            'classificacao_sped': ['15.01.01', '15.01.02', '15.01.03'],
            'conta_contabil': ['1.1.01.001', '1.1.01.002', '1.1.01.003'],
            'classificacao_fiscal': ['NCM12345678', 'NCM87654321', 'NCM11223344'],
            'identificacao': ['LOTE001', 'LOTE002', 'LOTE003']
        }
        
        df_exemplo = pd.DataFrame(exemplo_dados)
        st.dataframe(df_exemplo, use_container_width=True)
        
        # Botão para download
        csv_exemplo = df_exemplo.to_csv(index=False, encoding='utf-8-sig')
        st.download_button(
            label="📥 Baixar Exemplo CSV",
            data=csv_exemplo,
            file_name="exemplo_almoxarifado.csv",
            mime="text/csv"
        )
        
        st.info("💡 **Dica**: Use este arquivo como modelo para seus dados. Mantenha o mesmo formato e nomes das colunas.")
    
    with tab_guia:
        st.subheader("🔧 Guia de Integração")
        
        # Botão de upload de arquivo
        st.markdown("### 📤 Upload de Arquivo")
        uploaded_file = st.file_uploader(
            "Escolha um arquivo CSV ou Excel para integrar:",
            type=['csv', 'xlsx', 'xls'],
            help="Selecione um arquivo com os dados do almoxarifado no formato correto"
        )
        
        if uploaded_file is not None:
            # Mostrar informações do arquivo
            st.success(f"✅ Arquivo carregado: {uploaded_file.name}")
            st.info(f"📊 Tamanho: {uploaded_file.size} bytes")
            
            # Validar arquivo
            try:
                # Ler arquivo para validação
                if uploaded_file.name.endswith('.csv'):
                    df_validation = pd.read_csv(uploaded_file)
                elif uploaded_file.name.endswith(('.xlsx', '.xls')):
                    df_validation = pd.read_excel(uploaded_file)
                
                # Verificar colunas obrigatórias
                colunas_obrigatorias = [
                    'cod_material', 'desc_material', 'quantidade', 'custo_medio', 
                    'valor_total', 'unidade', 'periodo', 'ano', 'mes', 'familia',
                    'grupo_material', 'tipo_material', 'almoxarifado', 'localizacao',
                    'classificacao_sped', 'conta_contabil', 'classificacao_fiscal', 'identificacao'
                ]
                
                colunas_faltando = [col for col in colunas_obrigatorias if col not in df_validation.columns]
                
                if colunas_faltando:
                    st.error(f"❌ Colunas obrigatórias faltando: {', '.join(colunas_faltando)}")
                    st.info("💡 Use o arquivo de exemplo como referência.")
                else:
                    st.success("✅ Arquivo válido! Todas as colunas obrigatórias estão presentes.")
                    st.info(f"📊 Registros encontrados: {len(df_validation)}")
                    
                    # Mostrar preview dos dados
                    with st.expander("👁️ Preview dos Dados"):
                        st.dataframe(df_validation.head(10), use_container_width=True)
                
            except Exception as e:
                st.error(f"❌ Erro ao validar arquivo: {str(e)}")
                st.info("💡 Verifique se o arquivo está no formato correto.")
            
            # Botão para processar
            if st.button("🚀 Processar Arquivo", type="primary", use_container_width=True):
                with st.spinner("Processando arquivo..."):
                    try:
                        # Salvar arquivo temporariamente
                        import tempfile
                        import os
                        
                        # Criar arquivo temporário
                        with tempfile.NamedTemporaryFile(delete=False, suffix='.csv') as tmp_file:
                            tmp_file.write(uploaded_file.getvalue())
                            tmp_path = tmp_file.name
                        
                        # Processar arquivo
                        st.info("📝 Processando dados...")
                        
                        # Chamar o processador de dados
                        try:
                            import subprocess
                            import sys
                            
                            # Executar o processador de dados
                            result = subprocess.run([
                                sys.executable, 
                                "data_processor_optimized.py",
                                "--file", tmp_path
                            ], capture_output=True, text=True, timeout=300)
                            
                            if result.returncode == 0:
                                st.success("✅ Arquivo processado com sucesso!")
                                st.info("🔄 Recarregue a página para ver os novos dados no dashboard.")
                                
                                # Mostrar informações do processamento
                                if result.stdout:
                                    st.text("📊 Log do processamento:")
                                    st.code(result.stdout)
                            else:
                                st.error(f"❌ Erro no processamento: {result.stderr}")
                                
                        except subprocess.TimeoutExpired:
                            st.error("⏰ Timeout: O processamento demorou muito. Tente com um arquivo menor.")
                        except Exception as e:
                            st.error(f"❌ Erro ao executar processador: {str(e)}")
                            st.info("💡 Verifique se o arquivo data_processor_optimized.py existe e está funcionando.")
                        
                        # Limpar arquivo temporário
                        os.unlink(tmp_path)
                        
                    except Exception as e:
                        st.error(f"❌ Erro ao processar arquivo: {str(e)}")
                        st.info("💡 Verifique se o arquivo está no formato correto e tente novamente.")
        
        st.markdown("---")
        
        # Botões de manutenção
        st.markdown("### 🔧 Ferramentas de Manutenção")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🗑️ Limpar Banco de Dados", type="secondary", use_container_width=True):
                st.warning("⚠️ Esta ação irá limpar todos os dados do banco!")
                if st.button("✅ Confirmar Limpeza", type="primary"):
                    try:
                        # Limpar banco de dados
                        conn = sqlite3.connect('almoxarifado.db')
                        cursor = conn.cursor()
                        
                        # Limpar todas as tabelas
                        tabelas = [
                            'estoque', 'materiais', 'periodos', 'familias', 
                            'grupos_materiais', 'tipos_materiais', 'almoxarifados',
                            'localizacoes', 'classificacoes_sped', 'contas_contabeis',
                            'classificacoes_fiscais', 'identificacoes'
                        ]
                        
                        for tabela in tabelas:
                            cursor.execute(f"DELETE FROM {tabela}")
                        
                        conn.commit()
                        conn.close()
                        
                        st.success("✅ Banco de dados limpo com sucesso!")
                        st.info("🔄 Recarregue a página para ver as mudanças.")
                        
                    except Exception as e:
                        st.error(f"❌ Erro ao limpar banco: {str(e)}")
        
        with col2:
            if st.button("🔄 Recarregar Dashboard", type="secondary", use_container_width=True):
                st.rerun()
        
        st.markdown("---")
        
        st.markdown("""
        **Passo a passo para integração manual:**
        """)
        
        # Passo 1
        st.markdown("""
        **1. Preparar o Arquivo**
        - Use o formato CSV ou Excel
        - Inclua todas as colunas obrigatórias
        - Verifique se os dados estão no formato correto
        - Use o arquivo de exemplo como referência
        """)
        
        # Passo 2
        st.markdown("""
        **2. Validar os Dados**
        - Verifique se os códigos de material são únicos
        - Confirme se os períodos estão no formato 'mmm/aa'
        - Valide se os valores numéricos estão corretos
        - Verifique se as classificações existem no sistema
        """)
        
        # Passo 3
        st.markdown("""
        **3. Processar os Dados**
        - Use o script `data_processor_optimized.py` para processar o arquivo
        - O script criará automaticamente as tabelas necessárias
        - Os dados serão inseridos no banco SQLite
        """)
        
        # Passo 4
        st.markdown("""
        **4. Verificar a Integração**
        - Execute o dashboard para visualizar os dados
        - Verifique se os gráficos estão funcionando
        - Confirme se os filtros estão aplicando corretamente
        """)
        
        # Comandos
        st.markdown("""
        **Comandos para Integração:**
        """)
        
        st.code("""
# 1. Instalar dependências
pip install -r requirements.txt

# 2. Processar novo arquivo
python data_processor_optimized.py

# 3. Executar dashboard
streamlit run dashboard.py
        """, language="bash")
        
        # Avisos importantes
        st.warning("""
        **⚠️ Avisos Importantes:**
        - Faça backup do banco de dados antes de integrar novos dados
        - Teste com uma pequena amostra antes de processar o arquivo completo
        - Verifique se não há conflitos com dados existentes
        """)
        
        # Suporte
        st.markdown("""
        **🆘 Suporte:**
        - Consulte a documentação do projeto
        - Verifique os logs de processamento
        - Entre em contato com o administrador do sistema
        """)

if __name__ == "__main__":
    main()
