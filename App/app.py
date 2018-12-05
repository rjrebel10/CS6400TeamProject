from flask import Flask, flash, redirect, render_template, request, session, abort, url_for, jsonify
from flask_table import create_table, Col, Table
from socket import gethostname
import os
import pandas as pd
from sqlfunctions import *

# App config.
DEBUG = True
app = Flask(__name__)
app.config.from_object(__name__)
app.config['SECRET_KEY'] = '7d441f27d441f27567d441f2b6176a'
 
@app.route('/', methods=['GET', 'POST'])
def home():
    return redirect(url_for('menu'))

@app.route('/menu', methods=['GET'])
def menu(username=None):
    if not session.get('logged_in'):
        return render_template('login.html')
    else:
        conn = pymysql.connect(host=HOST,
                             user=USER,
                             password=PASSWORD,
                             database=DB)
        cursor = conn.cursor()
        username = session['username']
        sql = """SELECT User.name,
            Municipality.municipality_category,
            Government_Agency.agency_name_and_local_office,
            Company.location_of_headquarters, Company.num_employees
            FROM User LEFT JOIN Municipality ON User.username = Municipality.username
            LEFT JOIN Government_Agency ON User.username = Government_Agency.username
            LEFT JOIN Company ON User.username = Company.username
            WHERE User.username = %s;"""
        results = cursor.execute(sql,(username))
        res = list(cursor.fetchone())
        res = [x for x in res if x != "None" and x is not None]
        res = ' '.join((str(x) for x in res))
        return render_template('menu.html', res=res)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        try:
            session['name']=loginuser(request.form['username'],request.form['password'])
            session['logged_in'] = True
            session['username'] = request.form['username']
            return redirect(url_for('menu'))
        except:
            flash('Invalid Credentials')
            return render_template('login.html')
    else:
        if not session.get('logged_in'):
            return render_template('login.html')
        else:
            return redirect(url_for('menu'))

@app.route('/logout', methods=['GET', 'POST'])
def logout():
    session['logged_in'] = False
    session['username'] = None
    session['name'] = None
    return render_template('loggedout.html')


def get_cost_per():
     """
     function to get cost_per values for Add Resource Form
     """
     if not session.get('logged_in'):
         return render_template('login.html')
     else:
         conn = pymysql.connect(host=HOST, user=USER, password=PASSWORD, database=DB)
         cursor = conn.cursor()
         sql = "SELECT cost_option FROM Cost_Per;"
         results = cursor.execute(sql)
         res = cursor.fetchall()
         res = [element for tupl in res for element in tupl]
         return res
     
def get_dropdown_values():
     """
     function to get ESF values for dropdowns in Search Resources and Add Resource Forms
     """
     if not session.get('logged_in'):
         return render_template('login.html')
     else:
         conn = pymysql.connect(host=HOST, user=USER, password=PASSWORD, database=DB)
         cursor = conn.cursor()
         sql = "SELECT Allowable_ESFs.esf_number, Allowable_ESFs.esf_description FROM Allowable_ESFs;"
         results = cursor.execute(sql)
         res = list(cursor.fetchall())
         class_entry_relations = [" ".join(x) for x in res]
         return class_entry_relations        
 

@app.route('/_update_dropdown')
def update_dropdown():
    """Additional ESF Dropdown"""
    # the value of the first dropdown (selected by the user)
    selected_class = request.args.get('selected_class', type=str)
     
    # get values for the second dropdown
    updated_values = get_dropdown_values()
    updated_values = [x for x in updated_values if x!=selected_class]

    # create the value sin the dropdown as a html string
    html_string_selected = ''
    for entry in updated_values:
        html_string_selected += '<option value="{}">{}</option>'.format(entry, entry)

    return jsonify(html_string_selected=html_string_selected)


# I think this function can be deleted
@app.route('/_process_data')
def process_data():
    selected_class = request.args.get('selected_class', type=str)
    selected_entry = request.args.get('selected_entry', type=str)

    # process the two selected values here and return the response; here we just create a dummy string

    return jsonify(random_text="you selected {} and {}".format(selected_class, selected_entry))

def get_resource_id():
    """
    Function to auto-generate resource_id for Add Resource Form
    """
    conn = pymysql.connect(host=HOST, user=USER, password=PASSWORD, database=DB)
    cursor = conn.cursor()
    sql = "SELECT MAX(resource_id) FROM resource;"
    cursor.execute(sql)
    return cursor.fetchone()[0] + 1

@app.route('/addresource', methods=['GET', 'POST'])
def addresource():

    """
    Initialize the dropdown menues
    """
    
    if not session.get('logged_in'):
        return render_template('login.html')
    elif request.method == 'POST':
        resource_id = get_resource_id() #for testing
        username = session['username']
        resourcename = request.form['resourcename']
        prim_esf = request.form.get('prim_esf')
        add_esf = request.form.getlist('add_esf')
        model = request.form.get('model')
        capabilities = request.form['capabilities']
        lat = request.form['lat']
        long = request.form['long']
        maxdist = request.form['maxdist']
        cost = int(request.form['cost'])
        costper = str.strip(request.form.get('costper'))
        conn = pymysql.connect(host=HOST, user=USER, password=PASSWORD, database=DB)
        cursor = conn.cursor()
        #validating fields - How do I check that the latitude and longitude fields contain valid coordinates?
        if prim_esf is not None and lat is not None and long is not None and cost is not None and cost > 0:
            #this query updates the Resource table            
            sqlA = """INSERT INTO `resource` (`resource_id`, `username`, `name`, `model`, `capabilities`,
            `home_loc_lat`, `home_loc_long`, `cost`, `max_dist`, `res_status`, `cost_option`) VALUES
            (%s, %s, %s, %s, %s, %s, %s, %s, %s,
             'Available', %s);"""
            cursor.execute(sqlA,(resource_id,username,resourcename,model,capabilities,lat,long,cost,maxdist,costper))
            #this query inserts the Primary ESF into ESFs table
            sqlB = "INSERT INTO ESFs (`resource_id`, `esf_number`, `esf_type`) VALUES (%s, %s, 'Primary');"
            esf_num = str(prim_esf).split(' ', 1)[0]
            cursor.execute(sqlB, (resource_id, esf_num ))
            #this query inserts each Additional ESF into ESFs table
            if len(add_esf) > 0:
                 for value in add_esf:
                     sqlC = "INSERT INTO ESFs (`resource_id`, `esf_number`, `esf_type`) VALUES (%s, %s, 'Additional')"
                     esf_num = str(value).split(' ', 1)[0]
                     cursor.execute(sqlC, (resource_id, esf_num))
            conn.commit()
            return("Success")
    else:
        class_entry_relations = get_dropdown_values()

        default_classes = sorted(class_entry_relations)
        default_values = default_classes[:]
        default_values.remove('1 Transportation')
        cost_per_entries = get_cost_per()
        resource_id = get_resource_id()
        return render_template('addresource.html',
                           all_classes=default_classes,
                           all_entries=default_values,
                           cost_per_entries = cost_per_entries,
                           resource_id=resource_id,
                           username=session["username"])

def find_emergency_dec():
    """
    Query to fill dropdown in Add Incident Form
    """
    conn = pymysql.connect(host=HOST, user=USER, password=PASSWORD, database=DB)
    cursor = conn.cursor()
    sql = "SELECT declaration FROM incident_declarations;"
    results = cursor.execute(sql)
    res = cursor.fetchall()
    res = [element for tupl in res for element in tupl]
    return res

def generate_incident_id(declaration):
    """
    Generates an incident_id for Add Incident Form
    """
    conn = pymysql.connect(host=HOST, user=USER, password=PASSWORD, database=DB)
    cursor = conn.cursor()
    sqlA = "SELECT abbreviation FROM incident_declarations WHERE declaration=%s"
    results = cursor.execute(sqlA, (declaration))
    abbreviation = cursor.fetchone()[0]   
    sqlB = "SELECT max(incident_id) FROM incident WHERE abbreviation=%s"
    results = cursor.execute(sqlB, (abbreviation))
    res = cursor.fetchone()[0]
    res = int(res.split('-', 1)[1]) + 1
    incident_id = str(abbreviation) + "-" + str(res)
    return abbreviation, incident_id
    
@app.route('/addincident', methods=['GET', 'POST'])
def addincident(username=None):
    if not session.get('logged_in'):
        return render_template('login.html')
    elif request.method == 'POST':
        username = session['username']
        declaration = request.form.get('declaration')
        abbreviation, incident_id = generate_incident_id(declaration = declaration)
        inc_description = request.form['inc_description']
        date = request.form['date']
        lat = request.form['lat']
        long = request.form['long']
        conn = pymysql.connect(host=HOST, user=USER, password=PASSWORD, database=DB)
        cursor = conn.cursor()
        #need to add loc and long and other fields validation steps
        sql = "INSERT INTO `incident` (`username`, `incident_id`, `inc_description`, `date`, \
        `loc_lat`, `loc_long`, `abbreviation`) VALUES (%s, %s, %s,\
        %s, %s, %s, %s);"
        cursor.execute(sql, (username, incident_id, inc_description, date, lat, long, abbreviation))
        conn.commit()
        return ("success")
    else:
        all_declarations = find_emergency_dec()
        return render_template('addincident.html', all_declarations=all_declarations, username=session['username'])

def find_users_incidents():
    conn = pymysql.connect(host=HOST, user=USER, password=PASSWORD, database=DB)
    cursor = conn.cursor()
    sql = "SELECT incident_id, inc_description FROM incident WHERE username=%s;"
    username = session["username"]
    cursor.execute(sql, (username))
    res = cursor.fetchall()
    incident = [(x[0] + " : " + x[1]) for x in list(res)]
    return incident
        
@app.route('/searchresource', methods=['GET', 'POST'])
def searchresource():
    if not session.get('logged_in'):
        return render_template('login.html')
    elif request.method == 'POST':
        username = session['username']
        # 'Truck* Fire* Amb*'
        return_by = request.form['return_by']
        keyword = request.form['keyword']
        keyword = str(keyword).split(',')
        keyword = [x.strip() for x in keyword]
        keyword = "* ".join(keyword)
        keyword = keyword + "*"
        # '1'
        esf = request.form.get("esf").split(" ",1)[0]
        if esf == "":
            esf=None
        # 1000
        dist = request.form['location']
        if dist == "":
            dist=None
        # 'ED-1'
        incidentname= request.form.get('incident')
        incident = request.form.get('incident').split(" ",1)[0]
        if incident == "":
            incidentname=None
            incident=None            
        conn = pymysql.connect(host=HOST, user=USER, password=PASSWORD, database=DB)
        cursor = conn.cursor()
        if dist is None or incident==None:
            sql = """SELECT * FROM (SELECT DISTINCT
                resource_results.resource_id as ID, resource_results.res_name as Name, resource_results.Resource_Owner as Owner,
                CONCAT('$',resource_results.cost, '/' ,resource_results.cost_option) as Cost, resource_results.res_status as Status,
                IF(resource_results.res_status = 'AVAILABLE', 'NOW', requests.return_by) as Next_Available
                FROM
                (SELECT resource.resource_id, resource.name as res_name,
                resource.username as Resource_Owner, resource.home_loc_lat as res_lat, resource.home_loc_long as res_long,
                resource.cost, resource.cost_option, resource.res_status, resource.max_dist, resource.capabilities
                FROM
                resource
                WHERE MATCH (resource.name, resource.capabilities, resource.model) AGAINST ( %s IN BOOLEAN MODE)) as resource_results
                LEFT JOIN esfs ON resource_results.resource_id = esfs.resource_id
                LEFT JOIN requests ON resource_results.resource_id = requests.resource_id
                WHERE NOT(resource_results.res_status IN('In-Use','Deployed') AND requests.req_status <>'DEPLOYED')
                AND (%s is NULL OR esfs.esf_number = %s)) as Results;""" 
            results= pd.read_sql(sql, conn,params=(keyword, esf, esf))
            results=results.to_html(index=False,classes=["thead-dark","table-hover"])
            table=convert_button_tags(results)
            return render_template('searchresults.html', username=session['username'], table=table)
        else:
            sql = """SELECT * FROM (SELECT DISTINCT
                resource_results.resource_id as ID, resource_results.res_name as Name, resource_results.Resource_Owner as Owner,
                CONCAT('$',resource_results.cost, '/' ,resource_results.cost_option) as Cost, resource_results.res_status as Status,
                IF(resource_results.res_status = 'AVAILABLE', 'NOW', requests.return_by) as Next_Available,
                111.111 * DEGREES(ACOS(COS(RADIANS(resource_results.res_lat))* COS(RADIANS(inc_lat)) * COS(RADIANS(resource_results.res_long - resource_results.inc_long))
                + SIN(RADIANS(resource_results.res_lat))* SIN(RADIANS(resource_results.inc_lat)))) AS Distance_in_KM
                FROM
                (SELECT (SELECT incident_id FROM incident WHERE incident_id = %s) AS inc_id,
                (SELECT loc_lat FROM incident WHERE incident_id = %s) AS inc_lat,
                (SELECT loc_long FROM incident WHERE incident_id = %s) AS inc_long,
                resource.resource_id, resource.name as res_name,
                resource.username as Resource_Owner, resource.home_loc_lat as res_lat, resource.home_loc_long as res_long,
                resource.cost, resource.cost_option, resource.res_status, resource.max_dist, resource.capabilities
                FROM
                resource
                WHERE MATCH (resource.name, resource.capabilities, resource.model) AGAINST ( %s IN BOOLEAN MODE)) as resource_results
                LEFT JOIN esfs ON resource_results.resource_id = esfs.resource_id
                LEFT JOIN requests ON resource_results.resource_id = requests.resource_id
                LEFT JOIN requests as requests2 ON (requests2.resource_id = resource_results.resource_id AND requests2.incident_id = %s)
                WHERE (requests2.incident_id is Null OR requests2.incident_id <> %s) AND NOT(resource_results.res_status IN('In-Use','Deployed') AND requests.req_status <>'DEPLOYED')
                AND (%s is NULL OR esfs.esf_number = %s)) as Results WHERE Distance_in_KM < %s
                ORDER BY Distance_in_KM;""" 
            results= pd.read_sql(sql, conn,params=(incident, incident, incident, keyword, incident, incident, esf, esf, dist))
            reqbeg='<form action="/resourcestatus" method="POST"><button name="request" class="btn" value="'
            reqend='">Request</button></form>'
            reqdepbeg='<form action="/resourcestatus" method="POST"><button name="request_deploy" class="btn" value="'
            reqdepend='">Deploy</button></form>'
            results['Action']=reqbeg+results['ID'].astype('str')+','+incident+','+return_by+reqend
            results.loc[(results['Status']=='Available')&(results['Owner']==username), ['Action']] = reqdepbeg+results['ID'].astype('str')+','+incident+','+return_by+reqdepend
            results=results.to_html(index=False,classes=["thead-dark","table-hover"])
            table=convert_button_tags(results)
            return render_template('searchresultsforincident.html', username=session['username'], incidentname=incidentname, table=table)
    else:
        esfs = sorted(get_dropdown_values())
        incident = find_users_incidents()
        return render_template('searchresource.html', username=session['username'], esfs=esfs, incident=incident)
          
@app.route('/resourcestatus', methods=['GET','POST'])
def resourcestatus(username=None):
    if not session.get('logged_in'):
        return render_template('login.html')
    if request.method == 'POST':
        try:
            cvalues=request.form['cancel']
            if cvalues is not None:
                cancelvals=cvalues.split(',')
                cancel_request(cancelvals[0],cancelvals[1])
        except:
            pass
        try:
            rvalues=request.form['return']
            if rvalues is not None:
                returnvals=rvalues.split(',')
                return_resource(returnvals[0],returnvals[1])
        except:
            pass
        try:
            dvalues=request.form['deploy']
            if dvalues is not None:
                deployvals=dvalues.split(',')
                deploy_resource(deployvals[0],deployvals[1])
        except:
            pass
        try:
            reqvalues=request.form['request']
            if reqvalues is not None:
                reqvals=reqvalues.split(',')
                request_resource(reqvals[0],reqvals[1],reqvals[2])
        except:
            pass
        try:
            rdvalues=request.form['request_deploy']
            if rdvalues is not None:
                reqdepvals=rdvalues.split(',')
                request_deploy_resource(reqdepvals[0],reqdepvals[1],reqdepvals[2])
        except:
            pass
    username = session['username']
    in_use=resources_in_use(username)
    requested_by_me=resources_requested_by_me(username)
    requests_received_by_me=resources_requests_received_by_me(username)
    return render_template('resourcestatus.html', in_use=in_use, requested_by_me=requested_by_me, requests_received_by_me=requests_received_by_me)
 

@app.route('/report', methods=['GET', 'POST'])
def resource_report(username=None):
    if not session.get('logged_in'):
        return render_template('login.html')
    conn = pymysql.connect(host=HOST, user=USER, password=PASSWORD, database=DB)
    cursor = conn.cursor()
    username = session['username']
    sql="""Select Allowable_ESFs.esf_number AS ESF_Number, Allowable_ESFs.esf_description AS Primary_ESF,
	count(Resource.resource_id) AS Total_Resources, count(IF(Resource.res_status IN('In-Use','Deployed'), 1, null)) AS Resource_In_Use
    From Allowable_ESFs
    Left Join ESFs on Allowable_ESFs.esf_number = ESFs.esf_number
    Left Join Resource on Resource.resource_id = ESFs.resource_id
    where ESFs.esf_type="Primary" and Resource.username = %s
    group by Allowable_ESFs.esf_number, Allowable_ESFs.esf_description
    order by Allowable_ESFs.esf_number"""
    cursor.execute(sql, (username))
    data = cursor.fetchall()
    return render_template('report.html', ESF=data)

if __name__ == "__main__":
    if 'liveconsole' not in gethostname():
        app.run()
