from typing import List
from re import search
import pandas as pd
import numpy as np

from mlxtend.frequent_patterns import apriori, association_rules
from mlxtend.preprocessing import TransactionEncoder

"""
class SupportRecord():
    def __init__(self) -> None:
        pass
        #= namedtuple( # pylint: disable=C0103
        #'SupportRecord', ('items', 'support')

RelationRecord = namedtuple( # pylint: disable=C0103
    'RelationRecord', SupportRecord._fields + ('ordered_statistics',))
OrderedStatistic = namedtuple( # pylint: disable=C0103
    'OrderedStatistic', ('items_base', 'items_add', 'confidence', 'lift',))

class RuleRecord():
    def __init__(self, data:str) -> None:


        self.items = items
        # calculate dir path and file name
        self.file_dir_path = os.path.dirname(file_path)
        self.file_name = os.path.basename(file_path)

    def get_file_name(self):
        return self.file_name

    def get_file_dir_path(self):
        return self.file_dir_path

    def get_file_path(self):
        return self.file_path

    def __str__(self) -> str:
        return("FileData [file_name: {0}, file_dir_path: {1}]"
               .format(self.file_name,
                       self.file_dir_path))
"""

def get_records(con_graph_db, df_column_name, sql_statement, min_items=2):
    df = pd.read_sql_query(sql_statement, con_graph_db)
    print("df len: ", len(df))
    # stack functionality removes NaNs to generate the nested list:
    records_concats = pd.DataFrame(df[df_column_name]).stack().groupby(level=0).apply(list).values.tolist()
    records = []
    for r in records_concats:
        records.append(list(r[0].split(sep=',')))
    print('records len: ', len(records))
    pruned_records = []
    for r in records:
        if len(r)>min_items:
            pruned_records.append(r)
    print('pruned_records len: ', len(pruned_records))
    return records, pruned_records, df


def show_transactions_containing_items(df, col_name: str, items_list: List[str], print_elems = True):
    """
    Displays the summarized occurences of the items in the list troughout the whole set of transactions. 
    
    """
    if len(items_list) == 2:
        transactions_2_elem_rule(df, col_name, items_list, print_elems)
    if len(items_list) == 3:
        transactions_3_elem_rule(df, col_name, items_list, print_elems)
    if len(items_list) == 4:
        transactions_4_elem_rule(df, col_name, items_list, print_elems)
    if len(items_list) == 5:
        transactions_5_elem_rule(df, col_name, items_list, print_elems)

def transactions_2_elem_rule(df, col_name: str, items_list: List[str], print_elems = True):
    i = 0
    j = 0
    jj = 0
    for ind in df.index:
        if search(items_list[1], df[col_name][ind]):
            jj += 1
        
        if search(items_list[0], df[col_name][ind]):
            i += 1
            if search(items_list[1], df[col_name][ind]):
                j += 1
                if print_elems:
                    print(df[col_name][ind])

    print("Element count. Df len {0}. 1ind: {1}, 2dep: {2}, 2ind: {3}".format(len(df),i,j,jj))



def transactions_3_elem_rule(df, col_name: str, items_list: List[str], print_elems = True):
    i = 0
    j = 0
    k = 0
    jj = 0
    kk = 0
    for ind in df.index:
        if search(items_list[1], df[col_name][ind]):
            jj += 1
        if search(items_list[2], df[col_name][ind]):
            kk += 1

        if search(items_list[0], df[col_name][ind]):
            i += 1
            if search(items_list[1], df[col_name][ind]):
                j += 1
                if search(items_list[2], df[col_name][ind]):
                    k += 1
                    if print_elems:
                        print(df[col_name][ind])

    msg = """Element count. Df len {0}. 1ind: {1}, 2dep: {2}, 3dep: {3},
    2ind: {4}, 3ind: {5}""".format(len(df),i,j,k,jj,kk)
    print(msg)


def transactions_4_elem_rule(df, col_name: str, items_list: List[str], print_elems = True):
    i = 0
    j = 0
    k = 0
    l = 0
    jj = 0
    kk = 0
    ll =0
    for ind in df.index:
        if search(items_list[1], df[col_name][ind]):
            jj += 1
        if search(items_list[2], df[col_name][ind]):
            kk += 1
        if search(items_list[3], df[col_name][ind]):
            ll += 1

        if search(items_list[0], df[col_name][ind]):
            i += 1
            if search(items_list[1], df[col_name][ind]):
                j += 1
                if search(items_list[2], df[col_name][ind]):
                    k += 1
                    if search(items_list[3], df[col_name][ind]):
                        l += 1
                        if print_elems:
                            print(df[col_name][ind])

    msg = """Element count. Df len {0}. 1ind: {1}, 2dep: {2}, 3dep: {3}, 4dep: {4},
    2ind: {5}, 3ind: {6}, 4ind: {7}""".format(len(df),i,j,k,l,jj,kk,ll)
    print(msg)


def transactions_5_elem_rule(df, col_name: str, items_list: List[str], print_elems = True):
    i = 0
    j = 0
    k = 0
    l = 0
    m = 0
    jj = 0
    kk = 0
    ll =0
    mm = 0
    for ind in df.index:
        if search(items_list[1], df[col_name][ind]):
            jj += 1
        if search(items_list[2], df[col_name][ind]):
            kk += 1
        if search(items_list[3], df[col_name][ind]):
            ll += 1
        if search(items_list[4], df[col_name][ind]):
            mm += 1

        if search(items_list[0], df[col_name][ind]):
            i += 1
            if search(items_list[1], df[col_name][ind]):
                j += 1
                if search(items_list[2], df[col_name][ind]):
                    k += 1
                    if search(items_list[3], df[col_name][ind]):
                        l += 1
                        if search(items_list[4], df[col_name][ind]):
                            m += 1
                            if print_elems:
                                print(df[col_name][ind])

    msg = """Element count. Df len {0}. 1ind: {1}, 2dep: {2}, 3dep: {3}, 4dep: {4}, 5dep: {5}
    2ind: {6}, 3ind: {7}, 4ind: {8}, 5ind: {9}""".format(len(df),i,j,k,l,m,jj,kk,ll,mm)
    print(msg)


def get_rules_by_threshold(df, min_t=0.1, max_t=0.5, n=11, max_nr_rules=100):
    """
    Returns list of [threshold, nr_rules]
    """
    r = []
    for threshold in np.linspace(max_t,min_t,n):
        tmp = apriori(df, min_support=threshold, use_colnames=True)
        r.append([threshold, len(tmp)])
        if len(tmp)> max_nr_rules:
            break
    return r