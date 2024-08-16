from streamlit_agraph import agraph, Node, Edge, Config
import streamlit as st

@st.experimental_fragment
def generateBubbleChart(data):
    nodes = []
    edges = []
    node_counter = 0

    nodes.append(Node(id="Start", label="Start", size=40, color='#363b4f'))

    for category, themes in data.items():
        category_id = f"category_{node_counter}"
        nodes.append(Node(id=category_id, label=category, size=30, color='#4b3b8f'))
        edges.append(Edge(source="Start", target=category_id))
        node_counter += 1

        for theme, subjects in themes.items():
            theme_id = f"theme_{node_counter}"
            nodes.append(Node(id=theme_id, label=theme, size=20, color='#816a9e'))
            edges.append(Edge(source=category_id, target=theme_id))
            node_counter += 1

            for subject in subjects:
                subject_id = f"subject_{node_counter}"
                nodes.append(Node(id=subject_id, label=subject, size=10, color='#e1d0ed'))
                edges.append(Edge(source=theme_id, target=subject_id))
                node_counter += 1

    config = Config(
        width=1000,
        height=1000,
    )
    return agraph(nodes=nodes, edges=edges, config=config)