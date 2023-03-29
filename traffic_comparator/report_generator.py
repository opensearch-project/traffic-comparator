import inspect
import logging
import sys
from datetime import datetime, timedelta
from typing import IO, Dict, Optional

import traffic_comparator.reports
from traffic_comparator.response_comparison import (
    InvalidJsonForLoadingComparisonException,
    MissingFieldForLoadingComparisonJsonException, ResponseComparison)

logger = logging.getLogger(__name__)


class UnsupportedReportTypeException(Exception):
    def __init__(self, report_name, original_exception) -> None:
        super().__init__(f"The report type '{report_name}' is unknown or unavailable. "
                         f"Details: {str(original_exception)}")


class StreamingReportGenerator:
    _available_reports = None
    
    def __init__(self, display_update_period: timedelta = timedelta(minutes=1)) -> None:
        self._data = []
        self._display_update_period = display_update_period
        self._display_last_updated: datetime = datetime.now()

    def _is_time_to_update_display(self) -> bool:
        return datetime.now() >= self._display_last_updated + self._display_update_period

    def _display_stats(self, override_update=False) -> None:
        if len(self._data) > 0 and (self._is_time_to_update_display() or override_update):
            print("=" * 40)
            print(f"as of {datetime.now()}:")

            # TODO: this is entirely un-optimized -- it recomputes the reports each time we need them.
            # For small-ish amounts of data, that's fine, but we should improve this down the road.
            correctness_report = traffic_comparator.reports.DiffReport(self._data)
            print(correctness_report)
            performance_report = traffic_comparator.reports.PerformanceReport(self._data)
            print(performance_report, flush=True)
            self._display_last_updated = datetime.now()

    def update(self, line: str) -> None:
        try:
            self._data.append(ResponseComparison.from_json(line))
        except InvalidJsonForLoadingComparisonException as e:
            logger.error(f"Comparison could not be loaded due to invalid json. Skipping line. Details: {e}")
        except MissingFieldForLoadingComparisonJsonException as e:
            logger.error(f"Comparison could not be loaded due to a missing field. Skipping line. Details: {e}")
        self._display_stats()

    def finalize(self) -> None:
        self._display_stats(override_update=True)

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

    def generate_final_report(self, report_name: str, export_file: IO):
        self._find_available_reports()
        # This satisfies the type checker that we can move forward.
        assert self._available_reports is not None
        try:
            report_class = self._available_reports[report_name]
        except KeyError as e:
            raise UnsupportedReportTypeException(report_name, e)
        
        report = report_class(self._data)
        report.compute()
        report.export(output_file=export_file)
