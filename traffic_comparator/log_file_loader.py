import json
import logging
import re
from abc import ABC, abstractmethod
from enum import Enum
from typing import Optional, Type

from traffic_comparator.data import (Request, RequestResponsePair,
                                     RequestResponseStream, Response)

logger = logging.getLogger(__name__)


class UnknownLogFileFormatException(Exception):
    def __init__(self, format, original_exception) -> None:
        super().__init__(f"The log file format '{format}' is unknown or unsupported. "
                         f"Details: {str(original_exception)}")


class LogFileFormat(Enum):
    HAPROXY_JSONS = "haproxy-jsons"


class BaseLogFileLoader(ABC):
    def __init__(self, log_file_path: str) -> None:
        self.log_file_path = log_file_path

    @abstractmethod
    def load(self) -> RequestResponseStream:
        pass


class HAProxyJsonsFileLoader(BaseLogFileLoader):
    """
    The HAProxyJsons format is a bit of an idiosyncratic one.
    Each line of the file contains a JSON that should look like:
    {
      "request": {
        "timestamp": 123456789,  # (unix epoch time)
        "uri": XYZ,
        "headers": XYZ,
        "body": XYZ
      },
      "response": {
        "response_time_ms": 456,  # milliseconds between the request and the response
        "status_code": ABC
        "headers": ABC,
        "body": ABC
      }
    }
    The values within this fields are escaped to be safe-for-JSON strings, but
    they likely have whitespace and other unusual formats.

    The line starts with something a long the lines of `Feb  1 23:05:17 localhost haproxy[20]: ` before the json
    and some lines may not have a request/response log at all.
    """
    log_extractor = re.compile(r"[\w\s\:\[\]]+\:\s(\{.*\})$", flags=re.DOTALL)
    
    def parseLine(self, line) -> Optional[RequestResponsePair]:
        request = Request()
        response = Response()

        # The line starts with other material, so first the json (if present) is sperated from the prefixed info
        extracted_line = self.log_extractor.match(line)
        if extracted_line is None:
            return
        item = json.loads(extracted_line.groups()[0])

        # This will raise an error if there is not a request or response object.
        # The loader will continue with the next line.
        requestdata = item['request']
        responsedata = item['response']
    
        request.timestamp = requestdata.get('timestamp')
        request.uri = requestdata.get('uri')
        request.http_method = requestdata.get('method')
        request.headers = requestdata.get('headers')
        raw_request_body = requestdata.get('body')
        try:
            request.body = json.loads(raw_request_body)
        except json.JSONDecodeError:
            logger.debug(f"Request body could not be parsed as JSON: {request.body}")
            request.body = raw_request_body

        response.timestamp = responsedata.get('timestamp')
        response.statuscode = responsedata.get('status_code')
        response.headers = responsedata.get('headers')
        raw_response_body = responsedata.get('body')
        try:
            response.body = json.loads(raw_response_body)
        except json.JSONDecodeError:
            logger.debug(f"Response body could not be parsed as JSON: {response.body}")
            response.body = raw_response_body

        # Need to do something with the timstamps so that they're subtractable
        return RequestResponsePair(request, response, latency=responsedata.get('response_time_ms'))
    
    def load(self) -> RequestResponseStream:
        pairs: RequestResponseStream = []
        with open(self.log_file_path) as log_file:
            for i, line in enumerate(log_file):
                try:
                    parsed_pair = self.parseLine(line)
                    if parsed_pair:
                        pairs.append(parsed_pair)
                except Exception as e:
                    # figure out if I should be exiting on these or not (I think not)
                    logger.info(f"An error was found on line {i} of {self.log_file_path} "
                                f"and the data could not be loaded. Details: {e}")
        logger.info(f"Loaded {len(pairs)} logged requests/responses from {self.log_file_path}.")
        return pairs


LOG_FILE_LOADER_MAPPING: dict[LogFileFormat, Type[BaseLogFileLoader]] = {
    LogFileFormat.HAPROXY_JSONS: HAProxyJsonsFileLoader
}


def getLogFileLoader(logFileFormat: LogFileFormat) -> Type[BaseLogFileLoader]:
    try:
        return LOG_FILE_LOADER_MAPPING[logFileFormat]
    except KeyError as e:
        raise UnknownLogFileFormatException(logFileFormat, e)
