import streamlit as st
from streamlit_tree_select import tree_select
#home server -dropdown? or home region
from univ_tools import get_current_item

@st.cache_resource
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
    
    return item_lookup, reverse_item_lookup, recipe_lookup, reverse_recipe_lookup

item_lookup, reverse_item_lookup, recipe_lookup, reverse_recipe_lookup = load_resources()


#separate out logic later
def _recipe_dict(itemID):
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
        recurs = _recipe_dict(x["id"])
        if recurs is not None:
            if "yields" in recurs:
                ingredient["yields"] = recurs["yields"]
            ingredient["ingredients"] = recurs["ingredients"]
        ingredients.append(ingredient)
    retval["ingredients"] = ingredients
    return retval

def full_recipe_dict(search_term):
    search_term=search_term#.lower()
    itemID = reverse_item_lookup[search_term]
    if not int(itemID) in reverse_recipe_lookup:
        return None
    return _recipe_dict(itemID)


options_list = [x for x in reverse_item_lookup.keys() 
                if int(reverse_item_lookup[x]) in reverse_recipe_lookup.keys()]

# volume = st.radio("Production Volume",
#                     ["One",
#                      "Crafts LCD",
#                      "Amortized"])
# hqnq = st.toggle("Allow partial NQ results")
# nq = st.toggle("Ignore HQ/NQ Completely")
# count_crystals = st.toggle("Ignore Crystals")
# max_hops = st.slider("Max DC Hops", min_value=0, max_value=5, value=0, step=1)
# precraft_hq = st.slider("Required HQ Precrafts", min_value=0, max_value=5, value=0, step=1)


def counter():
    count = 0
    while True:
        yield str(count)
        count += 1

def prettify_tree(reci_dict, value_counter):
    retval = {}
    retval["label"] = reci_dict["text"]
    if "id" in reci_dict:
        prices = get_current_item(reci_dict["id"])
        retval["label"] += f" (HQ: {prices[0]}, NQ: {prices[1]})"
    retval["value"] = next(value_counter)
    # retval["showCheckbox"] = "
    if retval["value"] != "0":
        retval["label"] = retval["label"]+" x "+str(reci_dict["amount"])
    if "ingredients" in reci_dict:
        retval["children"] = [prettify_tree(x,value_counter) for x in reci_dict["ingredients"]]
    return retval



# button = st.button("Barse")
with st.form(key='my_form'):
    item = st.selectbox("Search for Item", options_list, None)
    if item is not None:

        reci = full_recipe_dict(item)
        ctr = counter()
        nodes = [prettify_tree(reci, ctr)]
        # print(nodes)
        
        return_select = tree_select(nodes, 
                                    # show_expand_all=True, #hardcode later
                                    checked = [0],
                                    expanded = [x for x in range(int(next(ctr)))], #gather all beforehand
                                    expand_disabled=False,
                                    no_cascade=True, 
                                    )
    submit_button = st.form_submit_button(label='Submit')

