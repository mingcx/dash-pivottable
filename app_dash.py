import dash
from dash.dependencies import Input, Output
import dash_pivottable
from data import data
from flask import Flask, url_for, send_file, send_from_directory, redirect
from flask import render_template
from dash import html
import flask_login
from AIDX_USER.database_connect import AzureDB_AIDX_user, db_session, Users, User_access
from flask import request

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



app= dash.Dash(server=server, url_base_pathname="/dashpivot/")
app.title = 'My Dash example'

server = app.server

app.layout = html.Div([
    dash_pivottable.PivotTable(
        id='table',
        data=data,
        cols=['Day of Week'],
        colOrder="key_a_to_z",
        rows=['Party Size'],
        rowOrder="key_a_to_z",
        rendererName="Grouped Column Chart",
        aggregatorName="Average",
        vals=["Total Bill"],
        valueFilter={'Day of Week': {'Thursday': False}}
    ),
    html.Div(
        id='output'
    )
])


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

for view_func in server.view_functions:
    if view_func.startswith(app.config['routes_pathname_prefix']):
        server.view_functions[view_func] = flask_login.login_required(server.view_functions[view_func])


if __name__ == '__main__':
    server.run(debug=True)
    #app.run_server(debug=True)
