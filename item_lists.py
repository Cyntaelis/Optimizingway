import xivjson
import server_tree


def format_node(node):
    # item_name = xivjson.item_lookup[node.item_id]["en"]
    hqnq = "HQ" if node.listing["hq"] else "NQ"
    ppu = node.listing["pricePerUnit"]
    qty = node.listing["quantity"]
    return f"{hqnq} x {qty} @ {ppu}"

def make_shopping_list(node_list):
    datacenters = server_tree.make_server_tree(node_list)
    # for node in node_list:
    #     world = node.listing["worldName"]
    #     dc = xivjson.reverse_servers_lookup[world]
    #     if dc in datacenters:
    #         datacenters[dc].append(node)
    #     else:
    #         datacenters[dc] = [node]
    
    retval = []
    for dcn, dc in sorted(datacenters.items()):
        retval.append("+ "+dcn)
        for worldn, world in sorted(dc.items()):
            retval.append("+-- "+worldn)
            for item_id, item in sorted(world.items()):
                retval.append("+---- "+xivjson.item_lookup[str(item_id)]["en"])
                for listing in sorted(item, key=lambda x: x.listing["pricePerUnit"]):
                    retval.append("+------ "+format_node(listing))

    #     nodes = sorted(datacenters[dc], key=lambda x:(x.listing["worldName"], x.item_id, x.listing["pricePerUnit"]))
    #     current_world = nodes[0].listing["worldName"]
    #     retval.append("-"+current_world)
    #     for node in nodes:
    #         if node.listing["worldName"] != current_world:
    #             current_world = node.listing["worldName"]
    #             retval.append("-"+current_world)
    #         retval.append("--"+format_node(node))
    retval = "".join([x+"\n" for x in retval])
    return retval

    # sorted_nodes = sorted(node_list, key=server_sort_comparator)
    