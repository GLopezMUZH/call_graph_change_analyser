#%%
import os
from bs4 import BeautifulSoup
import pandas as pd


#%%
"""
with open(file_path, 'r') as f:
    data = f.read()

Bs_data = BeautifulSoup(data, "xml")
"""
#%%
def param_placeholder(n, a='param,'):
    return(((a*n))[:-1])


#%%
# get method names !!!! 07.12 20:56
def get_function_names(function_tag):
    """
    function_name,
    function_long_name,
    function_parameters
    """
    function_name = function_tag.findAll('SimpleName', recursive=False)[0]['label']
    #return function_name, len(function_tag.findAll('SingleVariableDeclaration', recursive=False))
    nr_params_FormalParameters = len(function_tag.findAll('SingleVariableDeclaration', recursive=False))
    nr_params = nr_params_FormalParameters  # missing 'indirect' params 
    return [function_name, function_name, param_placeholder(nr_params)]


#%%
def get_called_functions(function_tag):
    called_functions = []
    for call_tag in function_tag.findAll('MethodInvocation'):
        called_function_name = call_tag.findAll('SimpleName', recursive=False)[0]['label']
        called_functions.append(called_function_name)

    print("len list ",len(called_functions))
    sc = set(called_functions)
    print("len sc ",len(sc))
    return sc

# %%
def get_function_to_file_funciton_tags(Bs_tree):
    """
    Returns an array of structure 
        ([function_name,function_long_name,function_parameters],
        ...[])
    function_parameters can be None when empty in declaration
    """
    function_tags = Bs_tree.findAll('MethodDeclaration')
    arr = []
    for function_tag in function_tags:
        function_names = get_function_names(function_tag)
        arr.append(function_names)
    return arr
    
