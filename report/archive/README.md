# 归档（已废弃，勿提交）

这里的文件是 11-13 的中间产物，**不是最终版**：

- `DSAI5102_07_Report_v2.md` / `.pdf`：由 C 的 `report/DSAI5102_07_Report_draft.docx`（`ce7e53e`）转换、并由 A 填入两处数据后的版本。数字是**折划分缺陷修复之前**的（COIL-20 k=40/80 判为未复现）。
- `PLACEHOLDERS.md`：docx 里 9 处彩色占位符的台账（A 两处已填、B 两处缺图、C 五处成稿后填）。
- `media/`：从 docx 导出的 Figure 1 流程图。
- `DSAI5102_07_Report_draft.docx`：C 的 11-13 docx 原稿（`ce7e53e`）。2026-11-16 起以 md/PDF 为唯一真值，docx 停用。

最终版：正文 `report/DSAI5102_Group16_Report_V3.md`（C 维护），PDF `report/DSAI5102_Group16_Report.pdf`（A 渲染，17 页）。

生成命令（如需复现归档产物）：
```bash
.venv/bin/python scripts/docx_to_md.py report/DSAI5102_07_Report_draft.docx
.venv/bin/python scripts/build_report_pdf.py report/DSAI5102_07_Report_draft.md
```
