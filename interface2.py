import streamlit as st
from streamlit_tree_select import tree_select
#home server -dropdown? or home region
from univ_tools import univ_client
from tree import tree_container
import xivjson
from xivjson import *

@st.cache_resource
def get_univ_client():
    return univ_client()
univ_client = get_univ_client()

# def load_resources():
#     import json

#     with open('items.json', 'r') as file:
#         item_lookup = json.load(file)

#     #reverse_item_lookup = {item_lookup[x]["en"].lower():x for x in item_lookup.keys()}
#     reverse_item_lookup = {item_lookup[x]["en"]:x for x in item_lookup.keys()}

#     with open('recipes-ingredient-lookup.json', 'r') as file:
#         recipe_lookup = json.load(file)

#     reverse_recipe_lookup = {recipe_lookup["recipes"][x]["itemId"]:
#                          recipe_lookup["recipes"][x]
#                          for x in recipe_lookup["recipes"].keys()}
    
#     return item_lookup, reverse_item_lookup, recipe_lookup, reverse_recipe_lookup, 
# univ_client = get_univ_client()

# item_lookup, reverse_item_lookup, recipe_lookup, reverse_recipe_lookup, univ_client = load_resources()

options_list = [x for x in reverse_item_lookup.keys() 
                if int(reverse_item_lookup[x]) in reverse_recipe_lookup.keys()]

def full_recipe_dict(search_term, quantity=1):
    search_term=search_term#.lower()
    itemID = reverse_item_lookup[search_term]
    if not int(itemID) in reverse_recipe_lookup:
        return None
    return tree_container(itemID, univ_client, quantity)

shopping_list=""
totals = 0


with st.form(key="settings"):
    item = st.selectbox("Home Server", ["Faerie","Sargatanas"], None)
    show_region = st.checkbox("Show cross DC results", True)
    show_home = st.checkbox("Always show some results from home server", True)
    submit_button = st.form_submit_button(label='Save Settings')

with st.form(key='tree_opti'):
    item = st.selectbox("Search for Item", options_list, None)
    quantity = st.number_input("Desired Quantity", 1, 99, step=1)
    hq = st.checkbox("Allow NQ")
    submit_button = st.form_submit_button(label='Optimize')
    if item is not None:

        reci = full_recipe_dict(item, quantity)
        # ctr = counter()
        nodes = reci.get_serialized_nodes()
        # print(nodes)
        # print(nodes)


if item is not None:        
    return_select = tree_select([nodes], 
                                checked = [0],
                                expanded = list(reci.node_mapping.keys()), #gather all beforehand
                                expand_disabled=False,
                                no_cascade=True, 
                                )
    print("update")
    # try:
    if len(return_select["checked"]) > 0 and return_select["checked"] != [0]:
        en = "en" #fix later
        shopping_list = "".join([f"{(item_lookup[str(reci.node_mapping[x].item_id)])[en]} \n -{reci.node_mapping[x].label}\n" for x in return_select["checked"]])
        print(return_select["checked"])  
    # except:
        # print(return_select["checked"])       
    

with st.sidebar:
    st.text_area(label=" ", value=shopping_list, height = 600)
    st.text_area(label=" ", value=totals, height = 100)

# #move later
# def recipe_dict(itemID):
#     retval = {"id":itemID, "text":item_lookup[str(itemID)]["en"]}
#     if not int(itemID) in reverse_recipe_lookup:
#         return None
#     recipe = reverse_recipe_lookup [int(itemID)]
#     if "yields" in recipe:
#         retval["yields"] = recipe["yields"]
#     ingredients = []
#     for x in recipe["ingredients"]:
#         ingredient = {}
#         ingredient["id"] = x["id"]
#         ingredient["text"] = item_lookup[str(x["id"])]["en"]
#         ingredient["amount"] = x["amount"]
#         recurs = _recipe_dict(x["id"])
#         if recurs is not None:
#             if "yields" in recurs:
#                 ingredient["yields"] = recurs["yields"]
#             ingredient["ingredients"] = recurs["ingredients"]
#         ingredients.append(ingredient)
#     retval["ingredients"] = ingredients
#     return retval

