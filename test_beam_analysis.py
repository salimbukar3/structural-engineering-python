import unittest

from beam_analysis import (
    bending_moment_at,
    calculate_maximum_moment,
    calculate_reactions,
)


class BeamAnalysisTests(unittest.TestCase):
    def test_worked_example_reactions(self):
        reaction_left, reaction_right = calculate_reactions(
            beam_length=6.0,
            udl=15.0,
            point_load=30.0,
            point_position=4.0,
        )

        self.assertAlmostEqual(reaction_left, 55.0)
        self.assertAlmostEqual(reaction_right, 65.0)

    def test_worked_example_maximum_moment(self):
        position, moment = calculate_maximum_moment(
            beam_length=6.0,
            udl=15.0,
            point_load=30.0,
            point_position=4.0,
        )

        self.assertAlmostEqual(position, 11 / 3)
        self.assertAlmostEqual(moment, 100.83333333333333)

    def test_end_moments_are_zero(self):
        left_moment = bending_moment_at(
            0.0,
            beam_length=6.0,
            udl=15.0,
            point_load=30.0,
            point_position=4.0,
        )

        right_moment = bending_moment_at(
            6.0,
            beam_length=6.0,
            udl=15.0,
            point_load=30.0,
            point_position=4.0,
        )

        self.assertAlmostEqual(left_moment, 0.0)
        self.assertAlmostEqual(right_moment, 0.0)

    def test_central_point_load(self):
        reaction_left, reaction_right = calculate_reactions(
            beam_length=8.0,
            point_load=40.0,
            point_position=4.0,
        )

        self.assertAlmostEqual(reaction_left, 20.0)
        self.assertAlmostEqual(reaction_right, 20.0)

        position, moment = calculate_maximum_moment(
            beam_length=8.0,
            point_load=40.0,
            point_position=4.0,
        )

        self.assertAlmostEqual(position, 4.0)
        self.assertAlmostEqual(moment, 80.0)

    def test_full_span_udl(self):
        reaction_left, reaction_right = calculate_reactions(
            beam_length=10.0,
            udl=5.0,
        )

        self.assertAlmostEqual(reaction_left, 25.0)
        self.assertAlmostEqual(reaction_right, 25.0)

        position, moment = calculate_maximum_moment(
            beam_length=10.0,
            udl=5.0,
        )

        self.assertAlmostEqual(position, 5.0)
        self.assertAlmostEqual(moment, 62.5)


if __name__ == "__main__":
    unittest.main()
