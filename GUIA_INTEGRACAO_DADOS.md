# 📥 Guia de Integração de Dados

## 🎯 **Visão Geral**

Este guia fornece instruções completas para integrar novos dados ao sistema de almoxarifado. A integração é feita através de arquivos CSV ou Excel que seguem um formato específico.

## 📋 **Colunas Obrigatórias**

### **Colunas Principais**
| Coluna | Tipo | Descrição | Exemplo |
|--------|------|-----------|---------|
| `cod_material` | Texto | Código único do material | MAT001 |
| `desc_material` | Texto | Descrição do material | Parafuso M6x20 |
| `quantidade` | Numérico | Quantidade em estoque | 1000 |
| `custo_medio` | Numérico | Custo médio unitário | 0.15 |
| `valor_total` | Numérico | Valor total (quantidade × custo_medio) | 150.00 |
| `unidade` | Texto | Unidade de medida | UN |
| `periodo` | Texto | Período no formato 'mmm/aa' | jan/23 |
| `ano` | Numérico | Ano | 2023 |
| `mes` | Numérico | Mês numérico (1-12) | 1 |

### **Colunas de Classificação**
| Coluna | Tipo | Descrição | Exemplo |
|--------|------|-----------|---------|
| `familia` | Texto | Família do material | Ferramentas |
| `grupo_material` | Texto | Grupo do material | Parafusos |
| `tipo_material` | Texto | Tipo do material | Metal |
| `almoxarifado` | Texto | Nome do almoxarifado | Principal |
| `localizacao` | Texto | Localização física | A1-B2 |
| `classificacao_sped` | Texto | Classificação SPED | 15.01.01 |
| `conta_contabil` | Texto | Conta contábil | 1.1.01.001 |
| `classificacao_fiscal` | Texto | Classificação fiscal | NCM12345678 |
| `identificacao` | Texto | Identificação adicional | LOTE001 |

## 🏗️ **Estrutura do Banco de Dados**

### **Tabelas Principais**
- **`materiais`**: Informações dos materiais
- **`estoque`**: Dados de estoque por período
- **`periodos`**: Períodos disponíveis
- **`familias`**: Famílias de materiais
- **`grupos_materiais`**: Grupos de materiais
- **`tipos_materiais`**: Tipos de materiais
- **`almoxarifados`**: Almoxarifados
- **`localizacoes`**: Localizações físicas
- **`classificacoes_sped`**: Classificações SPED
- **`contas_contabeis`**: Contas contábeis
- **`classificacoes_fiscais`**: Classificações fiscais
- **`identificacoes`**: Identificações adicionais

### **Relacionamentos**
- Cada material pertence a uma família, grupo e tipo
- Cada registro de estoque está associado a um material e período
- As classificações são referenciadas por IDs numéricos

## 📄 **Exemplo de Arquivo CSV**

```csv
cod_material,desc_material,quantidade,custo_medio,valor_total,unidade,periodo,ano,mes,familia,grupo_material,tipo_material,almoxarifado,localizacao,classificacao_sped,conta_contabil,classificacao_fiscal,identificacao
MAT001,Parafuso M6x20,1000,0.15,150.00,UN,jan/23,2023,1,Ferramentas,Parafusos,Metal,Principal,A1-B2,15.01.01,1.1.01.001,NCM12345678,LOTE001
MAT002,Porca M6,500,0.08,40.00,UN,jan/23,2023,1,Ferramentas,Porcas,Metal,Principal,A1-B3,15.01.02,1.1.01.002,NCM87654321,LOTE002
MAT003,Arruela M6,2000,0.03,60.00,UN,jan/23,2023,1,Ferramentas,Arruelas,Metal,Principal,A1-B4,15.01.03,1.1.01.003,NCM11223344,LOTE003
```

## 🔧 **Processo de Integração**

### **Passo 1: Preparar o Arquivo**
1. Use o formato CSV ou Excel
2. Inclua todas as colunas obrigatórias
3. Verifique se os dados estão no formato correto
4. Use o arquivo de exemplo como referência

### **Passo 2: Validar os Dados**
1. Verifique se os códigos de material são únicos
2. Confirme se os períodos estão no formato 'mmm/aa'
3. Valide se os valores numéricos estão corretos
4. Verifique se as classificações existem no sistema

### **Passo 3: Processar os Dados**
1. Use o script `data_processor_optimized.py` para processar o arquivo
2. O script criará automaticamente as tabelas necessárias
3. Os dados serão inseridos no banco SQLite

### **Passo 4: Verificar a Integração**
1. Execute o dashboard para visualizar os dados
2. Verifique se os gráficos estão funcionando
3. Confirme se os filtros estão aplicando corretamente

## 💻 **Comandos para Integração**

```bash
# 1. Instalar dependências
pip install -r requirements.txt

# 2. Processar novo arquivo
python data_processor_optimized.py

# 3. Executar dashboard
streamlit run dashboard.py
```

## ⚠️ **Avisos Importantes**

- **Backup**: Faça backup do banco de dados antes de integrar novos dados
- **Teste**: Teste com uma pequena amostra antes de processar o arquivo completo
- **Conflitos**: Verifique se não há conflitos com dados existentes
- **Formato**: Mantenha o formato exato das colunas e dados

## 🆘 **Suporte**

- Consulte a documentação do projeto
- Verifique os logs de processamento
- Entre em contato com o administrador do sistema

## 📊 **Validações Automáticas**

O sistema realiza as seguintes validações automaticamente:

1. **Unicidade**: Códigos de material únicos
2. **Formato**: Períodos no formato correto
3. **Tipos**: Valores numéricos válidos
4. **Relacionamentos**: Referências válidas entre tabelas
5. **Integridade**: Dados consistentes e completos

## 🔄 **Atualizações Futuras**

Para atualizar dados existentes:

1. **Incremental**: Adicione apenas novos períodos
2. **Completa**: Substitua todos os dados (cuidado!)
3. **Seletiva**: Atualize apenas materiais específicos

## 📈 **Monitoramento**

Após a integração, monitore:

- **Performance**: Tempo de carregamento do dashboard
- **Dados**: Verificação de integridade dos dados
- **Gráficos**: Funcionamento correto das visualizações
- **Filtros**: Aplicação correta dos filtros

## 🎯 **Melhores Práticas**

1. **Documentação**: Mantenha documentação dos dados
2. **Versionamento**: Use controle de versão para os arquivos
3. **Testes**: Teste sempre antes de integrar em produção
4. **Backup**: Faça backup regular dos dados
5. **Monitoramento**: Monitore o sistema após integrações

---

**Este guia garante uma integração suave e segura de novos dados ao sistema de almoxarifado!** 🎉
