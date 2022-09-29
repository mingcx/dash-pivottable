#from Azuredb.database import *
import pandas as pd
import numpy as np
#from Azuredb_PlantTrial.database_fromexcel import *
import xlrd
# from sqlalchemy import create_engine
# from sqlalchemy.orm import scoped_session, sessionmaker
# from sqlalchemy.ext.declarative import declarative_base
# from sqlalchemy import Table, Column, Float, Integer, String, MetaData, ForeignKey, DateTime, Boolean, sql
# from sqlalchemy.exc import IntegrityError
# from datetime import datetime
# from werkzeug.security import generate_password_hash,check_password_hash
import pyodbc
import urllib
import time
import statistics

def valuecolumn_to_value_string(value):
    try:
        asset_value=float(value)
        "{:.2f}".format(5)
        asset_value_str="{:.2f}".format(asset_value)
    except:
        asset_value=None                                #get value
        asset_value_str=str(value)                          #get value string
    return asset_value,asset_value_str

    
def get_df_string_from_df(df,convertcolumn=None,exclude_columns=None,interval_count=5):
    """Generate a string column from df column
    If the first element of column is number, return interval string
    if the first element of column is string, return the same string
    Parameters
    ----------
    df orginal, columns do not need convert, interval
    Returns
    -------
    df with all column as string
    """
    converted_data = []
    converted_columns=[]
    if convertcolumn:
        iteratecolumns=convertcolumn
    else:
        iteratecolumns=df.columns
    for column_name in iteratecolumns:
        if column_name not in exclude_columns:
            converted_columns.append(column_name)
            column_list=df[column_name].tolist()
            column_list_string=[]
            convert_to_float=True
            try:
                firstnumber=float(column_list[0])
                convert_to_float=True
            except ValueError:
                convert_to_float=False
            if convert_to_float and not pd.isnull(firstnumber): #if the column can be convert to numebr
                column_list_values=[]
                remove_none_column_list=[x for x in column_list if not pd.isnull(x)]
                column_list_ave=statistics.mean(remove_none_column_list)
                for value in column_list:
                    try:
                        convert_value=float(value)
                        if pd.isnull(convert_value):
                            convert_value=column_list_ave
                    except:
                        convert_value=column_list_ave  # if none use average data to fill in
                    column_list_values.append(convert_value)
                
                column_list_values.sort()
                data_count=len(column_list_values)
                column_list_values_sd=statistics.stdev(column_list_values)
                interval_data_count=int((data_count-1)/interval_count)
                interval_list=[]
                for index in range(1,interval_count):
                    lowlimit=column_list_values[(index-1)*interval_data_count]
                    highlimit=column_list_values[index*interval_data_count]
                    interval_list.append([lowlimit,highlimit])
                for value in column_list:
                    value_interval_string=interval_to_string(interval_list=interval_list,input_number=value,column_list_values_sd=column_list_values_sd)
                    column_list_string.append(value_interval_string)
                a=1
            else:
                for value in column_list:
                    column_list_string.append(value_interval_string)
            converted_data.append(column_list_string)
            df[column_name+'_int']=column_list_string
    converted_data=list(map(list, zip(*converted_data)))
    #get df 
    df_string = pd.DataFrame(converted_data, columns=converted_columns)   
    return df_string,df



def get_abbreviation(full_header):
    full_header_abb1="".join(e[0] for e in full_header.split())
    full_header_abb2=''.join(w[0].upper() for w in full_header.split())
    full_header_abb2 = full_header_abb2.replace(')','')
    full_header_abb2 = full_header_abb2.replace('(','')
    return full_header_abb1,full_header_abb2

def interval_to_string(interval_list,input_number,column_list_values_sd):
    find_interval=False
    for interval in interval_list:
        if input_number>=interval[0] and input_number<=interval[1]:
            find_interval=True
            if column_list_values_sd<1:
                return '{:6.2f}'.format(float(interval[0]))+' to '+ '{:6.2f}'.format(float(interval[1]))
            else:
                return '{:6.1f}'.format(float(interval[0]))+' to '+ '{:6.1f}'.format(float(interval[1]))

def from_sheet_to_df(   excelname=None,
                        sheetname=None,
                        skip_rows_count=0,
                        header_rows_count=1,
                        keyword_datetime='Date-Time'
                        ):
    
    filepath_excel=excelname
    goodread_data_xls = pd.read_excel(filepath_excel,sheet_name=sheetname,skiprows=skip_rows_count,header=None)
    goodread_data_xls_df=pd.DataFrame(goodread_data_xls)

    
    #get all pandas automtically generated columns
    ahead_caption="startcells"
    cols = goodread_data_xls_df.columns
    top_df_header= goodread_data_xls_df.head(header_rows_count) 



    # header process
    for column in goodread_data_xls_df.head(header_rows_count):
        copyhead=None
        for index in range (header_rows_count):
            if not pd.isnull(goodread_data_xls_df[column][index]):
                copyhead=goodread_data_xls_df[column][index]
            else:
                if copyhead:
                    goodread_data_xls_df[column][index]=copyhead

    for index, row in goodread_data_xls_df.head(header_rows_count).iterrows():
        for column in cols:
            cellvalue=row[column]
            if not pd.isnull(cellvalue):
                ahead_caption=cellvalue
            if ahead_caption != "startcells":
                if pd.isnull(row[column]):
                    row[column]=ahead_caption

    top_df= goodread_data_xls_df.head(header_rows_count) 


    header_dictionary={}
    full_header_list=[]
    full_header_abb1_list=[]
    full_header_abb2_list=[]

    for column in cols:
        column_list=top_df[column].tolist()
        #if not pd.isnull(column_list[0]):
            #three item list: keyword, asset, kpi
        if pd.isnull(column_list[0]):
            column_list[0]='C'
        keyword=column_list[0]
        full_header=column_list[0]
        for index in range (1,header_rows_count):
            if not pd.isnull(column_list[index]):
                strrr=column_list[index]
            else:
                strrr='NA'
            
            # if two rows the same or from merged cells, do not replicate
            if full_header!=strrr:
                full_header=full_header+' '+strrr

        # if header_rows_count> asset_monitor_rows_count:
        #     kpi_name=column_list[asset_monitor_rows_count]
        # # get asset
        # for index in range (1,asset_monitor_rows_count):
        #     if column_list[index] != column_list[index-1]:
        #         asset_name=asset_name+' '+column_list[index]

        
        full_header_abb1="".join(e[0] for e in full_header.split())
        full_header_abb2=''.join(w[0].upper() for w in full_header.split())
        full_header_abb2 = full_header_abb2.replace(')','')
        full_header_abb2 = full_header_abb2.replace('(','')
        if keyword_datetime:
            if keyword_datetime in full_header:
                full_header=keyword_datetime
                full_header_abb2=keyword_datetime
                full_header_abb1=keyword_datetime
     
        
        # if duplicated column names
        if full_header in header_dictionary.keys():
            # raise ValueError('duplicated columns')
            asset_name=full_header
            asset_name=asset_name+'_2'
            full_header=asset_name
            if full_header in header_dictionary.keys():
                raise ValueError('duplicated columns')
            else:
                header_dictionary[full_header] = [keyword,full_header_abb1,full_header_abb2,sheetname]
        else:
            header_dictionary[full_header] = [keyword,full_header_abb1,full_header_abb2,sheetname]
        
        

        full_header_list.append(full_header)
        full_header_abb1_list.append(full_header_abb1)
        full_header_abb2_list.append(full_header_abb2)


    full_header_df = goodread_data_xls_df.iloc[header_rows_count:]
    full_header_df.columns=full_header_list
    return full_header_df,header_dictionary



def from_sheet_to_df_mutlipetime(   excelname=None,
                                    sheetname=None,
                                    skip_rows_count=0,
                                    header_rows_count=1,
                                    keyword_datetime='Date-Time'
                                ):
    filepath_excel=excelname
    #goodread_data_xls = pd.read_excel(filepath_excel,sheet_name=sheetname,skiprows=skip_rows_count,header=None)
    goodread_data_xls = pd.read_excel(filepath_excel,sheet_name=sheetname,skiprows=skip_rows_count,header=None)
    goodread_data_xls_df=pd.DataFrame(goodread_data_xls)
    columncount=len(goodread_data_xls_df.columns) 
    columnslist=goodread_data_xls_df.iloc[0].tolist()
    keywordcount=0
    startcolumn_list=[]
    finishcolumn_list=[]
    withoutcolumnrow_df= goodread_data_xls_df.iloc[1: , :]
    full_column_list=goodread_data_xls_df.columns.to_list()
    dataframecount=0
    split_df_list=[]

    for idx, column in enumerate(columnslist): 
           
        if column==keyword_datetime:
            if idx==0:
                startcolumn_list.append(idx)
                kpicolumn_names=[keyword_datetime]   
                kpicolumn_inxs=[idx]
            else:
                finishcolumn_list.append(idx-1)
                startcolumn_list.append(idx)
                splitdf=withoutcolumnrow_df[kpicolumn_inxs].copy()
                splitdf.columns=kpicolumn_names
                splitdf[keyword_datetime].replace('', np.nan, inplace=True)
                splitdf[keyword_datetime].replace(' ', np.nan, inplace=True)
                splitdf[keyword_datetime].replace('  ', np.nan, inplace=True)
                splitdf[keyword_datetime].replace('   ', np.nan, inplace=True)
                splitdf.dropna(subset=[keyword_datetime], inplace=True)
                #splitdf.sort_values(keyword_datetime)
                split_df_list.append(splitdf)
                a=1
                #restrat next df
                kpicolumn_names=[keyword_datetime]
                kpicolumn_inxs=[idx]   
        else:
            kpicolumn_names.append(column)
            kpicolumn_inxs.append(idx)
    
    #this is for the last dataframe out of loop
    finishcolumn_list.append(columncount-1)
    splitdf=withoutcolumnrow_df[kpicolumn_inxs].copy()
    splitdf.columns=kpicolumn_names

    if keyword_datetime:
        splitdf[keyword_datetime].replace('', np.nan, inplace=True)
        splitdf.dropna(subset=[keyword_datetime], inplace=True)


    split_df_list.append(splitdf)

    return split_df_list
            
    aa=1

    # split_df_list=[]
    # for columnindex in range(1,columncount):
    #     columns_list=goodread_data_xls_df.columns
    #     column_name=goodread_data_xls_df.columns[columnindex]
    #     a=1
    #     if goodread_data_xls_df.columns[columnindex]==keyword_datetime:
    #         split_df_list.append(columnindex)
    

    # date_timeloc=goodread_data_xls_df.columns.get_loc(keyword_datetime)
    # a=1