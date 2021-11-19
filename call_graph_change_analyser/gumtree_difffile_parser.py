#%%
import os
import re

from models import MethodCallChangeInfo

#%%
def find_whole_word(w):
    return re.compile(r'\b({0})\b'.format(re.escape(w))).search

def match_diff(multiline_str):
    matches= False
    if len(multiline_str.splitlines())>2:
        if (find_whole_word('match')(multiline_str.splitlines()[1])):
            matches = True
    return matches

def get_call_names_from_change_block(raw: str):
    lines = raw.split('\n')
    indents = [(0,0,'root')]
    for a in raw.split('\n'):
        indent = 0
        while (a[indent] == ' '): 
            indent+=1
        if indent % 4:
            print("not multiple of 4")
            break
        cnt = a.replace('  ','')
        cnt = cnt.split("[", -1)[0]
        indents.append((len(indents), int(indent/4)+1,cnt))

    #calls = [ (x, y, z) for x, y, z in indents if z  == 'call ' ]
    call_next_indents = [ y+1 for x, y, z in indents if z  == 'call ' ]

    # Case 1: direct case, name is direct element, tabbed, from call
    call_names = [ z[6:len(z)].strip() for x, y, z in indents if (z[0:5]  == 'name:' and y in call_next_indents)]

    return call_names



#%%
def get_method_call_change_info_cpp(path_to_diff_file, path_to_src_file):
    source_node = 'hola'
    end_node = ''
    start_date = ''
    end_date = ''
    with open(path_to_diff_file) as file:
        file_contents = file.read()
        #print(file_contents)
        change_blocks = file_contents.split("===", -1)
        for blk in change_blocks:
            if not match_diff(blk):
                if find_whole_word('call')(blk):
                    print("BLK ST ************")
                    blk = blk.replace('---------------------','')
                    change_type = blk[0:blk.find('\n')]
                    print("Change type: ", change_type)
                    raw = blk[blk.find('\n')+1:len(blk)]
                    call_names = get_call_names_from_change_block(raw)
                    print(blk)
                    print(call_names)
                    print("BLK STOP ************")

    
    MethodCallChangeInfo(source_node, end_node, start_date, end_date)

    return 


# %%
