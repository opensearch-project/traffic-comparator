import json
from contextlib import contextmanager
from io import StringIO
from unittest.mock import patch

from traffic_comparator.data import Request, RequestResponsePair, Response
from traffic_comparator.data_loader import StreamingDataLoader

LOG_ENTRY = {
    "request":
    {
        "Accept": "*/*",
        "User-Agent": "curl/7.61.1",
        "Request-URI": "/",
        "Host": "localhost:9200",
        "Method": "GET",
        "HTTP-Version": "HTTP/1.1",
        "body": ""
    },
    "primaryResponse":
    {
        "HTTP-Version": "HTTP/1.1",
        "Reason-Phrase": "OK",
        "Status-Code": "200",
        "body": "{\n  \"cluster_name\" : \"primary-cluster\",\n \"tagline\" : \"You Know, for Search\"\n}\n",  # noqa: E501
        "content-length": "549",
        "content-type": "application/json; charset=UTF-8",
        "response_time_ms": 14
    },
    "shadowResponse":
    {
        "content-length": "549",
        "content-type": "application/json; charset=UTF-8",
        "response_time_ms": 199,
        "HTTP-Version": "HTTP/1.1",
        "Status-Code": "200",
        "body": "{\n  \"cluster_name\" : \"elasticsearch\",\n  \"tagline\" : \"You Know, for Search\"\n}\n",  # noqa: E501
        "Reason-Phrase": "OK"
    }
}

LOG_ENTRY_REQUEST = Request(
    timestamp=None,
    http_method="GET",
    uri="/",
    headers={
        "Accept": "*/*",
        "User-Agent": "curl/7.61.1",
        "Host": "localhost:9200"
    },
    body=""
)

LOG_ENTRY_PRIMARY_RESPONSE = Response(
    timestamp=None,
    statuscode=200,
    headers={
        "content-length": "549",
        "content-type": "application/json; charset=UTF-8"
    },
    latency=14,
    body={
        "cluster_name": "primary-cluster",
        "tagline": "You Know, for Search"
    }
)

LOG_ENTRY_SHADOW_RESPONSE = Response(
    timestamp=None,
    statuscode=200,
    headers={
        "content-length": "549",
        "content-type": "application/json; charset=UTF-8"
    },
    latency=199,
    body={
        "cluster_name": "elasticsearch",
        "tagline": "You Know, for Search"
    }
)


@contextmanager
def input(*lines):
    """Replace stdin input with specifies lines."""
    lines = "\n".join(lines)
    with patch("sys.stdin", StringIO(f"{lines}\n")):
        yield


def test_WHEN_streamingdataloader_has_stdin_line_THEN_loads():
    sdl = StreamingDataLoader()
    with input(json.dumps(LOG_ENTRY)):
        input_generator = sdl.next_input()
        line_count = 0
        for line in input_generator:
            line_count += 1
            assert len(line) == 2
            assert type(line[0]) is RequestResponsePair
            assert type(line[1]) is RequestResponsePair
            assert id(line[0].corresponding_pair) == id(line[1])
            assert id(line[1].corresponding_pair) == id(line[0])
            assert line[0].request == LOG_ENTRY_REQUEST
            assert line[0].response == LOG_ENTRY_PRIMARY_RESPONSE
            assert line[1].request == LOG_ENTRY_REQUEST
            assert line[1].response == LOG_ENTRY_SHADOW_RESPONSE
    assert line_count == 1


def test_WHEN_streamingdataloader_has_multiple_stdin_lines_THEN_loads_all():
    sdl = StreamingDataLoader()
    with input(*map(json.dumps, [LOG_ENTRY] * 10)):
        input_generator = sdl.next_input()
        line_count = 0
        for line in input_generator:
            line_count += 1
            assert len(line) == 2
            assert type(line[0]) is RequestResponsePair
            assert type(line[1]) is RequestResponsePair

    assert line_count == 10
