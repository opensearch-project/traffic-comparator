import json
import logging
from typing import TextIO, List, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


class ConfigFileNotJSONException(Exception):
    def __init__(self, test_config_path_full, original_exception):
        super().__init__(f"The config at path {test_config_path_full} is not parsable as JSON."
                         f" Details: {str(original_exception)}")


class ConfigFileMissingRequiredFieldException(Exception):
    def __init__(self, field, original_exception):
        super().__init__(f"The config file does not include the required field '{field}'. "
                         f" Details: {str(original_exception)}")


@dataclass
class ReportConfig:
    report_name: str
    display: bool
    export_filename: Optional[str] = None

    def __post_init__(self):
        if self.report_name is None:
            raise ConfigFileMissingRequiredFieldException('report_name', None)
        if self.display is None:
            raise ConfigFileMissingRequiredFieldException('display', None)
    

@dataclass
class Config:
    primary_log_file: str
    shadow_log_file: str
    log_file_format: str  # This could be an enum as well
    reports: List[ReportConfig]

    def __post_init__(self):
        if self.primary_log_file is None:
            raise ConfigFileMissingRequiredFieldException('primary_log_file', None)
        if self.shadow_log_file is None:
            raise ConfigFileMissingRequiredFieldException('shadow_log_file', None)
        if self.log_file_format is None:
            raise ConfigFileMissingRequiredFieldException('log_file_format', None)
    

def load_config_file(config_file: TextIO) -> Config:
    logging.debug(f"Loading config file from {config_file.name}")
    try:
        config_dict = json.load(config_file)
    except json.JSONDecodeError as e:
        raise ConfigFileNotJSONException(config_file.name, e)

    try:
        reports = config_dict.pop("reports")
    except KeyError:
        reports = []

    try:
        config = Config(reports=[ReportConfig(**report) for report in reports],
                        **config_dict)
    except TypeError as e:
        raise ConfigFileMissingRequiredFieldException('[see details]', e)
    return config
