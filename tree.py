from univ_tools import univ_client#, recipe_dict

#clean this
def load_resources():
    import json

    with open('items.json', 'r') as file:
        item_lookup = json.load(file)

    #reverse_item_lookup = {item_lookup[x]["en"].lower():x for x in item_lookup.keys()}
    reverse_item_lookup = {item_lookup[x]["en"]:x for x in item_lookup.keys()}

    with open('recipes-ingredient-lookup.json', 'r') as file:
        recipe_lookup = json.load(file)

    reverse_recipe_lookup = {recipe_lookup["recipes"][x]["itemId"]:
                         recipe_lookup["recipes"][x]
                         for x in recipe_lookup["recipes"].keys()}
    
    return item_lookup, reverse_item_lookup, recipe_lookup, reverse_recipe_lookup, #univ_client()

item_lookup, reverse_item_lookup, recipe_lookup, reverse_recipe_lookup,  = load_resources()

class tree_container: 
    #streamlit tree component uses lists of node keys for things
    #this container makes it easier to interface with that 

    def __init__(self,item_id, univ_client):
        self.item_id = item_id
        self.node_count = 0
        self.node_mapping = {}
        self.univ_client = univ_client#()
        self.root = tree_node(self, item_id)
        

    def _make_label(self, caller):
        key = f"node_{str(self.node_count)}"
        self.node_mapping[key] = caller
        self.node_count += 1
        return key

    def _price_query(self, item_id): 
        return self.univ_client.price_query(item_id)
        pass

    # def __repr__():
    #     return [self.root]

class listing_node:
    def __init__(self, tree_container, listing, item):
        val = [
            ["Price: ","pricePerUnit"],
            ["Quantity: ","quantity"],
            ["World: ","worldName"],
            ["HQ: ","hq"],
            ["Total: ","total"]
            ]
        val = ["".join((a[0],str(listing[a[1]])," | ")) for a in val]
        val = "".join(val)
        self.label = val
        self.item = item
        self.value = tree_container._make_label(self)
    
    def to_dict(self):
        return {
            "label":self.label,
            "value":self.value,
            "showCheckbox":True,
            "item":self.item
        }
    
class tree_node: 
    def __init__(self, tree_container, item_id, quantity=1):
        self.item_id = item_id
        self.tree_container = tree_container
        reci_dict = recipe_dict(item_id)
        if reci_dict is not None:
            self.label = reci_dict["text"]
            self.prod_yield = reci_dict["yields"]
            self.ingredients = self._process_ingredients(reci_dict["ingredients"])
        else:
            self.label = item_lookup[str(item_id)]["en"]   
            self.ingredients = []
        self.quantity = quantity
        self.item = ""
        self.value = self.tree_container._make_label(self)
        
        self.checked = False
        self.listings = self._process_price_query(tree_container._price_query(item_id))
        # self.children = [
        #         {
        #         "label":self.label+"_listings",
        #         "value":"Listings",
        #         "showCheckbox":False,
        #         "children":self.listings
        #         },
        #         {
        #         "label":self.label+"_ingredients",
        #         "value":"Ingredients",
        #         "showCheckbox":False,
        #         "children":self.ingredients
        #         }
        #     ]
        #do we want to add children to container?


    def _process_ingredients(self,ingredients):
        # if len(ingredients) == 0:
        #     return []
        return [tree_node(self.tree_container, item["id"], item["amount"]) for item in ingredients]# if recipe_dict(item["id"]) is not None]

    def _process_price_query(self,results): 
        # try:
        #     print(results["listings"])
        # except:
        #     print(type(results), results)
        # def listing_node(listing):
            
        #     val = [
        #         ["Price: ","pricePerUnit"],
        #         ["Quantity: ","quantity"],
        #         ["World: ","worldName"],
        #         ["HQ: ","hq"],
        #         ["Total: ","total"]
        #         ]
        #     val = ["".join((a[0],str(listing[a[1]])," | ")) for a in val]
        #     val = "".join(val)
            
        #     retval = {
        #         "label":val,
        #         "showCheckbox":True,
        #     }
        #     retval["value"] = self.tree_container._make_label(retval)
        #     retval.label = val
        #     return retval
    
        return [listing_node(self.tree_container,listing,self.label) for listing in results]#["listings"]]


    def refresh():
        pass

    def _on_check():
        pass

    def _on_uncheck():
        pass

    # def serialize(self):
    #     serial_listings = [x.serialize() for x in self.listings]
    #     serial_ingredients = [x.serialize() for x in self.ingredients]
    #     self.children = [
    #             {
    #             "label":self.label+"_listings",
    #             "value":"Listings",
    #             "showCheckbox":False,
    #             "children":serial_listings
    #             },
    #             {
    #             "label":self.label+"_ingredients",
    #             "value":"Ingredients",
    #             "showCheckbox":False,
    #             "children":serial_ingredients
    #             }
            # ]
    def to_dict(self):
        if self.ingredients == []:
            return {
                "label":self.label,
                "value":self.value,
                "showCheckbox":True,
                "children":[x.to_dict() for x in self.listings]
            }
        self.ingredients = [x for x in self.ingredients]
        self.children = [x.to_dict() for x in self.listings]+[x.to_dict() for x in self.ingredients]
        return {
            "label":self.label,
            "value":self.value,
            "showCheckbox":True,
            "children":self.children
        }
        


#move later
def recipe_dict(itemID):
    retval = {"id":itemID, "text":item_lookup[str(itemID)]["en"]}
    if not int(itemID) in reverse_recipe_lookup:
        return None
    recipe = reverse_recipe_lookup [int(itemID)]
    if "yields" in recipe:
        retval["yields"] = recipe["yields"]
    ingredients = []
    for x in recipe["ingredients"]:
        ingredient = {}
        ingredient["id"] = x["id"]
        ingredient["text"] = item_lookup[str(x["id"])]["en"]
        ingredient["amount"] = x["amount"]
        recurs = recipe_dict(x["id"])
        if recurs is not None:
            if "yields" in recurs:
                ingredient["yields"] = recurs["yields"]
            ingredient["ingredients"] = recurs["ingredients"]
        ingredients.append(ingredient)
    retval["ingredients"] = ingredients
    return retval
