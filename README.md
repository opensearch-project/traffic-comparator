# Opensearch Traffic Comparator

The Traffic Comparator can be used to compare traffic streams of mirrored requests to two opensearch clusters. THe tool matches up requests (if necessary) and then compares the responses and shows defferences in "correctness" (content of the response) and performance.

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

Run the TC framework with the `trafficcomparator` command, and a config file that specifies a file for each cluster's traffic. For example:
```
trafficcomparator run --config test_config.json
```

You can also get descriptions of the available reports with:
```
trafficcomparator available-reports
```

#### Config File Format
There are various required and optional config file fields.
```
{
    "primary_log": "The path to the log file from the primary cluster -- required.",
    "shadow_log": "The path to the log file from the shadow cluster -- required.",
    "log_file_format": "The descriptor for the file format of the log files. Required. Currently the only option is "haproxy-jsons" but more may be supported in the future.",

    # Reports is an optional field that should contain a list of report specifications.
    # If no reports are specified, there will be no output.
    "reports": [
        {
            "report_name": "The name of a report that's available to the analyzer.",
            "export_filename": "Optional. If you'd like the report written to a file, provide a filepath here. If this param is not present, nothing will be written to a file.",
            "display": "True or false, this is a required param for whether you'd like a summary of the report printed to the console."
        }
    ]
}
```

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