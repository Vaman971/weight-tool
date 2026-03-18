"""
conftest.py
-----------
Shared pytest fixtures for the full weight function test suite.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest


@pytest.fixture(scope="session")
def data_root() -> Path:
    return Path(__file__).resolve().parents[1] / "data"


@pytest.fixture(scope="session")
def cargo_data_dir() -> Path:
    return Path(__file__).resolve().parents[1] / "data" / "cargo_floor"


@pytest.fixture(scope="session")
def pax_data_dir() -> Path:
    return Path(__file__).resolve().parents[1] / "data" / "pax_floor"


@pytest.fixture(scope="session")
def door_data_dir() -> Path:
    return Path(__file__).resolve().parents[1] / "data" / "pax_door"


@pytest.fixture(scope="session")
def keel_data_dir() -> Path:
    return Path(__file__).resolve().parents[1] / "data" / "keel_beam"


# ── minimal synthetic DataFrames ────────────────────────────────────────────


@pytest.fixture()
def single_panel_row() -> pd.DataFrame:
    """1000×500 mm rectangular panel at Z=0."""
    return pd.DataFrame(
        [
            {
                "Panel": "C24-C25",
                "Element": "BASE_PANEL",
                "Mass": 1000.0,
                "X1": 0.0,
                "Y1": 0.0,
                "Z1": 0.0,
                "X2": 1000.0,
                "Y2": 0.0,
                "Z2": 0.0,
                "X3": 1000.0,
                "Y3": 500.0,
                "Z3": 0.0,
                "X4": 0.0,
                "Y4": 500.0,
                "Z4": 0.0,
                "Thickness": 12.3,
            }
        ]
    )


@pytest.fixture()
def single_beam_row() -> pd.DataFrame:
    """C24 TOP_FLANGE cross-beam."""
    return pd.DataFrame(
        [
            {
                "Frame": "C24",
                "Element": "TOP_FLANGE",
                "Mass": 125.0,
                "X1": 9499.6,
                "Y1": 715.0,
                "Z1": -1909.8,
                "X2": 9499.6,
                "Y2": -715.0,
                "Z2": -1909.8,
                "X3": 9521.6,
                "Y3": -715.0,
                "Z3": -1909.8,
                "X4": 9521.6,
                "Y4": 715.0,
                "Z4": -1909.8,
                "Thickness": 1.4,
            }
        ]
    )


@pytest.fixture()
def single_cs_row() -> pd.DataFrame:
    """C24 OBD_STRUT WEB from cargo floor."""
    return pd.DataFrame(
        [
            {
                "Frame": "C24",
                "Strut": "OBD_STRUT",
                "Element": "WEB",
                "Mass": 27.0,
                "X1": 9501.0,
                "Y1": 368.4,
                "Z1": -1911.2,
                "X2": 9501.0,
                "Y2": 331.6,
                "Z2": -1911.2,
                "X3": 9501.0,
                "Y3": 366.6,
                "Z3": -2087.2,
                "X4": 9501.0,
                "Y4": 403.4,
                "Z4": -2087.2,
                "Thickness": 1.6,
            }
        ]
    )


@pytest.fixture()
def single_isect_row() -> pd.DataFrame:
    """C24L WEB from PAX floor I-section strut."""
    return pd.DataFrame(
        [
            {
                "Frame": "C24L",
                "Element": "WEB",
                "Mass": 344.0,
                "X1": 9499.6,
                "Y1": -1328.0,
                "Z1": -599.5,
                "X2": 9499.6,
                "Y2": -1378.0,
                "Z2": -599.5,
                "X3": 9499.6,
                "Y3": -1378.0,
                "Z3": -1535.2,
                "X4": 9499.6,
                "Y4": -1328.0,
                "Z4": -1535.2,
                "Thickness": 2.6,
            }
        ]
    )


@pytest.fixture()
def single_rail_row() -> pd.DataFrame:
    """INBD SEAT RAIL TOP_FLANGE."""
    return pd.DataFrame(
        [
            {
                "Rail": "INBD",
                "Element": "TOP_FLANGE",
                "Mass": 2886.0,
                "X1": 9499.6,
                "Y1": 804.5,
                "Z1": -504.7,
                "X2": 9499.6,
                "Y2": 725.5,
                "Z2": -504.7,
                "X3": 15367.0,
                "Y3": 725.5,
                "Z3": -504.7,
                "X4": 15367.0,
                "Y4": 804.5,
                "Z4": -504.7,
                "Thickness": 2.2,
            }
        ]
    )
