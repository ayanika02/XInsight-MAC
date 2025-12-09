
import pandas as pd
import streamlit as st
from streamlit_extras.grid import grid
import time
import urllib.request
import os

import db


def init(): #added so that session variables get initialised
    st.session_state['dataset_file_content'] = 'Dummy content'
    st.session_state['dataset_file_name'] = None
    st.session_state['mime_type'] = None

def put_selected_file_details_in_sesion():
    selection = st.session_state['selection']
    checkedBoxes = selection['Select'].tolist()
    if True in checkedBoxes:
        dataset_file_name = selection['file_name'].tolist()[checkedBoxes.index(True)]
        mime_type = "application/octet-stream"
        if selection['file_name'].tolist()[checkedBoxes.index(True)] == "CSV":
            mime_type = "text/csv"
        elif selection['file_name'].tolist()[checkedBoxes.index(True)] == "Excel":
            mime_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        df = db.load_df_from_parquet(dataset_file_name)
        csv = df.to_csv()
        #dataset_file = db.get_dataset_file(dataset_file_name)
        st.session_state['dataset_file_content'] = csv
        st.session_state['dataset_file_name'] = dataset_file_name
        st.session_state['mime_type'] = mime_type


def ingestion_gui():
    init()
    colT1,colT2 = st.columns([1,8])
    with colT2:
        st.write("**Currently available datasets**")  #** for bold
        
    data_grid = grid([1], vertical_align="centre")
    container = data_grid.container()
    with container:
        ph = st.empty()
        dataset_df = db.get_datasets()
        dataset_df.insert(0, 'Select', False)
        selection = ph.data_editor(dataset_df, height=300,hide_index=True, column_config={"Select": st.column_config.CheckboxColumn(help="Select only one dataset"), 
                "dataset_id":"Dataset ID", "file_name": "File Name", "mime_type": "File Type", "file_size": "File Size in bytes", "date_created": "Data Uploaded"})
        #replace w aggrid
        st.session_state['selection'] = selection
        message = st.empty()
        put_selected_file_details_in_sesion()

        if st.button("Delete selected dataset", type="primary"):
            selection = st.session_state['selection']           
            checkedBoxes = selection['Select'].tolist()

            if True in checkedBoxes:
                dataset_id = selection['dataset_id'].tolist()[checkedBoxes.index(True)]
                result = db.delete_dataset(dataset_id)
                    #print(result)
                dataset_file_name = selection['file_name'].tolist()[checkedBoxes.index(True)]
                db.delete_dataset_file(dataset_file_name)
                message.success("Dataset deleted")
                time.sleep(1)
                message.empty()                  
                dataset_df = db.get_datasets()
                dataset_df.insert(0, 'Select',False)
                ph.data_editor(dataset_df, hide_index=True, column_config={"Select": st.column_config.CheckboxColumn(help="Select only one dataset"), "dataset_id":"Dataset ID", "file_name": "File Name", "mime_type": "File Type", "file_size": "File Size in bytes", "date_created": "Data Uploaded"})

        if st.download_button(label="Download selected dataset", data=st.session_state['dataset_file_content'], mime=st.session_state['mime_type'], file_name=st.session_state['dataset_file_name']):
                message.success("Dataset downloaded")
                time.sleep(1)
                message.empty()                  


        file,url = st.tabs(["Upload local file","Load from URL"])
                        
        with file:
            with st.form("upload-form", clear_on_submit=True):
                uploaded_file = st.file_uploader("FILE UPLOADER",type = ['csv','xlsx'])
                submitted = st.form_submit_button("UPLOAD DATASET")
                                    
            if submitted and uploaded_file is not None:
                fileName = uploaded_file.name
                st.session_state['dataset_file_name'] = fileName
                fileSize = uploaded_file.getvalue().__sizeof__()
                if uploaded_file.type=='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet':
                    st.session_state['mime_type'] = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                    mime_type = "Excel"
                    data_df = pd.read_excel(uploaded_file)
                else:
                    mime_type = "CSV"
                    data_df = pd.read_csv(uploaded_file)                    
                
                fileBytes = data_df.to_parquet()
                # result = db.save_df_as_table(data_df,fileName)
                st.session_state['uploaded_file'] = uploaded_file
                st.session_state['uploaded_file_name'] = uploaded_file.name
                result = db.insert_dataset(fileName, fileBytes, mime_type, fileSize) 
                dataset_df = db.get_datasets() #connection.execute('SELECT dataset_id, file_name, date_created from datasets').df()
                dataset_df.insert(0, 'Select',False)
                ph.data_editor(dataset_df, hide_index=True, column_config={"Select": st.column_config.CheckboxColumn(help="Select only one dataset"), "dataset_id":"Dataset ID", "file_name": "File Name", "mime_type": "File Type", "file_size": "File Size in bytes", "date_created": "Date Uploaded"})
                
        with url:
            with st.form("url-form", clear_on_submit=True):
                url_input = st.text_input("Enter URL 👇")
                submitted = st.form_submit_button("LOAD DATASET")

            if submitted and url_input is not None:
                response = urllib.request.urlopen(url_input, headers={'User-Agent': 'Mozilla/5.0'})
                fileSize = response.info().get('Content-Length', 0)
                st.session_state['mime_type'] =response.info().get('Content-Type', "text/csv")
                if st.session_state['mime_type'] =='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet':
                    mime_type = "Excel"
                else:
                    mime_type = "CSV"

                data_df = pd.read_csv(url_input)
                urlPath = urllib.parse.urlparse(url_input)
                fileName = os.path.basename(urlPath.path)
                fileBytes = data_df.to_parquet()
                result = db.insert_dataset(fileName, fileBytes, mime_type, fileSize)
                dataset_df = db.get_datasets()
                dataset_df.insert(0, 'Select',False)
                ph.data_editor(dataset_df, hide_index=True, column_config={"Select": st.column_config.CheckboxColumn(help="Select only one dataset"), "dataset_id":"Dataset ID", "file_name": "File Name", "mime_type": "File Type", "file_size": "File Size in bytes", "date_created": "Date Uploaded"})
