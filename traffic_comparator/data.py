from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional, TypeAlias, Union


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
    headers: Union[dict, str, None] = None  # maybe dict or list?
    body: Union[dict, str, None] = None

    def equivalent_to(self, other: Request):
        return (self.http_method, self.uri, self.headers, self.body) == \
            (other.http_method, other.uri, other.headers, other.body)


@dataclass
class Response:
    timestamp: Optional[int] = None  # int in epoch seconds format
    statuscode: Optional[int] = None
    headers: Union[dict, str, None] = None
    body: Union[dict, str, None] = None
    latency: Optional[int] = None  # Latency in ms


@dataclass
class RequestResponsePair:
    request: Request
    response: Response
    corresponding_pair: Optional[RequestResponsePair] = None

    @property
    def latency(self):
        return self.response.latency


RequestResponseStream: TypeAlias = List[RequestResponsePair]
