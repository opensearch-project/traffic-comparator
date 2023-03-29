import logging

from traffic_comparator.data_loader import StreamingDataLoader
from traffic_comparator.response_comparison import ResponseComparison

logger = logging.getLogger(__name__)


class StreamingAnalyzer:
    def __init__(self, dataLoader: StreamingDataLoader) -> None:
        self._data_loader = dataLoader
        self._comparisons = []

    def start(self):
        data_loader_generator = self._data_loader.next_input()
        for primary, shadow in data_loader_generator:
            comparison = ResponseComparison(primary.response, shadow.response, primary.request)

            # Is this step actually necessary? Do we care about keeping these locally?
            self._comparisons.append(comparison)

            print(comparison.to_json(), flush=True)

        logger.info(f"All inputs processed. Generated {len(self._comparisons)} comparisons.")
