# 📦 Dashboard do Almoxarifado

Sistema completo de análise e visualização de dados de movimentação de materiais, desenvolvido em Python com Streamlit e Plotly.

## 🚀 Funcionalidades Principais

### 📊 **Dashboard Geral**
- **Resumo de Saídas**: Métricas principais de movimentação
- **KPIs Avançados**: Indicadores de performance
- **Alertas Inteligentes**: Identificação automática de situações críticas
- **Visualizações Interativas**: Gráficos responsivos com filtros dinâmicos

### 🔍 **Análise Detalhada de Materiais**
- **Busca Inteligente**: Por código, descrição ou parte do material
- **Análise Completa**: Evolução de preços, movimentação e tendências
- **Filtros Avançados**: Por família, almoxarifado, valor mínimo
- **Informações Técnicas**: Dados detalhados e exportação

### 📈 **Análises Avançadas**
- **Análises Estatísticas**: Correlações, percentis, variabilidade
- **Previsão de Movimentação**: Modelos preditivos e tendências
- **Otimização de Estoque**: Análise ABC e sugestões de reposição
- **Relatórios**: Exportação para Excel e CSV

### 🔧 **Integração de Dados**
- **Upload Automático**: Processamento de arquivos CSV/Excel
- **Validação de Dados**: Verificação de colunas obrigatórias
- **Schema Normalizado**: Banco de dados otimizado
- **Documentação Completa**: Guia de integração incluído

## 🛠️ Tecnologias Utilizadas

- **Frontend**: Streamlit (Python)
- **Visualizações**: Plotly (gráficos interativos)
- **Banco de Dados**: SQLite (desenvolvimento) / PostgreSQL (produção)
- **Processamento**: Pandas, NumPy, SciPy
- **Formatação**: Padrão brasileiro (R$ 1.234.567,89)

## 📱 Características Especiais

- **Interface Responsiva**: Funciona perfeitamente em desktop, tablet e mobile
- **Formatação Brasileira**: Valores monetários e numéricos no padrão nacional
- **Zoom Otimizado**: Funciona perfeitamente no zoom padrão de 100%
- **Performance**: Carregamento rápido e visualizações fluidas

## 🚀 Instalação e Uso

### 1. **Instalar Dependências**
```bash
pip install -r requirements.txt
```

### 2. **Executar Dashboard**
```bash
streamlit run dashboard.py
```

### 3. **Acessar Interface**
Abra o navegador em `http://localhost:8501`

## 📁 Estrutura do Projeto

```
Projeto_Almoxarifado/
├── dashboard.py                    # Aplicação principal Streamlit
├── data_processor_optimized.py    # Processador de dados otimizado
├── database_schema.sql            # Schema do banco de dados
├── database_utils.py              # Utilitários de consulta
├── Database.csv                   # Dados de exemplo
├── exemplo_almoxarifado.csv       # Arquivo de exemplo para integração
├── requirements.txt               # Dependências Python
├── GUIA_FUNCIONALIDADES_DASHBOARD.md  # Documentação completa
├── GUIA_INTEGRACAO_DADOS.md       # Guia de integração
├── README.md                      # Este arquivo
└── .gitignore                     # Arquivos ignorados pelo Git
```

## 📊 Dados Suportados

### **Colunas Obrigatórias (18):**
- `cod_material`: Código único do material
- `desc_material`: Descrição do material
- `familia`: Família do material
- `periodo`: Período da movimentação (mmm/aa)
- `quantidade`: Quantidade movimentada
- `custo_medio`: Custo médio unitário
- `valor_total`: Valor total da movimentação
- E mais 11 colunas de classificação e localização

### **Formato de Dados:**
- **Arquivo**: CSV com separador vírgula
- **Encoding**: UTF-8
- **Período**: Formato mmm/aa (ex: jan/23, fev/23)
- **Valores**: Padrão brasileiro (R$ 1.234.567,89)

## 🎯 Funcionalidades Detalhadas

### **Dashboard Geral**
- **4 Métricas Principais**: Total de materiais, valor total, quantidade, materiais ativos
- **4 KPIs Avançados**: Saída média por material/período, valor médio, períodos ativos
- **Alertas Inteligentes**: Baixa saída, alta saída, materiais inativos
- **4 Gráficos Interativos**: Evolução temporal, distribuição, top materiais

### **Análise de Materiais**
- **Busca Inteligente**: 3 tipos de busca (código, descrição, ambos)
- **Filtros Avançados**: Família, almoxarifado, valor mínimo
- **Análise Completa**: 5 seções de análise detalhada
- **Exportação**: Dados para análise externa

### **Análises Avançadas**
- **6 Gráficos Estatísticos**: Correlações, percentis, variabilidade, estabilidade
- **Previsão**: Modelos de média móvel e tendência linear
- **Otimização**: Análise ABC e sugestões de reposição
- **Relatórios**: Exportação automática para Excel/CSV

## 📈 Métricas e KPIs

### **Métricas Principais:**
- Total de materiais únicos
- Valor total das saídas (R$)
- Quantidade total de saídas
- Materiais com movimentação ativa

### **KPIs Avançados:**
- Saída média por material
- Saída média por período
- Valor médio por saída (R$)
- Períodos com movimentação ativa

### **Análises Estatísticas:**
- Coeficiente de variação
- Índice de sazonalidade
- Índice de concentração
- Análise de percentis (P25, P50, P75, P90, P95)

## 🔧 Configuração

### **Banco de Dados:**
- **Desenvolvimento**: SQLite (arquivo local)
- **Produção**: PostgreSQL (configurável)
- **Schema**: 12 tabelas normalizadas
- **Índices**: Otimizados para consultas rápidas

### **Interface:**
- **Layout**: Wide (otimizado para telas grandes)
- **Sidebar**: Expandida por padrão
- **Responsividade**: Adaptável a diferentes tamanhos
- **Tema**: Dark mode com cores profissionais

## 📊 Exemplos de Uso

### **Análise de Tendências:**
1. Acesse "Análise de Materiais"
2. Busque por um material específico
3. Visualize a evolução de preços
4. Analise a movimentação por período
5. Identifique tendências de crescimento/declínio

### **Otimização de Estoque:**
1. Acesse "Análises Avançadas" → "Otimização de Estoque"
2. Visualize a classificação ABC
3. Analise sugestões de reposição
4. Identifique materiais com baixo giro
5. Exporte relatórios para ação

### **Integração de Novos Dados:**
1. Acesse "Integração de Dados"
2. Consulte a documentação das colunas
3. Baixe o arquivo de exemplo
4. Faça upload do seu arquivo CSV
5. Processe e valide os dados

## 🚨 Alertas e Monitoramento

### **Tipos de Alertas:**
- **Baixa Saída**: Materiais com pouca movimentação
- **Alta Saída**: Materiais com movimentação excessiva
- **Materiais Inativos**: Sem movimentação recente

### **Ações Recomendadas:**
- Revisar estratégia de estoque
- Ajustar níveis de reposição
- Investigar materiais problemáticos
- Otimizar processos de movimentação

## 📈 Performance

- **Carregamento**: Dados carregados uma vez por sessão
- **Filtros**: Aplicação instantânea
- **Gráficos**: Renderização em tempo real
- **Responsividade**: Interface fluida em qualquer dispositivo

## 🔄 Manutenção

### **Atualização de Dados:**
1. Substitua o arquivo `Database.csv`
2. Execute o processamento via interface
3. Valide os dados processados
4. Reinicie o dashboard

### **Limpeza do Sistema:**
- Botão "Limpar Banco de Dados" na aba de integração
- Confirmação obrigatória para evitar perda de dados
- Backup automático antes da limpeza

## 🛡️ Segurança

- **Dados Locais**: Armazenamento local sem conexões externas
- **Validação**: Verificação de integridade dos dados
- **Backup**: Cópia de segurança automática
- **Controle de Acesso**: Interface local protegida

## 📞 Suporte

### **Documentação:**
- `GUIA_FUNCIONALIDADES_DASHBOARD.md`: Documentação completa
- `GUIA_INTEGRACAO_DADOS.md`: Guia de integração
- `exemplo_almoxarifado.csv`: Arquivo de exemplo

### **Solução de Problemas:**
1. Verifique se todas as dependências estão instaladas
2. Confirme se o arquivo CSV está no formato correto
3. Verifique os logs de processamento
4. Consulte a documentação de integração

## 🔮 Próximas Funcionalidades

- [ ] **Machine Learning**: Modelos preditivos mais avançados
- [ ] **Alertas por Email**: Notificações automáticas
- [ ] **API REST**: Integração com outros sistemas
- [ ] **Mobile App**: Aplicativo nativo
- [ ] **Relatórios Agendados**: Geração automática
- [ ] **Dashboard Executivo**: Visão estratégica simplificada

## 📄 Licença

Este projeto é de uso interno e educacional.

## 👥 Contribuição

Para contribuir com o projeto:
1. Faça um fork do repositório
2. Crie uma branch para sua feature
3. Implemente as melhorias
4. Teste thoroughly
5. Submeta um pull request

---

**Desenvolvido com ❤️ usando Streamlit e Plotly**

**Versão**: 1.0 | **Data**: Setembro 2025 | **Status**: Produção