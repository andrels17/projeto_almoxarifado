-- Schema do Banco de Dados do Almoxarifado
-- Criado para otimizar consultas e dashboards

-- Tabela de Períodos
CREATE TABLE IF NOT EXISTS periodos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    periodo TEXT UNIQUE NOT NULL,
    ano INTEGER,
    mes INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de Famílias de Materiais
CREATE TABLE IF NOT EXISTS familias (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    codigo INTEGER UNIQUE NOT NULL,
    descricao TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de Grupos de Materiais
CREATE TABLE IF NOT EXISTS grupos_materiais (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    codigo INTEGER UNIQUE NOT NULL,
    descricao TEXT NOT NULL,
    familia_id INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (familia_id) REFERENCES familias(id)
);

-- Tabela de Tipos de Materiais
CREATE TABLE IF NOT EXISTS tipos_materiais (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    codigo INTEGER UNIQUE NOT NULL,
    descricao TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de Almoxarifados
CREATE TABLE IF NOT EXISTS almoxarifados (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    codigo INTEGER UNIQUE NOT NULL,
    descricao TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de Localizações
CREATE TABLE IF NOT EXISTS localizacoes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    codigo TEXT UNIQUE NOT NULL,
    descricao TEXT,
    codigo_almoxarifado INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (codigo_almoxarifado) REFERENCES almoxarifados(codigo)
);

-- Tabela de Classificações SPED
CREATE TABLE IF NOT EXISTS classificacoes_sped (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    codigo INTEGER UNIQUE NOT NULL,
    descricao TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de Contas Contábeis
CREATE TABLE IF NOT EXISTS contas_contabeis (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    codigo INTEGER UNIQUE NOT NULL,
    descricao TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de Classificações Fiscais
CREATE TABLE IF NOT EXISTS classificacoes_fiscais (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ncm TEXT UNIQUE,
    descricao TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de Identificações
CREATE TABLE IF NOT EXISTS identificacoes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    codigo INTEGER UNIQUE NOT NULL,
    descricao TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabela Principal de Materiais
CREATE TABLE IF NOT EXISTS materiais (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    codigo INTEGER UNIQUE NOT NULL,
    descricao TEXT NOT NULL,
    grupo_material_id INTEGER,
    tipo_material_id INTEGER,
    unidade TEXT,
    situacao TEXT,
    controla_estoque_min BOOLEAN,
    estoque_minimo REAL,
    controla_estoque_max BOOLEAN,
    estoque_maximo REAL,
    curva_xyz TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (grupo_material_id) REFERENCES grupos_materiais(id),
    FOREIGN KEY (tipo_material_id) REFERENCES tipos_materiais(id)
);

-- Tabela de Estoque (dados históricos)
CREATE TABLE IF NOT EXISTS estoque (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    periodo_id INTEGER,
    material_id INTEGER,
    localizacao_id INTEGER,
    almoxarifado_id INTEGER,
    classificacao_sped_id INTEGER,
    conta_contabil_id INTEGER,
    classificacao_fiscal_id INTEGER,
    identificacao_id INTEGER,
    quantidade REAL,
    custo_medio REAL,
    valor_total REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (periodo_id) REFERENCES periodos(id),
    FOREIGN KEY (material_id) REFERENCES materiais(id),
    FOREIGN KEY (localizacao_id) REFERENCES localizacoes(id),
    FOREIGN KEY (almoxarifado_id) REFERENCES almoxarifados(id),
    FOREIGN KEY (classificacao_sped_id) REFERENCES classificacoes_sped(id),
    FOREIGN KEY (conta_contabil_id) REFERENCES contas_contabeis(id),
    FOREIGN KEY (classificacao_fiscal_id) REFERENCES classificacoes_fiscais(id),
    FOREIGN KEY (identificacao_id) REFERENCES identificacoes(id)
);

-- Índices para otimizar consultas
CREATE INDEX IF NOT EXISTS idx_estoque_periodo ON estoque(periodo_id);
CREATE INDEX IF NOT EXISTS idx_estoque_material ON estoque(material_id);
CREATE INDEX IF NOT EXISTS idx_estoque_almoxarifado ON estoque(almoxarifado_id);
CREATE INDEX IF NOT EXISTS idx_estoque_localizacao ON estoque(localizacao_id);
CREATE INDEX IF NOT EXISTS idx_materiais_grupo ON materiais(grupo_material_id);
CREATE INDEX IF NOT EXISTS idx_materiais_tipo ON materiais(tipo_material_id);
CREATE INDEX IF NOT EXISTS idx_grupos_familia ON grupos_materiais(familia_id);
