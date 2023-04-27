from __future__ import annotations

import base64
import gzip
import json
import logging
from collections import namedtuple
from dataclasses import dataclass
from typing import List, Optional, Union

logger = logging.getLogger(__name__)


def decodeAndDecompressBody(raw_body: bytes, is_gzipped: bool, charset: str = 'utf-8') -> str:
    b64decoded = base64.b64decode(raw_body)
    if is_gzipped:
        try:
            return gzip.decompress(b64decoded).decode(charset)
        except gzip.BadGzipFile as e:
            logger.error(f"Encountered error unpacking gzipped message: {e}")
            logger.debug(f"Original message: {b64decoded}")
            return ""
    return b64decoded.decode(charset)


def parseBodyAsJson(body: str) -> Union[dict, str]:
    try:
        return json.loads(body)
    except json.JSONDecodeError as e:
        logger.info("Message body could not be loaded as json, returning as string instead. "
                    f"Details: {e}")
        return body


def parseBodyAsBulk(body: str) -> List[dict]:
    bulk_lines = body.splitlines()
    bulk_jsons = []
    for line in bulk_lines:
        try:
            bulk_jsons.append(json.loads(line))
        except json.JSONDecodeError as e:
            logger.error("A line of a bulk request could not be loaded as json. "
                         f"Details: {e}")
    return bulk_jsons


@dataclass
class Request:
    """
    These classes are intentionally very flexible to accomodate whatever data we get from the log file.
    If necessary data is missing, the Analyzer can decide whether to just drop a request from
    the calculation or throw an exception.
    """
    timestamp: Optional[int] = None  # int in epoch seconds format
    http_method: Optional[str] = None  # could be an enum
    uri: Optional[str] = None
    headers: Union[dict, str, None] = None
    raw_body: Optional[bytes] = None
    body: Union[dict, str, List[dict], None] = None

    def __post_init__(self):
        """This method is called after the initialization, and is used to
        decode and decompress the raw body, as applicable."""
        if self.body and not self.raw_body:
            # This is the case where it was already intantiated and is being recreated
            # for the report generator.
            return

        has_body = self.raw_body is not None and len(self.raw_body) > 0
        is_gzipped = type(self.headers) is dict and \
            "content-encoding" in self.headers and \
            self.headers["content-encoding"] == "gzip"
        is_bulk = self.uri is not None and "_bulk" in self.uri

        if not has_body:
            self.body = None
            self.raw_body = None
            return
        # This assert matches the criteria of has_body. It's necessary for the type checking to trust the next line.
        assert self.raw_body is not None
        decoded_body = decodeAndDecompressBody(self.raw_body, is_gzipped)
        self.body = parseBodyAsBulk(decoded_body) if is_bulk else parseBodyAsJson(decoded_body)
        self.raw_body = None

    def equivalent_to(self, other: Request):
        return (self.http_method, self.uri, self.headers, self.body) == \
            (other.http_method, other.uri, other.headers, other.body)


@dataclass
class Response:
    timestamp: Optional[int] = None  # int in epoch seconds format
    statuscode: Optional[int] = None
    headers: Union[dict, None] = None
    body: Union[dict, str, None] = None
    latency: Optional[int] = None  # Latency in ms
    raw_body: Optional[bytes] = None
    body: Union[dict, str, None] = None

    def __post_init__(self):
        """This method is called after the initialization, and is used to
        decode and decompress the raw body, as applicable."""
        if self.body and not self.raw_body:
            # This is the case where it was already intantiated and is being recreated
            # for the report generator. The body is already prepared.
            return

        has_body = self.raw_body is not None and len(self.raw_body) > 0
        is_gzipped = type(self.headers) is dict and \
            "content-encoding" in self.headers and \
            self.headers["content-encoding"] == "gzip"

        if not has_body:
            self.body = None
            self.raw_body = None
            return
        # This assert matches the criteria of has_body. It's necessary for the type checking to trust the next line.
        assert self.raw_body is not None
        decoded_body = decodeAndDecompressBody(self.raw_body, is_gzipped)
        self.body = parseBodyAsJson(decoded_body)  # Responses are never bulk calls
        self.raw_body = None

        # Process the headers to make all keys lower case, allowing for more consistent comparisons.
        self.headers = {k.lower(): v for k, v in self.headers.items()} if self.headers else None


@dataclass
class RequestResponsePair:
    request: Request
    response: Response
    corresponding_pair: Optional[RequestResponsePair] = None

    @property
    def latency(self):
        return self.response.latency


MatchedRequestResponsePair = namedtuple('MatchedResponsePairs', ['primary', 'shadow'])
