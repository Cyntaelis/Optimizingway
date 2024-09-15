import streamlit as st

from streamlit_tree_select import tree_select
#home server -dropdown? or home region
from univ_tools import univ_client
from tree_rewrite import make_options_list, full_recipe_tree
from item_lists import make_shopping_list
import xivjson
from xivjson import *

st.set_page_config(
    layout="wide", 
    page_title="Optimizingway",
    menu_items = {}
    )

hide_streamlit_style = """
<style>
.css-hi6a2p {padding-top: 0rem;}
</style>

"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

@st.cache_resource
def get_univ_client():
    return univ_client()
univ_client = get_univ_client()

@st.cache_resource
def cache_options_list():
    return make_options_list()
options_list = cache_options_list()

travel_order = ""
shopping_list = ""
totals = 0

lcol, mcol, rcol = st.columns([2,5,2])

with rcol.form(key="settings"):
    item = st.selectbox("Home Server", ["Faerie","Sargatanas"], None)
    show_cross_region = st.checkbox("Show cross region results", True)
    show_region = st.checkbox("Show cross DC results", True)
    show_home = st.checkbox("Always show some results from home DC", True)
    show_home = st.checkbox("Always show some results from home server", True)
    submit_button = st.form_submit_button(label='Save Settings')

with mcol.form(key='tree_opti'):
    form_lcol, form_mcol, form_rcol = st.columns([4,1,1])
    item = form_lcol.selectbox("Search for Item", options_list, None)
    quantity = form_mcol.number_input("Desired Quantity", 1, 99, step=1)
    hq = form_rcol.checkbox("Allow NQ")
    crystals = form_rcol.checkbox("Include Crystals")
    submit_button = st.form_submit_button(label='Optimize')
    if item is not None:

        reci_tree = full_recipe_tree(item, univ_client, quantity)#, hq, crystals)
        # ctr = counter()
        nodes = reci_tree.to_dict()
        # print(nodes)
        print(nodes)


if item is not None:  
    with mcol.container(border=True, height = 500):   
        return_select = tree_select([nodes], 
                                    checked = [0],
                                    expanded = list(reci_tree.node_mapping.keys()), #gather all beforehand
                                    expand_disabled=False,
                                    no_cascade=True, 
                                    )
        print("update")
        if len(return_select["checked"]) > 0 and return_select["checked"] != [0]:
            en = "en" #fix later
            checked_nodes = [reci_tree.node_mapping[x] for x in return_select["checked"]]
            #TODO:edit, not replace, we dont wanna wipe progress by accident
            shopping_list = make_shopping_list(checked_nodes)
            # shopping_list = "".join([f"{(item_lookup[str(reci.node_mapping[x].item_id)])[en]} \n -{reci.node_mapping[x].label}\n" for x in return_select["checked"]])
            # # print(return_select["checked"])  

with lcol:
    with st.container(border=True):
        # st.text_area(label="Travel Order", value=travel_order, height = 100)
        st.text_area(label="Shopping List", value=shopping_list, height = 650)


with rcol:
    with st.container(border=True):
        st.text_area(label="Total | Selected | Acquired", value=totals, height = 300)

