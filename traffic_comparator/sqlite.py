import json
import logging
import pathlib
import sqlite3
from typing import Optional, Union

from traffic_comparator.response_comparison import (
    InvalidJsonForLoadingComparisonException,
    MissingFieldForLoadingComparisonJsonException, ResponseComparison)

logger = logging.getLogger(__name__)


COLUMNS = ['request_uri', 'request_method', 'request_timestamp', 'request_headers', 'request_body',
           'source_response_timestamp', 'source_response_status', 'source_response_headers', 'source_response_body', 'source_response_latency',  # noqa: E501
           'target_response_timestamp', 'target_response_status', 'target_response_headers', 'target_response_body', 'target_response_latency',  # noqa: E501
           'responses_are_identical', 'headers_diff', 'bodies_diff']

# This is a dict of the above columns, listing those that should be loaded with a specific pandas datatype.
COLUMN_DATATYPES = {
    "request_uri": "string",
    "request_method": "string",
    "request_timestamp": "datetime64[ns]",
    "request_headers": "string",
    "request_body": "string",
    "source_response_timestamp": "datetime64[ns]",
    "source_response_status": "category",
    "source_response_headers": "string",
    "source_response_body": "string",
    "source_response_latency": int,
    "target_response_timestamp": "datetime64[ns]",
    "target_response_status": "category",
    "target_response_headers": "string",
    "target_response_body": "string",
    "target_response_latency": int,
    "responses_are_identical": int,  # This value is actually a bool, but sqlite treats it as an int
                                     # and that has convenient effects on the pandas side
    "headers_diff": "string",
    "bodies_diff": "string"
}

# This is also a subset of both COLUMNS and COLUMN_DATATYPES for those that should be parsed as JSONs.
COLUMN_JSONS = [
    "request_headers",
    "request_body",
    "source_response_headers",
    "source_response_body",
    "target_response_headers",
    "target_response_body",
    "headers_diff",
    "bodies_diff"
]


def json_load_function(x: str) -> Union[str, dict]:
    """This is a utility functions used in the notebook to parse the json data."""
    try:
        return json.loads(x)
    except json.JSONDecodeError:
        return x


def get_took_value(body: dict) -> Optional[int]:
    """This is used in the notebook to calculate the "took" value, a more accurate measure of latency."""
    if 'took' in body:
        return body['took']
    return None


# Functions for dumping to SQLite


def format_headers(headers: Union[dict, str, None]) -> str:
    if type(headers) is dict:
        return json.dumps(headers)
    elif type(headers) is str:
        return headers
    return ''


def format_body(body: Union[dict, str, list, None]) -> str:
    if type(body) in [dict, list]:
        return json.dumps(body)
    elif type(body) is str:
        return body
    assert body is None
    return ''


class dbComparisonTable:
    def __init__(self, table_name) -> None:
        self.name = table_name

    def createTable(self, cursor: sqlite3.Cursor):
        column_names = ','.join(COLUMNS)
        command = f"CREATE TABLE {self.name}({column_names})"
        logger.debug(f"Command to create table: {command}")
        cursor.execute(command)


class dbComparisonRow:
    def __init__(self, table: dbComparisonTable, comp: ResponseComparison):
        self.table = table
        
        if comp.original_request:
            self.request_uri = comp.original_request.uri
            self.request_method = comp.original_request.http_method
            self.request_timestamp = comp.original_request.timestamp
            self.request_headers = format_headers(comp.original_request.headers)
            self.request_body = format_body(comp.original_request.body)

        if comp.primary_response:
            self.source_response_status = comp.primary_response.statuscode
            self.source_response_headers = format_headers(comp.primary_response.headers)
            self.source_response_body = format_body(comp.primary_response.body)
            self.source_response_latency = comp.primary_response.latency

        if comp.shadow_response:
            self.target_response_status = comp.shadow_response.statuscode
            self.target_response_headers = format_headers(comp.shadow_response.headers)
            self.target_response_body = format_body(comp.shadow_response.body)
            self.target_response_latency = comp.shadow_response.latency

        self.responses_are_identical = comp.are_identical()
        self.headers_diff = str(comp.headers_diff)
        self.bodies_diff = str(comp.body_diff)

    def writeRow(self, cursor: sqlite3.Cursor):
        values = {}
        for c in COLUMNS:
            if c in self.__dict__ and self.__dict__[c] is not None:
                value = self.__dict__[c]
                if type(value) is bool:
                    values[c] = '1' if value else '0'
                elif value is not None:
                    values[c] = str(self.__dict__[c])
            else:
                values[c] = None

        values_keys = ",".join(f":{k}" for k in values.keys())
        command = f"INSERT INTO {self.table.name} VALUES ({values_keys})"
        cursor.execute(command, values)


def get_latest_table_name(cursor: sqlite3.Cursor) -> Optional[str]:
    results = cursor.execute("SELECT name FROM sqlite_master").fetchall()
    if len(results) > 0:
        return sorted(results)[-1][0]
    return None


def get_next_table_name(cursor: sqlite3.Cursor) -> str:
    latest_name = get_latest_table_name(cursor)
    if latest_name:
        # This assumes a name format of "comparisons_XYZ"
        latest_id = int(latest_name.split('_')[1])
    else:
        latest_id = 0
    return f"comparisons_{latest_id+1:03}"

            
class SqliteDumper:
    def __init__(self, db_file: pathlib.Path) -> None:
        self.con = sqlite3.connect(db_file)  # Creates the db if it doesn't already exist
        self.cur = self.con.cursor()
        table_name = get_next_table_name(self.cur)
        self.table = dbComparisonTable(table_name)
        logger.warning(f"Writing to db table {table_name}.")
        self.table.createTable(self.cur)
        self.con.commit()

    def close(self):
        self.con.close()
        logger.warning(f"Finished writing to db table {self.table.name}.")

    def update(self, line: str) -> None:
        comp = None
        try:
            comp = ResponseComparison.from_json(line)
        except InvalidJsonForLoadingComparisonException as e:
            logger.error(f"Comparison could not be loaded due to invalid json. Skipping line. Details: {e}")
        except MissingFieldForLoadingComparisonJsonException as e:
            logger.error(f"Comparison could not be loaded due to a missing field. Skipping line. Details: {e}")

        if comp is None:
            return
        
        row = dbComparisonRow(self.table, comp)
        row.writeRow(self.cur)
        self.con.commit()
        
