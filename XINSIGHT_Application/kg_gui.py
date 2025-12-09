import random
import streamlit as st
from rdflib import Graph, Literal, Namespace, URIRef
from dateutil import parser
import base64
from urllib.parse import quote
import pyvis
from collections import Counter
from rdflib.plugins.sparql import prepareQuery


'''
Knowledge graphs generated with this script is not yet being saved in the database.
'''

def preprocess_columns(df):
    columns = []
    for col in df.columns:
        col_processed = col.replace(" ", "_")
        col_processed = quote(col_processed, safe="_")  # Encode special characters
        columns.append(col_processed)
    df.columns = columns
    return df

def convert_to_ttl(df, main_column):
    # Create an RDF graph
    g = Graph()
    
    # Define namespaces
    maain_col = Namespace("http://example.com/"+main_column+'/')
    predicates = Namespace("http://example.com/predicates/")

    # Bind predicates for object properties
    for col in df.columns:
        if col != main_column:
            g.bind(col, predicates[col])

    # Iterate through the rows of the DataFrame
    for _, row in df.iterrows():
        subject_value = str(row[main_column]).replace(" ", "_")
        subject_value = quote(subject_value, safe='_')  # Encode special characters
        subject = URIRef(maain_col[subject_value])

        for col in df.columns:
            if col == main_column:
                continue
            elif df[col].dtype == 'object':
                g.add((subject, predicates[col], Literal(row[col])))
            elif df[col].dtype == 'int64':
                g.add((subject, predicates[col], Literal(row[col], datatype=Namespace("http://www.w3.org/2001/XMLSchema#integer"))))
            elif df[col].dtype == 'float64':
                g.add((subject, predicates[col], Literal(row[col], datatype=Namespace("http://www.w3.org/2001/XMLSchema#float"))))
            elif df[col].dtype == 'datetime64':
                date_value = parser.parse(str(row[col]), dayfirst=True).date()
                g.add((subject, predicates[col], Literal(date_value, datatype=Namespace("http://www.w3.org/2001/XMLSchema#date"))))

    return g

def vis_graph(g, columns, main_column):
    nodes = []
    edges = []
    node_types = []
    node_colors = {}

    predicate_colors = {col: '#%06x' % random.randint(0, 0xFFFFFF) for col in columns}

    for s, p, o in g:
        subject = str(s)
        object = str(o)
        predicate = str(p).split('/')[-1]

        if subject not in nodes:
            nodes.append(subject)
            node_types.append(subject.split('#')[0] + '#')
            node_colors[subject] = 'gray'

        if object not in nodes:
            nodes.append(object)
            node_types.append(object.split('#')[0] + '#')
            node_colors[object] = predicate_colors.get(predicate, 'gray')

        edges.append((subject, predicate, object))

        del subject, object, predicate

    pyvis_graph = pyvis.network.Network(notebook=True, cdn_resources='remote')
    for i, node in enumerate(nodes):
        if node.startswith("http://example.com/"+main_column+'/'):
            # Modify subject label
            sub_label=main_column + ': ' + node.split('#')[-1].split('/')[-1]
            pyvis_graph.add_node(i, label=sub_label, title=node, color=node_colors[node])
        else:
            pyvis_graph.add_node(i, label=node.split('#')[-1], title=node, color=node_colors[node])

    for source, predicate, target in edges:
        source_index = nodes.index(source)
        target_index = nodes.index(target)
        pyvis_graph.add_edge(source_index, target_index, label=predicate, title=source + ' ' + predicate + ' ' + target)

    pyvis_graph.force_atlas_2based()
    pyvis_graph.show("graph.html")
    st.components.v1.html(pyvis_graph.html, height=600)
    # Display metadata
    st.header("Graph Metadata")
    st.write(f"Number of Nodes: {len(nodes)}")
    st.write(f"Number of Edges: {len(edges)}")
    #st.write(f"Types of Nodes: {set(nodes)}")
    #node_type_counts = Counter(node_types)
    #for node_type, count in node_type_counts.items():
    #    st.write(f"- {node_type}: {count}")

def get_binary_file_downloader_html(data, file_label='File'):
    bin_str = base64.b64encode(data.encode()).decode()
    href = f'<a href="data:application/octet-stream;base64,{bin_str}" download="{file_label}">Download {file_label}</a>'
    return href

def run_query(ttl_data, query):
    g = ttl_data
    query = prepareQuery(query)
    results = g.query(query)
    results_str = '\n'.join(map(str, results))
    return results_str