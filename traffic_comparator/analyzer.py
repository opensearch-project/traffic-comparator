import logging
from typing import List, Tuple

from traffic_comparator.data import RequestResponseStream, RequestResponsePair
from traffic_comparator.data_loader import DataLoader
from traffic_comparator.log_file_loader import LogFileFormat
from traffic_comparator.response_comparison import ResponseComparison

logger = logging.getLogger(__name__)


class Analyzer:
    def __init__(self, dataLoader: DataLoader) -> None:
        self._primary_stream: RequestResponseStream = dataLoader.primary_data_stream
        self._shadow_stream: RequestResponseStream = dataLoader.shadow_data_stream

        logger.info(f"Analyzer initialized with primary data stream of {len(self._primary_stream)} items and "
                    f"shadow data stream of {len(self._shadow_stream)} items.")

        # Some data formats may come already correlated, but haproxy-jsons are not one of them.
        if dataLoader.log_file_format == LogFileFormat.HAPROXY_JSONS:
            self._correlated_data = False

    def _correlate_data_streams(self) -> None:
        """
        The Analyzer is initialized with primary and shadow streams that have not been
        correlated to each other--we don't yet know which requests to compare to each other.
        This has to be done before the responses can be compared.
        """
        # This is a copy of the _shadow_stream list. The RequestResponsePairs are the same objects
        # (i.e. passed by reference) so we can modify them.
        uncorrelated_shadow_pairs = self._shadow_stream[:]
        uncorrelated_primary_reqs_count = 0

        # This should go through primary requests in (roughly) sequential order.
        # They will be compared to the shadow requests--looking for an identical request at time >= t0.
        # Currently this is an O(n^2) process -- that's not sustainable! We need to either correlate at
        # source or improve this matching (dividing by uri/method might be a start)
        # Theortically, it'll be in much closer to O(N) because they should come in roughly the same order.
        for primary_pair in self._primary_stream:
            primary_request = primary_pair.request

            # Can't match a request without a timestamp.
            if primary_request.timestamp is None:
                continue

            # Search only within the unmatched shadow requests
            for shadow_pair in uncorrelated_shadow_pairs:
                shadow_request = shadow_pair.request

                # Ignore responses without a timestamp. Maybe I should just make this a required field?
                if shadow_request.timestamp is None:
                    continue

                if primary_request.equivalent_to(shadow_request) and \
                        primary_request.timestamp <= shadow_request.timestamp:
                    uncorrelated_shadow_pairs.remove(shadow_pair)
                    shadow_pair.corresponding_pair = primary_pair
                    primary_pair.corresponding_pair = shadow_pair
                    break
            if primary_pair.corresponding_pair is None:
                uncorrelated_primary_reqs_count += 1
                logger.debug(f"Primary request with timestamp {primary_request.timestamp} "
                             "could not find a corresponding shadow request.")
        logger.info(f"Correlating streams finished with {uncorrelated_primary_reqs_count} uncorrelated primary "
                    f"requests and {len(uncorrelated_shadow_pairs)} uncorrelated shadow requests.")

    def analyze(self) -> Tuple[List[ResponseComparison], List[RequestResponsePair]]:
        """
        Run through each correlated pair of requests and compare the responses.
        """
        # The comparisons can't be created until the requests are correlated, so that's a pre-req to analyzing if it
        # didn't happen when the data was loaded.
        if not self._correlated_data:
            self._correlate_data_streams()

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
