"""
test_registry.py
----------------
Tests for the component registry and generic build_structure pipeline.
"""

from __future__ import annotations

import pytest

from src.components.registry import COMPONENT_REGISTRY


class TestRegistry:

    def test_registry_has_cargo_floor(self):
        assert "cargo_floor" in COMPONENT_REGISTRY

    def test_registry_has_pax_floor(self):
        assert "pax_floor" in COMPONENT_REGISTRY

    def test_cargo_floor_has_three_components(self):
        assert len(COMPONENT_REGISTRY["cargo_floor"]) == 3

    def test_pax_floor_has_four_components(self):
        assert len(COMPONENT_REGISTRY["pax_floor"]) == 4

    @pytest.mark.parametrize("structure", ["cargo_floor", "pax_floor"])
    def test_each_entry_has_required_keys(self, structure):
        required = {"name", "loader", "builder", "file", "meta_keys"}
        for comp in COMPONENT_REGISTRY[structure]:
            assert required.issubset(
                comp.keys()
            ), f"{comp.get('name','?')} missing keys: {required - comp.keys()}"

    @pytest.mark.parametrize("structure", ["cargo_floor", "pax_floor"])
    def test_each_builder_is_callable(self, structure):
        for comp in COMPONENT_REGISTRY[structure]:
            assert callable(comp["builder"]), f"{comp['name']} builder not callable"

    @pytest.mark.parametrize("structure", ["cargo_floor", "pax_floor"])
    def test_each_loader_is_callable(self, structure):
        for comp in COMPONENT_REGISTRY[structure]:
            assert callable(comp["loader"]), f"{comp['name']} loader not callable"

    def test_component_names_are_unique_within_structure(self):
        for struct, comps in COMPONENT_REGISTRY.items():
            names = [c["name"] for c in comps]
            assert len(names) == len(
                set(names)
            ), f"Duplicate component names in '{struct}': {names}"

    def test_meta_keys_are_lists(self):
        for _struct, comps in COMPONENT_REGISTRY.items():
            for comp in comps:
                assert isinstance(
                    comp["meta_keys"], list
                ), f"{comp['name']} meta_keys must be a list"
