from typing import List
from re import search

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


def show_transactions_containing_items(df, items_list: List[str], print_elems = True):
    if len(items_list) == 2:
        transactions_2_elem_rule(df, items_list, print_elems)
    if len(items_list) == 4:
        transactions_4_elem_rule(df, items_list, print_elems)


def transactions_2_elem_rule(df, items_list: List[str], print_elems = True):
    i = 0
    j = 0
    for ind in df.index:
        if search(items_list[0], df['files_in_hash'][ind]):
            i += 1
            if search(items_list[1], df['files_in_hash'][ind]):
                j += 1
                if print_elems:
                    print(df['files_in_hash'][ind])

    print("Element count. Df len {0}. 1: {1}, 2: {2}".format(len(df),i,j))


def transactions_4_elem_rule(df, items_list: List[str], print_elems = True):
    i = 0
    j = 0
    k = 0
    l = 0
    for ind in df.index:
        if search(items_list[0], df['files_in_hash'][ind]):
            i += 1
            if search(items_list[1], df['files_in_hash'][ind]):
                j += 1
                if search(items_list[2], df['files_in_hash'][ind]):
                    k += 1
                    if search(items_list[3], df['files_in_hash'][ind]):
                        l += 1
                        if print_elems:
                            print(df['files_in_hash'][ind])

    print("Element count. Df len {0}. 1: {1}, 2: {2}, 3: {3}, 4: {4}".format(len(df),i,j,k,l))