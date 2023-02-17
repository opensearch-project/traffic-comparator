import json
import logging
import re
from abc import ABC, abstractmethod
from enum import Enum
from pathlib import Path
from typing import Optional, Type, Union

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
    def __init__(self, log_file_path: Path) -> None:
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
    # This regex matches a line that starts with most characters (alphanumeric, whitespace, colon, square brackets),
    # followed by a colon, whitespace, and then an opening curly bracket followed by anything (.*)
    # until a closing curly bracket. Everything between the curly brackets (inclusive) is captured to
    # be parsed as JSON.
    log_extractor = re.compile(r"[\w\s\:\[\]]+\:\s(\{.*\})$", flags=re.DOTALL)

    def parseHeaders(self, rawheaders: str) -> Union[dict, str]:
        try:
            return dict([s.split(':') for s in rawheaders.split('\r\n') if len(s) > 3])
        except Exception:
            return rawheaders

    def parseBodyAsJson(self, rawbody: str) -> Union[dict, str, None]:
        if rawbody == '-' or rawbody == '\x1f\x08':
            return None
        try:
            return json.loads(rawbody)
        except json.JSONDecodeError:
            logger.debug(f"Response body could not be parsed as JSON: {rawbody}")
        return rawbody
    
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
        request.headers = self.parseHeaders(requestdata.get('headers'))
        request.body = self.parseBodyAsJson(requestdata.get('body'))

        response.timestamp = responsedata.get('timestamp')
        response.statuscode = responsedata.get('status_code')
        response.headers = self.parseHeaders(responsedata.get('headers'))
        response.body = self.parseBodyAsJson(responsedata.get('body'))
        response.latency = responsedata.get('response_time_ms')

        return RequestResponsePair(request, response)
    
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
