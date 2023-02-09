import difflib
import json
from abc import ABC, abstractmethod
from typing import List, IO

from traffic_comparator.response_comparison import ResponseComparison


class BaseReport(ABC):
    """This is the base class for all reports. Each report should provide a docstring that explains the purpose
    of the report, as well as information on a potential outputted file (format, etc.) and any additional config
    or parameters to be provided.
    """
    def __init__(self, response_comparisons: List[ResponseComparison]):
        self._response_comparisons = response_comparisons
    
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
        self._percent_matching = 1.0 * self._number_identical / self._total_comparisons

    def __str__(self) -> str:
        return f"""
    {self._total_comparisons} responses were compared.
    {self._number_identical} were identical, for a match rate of {self._percent_matching}
    """

    def export(self, output_file: IO) -> None:
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
