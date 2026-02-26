# Shared Realms Prototype

This repository contains an implementation-oriented prototype based on the provided game design document for **Shared Realms**.

## What's included

- Core simulation engine for a persistent shared world.
- Role-specific player models (farmer, hero, royal guard, bounty hunter, mage).
- Dynamic economy with supply/demand and event-driven price shifts.
- Global event system (disasters, monster rampages, magical calamities).
- NPC bot subsystem that can fill role activity gaps.
- Role switching eligibility checks based on milestones, seasons, and role artifacts.
- A simple notification feed.
- Unit tests covering core behavior.

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
python -m shared_realms.demo
```

Run tests:

```bash
pytest
```
