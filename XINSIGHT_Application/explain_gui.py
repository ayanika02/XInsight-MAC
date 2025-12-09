#!/usr/bin/env python
# coding: utf-8

# In[5]:


import streamlit as st
import pandas as pd
import logging
import pickle
import db
from explain import visualize_decision_tree, visualize_decision_tree1, visualize_decision_tree2, visualize_decision_tree3

dataset_file_name = None 
def get_explain(dataset_file_name):
    # Read the CSV file
    #uploaded_file = st.file_uploader("Upload CSV", type=["csv"])

    if dataset_file_name is not None:
        #df = pd.read_csv(uploaded_file)
        df=db.load_df_from_parquet(dataset_file_name)
        # st.write(df)
        # columns = list(df.columns)
        # table = pd.DataFrame({"columns": columns, "Types": df.dtypes.to_list()})
        # st.dataframe(table, hide_index=True)    
        # Dropdown to select target and features
        with st.expander("Select Target"):
            target_name = st.selectbox('Select target', df.columns)
        with st.expander("Select Feature"):
            feature_name = st.multiselect('Select Features', df.columns)
        with st.expander("Select Library"):
            library_type = st.selectbox('Library type', ['Sklearn',  'Pyspark', 'XGboost','Lightgbm',])
        with st.expander("Select ML Task"):
            task_type = st.selectbox('Task type', ['Classification', 'Regression',])
        # row_index = st.number_input('Test_row Index', min_value=0, max_value=len(df) - 1, step=1)
        # if st.button("Generate CSV for Selected Row"):
        #         selected_row = df.iloc[[row_index]]
        #         csv = selected_row.to_csv(index=False)
            
        #         st.download_button(
        #             label="Download CSV",
        #             data=csv,
        #             file_name=f"row_{row_index}.csv",
        #             mime="text/csv"
        #         )

    # Set up Streamlit page
    logging.getLogger('matplotlib.font_manager').setLevel(logging.CRITICAL)

    # Add a dropdown box to choose file type
    file_type = st.selectbox("Choose file type", ("Pickle (.pkl)", "ONNX (.onnx)"))
    # Load the appropriate file type based on user selection
    if file_type == "ONNX (.onnx)":
        uploaded_file = st.file_uploader("Upload an ONNX model file", type=["onnx"])
    elif file_type == "Pickle (.pkl)":
        with st.expander("Upload pickle file"):
            uploaded_file = st.file_uploader("Choose a pickle model file (.pkl)")
    else:
        uploaded_file = None

    # Load and display the decision tree model
    if uploaded_file is not None:
        X=df[feature_name]
        y=df[target_name]
        #x = X.iloc[row_index]

        if file_type == "ONNX (.onnx)":
            print("onnx is not supported")
        elif file_type =="Pickle (.pkl)" :
            # Add code to load ONNX model 
            loaded_model = pickle.load(uploaded_file)


        try:
            # Visualize the decision tree
            with st.expander("Select different orientation"):
                ori = st.selectbox('Select Different Orientation', [ 'LR', 'RL'])
                if st.button('Visualize Decision Tree'):
                    viz = visualize_decision_tree(loaded_model, X, y,feature_name,target_name)
                
                    v = viz.view(scale=2,show_node_labels=True)
        
                    st.markdown(f"## Decision Tree Visualization")
                    row1 = st.container()
                    row2 = st.container()
                    row3=st.container()
                    
                    with row1:
                        st.image(v.svg(), use_column_width=True)
                        st.write("Tree visualizations")
                    with row2:
                        v2 = viz.view(scale=2,orientation= ori,show_node_labels=True)
                        st.image(v2.svg(), use_column_width=True)
                        st.write("Tree visualizations in LR or RL mode")
                    
                    with row3:
                        v3 = viz.view(scale=2,fancy=False)
                        st.image(v3.svg(), use_column_width=True)
                        st.write("Without Fancy View")

        except Exception as e:
                st.error(f"Error loading or processing: {e}")
        else:
                st.warning("Please upload a model file.")

    # Row index
        row_index= st.number_input('Test_Row_Index', min_value=1, max_value=len(df) - 1, step=1)
        x = X.iloc[row_index]
        button_key1 = 'visualize_button1'
        if st.button('Visualize prediction path',key=button_key1):
            st.write(x)
            viz = visualize_decision_tree(loaded_model, X, y, feature_name, target_name)
            row1 = st.container()
            row2 = st.container()  
            row3=st.container() 
            with row1:
                v1 = viz.view(scale=2,x=x)
            #st.markdown(f"## Prediction path explanations")
                st.image(v1.svg(), use_column_width=True)
                st.write("Prediction path explanations")
            with row2:
                v4=viz.view(scale=2,x=x, show_just_path=True)
                st.image(v4.svg(), use_column_width=True)
                st.write("Prediction just path")
        
        button_key4 = 'visualize_button4'
        if st.button('Visualize Feature Importance', key=button_key4):
            viz = visualize_decision_tree(loaded_model, X, y,feature_name,target_name)
            st.set_option('deprecation.showPyplotGlobalUse', False)
            st.pyplot(viz.instance_feature_importance(x, figsize=(3.5,2)))
            st.write("Feature Importance")

        
        button_key2 = 'visualize_button2'

        # Define the function for visualization here
        node_index = st.number_input('Give Node Id', min_value=0, max_value=30, step=1)
        if st.button('Visualize Decision Tree Leaf distribution', key=button_key2):
            #box = st.container(height = 800)
            viz = visualize_decision_tree(loaded_model, X, y,feature_name,target_name)
            #node_numbers = viz._decision_tree_model.tree_.nodes
            #st.write("All node numbers:", node_numbers)
  
            st.write("node statistics")
            st.write(viz.node_stats(node_id=node_index))
            #st.markdown(f"## Decision Tree Visualization")
            row1 = st.container()
            #row2 = st.container() 
            if task_type=="Classification": 
                with row1:
                    st.set_option('deprecation.showPyplotGlobalUse', False)
                    st.pyplot(viz.ctree_leaf_distributions(figsize=(3.5,2)))
                    st.write("Leaf Distribution")
            else:
                    with row1:
                        st.set_option('deprecation.showPyplotGlobalUse', False)
                        st.pyplot(viz.rtree_leaf_distributions(figsize=(3.5,2)))
                        st.write("Leaf Distribution")

#            with row2:
#                st.set_option('deprecation.showPyplotGlobalUse', False)
#                st.pyplot(viz.leaf_purity(figsize=(3.5,2)))
#                st.write("Leaf purity")

        if library_type=='Sklearn' or library_type=='Pyspark': 
            button_key3 = 'visualize_button3'
            if st.button('Visualize Feature space', key=button_key3):
                st.markdown(f"## Feature space exploration")
                viz = visualize_decision_tree(loaded_model, X, y,feature_name,target_name)
                box1 = st.container()
                box2 = st.container() 
                if task_type=="Classification":     
                    with box1:
                        st.set_option('deprecation.showPyplotGlobalUse', False)
                        st.pyplot(viz.ctree_feature_space(nbins=40, gtype='barstacked', show={'splits','title'}, features=['Medu'],figsize=(5,1.5)))
                        # st.image(v.svg(), use_column_width=True)
                        st.write("Tree partitions one-dimensional feature space.")
                
                    with box2:
                        st.set_option('deprecation.showPyplotGlobalUse', False)
                        st.pyplot(viz.ctree_feature_space(show={'splits','title'}, features=['Medu', 'studytime']))
                        st.write("Tree partitions two-dimensional feature space.")
                else:
                    with box1:
                        st.set_option('deprecation.showPyplotGlobalUse', False)
                        st.pyplot(viz.rtree_feature_space(show={'splits','title'}, features=['Medu'],figsize=(5,1.5)))
                        # st.image(v.svg(), use_column_width=True)
                        st.write("tree partitions one-dimensional feature space.")
                
                    with box2:
                        st.set_option('deprecation.showPyplotGlobalUse', False)
                        st.pyplot(viz.rtree_feature_space(show={'splits','title'}, features=['Medu', 'studytime']))
                        st.write("tree partitions two-dimensional feature space.")

            else:
                print('Feature space partitioning is not explored in XGboost or Lightgbm')   
            

#if __name__ == "__main__":
#    main()

def explain_gui():
    dataset_df = db.get_datasets()
    dataset_file_name = None
    dataset_file_name = st.selectbox(
        'Select a dataset',dataset_df['file_name'].tolist(), index=None, placeholder="Select a dataset...")

    if dataset_file_name is not None:
        get_explain(dataset_file_name)



