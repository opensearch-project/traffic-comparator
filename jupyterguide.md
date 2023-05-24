# Intro

It is possible to use either Jupyter notebooks (web-based UI to a local server that runs the python kernel) or in an IPython terminal (command line terminal with kernel running directly) to visualize comparison data.

# Walkthrough

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

