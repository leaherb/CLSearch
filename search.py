import sys
import os
import search as cls
import pandas as pd

##
## Main
##
## TODO:
#  * Add max results (to each search, or global, or at a time)
#  * Add scheduling by search
#  * Better handling of filters, and filters for categories other than car/truck
#  * Lots more error handling and search parameter validation
#  * Track changes in search parameters (index on other than name?)

## Load global parameters
email_config_file = './email_config.yml'
searches_config_file = './searches_config.yml'
database = 'database.pickle'

## Load email configuration settings 
try:
    email_configs = cls.load_yaml(email_config_file)
except Exception as e:
    print('{error}\nUnable to load YAML file \'{filename}\'. \nContinuing without email alert option ...'.\
          format(error=e, filename=email_config_file))
    
## Load search parameter settings 
try:
    saved_searches = cls.load_yaml(searches_config_file)
except Exception as e:
    print('{error}\nUnable to load YAML file \'{filename}\'. Quitting ...'.\
          format(error=e, filename=searches_config_file))
    sys.exit(1)


## Load prior results database 
if os.path.isfile(database):
    database_df = cls.load_data(database)
else:
    database_df = pd.DataFrame()

all_df = pd.DataFrame()   # compilation of search results this run

## Loop through saved searches, processing each
for search in saved_searches:
    print('='*50)
    #print(saved_searches[search])
    this_search = cls.SearchCarsTrucks(search_name=search, \
                                       config=saved_searches[search])
    print(this_search.search_name)
    
    ## Build dictionary of filters
    # TODO:
    #     * add category (and site?) to dictionary
    #     * see if it works adding &1=2
    #     * move this function to admin function then load once as yaml or json
    filters_dict = cls.build_indexed_filters(this_search.url_base)
    
    # process alert only if status is active
    if this_search.status == 'active':
        # get post result details 
        this_search.get_results(database=database_df, filters_dict=filters_dict)

        # add this search's results to all searches in this run
        all_df = all_df.append(this_search.results, ignore_index = True)

        # if there's an email addreess, send alert of any new posts
        new_df = this_search.results.query('notify == True')
        print('{} new posts found'.format(len(new_df)))
        
        if len(new_df) > 0 and this_search.email:
            print('emailing to ', this_search.email)
            this_search.send_email(email_configs, new_df)

# write all results, previous and this run, to storage as the new database
cls.dump_data(database, database_df.append(all_df, ignore_index=True))
