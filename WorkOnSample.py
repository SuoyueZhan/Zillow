from zillow_price import get_house_info
from selenium import webdriver
from time import sleep
import json
import MySQLdb


def read_web_chrome(url, saveToJson="Page1"):
    """find the first page of given url, defined by location/zip"""
    # obtain first page of zillow results
    print("Trying to reach: " + url)
    driver = webdriver.Chrome()
    driver.get(url)
    src = driver.page_source
    print("Page Source Obtained Successfully")

    # write source into json
    fileName = saveToJson+".json"
    with open(fileName, "w") as outfile:
        json.dump(src, outfile)

    # release driver
    driver.quit()

    # read in as string
    with open(fileName, "r") as infile:
        src = json.load(infile)

    return src


def find_total_pages(src):
    """find total number of pages for zillow"""
    totalPagesInd = src.find("totalPage")
    totalPages = int(src[totalPagesInd + 12:totalPagesInd + 13])
    return totalPages


def find_all_houses(src):
    """parse house information and write into json"""

    houses = src.split('"statusText"')
    for rawStr in houses[1:]:
        str = rawStr[:400]
        house = get_house_info(str)
        if "new construction" in rawStr.lower():
            house["new construction"] = True

        with open("houses.json", "a") as houseJson:
            json.dump(house, houseJson, indent=2)


def find_all_houses_list(src, houseList):
    """parse house information and write into json"""

    houses = src.split('"statusText"')
    for rawStr in houses[1:]:
        str = rawStr[:400]
        house = get_house_info(str)

        # Check if new construction
        if "new construction" in rawStr.lower():
            house["new construction"] = True

        # append copy of current house to List
        houseList.append(house.copy())

    # write list into the file
    with open("houses.json", "w") as houseJson:
        json.dump(houseList, houseJson, indent=2)
    return houseList


def construct_extra_page_urls(prim_url,totalPages):
    """construct corresponding urls for zillow based on page numbers found"""
    extra_url = []
    if totalPages > 1:
        for pageNum in range(2, totalPages+1):
            new_url = []
            append = '/' + str(pageNum) + '_p'
            new_url = prim_url + append
            extra_url.append(new_url)
    else:
        print("No Extra Page Detected")

    return extra_url


def read_extra_pages(extra_Url, houseList):
    """get other pages and find house information, append to the houses.jason"""
    for url in extra_Url:
        # sleepTime = randrange(3, 5)
        print("Waiting for 60s to avoid anti-robot check from zillow...")
        sleep(30)
        print("30s Left")
        sleep(30)
        fileNum = url[-3]
        fileName = "page" + fileNum
        src = read_web_chrome(url, fileName)
        print("Parsing information for page " + str(fileNum) + "...")
        houseList = find_all_houses_list(src, houseList)
        print("Page " + str(fileNum) + " parsing finished.")
        # sleepTime = randrange(3, 5)
        # sleep(sleepTime)
    return houseList


def get_location_from_db_uszips(zip):
    """find corresponding location string for zillow based on given zip, for zip-wise house search"""
    # local database conn
    db = MySQLdb.connect(
        host="localhost",
        user="root",
        password="40434043aA_",
        database="uszips"
    )

    # print(db)
    db.query("""select city, state_id, zip from uszipcode where zip = """ + str(zip))
    r = db.store_result()
    location = r.fetch_row()
    # print(location[0])
    location = location[0][0].lower() + "-" + location[0][1].lower() + "-" + str(location[0][2])
    return location

##############################################
# Main Entry of Zillow Scraper
##############################################


zipcode = input("Please specify the zipcode you are interested in for searching\n")

# get location string based on us zipcode database
location = get_location_from_db_uszips(zipcode)

# construct the url matching the input zipcode
prim_url = 'https://www.zillow.com/' + location

src = read_web_chrome(prim_url, "Page1")

# find total number of pages for specified zipcode search
print("Get the number of pages for search results...")
totalPages = find_total_pages(src)
print("There are " + str(totalPages) + " pages of results within the area: " + zipcode)

# find all house information for first page
print("Parsing information for page 1...")
houseListAll = []
houseListAll = find_all_houses_list(src, houseListAll)
print("Page 1 parsing finished.")
# construct new page urls
extraUrl = construct_extra_page_urls(prim_url, totalPages)

# find all house information on following pages, 1 min per page to avoid robot check
if extraUrl:
    houseListAll = read_extra_pages(extraUrl, houseListAll)
    with open("houses.json", "w") as houseJsonEx:
        json.dump(houseListAll, houseJsonEx, indent=2)

print(len(houseListAll))

# ################################
# # Testing Block Starts From Here
#
#
# with open("Page1.json", "r") as file:
#     src = json.load(file)
#
#
# listOfHouse = find_all_houses_list(src)
# print(listOfHouse[15])



