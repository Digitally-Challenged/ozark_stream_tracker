"""Project-wide constants. Single source of truth for sites, params, paths."""
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]

SITE_HARDY = "07069305"
SITE_IMBODEN = "07069500"
SITE_MAMMOTH = "07069190"  # Mammoth Spring vent gauge; DV discharge 1981-02-25->present
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
TABLES_DIR = PROJECT_ROOT / "reports" / "tables"
RATING_FLOWS_CFS = (400.0, 1000.0)      # spec §2.2 stage-at-fixed-discharge
RATING_TOLERANCE = 0.05                 # ±5% flow window for IV pairs
# Bulletin 17B Plate I generalized skew for the S. Missouri / NE Arkansas
# region is approximately -0.2 with map MSE 0.302. APPROXIMATE — replace
# with the USGS Arkansas/Missouri regional-skew study value when obtained,
# and flag every B17 result as provisional until then.
REGIONAL_SKEW = -0.2
REGIONAL_SKEW_MSE = 0.302
MAJOR_FLOOD_FT = 16.0
