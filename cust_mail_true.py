# *************************
# ******* Intro ***********
# *************************

# cust_mail_true v0.0.0
version = 'v0.0.0'
# written by Jason Miller
# logs into Lightspeed API
# searches through customer list and sets mailing to true
# for MailChimp integration

# *************************
# ******* Import ***********
# *************************
import numpy as mp
import pandas as pd
import datetime
import csv
import glob
import os
import lightspeed_api
import math



# *************************
# ******* Log file initialize ***********
# *************************

# ********---->> set current folder <<--------*******
folder_name = r'C:\Users\jaymi\OneDrive\Documents\3ROC'
os.chdir(folder_name)
scriptname = os.path.basename(__file__)
scriptname = scriptname[:-3]

# ********---->> set log <<--------*******
now = datetime.datetime.now()
beta = False #  True is testing, False is production and will label unique log file
if beta:
    logname = 'log.txt'
else:
    logname = 'log-' + scriptname + '-' + now.strftime('%Y%m%d%H%M') + '.txt'
log = open(str('./logs/' + logname), mode='w')

# *************************
# ******* define functions ***********
# *************************

# function to logging messages in process
def log_msg (s):
    now = datetime.datetime.now()
    sm = now.strftime('%Y%m%d-%H%M%S') + ': ' + str(s)
    print(sm)
    log.write(sm + '\n')

# function to dump dict to json
def write_json (dict, na):
    log_msg(str('write json: ' + na))
    import json

    # create json object from dictionary
    json = json.dumps(dict)
    log_msg('dump')

    # open file for writing, "w"
    f = open(str('./results/' + na + '.json'), "w")

    # write json object to file
    f.write(json)
    log_msg(str('write: ' + na + '.json'))

    # close file
    f.close()
    log_msg('closed')


# create log file header
log_msg(scriptname)
log_msg(version)
log_msg('program started')


# *************************
# ******* connect to Lightspeed API ***********
# *************************
log_msg('connecting to Lightspeed...')
import lightspeed_api

c = {'account_id': '161824',
     'client_id': '06dc34ba15a56d339e5bd26dc164a5423d126808a5fb6204c4cc12eaccd462bb',
     'client_secret': '3b3182c33c9718b14bd0a54d60446cc743385fa75479ec87a94ef47542b76090',
     'refresh_token': '09b1eb4aca647a280c37fb77423d79ed70aafc23'
     }

ls = lightspeed_api.Lightspeed(c)

log_msg('...connected to Lightspeed')


# *************************
# ******* main body start ***********
# *************************

# download custlist,
# make loop structure
# make sublist with mail as false, cycle through ids and set to true
# advance page

# access Customer Endpoint, filter for Contact.noEmail=true as var cust
log_msg('ping Customer endpoint')
querylist = {"offset":"0", "limit": "100", 'load_relations' : "[\"Contact\"]", "Contact.noEmail": "true"}
cust = ls.get('Customer', parameters=querylist)
log_msg('Customer downloaded')
num_cust = int(cust['@attributes']['count'])
log_msg(str('num_cust: ' + str(num_cust)))
del cust['@attributes'] # remove [@attributes]

# writes customer query to json
if beta:
    write_json(cust, 'cust')
else:
    write_json(cust, str(scriptname + '-' + now.strftime('%Y%m%d%H%M')))


# loop through all cust and update to check all contact boxes
#print(cust['Customer'][1]['customerID']) # format for queried Customer
for x in cust['Customer']:
    log_msg(x['customerID'])
    c = ls.get(str('Customer/' + str(x['customerID'])))
    log_msg(c)

    formatted = {
        'Customer': {
            "Tags": {
                "tag": "jrm"
            },
            "Contact": {
                'noEmail': 'false',
                'noPhone': 'false',
                'noMail': 'false'}
        }
        }
    ls.update(str("Customer/" + str(x['customerID'])), formatted["Customer"])
    log_msg('updated')

# _____________________________________
# other query examples
#querylist = {"offset":"0", "limit": "100", 'firstName' : "Anne"}  #works
#querylist = {"offset":"0", "limit": "100", 'load_relations' : "[\"Contact\"]", "Contact.contactID": "146"} #works
#querylist = {"offset":"0", "limit": "100", 'load_relations' : "[\"Contact\"]", "Contact.noPhone": "false"} #works





# *************************
# ******* main body ended ***********
# *************************



# *************************
# ******* program ended ***********
# *************************
log_msg('program ended')
log.close()




