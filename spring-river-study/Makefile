.PHONY: data qa ledger test inventory phase4 phase5 phase6 analysis

phase4:
	uv run python -m spring_river.analysis.phase4

phase5:
	uv run python -m spring_river.analysis.phase5

phase6:
	uv run python -m spring_river.analysis.phase6

analysis: ledger phase4 phase5 phase6

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
