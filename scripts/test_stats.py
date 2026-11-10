#!/usr/bin/env python3
"""Testes das contas do calendário e do parser do HTML público."""

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fetch_contributions import parse_calendar
from stats import best_day, monthly, parse_count, streaks

HTML = """
<h2>412 contributions in the last year</h2>
<table>
<td data-date="2026-11-07" id="contribution-day-component-6-0" data-level="0"></td>
<tool-tip for="contribution-day-component-6-0">No contributions on November 7th.</tool-tip>
<td data-date="2026-11-08" id="contribution-day-component-0-1" data-level="2"></td>
<tool-tip for="contribution-day-component-0-1">4 contributions on November 8th.</tool-tip>
<td data-date="2026-11-09" id="contribution-day-component-1-1" data-level="1"></td>
<tool-tip for="contribution-day-component-1-1">1 contribution on November 9th.</tool-tip>
<td data-date="2026-11-10" id="contribution-day-component-2-1" data-level="0"></td>
<tool-tip for="contribution-day-component-2-1">No contributions on November 10th.</tool-tip>
</table>
"""


class StatsTest(unittest.TestCase):
    def test_parse_count(self):
        self.assertEqual(parse_count("No contributions on November 9th."), 0)
        self.assertEqual(parse_count("1 contribution on November 9th."), 1)
        self.assertEqual(parse_count("  12   contributions on May 2nd. "), 12)

    def test_calendar_html(self):
        days, reported = parse_calendar(HTML)
        self.assertEqual(reported, 412)
        self.assertEqual([d["date"] for d in days], ["2026-11-07", "2026-11-08", "2026-11-09", "2026-11-10"])
        self.assertEqual(days[1]["count"], 4)
        self.assertEqual(days[1]["row"], 0)
        self.assertEqual(days[1]["col"], 1)

    def test_streak_skips_trailing_empty_day(self):
        days = [
            {"count": 0},
            {"count": 2},
            {"count": 1},
            {"count": 0},
        ]
        self.assertEqual(streaks(days), (2, 2))

    def test_streak_breaks(self):
        days = [{"count": c} for c in (1, 1, 0, 1, 0, 0)]
        self.assertEqual(streaks(days), (0, 2))

    def test_monthly_and_best(self):
        days = [
            {"date": "2026-10-30", "count": 2},
            {"date": "2026-11-01", "count": 5},
            {"date": "2026-11-02", "count": 1},
        ]
        months = monthly(days, n=3)
        self.assertEqual([m["month"] for m in months], ["2026-09", "2026-10", "2026-11"])
        self.assertEqual(months[-1]["total"], 6)
        self.assertEqual(best_day(days)["date"], "2026-11-01")


if __name__ == "__main__":
    unittest.main()
