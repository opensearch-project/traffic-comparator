import logging
from typing import Optional
import json

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

    def to_json(self) -> str:
        base = {}
        base["primary_response"] = self.primary_response.__dict__
        base["shadow_response"] = self.shadow_response.__dict__
        base["original_request"] = self.original_request.__dict__
        base['_status_code_diff'] = self.status_code_diff.to_json()
        base['_headers_diff'] = self.headers_diff.to_json()
        base['_body_diff'] = self.body_diff.to_json()
        return json.dumps(base)

    @classmethod
    def from_json(cls, line):
        source_dict = json.loads(line)
        original_request = Request(**source_dict["original_request"])
        primary_response = Response(**source_dict["primary_response"])
        shadow_response = Response(**source_dict["shadow_response"])

        # TODO: currently, this re-runs the comparison. This is computationally redundant,
        # but also, once we allow the user to specify masked fields, it will ignore those
        # when re-running it.
        # Options are to use cls.__new__ it instantiate an object without using the init method,
        # or to refactor the init method to only optionally do the diff computation.
        return cls(primary_response, shadow_response, original_request)
