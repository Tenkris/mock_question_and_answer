import unittest

from superman import max_chickens_under_roof


class MaxChickensUnderRoofTests(unittest.TestCase):
    def test_example_case(self) -> None:
        positions = [2, 5, 10, 12, 15]
        self.assertEqual(max_chickens_under_roof(positions, 5), 2)

    def test_all_chickens_fit_under_roof(self) -> None:
        positions = [1, 2, 3]
        self.assertEqual(max_chickens_under_roof(positions, 5), 3)

    def test_zero_or_negative_roof_length(self) -> None:
        positions = [0, 1, 2]
        self.assertEqual(max_chickens_under_roof(positions, 0), 0)
        self.assertEqual(max_chickens_under_roof(positions, -1), 0)

    def test_duplicate_positions(self) -> None:
        positions = [4, 4, 4, 7]
        self.assertEqual(max_chickens_under_roof(positions, 1), 3)

    def test_half_open_interval_behavior(self) -> None:
        positions = [0, 5]
        self.assertEqual(max_chickens_under_roof(positions, 5), 1)

    def test_sparse_distribution(self) -> None:
        positions = [0, 1, 2, 3, 10]
        self.assertEqual(max_chickens_under_roof(positions, 4), 4)

    def test_empty_positions(self) -> None:
        self.assertEqual(max_chickens_under_roof([], 5), 0)

    def test_single_chicken(self) -> None:
        self.assertEqual(max_chickens_under_roof([7], 3), 1)

    def test_large_roof_covers_all(self) -> None:
        positions = [-2, 0, 1, 5]
        self.assertEqual(max_chickens_under_roof(positions, 10), 4)

    def test_negative_coordinates(self) -> None:
        positions = [-10, -5, -1]
        self.assertEqual(max_chickens_under_roof(positions, 5), 2)

    def test_adjacent_points_excluded_by_half_open(self) -> None:
        positions = [0, 1, 1, 2]
        self.assertEqual(max_chickens_under_roof(positions, 1), 2)

    def test_many_duplicates_with_far_point(self) -> None:
        positions = [0, 0, 0, 0, 10]
        self.assertEqual(max_chickens_under_roof(positions, 1), 4)


if __name__ == "__main__":
    unittest.main()
