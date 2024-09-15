import requests
import asyncio
import xivjson
import time
from xivjson import *

region_lookup = servers_lookup

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
        self.cache = {}
        self.recent = 0
        self.last_reset = time.time()
    #     self.queue = asyncio.Queue()
    #     self.mutex = False

    # async def enqueue(self, query):
    #     self.queue.put(query)
    #     self.queue_consumer()

    # async def queue_consumer(self):
    #     if self.mutex:
    #         return
    #     self.mutex = True
    #     try:
    #         while not self.queue.empty():
    #             pass
                
    #     except Exception as e:
    #         self.mutex = False
    #         raise e
        
    def raw_price_query(self, item_id):
        region = REGION_NA
        params = {
        'listings': 100,
        'entries': 0,
        'statsWithin': 99999,
        # 'entriesWithin': 77777
        }

        self.recent += 1
        if self.recent > 15 and (time.time()-self.last_reset) <= 1:
            time.sleep(1)
            self.recent = 0
            self.last_reset = time.time()
            
        response = requests.get(URL+f"{region}/{item_id}", params=params)
        if response.status_code == 200:
            return response.json()
        else:
            pass
            # print(response)
            #maybe reenque?

    def price_query(self, item_id, filter_args=None):
    
        if item_id in self.cache:
            results = self.cache[item_id]
        else:
            print("query sent ",item_id)
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
                if worlds_seen["worldID"] > LIMIT_PER_WORLD:
                    continue
            else:
                worlds_seen["worldID"] = 1

            
            dc_id = reverse_servers_lookup[listing["worldName"]]
            if dc_id in datacenters_seen:
                datacenters_seen[dc_id] += 1
                if datacenters_seen[dc_id] > LIMIT_PER_DC:
                    continue
            else:
                datacenters_seen[dc_id] = 1

            if len(retval) <= LISTINGS_PER_ITEM:
                retval.append(listing)
            else:
                break
        return retval

    @staticmethod
    def _reduce_results(results):
        return [{k:x[k] for k in keylist} for x in results]


