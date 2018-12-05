import pymysql.cursors
import pandas as pd
import datetime
pd.set_option('max_colwidth',1000)

DB='cs6400_su18_team06'
HOST='127.0.0.1'
USER='admin'
PASSWORD='password'

#Log-In Tasks

def loginuser(username,password):
    sql = "SELECT * FROM User WHERE username=%s AND password=%s;"
    try:
        conn = pymysql.connect(host=HOST,
                             user=USER,
                             password=PASSWORD,
                             database=DB)
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        cursor.execute(sql,(username,password))
        results = cursor.fetchall()
        conn.commit()
        cursor.close()
        conn.close()
        if len(results)>0:
            name = results[0]['name']
        else:
            raise Exception
        return name
    except Exception as err:
        print("Failed connecting to database: {}".format(err))
        raise Exception

def signupuser(username,password,name):
    sql = "INSERT INTO User (username,password,name) VALUES (%s, %s, %s);"
    try:
        conn = pymysql.connect(host=HOST,
                             user=USER,
                             password=PASSWORD,
                             database=DB)
        cursor = conn.cursor()
        cursor.execute(sql,(username,password,name))
        conn.commit()
        cursor.close()
        conn.close()
        return "Success"
    except Exception as err:
        print("Failed connecting to database: {}".format(err))
        raise Exception
        
# Main Menu

#sn: I tested this query and it works, but need to figure out how to implement it within Main Menu template. implemented directly in 
# main menu template, so can delete this one later
def menudisplay(username):
    sql = """SELECT User.name, User.username,
            Municipality.municipality_category,
            Government_Agency.agency_name_and_local_office,
            Company.location_of_headquarters, Company.num_employees
            FROM User LEFT JOIN Municipality ON User.username = Municipality.username
            LEFT JOIN Government_Agency ON User.username = Government_Agency.username
            LEFT JOIN Company ON User.username = Company.username
            WHERE User.username = %s;"""
    try:
        conn = pymysql.connect(host=HOST,
                             user=USER,
                             password=PASSWORD,
                             database=DB)
        cursor = conn.cursor()
        cursor.execute(sql,(username))
        conn.commit()
        cursor.close()
        conn.close()
        return "Success"
    except Exception as err:
        print("Failed connecting to database: {}".format(err))
        raise Exception
        
# Add Resource

#how to render?
def costper_options():
    sql = "SELECT Cost_Per.cost_option FROM Cost_Per;"
    try:
        conn = pymysql.connect(host=HOST,
                             user=USER,
                             password=PASSWORD,
                             database=DB)
        cursor = conn.cursor()
        cursor.execute(sql)
        conn.commit()
        cursor.close()
        conn.close()
        return "Success"
    except Exception as err:
        print("Failed connecting to database: {}".format(err))
        raise Exception
        
def primary_esf_options():
    sql = "SELECT Allowable_ESFs.esf_number, Allowable_ESFs.esf_description FROM Allowable_ESFs;"
    try:
        conn = pymysql.connect(host=HOST,
                             user=USER,
                             password=PASSWORD,
                             database=DB)
        cursor = conn.cursor()
        cursor.execute(sql)
        conn.commit()
        cursor.close()
        conn.close()
        return "Success"
    except Exception as err:
        print("Failed connecting to database: {}".format(err))
        raise Exception

#why is the %s not showing up in blue?
def additional_esf_options(primary):
    sql = """SELECT Allowable_ESFs.esf_number, Allowable_ESFs.esf_description FROM Allowable_ESFs 
        WHERE Allowable_ESFs.esf_number != %s ;"""
    try:
        conn = pymysql.connect(host=HOST,
                             user=USER,
                             password=PASSWORD,
                             database=DB)
        cursor = conn.cursor()
        cursor.execute(sql,(primary))
        conn.commit()
        cursor.close()
        conn.close()
        return "Success"
    except Exception as err:
        print("Failed connecting to database: {}".format(err))
        raise Exception

#I don't think I set these insert queries up correctly. How to include the string values? How do we separate the primary and additional esfs?
def add_resource(resource_id, username, name, model, cap, lat, long, cost, max_dist, status, cost_option, esf_number):
    sql1 = """INSERT INTO `resource` (`resource_id`, `username`, `name`, `model`, `capabilities`, `home_loc_lat`, `home_loc_long`, `cost`, `max_dist`, `res_status`, `cost_option`) 
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, `Available`, %s);"""
    sql2 = "INSERT INTO `esfs` (`resource_id`, `esf_number`, `esf_type`) VALUES (%s, %s, 'Primary');"
    sql3 = "INSERT INTO `esfs` (`resource_id`, `esf_number`, `esf_type`) VALUES (%s, %s, 'Additional');"
    try:
        conn = pymysql.connect(host=HOST,
                             user=USER,
                             password=PASSWORD,
                             database=DB)
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        cursor.execute(sql1,(resource_id, username, name, model, cap, lat, long, cost, max_dist, "Available", cost_option))
        cursor.execute(sql2,(resource_id,esf_number,"Primary"))
        cursor.execute(sql3,(resource_id,esf_number,"Additional"))
        conn.commit()
        cursor.close()
        conn.close()
        return "Success"
    except Exception as err:
        print("Failed connecting to database: {}".format(err))
        raise Exception        

def resources_in_use(username):
    sql = """
    SELECT Resource.resource_id as "ID", Resource.name as "Resource Name", Incident.inc_description as "Incident",
    User.name as "Owner", Requests.deployed_date as "Start Date", Requests.return_by as "Return By",Incident.incident_id as Inc_ID
    FROM Incident
    LEFT JOIN Requests ON Requests.incident_id = Incident.incident_id
    LEFT JOIN Resource ON Resource.resource_id = Requests.resource_id
    LEFT JOIN User ON User.username = Resource.username
    WHERE Incident.username=%s AND
    Requests.req_status=%s;
    """
    try:
        conn = pymysql.connect(host=HOST,
                             user=USER,
                             password=PASSWORD,
                             database=DB)
        results= pd.read_sql(sql,conn,params=(username, "DEPLOYED"))
        returnbeg='<form action="/resourcestatus" method="POST"><button name="return" class="btn" value="'
        returnend='">Return</button></form>'
        results['Action']=returnbeg+results['ID'].astype('str')+','+results['Inc_ID'].astype('str')+returnend
        del results['Inc_ID']
        results=results.to_html(index=False,classes=["thead-dark","table-hover"])
        results=convert_button_tags(results)
        conn.close()
        return results
    except Exception as err:
        print("Failed running Query: {}".format(err))
        raise Exception

def resources_requested_by_me(username):
    sql = """
    SELECT Resource.resource_id as "ID", Resource.name as "Resource Name", Incident.inc_description as "Incident",
    User.name as "Owner", Requests.return_by as "Return By",Incident.incident_id as Inc_ID
    FROM Incident
    LEFT JOIN Requests ON Requests.incident_id = Incident.incident_id
    LEFT JOIN Resource ON Resource.resource_id = Requests.resource_id
    LEFT JOIN User ON User.username = Resource.username
    Where Incident.username=%s AND
    Requests.req_status=%s;
    """
    try:
        conn = pymysql.connect(host=HOST,
                             user=USER,
                             password=PASSWORD,
                             database=DB)
        results= pd.read_sql(sql,conn,params=(username, "PENDING"))
        cancelbeg='<form action="/resourcestatus" method="POST"><button name="cancel" class="btn" value="'
        cancelend='">Cancel</button></form>'
        results['Action']=cancelbeg+results['ID'].astype('str')+','+results['Inc_ID'].astype('str')+cancelend
        del results['Inc_ID']
        results=results.to_html(index=False,classes=["thead-dark","table-hover"])
        results=convert_button_tags(results)
        conn.close()
        return results
    except Exception as err:
        print("Failed running Query: {}".format(err))
        raise Exception
        
def resources_requests_received_by_me(username):
    sql = """
    SELECT Resource.resource_id as "ID", Resource.name as "Resource Name", Incident.inc_description as "Incident",
    User.name as "Owner", Requests.return_by as "Return By", Resource.res_status as "Status",Incident.incident_id as Inc_ID
    FROM Requests
    LEFT JOIN Resource ON Resource.resource_id = Requests.resource_id
    LEFT JOIN Incident ON Incident.incident_id = Requests.incident_id
    LEFT JOIN User ON Incident.username = User.username
    WHERE Resource.username = %s AND
    Requests.req_status = %s;
    """
    try:
        conn = pymysql.connect(host=HOST,
                             user=USER,
                             password=PASSWORD,
                             database=DB)
        results= pd.read_sql(sql,conn,params=(username, "PENDING"))
        formbeg='<form action="/resourcestatus" method="POST">'
        formend='</form>'
        cancelbeg='<button name="cancel" class="btn" value="'
        cancelend='">Reject</button>'
        deploybeg='<form action="/resourcestatus" method="POST"><button name="deploy" class="btn" value="'
        deployend='">Deploy</button>'
        results['Action']=formbeg+deploybeg+results['ID'].astype('str')+','+results['Inc_ID'].astype('str')+deployend+cancelbeg+results['ID'].astype('str')+','+results['Inc_ID'].astype('str')+cancelend+formend
        results.loc[(results['Status']=='Deployed')|(results['Status']=='In-Use'), ['Action']] = formbeg+cancelbeg+results['ID'].astype('str')+','+results['Inc_ID'].astype('str')+cancelend+formend
        del results['Status']
        del results['Inc_ID']
        results=results.to_html(index=False,classes=["thead-dark","table-hover"])
        results=convert_button_tags(results)
        conn.close()
        return results
    except Exception as err:
        print("Failed running Query: {}".format(err))
        raise Exception

def convert_button_tags(html):
    html=html.replace('&lt;','<')
    html=html.replace('&gt;','>')
    return html

def cancel_request(res_id,inc_id):
    sql = """
    DELETE FROM Requests
    WHERE requests.resource_id = %s
    AND requests.incident_id = %s;
    """
    try:
        conn = pymysql.connect(host=HOST,
                             user=USER,
                             password=PASSWORD,
                             database=DB)
        cursor = conn.cursor()
        cursor.execute(sql,(res_id,inc_id))
        conn.commit()
        cursor.close()
        conn.close()
        return "Success"
    except Exception as err:
        print("Failed running Query: {}".format(err))
        raise Exception

def return_resource(res_id,inc_id):
    sql1 = """
    UPDATE Requests
    SET Requests.req_status='Returned'
    WHERE Requests.resource_id = %s
    AND Requests.incident_id = %s;
    """
    sql2 = """
    UPDATE Resource
    SET Resource.res_status='Available'
    WHERE Resource.resource_id = %s;
    """
    try:
        conn = pymysql.connect(host=HOST,
                             user=USER,
                             password=PASSWORD,
                             database=DB)
        cursor = conn.cursor()
        cursor.execute(sql1,(res_id,inc_id))
        cursor.execute(sql2,(res_id))
        conn.commit()
        cursor.close()
        conn.close()
        return "Success"
    except Exception as err:
        print("Failed running Query: {}".format(err))
        raise Exception

def deploy_resource(res_id,inc_id):
    sql1 = """
    UPDATE Requests
    SET Requests.req_status = 'Deployed',
    Requests.deployed_date = CURDATE()
    WHERE Requests.resource_id = %s
    AND Requests.incident_id = %s;
    """
    sql2 = """
    UPDATE Resource
    SET Resource.res_status='Deployed'
    WHERE Resource.resource_id = %s;
    """
    try:
        conn = pymysql.connect(host=HOST,
                             user=USER,
                             password=PASSWORD,
                             database=DB)
        cursor = conn.cursor()
        cursor.execute(sql1,(res_id,inc_id))
        cursor.execute(sql2,(res_id))
        conn.commit()
        cursor.close()
        conn.close()
        return "Success"
    except Exception as err:
        print("Failed running Query: {}".format(err))
        raise Exception
        
def request_resource(res_id,inc_id,return_by):
    #return_by=datetime.datetime.strptime(return_by, '%m-%d-%Y').date()
    sql = """
    INSERT INTO Requests
    VALUES (%s, %s, 
    CURDATE(),NULL, %s, 'Pending' );
    """
    try:
        conn = pymysql.connect(host=HOST,
                             user=USER,
                             password=PASSWORD,
                             database=DB)
        cursor = conn.cursor()
        cursor.execute(sql,(res_id,inc_id,return_by))
        conn.commit()
        cursor.close()
        conn.close()
        return "Success"
    except Exception as err:
        print("Failed running Query: {}".format(err))
        raise Exception

def request_deploy_resource(res_id,inc_id,return_by):
    #return_by=datetime.datetime.strptime(return_by, '%m-%d-%Y').date()
    sql1 = """
    INSERT INTO Requests
    VALUES (%s, %s, 
    CURDATE(),NULL, %s, 'Pending' );
    """
    sql2 = """
    UPDATE Requests
    SET Requests.req_status = 'Deployed',
    Requests.deployed_date = CURDATE()
    WHERE Requests.resource_id = %s
    AND Requests.incident_id = %s;
    """
    sql3 = """
    UPDATE Resource
    SET Resource.res_status='Deployed'
    WHERE Resource.resource_id = %s;
    """
    try:
        conn = pymysql.connect(host=HOST,
                             user=USER,
                             password=PASSWORD,
                             database=DB)
        cursor = conn.cursor()
        cursor.execute(sql1,(res_id,inc_id,return_by))
        cursor.execute(sql2,(res_id,inc_id))
        cursor.execute(sql3,(res_id))
        conn.commit()
        cursor.close()
        conn.close()
        return "Success"
    except Exception as err:
        print("Failed running Query: {}".format(err))
        raise Exception
# Add Emergency Incident
# Search Resources
# Search Results for Incident
# Request Resource
# Deploy Resource 
# Resource Status
# Return Resource
# Cancel Resource Request
# Reject Resource Request
# Resource Report
