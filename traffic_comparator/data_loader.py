import logging
from pathlib import Path
from typing import List, Tuple, Generator

from traffic_comparator.data import RequestResponseStream, RequestResponsePair
from traffic_comparator.log_file_loader import (LogFileFormat,
                                                UnknownLogFileFormatException,
                                                getLogFileLoader)

logger = logging.getLogger(__name__)


class DataLoader:
    def __init__(self, log_files: List[Path], log_file_format: str) -> None:
        # Determine the file format (from config file) and find a matching file loader class.
        try:
            self.log_file_format = LogFileFormat(log_file_format)
        except ValueError as e:
            raise UnknownLogFileFormatException(log_file_format, e)
        self.log_file_loader = getLogFileLoader(self.log_file_format)
        logger.debug(f"Log file loader found for filetype {self.log_file_format}.")

        # Instantiate log file loader for the log files.
        self.log_loader = self.log_file_loader(log_files)
        logger.debug(f"Log file loaders instantiated for files {log_files}.")

        # Actually load the data from the files.
        # These should potentially be made async.
        self._primary_log_data, self._shadow_log_data = self.log_loader.load()

        logger.debug("Shadow and primary log files loaded.")

    @property
    def primary_data_stream(self) -> RequestResponseStream:
        return self._primary_log_data

    @property
    def shadow_data_stream(self) -> RequestResponseStream:
        return self._shadow_log_data


class StreamingDataLoader:
    def __init__(self) -> None:
        self.log_file_format = LogFileFormat.REPLAYER_TRIPLES
        self.log_loader = getLogFileLoader(self.log_file_format)

    def next_input(self) -> Generator[Tuple[RequestResponsePair, RequestResponsePair], None, None]:
        loader = self.log_loader.load_from_stdin()
        for line in loader:
            yield line
