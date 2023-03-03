import logging
from typing import List, Tuple

from traffic_comparator.data import RequestResponseStream, RequestResponsePair
from traffic_comparator.data_loader import DataLoader
from traffic_comparator.response_comparison import ResponseComparison

logger = logging.getLogger(__name__)


class Analyzer:
    def __init__(self, dataLoader: DataLoader) -> None:
        self._primary_stream: RequestResponseStream = dataLoader.primary_data_stream
        self._shadow_stream: RequestResponseStream = dataLoader.shadow_data_stream

        logger.info(f"Analyzer initialized with primary data stream of {len(self._primary_stream)} items and "
                    f"shadow data stream of {len(self._shadow_stream)} items.")

    def analyze(self) -> Tuple[List[ResponseComparison], List[RequestResponsePair]]:
        """
        Run through each correlated pair of requests and compare the responses.
        """

        comparisons = []
        skipped_requests = []
        for primary_pair in self._primary_stream:
            if primary_pair.corresponding_pair is not None:
                comparisons.append(ResponseComparison(primary_pair.response,
                                                      primary_pair.corresponding_pair.response,
                                                      primary_pair.request))
            else:
                skipped_requests.append(primary_pair)
        logger.info(f"{len(comparisons)} comparisons generated.")
        return comparisons, skipped_requests
