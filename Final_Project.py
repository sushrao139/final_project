#########################################
##### Name:   Sushmitha Rao         #####
##### Uniqname:   sushrao           #####
#########################################

from requests_oauthlib import OAuth1
import json
import requests

import urllib
import secrets # file that contains your OAuth credentials

CACHE_FILENAME = "etsy_cache.json"
CACHE_DICT = {}

client_key = secrets.ETSY_API_KEY #"m9nyb24i67vb4ibw1qoy9pua"

oauth = OAuth1(client_key)

print(oauth)

def test_oauth():
    ''' Helper function that returns an HTTP 200 OK response code and a 
    representation of the requesting user if authentication was 
    successful; returns a 401 status code and an error message if 
    not. Only use this method to test if supplied user credentials are 
    valid. Not used to achieve the goal of this assignment.'''

    url = " https://www.etsy.com/oauth/connect"
    auth = OAuth1(client_key)
    authentication_state = requests.get(url, auth=auth).json()
    return authentication_state


def open_cache():
    ''' Opens the cache file if it exists and loads the JSON into
    the CACHE_DICT dictionary.
    if the cache file doesn't exist, creates a new cache dictionary
    
    Parameters
    ----------
    None
    
    Returns
    -------
    The opened cache: dict
    '''
    try:
        cache_file = open(CACHE_FILENAME, 'r')
        cache_contents = cache_file.read()
        cache_dict = json.loads(cache_contents)
        cache_file.close()
    except:
        cache_dict = {}
    return cache_dict


def save_cache(cache_dict):
    ''' Saves the current state of the cache to disk
    
    Parameters
    ----------
    cache_dict: dict
        The dictionary to save
    
    Returns
    -------
    None
    '''
    dumped_json_cache = json.dumps(cache_dict)
    fw = open(CACHE_FILENAME,"w")
    fw.write(dumped_json_cache)
    fw.close() 


def construct_unique_key(baseurl, params):
    ''' constructs a key that is guaranteed to uniquely and 
    repeatably identify an API request by its baseurl and params

    AUTOGRADER NOTES: To correctly test this using the autograder, use an underscore ("_") 
    to join your baseurl with the params and all the key-value pairs from params
    E.g., baseurl_key1_value1
    
    Parameters
    ----------
    baseurl: string
        The URL for the API endpoint
    params: dict
        A dictionary of param:value pairs
    
    Returns
    -------
    string
        the unique key as a string
    '''
    #constructing the url using urllib instead of example from lecture
    queryString = urllib.parse.urlencode(params)
    key = (f"{baseurl}?{queryString}")
    return key


def make_request(baseurl, params):
    '''Make a request to the Web API using the baseurl and params
    
    Parameters
    ----------
    baseurl: string
        The URL for the API endpoint
    params: dictionary
        A dictionary of param:value pairs
    
    Returns
    -------
    dict
        the data returned from making the request in the form of 
        a dictionary
    '''
    key = construct_unique_key(baseurl,params)
    response = requests.get(key, {"api_key": client_key})
    return response.json()



def make_request_with_cache(baseurl, params):
    '''Check the cache for a saved result for this baseurl+params:values
    combo. If the result is found, return it. Otherwise send a new 
    request, save it, then return it.

    AUTOGRADER NOTES: To test your use of caching in the autograder, please do the following:
    If the result is in your cache, print "fetching cached data"
    If you request a new result using make_request(), print "making new request"

    Do no include the print statements in your return statement. Just print them as appropriate.
    This, of course, does not ensure that you correctly retrieved that data from your cache, 
    but it will help us to see if you are appropriately attempting to use the cache.
    
    Parameters
    ----------
    baseurl: string
        The URL for the API endpoint
    params: dictionary
        dictionary of parameters: location and limt (number of results)
    
    Returns
    -------
    dict
        the results of the query as a dictionary loaded from cache
        JSON
    '''

    if CACHE_FILENAME!= []:
        cache_dict = open_cache()
        country = params['location']
        if country in cache_dict:
            return cache_dict #[country]
        else:
            cache_dict = open_cache()
            cache_dict[country] = make_request(baseurl, params)
            save_cache(cache_dict)
            return cache_dict #[country]

    else:
        country = params['location']
        cache_dict = {}
        print(f'\nFetching data from Etsy. Please wait')
        cache_dict[country] = make_request(baseurl, params)
        save_cache(cache_dict)
        return cache_dict #[country]



def create_sql_database_tables():
    '''
    connects to sqlite3 and creates primary key table and foreign key table
    in a new database called ETSY. The datatype for each column is also mentioned
    
    Parameters
    ----------
    None
    
    Returns
    -------
    None
    '''
    import sqlite3

    conn = sqlite3.connect("ETSY.sqlite")
    cur =  conn.cursor()
    drop_listing = '''
        DROP TABLE IF EXISTS "listing";
    '''
    create_listing = '''
        CREATE TABLE IF NOT EXISTS "listing" (
            "listing_id" INTEGER NOT NULL,
            "user_id" INTEGER NOT NULL,
            "title" TEXT NOT NULL,
            "price" REAL NOT NULL,
            "currency_code" TEXT NOT NULL,
            "quantity" INTEGER NOT NULL,
            "tags" TEXT NOT NULL,
            "views" INTEGER NOT NULL,
            "num_favorer" INTEGER NOT NULL,
            "who_made" TEXT NOT NULL,
            "is_vintage" TEXT NOT NULL,
            "country" TEXT NOT NULL
        );
    '''
#PRIMARY KEY
#listing['listing_id'], listing['user_id'], listing['title'], listing['price'], listing['currency_code'], listing['quantity'], listing['tags'], listing['views'], listing['num_favorers'], listing['who_made'], listing['is_vintage'], country)
    drop_user_shop = '''
        DROP TABLE IF EXISTS "user_country";
    '''
    create_user_shop = '''
        CREATE TABLE IF NOT EXISTS "user_shop" (
            "user_id" INTEGER NOT NULL,
            "shop_section_id" INTEGER,
            "country" TEXT NOT NULL
        );
    '''

    cur.execute(drop_listing)
    cur.execute(create_listing)
    cur.execute(drop_user_shop)
    cur.execute(create_user_shop)
    conn.commit()

def add_data_to_database(cache_dict):
    '''
    accepts the entire cache dictionary and
    converts the data into two tables with a
    primary key:listing_id and secondary_key:user_id

    Parameters
    ----------
    cache_dict: dictionary
        dictionary of country(key): listings(value) 

    Returns
    -------
    None
    '''
    import sqlite3

    try:
        conn = sqlite3.connect(r"C:\Users\sushr\Documents\umich\courses\si507\final_proj\ETSY.sqlite")
        cur =  conn.cursor()
        #print("success")

        for country, listing_data in cache_dict.items():
            listings = listing_data['results']
            #print(listing)
            for listing in listings:
                if listing["state"] == "active":
                    insert_listing = '''
                        INSERT INTO listing VALUES(?,?,?,?,?,?,?,?,?,?,?,?)
                    '''
                    listing_items = [listing['listing_id'], listing['user_id'], listing['title'],
                     listing['price'], listing['currency_code'], listing['quantity'], str(listing['tags']), listing['views'],
                     listing['num_favorers'], listing['who_made'], listing['is_vintage'], country]
                    cur.execute(insert_listing, listing_items)
            conn.commit()
    except sqlite3.Error as error:
        print("Failed to insert data into sqlite table", error)

    try:
        conn = sqlite3.connect(r"C:\Users\sushr\Documents\umich\courses\si507\final_proj\ETSY.sqlite")
        cur =  conn.cursor()
        #print("success")

        for country, listing_data in cache_dict.items():
            listings = listing_data['results']
            #print(listing)
            for listing in listings:
                if listing["state"] == "active":
                    insert_user_shop = '''
                        INSERT INTO user_shop VALUES(?,?,?)
                    '''
                    listing_items = [listing['user_id'], listing['shop_section_id'], country]
                    cur.execute(insert_user_shop, listing_items)
            conn.commit()
    except sqlite3.Error as error:
        print("Failed to insert data into sqlite table", error)

def convert_sql_to_lists():
    '''
    connects to sqlite3 and retreives primary key table and foreign key table
    from database called ETSY. Then appends each row of data into a list for easier plotting
    
    Parameters
    ----------
    None
    
    Returns
    -------
    (price, who_made, is_vintage, country): Tuple

    returns a tuple of exctracted lists
    '''
    import sqlite3
    conn = sqlite3.connect(r"C:\Users\sushr\Documents\umich\courses\si507\final_proj\ETSY.sqlite")
    cur =  conn.cursor()
    cur.execute('SELECT price, who_made, is_vintage, currency_code, country FROM listing')
    data = cur.fetchall()
    # data[*][0] = temperature
    # data[*][1] = humidity
    # data[*][2] = feelslike
    # data[*][3] = timenow

    price = []
    who_made = []
    is_vintage = []
    currency_code = []
    country = []

    for row in data:
        price.append(row[0])
        who_made.append(row[1])
        is_vintage.append(row[2])
        currency_code.append(row[3])
        country.append(row[4])
    return (price, who_made, is_vintage, currency_code, country)

def plot_bar_chart(country_to_check, viz_choice):
    '''
    calls convert_sql_to_lists() and uses data to plot
    bar charts to visualize the data corresponding to the selected choice: 1,2,3,4
    
    Parameters
    ----------
    country_to_check: String
    string that can be filtered from the the list to plot only relevant data

    viz_choice: int
    a number between 1-4 which outputs a plot of choice
    
    Returns
    -------
    None
    '''
    price, who_made, is_vintage, currency_code, country = convert_sql_to_lists()
    list_of_available_countries, country_sellers = web_scrape_for_country_data()

    print(country_to_check)
    import pandas as pd
    import matplotlib.pyplot as plt
    df = pd.DataFrame({'price':price,'who_made':who_made, 'is_vintage': is_vintage, 'currency_code': currency_code, 'country': country})
    df_seller_by_country = pd.DataFrame({'country': list_of_available_countries, 'number_of_sellers': country_sellers})
    df_seller_by_country['country'] = df_seller_by_country['country'].str.lower()
    print(df_seller_by_country)
    df_country_to_check = df[df.country == country_to_check]
    df_other = df[df.country != country_to_check]
    if viz_choice == "1":

        bin_range = 10
        plt.hist([df_country_to_check.price, df_other.price],range=[0, 50], bins = bin_range, label=['Selected country: {country_to_check}', 'Other Countries'])
        plt.legend(loc='upper left')
        plt.ylabel('Count')
        plt.title('Price Distribution of Etsy Listings from Different Countries')
        plt.show()
    if viz_choice == "2":
        df_count_cc = df.groupby('currency_code').count()['country']
        df_count_cc = df_count_cc.reset_index()
        df_count_cc['percentage_currency'] = (df_count_cc['country'] / df_count_cc['country'].sum())*100#(df_count_cc['count'] / df_count_cc['count'].sum())*100
        print(df_count_cc)
        labels = df_count_cc['currency_code']
        sizes = df_count_cc['percentage_currency']
        explode = [0] * len(df_count_cc)
        print(country_to_check)
        currency_of_selected_country = df[df['country'] == country_to_check]['currency_code'].reset_index()#[0]
        currency_of_selected_country =currency_of_selected_country['currency_code'][0]
        print(currency_of_selected_country)
        index = pd.Index(df_count_cc['currency_code'])
        currency_of_selected_country_index = index.get_loc(currency_of_selected_country)
        explode[currency_of_selected_country_index] = 0.1
        print(explode)
        fig1, ax1 = plt.subplots()
        ax1.pie(sizes, explode=explode, labels=labels, autopct='%1.1f%%',
                shadow=True, startangle=90)
        ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
        plt.title(f'Distribution of the currencies used by {len(df.country.unique())} countries in the database')
        plt.show()
    if viz_choice == "3":
        df_count_who_made = df_country_to_check.groupby('who_made').count()['country']
        df_count_who_made = df_count_who_made.reset_index()
        df_count_who_made['percentage_handmade'] = (df_count_who_made['country'] / df_count_who_made['country'].sum())*100#(df_count_cc['count'] / df_count_cc['count'].sum())*100
        print(df_count_who_made)
        labels = df_count_who_made['who_made']
        sizes = df_count_who_made['percentage_handmade']
        fig, (ax1, ax2) = plt.subplots(1,2)
        ax1.pie(sizes, labels=labels, autopct='%1.1f%%',
                shadow=True, startangle=90)
        ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
        fig.suptitle(f'Distribution of the handmade items in {country_to_check} vs. the world in the top 100 items')
        df_count_who_made_world = df.groupby('who_made').count()['country']
        df_count_who_made_world = df_count_who_made_world.reset_index()
        df_count_who_made_world['percentage_handmade'] = (df_count_who_made_world['country'] / df_count_who_made_world['country'].sum())*100#(df_count_cc['count'] / df_count_cc['count'].sum())*100
        print(df_count_who_made_world)
        labels_world = df_count_who_made_world['who_made']
        sizes_world = df_count_who_made_world['percentage_handmade']
        ax2.pie(sizes_world, labels=labels_world, autopct='%1.1f%%', shadow=True, startangle=90)
        ax2.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
        plt.show()
    if viz_choice == "4":
        # countries = df_seller_by_country.country
        # print(countries)
        # sellers = df_seller_by_country.number_of_sellers
        import plotly.express as px
        fig = px.bar(df_seller_by_country, x='country', y='number_of_sellers', title=f"Number of Sellers Per Country. \nThe Number of Sellers in {country_to_check} is {df_seller_by_country[df_seller_by_country['country'] == country_to_check]['number_of_sellers'].item()}")
        print(df_seller_by_country[df_seller_by_country['country'] == "france"]['number_of_sellers'])
        fig.show()
        # print(sellers)
        # fig, ax = plt.subplots()
        # ax.bar(countries.tolist(),sellers.tolist())
        # plt.show()
    pass

def web_scrape_for_country_data():
    '''
    scrapes website which shows the number of sellers and participating countries in etsy
    and extracts two lists: number of sellers and country name
    
    Parameters
    ----------
    None
    
    Returns
    -------
    country_list, country_sellers: tuple

    returns a tuple of lists containing number of sellers per country and list of country names
    '''
    from bs4 import BeautifulSoup
    import requests


    BASE_URL = "http://topcraftsellers.com/top-etsy-sellers-by-country"
    response = requests.get(BASE_URL)
    soup = BeautifulSoup(response.text, 'html.parser')
    countrytable_1_parent = soup.find_all(class_="table table-striped table-condensed table-hover")
    # list_of_td = countrytable_1_parent.find('td')
    country_list = []
    country_sellers = []
    for country_table_sublist in countrytable_1_parent:
        country_table_sublist = country_table_sublist.find_all('td')
        country_table_sublist =[x.text.strip() for x in country_table_sublist]
        country_list.append([i for i in country_table_sublist[1::3]])
        country_sellers.append([i for i in country_table_sublist[2::3]])

    country_list = [item for sublist in country_list for item in sublist]
    country_sellers = [item for sublist in country_sellers for item in sublist]
    # course_listing_divs = course_listing_parent.find_all('div',recursive = False) #recursive false prevents find all from looking inside div
    # print(course_listing_divs[0])
    return(country_list, country_sellers)


if __name__ == "__main__":
    if not client_key:# or not client_secret:
        print("You need to fill in CLIENT_KEY and CLIENT_SECRET in secret_data.py.")
        exit()

    
    baseurl = "https://openapi.etsy.com/v2/listings/active"
    count = 100
    # for running this code for the first time, none of these countries are previously populated.
    # this seciton will run first before prompting user input
    location_list = ["india","canada","united states","france","china","pakistan", "brazil", "united kingdom", "ireland", "egypt"]
    for location in location_list:
        params = {"location": location,"limit":count,"sort_on":"score"}
        d = make_request_with_cache(baseurl,params)
    create_sql_database_tables()
    add_data_to_database(make_request_with_cache(baseurl,params))
    list_of_available_countries, country_sellers = web_scrape_for_country_data()
    list_of_available_countries = [each_string.lower() for each_string in list_of_available_countries]

    while True:
        country_to_check = input("Enter a country name to check database for top 100 Etsy listing in that country \n or press 1 to check countries already available in the database \n or type exit to exit program: ")
        if country_to_check == "1":
            CACHE_DICT = open_cache()
            available_countries = [*CACHE_DICT.keys()]
            country_to_check = input(f'\n\n{[country for country in available_countries]}. Enter any country name or type exit to exit program: ')
            if country_to_check == "exit":
                exit()
            else:
                params = {"location": country_to_check,"limit":count,"sort_on":"score"}
                cache_dict_w_new_country = make_request_with_cache(baseurl,params)
                create_sql_database_tables()
                add_data_to_database(make_request_with_cache(baseurl,params))
                viz_choice = input("\n\nSelect choice for visualization for selected country from sample of 100 listings:\n 1 - selected country item price distribution \n 2 - percentage of handmade vs. collectively made vs. made by someone else \n 3 - percentage of vintage items \n 4 - number of sellers \n or type 'exit' to exit program: ")
                while True:
                    if viz_choice == "exit":
                            exit()
                    elif viz_choice not in ["1","2","3","4"]:
                        viz_choice = input("\n\ninvalid choice! Must be selectrd from:\n1 - selected country price range \n2 - percentage of handmade vs. collectively made vs. made by someone else \n3 - percentage of vintage items \n4 - number of sellers \nor type 'exit' to exit program: ")
                        if viz_choice == "exit":
                            exit()
                        elif viz_choice not in ["1","2","3","4"]:
                            continue
                        else:
                            plot_bar_chart(country_to_check, viz_choice)
                    else:
                        plot_bar_chart(country_to_check, viz_choice)
                    break
            break
        elif country_to_check == "exit":
            exit()
        elif country_to_check not in list_of_available_countries:
            while True:
                country_to_check = input(f'\n\n{country_to_check} not in list. Please enter a valid country name or type exit to exit program: ')
                if country_to_check == "exit":
                    exit()
                elif country_to_check not in list_of_available_countries:
                    continue
                else:
                    params = {"location": country_to_check,"limit":count,"sort_on":"score"}
                    cache_dict_w_new_country = make_request_with_cache(baseurl,params)
                    create_sql_database_tables()
                    add_data_to_database(make_request_with_cache(baseurl,params))
                    #price, who_made, is_vintage, currency_code, country = convert_sql_to_lists()
                    viz_choice = input("\n\nSelect choice for visualization for selected country from sample of 100 listings:\n 1 - selected country price range \n 2 - percentage of handmade vs. collectively made vs. made by someone else \n 3 - percentage of vintage items \n 4 - number of sellers \n or type 'exit' to exit program: ")
                    while True:
                        if viz_choice == "exit":
                                exit()
                        elif viz_choice not in ["1","2","3","4"]:
                            viz_choice = input("\n\ninvalid choice! Must be selectrd from:\n1 - selected country price range \n2 - percentage of handmade vs. collectively made vs. made by someone else \n3 - percentage of vintage items \n4 - number of sellers \nor type 'exit' to exit program: ")
                            if viz_choice == "exit":
                                exit()
                            elif viz_choice not in ["1","2","3","4"]:
                                continue
                            else:
                                plot_bar_chart(country_to_check, viz_choice)
                        else:
                            plot_bar_chart(country_to_check, viz_choice)
                        break
                break
            break
        else:
            params = {"location": country_to_check,"limit":count,"sort_on":"score"}
            cache_dict_w_new_country = make_request_with_cache(baseurl,params)
            create_sql_database_tables()
            add_data_to_database(make_request_with_cache(baseurl,params))
            #price, who_made, is_vintage, currency_code, country = convert_sql_to_lists()
            viz_choice = input("\n\nSelect choice for visualization for selected country from sample of 100 listings:\n1 - selected country price range \n2 - percentage of handmade vs. collectively made vs. made by someone else \n3 - percentage of vintage items \n4 - number of sellers \nor type 'exit' to exit program: ")
            while True:
                if viz_choice == "exit":
                        exit()
                elif viz_choice not in ["1","2","3","4"]:
                    viz_choice = input("\n\ninvalid choice! Must be selectrd from:\n1 - selected country price range \n2 - percentage of handmade vs. collectively made vs. made by someone else \n3 - percentage of vintage items \n4 - number of sellers \nor type 'exit' to exit program: ")
                    if viz_choice == "exit":
                        exit()
                    elif viz_choice not in ["1","2","3","4"]:
                        continue
                    else:
                        plot_bar_chart(country_to_check, viz_choice)
                else:
                    plot_bar_chart(country_to_check, viz_choice)
                break
