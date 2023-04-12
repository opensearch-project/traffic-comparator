import base64
import json
from io import StringIO

from traffic_comparator.data import Request, Response
from traffic_comparator.log_file_loader import ReplayerTriplesFileLoader


def toBase64String(s: str):
    return base64.b64encode(s.encode('utf-8')).decode('utf-8')


LOG_ENTRY = {
    "request":
    {
        "Accept": "*/*",
        "User-Agent": "curl/7.61.1",
        "Request-URI": "/",
        "Host": "localhost:9200",
        "Method": "GET",
        "HTTP-Version": "HTTP/1.1",
        "body": toBase64String("")
    },
    "primaryResponse":
    {
        "HTTP-Version": "HTTP/1.1",
        "Reason-Phrase": "OK",
        "Status-Code": "200",
        "body": toBase64String("{\n  \"name\" : \"primary-cluster-node-1\",\n  \"cluster_name\" : \"primary-cluster\",\n \"tagline\" : \"You Know, for Search\"\n}\n"),  # noqa: E501
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
        "body": toBase64String("{\n  \"name\" : \"3c22f.ant.amazon.com\",\n  \"cluster_name\" : \"elasticsearch\",\n  \"tagline\" : \"You Know, for Search\"\n}\n"),  # noqa: E501
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
        "body": "",
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
        "body": """H4sIAAAAAAAAALRUy27DIBD8F86pFNt5uL31kj4OrZQoZ4vA2l0VA+LhJI387wU3adNKveETiF0GdmZ3TqQBJWkLltydCBVI7bDt
        J6SlWqNshoA2SoNxeE7jLcqsYopDDLqjDitxcHBkQmoEwYdL73DcK8OvUi4nE4KNVAYqulNduJvPF30fnqQROB8LuBgLeDYGsHBgJHXwLU5Cmi1
        DjLhp1WMsTwyovHTmOAK7HNq0XwUBHXWo5BWsULIhoatroM6HZmeC2mEw0in5DZ18FM+2gNfjeylIKPa31loo6mKx6dtKK+3Ff9w6bOFDyaSdHJ
        3IgnMX80PJ4RB1YyYoGTSueJjL4HjZopyW5e2yKKeLIlif9O0OTKXqyr5RE02QzH8dG9ACGY2BLAS8j/SSVfPyuN7fLDcb8A+vT9v982q9vQ/xD
        ow9t9TwNMTsrJjns3KaLyPbwZc75MCrL9p/zDzYaf8JAAD//wMAQEUGT9wFAAA=""",
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
    body=""
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
    body={'geonames':
          {'aliases': {},
           'mappings':
               {'properties': {
                'admin1_code': {'type': 'text', 'fields': {'keyword': {'type': 'keyword', 'ignore_above': 256}}},
                'admin2_code': {'type': 'text', 'fields': {'keyword': {'type': 'keyword', 'ignore_above': 256}}},
                'admin3_code': {'type': 'text', 'fields': {'keyword': {'type': 'keyword', 'ignore_above': 256}}},
                'admin4_code': {'type': 'text', 'fields': {'keyword': {'type': 'keyword', 'ignore_above': 256}}},
                'alternatenames': {'type': 'text', 'fields': {'keyword': {'type': 'keyword', 'ignore_above': 256}}},
                'asciiname': {'type': 'text', 'fields': {'keyword': {'type': 'keyword', 'ignore_above': 256}}},
                'cc2': {'type': 'text', 'fields': {'keyword': {'type': 'keyword', 'ignore_above': 256}}},
                'country_code': {'type': 'text', 'fields': {'keyword': {'type': 'keyword', 'ignore_above': 256}}},
                'dem': {'type': 'text', 'fields': {'keyword': {'type': 'keyword', 'ignore_above': 256}}},
                'elevation': {'type': 'long'},
                'feature_class': {'type': 'text', 'fields': {'keyword': {'type': 'keyword', 'ignore_above': 256}}},
                'feature_code': {'type': 'text', 'fields': {'keyword': {'type': 'keyword', 'ignore_above': 256}}},
                'geonameid': {'type': 'long'}, 'location': {'type': 'float'},
                'name': {'type': 'text', 'fields': {'keyword': {'type': 'keyword', 'ignore_above': 256}}},
                'population': {'type': 'long'},
                'timezone': {'type': 'text', 'fields': {'keyword': {'type': 'keyword', 'ignore_above': 256}}}}},
           'settings': {'index': {'creation_date': '1680889738063', 'number_of_shards': '5', 'number_of_replicas': '1',
                                  'uuid': 'FgNHRw-7SSeuGOIUwJFRUA', 'version': {'created': '135248027'},
                                  'provided_name': 'geonames'}}}}
)

BULK_API_LOG_ENTRY = {
    "request":
    {
        "content-length": "700",
        "host": "host.docker.internal",
        "Request-URI": "/_bulk",
        "content-type": "application/json",
        "Method": "POST",
        "HTTP-Version": "HTTP/1.1",
        "body": "eyJpbmRleCI6IHsiX2luZGV4IjogImdlb25hbWVzIn19CnsiZ2VvbmFtZWlkIjogMzAzODgxNSwgIm5hbWUiOiAiRm9udCBkZSBsYSBYb25hIiwgImNvdW50cnlfY29kZSI6ICJBRCIsICJ0aW1lem9uZSI6ICJFdXJvcGUvQW5kb3JyYSIsICJsb2NhdGlvbiI6IFsxLjQ0OTg2LCA0Mi41NTAwM119CnsiaW5kZXgiOiB7Il9pbmRleCI6ICJnZW9uYW1lcyJ9fQp7Imdlb25hbWVpZCI6IDMwMzg4MTYsICJuYW1lIjogIlhpeGVyZWxsYSIsICJjb3VudHJ5X2NvZGUiOiAiQUQiLCAidGltZXpvbmUiOiAiRXVyb3BlL0FuZG9ycmEiLCAibG9jYXRpb24iOiBbMS40ODczNiwgNDIuNTUzMjddfQp7ImluZGV4IjogeyJfaW5kZXgiOiAiZ2VvbmFtZXMifX0KeyJnZW9uYW1laWQiOiAzMDM4ODE3LCAibmFtZSI6ICJYaXhlcmVsbGEiLCAiYWx0ZXJuYXRlbmFtZXMiOiAiWGl4ZXJlbGxhIiwgImNvdW50cnlfY29kZSI6ICJBRCIsICJ0aW1lem9uZSI6ICJFdXJvcGUvQW5kb3JyYSIsICJsb2NhdGlvbiI6IFsxLjQ4NzY0LCA0Mi41NTI5NF19",  # noqa E501
        "accept-encoding": "gzip, deflate",
        "user-agent": "opensearch-py/1.0.0 (Python 3.8.10)",
        "accept": "*/*"
    },
    "primaryResponse":
    {
        "content-length": "276",
        "content-encoding": "gzip",
        "content-type": "application/json; charset=UTF-8",
        "response_time_ms": 38,
        "HTTP-Version": "HTTP/1.1",
        "Status-Code": "200",
        "body": "",
        "Reason-Phrase": "OK"
    },
    "shadowResponse":
    {
        "content-encoding": "gzip",
        "Connection": "keep-alive",
        "response_time_ms": 136,
        "HTTP-Version": "HTTP/1.1",
        "Status-Code": "200",
        "Content-Length": "282",
        "body": "",
        "Reason-Phrase": "OK",
        "Date": "Fri, 07 Apr 2023 17:57:30 GMT",
        "Content-Type": "application/json; charset=UTF-8"
    }
}

BULK_API_ENTRY_REQUEST = Request(
    timestamp=None,
    http_method="POST",
    uri="/_bulk",
    headers={
        "accept": "*/*",
        "host": "host.docker.internal",
        "accept-encoding": "gzip, deflate",
        "content-type": "application/json",
        "content-length": "700",
        "user-agent": "opensearch-py/1.0.0 (Python 3.8.10)"
    },
    body=[{'index': {'_index': 'geonames'}},
          {'geonameid': 3038815,
           'name': 'Font de la Xona',
           'country_code': 'AD',
           'timezone': 'Europe/Andorra',
           'location': [1.44986, 42.55003]},
          {'index': {'_index': 'geonames'}},
          {'geonameid': 3038816,
           'name': 'Xixerella',
           'country_code': 'AD',
           'timezone': 'Europe/Andorra',
           'location': [1.48736, 42.55327]},
          {'index': {'_index': 'geonames'}},
          {'geonameid': 3038817,
           'name': 'Xixerella',
           'alternatenames': 'Xixerella',
           'country_code': 'AD',
           'timezone': 'Europe/Andorra',
           'location': [1.48764, 42.55294]}]
)


VALID_LOG_FILE_STREAM = StringIO(json.dumps(LOG_ENTRY))
GZIPPED_LOG_FILE_STREAM = StringIO(json.dumps(GZIP_LOG_ENTRY))
BULK_LOG_FILE_STREAM = StringIO(json.dumps(BULK_API_LOG_ENTRY))


def test_WHEN_load_log_file_called_AND_valid_replayer_triples_THEN_returns_it():
    log_file_loader = ReplayerTriplesFileLoader.load(VALID_LOG_FILE_STREAM)
    for loaded_line in log_file_loader:
        # The line should have two elements
        assert len(loaded_line) == 2
        primary = loaded_line.primary
        shadow = loaded_line.shadow
    
        # Each of them should point to the other as the corresponding entry
        assert id(primary.corresponding_pair) == id(shadow)
        assert id(shadow.corresponding_pair) == id(primary)

        # The requests should be the same object.
        assert primary.request == shadow.request
        assert primary.request == LOG_ENTRY_REQUEST

        assert primary.response == LOG_ENTRY_PRIMARY_RESPONSE
        assert shadow.response == LOG_ENTRY_SHADOW_RESPONSE


def test_WHEN_load_log_file_called_AND_valid_replayer_triples_AND_gzipped_responses_THEN_returns_it():
    # In the future, we should uncompress the gzipped file, but for now, we just preserve it as a string.
    log_file_loader = ReplayerTriplesFileLoader.load(GZIPPED_LOG_FILE_STREAM)
    for loaded_line in log_file_loader:
        # The line should have two elements
        assert len(loaded_line) == 2
        primary = loaded_line.primary
        shadow = loaded_line.shadow

        # Each of them should point to the other as the corresponding entry
        assert id(primary.corresponding_pair) == id(shadow)
        assert id(shadow.corresponding_pair) == id(primary)

        # The requests should be the same object.
        assert primary.request == shadow.request
        assert primary.request == GZIP_LOG_ENTRY_REQUEST

        assert primary.response == GZIP_LOG_ENTRY_PRIMARY_RESPONSE
        assert shadow.response == GZIP_LOG_ENTRY_SHADOW_RESPONSE


def test_WHEN_load_log_file_called_AND_valid_replayer_triples_AND_bulk_api_request_THEN_returns_it():
    log_file_laoder = ReplayerTriplesFileLoader.load(BULK_LOG_FILE_STREAM)
    for loaded_line in log_file_laoder:
        assert len(loaded_line) == 2
        assert id(loaded_line.primary.request) == id(loaded_line.shadow.request)
        assert loaded_line.primary.request == BULK_API_ENTRY_REQUEST
