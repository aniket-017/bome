from app.catalog import iter_items, load
from app.normalize import CATALOG_NOUNS, NOUN_BY_PTYPE, extract_attrs, normalize


def test_normalize_knows_every_catalog_noun():
    assert set(CATALOG_NOUNS) == set(load())


def test_descriptions_start_with_their_noun_in_modifier_order():
    for noun in load().values():
        item = next(noun.items())
        assert item.description.startswith(noun.name + " ")
        assert list(item.modifiers) == [m for m in noun.modifiers if m in item.modifiers]
        assert NOUN_BY_PTYPE[extract_attrs(normalize(noun.name))["ptype"]] == noun.name


def test_catalog_descriptions_are_unique():
    seen: set[str] = set()
    for item in iter_items():
        assert item.description not in seen, item.description
        seen.add(item.description)
    assert len(seen) > 800_000
