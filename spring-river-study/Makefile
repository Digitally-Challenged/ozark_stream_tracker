.PHONY: data qa ledger test inventory

inventory:
	uv run python -m spring_river.ingest.inventory

data:
	uv run python -m spring_river.ingest.pull_all

qa:
	uv run python -m spring_river.qa.report

ledger:
	uv run python -m spring_river.hydro.ledger

test:
	uv run pytest -q
