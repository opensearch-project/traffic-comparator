import json
import logging
from typing import Optional

from deepdiff import DeepDiff

from traffic_comparator.data import Request, Response

logger = logging.getLogger(__name__)


class InvalidJsonForLoadingComparisonException(Exception):
    def __init__(self, original_exception) -> None:
        super().__init__("A comparison JSON line could not be loaded as valid json. "
                         f"Details: {str(original_exception)}")


class MissingFieldForLoadingComparisonJsonException(Exception):
    def __init__(self, field) -> None:
        super().__init__("A comparison JSON line could not be loaded because of a missing {field} field. ")


# These are volitaile or irrelevant paths that we want to ignore in our comparisons.
# In a future task (MIGRATIONS-863), this will be made customizable by the user, but for
# now, they're being hardcoded and will be updated as we test against new response types.
BODY_PATHS_TO_IGNORE = ["root['cluster_name']", "root['cluster_uuid']", "root['name']", "root['took']",
                        "root['tagline']", "root['version']", "root['_id']", "root['_shards']", "root['_seq_no']"]
HEADER_PATHS_TO_IGNORE = ["content-length", "access-control-allow-origin", "connection", "date",
                          "location"]


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
        self._headers_diff = DeepDiff(primary_response.headers, shadow_response.headers, ignore_string_case=True,
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
        if "raw_body" in base["primary_response"]:
            assert base["primary_response"]["raw_body"] is None
            del base["primary_response"]["raw_body"]
        base["shadow_response"] = self.shadow_response.__dict__
        if "raw_body" in base["shadow_response"]:
            assert base["shadow_response"]["raw_body"] is None
            del base["shadow_response"]["raw_body"]
        base["original_request"] = self.original_request.__dict__ if self.original_request else {}
        if "raw_body" in base["original_request"]:
            assert base["original_request"]["raw_body"] is None
            del base["original_request"]["raw_body"]
        # DeepDiff offers a `to_json` that returns a json string, but we want to embed the actual dictionary object,
        # not the string (otherwise it gets double escaped). DeepDiff objects do a have a `to_dict`, but it contains
        # elements that aren't json-escapable.
        base['_status_code_diff'] = json.loads(self.status_code_diff.to_json())
        base['_headers_diff'] = json.loads(self.headers_diff.to_json())
        base['_body_diff'] = json.loads(self.body_diff.to_json())
        return json.dumps(base)

    @classmethod
    def from_json(cls, line):
        try:
            source_dict = json.loads(line)
        except json.JSONDecodeError as e:
            raise InvalidJsonForLoadingComparisonException(e)
        
        if "original_request" in source_dict and source_dict["original_request"] != {}:
            original_request = Request(**source_dict["original_request"])
        else:
            original_request = None

        try:
            primary_response = Response(**source_dict["primary_response"])
        except KeyError:
            raise MissingFieldForLoadingComparisonJsonException("primary_response")

        try:
            shadow_response = Response(**source_dict["shadow_response"])
        except KeyError:
            raise MissingFieldForLoadingComparisonJsonException("shadow_response")

        comparison = object.__new__(cls)
        comparison.original_request = original_request
        comparison.primary_response = primary_response
        comparison.shadow_response = shadow_response
        comparison._body_diff = source_dict['_body_diff']
        comparison._headers_diff = source_dict['_headers_diff']
        comparison._status_code_diff = source_dict['_status_code_diff']

        return comparison
