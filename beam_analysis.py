from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


def validate_inputs(beam_length, udl, point_load, point_position):
    """Validate beam geometry and loading inputs."""
    if beam_length <= 0:
        raise ValueError("Beam length must be greater than 0 m.")

    if udl < 0 or point_load < 0:
        raise ValueError("Loads must be zero or positive.")

    if point_load > 0 and not 0 <= point_position <= beam_length:
        raise ValueError("Point-load position must lie on the beam.")


def calculate_reactions(
    beam_length,
    udl=0.0,
    point_load=0.0,
    point_position=0.0,
):
    """Calculate the vertical reactions of a simply supported beam.

    Units:
        beam_length: m
        udl: kN/m
        point_load: kN
        point_position: m from the left support

    Returns:
        (reaction_left, reaction_right) in kN
    """
    validate_inputs(beam_length, udl, point_load, point_position)

    total_udl = udl * beam_length

    reaction_right = (
        total_udl * (beam_length / 2)
        + point_load * point_position
    ) / beam_length

    reaction_left = total_udl + point_load - reaction_right

    return reaction_left, reaction_right


def bending_moment_at(
    x,
    beam_length,
    udl=0.0,
    point_load=0.0,
    point_position=0.0,
):
    """Return bending moment at position x in kN·m."""
    reaction_left, _ = calculate_reactions(
        beam_length,
        udl,
        point_load,
        point_position,
    )

    moment = reaction_left * x - (udl * x**2) / 2

    if x >= point_position:
        moment -= point_load * (x - point_position)

    return moment


def calculate_maximum_moment(
    beam_length,
    udl=0.0,
    point_load=0.0,
    point_position=0.0,
):
    """Find the maximum sagging bending moment and its position."""
    reaction_left, _ = calculate_reactions(
        beam_length,
        udl,
        point_load,
        point_position,
    )

    candidate_positions = [0.0, beam_length, point_position]

    if udl > 0:
        # Zero-shear point before the concentrated load.
        x_before_load = reaction_left / udl
        if 0 <= x_before_load <= point_position:
            candidate_positions.append(x_before_load)

        # Zero-shear point after the concentrated load.
        x_after_load = (reaction_left - point_load) / udl
        if point_position <= x_after_load <= beam_length:
            candidate_positions.append(x_after_load)

    candidate_moments = [
        (
            x,
            bending_moment_at(
                x,
                beam_length,
                udl,
                point_load,
                point_position,
            ),
        )
        for x in candidate_positions
    ]

    return max(candidate_moments, key=lambda item: item[1])


def analyse_beam(
    beam_length,
    udl=0.0,
    point_load=0.0,
    point_position=0.0,
    number_of_points=1001,
):
    """Calculate shear force and bending moment along the beam."""
    reaction_left, reaction_right = calculate_reactions(
        beam_length,
        udl,
        point_load,
        point_position,
    )

    x = np.linspace(0, beam_length, number_of_points)

    shear_force = reaction_left - udl * x
    shear_force -= np.where(x >= point_position, point_load, 0.0)

    bending_moment = reaction_left * x - (udl * x**2) / 2
    bending_moment -= point_load * np.maximum(0.0, x - point_position)

    return {
        "x": x,
        "shear_force": shear_force,
        "bending_moment": bending_moment,
        "reaction_left": reaction_left,
        "reaction_right": reaction_right,
    }


def save_diagrams(results, output_directory="results"):
    """Generate and save shear-force and bending-moment diagrams."""
    output_path = Path(output_directory)
    output_path.mkdir(parents=True, exist_ok=True)

    x = results["x"]

    plots = (
        (
            results["shear_force"],
            "Shear Force Diagram",
            "Shear force (kN)",
            "shear_force_diagram",
        ),
        (
            results["bending_moment"],
            "Bending Moment Diagram",
            "Bending moment (kN·m)",
            "bending_moment_diagram",
        ),
    )

    for values, title, y_label, filename in plots:
        plt.figure(figsize=(8, 4.5))
        plt.plot(x, values)
        plt.axhline(0, linewidth=0.8)
        plt.xlabel("Position along beam (m)")
        plt.ylabel(y_label)
        plt.title(title)
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.savefig(output_path / f"{filename}.png", dpi=200)
        plt.savefig(output_path / f"{filename}.svg")
        plt.close()


def main():
    """Run a worked example."""
    # Example beam:
    # - span = 6 m
    # - full-span UDL = 15 kN/m
    # - point load = 30 kN at 4 m from the left support
    beam_length = 6.0
    udl = 15.0
    point_load = 30.0
    point_position = 4.0

    results = analyse_beam(
        beam_length,
        udl,
        point_load,
        point_position,
    )

    max_moment_position, max_moment = calculate_maximum_moment(
        beam_length,
        udl,
        point_load,
        point_position,
    )

    print("SIMPLY SUPPORTED BEAM ANALYSIS")
    print("-" * 34)
    print(f"Left reaction: {results['reaction_left']:.2f} kN")
    print(f"Right reaction: {results['reaction_right']:.2f} kN")
    print(
        "Maximum bending moment: "
        f"{max_moment:.2f} kN·m at x = {max_moment_position:.2f} m"
    )

    save_diagrams(results)
    print("\nDiagrams saved in the 'results' folder.")


if __name__ == "__main__":
    main()
