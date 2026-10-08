import unittest
from pathlib import Path

import pandas as pd

from sales_logic import follow_ups_due, next_lead_id, prepare_leads, summary_metrics, to_csv_bytes

SAMPLE = Path(__file__).resolve().parents[1] / "data" / "sample_leads.csv"


class SalesLogicTests(unittest.TestCase):
    def setUp(self):
        self.leads = prepare_leads(pd.read_csv(SAMPLE))

    def test_metrics(self):
        m = summary_metrics(self.leads)
        self.assertEqual(m["total_leads"], 12)
        self.assertEqual(m["won_deals"], 2)
        self.assertEqual(m["won_revenue"], 215000.0)
        self.assertAlmostEqual(m["conversion_rate"], 16.6666666667)
        self.assertEqual(m["open_pipeline"], 1345000.0)

    def test_overdue_excludes_closed(self):
        due = follow_ups_due(self.leads, pd.Timestamp("2026-10-08"))
        self.assertEqual(set(due["lead_id"]), {"L001", "L002", "L007", "L010"})

    def test_new_id(self):
        self.assertEqual(next_lead_id(self.leads), "L013")

    def test_roundtrip_csv(self):
        from io import BytesIO
        restored = prepare_leads(pd.read_csv(BytesIO(to_csv_bytes(self.leads))))
        self.assertEqual(len(restored), 12)

    def test_rejects_negative_deal_value(self):
        invalid = pd.read_csv(SAMPLE)
        invalid.loc[0, "deal_value"] = -1
        with self.assertRaises(ValueError):
            prepare_leads(invalid)


if __name__ == "__main__":
    unittest.main()
