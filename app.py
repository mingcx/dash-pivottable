import dash
from dash.dependencies import Input, Output
from dash import Dash, dcc, html, Input, Output, dash_table, no_update  # Dash version >= 2.0.0
import dash_bootstrap_components as dbc
import plotly.express as px
import dash_pivottable
from data import data
from flask import Flask, url_for, send_file, send_from_directory, redirect
from flask import render_template
from dash import html
import flask_login
from AIDX_USER.database_connect import AzureDB_AIDX_user, db_session, Users, User_access
from flask import request
from read_trail_df import readtrial
from read_test_df import readtest
import numpy as np
import pandas as pd

server = Flask(__name__)
server.secret_key = 'minglogin'  # Change this!

#####login and logout setup#################################

#login prepare
login_manager = flask_login.LoginManager()
login_manager.init_app(server)

db_session.close() 
session = db_session()
session.expire_all()
db_users = session.query(Users).all()
db_user_email_list = [db_user.useremail for db_user in db_users]
user_email = None

tabs_styles = {
    'height': '44px',
}
tab_style = {
    'borderBottom': '1px solid #d6d6d6',
    'padding': '6px',
    'fontWeight': 'bold'
}

tab_selected_style = {
    'borderTop': '1px solid #d6d6d6',
    'borderBottom': '1px solid #d6d6d6',
    'backgroundColor': '#3A5962',
    'color': 'white',
    'padding': '6px'
}

class Flask_Login_User(flask_login.UserMixin):
    pass


@login_manager.user_loader
def user_loader(email):
    email = str(email).lower()
    if email not in db_user_email_list:
        return
    flask_user = Flask_Login_User()
    flask_user.id = email
    return flask_user



@login_manager.request_loader
def request_loader(request):
    email = request.form.get('email')
    email = str(email).lower()
    if email not in db_user_email_list:
        return
    flask_user = Flask_Login_User()
    flask_user.id = email
    return flask_user

@login_manager.unauthorized_handler
def unauthorized_handler():
    return redirect(url_for('login'))


@server.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    if request.method == 'POST':
        email = request.form['upload_email']
        email = str(email).lower()
        password = request.form['upload_password']

        azureDB_AIDX_user=AzureDB_AIDX_user()

        #check user first
        usercheck=azureDB_AIDX_user.user_password_check(   useremail=email,
                                                           password=password)

        if usercheck == "nouser" or usercheck == "unmatch":
            return render_template('message_case.html', output_case=usercheck)
        else:
            accesscheck=azureDB_AIDX_user.check_access( useremail=email,
                                                        access_platform='FC',
                                                        access_level='all')
            if accesscheck:
                user = Flask_Login_User()
                user.id = email
                flask_login.login_user(user)
                return redirect(url_for('index'))
            else:
                return render_template('message_case.html', output_case='no field chemical access')

            

        #check result: "nouser", "match" or "unmatch"
        if check_result == "nouser" or check_result == "unmatch":
            return render_template('message_case.html', output_case=check_result)
        else:
            user = Flask_Login_User()
            user.id = email
            flask_login.login_user(user)
            return redirect(url_for('index'))

@server.route('/logout')
def logout():
    flask_login.logout_user()
    return render_template('message_case.html', output_case='logout')


#####login and logout setup####################


@server.route('/')
@flask_login.login_required
def index():
    return render_template('index.html')


@server.route("/222")
@flask_login.login_required
def home2():
    return "Hello, Flask!2"



@server.route("/444")
@flask_login.login_required
def dash111():
    return "Hello, Flask!2"
    #return redirect("/dashpivot/")
    #app = dash.Dash(__name__)


####################first dash board###########################################3
app= dash.Dash(server=server, url_base_pathname="/dashpivot/")
app.title = 'My Dash example'

#server = app.server
data2,keyparameters_dic=readtrial()
app.layout = html.Div([
    dash_pivottable.PivotTable(
        id='table',
        #data=data,
        data=data2,
        cols=[keyparameters_dic['datetime']],
        colOrder="key_a_to_z",
        rows=[keyparameters_dic['KPI']],
        rowOrder="key_a_to_z",
        rendererName="Grouped Column Chart",
        aggregatorName="Average",
        vals=[keyparameters_dic['KPI_value']],
        hiddenAttributes=['Table'],
        hiddenFromAggregators=['First']
        #valueFilter={'Day of Week': {'Thursday': False}}
    ),
    # html.Div(
    #     id='output'
    # )
    html.Div(id="container",children=[   
        dash_pivottable.PivotTable(
        id='table2',
        #data=data,
        data=data2,
        cols=[keyparameters_dic['datetime']],
        colOrder="key_a_to_z",
        rows=[keyparameters_dic['KPI']],
        rowOrder="key_a_to_z",
        rendererName="Grouped Column Chart",
        aggregatorName="Average",
        vals=[keyparameters_dic['KPI_value']],
        hiddenAttributes=['Table'],
        hiddenFromAggregators=['First']
        #valueFilter={'Day of Week': {'Thursday': False}}
    )])
])

# app.config = {
#     'displaylogo': False
# }


@app.callback(Output('output', 'children'),
            [Input('table', 'cols'),
            Input('table', 'rows'),
            Input('table', 'rowOrder'),
            Input('table', 'colOrder'),
            Input('table', 'aggregatorName'),
            Input('table', 'rendererName')])
def display_props(cols, rows, row_order, col_order, aggregator, renderer):
    return [
        html.P(str(cols), id='columns'),
        html.P(str(rows), id='rows'),
        html.P(str(row_order), id='row_order'),
        html.P(str(col_order), id='col_order'),
        html.P(str(aggregator), id='aggregator'),
        html.P(str(renderer), id='renderer'),
    ]

####################first dash board finished###########################################3


####################second dash board###########################################3

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']


#app2 = Dash(__name__, server=server,external_stylesheets=external_stylesheets,url_base_pathname="/dashpivot2/")
app2 = Dash(__name__, server=server,url_base_pathname="/dashpivot2/")
app2.title = 'AID-X Octopus'

# #df = px.data.gapminder()
# df["id"] = df.index
# # print(df.head(15))
# dff = df[df.year == 2007]
# columns = ["country", "continent", "lifeExp", "pop", "gdpPercap"]
# color = {"lifeExp": "#636EFA", "pop": "#EF553B", "gdpPercap": "#00CC96"}

dff, defaultshow_columns, setup_identifier_columns,setup_condition_columns,KPI_columns, setup_product_dosage_dic=readtest()



#initial_active_cell = {"row": 0, "column": 0, "column_id": "country", "row_id": 0}


finallist=[]



######################generate width based on filter items, not used for now###########################
# sheetlist_lengh=sum(len(s) for s in dff[setup_identifier_columns[0]].unique())
# sheetlist_margin_lengh=len(dff[setup_identifier_columns[0]].unique())
# identifierlist_length=sum(len(s) for s in dff[setup_identifier_columns[1]].unique())
# identifierlist_margin_lengh=len(dff[setup_identifier_columns[0]].unique())
# totallengh=sheetlist_lengh*2+sheetlist_margin_lengh*2+identifierlist_length+identifierlist_margin_lengh*2
# sheetlist_ratio_string="{0:.0%}".format((sheetlist_lengh*2+sheetlist_margin_lengh*2)/totallengh)
# identifier_ratio_string="{0:.0%}".format((identifierlist_length+identifierlist_margin_lengh*2)/totallengh)



##############################################first line filter#############################################################
filterrow1_list=[]
filterrow1_list.append(html.Div([
        html.Div([
            html.Div([html.Label(setup_identifier_columns[0])],style={'font-family':'Garamond','font-size': '18px', 'width': '50%', 'display': 'inline-block', 'margin-bottom': '7px', 'height':'20px', 'verticalAlign': 'top'}),
            html.Div([dcc.Checklist(['All'],id='sheet_all_check')],style={'font-family':'Garamond', 'font-size': '18px', 'width': '35%', 'display': 'inline-block', 'margin-bottom': '7px', 'height':'20px', 'verticalAlign': 'top'})
            ]),
        dcc.Dropdown( 
            options=dff[setup_identifier_columns[0]].unique(),
            value=[],
            multi=True,
            id='filter_sheet'
        )
        ],style={'width': '30%', 'display': 'inline-block','margin-right': '1%',"vertical-align":"bottom"}
        ))

filterrow1_list.append(html.Div([
        html.Div([
            html.Div([html.Label(setup_identifier_columns[1])],style={'font-size': '16px', 'width': '30%', 'display': 'inline-block', 'margin-bottom': '7px', 'height':'20px', 'verticalAlign': 'top'}),
            html.Div([dcc.Checklist(['All'],id='identifier_all_check')],style={'font-size': '14px', 'width': '65%', 'display': 'inline-block', 'margin-bottom': '7px', 'height':'20px', 'verticalAlign': 'top'})
            ]),
        dcc.Dropdown(
            #options=np.insert(dff[setup_identifier_columns[1]].unique(),0,'All'),  
            options=dff[setup_identifier_columns[1]].unique(),
            value=[],
            multi=True,
            id='filter_identifier'
        )
        ],style={'width': '65%', 'display': 'inline-block',"vertical-align":"bottom"}
        ))

finallist.append(html.Div(filterrow1_list,style={'width': '96%', 'display': 'inline-block',"margin": 10}))

##############################################first line filter finished#############################################################



##############################################second line filter#############################################################
filterrow2_list=[]
first_chemical_column=list(setup_product_dosage_dic.keys())[0]
second_chemical_column=list(setup_product_dosage_dic.keys())[1]
filterrow2_list.append(html.Div([
        html.Div([
            html.Div([html.Label(first_chemical_column)],style={'font-family':'Garamond','font-size': '18px', 'width': '50%', 'display': 'inline-block', 'margin-bottom': '7px', 'height':'20px', 'verticalAlign': 'top'}),
            html.Div([dcc.Checklist(['All'],id='chemical_1_check')],style={'font-family':'Garamond', 'font-size': '18px', 'width': '35%', 'display': 'inline-block', 'margin-bottom': '7px', 'height':'20px', 'verticalAlign': 'top'})
            ]),
        dcc.Dropdown( 
            options=dff[first_chemical_column].unique(),
            value=[],
            multi=True,
            id='chemical_1_filter'
        )
        ],style={'width': '30%', 'display': 'inline-block','margin-right': '1%',"vertical-align":"bottom"}
        ))

filterrow2_list.append(html.Div([
        html.Div([
            html.Div([html.Label(second_chemical_column)],style={'font-size': '16px', 'width': '30%', 'display': 'inline-block', 'margin-bottom': '7px', 'height':'20px', 'verticalAlign': 'top'}),
            html.Div([dcc.Checklist(['All'],id='chemical_2_check')],style={'font-size': '14px', 'width': '65%', 'display': 'inline-block', 'margin-bottom': '7px', 'height':'20px', 'verticalAlign': 'top'})
            ]),
        dcc.Dropdown(
            #options=np.insert(dff[setup_identifier_columns[1]].unique(),0,'All'),  
            options=dff[second_chemical_column].unique(),
            value=[],
            multi=True,
            id='chemical-2-filter'
        )
        ],style={'width': '65%', 'display': 'inline-block',"vertical-align":"bottom"}
        ))

finallist.append(html.Div(filterrow2_list,style={'width': '96%', 'display': 'inline-block',"margin": 10}))

##############################################second line filter finished#############################################################



finallist.append(        html.Div(
            [
                dash_table.DataTable(
                    id="raw_data_table",
                    columns=[{"name": c, "id": c} for c in defaultshow_columns],
                    data=dff.to_dict("records"),
                    editable=False,
                    filter_action="native",
                    sort_mode="multi",
                    column_selectable="single",
                    row_selectable="multi",
                    row_deletable=True,
                    selected_columns=[],
                    selected_rows=[],
                    page_action="native",
                    page_current= 0,
                    page_size=15,
                    sort_action="native",
                    #active_cell=initial_active_cell,
                ),
            ],
            style={'width': '95%', 'display': 'inline-block',"margin": 10}
            #style={"margin": 50},
            #className="ten columns"
        ))

finallist.append(dbc.Alert(id='tbl_out'))

finallist.append(html.Div([
            dcc.Tabs(id="tabs-styled-with-inline", value='tab-1', children=[
                dcc.Tab(label='Data Analytics', value='analytics_tab', style=tab_style, selected_style=tab_selected_style),
                dcc.Tab(label='Graph', value='graph_tab', style=tab_style, selected_style=tab_selected_style),
                dcc.Tab(label='Chemisty', value='chemisty_tab', style=tab_style, selected_style=tab_selected_style),
                dcc.Tab(label='Sales/Supply', value='SS_tab', style=tab_style, selected_style=tab_selected_style),
                dcc.Tab(label='Machine Learning', value='AI_tab', style=tab_style, selected_style=tab_selected_style),
            ], style=tabs_styles),
            html.Div(id='tabs-content-inline')
        ],
        #style={'width': '90%', 'display': 'inline-block',"margin": 10}
        ))


###################append tab contant, which will be determined by call backs######################
#finallist.append(html.Div(id="container", children=[], className="mt-4"))
finallist.append(html.Div(id="container"))

###################put all parts together#######################################################3
#app2.layout = html.Div(finallist,className="row")
app2.layout = html.Div(finallist)
####################################################Layout finished######################################
####################################################Layout finished######################################
####################################################Layout finished######################################
####################################################Layout finished######################################
####################################################Layout finished######################################
####################################################Layout finished######################################




##################################container###############################
@app2.callback(
    #Output("output-graph", "children"), Input("table", "active_cell"),
    Output('container', 'children'), 
    Input('raw_data_table', 'active_cell'),
    Input('raw_data_table', 'data'),
    Input('tabs-styled-with-inline','value'))
def render_content(activecell,filtered_data,selectedtab):
    print(selectedtab)
    #print(filtered_data)

    if selectedtab == 'analytics_tab':
        ############### unpivot KPIs    #####################
        filtered_dataframe=pd.DataFrame(filtered_data)
        filtered_dataframe['uniqueID']=filtered_dataframe.index
        sheet_unpivotdf=pd.melt(filtered_dataframe, id_vars=['uniqueID'], value_vars=KPI_columns)
        sheet_int_unpivotdf = pd.merge(filtered_dataframe, sheet_unpivotdf, how="right", on='uniqueID')
        sheet_int_unpivotdf.rename(columns={'variable': 'KPI', 'value': 'KPI_value'}, inplace=True)

        ##################to list of list
        columnname_list=sheet_int_unpivotdf.columns.tolist()
        merged_list_list=sheet_int_unpivotdf.values.tolist()
        merged_list_list.insert(0,columnname_list)
        #######################################
        # filtered_dataframe=pd.DataFrame(filtered_data)
        # # table = pd.pivot_table(filtered_dataframe, values=KPI_columns, index=['Coag', 'Coag_Dosage (ppm)'],
        # #             aggfunc={KPI_columns[0]: np.mean,
        # #                      KPI_columns[1]: [min, max, np.mean]})

        # table2 = pd.pivot_table(filtered_dataframe, values=KPI_columns, index=['Coag', 'Coag_Dosage (ppm)'])
        # table2 = pd.pivot_table(filtered_dataframe, values=KPI_columns, index=['Coag'])
        # aaa_df=table2.reset_index()
        # print(aaa_df)
        firstchemcialfromchemicaldic=list(setup_product_dosage_dic)[0]
        firstdosagefromchemicaldic=setup_product_dosage_dic[firstchemcialfromchemicaldic]

        return html.Div(
            [
                dash_pivottable.PivotTable(
                    id='filtered_pivot_table',
                    #data=data,
                    data=merged_list_list,
                    cols=[keyparameters_dic['KPI']],
                    colOrder="key_a_to_z",
                    rows=[firstchemcialfromchemicaldic,firstdosagefromchemicaldic],
                    rowOrder="key_a_to_z",
                    rendererName="Table",
                    aggregatorName="Average",
                    vals=[keyparameters_dic['KPI_value']],
                    hiddenAttributes=['Table'],
                    hiddenFromAggregators=['First']
                    #valueFilter={'Day of Week': {'Thursday': False}}
                )
                # dash_pivottable.PivotTable(
                #     id='table',
                #     #data=data,
                #     data=data2,
                #     cols=[keyparameters_dic['datetime']],
                #     colOrder="key_a_to_z",
                #     rows=[keyparameters_dic['KPI']],
                #     rowOrder="key_a_to_z",
                #     rendererName="Grouped Column Chart",
                #     aggregatorName="Average",
                #     vals=[keyparameters_dic['KPI_value']],
                #     hiddenAttributes=['Table'],
                #     hiddenFromAggregators=['First']
                #     #valueFilter={'Day of Week': {'Thursday': False}}
                # )
            ],
            style={'width': '90%', 'display': 'inline-block',"margin": 10}
        )

    elif selectedtab == 'graph_tab':
        print('enter graph')
        return html.Div([
            html.H3('Tab content 2'),
            dcc.Graph(
                figure=dict(
                    data=[dict(
                        x=[1, 2, 3],
                        y=[5, 10, 6],
                        type='bar'
                    )]
                )
            )
        ])
    elif selectedtab == 'chemisty_tab':
         return html.Div([
            html.H3('Tab content 1'),
            dcc.Graph(
                figure=dict(
                    data=[dict(
                        x=[1, 2, 3],
                        y=[3, 1, 2],
                        type='bar'
                    )]
                )
            )
        ])   





#################################active cell call back
@app2.callback(
    #Output("output-graph", "children"), Input("table", "active_cell"),
    Output('tbl_out', 'children'), 
    Input('raw_data_table', 'active_cell'),
    Input('raw_data_table', 'data'),
)
def cell_clicked(active_cell,currentdata):
    if active_cell:
        cell_content=pd.DataFrame(currentdata).iloc[active_cell['row']][active_cell['column_id']]
    #cell_content=pd.DataFrame(currentdata).iat[active_cell['row'], active_cell['column']]
    return str(active_cell)+str(cell_content) if active_cell else "Click the table"



# ###########identifier filter for filters ################################## 
@app2.callback(
    #Output("output-graph", "children"), Input("table", "active_cell"),
    Output('filter_identifier', 'options'), 
    #Output('filter_identifier', 'value'),
    Input('filter_sheet', 'value')
)
def sheet_filter_to_pageidentifier(selectedsheets_list):
    if selectedsheets_list:
        filterdf_fromsheet=dff[dff[setup_identifier_columns[0]].isin(selectedsheets_list)]  
        return filterdf_fromsheet[setup_identifier_columns[1]].unique()
    else:
        return dff[setup_identifier_columns[1]].unique()

# ###########filter for filters finished ################################## 



# ###########check all identifiers ################################## 
@app2.callback(
    #Output("output-graph", "children"), Input("table", "active_cell"),
    Output('filter_identifier', 'value'), 
    #Output('filter_identifier', 'value'),
    Input('filter_sheet', 'value'),
    Input('identifier_all_check', 'value')
)
def select_all_identifiers(selectedsheets_list,checkedvalue):
    if 'All' in checkedvalue:
        if selectedsheets_list:
            filterdf_fromsheet=dff[dff[setup_identifier_columns[0]].isin(selectedsheets_list)]  
            #print(filterdf_fromsheet[setup_identifier_columns[1]].unique())
            return filterdf_fromsheet[setup_identifier_columns[1]].unique()
        else:
            return dff[setup_identifier_columns[1]].unique()
    else:
        return []

@app2.callback(
    #Output("output-graph", "children"), Input("table", "active_cell"),
    Output('filter_sheet', 'value'), 
    #Output('filter_identifier', 'value'),
    #Input('filter_sheet', 'value'),
    Input('sheet_all_check', 'value')
)
def select_all_sheets(checkedvalue):
    if 'All' in checkedvalue:
        return dff[setup_identifier_columns[0]].unique()
    else:
        return []
    
# ###########filter for filters finished ################################## 



# ###########update raw data table based on filters ################################## 
@app2.callback(
    Output("raw_data_table", "data"), 
    Input('filter_sheet', 'value'),
    Input('filter_identifier', 'value'),
    #Output('filter_identifier', 'value'),
)
def raw_data_table_filter(sheet_filter_list,identifier_filter_list):
    print(sheet_filter_list,identifier_filter_list)
    if identifier_filter_list:
        raw_data_filterdf=dff[dff[setup_identifier_columns[1]].isin(identifier_filter_list)]  
        # print (np.insert(filterdf[setup_identifier_columns[1]].unique(),0,'All'))
        return raw_data_filterdf.to_dict("records")

    else:
        if sheet_filter_list:
            raw_data_filterdf=dff[dff[setup_identifier_columns[0]].isin(sheet_filter_list)]
        else:
            raw_data_filterdf=dff
        # print (np.insert(filterdf[setup_identifier_columns[1]].unique(),0,'All'))
        return raw_data_filterdf.to_dict("records")


# ###########filter for filters finished ################################## 

# ###########filter for raw data
# @app2.callback(
#     #Output("output-graph", "children"), Input("table", "active_cell"),
#     Output('tbl_out', 'children'), 
#     Input('filter-'+setup_identifier_columns[0], 'value'),
#     Input('filter-'+setup_identifier_columns[0], 'value'),
# )
# def filter_raw_table(selected_sheets,selected_identifier):
#     if active_cell is None:
#         return no_update
#     return str(active_cell) if active_cell else "Click the table"

    # country = df.at[row, "country"]
    # print(country)

    # col = active_cell["column_id"]
    # print(f"column id: {col}")
    # print("---------------------")

    # y = col if col in ["pop", "gdpPercap"] else "lifeExp"

    # fig = px.line(
    #     df[df["country"] == country], x="year", y=y, title=" ".join([country, y])
    # )
    # fig.update_layout(title={"font_size": 20},  title_x=0.5, margin=dict(t=190, r=15, l=5, b=5))
    # fig.update_traces(line=dict(color=color[y]))

    # return dcc.Graph(figure=fig)
    return


######################################second dashboard finished#######################


###################################this is for authorization###############################################
for view_func in server.view_functions:
    if view_func.startswith(app.config['routes_pathname_prefix']):
        server.view_functions[view_func] = flask_login.login_required(server.view_functions[view_func])
###################################this is for authorization###############################################

if __name__ == '__main__':
    server.run(debug=True)
    #app.run_server(debug=True)
