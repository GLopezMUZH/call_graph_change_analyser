#%%
import pandas as pd
import matplotlib as mp
import sqlite3

#%%
def print_basic_stats_one_col(df_col):
    print("Mean:{:,.2f}".format(df_col.mean()))
    print("Median:{:,.2f}".format(df_col.median()))
    print("Mode:", df_col.mode())
    print("Min:{:,.2f}".format(df_col.min() ))
    print("Max:{:,.2f}".format( df_col.max() ))
    print("Std:{:,.2f}".format(df_col.std()))
    #print("Variance: {:,.2f}".format(df_col.var()))
    print("Sum: {:,.2f}".format(df_col.sum()))
    """ Compute the sample skewness.
    The statistic computed here is the adjusted Fisher-Pearson standardized
    moment coefficient G1. The algorithm computes this coefficient directly
    from the second and third central moment.
    https://github.com/pandas-dev/pandas/blob/7c48ff4409c622c582c56a5702373f726de08e96/pandas/core/nanops.py#L1080

    For a unimodal distribution, negative skew commonly indicates that the tail is on the left side of the distribution, 
    and positive skew indicates that the tail is on the right. In cases where one tail is long but the other tail is fat, 
    skewness does not obey a simple rule. For example, a zero value means that the tails on both sides of the mean balance out overall; 
    this is the case for a symmetric distribution, 
    but can also be true for an asymmetric distribution where one tail is long and thin, and the other is short but fat.
    """
    print("Skewness: ", round(df_col.skew(),2))
    print("Count: ", df_col.count())
    print("zeros_count: ", df_col.isin([0]).sum())
    #print("Kurtosis: ", round(df_col.kurtosis(), 2))