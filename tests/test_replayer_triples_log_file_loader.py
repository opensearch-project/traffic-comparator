import json

import pytest

from traffic_comparator.log_file_loader import ReplayerTriplesFileLoader
from traffic_comparator.data import Request, Response

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
        "body": "{\n  \"name\" : \"primary-cluster-node-1\",\n  \"cluster_name\" : \"primary-cluster\",\n \"tagline\" : \"You Know, for Search\"\n}\n",  # noqa: E501
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
        "body": "{\n  \"name\" : \"3c22f.ant.amazon.com\",\n  \"cluster_name\" : \"elasticsearch\",\n  \"tagline\" : \"You Know, for Search\"\n}\n",  # noqa: E501
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
        "name": "primary-cluster-node-1",
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
        "name": "3c22f.ant.amazon.com",
        "cluster_name": "elasticsearch",
        "tagline": "You Know, for Search"
    }
)


@pytest.fixture
def valid_log_file(tmpdir):
    log_file = tmpdir / "config.json"
    log_file.write(json.dumps(LOG_ENTRY))
    return log_file


def test_WHEN_load_log_file_called_AND_valid_replayer_triples_THEN_returns_it(valid_log_file):
    log_file_loader = ReplayerTriplesFileLoader([valid_log_file])
    streams = log_file_loader.load()
    assert len(streams) == 2  # a primary stream and a shadow stream
    primaryStream = streams[0]
    shadowStream = streams[1]

    # Each of these should have one RequestResponsePair entry
    assert len(primaryStream) == 1
    assert len(shadowStream) == 1

    # Each of them should point to the other as the corresponding entry
    assert id(primaryStream[0].corresponding_pair) == id(shadowStream[0])
    assert id(shadowStream[0].corresponding_pair) == id(primaryStream[0])
    
    # The requests should be the same object.
    assert primaryStream[0].request == shadowStream[0].request
    assert primaryStream[0].request == LOG_ENTRY_REQUEST

    assert primaryStream[0].response == LOG_ENTRY_PRIMARY_RESPONSE
    assert shadowStream[0].response == LOG_ENTRY_SHADOW_RESPONSE
