import logging
from typing import Generator

from traffic_comparator.data import MatchedRequestResponsePair
from traffic_comparator.log_file_loader import LogFileFormat, getLogFileLoader

logger = logging.getLogger(__name__)


class StreamingDataLoader:
    def __init__(self) -> None:
        self.log_file_format = LogFileFormat.REPLAYER_TRIPLES
        self.log_loader = getLogFileLoader(self.log_file_format)

    def next_input(self) -> Generator[MatchedRequestResponsePair, None, None]:
        loader = self.log_loader.load()
        for line in loader:
            yield line
