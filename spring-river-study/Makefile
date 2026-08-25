.PHONY: data qa ledger test inventory phase4 phase5 phase6 phase7 analysis report

QUARTO ?= $(shell command -v quarto 2>/dev/null || echo $(HOME)/.local/bin/quarto)

phase7:
	uv run python -m spring_river.analysis.phase7

report: analysis
	cd reports && QUARTO_PYTHON=$(CURDIR)/.venv/bin/python $(QUARTO) render report.qmd

phase4:
	uv run python -m spring_river.analysis.phase4

phase5:
	uv run python -m spring_river.analysis.phase5

phase6:
	uv run python -m spring_river.analysis.phase6

analysis: ledger phase4 phase5 phase6 phase7

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
