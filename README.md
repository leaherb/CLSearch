# CL-Search

**CL-Search** is a microservce. I am building a system if microservices to, eventually, build an app to automate Craigslist searches that will notify the requestor of new search results.

## Purpose
Automate [Craigslist](https://www.craigslist.org/about/sites){target="_blank"} searches. Store search results in a database.

Any number of named searches (defined in **search_config.yml**) are initiated with each run of **search.py**. Search configurations can be archived (not included in a run), or activated (included in a run).

## Disclaimer

I have no affiliation with Craigslist.

This project was created for educational purposes. I do not endorse its use for crawling or downloading data from Craigslist.

## Usage
1. Add search parameters to the configuration file **searches_config.yml**, in [YAML](https://yaml.org/) format. Any number of searches can be added to **searches_config.yml**. Only those with `status: active` will be processed. 

2. Run search.py:
```
python search.py
```

3. Search results are saved to a database, currently a file called **database.JSON**. If there is no existing database file, one will be created.


## Project Status
This project a work in progress.

  * An interface for building named searches would be a welcome addition.
  * No analysis functions provided for analyzing the database. 
  * An alert notifications module is not completed.

## How to Contribute

I strongly encourage you to submit pull requests to make improvements to this project.

Please use the [Udacity Git Commit Message Style Guide](https://udacity.github.io/git-styleguide/), and follow the "fork-and-pull" Git workflow:

1. Fork the repo on GitHub
1. Clone the project to your own computer
1. Commit changes to your own branch
1. Push your work back up to your fork
1. Submit a Pull request so that I can review your changes

Note: Please take care to merge the latest from "upstream" before making a pull request.

## To Do

[ ] Update this README with better instructions

[ ] Add:
  * requirements.txt
  * setup.py
  * /tests/test_basic.py
  * /tests/test_advanced.py
  
[ ] Improve email body
  
[ ] Add SMS option, as well as multiple alert distinations (SMS and/or email)

[ ] Add database format options (e.g. MySQL)

[ ] Add admin functions: create filter dictionaries, instead of creating during every search.py run

[ ] Add option to Limit post results (to each search, or global, or at a time)

[ ] Add scheduling by search (1/day, 1/week, etc)

[ ] Add filters for categories other than the default car/truck

[ ] Add error handling and search parameter validation

[ ] Track changes to search parameters (index on other than name?)

