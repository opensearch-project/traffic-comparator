from traffic_comparator.response_comparison import ResponseComparison
from traffic_comparator.data import Response

RESPONSE_BODY_1 = {"hello": "world"}
RESPONSE_BODY_2 = {"hello": "earth"}
RESPONSE_BODY_3 = {"hello": ["world", "earth"]}
RESPONSE_BODY_4 = {"hello": ["earth", "world"]}
RESPONSE_HEADERS = "content-type: application/json; charset=UTF-8|content-length: 154"


def test_WHEN_responses_identical_THEN_is_identical_is_true_AND_diffs_empty():
    response1 = Response(statuscode=200, headers=RESPONSE_HEADERS, body=RESPONSE_BODY_1)
    response2 = Response(statuscode=200, headers=RESPONSE_HEADERS, body=RESPONSE_BODY_1)

    response_comparison = ResponseComparison(response1, response2)
    assert response_comparison.is_identical()
    assert response_comparison.status_code_diff == {}
    assert response_comparison.headers_diff == {}
    assert response_comparison.body_diff == {}


def test_WHEN_status_codes_different_THEN_not_identical_AND_diff_explained():
    response1 = Response(statuscode=200, headers=RESPONSE_HEADERS, body=RESPONSE_BODY_1)
    response2 = Response(statuscode=404, headers=RESPONSE_HEADERS, body=RESPONSE_BODY_1)

    response_comparison = ResponseComparison(response1, response2)
    assert not response_comparison.is_identical()
    assert response_comparison.status_code_diff == {'values_changed': {'root': {'new_value': 404, 'old_value': 200}}}
    assert response_comparison.headers_diff == {}
    assert response_comparison.body_diff == {}


def test_WHEN_body_value_changed_THEN_not_identical_AND_diffs_explained():
    response1 = Response(statuscode=200, headers=RESPONSE_HEADERS, body=RESPONSE_BODY_1)
    response2 = Response(statuscode=200, headers=RESPONSE_HEADERS, body=RESPONSE_BODY_2)

    response_comparison = ResponseComparison(response1, response2)
    assert not response_comparison.is_identical()
    assert response_comparison.status_code_diff == {}
    assert response_comparison.headers_diff == {}
    assert response_comparison.body_diff == {'values_changed': {"root['hello']":
                                                                {'new_value': 'earth',
                                                                 'old_value': 'world'}}}


def test_WHEN_body_value_type_changed_THEN_not_identical_AND_diffs_explained():
    response1 = Response(statuscode=200, headers=RESPONSE_HEADERS, body=RESPONSE_BODY_1)
    response2 = Response(statuscode=200, headers=RESPONSE_HEADERS, body=RESPONSE_BODY_3)

    response_comparison = ResponseComparison(response1, response2)
    assert not response_comparison.is_identical()
    assert response_comparison.status_code_diff == {}
    assert response_comparison.headers_diff == {}

    body_diff = {'type_changes':
                 {"root['hello']": {'new_type': list,
                                    'new_value': ['world', 'earth'],
                                    'old_type': str,
                                    'old_value': 'world'}}}
    assert response_comparison.body_diff == body_diff

    
def test_WHEN_body_value_order_changed_THEN_not_identical_AND_diffs_explained():
    response1 = Response(statuscode=200, headers=RESPONSE_HEADERS, body=RESPONSE_BODY_3)
    response2 = Response(statuscode=200, headers=RESPONSE_HEADERS, body=RESPONSE_BODY_4)

    response_comparison = ResponseComparison(response1, response2)
    assert not response_comparison.is_identical()
    assert response_comparison.status_code_diff == {}
    assert response_comparison.headers_diff == {}
    body_diff = {'values_changed':
                 {"root['hello'][0]": {'new_value': 'earth',
                                       'old_value': 'world'},
                  "root['hello'][1]": {'new_value': 'world',
                                       'old_value': 'earth'}}}
    assert response_comparison.body_diff == body_diff


def test_WHEN_status_code_missing_THEN_comparison_succeeds():
    response1 = Response(headers=RESPONSE_HEADERS, body=RESPONSE_BODY_1)
    response2 = Response(headers=RESPONSE_HEADERS, body=RESPONSE_BODY_1)

    response_comparison = ResponseComparison(response1, response2)
    assert response_comparison.is_identical()
    assert response_comparison.status_code_diff == {}
    assert response_comparison.headers_diff == {}
    assert response_comparison.body_diff == {}
