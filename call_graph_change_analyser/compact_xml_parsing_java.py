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

def get_function_parameters(function_tag):
    # Formal Parameters
    nr_dir_params = len(function_tag.findAll('SingleVariableDeclaration', recursive=False))
    nr_param_tags = len(function_tag.findAll('Parameter', recursive=False))
    return nr_dir_params + nr_param_tags

def get_function_names(function_tag):
    print("TODO MAYBE OVERHEAD HERE")

def get_function_unqualified_name(function_tag):
    """
    function_unqualified_name,
    function_nr_parameters
    """
    function_name = function_tag.findAll('SimpleName', recursive=False)[0]['label']
    nr_params = get_function_parameters(function_tag) 
    return tuple([function_name, nr_params])


#%%
def get_called_functions(function_tag):
    called_functions = []
    for call_tag in function_tag.findAll('MethodInvocation'):
        called_function_name = call_tag.findAll(
            'SimpleName', recursive=False)[0]['label']
        called_functions.append(called_function_name)

    for call_tag in function_tag.findAll('MethodCallExpr'):
        called_function_name = call_tag.findAll(
            'SimpleName', recursive=False)[0]['label']
        called_functions.append(called_function_name)

    set_called_functions = set(called_functions)
    irrelevant_call_names = [
        'append', 'get', 'run', 'show', 'equals', 'getId',
        'bytesToHexString', 'e', 'i', 'arraycopy','when','toString']
    relevant_all_call_names = (
        set(set_called_functions) - set(irrelevant_call_names))
    return relevant_all_call_names

# %%
def get_function_calls_java(Bs_tree):
    """
    Returns an array of structure list(tuples()...)
        ([
        calling_function_unqualified_name,
        calling_function_nr_parameters,
        called_function_unqualified_name],
        ...[])
    function_parameters can be None when empty in declaration
    """
    function_tags = Bs_tree.findAll('MethodDeclaration')
    arr = []
    for function_tag in function_tags:
        function_names = get_function_unqualified_name(function_tag)
        for cf in get_called_functions(function_tag):
            row = function_names + (cf,)
            arr.append(row)
    return arr
    
