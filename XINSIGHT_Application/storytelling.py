import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import streamlit as st

import db

def check1(uploaded_data):
    if uploaded_data.type=='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet':
        #data1=pd.read_excel(uploaded_data)
        #data1.to_csv("test.csv") 
        #val = pd.DataFrame(pd.read_csv("test.csv"))
        val=pd.read_excel(uploaded_data)
    else:
        val=pd.read_csv(uploaded_data) 
    return(val)

def create_stories(dataset_file_name,tab1,tab2,tab3, tab4, tab5):
    
    #data = check1(uploaded_data)
    data = db.load_df_from_parquet(dataset_file_name)
    
    with tab1: #measures and dimensions
        print()  
    
    with tab2: #charts
        print()

    with tab3: #metrics
        print() 

    with tab4: #Time Series
        print()   

    with tab5: #dashboards
        print()     

