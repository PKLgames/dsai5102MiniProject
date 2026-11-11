# C 交付标准（报告 / slides 发出前必过）

> 两条门：**S5**（11-21 23:59 报告）与 **S6**（11-24 12:00 slides）。每条都能验，验不过不发。

## S5 · 报告

```bash
cd /home/pklgames/coding/dsai5102MiniProject
grep -rn "{{" report/ || echo "no placeholder"
python scripts/similarity_check.py              # 8-gram 与原文重合率
grep -c "D1\|D3\|D9\|D18" report/*.tex 2>/dev/null || true   # 偏离附录是否覆盖关键条目
```

- [ ] **六节齐全**：引言/被复现论文、方法、我们的实现、结果、诊断与偏离、结论与局限 + 数据来源与预处理 + 贡献声明
- [ ] `grep "{{"` 为空；报告中每个数字都能在 `results/README_numbers.md` 找到同名行
- [ ] 表 1–4、Fig.1–3 全部就位；Fig.1 自绘；Fig.2/3 与 csv 数值一致（随机抽 3 点核对）
- [ ] 8-gram 重合率 **<5%**（跑两次，取高的那次也 <5%）
- [ ] 引用：`[1]` arXiv:1802.03426 与 `[2]` NRMP 4:82 并列且关系说明正确；无「预印本=正式版」表述
- [ ] 数字旁有 `n_folds`；有 transductive 说明；无稳定性/九数据集/热力图等未做内容被写成已复现
- [ ] 附录 A 含 D1–D18 且每行有影响方向；附录 B 有环境+命令+实测时长
- [ ] 贡献声明三人各一段，能对到 commit/文件；AI 使用已披露
- [ ] 篇幅 6–8 页（不含附录），§3 ≤2 页
- [ ] 命名 `report/DSAI5102_<GroupID>_Report.pdf`，A 已复核数字（≥24 h 前）

## S6 · Slides

- [ ] 8 页、一条逻辑线（标题+结论 → 问题 → 方法 → 设置 → 主结果 → 差异 → 原因 → 结论）
- [ ] 每页 ≤6 行、字号 ≥24pt、无代码截图；第 5 页只有一个结论
- [ ] 第 7 页讲了 D3/D9 的偏差方向
- [ ] 彩排 ≥2 次记录在 `slides/rehearsal.md`；第 1 次 ≤5:00；实测 6:00 内讲完
- [ ] slides 里每个数字与报告一致（A 抽查 10 处）
- [ ] 命名 `slides/DSAI5102_<GroupID>_Slides.pdf`

## 对照评分表自查

| 维度 | 自检问题 |
|---|---|
| Completeness | 数据 / 方法 / 结果三块，每块能指到具体表、图、文件？ |
| Methodology | 划分、种子、指标、对照、阈值（SPEC §5）都写清了？每个偏差都有影响方向？ |
| Novelty | 自研实现 + 与原文差距的归因（D9）是否说出了**为什么**，而不只是「我们没复现」？ |
| Team | 贡献声明可核查？交接记录（`docs/log/HANDOFF_LOG.md`）被引用？ |
| Slides | 6 分钟讲得完？每页 ≤6 行？ |
| Time | 报告 11-21 23:59、slides 11-24 12:00 前提交？ |
