# CL-Search

**CL-Search** is a microservce, one of several that will (eventually) form an app that automates Craigslist searches and notifies the requestor of new search results.

## Purpose
Automate [Craigslist](https://www.craigslist.org/about/sites){target="_blank"} searches. Store search results in a database.

## Disclaimer

I have no affiliation with Craigslist.

This project was created for educational purposes. I do not endorse its use for crawling or downloading data from Craigslist.

## Usage
1. Add search parameters to the configuration file **searches_config.yml**, in [YAML](https://yaml.org/) format. Any number of searches can be added to **searches_config.yml**. Only those with `status: active` will be processed. 

2. Run search.py:
```
python search.py
```

> Search results are saved to a database, currently hardcoded to a file named **database.JSON**. If there is no existing database file, one will be created.


## Project Status

This project is a work in progress.

  * An interface for building named searches would be a welcome addition.

## How to Contribute

I encourage you to submit pull requests to help make improvements to this project. Consider opening an Issue so we can discuss your ideas.

Please use the [Udacity Git Commit Message Style Guide](https://udacity.github.io/git-styleguide/), and follow the "fork-and-pull" Git workflow:

1. Fork the repo on GitHub
1. Clone the project to your own computer
1. Commit changes to your own branch
1. Push your work back up to your fork
1. Submit a Pull request so that I can review your changes

Note: Please take care to merge the latest from "upstream" before making a pull request.

## To Do

[ ] Add:
  * requirements.txt
  * setup.py
  * /tests/test_basic.py
  * /tests/test_advanced.py
  
[ ] Add database options (e.g. NoSQL, PostgreSQL, etc)

[ ] Add admin functions: create filter dictionaries, instead of (re)creating with every run

[ ] Add option to Limit post results (to each search, or global, or at a time)

[ ] Add filters for categories other than the default car/truck

[ ] Add error handling and search parameter validation

[ ] Track changes to search parameters (index on other than name?)

