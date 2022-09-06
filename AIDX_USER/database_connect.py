from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Table, Column, Float, Integer, String, MetaData, ForeignKey, DateTime, Boolean, sql
from sqlalchemy.exc import IntegrityError
from datetime import datetime
from werkzeug.security import generate_password_hash,check_password_hash
import pyodbc
import urllib
import pandas as pd
import numpy as np
import xlrd
#from LEGO_NFinance.main import LEGO_NFinance
from datetime import datetime


#pip install pyodbc

DRIVER_SELECTION='azure'     #azure or desktop

# from azuredb.database import *
# init_db
# db.create_all()
# exit()
# Integer() - INT
# String() - ASCII strings - VARCHAR
# Unicode() - Unicode string - VARCHAR or NVARCHAR depending on database
# Boolean() - BOOLEAN, INT, TINYINT depending on db support for boolean type
# DateTime() - DATETIME or TIMESTAMP returns Python datetime() objects.
# Float() - floating point values
# Numeric() - precision numbers usifng Python Decimal()


# # this works 
# SERVER = 'gbl-gen-sql-legotest.database.windows.net'
# DATABASE = 'gbl_gen_sqldb_aidx_user'
# DRIVER = 'SQL+Server'
# USERNAME = 'mingzhaojin'
# PASSWORD = 'sugarLand!5753'
# DATABASE_CONNECTION = f'mssql://{USERNAME}:{PASSWORD}@{SERVER}/{DATABASE}?driver={DRIVER}'
# #this workds

#https://stackoverflow.com/questions/41344054/python-sqlalchemy-data-source-name-not-found-and-no-default-driver-specified


#this one works locally as well
if DRIVER_SELECTION=='azure':
    params = urllib.parse.quote_plus(
        'Driver={%s};' % 'ODBC Driver 17 for SQL Server' +
        'Server=tcp:%s,1433;' % 'gbl-gen-sql-legotest.database.windows.net' +
        'Database=%s;' % 'gbl_gen_sqldb_aidx_user' +
        'Uid=%s;' % 'mingzhaojin_rde_us' +
        'Pwd={%s};' % 'sugarLand!5753' +
        'Encrypt=yes;' +
        'TrustServerCertificate=no;' +
        # 'Trusted_Connection = yes;' +
        'Connection Timeout=30;')

    DATABASE_CONNECTION = 'mssql+pyodbc:///?odbc_connect=' + params

engine = create_engine(DATABASE_CONNECTION,fast_executemany=True)
db_session = scoped_session(sessionmaker(autocommit=False,
                                          autoflush=False,
                                          bind=engine))

Base = declarative_base()
Base.query = db_session.query_property()

def init_sqlalchemy():
    Base.metadata.create_all(engine)



class Users(Base):
    __tablename__ = 'Users'
    __table_args__ = {'implicit_returning': False} 
    __table_args__ = {'extend_existing': True}
    userid=                 Column(Integer, primary_key=True)
    useremail=              Column(String(128),  nullable=False, unique=True)
    userpassword_hash=      Column(String(128),  nullable=False)
    #has function for user
    def set_password(self,password):
        self.userpassword_hash=generate_password_hash(password)

    def check_password(self,password):
        return check_password_hash(self.userpassword_hash,password)


class User_access(Base):
    __tablename__ = 'User_access'
    __table_args__ = {'implicit_returning': False} 
    __table_args__ = {'extend_existing': True}
    access_id=          Column(Integer, primary_key=True)
    username=           Column(String(128))
    access_platform=    Column(String(128))
    access_level=       Column(String(128))
  
class User_utility(Base):
    __tablename__ = 'User_utility'
    __table_args__ = {'implicit_returning': False} 
    __table_args__ = {'extend_existing': True}
    utility_id=             Column(Integer, primary_key=True)
    username=               Column(String(128))
    access_platform=        Column(String(128))
    function_used=          Column(String(128))
    access_time=            Column(String(128))


class Project_finance(Base):
    __tablename__ = 'Project_finance'
    __table_args__ = {'implicit_returning': False} 
    __table_args__ = {'extend_existing': True}
    project_id_id=                  Column(Integer, primary_key=True)
    project_id_internal=            Column(String(128))
    project_id_gtrs=                Column(String(128))
    project_customer=               Column(String(128))
    project_site=                   Column(String(128))
    project_sales_office=           Column(String(128))
    project_mamnger_email=          Column(String(128))
    project_group=                  Column(String(128))
    register_time=                  Column(String(128))

class Project_work(Base):
    __tablename__ = 'Project_work'
    __table_args__ = {'implicit_returning': False} 
    __table_args__ = {'extend_existing': True}
    table_id=                       Column(Integer, primary_key=True)
    project_id_internal=            Column(String(128))
    project_id_gtrs=                Column(String(128))
    worktype=                       Column(String(128))
    site=                           Column(String(128))
    site_product=                   Column(String(128))
    product_name=                   Column(String(128))
    product_MIN=                    Column(String(128))
    complete_time=                  Column(String(128))
    estimated_hours=                Column(Integer)



#for manipulte database
class AzureDB_AIDX_user():
    def __init__(self):
        db_session.rollback()
        self.session=db_session()   #sqlsessin
        self.Base=Base      #sqlbase
        self.Users=Users   #table
        self.User_access=User_access      #table
        self.User_utility=User_utility   # project control table

        #following is for project manage and value tracking
        self.Project_finance=Project_finance
        self.Project_work=Project_work


    def init_db(self):
        self.Base.metadata.create_all(bind=engine)

    def close(self):
        self.session.close()

    def add_project_work(self,project_dic=None,project_work_df=None):


        #add product line finished

        if project_work_df is not None:
            for index, row in project_work_df.iterrows():
                newproject_work=self.Project_work()
                projectid_internal=str(row['project_id_internal'] ) 
                project = self.Project_finance.query.filter_by(project_id_internal=projectid_internal).first()
                if project is not None:
                    sitename=project.project_site
                product_name=str(row['product_name'])
                site_product=sitename+'_'+product_name
                newproject_work.project_id_internal= projectid_internal
                newproject_work.site=sitename
                newproject_work.site_product=site_product
                newproject_work.project_id_gtrs=  str(row['project_id_gtrs'])                 
                newproject_work.worktype=   str(row['worktype'])               
                newproject_work.product_name=   str(row['product_name'])                   
                newproject_work.product_MIN=  str(row['product_MIN'])          
                newproject_work.complete_time= str(row['complete_time'])            
                newproject_work.estimated_hours= int(row['estimated_hours'])                    
                self.session.add(newproject_work)
                print(row['project_id_internal']  + ' is added')               
            self.session.commit()
            print('project work commit fished') 

    def add_project(self,project_dic=None,project_df=None):
        if project_df is not None:
            lego_nfinance=LEGO_NFinance()
            lego_nfinance.read_N_data_from_excel(productline_name='CI')
            for index, row in project_df.iterrows():
                internal_id=row['project_id_internal']
                check_project=self.session.query(self.Project_finance).filter_by(project_id_internal=internal_id).first()
                if check_project:
                    self.Project_finance.query.filter(self.Project_finance.project_id_internal == internal_id).delete()
                newproject=self.Project_finance()
                newproject.project_id_internal= str(internal_id)         
                newproject.project_id_gtrs=  str(row['project_id_gtrs'])                 
                sitename=str(row['project_site'])
                newproject.project_site=   sitename
                salesoffice_from_dic=lego_nfinance.site_to_salesoffice_dic.get(sitename)    
                customername=sitename.split("-", 1)[0].strip()
                newproject.project_customer=   customername                
                newproject.project_sales_office=  salesoffice_from_dic         
                newproject.project_mamnger_email= str(row['project_mamnger_email'])            
                newproject.project_group= str(row['project_group'])                  
                newproject.register_time= str(row['register_time'])      
                self.session.add(newproject)
                print(row['project_id_internal']  + ' is added')               
            self.session.commit()
            print('commit fished') 
        
    #add new user to databse
    def add_user(self,useremail=None,password=None):
        u=self.Users(useremail=useremail)
        u.set_password(password)
        self.session.add(u)
        self.session.commit()
        print(useremail+' added')
    
    #check user and password, return are "no user", "match" and "unmatch"
    def user_exsit_check(self,useremail=None):
        check_user=self.session.query(self.User).filter_by(useremail=useremail).first()
        if not check_user:
            print('no user')
            return False
        else:
            print('user exsit')
            return True

    def user_password_check(self,useremail=None,password=None):
        check_user=self.session.query(self.Users).filter_by(useremail=useremail).first()
        if not check_user:
            print('nouser')
            return 'nouser'
        user_password_check_result=check_user.check_password(password)
        if user_password_check_result:
            print('match')
            return "match"
        else:
            print('unmatch')
            return "unmatch"

    #reset password by using old password, return are "no user", "unmatch" and "resetdone"
    def user_password_reset(self,useremail=None,oldpassword=None,newpassword=None,forcechange=False):
        password_check_result=self.user_password_check(useremail,oldpassword)
        if password_check_result != "match" and forcechange == False:
            return password_check_result
        else:
            check_user=self.session.query(self.Users).filter_by(useremail=useremail).first()
            check_user.set_password(newpassword)
            self.session.commit()
            return "resetdone"

    def add_access(self,useremail,access_platform,access_level):
        check_user=self.session.query(self.Users).filter_by(useremail=useremail).first()
        if not check_user:
            print('no user')
            return False
        else:
            check_access=self.session.query(self.User_access).filter_by(username=useremail,access_platform=access_platform,access_level=access_level).first()
            
            if not check_access:
                u_acess=self.User_access(username=useremail,access_platform=access_platform,access_level=access_level)
                self.session.add(u_acess)
                self.session.commit()
                print(useremail+' access '+access_platform+" "+access_level)
            else:
                print('access already in database')
            return True
    
    def check_access(self,useremail,access_platform,access_level):
        check_access=self.session.query(self.User_access).filter_by(username=useremail,access_platform=access_platform,access_level=access_level).first()
        if not check_access:
            print('no access')
            return False
        else:
            return True

    def add_utility(self,useremail,platform,functionused):
        access_time=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        u_uti=self.User_utility(username=useremail,access_platform=platform,function_used=functionused,access_time=access_time)
        self.session.add(u_uti)
        self.session.commit()
        print(useremail + ' used ' + functionused + " on " + platform+', '+access_time)
        return True