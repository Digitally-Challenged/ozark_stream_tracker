from spring_river import config


def test_sites_and_params():
    assert config.SITE_HARDY == "07069305"
    assert config.SITE_IMBODEN == "07069500"
    assert config.PARAM_DISCHARGE == "00060"


def test_paths_anchor_to_project_root():
    assert (config.PROJECT_ROOT / "pyproject.toml").exists()
    assert config.RAW_DIR.parts[-2:] == ("data", "raw")
