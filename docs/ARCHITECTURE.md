# Architecture

`app/main.py` mounts the health router at `/api` and the group controllers at `/groups`; `app/core/config.py` supplies settings. Controllers adapt HTTP, services enforce use cases and transactions, repositories access PostgreSQL and entities define SQLAlchemy mappings. Domain functions validate decimal amounts and calculate shares. Alembic owns schema migration and `app.seed` supplies the initial data.

The user selected an entity–repository–service–controller structure. See [the approved architecture proposal](BACKEND-ARCHITECTURE-PROPOSAL.md) for responsibilities, transaction design and implementation decisions.
