import sys
import os
import pandas as pd
import search as cls
import notify


def main():
    ## TODO:
    #  * Add max results (to each search, or global, or at a time)
    #  * Add scheduling by search
    #  * Better handling of filters, and filters for categories other than car/truck
    #  * Lots more error handling and search parameter validation
    #  * Track changes in search parameters (index on other than name?)

    ## Load global parameters
    searches_config_file = './searches_config.yml'
    database_type = 'JSON'  # ['pickle', 'JSON']
    database = 'database.' + database_type

    print(database)

    
    ## Load search parameter settings 
    try:
        saved_searches = cls.load_yaml(searches_config_file)
    except Exception as e:
        print('{error}\nUnable to load YAML file \'{filename}\'. Quitting ...'.\
            format(error=e, filename=searches_config_file))
        sys.exit(1)


    ## Initialize new search results
    all_df = pd.DataFrame()   

    ## Load prior results  
    if os.path.isfile(database):
        database_df = cls.load_data_pickle(database)
    else:
        database_df = pd.DataFrame()

    pd.set_option('display.max_columns', None)
    print(f'Rows pre-existing: {len(database_df.index)}\n')
    print(database_df.tail())


    ## Process search requests
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
        
        # process active searches only. todo: filter search list prior to for loop
        if this_search.status == 'active':
            # get post result details 
            this_search.get_results(database=database_df, filters_dict=filters_dict)

            # add this search's results to all searches in this run
            all_df = all_df.append(this_search.results, ignore_index = True)


    # write all results, previous and this run, to storage as the new database
    cls.dump_data_pickle(database, database_df.append(all_df, ignore_index=True))



if __name__ == "__main__":
    # execute only if run as a script
    main()