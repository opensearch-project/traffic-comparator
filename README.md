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

For all commands, there's a verbosity option (`--verbose`, `-v` for info level and `-vv` for debug). Logs are printed to stderr, so they don't interfere with streaming via stdin and out.

After the optional verbosity, there are 3 available commands:
`available-reports`, `stream`, and `stream-reports`.

Available-reports gives descriptions of the available reports:
```
$ trafficcomparator available-reports

DiffReport: Provides basic information on how many and what ratio of responses are succesfully matched.
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
$ cat mini_triples.log | trafficcomparator -v stream | trafficcomparator stream-report --export-reports DiffReport diffs.log
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
    
DiffReport was exported to diffs.log
```


Note that the `-v` flag applies only to one instance of the command. If there were more comparisons and it had taken more than a minute to run, the summary would have been output multiple times.

The traffic comparator currently has a built-in list of fields to "mask": they're ignored when comparing the results. That list can be seen [here](traffic_comparator/response_comparison.py#L13-L15). In the near future, it will be user-configurable. See [MIGRATIONS-863](https://opensearch.atlassian.net/browse/MIGRATIONS-863).

Note that these fields will still be shown when the results are diffed in the detailed version of the DiffReport. That issue will be fixed in [MIGRATIONS-1013](https://opensearch.atlassian.net/browse/MIGRATIONS-1013).


### Details on output of `stream`
The `stream` command generates comparison objects, which are passed to the reporting tool. You can use `tee` to capture these objects while they're being passed, like so:

```
$ cat mini_triples.log | trafficcomparator -v stream | tee comparisonResults.log | trafficcomparator stream-report --export-reports DiffReport diffs.log
```

The `comparisonResults.log` file will have one line for each comparison, and it will be a json object with the structure:
```
{
  "primary_response": XYZ,
  "shadow_reponse": XYZ,
  "original_request": XYZ,
  "_status_code_diff": {},
  "_headers_diff": {},
  "_body_diff": {}
}
```

The `_item_diff` fields contain the diff for that item between the two responses, as generated by the [DeepDiff](https://zepworks.com/deepdiff/current/) library. For instance, the diff sections for one sample triple is:
```
{
  "_status_code_diff": {},
  "_headers_diff": {
      "dictionary_item_added":
      [
          "root['access-control-allow-origin']",
          "root['Connection']",
          "root['Content-Length']",
          "root['Date']",
          "root['Content-Type']"
      ],
      "dictionary_item_removed":
      [
          "root['content-type']"
      ]
  },
  "_body_diff": {
      "dictionary_item_added":
      [
          "root['discovered_master']"
      ],
      "values_changed":
      {
          "root['number_of_nodes']":
          {
              "new_value": 3,
              "old_value": 2
          },
          "root['number_of_data_nodes']":
          {
              "new_value": 3,
              "old_value": 2
          },
          "root['active_primary_shards']":
          {
              "new_value": 11,
              "old_value": 0
          },
          "root['active_shards']":
          {
              "new_value": 16,
              "old_value": 0
          }
      }
  }
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

## Exploring Results in Jupyter Notebook/IPython

Currently, comparison results can be reported in very high level reports (average latencies, percent of matching status codes), or in very low level detail (all line-by-line diffs output to a file). Neither of these formats are conducive to data exploration or visualization.

A new option has been added: comparison results can be dumped to a sqlite database, and then read in using some provided functions in a Jupyter Notebook or IPython terminal, and explored and visualized there.

The following is a walk through of the sample `Results Repository.ipynb` file.

### Install Data Exploration-specific Dependencies

```
pip install --editable ".[data]"
```

### Dump Comparison Results to SQLite

A command has been added that handles accepting comparison results and dumping them to sqlite in the appropriate format.

If you're doing your comparison at the same time, it can be run as in the following example, with any of the possible settings from above. It supports running in streaming mode and will flush each write to the sqlite db.

```
cat input_triples.log | trafficcomparator stream | trafficcomparator dump-to-sqlite
```

If you have already generated comparisons (e.g. run the `stream` command) and saved the output, you can pipe that directly into the `dump-to-sqlite` command.

```
cat comparison_results.log | trafficcomparator dump-to-sqlite
```

### Start the Jupyter server and load results
It is possible to run all of the following either in a Jupyter notebook (web-based notebook UI to a local server that runs the python kernel) or in an IPython terminal (command line terminal with kernel running directly).

For the sake of illustration + better visualizations, I'm going to walk through the Jupyter notebook technique here.

Start the server with `jupyter notebook`.

You'll see a bunch of text along the lines of:
```
[I 16:00:25.491 NotebookApp] Serving notebooks from local directory: ~/code/traffic-comparator
[I 16:00:25.491 NotebookApp] Jupyter Notebook 6.5.4 is running at:
[I 16:00:25.491 NotebookApp] http://localhost:8888/?token=f8929f...
```

It should also open a window in your default webbrowser at http://localhost:8888/tree that shows the contents of this directory. You can create a new notebook in the upper right, but for the sake of this walkthrough, open `Result Repository.ipynb`.

Start with the first cell, which has all of the necessary imports. Click into it, and then execute it with shift-enter. Assuming you have all the dependencies installed, there should be no output and it will move your focus to the next cell.

The second cell handles the bulk of loading in the data from the database.
It establishes the path to the db (you can change this if you're done something custom), opens a connection to it, and then guesses the table you'd like to load. It defaults to the latest created table (assuming they were all created with the `dump-to-sqlite` command), but you can change the value of `table_name` if you'd like it to load a different one.

Then it executes a `READ *` command on that table and loads all of the data into a [Pandas dataframe](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.html). Pandas will be the main library used for exploring and managing the data, so it's worth reading through the quickstart guide if you're not familiar with it: https://pandas.pydata.org/docs/getting_started/intro_tutorials/01_table_oriented.html.

This cell also applies two utility functions to the data after loading it in. First, it uses a list that specifies which columns are json to attempt loading the fields as JSON and overwriting their values if succesful. Second, it looks for a `took` field in the body of each response and populates a new column with that value.

The last line (`df.head()`) prints the first five lines of the dataframe, as a way to preview the data and check that it loaded as expected.

The contents of these two cells are pretty universal -- you'll probably want to perform these operations for any projects you do with this data.
The rest of the code is much more specific to particular questions and explorations that I was curious about. My goal was to both answer real questions, and showcase some of the capabilities of Pandas and Jupyter Notebook for this application.