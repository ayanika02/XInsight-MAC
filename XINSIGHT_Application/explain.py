#!/usr/bin/env python
# coding: utf-8

# In[ ]:
import lightgbm as lgb
import xgboost as xgb
from xgboost import plot_importance, plot_tree, plotting
# import tensorflow_decision_forests as tf
# from tensorflow_decision_forests.tensorflow.core import Task
import pandas as pd
import numpy as np
import pickle
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier, DecisionTreeRegressor, _tree
import logging
import matplotlib as plt
#import ipywidgets as widgets
#from IPython.display import display
from sklearn.preprocessing import LabelEncoder
import dtreeviz

def label_encode_object_columns(df):
            for column in df.columns:
                if df[column].dtype == 'object':
                    label_encoder = LabelEncoder()
                    df[column] = label_encoder.fit_transform(df[column])
                # Print mapping if needed
                    print(f"Mapping for {column}: {dict(zip(label_encoder.classes_, label_encoder.transform(label_encoder.classes_)))}")

def visualize_decision_tree(loaded_model,X,y,feature_name,target_name):
    feature_names = feature_name
    target_name = target_name

    viz = dtreeviz.model(loaded_model, X, y,tree_index=1,target_name=target_name, feature_names=feature_names)
    return viz


def visualize_decision_tree1(loaded_model, X, y,df):
    # row_index = st.slider('Row Index', min_value=0, max_value=len(df) - 1, step=1)
    # x = df.iloc[row_index]
    viz= dtreeviz.model(loaded_model, X, y,
                    class_names=list(y.unique()),tree_index=1)
    # v1=viz1.view(x = x)
    return viz

def visualize_decision_tree2(loaded_model, X, y,df):
    viz = dtreeviz.model(loaded_model, X, y,
                        class_names=list(y.unique()),tree_index=1)
    return viz

def visualize_decision_tree3(loaded_model, X, y,df):
    viz = dtreeviz.model(loaded_model, X, y,
                        class_names=list(y.unique()),tree_index=1)

    return viz