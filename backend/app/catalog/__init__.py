"""Noun + Modifier parts catalog.

Every part is NOUN followed by its modifiers in the noun's fixed order, e.g.
    ELBOW 90 DEG LR CS ASTM A234 WPB DN 50 SCH 40 BW ASME B16.9

A `Noun` is registered once with its item group, unit of measure and modifier sequence. Generator
functions attached to it yield one dict per part (modifier name -> value); empty values are left out
of both the description and the stored modifiers. Generators only produce engineering-valid
combinations (size ranges per pressure class, schedules per size, lengths per diameter, ...).
"""
from __future__ import annotations

import importlib
from collections.abc import Callable, Iterable, Iterator
from dataclasses import dataclass, field

Spec = dict[str, str]


@dataclass
class CatalogItem:
    noun: str
    description: str
    modifiers: dict[str, str]
    item_group: str
    uom: str


@dataclass
class _Generator:
    fn: Callable[[], Iterable[Spec]]
    group: str
    uom: str


@dataclass
class Noun:
    name: str
    group: str
    uom: str
    modifiers: tuple[str, ...]
    # separator written before a modifier instead of a space, e.g. {"LENGTH": " X "} -> "M20 X 150 MM"
    glue: dict[str, str] = field(default_factory=dict)
    generators: list[_Generator] = field(default_factory=list)

    def generator(self, fn: Callable[[], Iterable[Spec]] | None = None, *, group: str | None = None,
                  uom: str | None = None):
        def register(f: Callable[[], Iterable[Spec]]):
            self.generators.append(_Generator(f, group or self.group, uom or self.uom))
            return f
        return register(fn) if fn else register

    def items(self) -> Iterator[CatalogItem]:
        allowed = set(self.modifiers)
        for gen in self.generators:
            for spec in gen.fn():
                unknown = spec.keys() - allowed
                if unknown:
                    raise ValueError(f"{self.name}/{gen.fn.__name__}: unknown modifiers {sorted(unknown)}")
                mods = {k: str(v).strip() for k, v in spec.items() if v not in (None, "")}
                desc = self.name
                for m in self.modifiers:
                    if m in mods:
                        desc += self.glue.get(m, " ") + mods[m]
                yield CatalogItem(self.name, " ".join(desc.split()), mods, gen.group, gen.uom)


NOUNS: dict[str, Noun] = {}


def noun(name: str, group: str, uom: str, modifiers: Iterable[str], glue: dict[str, str] | None = None) -> Noun:
    if name in NOUNS:
        raise ValueError(f"noun {name} registered twice")
    n = Noun(name, group, uom, tuple(modifiers), glue or {})
    NOUNS[name] = n
    return n


MODULES = (
    "piping", "flanges", "valves", "fasteners", "raw", "bearings", "seals", "transmission",
    "rotating", "electrical", "instrumentation", "tools", "consumables",
)


def load() -> dict[str, Noun]:
    for m in MODULES:
        importlib.import_module(f"app.catalog.{m}")
    return NOUNS


def iter_items() -> Iterator[CatalogItem]:
    for n in load().values():
        yield from n.items()
