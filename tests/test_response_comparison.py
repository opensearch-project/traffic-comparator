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
    assert response_comparison.are_identical()
    assert response_comparison.status_code_diff == {}
    assert response_comparison.headers_diff == {}
    assert response_comparison.body_diff == {}


def test_WHEN_status_codes_different_THEN_not_identical_AND_diff_explained():
    response1 = Response(statuscode=200, headers=RESPONSE_HEADERS, body=RESPONSE_BODY_1)
    response2 = Response(statuscode=404, headers=RESPONSE_HEADERS, body=RESPONSE_BODY_1)

    response_comparison = ResponseComparison(response1, response2)
    assert not response_comparison.are_identical()
    assert response_comparison.status_code_diff == {'values_changed': {'root': {'new_value': 404, 'old_value': 200}}}
    assert response_comparison.headers_diff == {}
    assert response_comparison.body_diff == {}


def test_WHEN_body_value_changed_THEN_not_identical_AND_diffs_explained():
    response1 = Response(statuscode=200, headers=RESPONSE_HEADERS, body=RESPONSE_BODY_1)
    response2 = Response(statuscode=200, headers=RESPONSE_HEADERS, body=RESPONSE_BODY_2)

    response_comparison = ResponseComparison(response1, response2)
    assert not response_comparison.are_identical()
    assert response_comparison.status_code_diff == {}
    assert response_comparison.headers_diff == {}
    assert response_comparison.body_diff == {'values_changed': {"root['hello']":
                                                                {'new_value': 'earth',
                                                                 'old_value': 'world'}}}


def test_WHEN_body_value_type_changed_THEN_not_identical_AND_diffs_explained():
    response1 = Response(statuscode=200, headers=RESPONSE_HEADERS, body=RESPONSE_BODY_1)
    response2 = Response(statuscode=200, headers=RESPONSE_HEADERS, body=RESPONSE_BODY_3)

    response_comparison = ResponseComparison(response1, response2)
    assert not response_comparison.are_identical()
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
    assert not response_comparison.are_identical()
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
    assert response_comparison.are_identical()
    assert response_comparison.status_code_diff == {}
    assert response_comparison.headers_diff == {}
    assert response_comparison.body_diff == {}


# Test the Masking Functionality
MASKING_RESPONSE_BODY_1 = {
    'name': 'eosu1',
    'cluster_name': 'gcstest',
    'cluster_uuid': 'EMacGyyZSK2KntmyWG3HgA',
    'version': {
        'number': '7.10.0',
        'build_flavor': 'oss',
        'build_type': 'deb',
        'build_hash': '51e9d6f22758d0374a0f3f5c6e8f3a7997850f96',
        'build_date': '2020-11-09T21:30:33.964949Z',
        'build_snapshot': False,
        'lucene_version': '8.7.0',
        'minimum_wire_compatibility_version': '6.8.0',
        'minimum_index_compatibility_version': '6.0.0-beta1'
    },
    'tagline': 'You Know, for Search'
}

MASKING_RESPONSE_BODY_2 = {
    'name': '28a6a5d46dd3c08b543eb5574ab10f5f',
    'cluster_name': '541757191419:os-service-domain',
    'cluster_uuid': '8OoM_tpITc6q9x-WlraUbA',
    'version': {
        'distribution': 'opensearch',
        'number': '1.3.2',
        'build_type': 'tar',
        'build_hash': 'unknown',
        'build_date': '2022-11-15T05:29:22.155152Z',
        'build_snapshot': False,
        'lucene_version': '8.10.1',
        'minimum_wire_compatibility_version': '6.8.0',
        'minimum_index_compatibility_version': '6.0.0-beta1'
    },
    'tagline': 'The OpenSearch Project: https://opensearch.org/'
}


def test_WHEN_responses_differ_on_masked_fields_THEN_comparison_suceeds():
    es_response = Response(headers={"content-length": 521},
                           body=MASKING_RESPONSE_BODY_1)
    os_response = Response(headers={'content-length': 572},
                           body=MASKING_RESPONSE_BODY_2)
    response_comparison = ResponseComparison(es_response, os_response)
    print(response_comparison.body_diff)
    assert response_comparison.status_code_diff == {}
    assert response_comparison.headers_diff == {}
    assert response_comparison.body_diff == {}
    assert response_comparison.are_identical()
