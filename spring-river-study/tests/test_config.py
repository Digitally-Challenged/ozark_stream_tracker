from spring_river import config


def test_sites_and_params():
    assert config.SITE_HARDY == "07069305"
    assert config.SITE_IMBODEN == "07069500"
    assert config.PARAM_DISCHARGE == "00060"


def test_paths_anchor_to_project_root():
    assert (config.PROJECT_ROOT / "pyproject.toml").exists()
    assert config.RAW_DIR.parts[-2:] == ("data", "raw")


def test_basin_source_default_and_choices():
    from spring_river import config

    assert config.BASIN_PRECIP_SOURCE in config.BASIN_SOURCES
    assert config.BASIN_SOURCES == ("aorc", "prism_polygon", "prism_buffer")
    assert config.RECHARGE_POLYGON_PATH.name == "mammoth_spring_recharge_modnr.geojson"
    assert config.AORC_DAY_END_HOUR_UTC == 12
