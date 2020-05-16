## Define objects and functions used by craigslist-search-alert

## Libraries
import os
import sys
import yaml
from requests import get
from datetime import datetime
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
import pickle
from time import sleep
from random import randint # avoid too many requests too fast
from warnings import warn
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from IPython.display import Image, HTML


## Objects
class SearchBase(object):
    """Base class for a single Craigslist search."""

    default_site = 'olympic'
    default_category = 'cta'
    
    def __init__(self, search_name, config):
        self.search_name = search_name
        self.status = config['metadata']['status']
        self.username = config['metadata']['username']
        if 'email' in config['metadata']:
            self.email = config['metadata']['email']
        else:
            self.email = None
        self.site = config['site']
        self.category = config['category']
        # keyword query, if any
        if 'keywords' in config:
            self.keywords = config['keywords']
        else:
            self.keywords = None
        # filters, if any
        if 'filters' in config:
            self.filters = config['filters']
        else:
            self.filters = None
        self.url_base = 'https://' + self.site + \
                        '.craigslist.org/search/' + self.category 
        self.url = self.url_base + '?'
        # TODO: Add filters. If no filters, add '1=1' as placehoder so multi-page results work
        self.results = pd.DataFrame()

        
    def get_results(self, database, filters_dict):
        """Create dataframe of search results."""
        # add keyword search to url
        if self.keywords:
            self.url = self.url + self.make_keyword_str()
        # add filters to url
        if self.filters:  
            self.url = self.url + self.make_filter_str(filters_dict)
        # update self.results with posts scraped from this search
        print(self.url)
        self.scrape_pages()
        # clean post data
        self.clean_results()
        # set 'notify' = True where post appears new (compared to database)
        self.mark_new_posts(database)
        
        return None


    def make_filter_str(self, filters):
        """
        Return string containing filter queries for Craigslist endpoint.
        """
        result_filters = ''
        ## There are 3 types of Craigslist filters (left column of Craigslist page):
        ##   * Boolean (True if box is checked, false if not checked)
        ##   * User values (user enters a value into a box, e.g. min price)
        ##   * Checkbox values (a given list of values, user can choose multiple checkboxes)
        if 'filter_booleans' in self.filters:
            self.filter_booleans = self.filters['filter_booleans']
        else:
            self.filter_booleans = None
        if 'filter_values' in self.filters:
            self.filter_values = self.filters['filter_values']
        else:
            self.filter_values = None
        if 'filter_boxes' in self.filters:
            self.filter_boxes = self.filters['filter_boxes']
        else:
            self.filter_boxes = None           

        # boolean filters
        try:
            for boo in self.filter_booleans:
                result_filters = result_filters + '&' + boo + '=1'
        except:
            None

        # user value filters
        try:
            for key, item in self.filter_values.items():
                if type(item) is str:
                    result_filters = result_filters + '&' + key + '=' + item
                elif type(item) is list:
                    for value in item:
                        result_filters = result_filters + '&' + key + '=' + value
        except:
            None

        # checkbox value filters
        try:
            for key, item in self.filter_boxes.items():
                #this_dict = checkbox_dict[key]
                this_dict = filters_dict[key]
                choices = ''.join(['&' + key + '=' + str(this_dict[x]) for x in item])
                result_filters = result_filters + choices
        except:
            None

        return result_filters

    

    def make_keyword_str(self):
        """
        Return string containing keyword query(ies) suitable for endpoint.
        """
        result_query = ''
        try:
            and_list = self.keywords['and'] 
        except:
            and_list = ''
        
        try:
            or_list = self.keywords['or']
        except:
            or_list = ''
        
        if not and_list and not or_list:
            return ''  # None will cause error 
        
        # use parentheses to separate series of 'or's from the 'and's 
        left = '%28'  # left parentheses
        right = '%29' # right parentheses
        or_tag = '%7C'
        and_tag = '%20'

        or_words = ''
        and_words = ''
        
        # build word search query
        if or_list:
            or_words = left + or_tag.join(or_list) + right
        if and_list:
            and_words = and_tag.join(and_list)

        # strip leading/following '+', in case there are not both or's and and's
        result_query = '?query=' + \
            '+'.join([or_words, and_words]).lstrip('+').rstrip('+')

        print('result_query = ', result_query)
            
        return result_query

    

    def scrape_pages(self):
        """Update self.results with post information scraped from self.url."""
        # Get first page of posts, and the total post count
        # (including any posts that extend beyond first page)
        response = get(self.url)
        page1_soup = BeautifulSoup(response.text, 'html.parser')
        page1_posts = page1_soup.find_all('li', class_= 'result-row')
        post_count = int([item.get_text() for item in page1_soup.select("span.totalcount")][0])
        
        # Parse the first page of posts, adding to self.results dataframe.
        for post in page1_posts:
                self.results = self.results.append(parse(post), \
                                                   ignore_index = True)

        # Each craigslist page is limited to 120 posts.
        # If our total post count <= page limit then we're done here.
        # Otherwise, continue parsing the rest of pages, one page at a time. 
        # To get additional pages, query craigslist again, adding the index of the
        # first post on the 'next' page. Before looping through the rest of the pages,
        # create an array of indexes of the first post of each page,
        # starting with 120 and incrementing by 120.        
        # For example, if there 275 posts, then page_index = [ 120 240 ]
        page_limit = 120
        if int(post_count) > page_limit:
            page_indexes = np.arange(page_limit, post_count+1, page_limit)
            for page in page_indexes:
                page_end_point = self.url + '&s=' + str(page)
                response = get(page_end_point)
                sleep(randint(1,5))
                #throw warning for status codes that are not 200
                if response.status_code != 200:
                    warn('Request: {request}; Status code: {status}'.format(request=requests, status=response.status_code))
                page_html = BeautifulSoup(response.text, 'html.parser')
                page_posts = page_html.find_all('li', class_= 'result-row')
                for post in page_posts:
                    self.results = self.results.append(parse(post), \
                                                       ignore_index = True)               

        print('Result count = ', len(self.results))

        return None


    
    def mark_new_posts(self, old_df):
        """
        Set 'notify' = True if search results appear new."
        """
        self.results['notify'] = False
        # columns to compare for differences
        columns = ['search_name','pid','cost','descr','pic']
        if len(old_df) > 0:    
            self.results['notify'] = ~self.results[columns].isin(old_df[columns])
        else:
            self.results['notify'] = True

        return None



    def clean_results(self):
        """Clean results dataframe."""
        # drop duplicate post URLs, avoiding spammy listings.
        self.results = self.results.drop_duplicates(subset='webpage')
        # tie results to search name 
        self.results['search_name'] = self.search_name
        # convert datetime strings into datetime objects
        self.results['post_date'] = self.results['post_date'].astype('datetime64[s]')
        self.results['crawl_date'] = self.results['crawl_date'].astype('datetime64[s]')
    
        return None


    def send_email(self, email_dict, new_df):
        """Send email alert with contents of given dataframe."""
        sender_email = email_dict['sender_email']
        smtp_server = email_dict['smtp_server']
        smtp_port = email_dict['smtp_port']
        smtp_user = email_dict['smtp_user']
        smtp_password = email_dict['smtp_password']
        # Create message container - the correct MIME type is multipart/alternative.
        msg = MIMEMultipart('alternative')
        msg['Subject'] = 'for ' + self.search_name
        msg['From'] = 'Craigslist Search Alert <' + sender_email + '>'
        msg['To'] = self.email

       # Create the body of the message (a plain-text and an HTML version).
        msg_text = "Recent listings for your {name} search:\n{listings}". \
                   format(name=self.search_name, \
                          listings=new_df[['webpage']]. \
                          to_string(index=False, header=False))
        columns = ['cost','descr','area','post_date','webpage','pic']
        pd.set_option('display.max_colwidth', -1)
        msg_html = '<html> <head></head> <body> \
                    <h2>Recent listings for: {name}</h2> {listings} \
                    </body> </html> '.\
                    format(listings=new_df[columns].to_html(), name=self.search_name) 

        # Record the MIME types of both parts - text/plain and text/html.
        part1 = MIMEText(msg_text, 'plain')
        part2 = MIMEText(msg_html, 'html')

        # Attach parts into message container.
        # According to RFC 2046, the last part of a multipart message,
        # in this case the HTML message, is best and preferred.
        msg.attach(part1)
        msg.attach(part2)
        # Send the message via SMTP server.
        mail = smtplib.SMTP(smtp_server, smtp_port)
        mail.ehlo()
        mail.starttls()
        mail.login(smtp_user, smtp_password)
        mail.sendmail(sender_email, self.email, msg.as_string())
        mail.quit()

        return None
        


class SearchCarsTrucks(SearchBase):
    """Search object for 'Cars and Trucks' for sale."""
    default_category = 'cta'




## Functions
def load_yaml(filename):
    """Return dictionary loaded with YAML file."""
    with open(filename, 'r') as yaml_file:
        # identifying Loader forces all parameters as str type
        return yaml.load(yaml_file, Loader=yaml.loader.BaseLoader)



def dump_yaml(filename, this_dict):
    with open(filename, 'w') as yaml_file:
        yaml.dump(this_dict, yaml_file, default_flow_style=False)
    return None



def load_data(filename):
    """Return dataframe loaded with pickled file."""
    with open(filename, 'rb') as f:
        return pickle.load(f)



def dump_data(filename, this_df):
    """Write pickled file with dataframe contents. Return None."""
    with open(filename, 'wb') as f:
        pickle.dump(this_df, f)
    return None



def parse(post):
    """Return dictionary of post data."""
    rec = {}
    rec['crawl_date'] = datetime.now().isoformat()
    rec['pid'] = post['data-pid']
    # get id of first pic, skipping first 2 characters ('1:')
    try:
        rec['pic'] = post.a['data-ids'].split(',')[0][2:]
        rec['pic'] = 'https://images.craigslist.org/' + rec['pic'] + '_300x300.jpg'
    except:
        None
    rec['cost'] = post.a.text.strip() or None 
    rec['post_date'] = post.p.time['datetime']
    rec['webpage'] = post.a['href']
    rec['descr'] = post.p.a.string.strip()
    # area (location) tags depend on search parameters
    try:
        rec['area'] = post.find('span', class_= 'nearby').text.strip()[1:-1]
    except:
        try:
            rec['area'] = post.find('span', class_= 'result-hood').text.strip()[1:-1]
        except:
            rec['area'] = None

    return rec



def build_indexed_filters(url):
    """
    Return embedded dictionary of filters and their indexed options.
    For example:
    {'auto_drivetrain': {'4wd': 3, 'fwd': 1, 'rwd': 2},
     'auto_fuel_type': {'diesel': 2, 'electric': 4, 'gas': 1, 'hybrid': 3, 'other': 5}
    """
    filters_dict = {}

    response = get(url)
    soup = BeautifulSoup(response.content, 'lxml')
    for list_filter in soup.find_all('div', class_='search-attribute'):
        filter_key = list_filter.attrs['data-attr']
        filter_labels = list_filter.find_all('label')
        options = [opt.text.strip() for opt in filter_labels]
        filters_dict[filter_key] = options

    # Index options for each filter, starting and incrementing by 1,
    # except 'condition' which starts and increments by 10.
    for key, value in filters_dict.items():
        step = 1
        stop = len(value) + 1
        if key == 'condition':
            step *= 10
            stop *= 10

        filters_dict[key] = dict(zip(value, range(step, stop, step)))

    return filters_dict



def make_filter_str(this_search, filters_dict):
    """
    Return string containing filter queries for Craigslist endpoint.
    """
    result_filters = ''

    ## There are 3 types of Craigslist filters (left column of Craigslist page):
    ##   * Boolean (True if box is checked, false if not checked)
    ##   * User values (user enters a value into a box, e.g. min price)
    ##   * Checkbox values (a given list of values, user can choose multiple checkboxes)

    # boolean filters
    try:
        for boo in this_search['filter_booleans']:
            result_filters = result_filters + '&' + boo + '=1'
    except:
        None

    # user value filters
    try:
        for key, item in this_search['filter_values'].items():
            if type(item) is str:
                result_filters = result_filters + '&' + key + '=' + item
            elif type(item) is list:
                for value in item:
                    result_filters = result_filters + '&' + key + '=' + value
    except:
        None

    # checkbox value filters
    try:
        for key, item in this_search['filter_boxes'].items():
            #this_dict = checkbox_dict[key]
            this_dict = filters_dict[key]
            choices = ''.join(['&' + key + '=' + str(this_dict[x]) for x in item])
            result_filters = result_filters + choices
    except:
        None

    return result_filters


##
## EOF
##

