# 📦 Dashboard do Almoxarifado - Guia de Funcionalidades

## 🎯 **Visão Geral do Sistema**

O **Dashboard do Almoxarifado** é uma solução completa de análise e gestão de dados de movimentação de materiais, desenvolvida com tecnologias modernas (Streamlit + Plotly) para fornecer insights valiosos e facilitar a tomada de decisões estratégicas.

### **📊 Características Principais:**
- **Interface Responsiva**: Funciona perfeitamente em desktop, tablet e mobile
- **Análises Avançadas**: Estatísticas robustas e visualizações interativas
- **Formatação Brasileira**: Valores monetários e numéricos no padrão nacional
- **Tempo Real**: Atualizações dinâmicas e filtros em tempo real
- **Integração de Dados**: Upload e processamento automático de novos dados

---

## 🏠 **1. Dashboard Geral**

### **📈 Resumo de Saídas**
**Objetivo**: Visão consolidada das movimentações de saída do estoque

**Métricas Principais:**
- **Total de Materiais**: Quantidade total de materiais únicos
- **Valor Total Saídas**: Soma de todos os valores de saída (R$)
- **Quantidade Total Saídas**: Volume total de materiais movimentados
- **Materiais com Saídas**: Quantidade de materiais ativos

### **📊 KPIs de Saídas**
**Objetivo**: Indicadores de performance para análise de eficiência

**Indicadores:**
- **Saída Média por Material**: Média de saídas por material
- **Saída Média por Período**: Média de saídas por período
- **Valor Médio por Saída**: Valor médio de cada saída (R$)
- **Períodos Ativos**: Quantidade de períodos com movimentação

### **🚨 Alertas Inteligentes**
**Objetivo**: Identificação automática de situações que requerem atenção

**Tipos de Alertas:**
- **Baixa Saída**: Materiais com pouca movimentação
- **Alta Saída**: Materiais com movimentação excessiva
- **Materiais Inativos**: Materiais sem movimentação recente

### **📈 Análises Visuais**

#### **Evolução das Saídas por Período**
- **Tipo**: Gráfico de linha temporal
- **Dados**: Valor total das saídas ao longo do tempo
- **Ordenação**: Cronológica (jan/23 → dez/25)
- **Rótulos**: Valores formatados em padrão brasileiro

#### **Distribuição das Saídas por Almoxarifado**
- **Tipo**: Gráfico de pizza
- **Dados**: Percentual de valor por almoxarifado
- **Rótulos**: Percentual e valor em R$
- **Interatividade**: Hover com detalhes

#### **Top 10 Materiais por Valor de Saídas**
- **Tipo**: Gráfico de barras horizontais
- **Dados**: Materiais com maior valor de saída
- **Rótulos**: Valores em R$ formatados
- **Cores**: Gradiente baseado no valor

#### **Top 10 Materiais por Quantidade de Saídas**
- **Tipo**: Gráfico de barras horizontais
- **Dados**: Materiais com maior volume de saída
- **Rótulos**: Quantidades formatadas
- **Cores**: Gradiente baseado na quantidade

---

## 🔍 **2. Análise Detalhada de Materiais**

### **🎯 Busca Inteligente de Materiais**
**Funcionalidades:**
- **Busca por Texto**: Nome, código ou parte do material
- **Tipos de Busca**: Código e Descrição, Apenas Código, Apenas Descrição
- **Ordenação**: Por valor total, quantidade ou custo médio
- **Filtros Avançados**: Família, almoxarifado, valor mínimo

### **📊 Análise Completa do Material Selecionado**

#### **Resumo do Material**
- **Informações Básicas**: Código, descrição, família, unidade
- **Métricas de Movimentação**: Total de saídas, valor total, custo médio
- **Período de Atividade**: Primeira e última movimentação

#### **Evolução de Preços**
- **Tipo**: Gráfico de linha temporal
- **Dados**: Custo médio por período
- **Ordenação**: Cronológica correta
- **Rótulos**: Valores em R$ formatados

#### **Movimentação por Período**
- **Tipo**: Gráfico de barras
- **Dados**: Quantidade de saídas por período
- **Ordenação**: Cronológica
- **Rótulos**: Quantidades formatadas

#### **Análise de Tendências**
- **Tipo**: Gráfico de linha com tendência
- **Dados**: Evolução temporal com linha de tendência
- **Análise**: Crescimento, declínio ou estabilidade
- **Rótulos**: Valores e tendência

#### **Informações Técnicas**
- **Dados Detalhados**: Tabela com todas as movimentações
- **Filtros**: Por período, valor, quantidade
- **Exportação**: Dados para análise externa

---

## 📊 **3. Análises Avançadas**

### **📈 Análises Estatísticas**

#### **Métricas Estatísticas**
- **Coeficiente de Variação**: Medida de dispersão dos dados
- **Índice de Sazonalidade**: Identificação de padrões sazonais
- **Índice de Concentração**: Distribuição de valor entre materiais
- **Variação das Saídas**: Estabilidade das movimentações

#### **Análise de Percentis**
- **P25, P50, P75, P90, P95**: Distribuição estatística dos valores
- **Visualização**: Gráfico de barras com percentis
- **Aplicação**: Identificação de outliers e concentrações

#### **Distribuição por Percentis**
- **Tipo**: Gráfico de barras
- **Dados**: 7 percentis (P10 a P99)
- **Rótulos**: Valores em R$ formatados
- **Cores**: Gradiente baseado no valor

#### **Variabilidade por Material**
- **Tipo**: Gráfico de barras horizontais
- **Dados**: Top 10 materiais com maior variabilidade (CV%)
- **Filtro**: Apenas materiais com ≥ 3 registros
- **Rótulos**: Coeficiente de variação em %

#### **Estabilidade Temporal**
- **Tipo**: Gráfico de linha temporal
- **Dados**: Coeficiente de variação por período
- **Ordenação**: Cronológica
- **Rótulos**: Valores de CV% formatados

#### **Concentração por Família**
- **Tipo**: Gráfico de barras horizontais
- **Dados**: Top 10 famílias por percentual de valor
- **Rótulos**: Percentuais formatados
- **Cores**: Gradiente baseado no percentual

#### **Análise de Diversificação**
- **Tipo**: Gráfico de barras verticais
- **Dados**: Número de materiais, famílias, almoxarifados
- **Rótulos**: Quantidades formatadas
- **Aplicação**: Avaliação da diversificação do portfólio

### **🔮 Previsão de Movimentação**

#### **Busca Inteligente de Materiais**
- **Interface**: Mesma busca avançada da análise de materiais
- **Filtros**: Por família, almoxarifado, valor mínimo
- **Ordenação**: Por valor, quantidade ou custo médio

#### **Análise de Previsão**
- **Gráfico Temporal**: Movimentação real + média móvel + previsão
- **Métodos**: Média móvel e tendência linear
- **Métricas**: Previsão, tendência, confiança
- **Rótulos**: Valores em cada ponto

#### **Análise de Entradas vs Saídas**
- **Total Entradas**: Quantidade total de entradas
- **Total Saídas**: Quantidade total de saídas
- **Saldo Líquido**: Diferença entre entradas e saídas

### **⚡ Otimização de Estoque**

#### **Análise ABC por Movimentação**
- **Classificação**: A, B, C baseada em score composto
- **Critérios**: Valor total e quantidade de saídas
- **Visualização**: Gráfico de pizza com distribuição
- **Tabelas**: Materiais por classificação

#### **Análise de Reposição por Saídas**
- **Busca**: Interface de busca inteligente
- **Cálculos**: Ponto de reposição baseado em saídas
- **Métricas**: Consumo médio mensal, estoque estimado
- **Aplicação**: Sugestões de reposição

### **💡 Sugestões Inteligentes**

#### **Sugestões de Compra**
- **Critérios**: Estoque estimado vs ponto de reposição
- **Priorização**: Baseada em classificação ABC
- **Métricas**: Quantidade sugerida, urgência
- **Aplicação**: Lista de compras inteligente

#### **Análise de Oportunidades**
- **Baixo Giro**: Materiais com pouca movimentação
- **Excesso de Estoque**: Materiais com estoque alto
- **Oportunidades**: Materiais com potencial de crescimento

### **📊 Relatórios**

#### **Exportação de Dados**
- **Formatos**: Excel (.xlsx) e CSV
- **Conteúdo**: Dados filtrados e processados
- **Aplicação**: Análise externa e relatórios gerenciais

#### **Relatórios Automáticos**
- **Resumo Executivo**: Principais métricas e insights
- **Análise de Tendências**: Evolução temporal dos dados
- **Recomendações**: Sugestões baseadas nos dados

---

## 🔧 **4. Integração de Dados**

### **📋 Documentação das Colunas**
**Colunas Obrigatórias (18):**
1. **cod_material**: Código único do material
2. **desc_material**: Descrição do material
3. **familia**: Família do material
4. **grupo_material**: Grupo do material
5. **tipo_material**: Tipo do material
6. **unidade**: Unidade de medida
7. **almoxarifado**: Almoxarifado de origem
8. **localizacao**: Localização física
9. **classificacao_sped**: Classificação SPED
10. **conta_contabil**: Conta contábil
11. **classificacao_fiscal**: Classificação fiscal
12. **identificacao**: Identificação única
13. **periodo**: Período da movimentação (mmm/aa)
14. **quantidade**: Quantidade movimentada
15. **custo_medio**: Custo médio unitário
16. **valor_total**: Valor total da movimentação
17. **data_movimentacao**: Data da movimentação
18. **observacoes**: Observações adicionais

### **🏗️ Estrutura do Banco de Dados**
- **Schema Normalizado**: 12 tabelas relacionadas
- **Relacionamentos**: Chaves estrangeiras bem definidas
- **Índices**: Otimização para consultas rápidas
- **Integridade**: Validação de dados e consistência

### **📄 Exemplo de Arquivo**
- **Formato**: CSV com separador vírgula
- **Encoding**: UTF-8
- **Download**: Arquivo de exemplo disponível
- **Validação**: Verificação automática de colunas

### **🔄 Guia de Integração**
1. **Preparação**: Verificar formato e colunas obrigatórias
2. **Upload**: Selecionar arquivo CSV ou Excel
3. **Validação**: Verificação automática de dados
4. **Processamento**: Inserção em lote no banco
5. **Confirmação**: Relatório de sucesso/erro

---

## 🎨 **5. Características Técnicas**

### **💻 Tecnologias Utilizadas**
- **Frontend**: Streamlit (Python)
- **Visualizações**: Plotly (gráficos interativos)
- **Banco de Dados**: SQLite (desenvolvimento) / PostgreSQL (produção)
- **Processamento**: Pandas (análise de dados)
- **Estatísticas**: NumPy, SciPy (cálculos avançados)

### **📱 Responsividade**
- **Layout Adaptável**: Funciona em desktop, tablet e mobile
- **Zoom Padrão**: Otimizado para 100% de zoom
- **Media Queries**: Ajustes específicos para telas pequenas
- **Interface Intuitiva**: Navegação fácil em qualquer dispositivo

### **🇧🇷 Formatação Brasileira**
- **Valores Monetários**: R$ 1.234.567,89
- **Quantidades**: 1.234.567
- **Percentuais**: 42,3%
- **Datas**: dd/mm/aaaa
- **Consistência**: Padrão nacional em todos os valores

### **⚡ Performance**
- **Carregamento Rápido**: Otimização de consultas
- **Processamento em Lote**: Inserção eficiente de dados
- **Cache Inteligente**: Dados carregados uma vez por sessão
- **Responsividade**: Interface fluida e responsiva

---

## 🚀 **6. Benefícios do Sistema**

### **📊 Para Gestores**
- **Visão Estratégica**: Dashboards executivos com KPIs relevantes
- **Tomada de Decisão**: Dados precisos e análises avançadas
- **Otimização**: Identificação de oportunidades de melhoria
- **Relatórios**: Exportação para análises externas

### **📈 Para Analistas**
- **Análises Avançadas**: Estatísticas robustas e visualizações
- **Flexibilidade**: Filtros dinâmicos e buscas inteligentes
- **Detalhamento**: Análise granular por material
- **Previsões**: Modelos de previsão e tendências

### **🔧 Para Operações**
- **Gestão de Estoque**: Análise de reposição e sugestões
- **Controle de Qualidade**: Identificação de materiais problemáticos
- **Eficiência**: Alertas automáticos e recomendações
- **Integração**: Upload fácil de novos dados

### **💼 Para a Organização**
- **Transparência**: Dados acessíveis e compreensíveis
- **Eficiência**: Redução de tempo em análises manuais
- **Precisão**: Eliminação de erros de cálculo
- **Escalabilidade**: Suporte a grandes volumes de dados

---

## 📞 **7. Suporte e Manutenção**

### **🛠️ Funcionalidades de Manutenção**
- **Limpeza de Banco**: Reset completo dos dados
- **Recarregamento**: Atualização da interface
- **Validação**: Verificação de integridade dos dados
- **Logs**: Acompanhamento de processamentos

### **📋 Documentação Técnica**
- **Código Fonte**: Comentários e documentação
- **Schema do Banco**: Estrutura completa documentada
- **APIs**: Endpoints para integração
- **Configurações**: Parâmetros personalizáveis

### **🔄 Atualizações**
- **Versões**: Controle de versão do sistema
- **Melhorias**: Implementação contínua de funcionalidades
- **Correções**: Resolução rápida de problemas
- **Feedback**: Incorporação de sugestões dos usuários

---

## 🎯 **8. Próximos Passos**

### **🔮 Funcionalidades Futuras**
- **Machine Learning**: Modelos preditivos mais avançados
- **Alertas por Email**: Notificações automáticas
- **API REST**: Integração com outros sistemas
- **Mobile App**: Aplicativo nativo para dispositivos móveis

### **📈 Melhorias Planejadas**
- **Performance**: Otimizações adicionais
- **Visualizações**: Novos tipos de gráficos
- **Relatórios**: Templates personalizáveis
- **Integração**: Conectores para mais fontes de dados

---

## 📝 **9. Conclusão**

O **Dashboard do Almoxarifado** representa uma solução completa e moderna para gestão e análise de dados de movimentação de materiais. Com interface responsiva, análises avançadas e formatação brasileira, o sistema oferece todas as ferramentas necessárias para uma gestão eficiente e baseada em dados.

### **✨ Principais Diferenciais:**
- **Interface Intuitiva**: Fácil de usar e navegar
- **Análises Robustas**: Estatísticas avançadas e visualizações
- **Responsividade**: Funciona em qualquer dispositivo
- **Formatação Nacional**: Padrão brasileiro em todos os valores
- **Integração Simples**: Upload fácil de novos dados
- **Performance**: Rápido e eficiente

### **🎯 Resultado Final:**
Um sistema profissional, completo e eficiente que transforma dados brutos em insights valiosos, facilitando a tomada de decisões estratégicas e operacionais no almoxarifado.

---

**Desenvolvido com ❤️ usando Streamlit e Plotly**

**Versão**: 1.0 | **Data**: Setembro 2025 | **Status**: Produção
