from traffic_comparator.sqlite import (COLUMN_DATATYPES, COLUMN_JSONS, COLUMNS,
                                       get_took_value, json_load_function)


def test_column_list_sanity_checks():
    # These prove the assertions in the descriptions of the COLUMN objects

    # COLUMN_DATATYPES contains the same items as COLUMNS
    assert sorted(list(COLUMN_DATATYPES.keys())) == sorted(COLUMNS)

    # COLUMN_JSONS is a subset of COLUMNS
    for entry in COLUMN_JSONS:
        assert entry in COLUMNS


def test_json_load_function_happy_path():
    json_string = """{"hello": "world", "goodnight": ["moon", "noises everywhere"]}"""
    actual_dict = {"hello": "world", "goodnight": ["moon", "noises everywhere"]}

    assert actual_dict == json_load_function(json_string)


def test_json_laod_function_invalid_json_returns_original_string():
    invalid_json_string = """{"hello": "world" """

    assert invalid_json_string == json_load_function(invalid_json_string)


def test_get_took_value_happy_path():
    body = {"result": "xyz", "more_body_contents": "abc", "took": 194, "different_int": 49}
    assert 194 == get_took_value(body)


def test_get_took_value_no_took_field():
    body = {"result": "xyz", "more_body_contents": "abc", "different_int": 49}
    assert get_took_value(body) is None
