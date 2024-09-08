import requests

available_dcs = [
    {
        "name": "Aether",
        "region": "North-America",
        "worlds": [ 40, 54, 57, 63, 65, 73, 79, 99 ] 
    },
    {
        "name": "Crystal",
        "region": "North-America",
        "worlds": [ 34, 37, 41, 62, 74, 75, 81, 91 ]
    },
    {
        "name": "Primal",
        "region": "North-America",
        "worlds": [ 35, 53, 55, 64, 77, 78, 93, 95 ]
    },
    {
        "name": "Dynamis",
        "region": "North-America",
        "worlds": [ 404, 405, 406, 407, 408, 409, 410, 411 ]
    },
    { 
        "name": "Materia", 
        "region": "Oceania", 
        "worlds": [ 21, 22, 86, 87, 88 ] 
    },
]

region_lookup = {y:x["name"] for x in available_dcs for y in x["worlds"]}

REGION_NA = "North-America"
home_world =  { "id": 54, "name": "Faerie" }
URL = "https://universalis.app/api/v2/"
LIMIT_PER_WORLD = 5
LIMIT_PER_DC = 7
LISTINGS_PER_ITEM = 15
keylist = keylist = ['lastReviewTime', 
           'pricePerUnit', 
           'quantity', 
           'worldName', 
           'worldID', 
           'hq',
           'total']

class univ_client:

    def __init__(self):
        self.queue = None
        self.cache = {}

    def raw_price_query(self, item_id):
        region = REGION_NA
        params = {
        'listings': 100,
        'entries': 0,
        'statsWithin': 99999,
        # 'entriesWithin': 77777
        }
        response = requests.get(URL+f"{region}/{item_id}", params=params)
        if response.status_code == 200:
            return response.json()
        else:
            print(response)
            #maybe reenque?

    def price_query(self, item_id):
        
        if item_id in self.cache:
            results = self.cache[item_id]
        else:
            print("query sent")
            results = self.raw_price_query(item_id)
            if results is not None:
                self.cache[item_id] = results    
        filtered_results = self._filter_price_query(results)
        return self._reduce_results(filtered_results)

    @staticmethod
    def _filter_price_query(results): 
        # print(results)
        listings = sorted(results["listings"], key=(lambda x:int(x["pricePerUnit"])) ) 
        retval = []
        worlds_seen = {}
        datacenters_seen = {}
        for listing in listings:
            if listing["onMannequin"]:
                continue
            if listing["worldID"] in worlds_seen:
                worlds_seen["worldID"] += 1
                if worlds_seen["worldID"] >= LIMIT_PER_WORLD:
                    continue
            else:
                worlds_seen["worldID"] = 1
            dc_id = region_lookup[listing["worldID"]]
            if dc_id in datacenters_seen:
                datacenters_seen[dc_id] += 1
                if datacenters_seen[dc_id] >= LIMIT_PER_DC:
                    continue
            else:
                datacenters_seen[dc_id] = 1
            if len(retval) <= LISTINGS_PER_ITEM:
                retval.append(listing)
        return retval

    @staticmethod
    def _reduce_results(results):
        return [{k:x[k] for k in keylist} for x in results]

"""
"worldUploadTimes"
"recentHistory": [
    {
      "hq": false,
      "pricePerUnit": 1630,
      "quantity": 8,
      "timestamp": 1725797049,
      "onMannequin": false,
      "worldName": "Halicarnassus",
      "worldID": 406,
      "buyerName": "Yukine Kuchiki",
      "total": 13040
    },

"listings": [
    {
      "lastReviewTime": 0,
      "pricePerUnit": 830,
      "quantity": 6,
      "stainID": 0,
      "worldName": "Coeurl",
      "worldID": 74,
      "creatorName": "",
      "creatorID": null,
      "hq": false,
      "isCrafted": false,
      "listingID": "5207287793992822",
      "materia": [],
      "onMannequin": false,
      "retainerCity": 14,
      "retainerID": "33777097241626681",
      "retainerName": "The-bargain-bun",
      "sellerID": null,
      "total": 4980,
      "tax": 249
    },
"""

# Send the GET request with additional query parameters
# response = requests.get(url, params=params)



def get_current_item(id):
    item_id = str(id) 
    worldDcRegion = "North-America"
    endpoint = f"https://universalis.app/api/v2/aggregated/{worldDcRegion}/{item_id}"
    response = requests.get(endpoint)
    if response.status_code == 200:
    # Get the response content (usually JSON)
        data = response.json()
        # return data
    else:
        print(f"Request failed with status code: {response.status_code}")
        return
    hq="-"
    nq="-"

    if "hq" in data["results"][0] and "region" in data["results"][0]["hq"]["averageSalePrice"]:
        hq = data["results"][0]["hq"]["averageSalePrice"]["region"]["price"]
        hq = str(round(int(hq)))

    if "nq" in data["results"][0] and "region" in data["results"][0]["nq"]["averageSalePrice"]:
        nq = data["results"][0]["nq"]["averageSalePrice"]["region"]["price"]
        nq = str(round(int(nq)))
    #'averageSalePrice': {'region': {'price':
    return hq,nq


def get_current( 
        item_id_list: str, 
        world_dc_region: str = "North-America" # 
        ) -> dict: #json
    """
    #uses cached aggregates over 4 days, switch to CurrentlyShown later as we want current individual listings
    """
    #todo check that IDs are valid
    if isinstance(item_id_list, list):
        item_id_list_str = "".join(item_id_list)
    else: 
        item_id_list_str = item_id_list
    pass

