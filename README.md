# Opensearch Traffic Comparator

The Traffic Comparator can be used to compare traffic streams of mirrored requests to two opensearch clusters. The tool matches up requests (if necessary) and then compares the responses and shows defferences in "correctness" (content of the response) and performance.

## Security

See [CONTRIBUTING](CONTRIBUTING.md#security-issue-notifications) for more information.

## License

This project is licensed under the Apache-2.0 License.


## Running the Traffic Comparator

To run the Traffic Comparator, perform the following steps.

### PRE-REQUISITES

* Python3 and venv
* Currently in the same directory as this README, the setup.py, etc

### Step 1 - Activate your Python virtual environment

To isolate the Python environment for the project from your local machine, create virtual environment like so:
```
python3 -m venv .venv
source .venv/bin/activate
```

You can exit the Python virtual environment and remove its resources like so:
```
deactivate
rm -rf .venv
```

Learn more about venv [here](https://docs.python.org/3/library/venv.html).

### Step 2 - Run the TC
The `trafficcomparator` command is installed as a command on your machine (make sure you're in your virtual environment) with:
```
pip install --editable .
```

Run the TC framework with the `trafficcomparator` command.  It offers several entrypoints.

For all commands, there's a verbosity option (`--verbose`, `-v` for info level and `--v` for debug). Logs are printed to stderr, so they don't interfere with streaming via stdin and out.

After the optional verbosity, there are 3 available commands:
`available-reports`, `stream`, and `stream-reports`.

Available-reports gives descriptions of the available reports:
```
$ trafficcomparator available-reports

BasicCorrectnessReport: Provides basic information on how many and what ratio of responses are succesfully matched.
    The exported file provides the same summary as the cli and then a list of diffs for every response
    that does not match.
    
PerformanceReport: Provides basic performance data including: average, median, p90 and p99 latencies.
    The exported file provides a CSV file which lists response body, latency and status code of both primary
    and shadow cluster for to each request.
```

The next two commands are usually run together. `stream` handles accepting a stream of json-formatted "triples" from stdin. This is the output of the Replayer and is documented in detail in [log_file_loader.py](traffic_comparator/log_file_loader.py), but at a high level, it is json objects with a request, primary response, and shadow response. `stream` generates a comparison for each pair of responses and outputs a json-formatted version of that comparison to stdout.

`stream-report` accepts a stream of comparison objects from stdin and outputs to stdout an intermittent (every 1 minute, by default) summary report of correctness and performance statistics. When the stream ends, it outputs a final summary statistic, and then, for any reports specified as an export report, a detailed version to a file.

An example of complete usage:

```
$ tail mini_triples.log | trafficcomparator -v stream | trafficcomparator stream-report --export-reports BasicCorrectnessReport correctness_report.log                                                                                                 ──(Tue,Mar28)─┘
INFO:traffic_comparator.analyzer:All inputs processed. Generated 10 comparisons.
========================================
as of 2023-03-28 23:00:55.362715:

    10 response were compared.
    0 were identical, for a match rate of 0.00%
    The status codes matched in 90.00% of responses.
    

            ==Stats for primary cluster==
    99th percentile = 59.1
    90th percentile = 51.0
    50th percentile = 23.5
    Average Latency = 28.2
    
            ==Stats for shadow cluster==
    99th percentile = 309.8
    90th percentile = 209.4
    50th percentile = 121.0
    Average Latency = 156.2
    
BasicCorrectnessReport was exported to correctness_report.log
```

Note that the `-v` flag applies only to one instance of the command. If there were more comparisons and it had taken more than a minute to run, the summary would have been output multiple times.

The traffic comparator currently has a built-in list of fields to "mask": they're ignored when comparing the results. That list can be seen [here](traffic_comparator/response_comparison.py#L13-L15). In the near future, it will be user-configurable. See [MIGRATIONS-863](https://opensearch.atlassian.net/browse/MIGRATIONS-863).

Note that these fields will still be shown when the results are diffed in the detailed version of the BasicCorrectnessReport. That issue will be fixed in [MIGRATIONS-1013](https://opensearch.atlassian.net/browse/MIGRATIONS-1013).


## Working on the Traffic Comparator

To install dev dependencies (e.g. flake8 and pytest):
```
pip install --editable ".[dev]"
```


### Run Unit Tests
In this directory (you should see the `test` and `traffic_comparator` directories)

```
pytest
```