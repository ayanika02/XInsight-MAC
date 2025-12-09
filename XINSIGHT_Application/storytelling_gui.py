import streamlit as st
from streamlit_extras.grid import grid
import pandas as pd

import db
import storytelling
import measures_and_dimensions_gui
#import charts_gui_v2
import charts_gui_v3
import metric_gui
import time_series

dataset_file_name = None 


def create_stories(dataset_file_name):
    storytelling_grid = grid([1], vertical_align="centre")
    with storytelling_grid.container():
        tab1,tab2,tab3,tab4, tab5=st.tabs(['Measures and Dimensions','Charts', 'Metrics', 'Time Series', 'Dashboards'])

        with tab1:
            if dataset_file_name is not None:
                measures_and_dimensions_gui.show_measures_and_dimensions(dataset_file_name)

        with tab2:
            if dataset_file_name is not None:
                # df = db.show_chart_data()
                # df.index = df.index+1
                # st.table(df)
                #charts_gui_v2.show_charts(dataset_file_name)
                charts_gui_v3.show_charts(dataset_file_name)
                #chart_spec = charts_gui.show_charts(dataset_file_name)
                #st.write(chart_spec)
        with tab3:
              if dataset_file_name is not None:
                metric_gui.show_metrics(dataset_file_name)
        
        with tab4:
              if dataset_file_name is not None:
                time_series.time_series_forecasting(dataset_file_name)
                # time_series.show_metrics(dataset_file_name)

        with tab5:
            st.write("Dashboard - work in progress")
            
def storytelling_gui():
    dataset_df = db.get_datasets()
    dataset_file_name = None
    dataset_file_name = st.selectbox(
        'Select a dataset',dataset_df['file_name'].tolist(), index=None, placeholder="Select a dataset...")

    if dataset_file_name is not None:
        create_stories(dataset_file_name)
