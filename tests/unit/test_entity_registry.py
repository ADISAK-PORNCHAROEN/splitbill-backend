from app.entities.registry import MAPPED_ENTITIES, metadata


def test_entity_registry_loads_every_mapped_table() -> None:
    entity_tables = {entity.__tablename__ for entity in MAPPED_ENTITIES}

    assert entity_tables == set(metadata.tables)
    assert entity_tables == {"users", "groups", "memberships", "expenses", "shares"}
