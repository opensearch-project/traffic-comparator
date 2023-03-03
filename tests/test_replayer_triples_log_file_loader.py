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

GZIP_LOG_ENTRY = {
    "request":
    {
        "host": "host.docker.internal",
        "Request-URI": "/geonames",
        "content-type": "application/json",
        "Method": "GET",
        "HTTP-Version": "HTTP/1.1",
        "body": "",
        "accept-encoding": "gzip, deflate",
        "Accept": "*/*"
    },
    "primaryResponse":
    {
        "content-length": "162",
        "content-encoding": "gzip",
        "content-type": "application/json; charset=UTF-8",
        "response_time_ms": 23,
        "HTTP-Version": "HTTP/1.1",
        "Status-Code": "404",
        "body": """\u001f�\b\u0000\u0000\u0000\u0000\u0000\u0000\u0000ԎA\n�@\bE�\u0012\\��EVs�\u0010
\u0006��v�ՠ#��ܽÔ@z��>���\rHU\u0014�\u0006*RbB7�0nP�K\r�y�5r]��y��&ZJ\u0016�\u001e��j\b�ҙ�G��n��0�Ȧ�|}�<W.2�晸&���
\u0010���hg�YG��v\u001e�S�/��`\u0005�\u001b��:�\u001f\u0000\u0000\u0000��\u0003\u0000�\u0013H�y\u0001\u0000\u0000""",
        "Reason-Phrase": "Not Found"
    },
    "shadowResponse":
    {
        "content-length": "367",
        "content-encoding": "gzip",
        "content-type": "application/json; charset=UTF-8",
        "response_time_ms": 12,
        "HTTP-Version": "HTTP/1.1",
        "Status-Code": "200",
        "body": """\u001f�\b\u0000\u0000\u0000\u0000\u0000\u0000\u0000�T�N�0\u0010�\u0017�EJ\u0002mZ6\u0006\u0006�
\u0018\u0010\f�\"׾�\u0016�ϲ�дʿc��\u0014$6gJ�{��w�N�\u0001�T�#�'B��n�\u001d\u0016DQc�nƀ�h�zqN�J�b�!
\u0006}ox8x� �\u0000�Ǣ\u000f�?���dAD��BEw؅�b�\u001a�p%���\\��s\u0001��\u0001,=XM=\\�IH�cBDܴ�1V$
\u0006�V{���.\u0007��� ��^�����\u001b\u0012��\u0006��0�LR7.F:%/��W�l\u000b�z}��$����\u0012��ͦ
\u001f+����q녂#ꤓ\u001c�ȁ���\t��\u0010uc6(\u00194�x���x��,�ˢ(��z\u001d�O�j\u0007�ºr{j�\t��ױ\u0005#
\u0005�S�m#��m����a�*{�\u001e��z��n\u001eBa\u0007֝Gj�\u001abv�gY��D��+w�\u0003��I���`��\u0017\u0000\u0000
\u0000��\u0003\u0000~��[�\u0005\u0000\u0000""",
        "Reason-Phrase": "OK"
    }
}

GZIP_LOG_ENTRY_REQUEST = Request(
    timestamp=None,
    http_method="GET",
    uri="/geonames",
    headers={
        "Accept": "*/*",
        "host": "host.docker.internal",
        "accept-encoding": "gzip, deflate",
        "content-type": "application/json",
    },
    body=""
)

GZIP_LOG_ENTRY_PRIMARY_RESPONSE = Response(
    timestamp=None,
    statuscode=404,
    headers={
        "content-length": "162",
        "content-type": "application/json; charset=UTF-8",
        "content-encoding": "gzip"
    },
    latency=23,
    body="""\u001f�\b\u0000\u0000\u0000\u0000\u0000\u0000\u0000ԎA\n�@\bE�\u0012\\��EVs�\u0010
\u0006��v�ՠ#��ܽÔ@z��>���\rHU\u0014�\u0006*RbB7�0nP�K\r�y�5r]��y��&ZJ\u0016�\u001e��j\b�ҙ�G��n��0�Ȧ�|}�<W.2�晸&���
\u0010���hg�YG��v\u001e�S�/��`\u0005�\u001b��:�\u001f\u0000\u0000\u0000��\u0003\u0000�\u0013H�y\u0001\u0000\u0000"""
)

GZIP_LOG_ENTRY_SHADOW_RESPONSE = Response(
    timestamp=None,
    statuscode=200,
    headers={
        "content-length": "367",
        "content-type": "application/json; charset=UTF-8",
        "content-encoding": "gzip"
    },
    latency=12,
    body="""\u001f�\b\u0000\u0000\u0000\u0000\u0000\u0000\u0000�T�N�0\u0010�\u0017�EJ\u0002mZ6\u0006\u0006�
\u0018\u0010\f�\"׾�\u0016�ϲ�дʿc��\u0014$6gJ�{��w�N�\u0001�T�#�'B��n�\u001d\u0016DQc�nƀ�h�zqN�J�b�!
\u0006}ox8x� �\u0000�Ǣ\u000f�?���dAD��BEw؅�b�\u001a�p%���\\��s\u0001��\u0001,=XM=\\�IH�cBDܴ�1V$
\u0006�V{���.\u0007��� ��^�����\u001b\u0012��\u0006��0�LR7.F:%/��W�l\u000b�z}��$����\u0012��ͦ
\u001f+����q녂#ꤓ\u001c�ȁ���\t��\u0010uc6(\u00194�x���x��,�ˢ(��z\u001d�O�j\u0007�ºr{j�\t��ױ\u0005#
\u0005�S�m#��m����a�*{�\u001e��z��n\u001eBa\u0007֝Gj�\u001abv�gY��D��+w�\u0003��I���`��\u0017\u0000\u0000
\u0000��\u0003\u0000~��[�\u0005\u0000\u0000"""
)


@pytest.fixture
def valid_log_file(tmpdir):
    log_file = tmpdir / "triple.json"
    log_file.write(json.dumps(LOG_ENTRY))
    return log_file


@pytest.fixture
def gzipped_log_file(tmpdir):
    log_file = tmpdir / "gzip-triple.json"
    log_file.write(json.dumps(GZIP_LOG_ENTRY))
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


def test_WHEN_load_log_file_called_AND_valid_replayer_triples_AND_gzipped_responses_THEN_returns_it(gzipped_log_file):
    # In the future, we should uncompress the gzipped file, but for now, we just preserve it as a string.
    log_file_loader = ReplayerTriplesFileLoader([gzipped_log_file])
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
    assert primaryStream[0].request == GZIP_LOG_ENTRY_REQUEST

    assert primaryStream[0].response == GZIP_LOG_ENTRY_PRIMARY_RESPONSE
    assert shadowStream[0].response == GZIP_LOG_ENTRY_SHADOW_RESPONSE
