#!/usr/bin/env python3
"""检查管理层研究纪律写进了规范源和消费入口。

这里不给任何人打分，也不把分数换成估值。仓库没有读取管理层判断的运行时算法。
"""
from pathlib import Path
import subprocess
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
CANON = ROOT / "skills" / "management-deep-dive.md"

CONSUMERS = (
    "skills/investment-research.md",
    "skills/investment-checklist.md",
    "skills/investment-team.md",
    "skills/earnings-review.md",
    "skills/earnings-team.md",
    "skills/thesis-tracker.md",
    "skills/thesis-drift.md",
    "skills/deep-company-series.md",
)

EVIDENCE_FIELDS = (
    "事件ID",
    "表述与来源",
    "当时信息",
    "类别",
    "承认的问题",
    "归因",
    "实施状态",
    "代价",
    "反证",
    "复核",
    "证据可信度",
    "归责",
)

DUTIES = {
    "skills/investment-research.md": ("估值衔接", "再高增长五年", "维持原假设"),
    "skills/investment-checklist.md": ("不计算加权平均", "未知不是 1 星"),
    "skills/investment-team.md": ("不是管理层四项的加权平均",),
    "skills/earnings-review.md": ("指引未达到本身不是不诚信", "维持原假设"),
    "skills/earnings-team.md": ("不换算成诚信星级", "维持原假设"),
    "skills/thesis-tracker.md": ("未知的管理层事件不计入破裂或成立", "不改原预测"),
    "skills/thesis-drift.md": ("四项方向可以不同", "维持原假设"),
    "skills/deep-company-series.md": ("兑现率不是诚信分",),
}


class ManagementDisciplineTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.canon = CANON.read_text(encoding="utf-8")

    def test_canonical_sections_and_fields(self):
        for heading in (
            "## 规范地位与执行边界",
            "## 管理层证据记录",
            "## 四项判断与诚信门槛",
            "## 估值衔接",
        ):
            self.assertIn(heading, self.canon)
        for field in EVIDENCE_FIELDS:
            self.assertIn(field, self.canon)
        for stage in ("口头反思", "具体诊断", "已执行改变", "跨事件复核"):
            self.assertIn(stage, self.canon)

    def test_scores_are_discipline_not_a_runtime_model(self):
        self.assertIn("主观研究纪律", self.canon)
        self.assertIn("加权不再计算", self.canon)
        self.assertIn("不读取管理层分数", self.canon)
        self.assertIn("不会把学习成熟度", self.canon)
        self.assertNotIn("| 诚信度 | 35% |", self.canon)
        self.assertNotIn('三个都是"是"', self.canon)
        self.assertNotIn("优秀——说到做到", self.canon)
        for tool in ("tools/financial_rigor.py", "tools/terminal_value.py"):
            text = (ROOT / tool).read_text(encoding="utf-8")
            self.assertNotIn("诚信门槛", text)
            self.assertNotIn("学习成熟度", text)

    def test_unknown_rumor_and_integrity_stay_distinct(self):
        for gate in ("不可投", "未证实", "未知", "可研究"):
            self.assertIn(gate, self.canon)
        self.assertIn("未知不代入 1 分", self.canon)
        self.assertIn("不自动定罪，也不自动放行", self.canon)
        self.assertIn("计数不是诚信分", self.canon)
        self.assertIn("虚构", self.canon)
        self.assertNotIn("王宁", self.canon)
        self.assertNotIn("泡泡玛特", self.canon)

    def test_valuation_bridge_blocks_double_counting(self):
        self.assertIn("同一条优势不得同时上调增长", self.canon)
        self.assertIn("维持原假设", self.canon)
        self.assertIn("不得提高折现率", self.canon)
        self.assertIn("更慢的增长", self.canon)

    def test_consumers_follow_the_same_source(self):
        for relative, duties in DUTIES.items():
            text = (ROOT / relative).read_text(encoding="utf-8")
            self.assertIn("skills/management-deep-dive.md", text, relative)
            self.assertIn("诚信门槛", text, relative)
            for duty in duties:
                self.assertIn(duty, text, relative)
        for relative in CONSUMERS:
            self.assertIn(relative, DUTIES)

    def test_generated_codex_skill_matches_source(self):
        result = subprocess.run(
            [sys.executable, "scripts/sync-codex-skills.py", "--check"],
            cwd=ROOT,
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        generated = (ROOT / "codex-skills/management-deep-dive/SKILL.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("## 管理层证据记录", generated)
        prompt = (ROOT / "codex-prompts/management-deep-dive.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("management-deep-dive", prompt)
        self.assertNotIn("35%", prompt)


if __name__ == "__main__":
    unittest.main()
