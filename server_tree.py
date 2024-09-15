from xivjson import * 
import xivjson
# class server_tree:
#     def __init__(self, node_list):
#         keyfuncs = [
#             lambda node: xivjson.reverse_servers_lookup[node.listing["worldName"]]
#             lambda node: node.listing["worldName"]
#             lambda node: node.item_id
#         ]
#         return autotree(node_list, keyfuncs)
    
def make_server_tree(node_list):
        keyfuncs = [
            lambda node: xivjson.reverse_servers_lookup[node.listing["worldName"]],
            lambda node: node.listing["worldName"],
            lambda node: node.item_id
        ]
        return autotree(node_list, keyfuncs)

def autodict(node_list, key_func):
    retval = {}
    for node in node_list:
        key = key_func(node)
        if key in retval:
            retval[key].append(node)
        else:
            retval[key] = [node]
    return retval

def autotree(node_list, key_funcs):
    if key_funcs == []:
        return node_list
    key_func = key_funcs[0]
    retval = autodict(node_list, key_func)
    for key in retval:
        retval[key] = autotree(retval[key], key_funcs[1:])
    return retval
