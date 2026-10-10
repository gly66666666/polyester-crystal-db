#!/usr/bin/env python3
r"""把 oa_survey.json 的统计结果渲染成论文用的完整 LaTeX 表格

目的：论文中的数字必须由实测数据生成，杜绝手抄与四舍五入口径不一致。
输出为**完整的 table 环境**（而非片段），避免在 tabularx 环境内
用 \input 引入片段所引发的 "Misplaced \noalign" 问题。

用法：
  python src/annotation/make_oa_table.py            # 写入 paper/tab_oa.tex
  python src/annotation/make_oa_table.py --stdout
"""

from __future__ import annotations

import argparse
import collections
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
PROJECT_ROOT = HERE.parents[1]
SRC = PROJECT_ROOT / "data" / "processed" / "oa_survey.json"
OUT = PROJECT_ROOT / "paper" / "tab_oa.tex"

LABEL = {
    "closed": ("\\texttt{closed}", "无合法开放获取版本，须机构订阅 / 馆际互借 / 人工获取"),
    "oa_landing": ("\\texttt{oa\\_landing}", "判定为 OA，但链接为出版商落地页或 HTML，无法自动下载"),
    "oa_pdf": ("\\texttt{oa\\_pdf}", "给出 \\texttt{url\\_for\\_pdf} 且实际取回内容为 PDF，可自动下载"),
    "query_failed": ("\\texttt{query\\_failed}", "Unpaywall 查询失败，不计入结论"),
}
ORDER = ["closed", "oa_landing", "oa_pdf", "query_failed"]


def render(rows: list[dict]) -> str:
    c = collections.Counter(r.get("status") for r in rows)
    n = len(rows)
    ok_n = n - c.get("query_failed", 0)
    is_oa_n = sum(1 for r in rows if r.get("is_oa"))
    polys = sorted({r.get("polymer_abbr") for r in rows if r.get("polymer_abbr")})
    per = n // max(len(polys), 1)

    lines = [
        "\\begin{table}[htbp]",
        "\\centering",
        f"\\caption{{全文可获取性分层抽样实测（{len(polys)} 个成员分层抽样，"
        f"每成员取前 {per} 条高相关候选，共 $n={n}$）}}",
        "\\label{tab:oa}",
        "\\begin{tabularx}{\\textwidth}{l c c X}",
        "\\toprule",
        "状态 & 条数 & 占比 & 含义\\\\",
        "\\midrule",
    ]
    for k in ORDER:
        if c.get(k):
            lbl, desc = LABEL[k]
            lines.append(f"{lbl} & {c[k]} & {c[k]/n*100:.1f}\\% & {desc} \\\\")
    lines.append("\\midrule")
    lines.append(
        f"\\multicolumn{{4}}{{p{{0.94\\textwidth}}}}{{\\footnotesize "
        f"样本 {n} 条；Unpaywall 查询成功 {ok_n} 条。"
        f"判定为开放获取（\\texttt{{is\\_oa}}=true）共 {is_oa_n} 条"
        f"（占查询成功样本 {is_oa_n/max(ok_n,1)*100:.1f}\\%），"
        f"其中可自动下载全文 PDF 的 {c.get('oa_pdf',0)} 条。}}\\\\"
    )
    lines += ["\\bottomrule", "\\end{tabularx}", "\\end{table}"]
    return "\n".join(lines)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--stdout", action="store_true")
    args = ap.parse_args()
    rows = json.loads(SRC.read_text(encoding="utf-8"))
    tex = render(rows)
    if args.stdout:
        print(tex)
    else:
        OUT.parent.mkdir(parents=True, exist_ok=True)
        OUT.write_text(tex + "\n", encoding="utf-8")
        print(f"已写入 {OUT}")


if __name__ == "__main__":
    main()
