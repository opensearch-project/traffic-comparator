import inspect
import logging
import sys
from typing import Dict, Type, Optional, IO

import traffic_comparator.reports
from traffic_comparator.data import RequestResponseStream
from traffic_comparator.data_loader import DataLoader
from traffic_comparator.response_comparison import ResponseComparison

logger = logging.getLogger(__name__)


class UnsupportedReportTypeException(Exception):
    def __init__(self, report_name, original_exception) -> None:
        super().__init__(f"The report type '{report_name}' is unknown or unavailable. "
                         f"Details: {str(original_exception)}")


class Analyzer:
    _available_reports: Optional[Dict[str, Type[traffic_comparator.reports.BaseReport]]] = None
    
    def __init__(self, dataLoader: DataLoader) -> None:
        self._primary_stream: RequestResponseStream = dataLoader.primary_data_stream
        self._shadow_stream: RequestResponseStream = dataLoader.shadow_data_stream

        logger.info(f"Analyzer initialized with primary data stream of {len(self._primary_stream)} items and "
                    f"shadow data stream of {len(self._shadow_stream)} items.")

        self._correlate_data_streams()
        self._find_available_reports()

        self._computed_reports = {}

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
        
    def analyze(self) -> None:
        """
        Run through each correlated pair of requests and compare the responses.
        """
        self.comparisons = []
        for primary_pair in self._primary_stream:
            # Right now I'm only dealing with primary requests that have a corresponding request,
            # and skipping the rest. I should maybe also highlight the ones that don't have a match.
            if primary_pair.corresponding_pair is not None:
                self.comparisons.append(ResponseComparison(primary_pair.response,
                                                           primary_pair.corresponding_pair.response))
        logger.info(f"{len(self.comparisons)} comparisons generated.")
        logger.debug(self.comparisons)

    @classmethod
    def _find_available_reports(cls) -> None:
        # This is essentially the discovery mechanism for report plugins. New report options can be
        # added to the reports module (currently just a single file) and will be discovered here.

        report_module = "traffic_comparator.reports"
        base_report = traffic_comparator.reports.BaseReport
        cls._available_reports = {name: obj for name, obj in inspect.getmembers(sys.modules[report_module])
                                  if inspect.isclass(obj) and issubclass(obj, base_report) and obj is not base_report}
        logger.info(f"Reports found: {list(cls._available_reports.keys())}")

    @classmethod
    def available_reports(cls) -> Dict[str, Optional[str]]:
        if cls._available_reports is None:
            cls._find_available_reports()

        # This satisfies the type checker that we can move forward.
        assert cls._available_reports is not None
        return {name: report.__doc__ for name, report in cls._available_reports.items()}

    def generate_report(self, report_name: str, export=False, export_file: Optional[IO] = None):
        if report_name in self._computed_reports:
            report = self._computed_reports[report_name]
        else:
            if self._available_reports is None:
                self._find_available_reports()
            # This satisfies the type checker that we can move forward.
            assert self._available_reports is not None
            try:
                report_class = self._available_reports[report_name]
            except KeyError as e:
                raise UnsupportedReportTypeException(report_name, e)
            report = report_class(self.comparisons)
            report.compute()
            self._computed_reports[report_name] = report
        
        if export and export_file:
            report.export(output_file=export_file)
        else:
            return str(report)
