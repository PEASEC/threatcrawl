"""This script plots a multigraph for the given url_map

ATTENTION: this script can take a while to finish!
"""

import json
import networkx as nx
import matplotlib.pyplot as plt

################################################################################
urlmap_file = "assets/20221209_065638_url_map.json"
################################################################################

with open(urlmap_file) as f:
  url_map = json.load(f)

nodes = {}

for entry in url_map:
  if entry["url from"] not in nodes:
    nodes[entry["url from"]] = len(nodes) + 1
  if entry["url to"] not in nodes:
    nodes[entry["url to"]] = len(nodes) + 1

edges = []
for entry in url_map:
  edges.append((nodes[entry["url from"]], nodes[entry["url to"]]))

options = {
    'node_size': 0.5,
    'width': 0.1,
}

G = nx.Graph()
G.add_edges_from(edges)
nx.draw_networkx(G, with_labels=False, **options)
plt.show()
