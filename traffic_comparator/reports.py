import difflib
import json
from abc import ABC, abstractmethod
from typing import List, IO
import numpy as np
from traffic_comparator.response_comparison import ResponseComparison
from traffic_comparator.data import RequestResponsePair
import csv


class BaseReport(ABC):
    """This is the base class for all reports. Each report should provide a docstring that explains the purpose
    of the report, as well as information on a potential outputted file (format, etc.) and any additional config
    or parameters to be provided.
    """
    def __init__(self, response_comparisons: List[ResponseComparison], uncompared_requests: List[RequestResponsePair]):
        self._response_comparisons = response_comparisons
        self._uncompared_requests = uncompared_requests
        self._computed = False
    
    @abstractmethod
    def compute(self) -> None:
        pass

    @abstractmethod
    def __str__(self) -> str:
        pass

    @abstractmethod
    def export(self, output_file: IO) -> None:
        pass


class BasicCorrectnessReport(BaseReport):
    """Provides basic information on how many and what ratio of responses are succesfully matched.
    The exported file provides the same summary as the cli and then a list of diffs for every response
    that does not match.
    """
    def compute(self) -> None:
        self._total_comparisons = len(self._response_comparisons)
        self._number_identical = sum([comp.is_identical() for comp in self._response_comparisons])
        self._statuses_identical = sum([comp.primary_response.statuscode == comp.shadow_response.statuscode
                                        for comp in self._response_comparisons])
        if self._total_comparisons != 0:
            self._percent_matching = 1.0 * self._number_identical / self._total_comparisons
            self._percent_statuses_matching = 1.0 * self._statuses_identical / self._total_comparisons
        else:
            self._percent_matching = 0
            self._percent_statuses_matching = 0
        self._number_skipped = len(self._uncompared_requests)
        self._computed = True

    def __str__(self) -> str:
        if not self._computed:
            self.compute()

        return f"""
    {self._number_identical} were identical, for a match rate of {self._percent_matching:.2%}
    The status codes matched in {self._percent_statuses_matching:.2%} of responses.
    {self._number_skipped} requests from the primary cluster were not matched with a request from the shadow cluster.
    """

    def export(self, output_file: IO) -> None:
        if not self._computed:
            self.compute()

        # I'm using the DeepDiff library to generate diffs, but difflib (from the stdlib) to display them.
        # This is fine for now, but it may be better to synchronize them down the line.

        d = difflib.Differ()

        # Write the CLI output at the top of the file.
        output_file.write(str(self))
        output_file.write("\n")

        # Write each non-matching comparison
        for comp in self._response_comparisons:
            if comp.is_identical():
                continue
            output_file.write('=' * 40)
            output_file.write("\n")
            # Write each response to a json and split the lines (necessary input format for difflib)
            primary_response_lines = [f"Status code: {comp.primary_response.statuscode}",
                                      f"Headers: {comp.primary_response.headers}"] + \
                json.dumps(comp.primary_response.body, sort_keys=True, indent=4).splitlines()
            shadow_response_lines = [f"Status code: {comp.shadow_response.statuscode}",
                                     f"Headers: {comp.shadow_response.headers}"] + \
                json.dumps(comp.shadow_response.body, sort_keys=True, indent=4).splitlines()

            result = list(d.compare(primary_response_lines, shadow_response_lines))
            output_file.write("\n".join(result))
            output_file.write("\n")


class PerformanceReport(BaseReport):
    """Provides basic performance data including: average, median, p90 and p99 latencies.
    The exported file provides a CSV file which lists response body, latency and status code of both primary
    and shadow cluster for to each request.
    """
    def compute(self) -> None:
        self._primary_latencies = []
        self._shadow_latencies = []
        for resp in self._response_comparisons:
            if resp.primary_response.latency and resp.primary_response.latency > 0:
                self._primary_latencies.append(resp.primary_response.latency)
            if resp.shadow_response.latency and resp.shadow_response.latency > 0:
                self._shadow_latencies.append(resp.shadow_response.latency)

        self._computed = True

    def __str__(self) -> str:
        # pull in data computed in compute and print the averages
        if not self._computed:
            self.compute()

        # I'm using NumPy to calculate performance metrics

        return f"""
            ==Stats for primary cluster==
    99th percentile = {'%.1f' % np.percentile(self._primary_latencies, 99)}
    90th percentile = {'%.1f' % np.percentile(self._primary_latencies, 90)}
    50th percentile = {'%.1f' % np.percentile(self._primary_latencies, 50)}
    Average Latency = {'%.1f' % np.average(self._primary_latencies)}
    
            ==Stats for shadow cluster==
    99th percentile = {'%.1f' % np.percentile(self._shadow_latencies, 99)}
    90th percentile = {'%.1f' % np.percentile(self._shadow_latencies, 90)}
    50th percentile = {'%.1f' % np.percentile(self._shadow_latencies, 50)}
    Average Latency = {'%.1f' % np.average(self._shadow_latencies)}
    """

    def export(self, output_file: IO) -> None:
        writer = csv.writer(output_file)
        writer.writerow(['request_uri', 'request_method',
                         'request_body', 'primary_response_latency_ms', 'primary_response_status_code',
                         'primary_response_body', 'shadow_response_latency_ms', 'shadow_response_status_code',
                         'shadow_response_body'])
        for resp in self._response_comparisons:
            writer.writerow([resp.original_request.uri if resp.original_request else None,
                            resp.original_request.http_method if resp.original_request else None,
                            resp.original_request.body if resp.original_request else None,
                            resp.primary_response.latency,
                            resp.primary_response.statuscode,
                            resp.primary_response.body,
                            resp.shadow_response.latency,
                            resp.shadow_response.statuscode,
                            resp.shadow_response.body])
