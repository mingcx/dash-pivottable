from numpy.core.numeric import full_like
import xlrd
import pyodbc
import urllib
import time
import pandas as pd
from pipeline_Plant_Trial.prepare import from_sheet_to_df,interval_to_string,get_abbreviation,valuecolumn_to_value_string, get_df_string_from_df,from_sheet_to_df_mutlipetime
import operator

from data import data
aaa=data
def readtrial():
    filepath_excel="SuncorWTDC_Data/ChampionX_WTDC_20220911_simplifedfordemo.xlsx"
    calculate_columns_sheetname='CalculatedColumns(RE)'
    setup_sheetname='Setup(RE)'

    sheet_df_list=[]
    header_dictionary={}

    setup_df=pd.read_excel(filepath_excel,sheet_name=setup_sheetname)


    for idx,row in setup_df.iterrows():  
        if row['RequiredColumns/Parameters']=='EB_Name_Column':
            EB_name_column=row['Excel_Column/Input']
        if row['RequiredColumns/Parameters']=='EB_Dosage_Column':
            EB_calculated_dosage_column=row['Excel_Column/Input']
        if row['RequiredColumns/Parameters']=='REB_Name_Column':
            REB_name_column=row['Excel_Column/Input']
        if row['RequiredColumns/Parameters']=='REB_Dosage_Column':
            REB_calculated_dosage_column=row['Excel_Column/Input']
        if row['RequiredColumns/Parameters']=='Time_interval':
            time_interval=row['Excel_Column/Input']
        if row['RequiredColumns/Parameters']=='Dosage_interval_count':
            try:
                dosage_interval_count=int(row['Excel_Column/Input'])+1
            except:
                dosage_interval_count=5
        if row['RequiredColumns/Parameters']=='Keyword_datetime':
            keyword_datetime=row['Excel_Column/Input']
        if row['RequiredColumns/Parameters']=='Interval_columns':
            Interval_columns_str=row['Excel_Column/Input']
        if row['RequiredColumns/Parameters']=='KPI_columns':
            KPI_columns_str=row['Excel_Column/Input']

    if Interval_columns_str:
        Interval_columns=Interval_columns_str.split("$")
    if KPI_columns_str:
        KPI_columns=KPI_columns_str.split("$")


    sheetname='Data_Main' 
    sheetdf,sheetdf_headdic=from_sheet_to_df( excelname=filepath_excel,
                                                sheetname=sheetname,
                                                skip_rows_count=0,
                                                header_rows_count=1,
                                                keyword_datetime=keyword_datetime
                                                )
    sheetdf.sort_values(keyword_datetime)
    sheet_df_list.append(sheetdf) 
    header_dictionary.update(sheetdf_headdic)

    #add sheet 
    sheetname='Data_1'
    sheetdf,sheetdf_headdic=from_sheet_to_df(   excelname=filepath_excel,
                                                sheetname=sheetname,
                                                skip_rows_count=0,
                                                header_rows_count=1,
                                                keyword_datetime=keyword_datetime
                                                )
    sheetdf.sort_values(keyword_datetime)
    sheet_df_list.append(sheetdf)
    header_dictionary.update(sheetdf_headdic)   

   #add sheet wiht multiple time
    sheetname='Data_2'
    sheetdflist=from_sheet_to_df_mutlipetime(   excelname=filepath_excel,
                                                            sheetname=sheetname,
                                                            skip_rows_count=0,
                                                            header_rows_count=1,
                                                            keyword_datetime=keyword_datetime
                                                            )
    sheet_df_list.extend(sheetdflist)  # use extend for list appending

    ######################assembly all dfs together based on date and time############################
    for idx,sheetdf in enumerate(sheet_df_list):
        sheet_df_list[idx][keyword_datetime] = pd.to_datetime(sheetdf[keyword_datetime])

    for idx,sheetdf in enumerate(sheet_df_list):
        if idx==0:
            sheet_merged_df=sheetdf
        else:
            sheetdf
            sheet_merged_df=pd.merge_asof(sheet_merged_df.sort_values(keyword_datetime), sheetdf.sort_values(keyword_datetime), on=keyword_datetime)
    sheet_merged_df.set_index(keyword_datetime, inplace=True)

    timestamps_prepare = pd.Series(pd.date_range(sheet_merged_df.index.min().floor('H'), sheet_merged_df.index.max().ceil('H'), freq=time_interval),name='times')
    sheet_merged_interval_df=pd.merge_asof(timestamps_prepare, sheet_merged_df.reset_index(), left_on='times', right_on=keyword_datetime, direction='nearest')
    sheet_merged_interval_df = sheet_merged_interval_df.drop('times', 1)  #DROP other time columns

    ######################assembly all dfs together############################

    ###############   from numerical to interval   ####################
    #sheet_merged_interval_string_df: include only converted columns
    #originaldf: include only converted columns and orginal dfs
    sheet_merged_interval_string_df,originaldf=get_df_string_from_df(df=sheet_merged_interval_df,convertcolumn=Interval_columns,exclude_columns=['Date-Time'])


    ############### unpivot KPIs    #####################
    sheet_unpivotdf=pd.melt(originaldf, id_vars=[keyword_datetime], value_vars=KPI_columns)
    sheet_int_unpivotdf = pd.merge(originaldf, sheet_unpivotdf, how="right", on=keyword_datetime)
    sheet_int_unpivotdf.rename(columns={'variable': 'KPI', 'value': 'KPI_value'}, inplace=True)


    ###############  change df to list of list  final step############
    columnname_list=sheet_int_unpivotdf.columns.tolist()
    merged_list_list=sheet_int_unpivotdf.values.tolist()
    merged_list_list.insert(0,columnname_list)


    #########################wirte to excel: debug only##################
    # writer = pd.ExcelWriter('DashExport'+'/'+'Dashoutput.xlsx')
    # sheet_merged_interval_df.to_excel(writer, sheet_name='orginal')
    # sheet_merged_interval_df.to_csv('DashExport'+'/'+'Dashout.csv')
    # sheet_merged_interval_string_df.to_csv('DashExport'+'/'+'Dashout_st_Interval.csv')
    # sheet_int_unpivotdf.to_csv('DashExport'+'/'+'finalUnpivot_int.csv')
    ########################export debug finished#########################

    keyparameters_dic={}
    keyparameters_dic['datetime']=keyword_datetime
    keyparameters_dic['EB']=EB_name_column
    keyparameters_dic['REB']=REB_name_column
    keyparameters_dic['EB_Dosage']=EB_calculated_dosage_column
    keyparameters_dic['REB_Dosage']=REB_calculated_dosage_column
    keyparameters_dic['KPI']='KPI'
    keyparameters_dic['KPI_value']='KPI_value'


    return merged_list_list,keyparameters_dic


dataa=readtrial()


#combine dataframe vertically
#https://statisticsglobe.com/combine-pandas-dataframes-vertically-horizontally-python

a=1