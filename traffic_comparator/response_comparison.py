import logging

from deepdiff import DeepDiff

from traffic_comparator.data import Response
from traffic_comparator.data import Request

logger = logging.getLogger(__name__)


class ResponseComparison:
    def __init__(self, primary_response: Response, shadow_response: Response, original_request: Request = None) -> None:
        self.primary_response = primary_response
        self.shadow_response = shadow_response
        self.original_request = original_request
        # The reason behind adding a request to be part of the
        # response comparisons is to clarify what were these
        # responses for.

        # Depending on the performance of DeepDiff on large bodies, this could be pulled out.
        self._status_code_diff = DeepDiff(primary_response.statuscode, shadow_response.statuscode)
        self._headers_diff = DeepDiff(primary_response.headers, shadow_response.headers)
        self._body_diff = DeepDiff(primary_response.body, shadow_response.body)
        logger.debug(self._body_diff)

    @property
    def status_code_diff(self):
        return self._status_code_diff

    @property
    def headers_diff(self):
        return self._headers_diff

    @property
    def body_diff(self):
        return self._body_diff

    def is_identical(self):
        logger.debug(f"Identical?: {self.status_code_diff == {} and self.headers_diff == {} and self.body_diff == {}}")
        return self.status_code_diff == {} and self.headers_diff == {} and self.body_diff == {}
