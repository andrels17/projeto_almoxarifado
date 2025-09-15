"""
Processador de Dados do Almoxarifado
Processa o arquivo CSV e prepara os dados para importação no banco de dados
"""

import pandas as pd
import sqlite3
import numpy as np
from datetime import datetime
import re
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AlmoxarifadoDataProcessor:
    def __init__(self, csv_file_path, db_path="almoxarifado.db"):
        self.csv_file_path = csv_file_path
        self.db_path = db_path
        self.df = None
        self.conn = None
        
    def load_csv_data(self):
        """Carrega e processa o arquivo CSV"""
        logger.info(f"Carregando dados do arquivo: {self.csv_file_path}")
        
        try:
            # Carregar CSV com encoding correto
            self.df = pd.read_csv(
                self.csv_file_path, 
                sep=';', 
                encoding='latin-1',
                low_memory=False
            )
            
            logger.info(f"Dados carregados: {len(self.df)} registros, {len(self.df.columns)} colunas")
            
            # Renomear colunas para facilitar o processamento
            self.df.columns = [
                'periodo', 'cod_familia', 'desc_familia', 'cod_grupo_material', 'desc_grupo_material',
                'cod_material', 'desc_material', 'cod_tipo_material', 'desc_tipo_material', 'situacao',
                'localizacao', 'desc_localizacao', 'cod_localizacao', 'cod_almoxarifado', 'desc_almoxarifado',
                'unidade', 'quantidade', 'custo_medio', 'vlr_total', 'cod_classificacao_sped',
                'desc_classificacao_sped', 'controla_est_min', 'estoque_minimo', 'controla_est_max',
                'estoque_maximo', 'conta_contabil', 'desc_conta_contabil', 'ncm', 'desc_classificacao_fiscal',
                'cod_identificacao', 'desc_identificacao', 'curva_xyz'
            ]
            
            return True
            
        except Exception as e:
            logger.error(f"Erro ao carregar CSV: {e}")
            return False
    
    def clean_data(self):
        """Limpa e normaliza os dados"""
        logger.info("Iniciando limpeza dos dados...")
        
        # Converter período para formato padrão
        self.df['periodo'] = self.df['periodo'].astype(str)
        
        # Limpar valores numéricos
        numeric_columns = ['cod_familia', 'cod_grupo_material', 'cod_material', 'cod_tipo_material',
                          'cod_almoxarifado', 'quantidade', 'custo_medio', 'vlr_total',
                          'cod_classificacao_sped', 'estoque_minimo', 'estoque_maximo',
                          'conta_contabil', 'cod_identificacao']
        
        for col in numeric_columns:
            if col in self.df.columns:
                # Substituir vírgulas por pontos e converter para numérico
                self.df[col] = self.df[col].astype(str).str.replace(',', '.')
                self.df[col] = pd.to_numeric(self.df[col], errors='coerce')
        
        # Limpar strings
        string_columns = ['desc_familia', 'desc_grupo_material', 'desc_material', 'desc_tipo_material',
                         'desc_localizacao', 'desc_almoxarifado', 'desc_classificacao_sped',
                         'desc_conta_contabil', 'desc_classificacao_fiscal', 'desc_identificacao']
        
        for col in string_columns:
            if col in self.df.columns:
                self.df[col] = self.df[col].astype(str).str.strip().str.upper()
                self.df[col] = self.df[col].replace('NAN', '')
        
        # Converter booleanos
        self.df['controla_est_min'] = self.df['controla_est_min'].map({'Sim': True, 'Não': False, 'NÃO': False})
        self.df['controla_est_max'] = self.df['controla_est_max'].map({'Sim': True, 'Não': False, 'NÃO': False})
        
        # Remover linhas com dados essenciais faltando
        initial_count = len(self.df)
        self.df = self.df.dropna(subset=['cod_material', 'desc_material'])
        removed_count = initial_count - len(self.df)
        
        if removed_count > 0:
            logger.warning(f"Removidas {removed_count} linhas com dados essenciais faltando")
        
        logger.info(f"Limpeza concluída. Registros restantes: {len(self.df)}")
        return True
    
    def create_database_connection(self):
        """Cria conexão com o banco de dados"""
        try:
            self.conn = sqlite3.connect(self.db_path)
            logger.info(f"Conexão com banco de dados estabelecida: {self.db_path}")
            return True
        except Exception as e:
            logger.error(f"Erro ao conectar com banco de dados: {e}")
            return False
    
    def create_tables(self):
        """Cria as tabelas no banco de dados"""
        try:
            with open('database_schema.sql', 'r', encoding='utf-8') as f:
                schema = f.read()
            
            # Executar schema em partes (SQLite não suporta múltiplas statements)
            statements = schema.split(';')
            for statement in statements:
                statement = statement.strip()
                if statement:
                    self.conn.execute(statement)
            
            self.conn.commit()
            logger.info("Tabelas criadas com sucesso")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao criar tabelas: {e}")
            return False
    
    def insert_lookup_data(self):
        """Insere dados de lookup (tabelas de referência)"""
        logger.info("Inserindo dados de lookup...")
        
        try:
            # Inserir períodos
            periodos = self.df[['periodo']].drop_duplicates()
            for _, row in periodos.iterrows():
                periodo = row['periodo']
                # Extrair ano e mês do período
                try:
                    if '/' in periodo:
                        mes, ano = periodo.split('/')
                        ano = int('20' + ano) if len(ano) == 2 else int(ano)
                        mes = int(mes)
                    else:
                        ano = 2023
                        mes = 1
                except:
                    ano = 2023
                    mes = 1
                
                self.conn.execute("""
                    INSERT OR IGNORE INTO periodos (periodo, ano, mes) 
                    VALUES (?, ?, ?)
                """, (periodo, ano, mes))
            
            # Inserir famílias
            familias = self.df[['cod_familia', 'desc_familia']].drop_duplicates()
            for _, row in familias.iterrows():
                self.conn.execute("""
                    INSERT OR IGNORE INTO familias (codigo, descricao) 
                    VALUES (?, ?)
                """, (int(row['cod_familia']), row['desc_familia']))
            
            # Inserir grupos de materiais
            grupos = self.df[['cod_grupo_material', 'desc_grupo_material', 'cod_familia']].drop_duplicates()
            for _, row in grupos.iterrows():
                # Buscar ID da família
                familia_id = self.conn.execute("""
                    SELECT id FROM familias WHERE codigo = ?
                """, (int(row['cod_familia']),)).fetchone()
                
                familia_id = familia_id[0] if familia_id else None
                
                self.conn.execute("""
                    INSERT OR IGNORE INTO grupos_materiais (codigo, descricao, familia_id) 
                    VALUES (?, ?, ?)
                """, (int(row['cod_grupo_material']), row['desc_grupo_material'], familia_id))
            
            # Inserir tipos de materiais
            tipos = self.df[['cod_tipo_material', 'desc_tipo_material']].drop_duplicates()
            for _, row in tipos.iterrows():
                self.conn.execute("""
                    INSERT OR IGNORE INTO tipos_materiais (codigo, descricao) 
                    VALUES (?, ?)
                """, (int(row['cod_tipo_material']), row['desc_tipo_material']))
            
            # Inserir almoxarifados
            almoxarifados = self.df[['cod_almoxarifado', 'desc_almoxarifado']].drop_duplicates()
            for _, row in almoxarifados.iterrows():
                self.conn.execute("""
                    INSERT OR IGNORE INTO almoxarifados (codigo, descricao) 
                    VALUES (?, ?)
                """, (int(row['cod_almoxarifado']), row['desc_almoxarifado']))
            
            # Inserir localizações
            localizacoes = self.df[['cod_localizacao', 'desc_localizacao', 'cod_almoxarifado']].drop_duplicates()
            for _, row in localizacoes.iterrows():
                if pd.notna(row['cod_localizacao']):
                    self.conn.execute("""
                        INSERT OR IGNORE INTO localizacoes (codigo, descricao, codigo_almoxarifado) 
                        VALUES (?, ?, ?)
                    """, (str(row['cod_localizacao']), row['desc_localizacao'], int(row['cod_almoxarifado'])))
            
            # Inserir classificações SPED
            speds = self.df[['cod_classificacao_sped', 'desc_classificacao_sped']].drop_duplicates()
            for _, row in speds.iterrows():
                if pd.notna(row['cod_classificacao_sped']):
                    self.conn.execute("""
                        INSERT OR IGNORE INTO classificacoes_sped (codigo, descricao) 
                        VALUES (?, ?)
                    """, (int(row['cod_classificacao_sped']), row['desc_classificacao_sped']))
            
            # Inserir contas contábeis
            contas = self.df[['conta_contabil', 'desc_conta_contabil']].drop_duplicates()
            for _, row in contas.iterrows():
                if pd.notna(row['conta_contabil']):
                    self.conn.execute("""
                        INSERT OR IGNORE INTO contas_contabeis (codigo, descricao) 
                        VALUES (?, ?)
                    """, (int(row['conta_contabil']), row['desc_conta_contabil']))
            
            # Inserir classificações fiscais
            fiscais = self.df[['ncm', 'desc_classificacao_fiscal']].drop_duplicates()
            for _, row in fiscais.iterrows():
                if pd.notna(row['ncm']):
                    self.conn.execute("""
                        INSERT OR IGNORE INTO classificacoes_fiscais (ncm, descricao) 
                        VALUES (?, ?)
                    """, (str(row['ncm']), row['desc_classificacao_fiscal']))
            
            # Inserir identificações
            ids = self.df[['cod_identificacao', 'desc_identificacao']].drop_duplicates()
            for _, row in ids.iterrows():
                if pd.notna(row['cod_identificacao']):
                    self.conn.execute("""
                        INSERT OR IGNORE INTO identificacoes (codigo, descricao) 
                        VALUES (?, ?)
                    """, (int(row['cod_identificacao']), row['desc_identificacao']))
            
            self.conn.commit()
            logger.info("Dados de lookup inseridos com sucesso")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao inserir dados de lookup: {e}")
            return False
    
    def insert_materials_and_stock(self):
        """Insere materiais e dados de estoque"""
        logger.info("Inserindo materiais e dados de estoque...")
        
        try:
            # Inserir materiais
            materiais = self.df[['cod_material', 'desc_material', 'cod_grupo_material', 
                               'cod_tipo_material', 'unidade', 'situacao', 'controla_est_min',
                               'estoque_minimo', 'controla_est_max', 'estoque_maximo', 'curva_xyz']].drop_duplicates()
            
            for _, row in materiais.iterrows():
                # Buscar IDs das tabelas relacionadas
                grupo_id = self.conn.execute("""
                    SELECT id FROM grupos_materiais WHERE codigo = ?
                """, (int(row['cod_grupo_material']),)).fetchone()
                grupo_id = grupo_id[0] if grupo_id else None
                
                tipo_id = self.conn.execute("""
                    SELECT id FROM tipos_materiais WHERE codigo = ?
                """, (int(row['cod_tipo_material']),)).fetchone()
                tipo_id = tipo_id[0] if tipo_id else None
                
                self.conn.execute("""
                    INSERT OR IGNORE INTO materiais 
                    (codigo, descricao, grupo_material_id, tipo_material_id, unidade, situacao,
                     controla_estoque_min, estoque_minimo, controla_estoque_max, estoque_maximo, curva_xyz)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (int(row['cod_material']), row['desc_material'], grupo_id, tipo_id,
                      row['unidade'], row['situacao'], row['controla_est_min'], row['estoque_minimo'],
                      row['controla_est_max'], row['estoque_maximo'], row['curva_xyz']))
            
            # Inserir dados de estoque
            for _, row in self.df.iterrows():
                # Buscar IDs das tabelas relacionadas
                periodo_id = self.conn.execute("""
                    SELECT id FROM periodos WHERE periodo = ?
                """, (row['periodo'],)).fetchone()
                periodo_id = periodo_id[0] if periodo_id else None
                
                material_id = self.conn.execute("""
                    SELECT id FROM materiais WHERE codigo = ?
                """, (int(row['cod_material']),)).fetchone()
                material_id = material_id[0] if material_id else None
                
                localizacao_id = None
                if pd.notna(row['cod_localizacao']):
                    localizacao_id = self.conn.execute("""
                        SELECT id FROM localizacoes WHERE codigo = ?
                    """, (str(row['cod_localizacao']),)).fetchone()
                    localizacao_id = localizacao_id[0] if localizacao_id else None
                
                almoxarifado_id = self.conn.execute("""
                    SELECT id FROM almoxarifados WHERE codigo = ?
                """, (int(row['cod_almoxarifado']),)).fetchone()
                almoxarifado_id = almoxarifado_id[0] if almoxarifado_id else None
                
                classificacao_sped_id = None
                if pd.notna(row['cod_classificacao_sped']):
                    classificacao_sped_id = self.conn.execute("""
                        SELECT id FROM classificacoes_sped WHERE codigo = ?
                    """, (int(row['cod_classificacao_sped']),)).fetchone()
                    classificacao_sped_id = classificacao_sped_id[0] if classificacao_sped_id else None
                
                conta_contabil_id = None
                if pd.notna(row['conta_contabil']):
                    conta_contabil_id = self.conn.execute("""
                        SELECT id FROM contas_contabeis WHERE codigo = ?
                    """, (int(row['conta_contabil']),)).fetchone()
                    conta_contabil_id = conta_contabil_id[0] if conta_contabil_id else None
                
                classificacao_fiscal_id = None
                if pd.notna(row['ncm']):
                    classificacao_fiscal_id = self.conn.execute("""
                        SELECT id FROM classificacoes_fiscais WHERE ncm = ?
                    """, (str(row['ncm']),)).fetchone()
                    classificacao_fiscal_id = classificacao_fiscal_id[0] if classificacao_fiscal_id else None
                
                identificacao_id = None
                if pd.notna(row['cod_identificacao']):
                    identificacao_id = self.conn.execute("""
                        SELECT id FROM identificacoes WHERE codigo = ?
                    """, (int(row['cod_identificacao']),)).fetchone()
                    identificacao_id = identificacao_id[0] if identificacao_id else None
                
                self.conn.execute("""
                    INSERT INTO estoque 
                    (periodo_id, material_id, localizacao_id, almoxarifado_id, classificacao_sped_id,
                     conta_contabil_id, classificacao_fiscal_id, identificacao_id, quantidade, custo_medio, valor_total)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (periodo_id, material_id, localizacao_id, almoxarifado_id, classificacao_sped_id,
                      conta_contabil_id, classificacao_fiscal_id, identificacao_id, row['quantidade'],
                      row['custo_medio'], row['vlr_total']))
            
            self.conn.commit()
            logger.info("Materiais e dados de estoque inseridos com sucesso")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao inserir materiais e estoque: {e}")
            return False
    
    def process_all(self):
        """Executa todo o pipeline de processamento"""
        logger.info("Iniciando processamento completo dos dados...")
        
        if not self.load_csv_data():
            return False
        
        if not self.clean_data():
            return False
        
        if not self.create_database_connection():
            return False
        
        if not self.create_tables():
            return False
        
        if not self.insert_lookup_data():
            return False
        
        if not self.insert_materials_and_stock():
            return False
        
        logger.info("Processamento concluído com sucesso!")
        return True
    
    def close_connection(self):
        """Fecha a conexão com o banco de dados"""
        if self.conn:
            self.conn.close()
            logger.info("Conexão com banco de dados fechada")

if __name__ == "__main__":
    processor = AlmoxarifadoDataProcessor("Database.csv")
    
    try:
        success = processor.process_all()
        if success:
            print("✅ Processamento concluído com sucesso!")
            print(f"📊 Banco de dados criado: {processor.db_path}")
        else:
            print("❌ Erro no processamento dos dados")
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
    finally:
        processor.close_connection()
