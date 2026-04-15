import pandas as pd
import networkx as nx

def convert_df_to_kg(df):
    """
    Converts a Pandas DataFrame to a NetworkX graph.

    Args:
        df (pd.DataFrame): A Pandas DataFrame with columns 'head', 'tail', and 'relation'.

    Returns:
        nx.Graph: A NetworkX graph object.
    """
    G = nx.Graph()
    for _, row in df.iterrows():
        G.add_edge(row['head'], row['tail'], label=row['relation'])
    return G