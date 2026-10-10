#!/usr/bin/env python3
"""数据库初始化脚本（任务6）

- 读取并执行 src/database/schema.sql 建表
- 向 polymers 表写入 12 个聚酯家族 Tier1 成员
- DB 路径：项目根目录 / data / polymer_crystal.db（与脚本位置无关，可任意 CWD 运行）

注意：cru_smiles 初版留空，将在抽取阶段用 RDKit 归一化后回填，避免手写 SMILES 引入错误。
CAS 号不在此写入（指南原稿中多个 CAS 为误填，统一留待核验后再补）。
"""

from pathlib import Path
import sqlite3
import sys

# 以本文件位置反推项目根目录（…/polyester-crystal-db）
HERE = Path(__file__).resolve().parent          # …/src/database
PROJECT_ROOT = HERE.parents[1]                  # …/polyester-crystal-db
SCHEMA_PATH = HERE / "schema.sql"
DB_PATH = PROJECT_ROOT / "data" / "polymer_crystal.db"

# (abbr, name_en, name_zh, family_branch, repeat_unit_mw, has_chiral_center, tacticity_policy, tier)
POLYESTER_TIER1 = [
    ("PET",  "Poly(ethylene terephthalate)",            "聚对苯二甲酸乙二醇酯", "aromatic",   192.17, 0, "N.A.",        1),
    ("PBT",  "Poly(butylene terephthalate)",            "聚对苯二甲酸丁二醇酯", "aromatic",   220.22, 0, "N.A.",        1),
    ("PEN",  "Poly(ethylene naphthalate)",              "聚萘二甲酸乙二醇酯",   "aromatic",   240.21, 0, "N.A.",        1),
    ("PLA",  "Poly(lactic acid)",                       "聚乳酸",               "aliphatic",   72.06, 1, "isotactic",  1),
    ("PGA",  "Poly(glycolic acid)",                     "聚乙醇酸",             "aliphatic",   58.04, 0, "N.A.",        1),
    ("PTT",  "Poly(trimethylene terephthalate)",         "聚对苯二甲酸丙二醇酯", "aromatic",   206.20, 0, "N.A.",        1),
    ("PBN",  "Poly(butylene naphthalate)",              "聚萘二甲酸丁二醇酯",   "aromatic",   254.24, 0, "N.A.",        1),
    ("PCL",  "Poly(ε-caprolactone)",                    "聚己内酯",             "aliphatic",  114.14, 0, "N.A.",        1),
    ("PBS",  "Poly(butylene succinate)",                "聚丁二酸丁二醇酯",     "aliphatic",  172.18, 0, "N.A.",        1),
    ("PBSA", "Poly(butylene succinate-co-adipate)",      "聚丁二酸-己二酸丁二醇酯","copolyester", None,   0, "N.A.",        1),
    ("PHB",  "Poly(hydroxybutyrate)",                    "聚羟基丁酸酯",         "aliphatic",   86.09, 1, "isotactic",  1),
    ("PHBV", "Poly(hydroxybutyrate-co-valerate)",        "聚(羟基丁酸-co-羟基戊酸)","copolyester", None,   1, "N.A.",        1),
]


def init_database() -> None:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.executescript(SCHEMA_PATH.read_text(encoding="utf-8"))

    cur.executemany(
        """
        INSERT OR IGNORE INTO polymers
            (abbr, name_en, name_zh, family_branch, cru_smiles,
             repeat_unit_mw, has_chiral_center, tacticity_policy, tier)
        VALUES (?, ?, ?, ?, NULL, ?, ?, ?, ?)
        """,
        POLYESTER_TIER1,
    )

    conn.commit()

    n_poly = cur.execute("SELECT COUNT(*) FROM polymers").fetchone()[0]
    conn.close()

    print(f"✓ 数据库初始化完成: {DB_PATH}")
    print(f"✓ 已写入 {n_poly} 个聚合物成员（Tier1）")


if __name__ == "__main__":
    try:
        init_database()
    except Exception as e:
        print(f"✗ 初始化失败: {e}", file=sys.stderr)
        sys.exit(1)
