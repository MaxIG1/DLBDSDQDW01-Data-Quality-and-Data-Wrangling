# %%
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import re
import pandas as pd
import datetime
import h5py
import os


# %% [markdown]
# ### Defining the Scrapper

# %%
# defining a span checker that analyzes how many subpages there are.
# This might change on a daily basis, which is why we need this function.


def span_checker(spans):
    max_num = 0
    for span in spans:
        try:
            int_span = int(span.text)
            if int_span > max_num:
                max_num = int_span
        except ValueError:
            pass
    print(f"The page contains {max_num} subpages")
    return max_num


# %%
def scrape(url, select_statement, site_type, title):
    max_num = 0

    # first, get the first site to access the navigation of it.
    # hence Yahoo is only on page site, the function will stop here if yahoo is scrapped.
    driver = webdriver.Chrome()
    driver.get(url)

    if site_type == "yahoo":
        button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CLASS_NAME, "btn.secondary.reject-all"))
        )
        button.click()
        WebDriverWait(driver, 10).until(EC.title_contains(title))
        html_content = driver.page_source
        soup = BeautifulSoup(html_content, "lxml")
        driver.quit()
        return soup

    if site_type == "boerse":
        html_content = driver.page_source
        soup = BeautifulSoup(html_content, "lxml")
        driver.quit()
        return soup

    html_content = driver.page_source
    soup = BeautifulSoup(html_content, "lxml")

    # second check how many pages there are
    spans = soup.select(select_statement)
    max_num = span_checker(spans)

    # third, access all the sites
    soup_list = []
    print("the following pages have been scrapped:")
    for i in range(1, max_num + 1):
        if site_type == "booking":
            url = url[:-1]
            driver.get(url + str(1 + (i - 1) * 25))
            print(url + str(1 + (i - 1) * 25))
            html_content = driver.page_source
            soup = BeautifulSoup(html_content, "lxml")
            soup_list.append(soup)
        elif site_type == "immowelt":
            print(url + str(i))
            driver.get(url + str(i))
            html_content = driver.page_source
            soup = BeautifulSoup(html_content, "lxml")
            soup_list.append(soup)
        else:
            pass

    # close the driver and
    driver.quit()

    # finally create the combined soup with all pages
    global combined_soup
    combined_soup = BeautifulSoup("", "lxml")
    for soup in soup_list:
        combined_soup.append(soup)


# %% [markdown]
# ### Defining the HDF5 Save Function
#


# %%
def get_datetime_str():
    now = datetime.datetime.now()
    now_str = now.strftime("%Y-%m-%d %H:%M:%S")
    return now_str


# %%
# creating the HDF5 save file

filename = "scraping_data.h5"
today_str = datetime.datetime.now().strftime("%Y-%m-%d")
now_str = get_datetime_str()

if os.path.isfile(filename):
    print("file already exists")

else:
    print("creating a new file")
    f = h5py.File(filename, "w")

    # Create groups
    f.create_group("immowelt")
    f.create_group("booking")
    f.create_group("boerse")

    # Create subgroup for immowelt group
    f["immowelt"].create_group(today_str)
    f["immowelt"][today_str].attrs["saved_datetime"] = now_str

    # Create subgroup for booking group
    f["booking"].create_group(today_str)
    f["booking"][today_str].attrs["saved_datetime"] = now_str

    # Create subgroup for boerse group
    f["boerse"].create_group(today_str)
    f["boerse"][today_str].attrs["saved_datetime"] = now_str

    # Close HDF5 file
    f.close()


# %%
# Creating the save function
def save_to_hdf5(filename, df, site, special_var):
    now_str = get_datetime_str()
    # saving immowelt data
    path = f"/{site}/{today_str}/df_{site}_{special_var}{today_str}/"

    f = h5py.File(filename, "a")
    if today_str not in f[site]:
        f[site].create_group(today_str)
        f[site][today_str].attrs["saved_datetime"] = now_str

    else:
        print(f"entry for {today_str} already exists. Data will be appended")

    f.close()

    hdf = pd.HDFStore(filename)

    # Store the dataframe in the HDFStore
    hdf.put(path, df, format="table")
    print(f"the data has been saved to {path}")
    # Close the HDFStore and HDF5 file
    hdf.close()


# %% [markdown]
# ### Scrapping ImmoWelt

# %%
# imo
url = "https://www.immowelt.de/liste/muenchen/wohnungen/mieten?d=true&sd=DESC&sf=RELEVANCE&sp="
select_statement = "div.Pagination-190de span"
site_type = "immowelt"
title = " "


# %%
scrape(url, select_statement, site_type, title)

# %%
# retrieving the fact section of the available renting objects in munich
munich = combined_soup.find_all("div", class_="FactsSection-52a7d")


# %%
# creating a dataframe with the core information
col1 = []
col2 = []
col3 = []
col4 = []

for offer in munich:
    col1.append(offer.text.split()[0].replace(".", "").split(",")[0])
    col2.append(offer.text.split()[1].replace("€", ""))
    col3.append(offer.text.split()[2].replace("m²", ""))
    result = re.search(r"!?location(.+?)(check|$)", offer.text)
    col4.append(result[1])


df = pd.DataFrame({"Rent": col1, "SQM": col2, "No. rooms": col3, "Area": col4})
df["Rent"] = pd.to_numeric(df["Rent"], errors="coerce")
df["SQM"] = pd.to_numeric(df["SQM"], errors="coerce")
df["No. rooms"] = pd.to_numeric(df["No. rooms"], errors="coerce")
df.dropna(inplace=True)
df.reset_index(inplace=True, drop=True)


# %%
# grouping
df_rooms = df.select_dtypes(include=["float", "int"])
df_rooms = df_rooms.groupby("No. rooms").mean().reset_index()


# %%
save_to_hdf5(filename, df, site_type, "")
save_to_hdf5(filename, df_rooms, site_type, "rooms")

# %% [markdown]
# ### Scrapping Booking.com

# %%
# booking
url = "https://www.booking.com/searchresults.html?label=gen173nr-1FCAEoggI46AdIM1gEaI4CiAEBmAExuAEYyAEP2AEB6AEB-AECiAIBqAIEuAKAteiiBsACAdICJDJmODU2ZGQwLTZjMzgtNGU4Yi05N2JiLTVmMTVmNTBiNWI5ZdgCBeACAQ&aid=304142&ss=Munich&efdco=1&lang=en-us&sb=1&src_elem=sb&src=index&dest_id=-1829149&dest_type=city&ac_position=0&ac_click_type=b&ac_langcode=en&ac_suggestion_list_length=5&search_selected=true&search_pageview_id=cc0f46c0a1a700b2&ac_meta=GhBjYzBmNDZjMGExYTcwMGIyIAAoATICZW46Bk11bmljaEAASgBQAA%3D%3D&checkin=2023-06-01&checkout=2023-06-07&group_adults=2&no_rooms=1&group_children=0&sb_travel_purpose=leisure&offset=1"
select_statement = "li.f32a99c8d1"
site_type = "booking"
title = " "

# %%
scrape(url, select_statement, site_type, title)

# %%
div_elements = combined_soup.find_all("div", class_="d20f4628d0")

# %%
# creating a dataframe with the core information
col1 = []
col2 = []
col3 = []
col4 = []

for div in div_elements:
    col1.append(
        div.find("div", {"data-testid": "title", "class": "fcab3ed991 a23c043802"}).text
    )
    span = div.find("span", {"class": "c5888af24f e729ed5ab6", "aria-hidden": "true"})
    if span is not None:
        col3.append(int(span.text.replace(",", "").replace("€", "").replace(" ", "")))
        col2.append(
            int(
                div.find("span", {"data-testid": "price-and-discounted-price"})
                .text.replace(",", "")
                .replace("€", "")
                .replace(" ", "")
            )
        )
    else:
        col2.append(-1)
        col3.append(
            int(
                div.find("span", {"data-testid": "price-and-discounted-price"})
                .text.replace(",", "")
                .replace("€", "")
                .replace(" ", "")
            )
        )

df_hotel = pd.DataFrame({"Name": col1, "Discounted": col2, "Undiscounted": col3})


# %%
save_to_hdf5(filename, df_hotel, site_type, "")

# %% [markdown]
# ### Scrapping Yahoo Finance
# for the five biggest German real estate companies that are stock companies.

# %%
# five biggest according to
# https://www.savills.de/research_articles/260049/291332-0

# %%
# # creating a dictionary with the websites and the necessary titles.
# # Titles are need so that the functions knows its on the right site.
# site_type = "yahoo_finance"
# finance_url = {
#     "vonovia": {
#         "url": "https://de.finance.yahoo.com/quote/VNA.DE?p=VNA.DE&.tsrc=fin-srch",
#         "select_statement": "",
#         "site_type": "yahoo",
#         "title": "Vonovia SE (VNA.DE)",
#     },
#     "deutsche_wohnen": {
#         "url": "https://de.finance.yahoo.com/quote/DWNI.DE?p=DWNI.DE&.tsrc=fin-srch",
#         "select_statement": "",
#         "site_type": "yahoo",
#         "title": "Deutsche Wohnen SE (DWNI.DE)",
#     },
#     "saga": {
#         "url": "https://de.finance.yahoo.com/quote/SAGA?p=SAGA&.tsrc=fin-srch",
#         "select_statement": "",
#         "site_type": "yahoo",
#         "title": "Sagaliam Acquisition Corp. (SAGA)",
#     },
#     "leg": {
#         "url": "https://de.finance.yahoo.com/quote/LEG.DE?p=LEG.DE&.tsrc=fin-srch",
#         "select_statement": "",
#         "site_type": "yahoo",
#         "title": "LEG Immobilien SE (LEG.DE)",
#     },
#     "grand_city": {
#         "url": "https://de.finance.yahoo.com/quote/GYC.DE?p=GYC.DE&.tsrc=fin-srch",
#         "select_statement": "",
#         "site_type": "yahoo",
#         "title": "Grand City Properties S.A. (GYC.DE)",
#     },
# }

# %%
# col1 = []
# col2 = []


# # Scrapping the different stocks from the dictionary
# for key, vonovia_data in finance_url.items():
#     soup = scrape(
#         vonovia_data["url"],
#         vonovia_data["select_statement"],
#         vonovia_data["site_type"],
#         vonovia_data["title"],
#     )
#     div_elements_yahoo = soup.find("div", class_="D(ib) Va(m) Maw(65%) Ov(h)")

#     col1.append(key)
#     # in some instances there are multiple points in the price,
#     # thus everything after the first point will be deleted
#     parts = (
#         re.sub(r"[+\-].*", "", div_elements_yahoo.text.split()[0])
#         .replace(",", ".")
#         .split(".")
#     )
#     string_stock_price = ".".join(parts[:2])
#     col2.append(float(string_stock_price))

# df_stocks = pd.DataFrame({"Name": col1, "Price": col2})


# %% [markdown]
# ### Scrapping Boerse.de
# for the four biggest German real estate companies that are stock companies.

# %%
# creating a dictionary with the websites and the necessary titles.
# titles are needed so that the function knows it's on the right site.
site_type = "boerse"

finance_url = {
    "vonovia": {
        "url": "https://www.boerse.de/aktien/Vonovia-Aktie/DE000A1ML7J1",
        "select_statement": "",
        "site_type": "boerse",
        "title": "",
    },
    "deutsche_wohnen": {
        "url": "https://www.boerse.de/aktien/Deutsche-Wohnen-Aktie/DE000A0HN5C6",
        "select_statement": "",
        "site_type": "boerse",
        "title": "",
    },
    "leg": {
        "url": "https://www.boerse.de/aktien/LEG-Immobilien-Aktie/DE000LEG1110",
        "select_statement": "",
        "site_type": "boerse",
        "title": "",
    },
    "grand_city": {
        "url": "https://www.boerse.de/aktien/Grand-City-Properties-Aktie/LU0775917882",
        "select_statement": "",
        "site_type": "boerse",
        "title": "",
    },
}

# %%
col1 = []
col2 = []


# Scrapping the different stocks from the dictionary
for key, data in finance_url.items():
    soup = scrape(
        data["url"],
        data["select_statement"],
        data["site_type"],
        data["title"],
    )

    div_elements = soup.find_all("div", class_="col-sm-12 col-xs-12")

    # Check if the 'div' element contains a 'span' element with the class 'BW_PUSH'
    # this is necessary because the col-sm-12 col-xs-12 class is used more often, yet the combination is unique.
    for div in div_elements:
        if div.find("span", class_="BW_PUSH"):
            share_price = div.find("span", class_="BW_PUSH").text
            share_price = (
                share_price.replace("\n", "").replace("EUR", "").replace(",", ".")
            )

    col1.append(key)
    col2.append(float(share_price))

df_stocks = pd.DataFrame({"Name": col1, "Price": col2})

# %%
save_to_hdf5(filename, df_stocks, site_type, "")

# %%
hdf = pd.HDFStore(filename, mode="r")
if len(hdf.keys()) == 4:
    print("everything saved")
else:
    print("Houston, we got a problem")
hdf.close()
