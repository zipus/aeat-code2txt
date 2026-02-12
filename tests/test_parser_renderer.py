import unittest
from decimal import Decimal
from pathlib import Path

from aeat_code2txt.formulas import evaluate_formula
from aeat_code2txt.layout import Field, RecordLayout
from aeat_code2txt.parser import parse_layout_file
from aeat_code2txt.renderer import render_record
from aeat_code2txt.reverse import parse_report, validate_report


class ParserRendererTestCase(unittest.TestCase):
    def test_parse_layout_file_extracts_code_and_formula(self):
        csv_path = Path(__file__).resolve().parents[1] / "csv_x2c" / "DP30303.csv"
        record = parse_layout_file(csv_path)
        codes = {field.code for field in record.fields if field.code}
        self.assertIn("59", codes)

        formula_fields = [f for f in record.fields if f.formula]
        self.assertTrue(formula_fields)
        self.assertTrue(any("[46]" in f.formula for f in formula_fields))

    def test_formula_evaluation(self):
        values = {"1": Decimal("10"), "2": Decimal("3"), "3": Decimal("2")}
        result = evaluate_formula("[1] + [2] - [3]", values)
        self.assertEqual(result, Decimal("11"))

    def test_render_record_length(self):
        fields = [
            Field(
                number=1,
                position=1,
                length=2,
                raw_type="An",
                description="Const",
                validation="",
                content="Constante \"AA\"",
                const_value="AA",
                key="const",
            ),
            Field(
                number=2,
                position=3,
                length=5,
                raw_type="Num",
                description="Code [01]",
                validation="",
                content="",
                code="01",
                decimals=2,
                key="01",
            ),
        ]
        record = RecordLayout(name="TEST", fields=fields)
        rendered = render_record(record, amounts={"01": Decimal("12.34")})
        self.assertEqual(len(rendered), record.length())
        self.assertTrue(rendered.startswith("AA"))

    def test_reverse_parse_and_validate(self):
        fields = [
            Field(
                number=1,
                position=1,
                length=2,
                raw_type="An",
                description="Const",
                validation="",
                content="Constante \"AA\"",
                const_value="AA",
                key="const",
            ),
            Field(
                number=2,
                position=3,
                length=5,
                raw_type="Num",
                description="Code [01]",
                validation="",
                content="",
                code="01",
                decimals=2,
                key="01",
            ),
        ]
        record = RecordLayout(name="TEST", fields=fields)
        text = render_record(record, amounts={"01": Decimal("12.34")})
        report = type("Report", (), {"records": [record]})
        data = parse_report(text, report)
        self.assertEqual(data["01"], "01234")
        issues = validate_report(text, report)
        self.assertEqual(issues, [])


if __name__ == "__main__":
    unittest.main()
