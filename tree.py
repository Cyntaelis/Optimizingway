from univ_tools import univ_client
from xivjson import * #item_lookup, recipe_dict

def make_options_list():
    return [x for x in reverse_item_lookup.keys() 
            if int(reverse_item_lookup[x]) in reverse_recipe_lookup.keys()]

def full_recipe_tree(search_term, univ_client, quantity=1):
    search_term=search_term#.lower()
    itemID = reverse_item_lookup[search_term]
    if not int(itemID) in reverse_recipe_lookup:
        return None
    return tree_container(itemID, univ_client, quantity)

class tree_container: 
    #streamlit tree component uses lists of node keys for things
    #this container makes it easier to interface with that 

    def __init__(self, item_id, univ_client, quantity=1):
        self.item_id = item_id
        self.node_count = 0
        self.node_mapping = {}
        self.univ_client = univ_client#()
        self.root = tree_node(self, item_id, quantity)
        self.quantity=quantity

    def make_node_id(self, caller):
        key = f"node_{str(self.node_count)}"
        self.node_mapping[key] = caller
        self.node_count += 1
        return key

    def price_query(self, item_id): 
        return self.univ_client.price_query(item_id)
        pass

    def get_serialized_nodes(self):
        return self.root.to_dict()
    
    def render_tree(self):
        pass

class abstract_node():

    def to_dict():
        pass 

    def refresh():
        pass

    def _on_check():
        pass

    def _on_uncheck():
        pass

class spacer_node(abstract_node):

    def __init__(self, 
                 tree_container, 
                 listings=None, 
                 ingredients=None,
                 item_id=None,
                 quantity=None):
        
        self.tree_container=tree_container
        self.value = tree_container.make_node_id(self)

        if listings is not None:
            self.item_id=item_id
            self.listings = self._process_price_query(listings)
            self.json = (
                {
                "label":"Listings",
                "value":self.value,
                "showCheckbox":False,
                "children":[x.to_dict() for x in self.listings]
                }
            )

        if ingredients is not None:
            self.quantity = quantity
            self.ingredients = self._process_ingredients(ingredients)
            self.json = (
                {
                "label":"Ingredients",
                "value":self.value,
                "showCheckbox":False,
                "children":[x.to_dict() for x in self.ingredients]
                }
            )

    def _process_ingredients(self, ingredients):
        # print(ingredients)
        return [tree_node(self.tree_container, item["id"], item["amount"]*self.quantity) for item in ingredients]

    def _process_price_query(self, results): 
        return [listing_node(self.tree_container, listing, self.item_id) for listing in results]

    def to_dict(self):
        return self.json

class listing_node(abstract_node):

    def __init__(self, tree_container, listing, item_id):
        self.tree_container=tree_container
        self.item_id = item_id
        self.value = self.tree_container.make_node_id(self)
        self.listing = listing
        self.label = self._make_label()

    def _make_label(self):
        val = [
            ["Price: ","pricePerUnit"],
            ["Quantity: ","quantity"],
            ["World: ","worldName"],
            ["HQ: ","hq"],
            ["Total: ","total"]
            ]
        val = ["".join((a[0],str(self.listing[a[1]])," | ")) for a in val]
        val = "".join(val)
        return val

    def to_dict(self):
        return {
            "label":self.label,
            "value":self.value,
            "showCheckbox":True
        }
    
class tree_node(abstract_node): 
    def __init__(self, tree_container, item_id, quantity=1):
        self.item_id = item_id
        self.tree_container = tree_container
        self.quantity = quantity
        self.value = self.tree_container.make_node_id(self)
        self.label = f'{item_lookup[str(item_id)]["en"]} (required: {quantity})' #[required: x (x per craft) | prod yield: x | selected: x]

        reci_dict = recipe_dict(item_id)
        if reci_dict is not None:
            self.prod_yield = reci_dict["yields"]
            self.ingredients = self._process_ingredients(reci_dict["ingredients"])
        else: 
            self.ingredients = []

        self.checked = False
        listings = self.tree_container.price_query(item_id)
        self.listings = self._process_price_query(listings)

    def _process_ingredients(self,ingredients):
        return spacer_node(self.tree_container, ingredients=ingredients, quantity=self.quantity)

    def _process_price_query(self,listings): 
        return spacer_node(self.tree_container, listings=listings, item_id=self.item_id)
    
    def to_dict(self):
        # print("\nlistings",self.listings.to_dict(),"\n")
        retval = {
                "label":self.label,
                "value":self.value,
                "showCheckbox":False, #True, revert when functionality added
                "children":[self.listings.to_dict()]
            }
        
        if self.ingredients != []:
            # print("\ningredients",self.ingredients.to_dict(),"\n")
            retval["children"]=[self.listings.to_dict(),self.ingredients.to_dict()]
        
        # print(retval["children"])
        return retval

