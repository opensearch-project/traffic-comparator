import logging

from traffic_comparator.data import RequestResponseStream
from traffic_comparator.log_file_loader import (LogFileFormat,
                                                UnknownLogFileFormatException,
                                                getLogFileLoader)
from traffic_comparator.config_file_loader import Config

logger = logging.getLogger(__name__)

LOG_FILE_FORMAT_KEY = "log_file_format"
PRIMARY_LOG_FILE_KEY = "primary_log"
SHADOW_LOG_FILE_KEY = "shadow_log"


class DataLoader:
    def __init__(self, config: Config) -> None:
        # Determine the file format (from config file) and find a matching file loader class.
        try:
            self.log_file_format = LogFileFormat(config.log_file_format)
        except ValueError as e:
            raise UnknownLogFileFormatException(config.log_file_format, e)
        self.log_file_loader = getLogFileLoader(self.log_file_format)
        logger.debug(f"Log file loader found for filetype {self.log_file_format}.")

        # Find the primary and shadow log file paths from the config file.
        self.primary_log_file = config.primary_log_file
        self.shadow_log_file = config.shadow_log_file

        # Instantiate log file loaders for each log files.
        self.primary_log_loader = self.log_file_loader(self.primary_log_file)
        self.shadow_log_loader = self.log_file_loader(self.shadow_log_file)
        logger.debug(f"Log file loaders instantiated for files {self.primary_log_file} and {self.shadow_log_file}")

        # Actually load the data from the files.
        # These should potentially be made async.
        # It's also possible that one relies on the other (correlated data)-- for now we're skipping that.
        self._primary_log_data = self.primary_log_loader.load()
        self._shadow_log_data = self.shadow_log_loader.load()
        logger.debug("Shadow and primary log files loaded.")

    @property
    def primary_data_stream(self) -> RequestResponseStream:
        return self._primary_log_data

    @property
    def shadow_data_stream(self) -> RequestResponseStream:
        return self._shadow_log_data
