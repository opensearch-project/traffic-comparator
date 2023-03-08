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

Run the TC framework with the `trafficcomparator` command. It requires several command line options: the paths to the primary and shadow log files and the format of the log files. Optionally, you can specify a list of reports to display, and a list of reports to export to a file, followed by the file names for each export. See the documentation for more information:
```
$ trafficcomparator run --help

Usage: trafficcomparator run [OPTIONS]

Options:
  --log-file PATH                 Path to a log file. This option is required
                                  at least once and can be provided many
                                  times. If the file format has seperate
                                  primary and shadow logs, the first use
                                  should be the primary log and the second the
                                  shadow.  [required]
  --log-file-format TEXT          Specification for the log file format (must
                                  be supported by a LogFileLoader).
                                  [required]
  --display-reports TEXT          A list of reports that should be printed (in
                                  a summary form) to stdout.
  --export-reports <TEXT FILENAME>...
                                  A list of reports to export and the file
                                  path to export it to. This can be '-' for
                                  stdout.
  -v, --verbose
  --help                          Show this message and exit.
```

For example:
```
$ trafficcomparator run --log-file test_primary_logs.log --log-file test_shadow_logs.log --log-file-format haproxy-jsons --display-reports BasicCorrectnessReport
BasicCorrectnessReport:

    5 responses were compared.
    4 were identical, for a match rate of 0.8
    1 request(s) from the primary cluster were not matched with a request from the shadow cluster

```

You can also get descriptions of the available reports with:
```
trafficcomparator available-reports
```

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