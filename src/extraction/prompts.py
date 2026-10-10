#!/usr/bin/env python3
"""抽取 prompt 与输出合约（对齐执行计划 §4.2）

输出合约（LLM 必须只输出一个 JSON 对象，字段含义与单位见下）：
- polymer_abbr:        聚合物缩写（PET/PTT/PBT/PLA/...），必须属于已知家族成员
- polymorph_label:     晶型标签（triclinic / alpha / beta / alpha_prime / sc ...），未知填 null
- crystal_system:      晶系（triclinic/monoclinic/orthorhombic/hexagonal），未知填 null
- space_group:         空间群（如 P-1 / P212121），未知填 null
- a_A, b_A, c_A:       晶胞边长，单位 Å（埃）
- alpha_deg, beta_deg, gamma_deg: 晶系角，单位 °（度）
- z:                   每晶胞重复单元数（整数）
- rho_crystal_gcm3:    晶体密度，单位 g/cm³
- fiber_period_A:      纤维恒等周期 / 链轴长度，单位 Å
- chain_conformation:  链构象（如 tggt），未知填 null
- t_c_celsius:         结晶温度，单位 °C
- tm_celsius:          熔点，单位 °C
- tm0_celsius:         平衡熔点，单位 °C
- tg_celsius:          玻璃化转变温度，单位 °C
- delta_hf_jg:         熔融焓，单位 J/g
- xtallinity_pct:      结晶度，单位 %
- growth_rate_nms:     球晶径向生长速率，单位 nm/s
- long_period_nm:      SAXS 长周期，单位 nm
- lamellar_thickness_nm: 片晶厚度，单位 nm
- avrami_n, avrami_k:  Avrami 参数
- t_half_min:          半结晶时间，单位 min
- mw_gmol, mn_gmol:    数均/重均分子量，单位 g/mol
- pdi:                 多分散指数 Mw/Mn
- anneal_t_celsius, anneal_time_h: 退火温度/时间
- draw_ratio, cooling_rate, cryst_route: 加工/热历史
- evidence:            原始出处定位（表号/图号 + 简短数值上下文），≤200 字符
- confidence:          自评置信度 0–1（浮点）
- unknown_fields:      本记录中"无法确定/原文未给"的字段名列表，必须显式列出

三条硬规则（写进 system prompt）：
1. 宁可 null 不许编：任何拿不准的数值必须填 null 并列入 unknown_fields，禁止插值或猜测。
2. 置信度必须自评；低于 0.7 视为不可信，将进入人工复核队列。
3. 每条必须能回溯到原文（evidence 写清表/图号）；无出处定位不得编造数值。
"""

SYSTEM_PROMPT = """你是一名高分子晶体学数据抽取专家。任务：从给定文献文本中抽取聚酯家族聚合物的晶体结构与热/动力学实测数据。

硬性规则：
1. 只输出一个 JSON 对象，不要任何解释、不要 Markdown 代码块包裹。JSON 字段严格遵循下方"输出合约"。
2. 宁可返回 null，也绝对不要编造或插值数值。凡是原文没有给出、或你无法从文本确定具体数值的字段，填 null，并把字段名加入 unknown_fields 列表。unknown_fields 必须如实列出所有未确定的字段。
3. 对每个字段自评置信度 confidence（0–1 浮点）。如果你对整条记录把握很低，就把 confidence 设低（如 <0.7）。
4. evidence 字段必须写明该数值在原文中的定位（表号/图号），例如 "Table 2 (unit cell)" 或 "Fig. 3 DSC, Tm=255°C"。不得超过 200 字符，且仅写与数值相关的简短上下文，不得大段复制原文。
5. 单位已通过字段后缀固定（_A=Å, _deg=°, _gcm3=g/cm³, _celsius=°C, _jg=J/g, _pct=%, _nms=nm/s, _nm=nm, _min=min, _gmol=g/mol）。不要换算单位，按原文给出的数值与单位如实填入对应字段。

输出合约字段（全部可选，给不出就 null）：
polymer_abbr, polymorph_label, crystal_system, space_group,
a_A, b_A, c_A, alpha_deg, beta_deg, gamma_deg, z, rho_crystal_gcm3,
fiber_period_A, chain_conformation, t_c_celsius, tm_celsius, tm0_celsius,
tg_celsius, delta_hf_jg, xtallinity_pct, growth_rate_nms, long_period_nm,
lamellar_thickness_nm, avrami_n, avrami_k, t_half_min, mw_gmol, mn_gmol,
pdi, anneal_t_celsius, anneal_time_h, draw_ratio, cooling_rate, cryst_route,
evidence, confidence, unknown_fields
"""


def build_user_prompt(polymer_abbr: str, text: str, polymorph_hint: str = "") -> str:
    hint = f"\n已知该文献聚焦的聚合物为 {polymer_abbr}（晶型提示：{polymorph_hint}）。" if polymorph_hint else \
           f"\n请重点抽取与聚合物 {polymer_abbr} 相关的晶体数据；若文献涉及多个成员，只抽取 {polymer_abbr} 的部分。"
    # 截断超长文本，避免超出上下文（deepseek-v4-flash 1M 上下文足够，但 PDF 全文可能极长）
    max_chars = 60000
    if len(text) > max_chars:
        text = text[:max_chars] + "\n...[截断]..."
    return (
        f"请从以下文献文本中抽取晶体学/热力学数据。{hint}\n\n"
        f"===== 文献文本开始 =====\n{text}\n===== 文献文本结束 =====\n\n"
        f"按 system 指令输出 JSON。"
    )


# contract 字段 → (schema 列名, 是否整数)
FIELD_MAP = {
    "polymer_abbr": ("polymer_abbr", False),
    "polymorph_label": ("polymorph_label", False),
    "crystal_system": ("crystal_system", False),
    "space_group": ("space_group", False),
    "a_A": ("a", False), "b_A": ("b", False), "c_A": ("c", False),
    "alpha_deg": ("alpha", False), "beta_deg": ("beta", False), "gamma_deg": ("gamma", False),
    "z": ("z", True),
    "rho_crystal_gcm3": ("rho_crystal", False),
    "fiber_period_A": ("fiber_period", False),
    "chain_conformation": ("chain_conformation", False),
    "t_c_celsius": ("t_c", False),
    "tm_celsius": ("tm", False), "tm0_celsius": ("tm0", False), "tg_celsius": ("tg", False),
    "delta_hf_jg": ("delta_hf", False),
    "xtallinity_pct": ("xtallinity_pct", False),
    "growth_rate_nms": ("growth_rate", False),
    "long_period_nm": ("long_period", False),
    "lamellar_thickness_nm": ("lamellar_thickness", False),
    "avrami_n": ("avrami_n", False), "avrami_k": ("avrami_k", False), "t_half_min": ("t_half", False),
    "mw_gmol": ("mw", False), "mn_gmol": ("mn", False), "pdi": ("pdi", False),
    "anneal_t_celsius": ("anneal_t", False), "anneal_time_h": ("anneal_time_h", False),
    "draw_ratio": ("draw_ratio", False), "cooling_rate": ("cooling_rate", False),
    "cryst_route": ("cryst_route", False),
}
