from numpy.core.numeric import full_like
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
import pandas as pd
from pipeline_Plant_Trial.prepare import from_sheet_to_df,interval_to_string,get_abbreviation,valuecolumn_to_value_string, get_df_string_from_df
import operator



ops = {
    '+' : operator.add,
    '-' : operator.sub,
    '*' : operator.mul,
    '/' : operator.truediv,  # use operator.div for Python 2
    '%' : operator.mod,
    '^' : operator.xor,
}


filepath_excel="WTDC_Data_Exported2.xlsx"
project_name='SUFB_WTDC_2022'
calculate_columns_sheetname='CalculatedColumns(RE)'
setup_sheetname='Setup(RE)'





#read excel
excelfile=pd.ExcelFile(filepath_excel)
xls_sheets=excelfile.sheet_names
#df = pd.read_excel(filepath_excel, sheet_name = sheetname)


#read new column setup
columnsetup_df=pd.read_excel(filepath_excel,sheet_name=calculate_columns_sheetname)
setup_df=pd.read_excel(filepath_excel,sheet_name=setup_sheetname)

sheet_df_list=[]
header_dictionary={}
#column_sheet_dictionary={}
#get all setup from Required_columns_sheetname


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

#add sheet 
sheetname='Process Data'   
sheetdf,sheetdf_headdic=from_sheet_to_df( excelname=filepath_excel,
                                            sheetname=sheetname,
                                            skip_rows_count=0,
                                            header_rows_count=1,
                                            keyword_datetime=keyword_datetime
                                            )
sheet_df_list.append(sheetdf) 
header_dictionary.update(sheetdf_headdic)
#add sheet finished     

#add sheet 
sheetname='Test Results(CX)'
sheetdf,sheetdf_headdic=from_sheet_to_df(   excelname=filepath_excel,
                                            sheetname=sheetname,
                                            skip_rows_count=5,
                                            header_rows_count=4,
                                            keyword_datetime=keyword_datetime
                                            )
sheet_df_list.append(sheetdf)
header_dictionary.update(sheetdf_headdic)     
#add sheet finished                        

#add sheet 
sheetname='Lab Results'
sheetdf,sheetdf_headdic=from_sheet_to_df(   excelname=filepath_excel,
                                            sheetname=sheetname,
                                            skip_rows_count=0,
                                            header_rows_count=1,
                                            keyword_datetime=keyword_datetime
                                            )
sheet_df_list.append(sheetdf)
header_dictionary.update(sheetdf_headdic)     
#add sheet finished     

#add sheet 
sheetname='Chemical'
sheetdf,sheetdf_headdic=from_sheet_to_df(   excelname=filepath_excel,
                                            sheetname=sheetname,
                                            skip_rows_count=0,
                                            header_rows_count=1,
                                            keyword_datetime=keyword_datetime
                                            )
sheet_df_list.append(sheetdf)   
header_dictionary.update(sheetdf_headdic)
#add sheet finished

#assemble#####################################################################
for idx,sheetdf in enumerate(sheet_df_list):
    sheet_df_list[idx][keyword_datetime] = pd.to_datetime(sheetdf[keyword_datetime])

for idx,sheetdf in enumerate(sheet_df_list):
    if idx==0:
        sheet_merged_df=sheetdf

    else:
        sheet_merged_df=pd.merge_asof(sheet_merged_df, sheetdf, on=keyword_datetime)

sheet_merged_df.set_index(keyword_datetime, inplace=True)

timestamps_prepare = pd.Series(pd.date_range(sheet_merged_df.index.min().floor('H'), sheet_merged_df.index.max().ceil('H'), freq=time_interval),name='times')
sheet_merged_interval_df=pd.merge_asof(timestamps_prepare, sheet_merged_df.reset_index(), left_on='times', right_on=keyword_datetime, direction='nearest')
sheet_merged_interval_df = sheet_merged_interval_df.drop('times', 1)  #DROP other time columns

#assemble  finished #####################################################################

#process special columns###################################################################

for idx,row in columnsetup_df.iterrows():  
    newcolumn_name=row['NewColumnName']
    sheet_name=row['ColumnType']
    full_header_abb1="".join(e[0] for e in newcolumn_name.split())
    full_header_abb2=''.join(w[0].upper() for w in newcolumn_name.split())
    header_dictionary[newcolumn_name]=['C',full_header_abb1,full_header_abb2,sheet_name]
    column1_name=row['Column1']
    column2_name=row['Column2']

    #caulcuate new column and add to dataframe
    try:
        Multiply_Constant=float(row['Multiply_Constant'])
    except:
        Multiply_Constant=1
    C1_C2_Operation=row['C1_C2_Operation']
    new_column_list=[]
    for idx2,row2 in sheet_merged_interval_df.iterrows():
        try:
            column1_value=float(row2[column1_name])
        except:
            column1_value=None
        try:
            column2_value=float(row2[column2_name])
        except:
            column2_value=1
        if column1_value: # if column 1 value is not none or cannot convert to float
            new_column_value=ops[C1_C2_Operation](column1_value,column2_value)*Multiply_Constant
        else:
            new_column_value=None
        new_column_list.append(new_column_value)
    sheet_merged_interval_df[newcolumn_name]=new_column_list


#get string_df
sheet_merged_interval_string_df=get_df_string_from_df(df=sheet_merged_interval_df,exclude_columns=['Date-Time'])

#original data
orginal_df_list_list=[]

#demo data
demo_column_list=['record_id','date_dateall','sheet','KPI','KPI_short','KPI_value','KPI_valuestr','KPI_range']
demo_sheets=['Lab Results','Test Results(CX)']
demo_df_list_list=[]
#process data
process_column_list=['record_id','date_dateall','sheet','process','process_short','process_value','process_vstr','process_range']
process_sheets=['Process Data']
process_df_list_list=[]
#condition data
condition_column_list=['record_id','date_dateall','sheet','adjustment_legend','adjustment_str_legend','adjustment_value','adjustment_valuestr']
condition_sheets=['Chemical']
condi_df_list_list=[]


record_id_int=0
for index, row in sheet_merged_interval_df.iterrows():
    if not pd.isnull(row[keyword_datetime]):
        
        record_id_int=record_id_int+1
        record_id=project_name+'_'+format(record_id_int, '06d')
        date_dateall=row[keyword_datetime]
        orginal_df_column_list=['record_id','date_dateall']
        original_row_list=[]
        original_row_list.append(record_id)
        original_row_list.append(date_dateall)
        


        #get EB and REB for condition:
        EB_name=row[EB_name_column]
        EB_dosage=row[EB_calculated_dosage_column]
        REB_name=row[REB_name_column]
        REB_dosage=row[REB_calculated_dosage_column]

        EB_dosage_interval_string=sheet_merged_interval_string_df.iloc[index][EB_calculated_dosage_column]
        REB_dosage_interval_string=sheet_merged_interval_string_df.iloc[index][REB_calculated_dosage_column]


        # EB_dosage_value,EB_dosage_string=valuecolumn_to_value_string(EB_dosage)

        # REB_dosage_value,REB_dosage_string=valuecolumn_to_value_string(REB_dosage)

        # EB_dosage_interval_string=interval_to_string(interval_list=eb_dosage_interval_list,input_number=EB_dosage_value)
        # REB_dosage_interval_string=interval_to_string(interval_list=reb_dosage_interval_list,input_number=REB_dosage_value)
        
        #select
        condition_row_list=[]
        condition_row_list.append(record_id)
        condition_row_list.append(date_dateall)
        condition_row_list.append('Chemical')
        condition_row_list.append(' Select')
        condition_row_list.append(' Select')
        condition_row_list.append(None)
        condition_row_list.append(None)
        condi_df_list_list.append(condition_row_list)
        
        #EB EB_value
        if (not pd.isnull(EB_name)) and (not pd.isnull(EB_dosage)):
            condition_row_list=[]
            condition_row_list.append(record_id)
            condition_row_list.append(date_dateall)
            condition_row_list.append('Chemical')
            condition_row_list.append('EBppm')
            condition_row_list.append('EB')
            condition_row_list.append(EB_dosage)
            condition_row_list.append(EB_name)
            condi_df_list_list.append(condition_row_list)

            #EBinverval EB_value
            condition_row_list=[]
            condition_row_list.append(record_id)
            condition_row_list.append(date_dateall)
            condition_row_list.append('Chemical')
            condition_row_list.append('EBppm')
            condition_row_list.append('EBppm')
            condition_row_list.append(EB_dosage)
            condition_row_list.append(EB_dosage_interval_string)
            condi_df_list_list.append(condition_row_list)
            
            #EB@inverval EB_value
            condition_row_list=[]
            condition_row_list.append(record_id)
            condition_row_list.append(date_dateall)
            condition_row_list.append('Chemical')
            condition_row_list.append('EBppm')
            condition_row_list.append('EB@ppm')
            condition_row_list.append(EB_dosage_interval_string)
            if EB_dosage_interval_string:
                condition_row_list.append(EB_name+'@'+EB_dosage_interval_string)
            else:
                condition_row_list.append(EB_name+'@'+'outliers')
            condi_df_list_list.append(condition_row_list)

        #REB REB_value
        if (not pd.isnull(REB_name)) and (not pd.isnull(REB_dosage)):
            condition_row_list=[]
            condition_row_list.append(record_id)
            condition_row_list.append(date_dateall)
            condition_row_list.append('Chemical')
            condition_row_list.append('REBppm')
            condition_row_list.append('REB')
            condition_row_list.append(REB_dosage)
            condition_row_list.append(REB_name)
            condi_df_list_list.append(condition_row_list)

            

            #REBinverval REB_value
            condition_row_list=[]
            condition_row_list.append(record_id)
            condition_row_list.append(date_dateall)
            condition_row_list.append('Chemical')
            condition_row_list.append('REBppm')
            condition_row_list.append('REBppm')
            condition_row_list.append(REB_dosage)
            condition_row_list.append(REB_dosage_interval_string)
            condi_df_list_list.append(condition_row_list)
            
            #REB@inverval REB_value
            condition_row_list=[]
            condition_row_list.append(record_id)
            condition_row_list.append(date_dateall)
            condition_row_list.append('Chemical')
            condition_row_list.append('REBppm')
            condition_row_list.append('REB@ppm')
            condition_row_list.append(REB_dosage)
            if REB_dosage_interval_string:
                condition_row_list.append(REB_name+'@'+REB_dosage_interval_string)
            else:
                condition_row_list.append(REB_name+'@'+'outliers')
            condi_df_list_list.append(condition_row_list)



        for column_name in sheet_merged_interval_df.columns:
            original_row_list.append(row[column_name])  #for orginal
            orginal_df_column_list.append(column_name)


            # process data
            sheetname=header_dictionary[column_name][3]  # no 3 is the sheet name
            column_short=header_dictionary[column_name][2] # no 2 is the abbreviation2
            try:
                asset_value=float(row[column_name])
                "{:.2f}".format(5)
                asset_value_str="Range"+"{:.2f}".format(asset_value)
                #asset_value_str='hold'
            except:
                asset_value=None                                #get value
                asset_value_str="Range"+str(asset_value)                          #get value string
                #asset_value_str='hold'
            
            # process data
            if sheetname in process_sheets:   
                row_list=[]
                row_list.append(record_id)
                row_list.append(date_dateall)
                row_list.append(sheetname)              #sheetname
                row_list.append(column_name)            #value
                row_list.append(column_short)
                row_list.append(asset_value)
                row_list.append(asset_value_str)
                row_list.append(None)
                process_df_list_list.append(row_list)

            # demo data
            if sheetname in demo_sheets:   # no 3 is the sheet name
                row_list=[]
                row_list.append(record_id)
                row_list.append(date_dateall)
                row_list.append(sheetname)              #sheetname
                row_list.append(column_name)            #value
                row_list.append(column_short)
                row_list.append(asset_value)
                row_list.append(asset_value_str)
                row_list.append(None)                   # range string, empty for now
                demo_df_list_list.append(row_list)

                        # process data

            # #add select for two data
            # if sheetname in process_sheets:   
            #     row_list=[]
            #     row_list.append(record_id)
            #     row_list.append(date_dateall)
            #     row_list.append(sheetname)              #sheetname
            #     row_list.append(' Select')            #value
            #     row_list.append(' Select')
            #     row_list.append(None)
            #     row_list.append("")
            #     row_list.append(None)
            #     process_df_list_list.append(row_list)

            #             # demo data
            # if sheetname in demo_sheets:   # no 3 is the sheet name
            #     row_list=[]
            #     row_list.append(record_id)
            #     row_list.append(date_dateall)
            #     row_list.append(sheetname)              #sheetname
            #     row_list.append(' Select')            #value
            #     row_list.append(' Select')
            #     row_list.append(None)
            #     row_list.append("")
            #     row_list.append(None)                   # range string, empty for now
            #     demo_df_list_list.append(row_list)

        orginal_df_list_list.append(original_row_list)
            

aaa=process_df_list_list

#add column names
condtion_table_df = pd.DataFrame(condi_df_list_list, columns=condition_column_list)
demo_table_df=pd.DataFrame(demo_df_list_list, columns=demo_column_list)  
process_df=pd.DataFrame(process_df_list_list, columns=process_column_list)  
orginal_df=pd.DataFrame(orginal_df_list_list, columns=orginal_df_column_list) 
#export 
writer = pd.ExcelWriter('Excel_PowerBI'+'\\'+project_name+'.xlsx')
orginal_df.to_excel(writer, sheet_name='orginal')
condtion_table_df.to_excel(writer, sheet_name='condition')
demo_table_df.to_excel(writer, sheet_name='demo')
process_df.to_excel(writer, sheet_name='process')

writer.save()


a=1


