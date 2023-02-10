from traffic_comparator.data import Request

REQUEST_TIMESTAMP = 1675811048
REQUEST_URI = "/index1/_doc/1"
REQUEST_BODY = {"hello": "world"}
REQUEST_HEADER = "accept: */*#0D#0Acontent-type: application/json#0D#0Acontent-length: 17#0D#0A"


def test_WHEN_requests_identical_THEN_are_equivalent():
    r1 = Request(timestamp=REQUEST_TIMESTAMP, uri=REQUEST_URI, body=REQUEST_BODY)
    r2 = Request(timestamp=REQUEST_TIMESTAMP, uri=REQUEST_URI, body=REQUEST_BODY)
    assert r1.equivalent_to(r2)
    assert r2.equivalent_to(r1)


def test_WHEN_requests_identical_except_timestamp_THEN_are_equivalent():
    r1 = Request(timestamp=REQUEST_TIMESTAMP, uri=REQUEST_URI, body=REQUEST_BODY)
    r2 = Request(timestamp=REQUEST_TIMESTAMP + 15, uri=REQUEST_URI, body=REQUEST_BODY)
    assert r1.equivalent_to(r2)
    assert r2.equivalent_to(r1)


def test_WHEN_requests_identical_except_method_THEN_are_not_equivalent():
    r1 = Request(timestamp=REQUEST_TIMESTAMP, http_method="GET", uri=REQUEST_URI, body=REQUEST_BODY)
    r2 = Request(timestamp=REQUEST_TIMESTAMP, http_method="POST", uri=REQUEST_URI, body=REQUEST_BODY)
    assert not r1.equivalent_to(r2)
    assert not r2.equivalent_to(r1)


def test_WHEN_requests_identical_except_uri_THEN_are_not_equivalent():
    r1 = Request(timestamp=REQUEST_TIMESTAMP, uri=REQUEST_URI, body=REQUEST_BODY)
    r2 = Request(timestamp=REQUEST_TIMESTAMP, uri="/index1/_doc/2", body=REQUEST_BODY)
    assert not r1.equivalent_to(r2)
    assert not r2.equivalent_to(r1)


def test_WHEN_requests_identical_except_headers_THEN_are_not_equivalent():
    r1 = Request(timestamp=REQUEST_TIMESTAMP, headers=REQUEST_HEADER, uri=REQUEST_URI, body=REQUEST_BODY)
    r2 = Request(timestamp=REQUEST_TIMESTAMP, headers="content-type: text/html", uri=REQUEST_URI, body=REQUEST_BODY)
    assert not r1.equivalent_to(r2)
    assert not r2.equivalent_to(r1)
