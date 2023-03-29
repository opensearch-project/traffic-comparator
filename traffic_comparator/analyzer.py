import logging

from typing import IO
from traffic_comparator.data_loader import StreamingDataLoader
from traffic_comparator.response_comparison import ResponseComparison

logger = logging.getLogger(__name__)


class StreamingAnalyzer:
    def __init__(self, dataLoader: StreamingDataLoader, output: IO) -> None:
        self._data_loader = dataLoader
        self._comparisons_count = 0
        self._output = output

    def start(self):
        data_loader_generator = self._data_loader.next_input()
        for primary, shadow in data_loader_generator:
            comparison = ResponseComparison(primary.response, shadow.response, primary.request)

            # Is this step actually necessary? Do we care about keeping these locally?
            self._comparisons_count += 1

            print(comparison.to_json(), flush=True, file=self._output)

        logger.info(f"All inputs processed. Generated {self._comparisons_count} comparisons.")
