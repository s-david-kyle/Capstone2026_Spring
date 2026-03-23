import pandas as pd
import networkx as nx

def create_demo_graph():
    # Define the heads, relations, and tails
    head = ['drugA', 'drugB', 'drugC', 'drugD', 'drugA', 'drugC', 'drugD', 'drugE', 'gene1', 'gene2','gene3', 'gene4', 'gene50', 'gene2', 'gene3', 'gene4']
    relation = ['treats', 'treats', 'treats', 'treats', 'inhibits', 'inhibits', 'inhibits', 'inhibits', 'associated', 'associated', 'associated', 'associated', 'associated', 'interacts', 'interacts', 'interacts']
    tail = ['fever', 'hepatitis', 'bleeding', 'pain', 'gene1', 'gene2', 'gene4', 'gene20', 'obesity', 'heart_attack', 'hepatitis', 'bleeding', 'cancer', 'gene1', 'gene20', 'gene50']

    # Create a dataframe
    df = pd.DataFrame({'head': head, 'relation': relation, 'tail': tail})

    # Create a knowledge graph
    G = nx.Graph()
    for _, row in df.iterrows():
        G.add_edge(row['head'], row['tail'], label=row['relation'])
    
    return G
