import logging

from deepdiff import DeepDiff

from traffic_comparator.data import Response

logger = logging.getLogger(__name__)

# These are volitaile or irrelevant paths that we want to ignore in our comparisons.
# In a future task (MIGRATIONS-863), this will be made customizable by the user, but for
# now, they're being hardcoded and will be updated as we test against new response types.
BODY_PATHS_TO_IGNORE = ["root['cluster_name']", "root['cluster_uuid']", "root['name']", "root['took']"]
BODY_PATH_REGEXES_TO_IGNORE = [r"root['nodes']['\w+']['host']",
                               r"root['nodes']['\w+']['ip']",
                               r"root['nodes']['\w+']['http']['publish_address']",
                               r"root['nodes']['\w+']['name']"
                               ]
HEADER_PATHS_TO_IGNORE = ["content-length"]


class ResponseComparison:
    def __init__(self, primary_response: Response, shadow_response: Response) -> None:
        self.primary_response = primary_response
        self.shadow_response = shadow_response

        # Depending on the performance of DeepDiff on large bodies, this could be pulled out.
        self._status_code_diff = DeepDiff(primary_response.statuscode, shadow_response.statuscode)
        self._headers_diff = DeepDiff(primary_response.headers, shadow_response.headers,
                                      exclude_paths=HEADER_PATHS_TO_IGNORE)
        self._body_diff = DeepDiff(primary_response.body, shadow_response.body,
                                   exclude_paths=BODY_PATHS_TO_IGNORE,
                                   exclude_regex_paths=BODY_PATH_REGEXES_TO_IGNORE)
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
        return self.status_code_diff == {} and self.headers_diff == {} and self.body_diff == {}
