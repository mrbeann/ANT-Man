#coding=utf-8
"""
show content of a .pkl file
"""
import pickle 
import pandas as pd
from configs import measure_path, measure_path_social, model_path

pickle_file_name = None
with open(pickle_file_name, 'rb') as f:
    power_qos = pickle.load(f)
    print(power_qos)

