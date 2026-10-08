"""Hidden tests for Part 1, Exercise 1 (mask_invalid_samples).

This file lives under test/, which the TMC Python3 plugin always treats as
non-student content (see docs/README.md in this repo) - students only see
src/__main__.py, never this file's contents.
"""

import unittest

import numpy as np
from tmc import points

from src.__main__ import mask_invalid_samples


class MaskInvalidSamplesTest(unittest.TestCase):
    @points("1.1")
    def test_removes_nans(self):
        raw = np.array([1.0, np.nan, 2.5, np.nan, 3.25])
        result = mask_invalid_samples(raw)
        np.testing.assert_array_equal(result, np.array([1.0, 2.5, 3.25]))

    @points("1.1")
    def test_no_nans_returns_all_values(self):
        raw = np.array([4.0, 5.0, 6.0])
        result = mask_invalid_samples(raw)
        np.testing.assert_array_equal(result, raw)

    @points("1.2")
    def test_all_nans_returns_empty(self):
        raw = np.array([np.nan, np.nan])
        result = mask_invalid_samples(raw)
        self.assertEqual(result.size, 0)

    @points("1.2")
    def test_preserves_order(self):
        raw = np.array([3.0, np.nan, 1.0, np.nan, 2.0])
        result = mask_invalid_samples(raw)
        np.testing.assert_array_equal(result, np.array([3.0, 1.0, 2.0]))


if __name__ == "__main__":
    unittest.main()
