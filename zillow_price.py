import re
import json

# define zillow house
patterns = {
    "status": ':',
    "price": '"unformattedPrice":',
    "addressStreet": '"addressStreet":',
    "addressCity": '"addressCity":',
    "addressState": '"addressState":',
    "zipcode": '"addressZipcode":',
    "beds": '"beds":',
    "baths": '"baths":',
    "area": '"area":'
}

house = {
    "status": '',
    "price": '',
    "addressStreet": '',
    "addressCity": '',
    "addressState": '',
    "zipcode": '',
    "beds": '',
    "baths": '',
    "area": '',
    "new construction": False
}


def get_house_info(str):
    itemSeparateComma = [m.start() for m in re.finditer(",", str)]
    for keys in patterns:
        startInd = str.find(patterns[keys]) + len(patterns[keys])
        endInd = min(value for value in itemSeparateComma if value > str.find(patterns[keys]))
        itemText = str[startInd:endInd]
        house[keys] = itemText

    return house


def find_info(src, infoStr):
    """find out the specified information from zillow, including address, prices, number of bath, number of bed, area"""

    if infoStr.lower() in patterns.keys():
        firstPattern = patterns[infoStr.lower()][0]
        secondPattern = patterns[infoStr.lower()][1]
        maxDigit = patterns["max" + infoStr.title() + "Digits"]
    else:
        print("Requested Info not supported yet :(")
        return None

    addressIndPrim = [m.start() for m in re.finditer(firstPattern, src)]

    address = []

    for ind in addressIndPrim:
        startInd = ind + len(firstPattern)
        endInd = ind + maxDigit + len(firstPattern)
        rawAddress = src[startInd:endInd]
        separateInd = rawAddress.find(secondPattern)
        actualAddress = rawAddress[:separateInd]
        address.append(actualAddress)

    return address


with open("sample.json", "r") as file:
    src = json.load(file)

# totalPagesInd = src.find("totalPage")
#
# iAddress = 0
# total_pages = src[totalPagesInd+12:totalPagesInd+14]
