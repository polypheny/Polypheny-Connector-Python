import os
import matplotlib.pyplot as plt
import networkx as nx
import polypheny


def draw_graph(con):
    cur = con.cursor()

    # Fetch nodes
    cur.executeany("cypher", 'MATCH (n:Person) RETURN n ORDER BY n.id', namespace="cyphertest")
    nodes = cur.fetchall()

    # Fetch start of relationships
    cur.executeany("cypher", 'MATCH (a:Person)-[:KNOWS]->() RETURN a', namespace="cyphertest")
    start_nodes = cur.fetchall()

    # Fetch end of relationships
    cur.executeany("cypher", 'MATCH (a)-[:KNOWS]->(b:Person) RETURN b', namespace="cyphertest")
    end_nodes = cur.fetchall()

    cur.close()
    con.close()

    # Create graph
    G = nx.DiGraph()

    # Add nodes to graph
    for node in nodes:
        G.add_node(node['id'], label=node['properties']['name'])

    # Add edges to graph
    for start, end in zip(start_nodes, end_nodes):
        G.add_edge(start['id'], end['id'], type='KNOWS')

    # Draw graph
    pos = nx.spring_layout(G)
    labels = nx.get_node_attributes(G, 'label')
    nx.draw(G, pos, with_labels=True, labels=labels, node_size=3000, node_color='skyblue', font_size=10,
            font_color='black', font_weight='bold', edge_color='gray')
    plt.show()


if __name__ == "__main__":
    con = polypheny.connect(os.path.expanduser("~/.polypheny/polypheny-prism.sock"), username='pa', password='',
                            transport='unix')
    draw_graph(con)
