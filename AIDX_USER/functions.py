import pandas as pd

def read_excel_tab_to_dic(full_path=None, sheetname=None):
    df=pd.read_excel(full_path, sheet_name=sheetname)
    key_list=df[0]
    value_list=df[1]
    df_dict= dict(zip(key_list, value_list))
    return df_dict