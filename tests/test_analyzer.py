import json
from unittest.mock import patch

from traffic_comparator.analyzer import StreamingAnalyzer
from traffic_comparator.data import Request, RequestResponsePair, Response

REQUEST = Request(
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

PRIMARY_RESPONSE = Response(
    timestamp=None,
    statuscode=200,
    headers={
        "content-length": "100",
        "content-type": "application/json; charset=UTF-8"
    },
    latency=14,
    body={
        "tagline": "You Know, for Search",
        "important_data": "Hello, world"

    }
)

SHADOW_RESPONSE = Response(
    timestamp=None,
    statuscode=201,
    headers={
        "content-length": "200",
        "content-type": "application/json; charset=UTF-8"
    },
    latency=199,
    body={
        "tagline": "You Know, for Search",
        "important_data": "Anything but hello world"
    }
)

PRIMARY_PAIR = RequestResponsePair(REQUEST, PRIMARY_RESPONSE)
SHADOW_PAIR = RequestResponsePair(REQUEST, SHADOW_RESPONSE, PRIMARY_PAIR)
PRIMARY_PAIR.corresponding_pair = SHADOW_PAIR

COMPARISON_DICT = {
    'primary_response': PRIMARY_RESPONSE.__dict__,
    'shadow_response': SHADOW_RESPONSE.__dict__,
    'original_request': REQUEST.__dict__,
    '_status_code_diff': '{"values_changed":{"root":{"new_value":201,"old_value":200}}}',
    '_headers_diff': '{}',
    '_body_diff': '{"values_changed":{"root[\'important_data\']":{"new_value":"Anything but hello world","old_value":"Hello, world"}}}'  # noqa: E501
}


@patch('traffic_comparator.data_loader.StreamingDataLoader', autospec=True)
def test_WHEN_streaming_analyzer_given_reqres_pair_THEN_outputs_comparison(MockDataLoader, capsys):
    # Prepare data_loader.next_input with a single-item iterable
    MockDataLoader.next_input = lambda: [(PRIMARY_PAIR, SHADOW_PAIR)]

    # Initialize the analyzer
    analyzer = StreamingAnalyzer(MockDataLoader)
    analyzer.start()
    assert len(analyzer._comparisons) == 1
    captured = capsys.readouterr()
    assert json.loads(captured[0]) == COMPARISON_DICT
