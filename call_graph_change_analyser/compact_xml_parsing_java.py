#%%
import os
from bs4 import BeautifulSoup


#%%
with open(file_path, 'r') as f:
    data = f.read()

Bs_data = BeautifulSoup(data, "xml")

#%%
# get method names !!!! 07.12 20:56
def get_function_name(function_tag):
    function_name = function_tag.findAll('SimpleName', recursive=False)[0]['label']
    return function_name, len(function_tag.findAll('SingleVariableDeclaration', recursive=False))


# %%
# WORKING get function names !!!! 07.12 20:56
function_tags = Bs_data.findAll('MethodDeclaration')
i = 1
for function_tag in function_tags:
    function_name = ''
    print("----- function {0}".format(i))
    i += 1
    function_name = get_function_name(function_tag)
    print(function_name)


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

#%%
print(get_function_name(Bs_data.findAll('MethodDeclaration')[0]))
print(get_called_functions(Bs_data.findAll('MethodDeclaration')[0]))
# %%