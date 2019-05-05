# Import libraries
from bs4 import BeautifulSoup
from requests import get
import pandas as pd
import pandas_gbq
import time
import numpy as np
import datetime as dt
import regex as re
from google.cloud import bigquery

# Get product lists from first result page
def links_first_page(html_soup):
    links = []
    for i in html_soup.find_all("div", class_="is-visible item-box__container"):
        for t in i.find_all("section", class_="item-box js-catalog-item"):
            for z in t.find_all("figure", class_="item-box__media media media--item"):
                for y in z.find_all("div", class_="media__placeholder"):
                    for u in y.find_all("a", class_="media__image-wrapper js-item-link"):
                        links.append(u.get('href'))
    return links

# ## Get all product lists related to search
def all_product_lists(html_soup):
    next_pages = []
    for i in html_soup.find_all("div", class_="new-page-controls js-page-controls box box--plain"):
        for t in i.find_all("li", class_="new-pagination__step"):
            for z in t.find_all("a", class_="new-pagination__action"):
                next_pages.append(z.get('href'))
    return next_pages

# Get all product detail pages from all product list pages
def get_product_detail_pages(links, next_pages):
    for i in next_pages:
        next_url = "https://www.kleiderkreisel.de" + i
        response = get(next_url, headers=headers)
        html_soup = BeautifulSoup(response.text, 'html.parser')
        links_next_page = []
        for i in html_soup.find_all("div", class_="is-visible item-box__container"):
            for t in i.find_all("section", class_="item-box js-catalog-item"):
                for z in t.find_all("figure", class_="item-box__media media media--item"):
                    for y in z.find_all("div", class_="media__placeholder"):
                        for u in y.find_all("a", class_="media__image-wrapper js-item-link"):
                            links_next_page.append(u.get('href'))
    
    # Concatenate all product detail pages to scrape and create dataframe
    product_details = links + links_next_page

    product_detail_pages = []
    for i in product_details:
        product_url = "https://www.kleiderkreisel.de" + i
        product_detail_pages.append(product_url)
    df = pd.DataFrame({'product_detail_pages': product_detail_pages})

    return df, product_detail_pages


# ## Get info from product detail pages
def get_product_details(df, product_detail_pages):
    df['date'] = dt.datetime.now().date()
    df['product_name'] = np.nan
    df['pic_links'] = np.nan
    df['price'] = np.nan
    df['brand'] = np.nan
    df['condition'] = np.nan
    df['color'] = np.nan
    df['release_datetime'] = np.nan
    df['location'] = np.nan
    df['user_name'] = np.nan
    df['user_last_online'] = np.nan

    for index, i in enumerate(product_detail_pages):
    
        # get HTML for each product detail page
        response = get(i, headers=headers)
        #time.sleep(5)
        html_product = BeautifulSoup(response.text, 'html.parser')
    
        # Safe product name
        for i in html_product.find_all("h1", class_="details-list__item-title", itemprop="name"):
            name = i.text
            df['product_name'][index] = name
    
        # Safe thumb nail pics as list to dataframe
        pic_links = []
        for i in html_product.find_all("figure", class_=re.compile("item-description item-photo item-photo--")):
            for u in i.find_all("a", class_=re.compile("item-thumbnail")):
                pic_links.append(u.get('href'))
            df['pic_links'][index] = pic_links
        
        # Safe prices to df
        for i in html_product.find_all("div", class_="c-text--heading c-text--left c-text"):
            price = i.text
            df['price'][index] = price
        
        # Safe brand to df
        for i in html_product.find_all("div", class_="details-list__item-value"):
            for t in i.find_all("span"):
                brand = t.text
                df['brand'][index] = brand
            
        # Safe size to df
        for i in html_product.find_all("div", class_="details-list__item-value", itemprop="itemCondition"):
            condition = i.text
            df['condition'][index] = condition
        
        # Safe color to df
        for i in html_product.find_all("div", class_="details-list__item-value", itemprop="color"):
            color = i.text
            df['color'][index] = color
        
        # Safe release date to df > last online
        datetime = []
        for idf, i in enumerate(html_product.find_all("time", class_="relative")):
            datetime.append(i.get('datetime'))
        df['release_datetime'][index] = datetime[0]
        df['user_last_online'][index] = datetime[1]
    
        # Safe location to df
        # To Do: Get all locations
        for i in html_product.find_all("div", class_="details-list__item details-list--country"):
            location = i.text
            #print(location)
            df['location'][index] = location
    
    # TO DO size, payment options, clicks !!!
    #for i in html_product.find_all("div", class_="details-list__item-value"):
    #    print(i.text)
    
        # Safe user name to df
        for i in html_product.find_all("span", class_="user-login-name"):
            user_name = i.text
            df['user_name'][index] = user_name
    
    return df

if __name__ == "__main__":

    # Define header and URL
    headers = ({'User-Agent':
            'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36'})
    url = "https://www.kleiderkreisel.de/kleidung?order=newest_first&search_text=hemd%20minimum%20xl"

    # Start website request
    response = get(url, headers=headers)
    html_soup = BeautifulSoup(response.text, 'html.parser')

    # Run program
    links = links_first_page(html_soup)
    next_pages = np.unique(all_product_lists(html_soup)).tolist()[1:]
    df, product_detail_pages = get_product_detail_pages(links, next_pages)
    df = get_product_details(df, product_detail_pages)

    # Instantiate BigQuery client and write results to table
    project = 'kleiderkreisel-scraper'
    dataset_table_id = 'gunnar.minimum_shirt'
    client = bigquery.Client()
    pandas_gbq.to_gbq(df, dataset_table_id, project, if_exists='append')