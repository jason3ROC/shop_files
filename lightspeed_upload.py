# *************************
# ******* Intro ***********
# *************************

# cust_mail_true v0.0.0
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
import json

# *************************
# ******* Log file initialize ***********
# *************************

# ********---->> set current folder <<--------*******
folder_name = r'C:\Users\jaymi\OneDrive\Documents\3ROC\logs'
os.chdir(folder_name)

# ********---->> set log <<--------*******
now = datetime.datetime.now()
beta = False #  True is testing, False is production and will label unique log file
if beta:
    logname = 'log.txt'
else:
    logname = 'log-' + now.strftime('%Y%m%d%H%M') + '.txt'
log = open(logname, mode='w')

# *************************
# ******* define functions ***********
# *************************
def log_msg (s):
    sm = now.strftime('%Y%m%d%H%M%S') + ': ' + s
    print(sm)
    log.write(sm + '\n')

log_msg('program started')


"""  *************************************************************************************************************
     ******************************     data_dump()  *******************************************************
     *************************************************************************************************************

     This function returns the json file from the lightspeed query
"""

def data_dump(item_,sname):
    # prints the item list from lightspeed api for debugging
    # create json object from dictionary
    json_item = json.dumps(item_)

    # open file for writing, "w"
    f = open(sname + "_ls_items.json", "w")

    # write json object to file
    f.write(json_item)
    log_msg('write json')

    # close file
    f.close()
    log_msg(f'json file written to {sname}_item_list.json')

    return json_item



"""  *************************************************************************************************************
         ******************************      tags_add()  *******************************************************
         *************************************************************************************************************

         This function connects to Lightspeed and adds multiple tags 
"""

def tags_add(ls_type, ID, tags, newtag):
    """
    receive ID and tags
    parse tags and format payload
    put tags to item matrix

    ls_type - type of item
    ID -
    tags -


    """
    log_msg('tags_add called')

    payload = list2xml(newtag, str2list(tags), ls_type)
    log_msg(str(payload))

    try:
        r = ls.add_tags(ls_type + "/" + str(ID), payload)
        time.sleep(1)

        try:
            payload = {'load_relations': "[\"TagRelations.Tag\"]"}
            item = ls.get(ls_type + '/' + str(ID), parameters=payload)
            s = str(item[ls_type]['Tags']['tag'])
            log_msg(f'item {ls_type}: {ID} - found tags to be s - {s}')
            if newtag in s:
                log_msg(f'item {ls_type}: {ID} - tagged as {newtag}')
            else:
                log_msg(f'item {ls_type}: {ID} - tag error at try loop')
        except:
            log_msg(f'item {ls_type}: {ID} - tag error after update')
            r = 0

    except:
        log_msg(f'item {ls_type}: {ID} - not tagged.')
        r=0

    return r


def str2list(s):

    if '[' in s:
        s = s.strip(',')
        s = s.replace(', ', '')
        s = s.replace('[', '')
        s = s.replace(']', '')
        s = s.replace('\'\'', '\'')
        s = s[1:-1]
        s = s.split(sep='\'')
    else:
        s = [s]


    print('s: ' + str(s))
    if type(s) == list:
        return s
    else:
        return ['']


def list2xml(newtag, taglist, ls_type):
    print('taglist: ' + str(taglist))
    # taglist = taglist.append([newtag])
    taglist.append(newtag)
    # taglist = taglist + newtag
    print('new taglist: ' + str(taglist))
    prefix = "<" + str(ls_type) + "><Tags>"
    suffix = "</Tags></" +str(ls_type) + ">"
    tags = ''
    for t in taglist:
        print(t)
        tags = tags + '<tag>' + str(t) + '</tag>'
    print('tags: ' + prefix + tags + suffix)

    return prefix + tags + suffix


""""# *************************
# ******* connect to Lightspeed API ***********
 ************************* """

# use the site below as key reference for API communication
#https://developers.lightspeedhq.com/retail/endpoints/Item/

log_msg('connecting to Lightspeed...')

# custom modification of https://pypi.org/project/lightspeed-api/
# added some mods since multi tagging can only be done in HTML not JSON uploads
import lightspeed_requests
import lightspeed_jrm

# get from OS file
c = {'account_id': '161824',
     'client_id': '06dc34ba15a56d339e5bd26dc164a5423d126808a5fb6204c4cc12eaccd462bb',
     'client_secret': '3b3182c33c9718b14bd0a54d60446cc743385fa75479ec87a94ef47542b76090',
     'refresh_token': 'e01d914401011883715fd705869894c04ad8a0cf'
     }

# create new instance of Lightspeed for item tagging
ls = lightspeed_requests.LightspeedRequests(c)

# create new instance of Lightspeed for item upload
ls1 = lightspeed_jrm.Lightspeed(c)

log_msg('...connected to Lightspeed')


# *************************
# ******* main body start ***********
# *************************

# define variables needed for upload

# variables from GoForm data
prod_desc = 'test product'
prod_csku = 12341234
prod_price = 12.34
vendor_contact = {'email' : 'jay.miller.mse@gmail.com', 'first' : 'Jason', 'last' : 'Miller'}
prod_form = 9876  # this is the go form number


# for vendor need to lookup master list to see if email address already linked to vendor profile
# if yes - use vendorID, if no, leave blank and new vendor created
payload = {'load_relations': "[\"Contact\"]"}
df_vendor = ls1.get('Vendor', parameters=payload)   # get master list of vendors
data_dump(df_vendor, 'vendors')
# !!! not all vendor profiles have email address
# match to email
# vendorID = ###   # match to vendorID
vendor_id = 1234


# !!! move this code after product creation
# create a 'list' of {'used','last_name', 'formID'}
# need to add tags after item creation (?)
prod_tags = str('used; test')
# example code, see function at bottom
# suspect that functiono reads a string = tag1; tag2; tag3
#prod_id = 111690
#r = tags_add('Item', str(prod_id), prod_tags)


# static variable
prod_cate = 1

# need to add quantity after item creation (?)
q = 1

formatted = {'Item':
{
      "defaultCost": "0",
      "discountable": "true",
      "tax": "false",
      "itemType": "default",
      "description": prod_desc,
      "customSku": prod_csku,
      "categoryID": prod_cate,
      "taxClassID": "1",
      "itemMatrixID": "0",
      "defaultVendorID": vendor_id,
      "Prices": {
      "ItemPrice": [
        {
          "amount": prod_price,
          "useTypeID": "1",
          "useType": "Default"
        },
        {
          "amount": prod_price,
          "useTypeID": "2",
          "useType": "MSRP"
        },
        {
          "amount": prod_price,
          "useTypeID": "3",
          "useType": "Online"
        }
      ]}
}
}

# upload item to Lightspeed
# item = ls1.create("Item", formatted["Item"])  #code works so I commented to stop adding products

# VERIFY - if item status code is 200 then good


# TEST CODE - get item ID and dump JSON
payload = {'load_relations': "[\"ItemShops\"]"}
df_item = ls1.get('Item/118248', parameters=payload)   # get master list of vendors
data_dump(df_item, 'items')

# add quantity to item
# item = ls.create("Item", formatted["Item"])
formatted = {"ItemShops": {"ItemShop": {"itemShopID": 745048, "qoh": 12}}}
item = ls1.update("Item/118248", formatted)

# https://developers.lightspeedhq.com/retail/tutorials/inventory/#adjusting-itemshops-directly

# VERIFY - if item status code is 200 then good


# add tags to item
# !!! move this code after product creation
# create a 'list' of {'used','last_name', 'formID'}
# need to add tags after item creation (?)
prod_tags = str('used; test')
# example code, see function at bottom
# suspect that functiono reads a string = tag1; tag2; tag3
prod_id = 118248
r = tags_add('Item', str(prod_id), prod_tags, prod_form)


# VERIFY - if item status code is 200 then good



# *************************
# ******* main body ended ***********
# *************************



# *************************
# ******* program ended ***********
# *************************
log_msg('program ended')







