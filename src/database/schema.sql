-- 聚酯家族高分子结晶数据库 schema (v1.1，对齐执行计划 §3 四层模型)
--
-- 单位约定（写库前务必遵守）：
--   · 晶胞长度 a/b/c、纤维周期 fiber_period 一律 Å
--   · 晶系角 alpha/beta/gamma 一律 °
--   · 晶体密度 rho_crystal 一律 g/cm3
--   · 温度默认 °C（保留 *_unit 列的字段才允许 K）
--   · 能量 delta_hf 默认 J/g（保留 delta_hf_unit 列才允许 kJ/mol）
--   · 速度 growth_rate 默认 nm/s
--
-- 重要约束：observations 表【不】对晶胞参数设 UNIQUE。
--   同一聚合物不同文献常给出略不同的晶胞参数，这些"分歧记录"是本项目
--   的核心价值（冲突消解见计划 §4.4），必须全部保留，绝不能因数值重复被拒。

-- ===== L0 聚合物成员 =====
CREATE TABLE IF NOT EXISTS polymers (
    polymer_id        INTEGER PRIMARY KEY AUTOINCREMENT,
    abbr              TEXT NOT NULL UNIQUE,
    name_en           TEXT NOT NULL,
    name_zh           TEXT,
    family_branch     TEXT,                     -- aromatic / aliphatic / copolyester
    cru_smiles        TEXT,                     -- 重复单元 SMILES；抽取阶段由 RDKit 归一化后回填，初版留空
    repeat_unit_mw    REAL,                     -- 重复单元分子量 (g/mol)
    has_chiral_center INTEGER DEFAULT 0,         -- 0/1
    tacticity_policy  TEXT,                     -- isotactic / syndiotactic / atactic / N.A.
    tier              INTEGER DEFAULT 1,         -- 1 = Tier1 必收，2 = Tier2 候选
    notes             TEXT,
    created_at        TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ===== L1 晶型（一个成员可有 1~5 个晶型） =====
CREATE TABLE IF NOT EXISTS polymorphs (
    polymorph_id       INTEGER PRIMARY KEY AUTOINCREMENT,
    polymer_id         INTEGER NOT NULL,
    polymorph_label    TEXT,                     -- alpha / beta / alpha_prime / sc / monoclinic ...
    crystal_system     TEXT,                     -- triclinic / monoclinic / orthorhombic / hexagonal
    space_group        TEXT,                     -- 如 P-1
    a REAL, b REAL, c REAL,                      -- Å
    alpha REAL, beta REAL, gamma REAL,           -- °
    z                  INTEGER,                  -- 每晶胞重复单元数
    chain_conformation TEXT,                     -- 如 tggt（PTT 的近 trans-gauche-gauche-trans）
    rho_crystal        REAL,                     -- g/cm3
    fiber_period       REAL,                     -- Å（纤维恒等周期 / 链轴长度）
    helix_type         TEXT,
    packing_note       TEXT,
    created_at         TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (polymer_id) REFERENCES polymers(polymer_id)
);

-- ===== L2 观测行（计数的"一条"= 一条 Tc/一组结构） =====
CREATE TABLE IF NOT EXISTS observations (
    obs_id             INTEGER PRIMARY KEY AUTOINCREMENT,
    polymer_id         INTEGER NOT NULL,
    polymorph_id       INTEGER,                  -- 可空：文献未指明晶型时
    -- 溯源
    doi                TEXT,
    ref_year           INTEGER,
    ref_source         TEXT,                     -- 期刊 / 书名
    ref_table          TEXT,                     -- 原文表号 / 图号
    source_field       TEXT,                     -- measured / review-cited
    -- 样品
    mn                 REAL, mw REAL, pdi REAL, origin TEXT,
    -- 热历史（决定晶型与结晶度的关键变量）
    t_c                REAL, t_c_unit     TEXT DEFAULT '°C',
    cryst_route        TEXT,                     -- melt / solution / cold-crystallization / stress-induced
    cooling_rate       REAL,
    anneal_t           REAL, anneal_time_h REAL,
    draw_ratio         REAL, shear_orientation TEXT,
    -- 结构观测
    xtallinity_pct     REAL,
    long_period        REAL,                     -- nm（SAXS）
    lamellar_thickness REAL,                     -- nm
    unit_cell_refined  INTEGER DEFAULT 0,         -- 本条是否重修了晶胞
    -- 动力学
    growth_rate        REAL, growth_rate_unit TEXT DEFAULT 'nm/s',
    avrami_n           REAL, avrami_k REAL, t_half REAL,
    -- 热力学
    tm                 REAL, tm_unit TEXT DEFAULT '°C',
    tm0                REAL,
    delta_hf           REAL, delta_hf_unit TEXT DEFAULT 'J/g',
    tg                 REAL,
    -- 质量标记
    extraction_confidence REAL,
    reviewed_by        TEXT, review_status TEXT, conflict_flag INTEGER DEFAULT 0,
    clash_with_ids     TEXT,                     -- 指向冲突记录的 obs_id 列表（逗号分隔）
    created_at         TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (polymer_id) REFERENCES polymers(polymer_id),
    FOREIGN KEY (polymorph_id) REFERENCES polymorphs(polymorph_id)
);

-- ===== L2.5 全原子坐标（高分子 CIF 罕见，多数情况为空，预留） =====
CREATE TABLE IF NOT EXISTS atomic_coordinates (
    coord_id     INTEGER PRIMARY KEY AUTOINCREMENT,
    polymorph_id INTEGER NOT NULL,
    atom_label   TEXT, atom_type TEXT,
    x REAL, y REAL, z REAL,
    occupancy    REAL DEFAULT 1.0,
    b_factor    REAL,
    FOREIGN KEY (polymorph_id) REFERENCES polymorphs(polymorph_id)
);

-- ===== L2.5 通用物性扩展表（observations 未列出的其它实测量） =====
CREATE TABLE IF NOT EXISTS properties (
    property_id          INTEGER PRIMARY KEY AUTOINCREMENT,
    obs_id               INTEGER NOT NULL,
    property_name        TEXT NOT NULL,
    property_value       REAL NOT NULL,
    property_unit        TEXT,
    measurement_condition TEXT,
    FOREIGN KEY (obs_id) REFERENCES observations(obs_id)
);

-- ===== L3 文献来源 / 抽取溯源 =====
CREATE TABLE IF NOT EXISTS literature_sources (
    literature_id       INTEGER PRIMARY KEY AUTOINCREMENT,
    doi                 TEXT UNIQUE,
    title               TEXT,
    authors             TEXT,
    journal             TEXT,
    year                INTEGER,
    abstract            TEXT,
    pdf_path            TEXT,
    extraction_model    TEXT,
    extraction_version  TEXT,
    extraction_time     TIMESTAMP,
    raw_snippet         TEXT,                     -- 仅存数值性事实片段，不存整段原文
    created_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ===== 索引 =====
CREATE INDEX IF NOT EXISTS idx_polymer_abbr       ON polymers(abbr);
CREATE INDEX IF NOT EXISTS idx_polymorph_polymer ON polymorphs(polymer_id);
CREATE INDEX IF NOT EXISTS idx_obs_polymer       ON observations(polymer_id);
CREATE INDEX IF NOT EXISTS idx_obs_polymorph     ON observations(polymorph_id);
CREATE INDEX IF NOT EXISTS idx_obs_doi           ON observations(doi);
CREATE INDEX IF NOT EXISTS idx_obs_year          ON observations(ref_year);
CREATE INDEX IF NOT EXISTS idx_lit_doi           ON literature_sources(doi);
