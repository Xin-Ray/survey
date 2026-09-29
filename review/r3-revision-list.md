# IoT-J 综述 第三轮修改清单（根据 Julia 2026-09-21 反馈）

## Context

Julia 的新反馈（`IEEE_IoT_Consolidated_Review_Comments.txt`，10 条 + 5 个最重要未解决问题）针对的是 Overleaf 上 `version2.1-shrink8 IOT/STmodel.tex` 的 8 页投稿版（2026-09-18 编译的 PDF）。她的核心顾虑：**12 篇 purposive 选出的研究能否支撑全文对整个领域的结论**。旧反馈（`feedback_iotsurvey.txt`，14 条）里仍需继续加强的是 #1 IoT 深度、#5 对比表完整性、#9 批判性评估、#10 安全/隐私、#11 数据集、#14 参考文献与语言。

已确定的三项决策（用户已确认）：
1. **样本扩到 ~20–24 篇**：从 363 条 rule-eligible 池中补 8–12 篇，优先补真正在 connected/IoT 系统上评估的研究（wearable、CGM、edge）。
2. **IEEE Xplore + Scopus 重新检索并记录计数**（有机构权限）。
3. **主文保持 8 页；完整表格放 Supplementary PDF**（IoT-J 允许）。

目标：下一轮只剩 minor。

---

## 现稿中已发现的具体问题（读 9/18 PDF 得到，逐条对应 Julia 意见）

| # | 位置 | 问题 | 改法 |
|---|---|---|---|
| a | §II 末段 + Fig.1 虚线框 | **已实测，两个数字都错**（Julia 第 2 条）：实际是 12 篇全部被 PubMed 收录、检索命中 **4** 篇（非 6）、其中 **3** 篇在 363 条内（非 1）；"the rest are indexed elsewhere" 不成立 | 按 `review/search/FINDINGS.md` §2 改写，逐篇给出未命中原因（4 篇缺空间词、2 篇未匹配 DL 块、1 篇缺健康词、1 篇命中但被规则 iii 排除）；同步 Fig.1 虚线框 |
| b | §V 首句 | "four domains from the past five years" 但含 2016 [34]、2020 [56] | 改为 "published 2016–2025" |
| c | Fig.2 "Section" 列 | Sensing 行写 §II、Communication 行写 §II, VIII（§II 是 Methodology） | 改为 §III 与 §III, VIII；全文 \ref 检查 |
| d | §III 倒数第二段 | "gap G7 in Section VIII" 但 §VIII 没有 G1–G7 编号 | §VIII 的 gap 段落加 G1–G8 编号（Measurement, Fusion, Explanation, Federation, World-model twins, Lifestyle, Harmonization, Safety），或删掉 G7 |
| e | Table II 标题/摘要/引言 | "Quantitative synthesis" 被 Julia 第 4 条点名 | 全部改为 "structured summary of reported quantitative evidence"（摘要 "We synthesize quantitative evidence" → "We give a structured summary of the quantitative evidence reported by…"；引言 "a quantitative synthesis" 同改） |
| f | Table II Deployment 列 | "Gateway feasible" / "Scanner-side (pruned)" 是作者推断（Julia 第 3 条） | 拆成两列：**Deployment (reported)** 与 **Placement (inferred, ours)**；表注写明推断规则 |
| g | Table II Nitski 行 + §V-A | "externally validated on a second registry (UHN)"（Julia 第 7 条：若用该队列调过模型不能叫 external） | 核对 Nitski et al. 2021 原文：若 UHN 用于 fine-tune/recalibration 则改为 "second-cohort evaluation after recalibration"；同样核 Kong "Two cohorts"、Lin & Luo "Two cohorts" |
| h | 摘要、§X 结论 | "spatial and environmental context often improves…"、"Attention based and hybrid architectures generally reported gains…" 写成了领域结论（Julia 第 10 条、第 5 个未解决问题） | 每处加 "in the N studies summarized here"；禁止 "consistently/generally" 跨研究比较 |
| i | §V-A、§VIII、§X | "no quantitative dietary study was surfaced by our search" 把样本缺失外推到全领域 | 改为 "none of the N selected studies… ; the rule-eligible pool was not exhaustively screened for dietary work" |
| j | Table I 标题 | "judged from each review's title and abstract"（Julia 第 6 条） | 全文精读最接近的 5–6 篇综述；每个 •/◦/– 标注依据（该综述的 §/Table），放 Supplement Table S0；主文 Table I 标题改为 "judged from full text; evidence in Supplement S0" |
| k | §VI Privacy 段 | "return encrypted updates" 暗示 FL 自带加密（Julia 第 9 条最后一点） | 改为 "return model updates (plain unless secure aggregation or encryption is added)"；加一句 FL ≠ privacy |
| l | 全文用词 | health care / healthcare 混用；organise/modelling 英式拼写；"action conditioned"、"attention based"、"privacy preserving"、"world model based" 未连字符 | 统一：healthcare、organize/modeling（美式）、action-conditioned、attention-based、privacy-preserving、world-model-based、spatiotemporal（不用 spatio-temporal，引用标题除外） |
| m | 缩写 | CGM, EEG, fMRI, CMR, DXA, EP, AL, MAE, RMSE, AUROC, iAUC, GRU, TCN, SVM, GCN, STGNN, ODE, MODMA, BRFSS, ACS, ADNI, NACC, SRTR, UHN, Health ABC 多处首次出现未定义 | 正文首次出现定义；Table II 表注加缩写表 |
| n | 参考文献 | [2][5][6][13][14][16][32][33][34][38] 缺 volume/issue/pages/article no.；[56] GluNet 作者 "J. Daniels" 不存在（真实：Li, Liu, **Zhu**, Herrero, Georgiou）；[54] MICN 无链接 | 用 `endnote/out_live/cache.json` 里的 Crossref 记录自动补全；改 GluNet 作者；MICN 加 OpenReview URL |
| o | Table I、Table II、Fig.1 | 正常缩放下过密（Julia 第 10 条） | 主文 Table II 减列（见下）；Fig.1 重画为单栏、≥8pt 字号；Table I 缩 Note 列 |
| p | §X 结论 | RQ1–RQ4 是隐含回答 | 显式写 "**RQ1.** … **RQ2.** … **RQ3.** … **RQ4.** …" 四段 |

---

## 修改清单（按优先级；P0 = Julia 的 5 个最重要未解决问题）

### P0-1 说明 12 篇→扩到 ~20–24 篇的选取逻辑（Julia #1，第 1 个未解决问题）
- 从 363 条 rule-eligible 记录里按**明确的抽样框**补 8–12 篇：每个 (data type × domain) 格至少 1 篇，**优先含真实 connected-device 评估**（wearable/CGM/edge 推理/联邦部署），以回应 #3。
- 在 §II 写出：(1) 抽样框（5 data types × 4 domains 的格）；(2) **saturation rule** 的停止条件（连续 k 篇不再新增 data type/model family/domain/IoT layer 即停）；(3) 每篇的 **inclusion reason**（一列，放 Supplement Table S1，主文 Table II 用一个字母码引用）。
- 全文把 "twelve/12" 改为新数 N；把 "sampled purposively for coverage" 改为 "purposively sampled illustrative set"，并在 §IX 保留局限说明。
- 为每篇新研究做数据提取（同 Table II 字段 + 新增字段，见 P0-4）。

### P0-2 检索可复现（Julia #2，第 2 个未解决问题）— **大部分已完成，见 `review/search/FINDINGS.md`**
- ✅ 原始检索串与筛选规则已从另一台机器恢复并验证（重跑 1,173/274/3/1,444 vs 论文 1,171/268/3/1,436，差值为 11 天新索引）
- ✅ IEEE Xplore 用同一套概念块记了计数：arm A **928**、arm B **274**（记录导出待免费 IEEE 账号）
- ✅ 已查明 **Scopus 无机构权限**（YU 图书馆 A–Z 列表 0 命中），§II 的三库声明必须改
- ⬜ 剩下：IEEE 记录导出 → 合并去重；Scopus 措辞定稿；检索串写进 §II（论文声称在 Fig.1，实际不存在）
- 记录 **backward/forward citation chasing**：起点（Table I 的综述）、工具（Crossref / OpenAlex cited-by）、得到的记录数——这是目前唯一还没有任何记录的来源。
- 写明 **单人筛选与提取**（single reviewer），以及人工复核的实际执行者与日期。
- 更新 Fig.1 为两库计数：Identified (PubMed 1,436 + IEEE Xplore 1,202 + citation chasing) → duplicates removed → screened → rule-excluded → eligible → sampled N。
- 检索串、日期、各库计数、去重方法全文放 Supplement S2（主文 Fig.1 只放合计 + 脚注给检索串）。

### P0-3 区分真实 IoT 部署与推断可行性（Julia #3，第 3 个未解决问题）
- Table II 拆 **Deployment (reported)** / **Placement (inferred)** 两列（上表 f）。
- 新增 **Evidence class** 列，四类：(A) deployed connected/IoT system；(B) clinical-device study；(C) longitudinal study relevant to IoT；(D) non-health methodological exemplar。
- §V 开头一句报告 **多少篇真正评估了 connected IoT 系统**（现 12 篇里约 2 篇：GluNet-CGM、Lim life-log）；扩样后更新。
- 若 A 类仍是少数：摘要与结论加限定 "most quantitative evidence comes from clinical-device and longitudinal studies rather than deployed connected-health systems"；标题保留但摘要第一句不再暗示已部署证据。

### P0-4 一致的研究质量 / 部署就绪评估（Julia #7 + #5，第 4 个未解决问题）
- 新建 **Supplement Table S3 — Quality assessment**，每篇研究一行，列：patient-level split? / temporal-site leakage risk / missing-data handling / external validation (真外部 vs recalibrated) / calibration / uncertainty / subgroup fairness / comparator strength (strong contemporary baseline?) / reproducibility (code/data) / clinical validation。用 ✓ / ◦ / – / n/r。
- 新建 **Supplement Table S4 — Full study table**：Table II 全部字段 + spatial & temporal resolution、sampling frequency、study duration、missing-data handling、privacy/security、latency/energy/bandwidth/model size、primary limitation。
- 主文 Table II 精简为：Study | Domain & data type | Evidence class | Dataset (n; access) | Model | Validation (with "within-cohort" 定义在表注) | Deployment reported / inferred | Task; metric | Baseline strength | Incl. reason code。
- §V 加一段 3–4 句的**横向质量结论**（例："N/M studies use patient-level splits; k report calibration; none reports latency"），数字从 S3 汇总。

### P0-5 结论收窄到证据范围（Julia #10，第 5 个未解决问题）
- 上表 e/h/i/p 全部执行；摘要、§I 贡献段、§V、§VIII、§X 逐句检查，每个 finding 加范围限定。
- §I "contribution" 段改成 **两到三条精确的 unique contribution**（Julia #6 最后一点），与 Table I 的 "This survey" 行一一对应。

### P1-6 Table I 证据强化（Julia #6）
- 上表 j；补充 Julia 点名的最强综述类别：IoT healthcare、human digital twins、edge intelligence、federated smart healthcare、spatiotemporal health modeling（现表已有 Chen/Amin/Nguyen/Wang；缺 IoT-healthcare 总览与 spatiotemporal-health 专门综述，各补 1 篇，用 Crossref/OpenAlex 找 2023–2026 高引）。
- 写明 Table I 的选取方法（检索 + citation chasing 中的 review 类记录，按主题覆盖挑选）。

### P1-7 网络、互操作、安全的结构化 IoT 处理（Julia #9；旧 #1、#10）
- §VIII "Networking directions" 改为小节 **VIII-B Communication substrate**：一张紧凑表（或 Supplement S5）比较 BLE / Wi-Fi / cellular-5G / LoRaWAN / MQTT / CoAP：typical data rate、latency、energy、range、适合的 sensing tier、对 sampling rate/packet loss/model-update cadence 的影响。
- 扩写 FHIR 与 IEEE 11073：各 2–3 句说明在 pipeline 哪一层、解决什么（schema vs device profile）。
- 新建 **Supplement Table S6 — Threats × layers**：行 = device / communication / edge / cloud / digital twin / world model；列 = confidentiality / integrity / availability / privacy / patient-safety；格内写 threat → protection（authentication, encryption, secure aggregation, poisoning defense, inference-attack defense, DP, non-IID FL）。主文 §VI–VII 保留一句指向。
- 上表 k（FL ≠ encryption/privacy）。

### P1-8 数据集与 benchmark 指南（Julia #8；旧 #11）
- 新建 **Supplement Table S7 — Public datasets**（从 Table II/S4 出现的数据集起：MODMA, OpenNeuro, UVA/Padova, BRFSS+ACS, ADNI, NACC, SRTR, Health ABC，再补 2–4 个 wearable/CGM 公开集）：population, modality, device, duration, sampling rate, spatial resolution, missingness, access, supported tasks, limitations。
- 三个 suitability 标记列：device-level IoT/edge evaluation；multisite validation & continual sync；digital-twin/intervention evaluation。
- 主文 §VIII 加一句："no established benchmark evaluates the full sensor-to-twin-to-decision pipeline"（确认仍成立后）。

### P1-9 语言、缩写、章节引用、可读性（Julia #10；旧 #14）
- 上表 b/c/d/l/m/o。
- 用脚本做三项自动检查（见 Verification）。

### P1-10 参考文献最终核对（Julia #10；旧 #14）
- 上表 n；扩样新增文献同样走 `endnote/bib2endnote.py` 验证（作者、DOI、卷期页）。
- 更新 EndNote 导出文件（RIS/XML）并重新发给 Julia。

---

## Supplementary 文档结构（新文件，单一来源）

- `version2.1-shrink8 IOT/supplement.tex`：独立 IEEEtran 文档，标题 "Supplementary Material for …"，`\input{supp-tables}`。
- `supp-tables.tex`：S0 Table I 判定依据；S1 inclusion reasons；S2 检索串/日期/各库计数/去重/引文追踪；S3 quality assessment；S4 full study table；S5 protocol comparison；S6 threats × layers；S7 datasets。
- 主文用 `\ifsubmission` 引用 "Supplement S3" 等；`STmodel-full.tex`（extended build）保持可编译（CLAUDE.md 的 `\ifsubmission\else` 规则不变；每个 `\ref` 两个 build 都要能解析）。
- 参考文献：supplement 单独 `\bibliography{newST}`，编号会与主文不同 → supplement 表里同时给 bibkey 或首作者+年份，避免读者对不上。

## 执行顺序（建议）

1. 先做 P0-2 的检索重跑（IEEE Xplore/Scopus 通过已登录 Chrome；导出计数与 CSV），因为 P0-1 的补样要从合并后的池里抽。
2. P0-1 补样 + 数据提取（S4/S3 字段一次提完）。
3. 改 Table II / Fig.1 / §II / §V / §IX（P0-3、P0-4、P0-5）。
4. Supplement 建文件、填 S0–S7；主文瘦身回 8 页。
5. P1-6、P1-7、P1-8 文字与小表。
6. P1-9 语言/缩写/引用脚本检查；P1-10 参考文献；重新导出 EndNote。
7. 写 response-to-comments（逐条对 Julia 的 10 条 + 5 个问题，标注改在哪一节/哪张表）。

## Verification

- Overleaf 编译主文：0 error，`Output written … 8 pages`；`STmodel-full.tex` 与 `supplement.tex` 均能编译（本机无 TeX，用 Overleaf）。
- 脚本检查（本地 Python，对下载的 tex）：
  - 术语一致性 grep：`health care|spatio-temporal|organis|modelling|action conditioned|attention based|privacy preserving|world model based`（引用标题除外）应为 0。
  - 缩写首次出现检查：对上表 m 的列表，确认首次出现处带全称。
  - 章节引用检查：Fig.2 Section 列与 `\label` 对应；无 "G7" 类未定义引用。
  - 数字一致性：Fig.1 计数 = §II 正文 = Supplement S2；"N studies" 全文一致；"k of N" 类句子由 S3/S4 汇总脚本生成。
- 参考文献：`python3 endnote/bib2endnote.py --bib <新 bib> --tex <STmodel.tex> --out out_r3 --overrides endnote/overrides.json` → 0 AUTHOR-MISMATCH / DOI-TITLE-MISMATCH，partial 逐条人工确认。
- Table II/S4 每个数值对照原文核对一次（尤其新增研究和 Nitski 的 validation 描述）。
- 对照 Julia 10 条逐条自检：每条能指出对应的节/表/图。

## 需要你提供 / 确认的信息

- ✅ 脚本与日志已找到（Windows 机器 `D:\xxiangworking\...\New_version\search\`），并已验证；`review/20w.md` 不存在，真实文件是 `review_stmodel.md` 与 `review/2026-09-15-nobel-overleaf-review.md/.csv`
- ⬜ **那 60 条人工复核当初是 AI 判的，不是人判的**（见 `FINDINGS.md` §3）。二选一：你亲自重判同一批 60 条（`review/search/handcheck/`），或删掉 precision 与 ≈260 估计
- ⬜ Scopus：2026-09-11 那次到底有没有跑过（YU 无权限；若无则从来源里去掉）
- ⬜ Nitski 2021 是否用 UHN 队列做过 recalibration（决定能否写 external validation）
