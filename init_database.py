#!/usr/bin/env python3
"""
Script de inicialização do banco de dados para Streamlit Cloud
"""

import sqlite3
import pandas as pd
import os

def init_database():
    """Inicializa o banco de dados se não existir"""
    
    # Verificar se o banco existe
    if not os.path.exists('almoxarifado.db'):
        print("Criando banco de dados...")
        
        # Ler o schema
        with open('database_schema.sql', 'r', encoding='utf-8') as f:
            schema = f.read()
        
        # Conectar e criar tabelas
        conn = sqlite3.connect('almoxarifado.db')
        cursor = conn.cursor()
        
        # Executar schema
        cursor.executescript(schema)
        conn.commit()
        
        # Verificar se existe arquivo de dados
        if os.path.exists('Database.csv'):
            print("Carregando dados do CSV...")
            
            # Carregar dados
            df = pd.read_csv('Database.csv', encoding='utf-8')
            
            # Processar dados (simplificado para demo)
            # Aqui você pode adicionar a lógica de processamento se necessário
            
            print(f"Dados carregados: {len(df)} registros")
        
        conn.close()
        print("Banco de dados inicializado com sucesso!")
    else:
        print("Banco de dados já existe!")

if __name__ == "__main__":
    init_database()
