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

home_world =  { "id": 54, "name": "Faerie" }


def get_current_item(id):
    item_id = str(id) 
    worldDcRegion = "North-America"
    endpoint = f"https://universalis.app/api/v2/aggregated/{worldDcRegion}/{item_id}"
    response = requests.get(endpoint)
    print(endpoint)
    if response.status_code == 200:
    # Get the response content (usually JSON)
        data = response.json()
        print(data)
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


