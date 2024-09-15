from univ_tools import univ_client, filter
from xivjson import * #item_lookup, recipe_dict

TESTING="TESTING"

def make_options_list():
    return [x for x in reverse_item_lookup.keys() 
            if int(reverse_item_lookup[x]) in reverse_recipe_lookup.keys()]

def full_recipe_tree(search_term, univ_client, quantity=1):
    search_term=search_term#.lower()
    itemID = reverse_item_lookup[search_term]
    if not int(itemID) in reverse_recipe_lookup:
        return None
    return tree_container(itemID, univ_client)
    # return item_block(itemID, univ_client, quantity=quantity, target=True)

class tree_container:    
    #streamlit tree component uses lists of node keys for things
    #this container makes it easier to interface with that 

    def __init__(self, item_id, univ_client, quantity=1):
        self.node_count = 0
        self.node_mapping = {}
        self.univ_client = univ_client#()
        self.root = item_block(item_id, univ_client, self, quantity=quantity, target=True)#recipe_tree#tree_node(self, item_id, quantity)
        self.quantity=quantity

    def make_node_id(self, node):
        key = f"node_{str(self.node_count)}"
        self.node_mapping[key] = node
        self.node_count += 1
        return key

    def price_query(self, item_id): 
        return self.univ_client.price_query(item_id)
        pass

    def get_serialized_nodes(self):
        return self.to_dict()
    
    def to_dict(self):
        retval = self.root.to_dict()
        def affix_key(node):
            if node["value"] is None:
                node["value"] = self.make_node_id(node)
            if "children" in node and node["children"] is not None:
                for child in node["children"]:
                    if child is not None:
                        affix_key(child)
        affix_key(retval)
        return retval
            

# class recipe_tree_node: #just the reci data
#     def __init__(self, item_id, quantity=1):
#         self.item_id = item_id
#         self.item_name = item_lookup[str(item_id)]
#         self.quantity = quantity
#         reci_dict = recipe_dict(item_id)
#         if reci_dict is not None:
#             self.prod_yield = reci_dict["yields"]
#             self.ingredients = [recipe_tree_node(item["id"], item["amount"]) for item in ingredients]
#         else: 
#             self.prod_yield = 1
#             self.ingredients = []
#         self.all_unique_items = {item_id:True}
#         for ingredient in self.ingredients:
#             for item_id in ingredient.all_unique_items.keys():
#                 self.all_unique_items[item_id]:True


# class recipe_tree_container: #mats counter
#     def __init__(self, recipe_tree):
#         self.recipe_tree = recipe_tree
#         self.items = {item_id:0 for item_id in recipe_tree.all_unique_items.keys()}

#     def intertree(self):
#         pass

def text_block(*args, sep=" "):
        return (
            {
            "label":"".join([str(x)+sep for x in args]),
            "value":None,
            "showCheckbox":False,
            }
        )

def click_block(text, default=True):
        return (
            {
            "label":text,
            "value":None,
            "showCheckbox":True,
            }
        )

class item_block:
    def __init__(self, 
                item_id,
                univ_client,
                tree_container,
                target=False,
                quantity=1):
        self.tree_container=tree_container
        self.item_id = item_id
        self.reci_dict = recipe_dict(item_id)
        self.yields = self.reci_dict["yields"] if self.reci_dict is not None else 1
        job = None #self.reci_dict["job"]
        self.ingredients = crafting_block(item_id, self.reci_dict["ingredients"], univ_client, 
                                          self.tree_container, job=job, yields=self.yields) if self.reci_dict is not None else None
        self.listings = listings_block(item_id, univ_client, self.tree_container)
        self.quantity = quantity
        self.target = target

    def to_dict(self):
        num_hq=TESTING
        num_nq=TESTING
        child_block = [text_block(f"(expected: {num_hq} HQ / {num_nq} NQ | required: {self.quantity})"),
                        click_block("Use currently owned inventory", False),
                        self.listings.to_dict()
                        ]
        if self.ingredients is not None:
            child_block.append(self.ingredients.to_dict())
        return (
            {
            "label":f'{item_lookup[str(self.item_id)]["en"]}{"" if self.target else f" (required per craft: {self.quantity})"}',
            "value":self.tree_container.make_node_id(self),
            "showCheckbox":False,
            "children":child_block
            }
        )


class crafting_block:
    def __init__(self, 
                item_id,
                ingredients,
                univ_client,
                tree_container,
                job=None,
                quantity=None,
                yields=1):
        self.tree_container=tree_container
        self.item_id = item_id
        self.quantity = quantity
        self.yields = yields
        self.ingredients = [item_block(item["id"], univ_client, self.tree_container, quantity=item["amount"]) for item in ingredients]
        # self.job = job
        print(self.ingredients)

    def to_dict(self):
        num_crafted = TESTING
        child_block = [text_block(f"(total expected: {num_crafted} | {self.yields} per craft"),# | {self.job})"),
                        click_block("Use currently owned inventory", False),
                        ]
        child_block.extend(item.to_dict() for item in self.ingredients)
                        
        return (
            {
            "label":f'Crafting (required per craft: {self.quantity})',
            "value":self.tree_container.make_node_id(self),
            "showCheckbox":False,
            "children":child_block
            }
        )

class listings_block:
    def __init__(self, item_id, univ_client, 
                 tree_container,
                 pre_filter = None, #filter before caching
                 post_filter = None #filter after caching
                 ):
        self.tree_container=tree_container
        self.univ_client = univ_client
        self.item_id = item_id
        self._listings = []
        self.pre_filter = pre_filter
        self.post_filter = post_filter

    def get_listings(self):
        self._listings = self.univ_client.price_query(self.item_id, self.tree_container, pre_filter=self.pre_filter)
        # self._listings = self.post_filter(self._listings)
        return self._listings

    def to_dict(self):
        listings = self.get_listings()
        child_block = [click_block("Include NQ")]
        child_block.extend([single_listing_block(self.item_id,x,self.tree_container).to_dict() for x in listings])
        return (
            {
            "label":"Listings",
            "value":self.tree_container.make_node_id(self),
            "showCheckbox":False,
            "children":child_block
            }
        )


class single_listing_block:
    def __init__(self, item_id, listing, tree_container):
        self.item_id = item_id
        self.tree_container = tree_container
        self.listing = listing
    
    def to_dict(self):
        return {
            "label":self._make_label(),
            "value":self.tree_container.make_node_id(self),
            "showCheckbox":True
        }

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

