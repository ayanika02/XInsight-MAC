import streamlit as st
from streamlit_extras.grid import grid

import db
import insights

dataset_file_name = None 

def get_insights(dataset_file_name):
    eda_grid = grid([1], vertical_align="centre")
    with eda_grid.container():
        tab1,tab2,tab3,tab4,tab5,tab6,tab7,tab8=st.tabs(['Data Info','Numeric Features','Categorical Features','Show Data','Bivariate-Correlation','Multivariate-Correlation','Clustering','Knowledge Graph'])
        insights.perform_eda(dataset_file_name,tab1,tab2,tab3,tab4,tab5,tab6,tab7,tab8)

def insights_gui():
    dataset_df = db.get_datasets()
    dataset_file_name = None
    dataset_file_name = st.selectbox(
        'Select a dataset',dataset_df['file_name'].tolist(), index=None, placeholder="Select a dataset...")

    if dataset_file_name is not None:
        get_insights(dataset_file_name)
    
