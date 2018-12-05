
Create tables:
==============




CREATE TABLE Allowable_ESFs (
esf_description varchar(250) NOT NULL,
esf_number int NOT NULL,
PRIMARY KEY (esf_number)
);


CREATE TABLE Incident_Declarations (
declaration varchar(250) NOT NULL,
abbreviation varchar(250) NOT NULL,
PRIMARY KEY (abbreviation)
);


CREATE TABLE Cost_Per (
cost_option varchar(250) NOT NULL,
PRIMARY KEY (cost_option)
);


CREATE TABLE User (
username varchar(50) NOT NULL,
name varchar(250) NOT NULL,
password varchar(60) NOT NULL,
PRIMARY KEY (username)
);


CREATE TABLE Individual (
username varchar(50) NOT NULL,
job_title varchar(250) NOT NULL,
date_of_hire date NOT NULL, 
PRIMARY KEY (username),
FOREIGN KEY (username)
   REFERENCES User(username)
);


CREATE TABLE Municipality (
username varchar(50) NOT NULL,
municipality_category varchar(250) NOT NULL,
PRIMARY KEY (username),
FOREIGN KEY (username)
   REFERENCES User(username)
);


CREATE TABLE Government_Agency (
username varchar(50) NOT NULL,
agency_name_and_local_office varchar(250) NOT NULL,
PRIMARY KEY (username),
FOREIGN KEY (username)
   REFERENCES User(username)
);


CREATE TABLE Company (
username varchar(50) NOT NULL,
location_of_headquarters varchar(250) NOT NULL,
num_employees int NOT NULL,
PRIMARY KEY (username),
FOREIGN KEY (username)
   REFERENCES User(username)
);


CREATE TABLE Resource (
resource_id int NOT NULL AUTO_INCREMENT,
username varchar(50) NOT NULL,
name varchar(250) NOT NULL,
model varchar(250) DEFAULT NULL,
capabilities varchar(250) DEFAULT NULL,
home_loc_lat float(10, 2) NOT NULL,
home_loc_long float(10, 2) NOT NULL, 
cost decimal(10, 2) NOT NULL,
max_dist int DEFAULT NULL,
res_status varchar(50) DEFAULT 'AVAILABLE' ,
cost_option varchar(250) NOT NULL,
PRIMARY KEY (resource_id),
FOREIGN KEY (username)
   REFERENCES User(username),
FOREIGN KEY (cost_option)
   REFERENCES Cost_Per(cost_option)
);


CREATE TABLE Incident (
username varchar(50) NOT NULL,
incident_id int NOT NULL AUTO_INCREMENT,
inc_description varchar(250) DEFAULT NULL,
date date DEFAULT NULL,
loc_lat float(10, 2) DEFAULT NULL,
loc_long float(10, 2) DEFAULT NULL,
abbreviation varchar(250) DEFAULT NULL,
PRIMARY KEY (incident_id),
FOREIGN KEY (username)
   REFERENCES User (username),
FOREIGN KEY (abbreviation)
   REFERENCES Incident_Declarations (abbreviation)
);


CREATE TABLE Requests (
resource_id int NOT NULL,
incident_id int NOT NULL,
request_date date NOT NULL,
deployed_date date DEFAULT NULL, 
return_by date NOT NULL,
req_status varchar(20) DEFAULT 'PENDING',
PRIMARY KEY (resource_id, incident_id),
FOREIGN KEY (resource_id)   
   REFERENCES Resource (resource_id),
FOREIGN KEY (incident_id)   
   REFERENCES Incident(incident_id)
);


CREATE TABLE ESFs (
resource_id int NOT NULL,
esf_number int NOT NULL,
esf_type varchar(250) NOT NULL,
PRIMARY KEY (resource_id, esf_number),
FOREIGN KEY (resource_id)   
   REFERENCES Resource (resource_id),
FOREIGN KEY (esf_number)  
   REFERENCES Allowable_ESFs(esf_number)
);
