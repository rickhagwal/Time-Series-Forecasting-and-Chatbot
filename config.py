###################################################################
######## Configuration files for Bot   ##########################
###################################################################

"""
    config.py 
    
    This files has all the configurations for your bot.
    
"""

import os
import ibm_watson
from slackclient import SlackClient
import mysql.connector
from mysql.connector import Error

location = "/Users/Richa.Khagwal/Downloads/TWG_Bot (2)/TWG_Bot/"  # replace with the full folder path where you downloaded the github repo

###################################################################
######## Slack configuration   ##########################
###################################################################


SLACK_BOT_TOKEN='******'
SLACK_VERIFICATION_TOKEN='******' 

# instantiate Slack client
slack_client = SlackClient(SLACK_BOT_TOKEN) # do not change this parameter

###################################################################
######## Watson service configuration   ##########################
###################################################################

service = ibm_watson.AssistantV1(
    iam_apikey = '*********', # replace with Password
    version = '2018-09-20'
)
workspace_id = '**********' # replace with Assistant ID

###################################################################
######## MySQL Database connection   ##########################
###################################################################

try:
    conn = mysql.connector.connect(host="localhost",
                user="root",
                password="Twg@1*****!",  
                database="sc_data")
    if conn.is_connected():
        print('Connected to MySQL database')
    else:
        print("nope")
except Error as e:
    print(e)

###################################################################
######## Log files configuration   ##########################
###################################################################

log_commands_path = location + "logs/log_commands.py" # do not change this parameter
follow_up_path = location + "logs/followup_email.py" # do not change this parameter

###################################################################
######## Temp files configuration   ##########################
###################################################################

onetime_path = location + "nlp/nlp_solutions/onetime_run_file.py" # do not change this parameter
onetime_file = location + "nlp/nlp_solutions/onetime.txt" # do not change this parameter
