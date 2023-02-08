import json

import pytest

from traffic_comparator.config_file_loader import (
    Config, ConfigFileMissingRequiredFieldException,
    ConfigFileNotJSONException, ReportConfig, load_config_file)

CONFIG_JSON = {
    "primary_log_file": "test_primary_logs.log",
    "shadow_log_file": "test_shadow_logs.log",
    "log_file_format": "haproxy-jsons",
    "reports": [
        {
            "report_name": "BasicCorrectnessReport",
            "export_filename": "correctness_report.txt",
            "display": True
        }
    ]
}
CONFIG = Config(
    primary_log_file=CONFIG_JSON["primary_log_file"],
    shadow_log_file=CONFIG_JSON["shadow_log_file"],
    log_file_format=CONFIG_JSON["log_file_format"],
    reports=[
        ReportConfig(report_name=CONFIG_JSON["reports"][0]["report_name"],
                     display=CONFIG_JSON["reports"][0]["display"],
                     export_filename=CONFIG_JSON["reports"][0]["export_filename"])
    ]
)


@pytest.fixture
def valid_config_file(tmpdir):
    config_file = tmpdir / "config.json"
    config_file.write(json.dumps(CONFIG_JSON))
    return config_file


@pytest.fixture
def non_parseable_file(tmpdir):
    config_file = tmpdir / "config.json"
    config_file.write("{]")
    return config_file


@pytest.fixture
def invalid_file_missing_primary_log_file(tmpdir):
    config_file = tmpdir / "config.json"
    config_file.write(json.dumps({k: v for k, v in CONFIG_JSON.items() if k != "primary_log_file"}))
    return config_file


@pytest.fixture
def invalid_file_missing_log_format(tmpdir):
    config_file = tmpdir / "config.json"
    config_file.write(json.dumps({k: v for k, v in CONFIG_JSON.items() if k != "log_file_format"}))
    return config_file


@pytest.fixture
def invalid_file_missing_report_name(tmpdir):
    reports = [{
        "display": True,
        "export_filename": "outputfile.csv"
    }]
    config_file = tmpdir / "config.json"
    config_file.write(json.dumps({k: v for k, v in CONFIG_JSON.items() if k != "reports"} | {"reports": reports}))
    return config_file


@pytest.fixture
def invalid_file_missing_report_display(tmpdir):
    config_file = tmpdir / "config.json"
    reports = [{
        "report_name": "PerformanceReport",
        "export_filename": "outputfile.csv"
    }]
    config_file = tmpdir / "config.json"
    config_file.write(json.dumps({k: v for k, v in CONFIG_JSON.items() if k != "reports"} | {"reports": reports}))
    return config_file


@pytest.fixture
def valid_file_no_reports(tmpdir):
    config_file = tmpdir / "config.json"
    config_file.write(json.dumps({k: v for k, v in CONFIG_JSON.items() if k != "reports"}))
    return config_file


def test_WHEN_load_config_file_called_AND_valid_THEN_returns_it(valid_config_file):
    with open(valid_config_file, 'r') as f:
        config_value = load_config_file(f)  # type: ignore
    assert config_value == CONFIG


def test_WHEN_load_config_file_called_AND_not_valid_json_THEN_raises(non_parseable_file):
    with open(non_parseable_file, 'r') as f:
        with pytest.raises(ConfigFileNotJSONException):
            load_config_file(f)  # type: ignore


def test_WHEN_load_config_file_called_AND_missing_log_file_THEN_raises(invalid_file_missing_primary_log_file):
    with open(invalid_file_missing_primary_log_file, 'r') as f:
        with pytest.raises(ConfigFileMissingRequiredFieldException):
            load_config_file(f)  # type: ignore


def test_WHEN_load_config_file_called_AND_missing_log_format_THEN_raises(invalid_file_missing_log_format):
    with open(invalid_file_missing_log_format, 'r') as f:
        with pytest.raises(ConfigFileMissingRequiredFieldException):
            load_config_file(f)  # type: ignore


def test_WHEN_load_config_file_called_AND_report_name_THEN_raises(invalid_file_missing_report_name):
    with open(invalid_file_missing_report_name, 'r') as f:
        with pytest.raises(ConfigFileMissingRequiredFieldException):
            load_config_file(f)  # type: ignore


def test_WHEN_load_config_file_called_AND_report_display_THEN_raises(invalid_file_missing_report_display):
    with open(invalid_file_missing_report_display, 'r') as f:
        with pytest.raises(ConfigFileMissingRequiredFieldException):
            load_config_file(f)  # type: ignore


def test_WHEN_load_config_file_called_AND_no_reports_THEN_returns_it(valid_file_no_reports):
    with open(valid_file_no_reports, 'r') as f:
        config_value = load_config_file(f)  # type: ignore
    CONFIG.reports = []
    assert config_value == CONFIG
