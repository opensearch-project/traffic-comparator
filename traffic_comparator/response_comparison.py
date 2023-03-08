import logging
from typing import Optional

from deepdiff import DeepDiff

from traffic_comparator.data import Response, Request

logger = logging.getLogger(__name__)

# These are volitaile or irrelevant paths that we want to ignore in our comparisons.
# In a future task (MIGRATIONS-863), this will be made customizable by the user, but for
# now, they're being hardcoded and will be updated as we test against new response types.
BODY_PATHS_TO_IGNORE = ["root['cluster_name']", "root['cluster_uuid']", "root['name']", "root['took']",
                        "root['tagline']", "root['version']"]
HEADER_PATHS_TO_IGNORE = ["content-length"]


class ResponseComparison:
    def __init__(self, primary_response: Response, shadow_response: Response,
                 original_request: Optional[Request] = None) -> None:
        self.primary_response = primary_response
        self.shadow_response = shadow_response
        self.original_request = original_request
        # The reason behind adding a request to be part of the response comparisons
        # is to clarify what request led to these responses.

        # Depending on the performance of DeepDiff on large bodies, this could be pulled out to an async function.
        self._status_code_diff = DeepDiff(primary_response.statuscode, shadow_response.statuscode)
        self._headers_diff = DeepDiff(primary_response.headers, shadow_response.headers,
                                      exclude_paths=HEADER_PATHS_TO_IGNORE)
        self._body_diff = DeepDiff(primary_response.body, shadow_response.body,
                                   exclude_paths=BODY_PATHS_TO_IGNORE)
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

    def are_identical(self):
        logger.debug(f"Identical?: {self.status_code_diff == {} and self.headers_diff == {} and self.body_diff == {}}")
        return self.status_code_diff == {} and self.headers_diff == {} and self.body_diff == {}
