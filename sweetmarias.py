from bs4 import BeautifulSoup
from requests_html import HTMLSession
from pprint import pprint
from itertools import chain
import csv
import time


# url for webpage
url = 'https://www.sweetmarias.com/green-coffee.html?product_list_limit=all&sm_status=1'

s = HTMLSession()
r = s.get(url)

#render the page
r.html.render(sleep=3)

## make sure the page loads
## print(r.status_code)

products = r.html.find('div.table-wrapper', first=True)

# define a list in which to place all product dictionaries
product_list=[]
for item in products.absolute_links:
    r = s.get(item)
    # time.sleep(.5)

    # define a dict in which to place all product attributes
    product_dict={}

    # Check if the item is in stock
    if r.html.find('div.product-info-price', first=True):
        stock = True
    else:
        stock = False

    if stock:
        # print(f'{row_label}:{row_value}')
        name = r.html.find('h1.page-title', first=True)
        score = r.html.find('h5.score-value', first=True)
        price = r.html.find('span.price', first=True)
        specs = r.html.find('table.additional-attributes-table', first=True)
        # print(specs.html) # this is the table in html

        try:
            product_dict['score']=score.text
            product_dict['name']=name.text
            product_dict['price']=price.text
            product_dict['url']=item
            
            if specs.html:
                specs_present = True
            else:
                specs_present = False
            
            if specs.html and score != 'none':                    
                ## use beautiful soup to parse the specs table
                soup = BeautifulSoup(specs.html, 'lxml')
                table = soup.find_all('table')[0]
                
                ## parse the product specs table
                for row in table.find_all('tr'):
                    
                    th_tags = row.find('th')
                    row_label = th_tags.get_text().strip()

                    td_tags = row.find('td')
                    row_value = td_tags.get_text().strip()

                    product_dict[row_label]=row_value
            # print(product_dict)
            product_list.append(product_dict)
        except:
            pass

    else:
        pass

## make sure all product dictionaries have the same keys (important for writing to csv)
keys = set(chain.from_iterable(product_list))
for item in product_list:
     item.update({key: None for key in keys if key not in item})

pprint(product_list)

# write list of product dictionaries to csv file
with open('sm-green-instock.csv', mode='w') as csv_file:
    fieldnames = product_list[0].keys()
    writer = csv.DictWriter(csv_file, fieldnames=fieldnames)

    writer.writeheader()
    writer.writerows(product_list)
