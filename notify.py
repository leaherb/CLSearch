    
## Load global parameters
email_config_file = './email_config.yml'

teststring = 'teststring'


def testme(str=teststring):
    print(str)


def main():
    ## Load email configuration settings 
    try:
        email_configs = cls.load_yaml(email_config_file)
    except Exception as e:
        print('{error}\nUnable to load YAML file \'{filename}\'. \nContinuing without email alert option ...'.\
            format(error=e, filename=email_config_file))

    # UNTESTED after refactoring from search.py...
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


if __name__ == "__main__":
    # execute only if run as a script
    testme('notify main')
    #main()