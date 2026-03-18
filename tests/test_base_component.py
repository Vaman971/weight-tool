"""
test_base_component.py
----------------------
Tests for the BaseComponent abstract base class.
"""

from __future__ import annotations

import pandas as pd
import pytest

from src.components.base import BaseComponent
from src.weight_functions import WeightFunction


class _ConcreteComponent(BaseComponent):
    """Minimal concrete subclass for testing the base class."""

    def build(self) -> WeightFunction:
        wf = WeightFunction(self.name)
        return wf


class TestBaseComponent:

    def test_empty_df_raises(self):
        with pytest.raises(ValueError, match="empty or None"):
            _ConcreteComponent("TEST", pd.DataFrame(), {})

    def test_none_df_raises(self):
        with pytest.raises((ValueError, AttributeError)):
            _ConcreteComponent("TEST", None, {})

    def test_density_g_per_cm3_returned(self):
        df = pd.DataFrame([{"x": 1}])
        comp = _ConcreteComponent("T", df, {"density_g_per_cm3": 2.83})
        assert comp._density_g_per_cm3() == pytest.approx(2.83)

    def test_zero_density_raises(self):
        df = pd.DataFrame([{"x": 1}])
        comp = _ConcreteComponent("T", df, {"density_g_per_cm3": 0.0})
        with pytest.raises(ValueError):
            comp._density_g_per_cm3()

    def test_negative_density_raises(self):
        df = pd.DataFrame([{"x": 1}])
        comp = _ConcreteComponent("T", df, {"density_g_per_cm3": -1.0})
        with pytest.raises(ValueError):
            comp._density_g_per_cm3()

    def test_areal_density_returned(self):
        df = pd.DataFrame([{"x": 1}])
        comp = _ConcreteComponent("T", df, {"areal_density_g_per_m2": 4900.0})
        assert comp._areal_density_g_per_m2() == pytest.approx(4900.0)

    def test_zero_areal_density_raises(self):
        df = pd.DataFrame([{"x": 1}])
        comp = _ConcreteComponent("T", df, {"areal_density_g_per_m2": 0.0})
        with pytest.raises(ValueError):
            comp._areal_density_g_per_m2()

    @pytest.mark.parametrize("flag,expected", [(True, True), (False, False)])
    def test_symmetrical_flag(self, flag, expected):
        df = pd.DataFrame([{"x": 1}])
        comp = _ConcreteComponent("T", df, {"symmetrical": flag})
        assert comp._symmetrical() == expected

    def test_symmetrical_defaults_to_false(self):
        df = pd.DataFrame([{"x": 1}])
        comp = _ConcreteComponent("T", df, {})
        assert comp._symmetrical() is False

    def test_build_returns_weight_function(self):
        df = pd.DataFrame([{"x": 1}])
        comp = _ConcreteComponent("T", df, {})
        result = comp.build()
        assert isinstance(result, WeightFunction)
