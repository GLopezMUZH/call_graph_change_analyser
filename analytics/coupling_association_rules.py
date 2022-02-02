


# for processing apriori
sql_statement = """select commit_hash, file_name from file_commit"""
dfsql = pd.read_sql_query(sql_statement, con_graph_db)
df_hash = dfsql.groupby('commit_hash')['file_name'].apply(list)

te = TransactionEncoder()
oht_ary = te.fit(df_hash).transform(df_hash, sparse=True)
sparse_df = pd.DataFrame.sparse.from_spmatrix(oht_ary, columns=te.columns_)
sparse_df

for threshold in np.linspace(0.5,0.01,11):
    tmp = apriori(sparse_df, min_support=threshold, use_colnames=True)
    print(threshold, len(tmp))
    if len(tmp)> 250:
        break



frequent_itemsets = apriori(sparse_df, min_support=0.02, use_colnames=True)
frequent_itemsets['length'] = frequent_itemsets['itemsets'].apply(lambda x: len(x))
frequent_itemsets

fi2 = frequent_itemsets[ (frequent_itemsets['length'] > 2) &
                   (frequent_itemsets['support'] >= 0.01) ]
print(len(fi2))
print(fi2.head(3))

print(max(fi2['length']))

l_items = list(fi.iloc[0]['itemsets'])
print(l_items)
print(type(l_items))

show_transactions_containing_items(df, 'files_in_hash', l_items, print_elems=False)


for index, row in fi2.iterrows():
    l_items = list(row['itemsets'])
    print(l_items)
    show_transactions_containing_items(df, 'files_in_hash', l_items, print_elems=False)

    list_combinations = list(combinations(l_items, 2))
    for c in list_combinations:
        print("Dependency: {0} {1} {2}".format(exist_import_dependency(con_graph_db, c[0], c[1]),c[0], c[1]))

