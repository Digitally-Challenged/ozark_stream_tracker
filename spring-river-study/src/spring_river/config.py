"""Project-wide constants. Single source of truth for sites, params, paths."""
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]

SITE_HARDY = "07069305"
SITE_IMBODEN = "07069500"
NWS_GAUGE = "HDYA4"
PARAM_DISCHARGE = "00060"  # cfs
PARAM_STAGE = "00065"      # ft

START_DATE = "1981-01-01"

WEST_PLAINS_LATLON = (36.7439, -91.8524)
RECHARGE_BUFFER_KM = 30  # stated approximation of Mammoth Spring recharge basin

RAW_DIR = PROJECT_ROOT / "data" / "raw"
INTERIM_DIR = PROJECT_ROOT / "data" / "interim"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
DOCS_DIR = PROJECT_ROOT / "docs"
FIGURES_DIR = PROJECT_ROOT / "reports" / "figures"
