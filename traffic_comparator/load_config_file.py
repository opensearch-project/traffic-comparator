import json
import logging
from typing import TextIO

logger = logging.getLogger(__name__)


class ConfigFileNotJSONException(Exception):
    def __init__(self, test_config_path_full, original_exception):
        super().__init__(f"The config at path {test_config_path_full} is not parsable as JSON."
                         f" Details: {str(original_exception)}")


def load_config_file(config_file: TextIO) -> dict:
    logging.debug(f"Loading config file from {config_file.name}")
    try:
        config = json.load(config_file)
    except json.JSONDecodeError as e:
        raise ConfigFileNotJSONException(config_file.name, e)
    return config
