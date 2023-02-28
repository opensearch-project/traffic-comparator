import json
import logging
import re
from abc import ABC, abstractmethod
from enum import Enum
from pathlib import Path
from typing import Optional, Type, Union, List, Tuple

from traffic_comparator.data import (Request, RequestResponsePair,
                                     RequestResponseStream, Response)

logger = logging.getLogger(__name__)


class UnknownLogFileFormatException(Exception):
    def __init__(self, format, original_exception) -> None:
        super().__init__(f"The log file format '{format}' is unknown or unsupported. "
                         f"Details: {str(original_exception)}")


class IncorrectLogFilePathInputException(Exception):
    def __init__(self, format, expected_number, actual_number) -> None:
        super().__init__(f"The incorrect number of log files for the format '{format}' were provided. "
                         f"{expected_number} files were expected but {actual_number} were provided.")


class LogFileFormat(Enum):
    HAPROXY_JSONS = "haproxy-jsons"
    REPLAYER_TRIPLES = "replayer-triples"


class BaseLogFileLoader(ABC):
    def __init__(self, log_file_paths: List[Path]) -> None:
        self.log_file_paths = log_file_paths

    @abstractmethod
    def load(self) -> Tuple[RequestResponseStream, RequestResponseStream]:
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
        response.latency = responsedata.get('response_time_ms')
        raw_response_body = responsedata.get('body')
        try:
            response.body = json.loads(raw_response_body)
        except json.JSONDecodeError:
            logger.debug(f"Response body could not be parsed as JSON: {response.body}")
            response.body = raw_response_body

        # Need to do something with the timstamps so that they're subtractable
        return RequestResponsePair(request, response)
    
    def _load_single_file(self, file_path) -> RequestResponseStream:
        pairs: RequestResponseStream = []
        with open(file_path) as log_file:
            for i, line in enumerate(log_file):
                try:
                    parsed_pair = self.parseLine(line)
                    if parsed_pair:
                        pairs.append(parsed_pair)
                except Exception as e:
                    # figure out if I should be exiting on these or not (I think not)
                    logger.info(f"An error was found on line {i} of {file_path} "
                                f"and the data could not be loaded. Details: {e}")
        logger.info(f"Loaded {len(pairs)} logged requests/responses from {file_path}.")
        return pairs

    def load(self) -> Tuple[RequestResponseStream, RequestResponseStream]:
        if len(self.log_file_paths) != 2:
            raise IncorrectLogFilePathInputException(LogFileFormat.HAPROXY_JSONS, 2, len(self.log_file_paths))
        primary_stream = self._load_single_file(self.log_file_paths[0])
        shadow_stream = self._load_single_file(self.log_file_paths[1])
        return (primary_stream, shadow_stream)


class ReplayerTriplesFileLoader(BaseLogFileLoader):
    """
    This is the log format output by the Replayer. Each line is a "triple": a json
    that contains the request, the response from the primary, and the response from the shadow.
    One idiosyncracy (for the time being) is that the headers are not in a seperate object -- they're
    mixed in with the main fields and therefore should be considered whatever fields are left over
    when the known ones are removed.
    
    {
      "request": {
        "Request-URI": XYZ,
        "Method": XYZ,
        "HTTP-Version": XYZ
        "body": XYZ,
        "header-1": XYZ,
        "header-2": XYZ

      },
      "primaryResponse": {
        "HTTP-Version": ABC,
        "Status-Code": ABC,
        "Reason-Phrase": ABC,
        "response_time_ms": 456, # milliseconds between the request and the response
        "body": ABC,
        "header-1": ABC
      },
      "shadowResponse": {
        "HTTP-Version": ABC,
        "Status-Code": ABC,
        "Reason-Phrase": ABC,
        "response_time_ms": 456, # milliseconds between the request and the response
        "body": ABC,
        "header-2": ABC
      }
    }
    The body field contains a string which can be decoded as json (or an empty string).
    """
    ignored_fields = ["Reason-Phrase", "HTTP-Version"]
    
    def _parseBodyAsJson(self, rawbody: str) -> Union[dict, str, None]:
        try:
            return json.loads(rawbody)
        except json.JSONDecodeError:
            logger.debug(f"Response body could not be parsed as JSON: {rawbody}")
        return rawbody

    def _parseResponse(self, responsedata) -> Response:
        r = Response()
        # Pull out known fields
        r.body = self._parseBodyAsJson(responsedata.pop("body"))
        r.latency = responsedata.pop("response_time_ms")
        r.statuscode = int(responsedata.pop("Status-Code"))

        # Discard unnecessary fields
        for field in self.ignored_fields:
            if field in responsedata:
                responsedata.pop(field)

        # The remaining fields are headers
        r.headers = responsedata
        return r

    def _parseRequest(self, requestdata) -> Request:
        r = Request()
        # Pull out known fields
        r.body = self._parseBodyAsJson(requestdata.pop("body"))
        r.http_method = requestdata.pop("Method")
        r.uri = requestdata.pop("Request-URI")

        # Discard unnecessary fields
        for field in self.ignored_fields:
            if field in requestdata:
                requestdata.pop(field)

        # The remaining fields are headers
        r.headers = requestdata
        return r

    def _parseLine(self, line) -> Tuple[RequestResponsePair, RequestResponsePair]:
        item = json.loads(line)

        # If any of these objects are missing, it will throw and error and this log file
        # line will be skipped. The error is logged by the caller.
        requestdata = item['request']
        primaryResponseData = item['primaryResponse']
        shadowResponseData = item['shadowResponse']

        request = self._parseRequest(requestdata)

        primaryPair = RequestResponsePair(request, self._parseResponse(primaryResponseData))
        shadowPair = RequestResponsePair(request, self._parseResponse(shadowResponseData),
                                         corresponding_pair=primaryPair)
        primaryPair.corresponding_pair = shadowPair

        return primaryPair, shadowPair
    
    def load(self) -> Tuple[RequestResponseStream, RequestResponseStream]:
        primaryPairs = []
        shadowPairs = []
        for file_path in self.log_file_paths:
            with open(file_path) as log_file:
                for i, line in enumerate(log_file):
                    try:
                        primaryPair, shadowPair = self._parseLine(line)
                        if primaryPair:
                            primaryPairs.append(primaryPair)
                        if shadowPair:
                            shadowPairs.append(shadowPair)
                    except Exception as e:
                        # figure out if I should be exiting on these or not (I think not)
                        logger.info(f"An error was found on line {i} of {file_path} "
                                    f"and the data could not be loaded. Details: {e}")
            logger.info(f"Loaded {len(primaryPairs)} primary and {len(shadowPairs)} shadow pairs from {file_path}.")
        return (primaryPairs, shadowPairs)


LOG_FILE_LOADER_MAPPING: dict[LogFileFormat, Type[BaseLogFileLoader]] = {
    LogFileFormat.HAPROXY_JSONS: HAProxyJsonsFileLoader,
    LogFileFormat.REPLAYER_TRIPLES: ReplayerTriplesFileLoader
}


IsCorrelatedFormat = {
    LogFileFormat.HAPROXY_JSONS: False,
    LogFileFormat.REPLAYER_TRIPLES: True
}


def getLogFileLoader(logFileFormat: LogFileFormat) -> Type[BaseLogFileLoader]:
    try:
        return LOG_FILE_LOADER_MAPPING[logFileFormat]
    except KeyError as e:
        raise UnknownLogFileFormatException(logFileFormat, e)
