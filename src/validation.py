"""
Mass and coordinate reconciliation for weight-function outputs.

Produces:
  - Per-parameter comparison table with % relative error and std deviation
  - Pass/Fail flag based on the 5% tolerance threshold
  - Matplotlib visualisation showing component geometry on a shared 3-D plot
"""

from __future__ import annotations

import logging
from dataclasses import dataclass

import matplotlib

matplotlib.use("Agg")  # non-interactive backend for CI / headless environments
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from matplotlib.figure import Figure  # noqa: E402
from mpl_toolkits.mplot3d.art3d import Poly3DCollection  # noqa: E402

from .geometry import FloatArray  # noqa: E402
from .weight_functions import WeightFunction  # noqa: E402

logger = logging.getLogger(__name__)

TOLERANCE_PCT = 5.0
ValidationTargets = dict[str, float | None]


@dataclass
class ReconciliationEntry:
    """Represent one row in a reconciliation report.

    Parameters
    ----------
    parameter : str
        Human-readable name of the compared quantity.
    expected : float
        Target value from the benchmark dataset.
    actual : float
        Value computed by the Python pipeline.
    abs_diff : float
        Absolute difference between expected and actual values.
    pct_diff : float
        Percentage difference relative to the expected value.
    std_dev : float
        Standard deviation across the expected and actual values.
    pass_fail : str
        Reconciliation status label.
    """

    parameter: str
    expected: float
    actual: float
    abs_diff: float
    pct_diff: float
    std_dev: float
    pass_fail: str


def _pct_diff(expected: float, actual: float) -> float:
    """Relative percentage difference vs expected value."""
    if expected == 0.0:
        return float("inf") if actual != 0 else 0.0
    return abs((actual - expected) / expected) * 100.0


def reconcile(
    weight_functions: list[WeightFunction],
    targets: ValidationTargets,
) -> pd.DataFrame:
    """
    Compare aggregate Python outputs against Excel benchmark targets.

    Parameters
    ----------
    weight_functions : list[WeightFunction]
        Computed weight function instances (one per component).
    targets : dict
        Expected values with keys mass_kg, x_mm, y_mm, z_mm.

    Returns
    -------
    pd.DataFrame
        Reconciliation report with columns:
        Parameter, Expected, Actual, AbsDiff, PctDiff, StdDev, PassFail.
    """
    total_mass_kg = sum(wf.total_mass_kg for wf in weight_functions)

    # Compute combined CoG via parallel-axis theorem approach
    total_mass_g = sum(wf.total_mass_g for wf in weight_functions)
    if total_mass_g == 0.0:
        combined_cog: FloatArray = np.zeros(3, dtype=float)
    else:
        moment: FloatArray = np.zeros(3, dtype=float)
        for wf in weight_functions:
            moment += wf.total_mass_g * wf.centre_of_gravity
        combined_cog = moment / total_mass_g

    actuals = {
        "Mass (kg)": total_mass_kg,
        "X CoG (mm)": combined_cog[0],
        "Y CoG (mm)": combined_cog[1],
        "Z CoG (mm)": combined_cog[2],
    }
    expected_map = {
        "Mass (kg)": targets.get("mass_kg"),
        "X CoG (mm)": targets.get("x_mm"),
        "Y CoG (mm)": targets.get("y_mm"),
        "Z CoG (mm)": targets.get("z_mm"),
    }

    records = []
    for param, actual in actuals.items():
        expected = expected_map.get(param)
        if expected is None:
            continue
        abs_diff = abs(actual - expected)
        pct = _pct_diff(expected, actual)
        std_dev = float(np.std([expected, actual]))
        pass_fail = "PASS" if pct < TOLERANCE_PCT else "FAIL"
        records.append(
            ReconciliationEntry(
                parameter=param,
                expected=expected,
                actual=round(actual, 3),
                abs_diff=round(abs_diff, 3),
                pct_diff=round(pct, 2),
                std_dev=round(std_dev, 3),
                pass_fail=pass_fail,
            )
        )
        logger.info(
            "%-18s | expected=%-10.3f actual=%-10.3f | %%diff=%.2f | %s",
            param,
            expected,
            actual,
            pct,
            pass_fail,
        )

    df = pd.DataFrame(
        [
            {
                "Parameter": r.parameter,
                "Expected": r.expected,
                "Actual": r.actual,
                "AbsDiff": r.abs_diff,
                "PctDiff (%)": r.pct_diff,
                "StdDev": r.std_dev,
                "PassFail": r.pass_fail,
            }
            for r in records
        ]
    )
    return df


def plot_components(
    weight_functions: list[WeightFunction],
    output_path: str | None = None,
) -> Figure:
    """
    Render all component primitives on a shared 3-D axis plot.

    Each component is drawn in a distinct colour. The combined CoG is
    marked with a cross-hair marker.

    Parameters
    ----------
    weight_functions : list[WeightFunction]
        Weight function instances whose primitives will be plotted.
    output_path : str, optional
        If provided, save the figure to this path.

    Returns
    -------
    matplotlib.figure.Figure
    """
    colours = [
        "#1f77b4",  # blue
        "#ff7f0e",  # orange
        "#2ca02c",  # green
        "#d62728",  # red
        "#9467bd",  # purple
        "#8c564b",  # brown
        "#e377c2",  # pink
        "#17becf",  # cyan
    ]
    fig = plt.figure(figsize=(14, 9))
    ax = fig.add_subplot(111, projection="3d")

    for i, wf in enumerate(weight_functions):
        colour = colours[i % len(colours)]
        faces = []

        # USE REAL GEOMETRY INSTEAD OF CENTROIDS
        for prim in wf.primitives:
            if prim.points is not None:
                faces.append(prim.points.tolist())

        # Plot surfaces
        if faces:
            poly = Poly3DCollection(
                faces,
                alpha=0.4,  # more visible
                facecolor=colour,
                edgecolor="k",  # black edges for clarity
                linewidths=0.5,
                label=wf.component_name,
            )
            ax.add_collection3d(poly)

        # keep centroids (can comment if cluttered)
        centroids = np.asarray([p.centroid for p in wf.primitives], dtype=float)
        if centroids.size > 0:
            ax.scatter(
                centroids[:, 0],
                centroids[:, 1],
                centroids[:, 2],
                c=colour,
                s=5,
                alpha=0.4,
            )

    # Combined CoG
    total_mass_g = sum(wf.total_mass_g for wf in weight_functions)
    if total_mass_g > 0:
        moment = np.zeros(3, dtype=float)
        for wf in weight_functions:
            moment += wf.total_mass_g * wf.centre_of_gravity
        cog = moment / total_mass_g

        ax.scatter(
            cog[0],
            cog[1],
            cog[2],
            c="red",
            s=150,
            marker="X",
            zorder=10,
            label="Combined CoG",
        )

    # Labels
    ax.set_xlabel("X (mm)")
    ax.set_ylabel("Y (mm)")
    ax.set_zlabel("Z (mm)")
    ax.set_title("Structure Component Geometry")

    # correct proportions
    ax.set_box_aspect([3, 1, 0.5])

    # Better viewing angle
    ax.view_init(elev=20, azim=-60)

    ax.legend(loc="upper left", fontsize=8)

    if output_path:
        fig.savefig(output_path, dpi=150, bbox_inches="tight")
        logger.info("Plot saved to %s", output_path)

    return fig
