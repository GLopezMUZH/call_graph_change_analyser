#%%
from bs4 import BeautifulSoup

#%%
# TEST------------------------------------------
#file_curr_path = os.path.normpath('C:/Users/lopm/Documents/gitprojects/call_graph_change_analyser/project_results/JKQtPlotter/.cache/JKQtPlotter/current/lib/jkqtplotter/jkqtpbaseplotterstyle.cpp.xml')
#file_curr_path = os.path.normpath('C:/Users/lopm/Documents/mt/sandbox/stuff/uvcannode_compact.xml')
file_curr_path = os.path.normpath(
    'C:/Users/lopm/Documents/mt/sandbox/stuff/jkqtpbaseplotterstyle_compact.xml')
#file_curr_path = os.path.normpath('C:/Users/lopm/Documents/mt/sandbox/stuff/function_names_Compact.xml')

# graphs/jkqtpscatter.cpp.xml')
#file_prev_path = os.path.normpath('C:/Users/lopm/Documents/gitprojects/call_graph_change_analyser/project_results/JKQtPlotter/.cache/JKQtPlotter/previous/lib/jkqtplotter/jkqtpbaseplotterstyle.cpp.xml')


#%%
def get_xml_objects(file_path):
    with open(file_path, 'r') as f:
        xml_data = f.read()
    Bs_data = BeautifulSoup(xml_data, "xml")
    return Bs_data

def get_function_name(function_tag):
    """
    Returns the name of the function from the tags name_detail[label] or if nested name, the name_detail's inside the name_tag .
  
    This function is used for getting the name of functions in the function declaration. 
    It searches just within the direct children of the current tag.
  
    Parameters:
    function_tag (BeautifulSoup.Tag): The Tag to get the name from, it can be a function or a constructor
  
    Returns:
    str: The name of the funciton (eg. JKQTPSetSystemDefaultBaseStyle or JKQTBasePlotterStyle::loadSettings)
    int: The defined number of parameters for this function
  
    """
    function_name = ''
    for name_tag_indirect in function_tag.findAll('name_tag', recursive=False):
        for ct in name_tag_indirect.children:
            if ct.name == 'name_detail':
                function_name = "".join((function_name, ct['label']))
            if ct.name == 'operator':
                function_name = "".join((function_name, ct['label']))
    for name_detail_direct in function_tag.findAll('name_detail', recursive=False):
        function_name = name_detail_direct['label']
    return function_name, len(function_tag.parameter_list.findAll('parameter', recursive=False))



