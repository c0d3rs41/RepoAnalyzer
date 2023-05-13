import requests
import urllib.request 
import sys
import psycopg

import net_test as nt #Script containing function to check network connection

#Checking network connection
connected = nt.connect()

while not connected:
    print("Waiting for network connection...",end="\r")
    connected = nt.connect()

try: 
  conn = psycopg.connect(dbname="example_db",  #Creating connection with db
                        user="docker",
                        password="docker",
                        port="5432",
                        host="0.0.0.0")

  cursor = conn.cursor()

  # Create table statement

  sqlCreateTable1 = """create table if not exists owner_info(
  ownerId int primary key not null,
  ownername varchar(50) not null,
  ownerEmail varchar(50));"""

  sqlCreateTable2 = """create table if not exists repo_info(
  ownerId int not null,
  repoId int primary key not null,
  repoName varchar(100) not null,
  status char(15) not null,stars int not null,

  CONSTRAINT cons_fk FOREIGN KEY(ownerId)
  REFERENCES owner_info(ownerId)
  ON DELETE CASCADE
  );"""

  # Creating tables in PostgreSQL database

  cursor.execute(sqlCreateTable1)
  conn.commit()

  cursor.execute(sqlCreateTable2)
  conn.commit()

except Exception as error:
  print ("An exception has occured:", error)
  print ("Exception TYPE:", type(error))


#Important functions for inserting tuples into the tables

def insert_values_owner(id,name,email):

  try:
    query_stmt = """insert into owner_info values (%s,%s,%s)"""
    values=(id,name,email)
    cursor.execute(query_stmt,values)

    conn.commit()

    count = cursor.rowcount

  except Exception as error:
    print("Error in inserting tuple into owner_info table.")
    print(error)

  # else:
  #   print(count, "Record inserted successfully into table owner_info")

def insert_values_repo(ownerId,repoId,repoName,status,stars):

  try: 
    query_stmt = """insert into repo_info values (%s,%s,%s,%s,%s)"""
    values=(ownerId,repoId,repoName,status,stars)

    cursor.execute(query_stmt,values)

    conn.commit()

    count = cursor.rowcount

  except Exception as error:
    print("Error in inserting tuple into repo_info table.")
    print(error)

  # else:
  #   print(count, "Record inserted successfully into table repo_info")

#Function for testing network connection
def connect(host='http://google.com'):
  try:
    urllib.request.urlopen(host) #Python 3.x
    return True

  except:
    return False

'''Performing basic OAuthentication using the requests library.

Since this is a python based CLI, device flow will be used

Overview of the device flow (steps)

  1)Your app requests device and user verification codes and gets the authorization URL where the user will enter the user verification code.

  2)The app prompts the user to enter a user verification code at https://github.com/login/device.

  3)The app polls for the user authentication status. Once the user has authorized the device, the app will be able to make API calls with a new access token.'''

#Checking for network connection once again before authentication

connected = nt.connect()

while not connected:
    print("Waiting for network connection...",end="\r")
    connected = nt.connect()

#-------------Step1-----------------

url = "https://github.com/login/device/code"
myobj = {'client_id':'cf47adfb8b4eb9f6c170','scope':'repo user admin:org'}

res = requests.post(url,json=myobj,headers = {"Accept": "application/json"})

details = res.json() #Converts json to dictionary

#-----------------Step2------------
print("Enter the below details in the verification page: ")
print("User code:",details["user_code"]) 

print("Verification url:",details["verification_uri"])

choice = input("Type y on completion or n for exit: ")
choice = choice.lower()

if(choice!="y" and choice!="yes"):
    print("Exiting...")
    sys.exit(1)
#-----------------Step3------------
retrieve_url = "https://github.com/login/oauth/access_token"
obj = {'client_id':'cf47adfb8b4eb9f6c170','device_code':details["device_code"],'grant_type':'urn:ietf:params:oauth:grant-type:device_code'}
auth_token_details = requests.post(retrieve_url,json = obj,headers = {"Accept": "application/json"})

#Error handling incase the user presses y without authenticating
try:
    auth_token_details.json()["access_token"]

except:
    print("\nERROR: " + auth_token_details.json()["error_description"])
    sys.exit(1)

else:
    token = auth_token_details.json()["access_token"]

#-----------Getting details from the Github API---------

url = "https://api.github.com"

headers = {"Authorization": "Bearer " + token,"X-GitHub-Api-Version": "2022-11-28"}
params = {"type":"all"}
res = requests.get(url + "/user/repos",params=params,headers=headers) #Making a request to get the repo details

data = res.json()

email_res = requests.get(url + "/user/emails",params=params,headers=headers).json() #request to get the email information
email = email_res[0]["email"]

user = data[0]["owner"]["login"]

print()

#Clean slate
cursor.execute("delete from repo_info")
cursor.execute("delete from owner_info")

for i in range(len(data)):
  repo = data[i]

  status = "Private" if(repo["private"]) else "Public" #Status of the repo

  #Storing the obtained information in database
  #Database has 2 tables: owner_info and repo_info

  query = "select * from owner_info where ownerId=" + str(repo["owner"]["id"])
  cursor.execute(query)

  ret = cursor.fetchall()

  if(not ret): #Checking if the owner info is already present (deduplication)

    if(repo["owner"]["type"] == "User"):
      email = requests.get(url + "/user/emails",params=params,headers=headers).json()[0]["email"]

    elif(repo["owner"]["type"] == "Organization"):
      headers_org = {"Accept": "application/vnd.github+json","Authorization": "Bearer " + token,"X-GitHub-Api-Version": "2022-11-28"}
      res_org = requests.get(url + "/orgs/Sai-Organization-Testing",params=params,headers=headers_org)

      email = res_org.json()["email"]

    insert_values_owner(str(repo["owner"]["id"]),repo["owner"]["login"],email)

  insert_values_repo(str(repo["owner"]["id"]),repo["id"],repo["name"],status,repo["stargazers_count"])

  #Printing values

  print(repo["owner"]["id"],end="\t")
  print(repo["owner"]["login"],end="\t")
  print(email,end="\t")
  print(repo["id"],end="\t")
  print(repo["name"],end="\t")
  print(status,end="\t")
  print(repo["stargazers_count"])
  print(repo["owner"]["type"])
  print()


#Storing the csv file to resultsFile.csv

try:
  query = "select o.ownerId,o.ownerName,o.ownerEmail,r.repoId,r.repoName,r.status,r.stars from owner_info o,repo_info r where o.ownerId=r.ownerId"

  outputquery = "COPY ({0}) TO STDOUT WITH CSV HEADER".format(query)

  with cursor.copy(outputquery) as copy:
    with open("resultsfile.csv", "wb") as f:
      while data := copy.read():
        f.write(data)

except Exception as error:
  print ("Error in storing csv file:", error)
  print ("Exception TYPE:", type(error))

else:
  print("CSV file generated successfully.")

#Closing all connections
cursor.close()
conn.close()
