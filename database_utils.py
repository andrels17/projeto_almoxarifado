"""
Utilitários para consultas no banco de dados do Almoxarifado
"""

import sqlite3
import pandas as pd
from datetime import datetime

class DatabaseUtils:
    def __init__(self, db_path="almoxarifado.db"):
        self.db_path = db_path
    
    def get_connection(self):
        """Retorna conexão com o banco de dados"""
        return sqlite3.connect(self.db_path)
    
    def get_estatisticas_gerais(self):
        """Retorna estatísticas gerais do banco"""
        conn = self.get_connection()
        
        queries = {
            'total_materiais': "SELECT COUNT(DISTINCT codigo) FROM materiais",
            'total_familias': "SELECT COUNT(*) FROM familias",
            'total_grupos': "SELECT COUNT(*) FROM grupos_materiais",
            'total_almoxarifados': "SELECT COUNT(*) FROM almoxarifados",
            'total_periodos': "SELECT COUNT(*) FROM periodos",
            'total_registros_estoque': "SELECT COUNT(*) FROM estoque"
        }
        
        stats = {}
        for key, query in queries.items():
            result = conn.execute(query).fetchone()
            stats[key] = result[0] if result else 0
        
        conn.close()
        return stats
    
    def get_materiais_por_familia(self):
        """Retorna distribuição de materiais por família"""
        conn = self.get_connection()
        
        query = """
            SELECT f.descricao as familia, COUNT(m.id) as total_materiais
            FROM familias f
            LEFT JOIN grupos_materiais g ON f.id = g.familia_id
            LEFT JOIN materiais m ON g.id = m.grupo_material_id
            GROUP BY f.id, f.descricao
            ORDER BY total_materiais DESC
        """
        
        result = pd.read_sql_query(query, conn)
        conn.close()
        return result
    
    def get_estoque_por_periodo(self):
        """Retorna evolução do estoque por período"""
        conn = self.get_connection()
        
        query = """
            SELECT p.periodo, p.ano, p.mes,
                   COUNT(DISTINCT e.material_id) as total_materiais,
                   SUM(e.quantidade) as quantidade_total,
                   SUM(e.valor_total) as valor_total,
                   AVG(e.custo_medio) as custo_medio
            FROM estoque e
            JOIN periodos p ON e.periodo_id = p.id
            GROUP BY p.id, p.periodo, p.ano, p.mes
            ORDER BY p.ano, p.mes
        """
        
        result = pd.read_sql_query(query, conn)
        conn.close()
        return result
    
    def get_top_materiais_valor(self, limit=20):
        """Retorna top materiais por valor"""
        conn = self.get_connection()
        
        query = """
            SELECT m.codigo, m.descricao, f.descricao as familia,
                   SUM(e.valor_total) as valor_total,
                   SUM(e.quantidade) as quantidade_total,
                   AVG(e.custo_medio) as custo_medio
            FROM estoque e
            JOIN materiais m ON e.material_id = m.id
            JOIN grupos_materiais g ON m.grupo_material_id = g.id
            JOIN familias f ON g.familia_id = f.id
            GROUP BY m.id, m.codigo, m.descricao, f.descricao
            ORDER BY valor_total DESC
            LIMIT ?
        """
        
        result = pd.read_sql_query(query, conn, params=(limit,))
        conn.close()
        return result
    
    def get_materiais_baixo_estoque(self, percentual_minimo=0.1):
        """Retorna materiais com estoque baixo"""
        conn = self.get_connection()
        
        query = """
            SELECT m.codigo, m.descricao, f.descricao as familia,
                   SUM(e.quantidade) as quantidade_atual,
                   m.estoque_minimo,
                   AVG(e.custo_medio) as custo_medio,
                   SUM(e.valor_total) as valor_total
            FROM estoque e
            JOIN materiais m ON e.material_id = m.id
            JOIN grupos_materiais g ON m.grupo_material_id = g.id
            JOIN familias f ON g.familia_id = f.id
            WHERE m.controla_estoque_min = 1
            GROUP BY m.id, m.codigo, m.descricao, f.descricao, m.estoque_minimo
            HAVING quantidade_atual <= (m.estoque_minimo * (1 + ?))
            ORDER BY (quantidade_atual / m.estoque_minimo) ASC
        """
        
        result = pd.read_sql_query(query, conn, params=(percentual_minimo,))
        conn.close()
        return result
    
    def get_curva_abc(self):
        """Retorna dados para análise de curva ABC"""
        conn = self.get_connection()
        
        query = """
            SELECT m.codigo, m.descricao, f.descricao as familia,
                   SUM(e.valor_total) as valor_total,
                   SUM(e.quantidade) as quantidade_total
            FROM estoque e
            JOIN materiais m ON e.material_id = m.id
            JOIN grupos_materiais g ON m.grupo_material_id = g.id
            JOIN familias f ON g.familia_id = f.id
            GROUP BY m.id, m.codigo, m.descricao, f.descricao
            ORDER BY valor_total DESC
        """
        
        result = pd.read_sql_query(query, conn)
        
        # Calcular percentuais acumulados
        result['valor_acumulado'] = result['valor_total'].cumsum()
        result['percentual_acumulado'] = (result['valor_acumulado'] / result['valor_total'].sum()) * 100
        
        # Classificar em A, B, C
        result['classificacao'] = 'C'
        result.loc[result['percentual_acumulado'] <= 80, 'classificacao'] = 'A'
        result.loc[(result['percentual_acumulado'] > 80) & (result['percentual_acumulado'] <= 95), 'classificacao'] = 'B'
        
        conn.close()
        return result
    
    def export_to_excel(self, filename="relatorio_almoxarifado.xlsx"):
        """Exporta dados principais para Excel"""
        conn = self.get_connection()
        
        with pd.ExcelWriter(filename, engine='openpyxl') as writer:
            # Estatísticas gerais
            stats = self.get_estatisticas_gerais()
            pd.DataFrame([stats]).to_excel(writer, sheet_name='Estatísticas', index=False)
            
            # Materiais por família
            self.get_materiais_por_familia().to_excel(writer, sheet_name='Materiais por Família', index=False)
            
            # Estoque por período
            self.get_estoque_por_periodo().to_excel(writer, sheet_name='Estoque por Período', index=False)
            
            # Top materiais
            self.get_top_materiais_valor(50).to_excel(writer, sheet_name='Top 50 Materiais', index=False)
            
            # Curva ABC
            self.get_curva_abc().to_excel(writer, sheet_name='Curva ABC', index=False)
            
            # Materiais baixo estoque
            self.get_materiais_baixo_estoque().to_excel(writer, sheet_name='Baixo Estoque', index=False)
        
        conn.close()
        return filename

if __name__ == "__main__":
    # Exemplo de uso
    utils = DatabaseUtils()
    
    print("=== Estatísticas Gerais ===")
    stats = utils.get_estatisticas_gerais()
    for key, value in stats.items():
        print(f"{key}: {value}")
    
    print("\n=== Top 10 Materiais por Valor ===")
    top = utils.get_top_materiais_valor(10)
    print(top[['codigo', 'descricao', 'valor_total']].head())
    
    print("\n=== Materiais com Baixo Estoque ===")
    baixo_estoque = utils.get_materiais_baixo_estoque()
    print(f"Total de materiais com baixo estoque: {len(baixo_estoque)}")
    
    # Exportar para Excel
    print("\n=== Exportando para Excel ===")
    filename = utils.export_to_excel()
    print(f"Relatório exportado para: {filename}")
