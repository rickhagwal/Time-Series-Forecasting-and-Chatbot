###################################################################
######## NLP analysis   ###########################################
###################################################################

"""

    nlp_commands.py
    
    This file handles three things,
    
    1. IBM watson api calls
    2. Custom NLP functions (nlp_solutions)
    3. Talk to backend system to retrieve data
    
    Once all the processing is completed, it sends the output back to main program.

"""

import os,sys
sys.path.append(os.path.normpath(os.getcwd()))
import random
import calendar
from config import service, workspace_id, location,conn
import pandas as pd
import numpy as np
import datetime
from matplotlib import pyplot as plt
import seaborn as sns
import matplotlib.pylab as pl
from slack_commands import slack_tiles, message_buttons,file_upload

def is_not_empty(any_structure):
    if any_structure:
        print('Structure is not empty.')
        return True
    else:
        print('Structure is empty.')
        return False



def handle_command(message, channel, message_user,context):
    """
        NLP analysis on top of the conversation
    """
    print("handle_command:: ")
    print("message:: ",message)
    print("channel:: ",channel)
    print("message_user:: ",message_user)
    print("context:: ",context)
    current_action = '' # Intialize current action to empty
    slack_output = ''   # Intialize Slack output to empty
    
    print("service ",service)
    print("workspace_id ",workspace_id)
    print("location ",location)
  # Send message to Assistant service.
    response = service.message(
    workspace_id = workspace_id,
    input = {'text': message},
    context = context).get_result()
    print("response::::: ",response)
       
    try:
        slack_output = ''.join(response['output']['text'])
    except:
        slack_output = ''
    print('slack_output:: ',slack_output)
  # Update the stored context with the latest received from the dialog.
    context = response['context']
    print(context, response)
    ###############################################################
    ###########  Idenify search term  ###########
    ###############################################################
    
#     try:
#         search_key = response['entities'][0]['value']
#     except:
#         search_key = ''
    
#     try:
#         search_term = str(response['context']['brand_name'])    
#     except:
#         search_term = ''
    try:
        brand = str(response['context']['brand'])    
    except:
        brand = ''
    try:
        size = str(response['context']['size'])    
    except:
        size = ''    
    try:
        varietal = str(response['context']['varietal'])    
    except:
        varietal = ''
    try:
        year = str(response['context']['year'])    
    except:
        year = ''    
    try:
        month = str(response['context']['month'])    
    except:
        month = ''
    try:
        number = str(response['context']['number'])    
    except:
        number = ''
    try:
        year1 = str(response['context']['year1'])    
    except:
        year1 = ''
    try:
        year2 = str(response['context']['year2'])    
    except:
        year2 = ''
    #######################################code starts#######################################
    
    try:
        plant = response['context']['plant']
    except:
        plant = None
    try:
        chart_type = response['context']['chart_type']
    except:
        chart_type = None
    print('brand ',brand)
    print('size ',size)
    print('varietal ',varietal)
    print('year ',year)
    print('month ',month)
    print('number ',number)
    print('plant ',plant)
    #print('masterCodeValue ',masterCodeValue)
    print('chart_type ',chart_type)
    
    if plant =="SC":
        plant_full = "Livermore"
    elif plant == "SR":
        plant_full ="Ripon"
    elif plant =="W":
        plant_full ="Westfield"
    else:
        plant_full = "all"
    print('plant_full ',plant_full)
    
    ####################################### code ends#######################################
    
    print(brand)
    print(size)
    print(varietal)
    print(year)
    print(month)
    print(number)
    print(year1)
    print(year2)
    res = ''
    
    ###############################################################
    ###########  data search  ###########
    ###############################################################
    
    
    
    
    
    #############################forecast with all variables##################################
    
    try:
        if response['context']['currentIntent'] == 'forecast' and brand.strip() != '' and size.strip() != '' and varietal.strip() != '' and year.strip() != '' and month.strip() != '':
                curr= conn.cursor()
                curr.execute("select sum(`forecast`.`Quantity`) from botdb.forecast inner join botdb.masterdb on `forecast`.`master`=`masterdb`.`Cat Cd10 Description` where `masterdb`.`Brand Description`= '%s' and `masterdb`.`Varietal/ Flavor Description`= '%s' and `masterdb`.`Size Description`= '%s' and year(`forecast`.`Date`)=%d and month(`forecast`.`Date`)=%d;"%(brand,varietal,size,int(year),int(month)))
                quantity= curr.fetchall()
                res = ("The Sales Forecast for %s %s %s for %s %s is %d"%(brand,varietal,size,calendar.month_name[int(month)],year,int(quantity[0][0])))
                response['context']['brand']=None
                response['context']['varietal']=None
                response['context']['month']=None
                response['context']['year']=None
                response['context']['size']=None
                response['context']['currentIntent']=None
    except:
        pass
    
     #############################forecast for brand size varietal and year##################################
    
    try:
        if response['context']['currentIntent'] == 'forecast' and brand.strip() != '' and size.strip() != '' and varietal.strip() != '' and year.strip() != '' and month.strip() == '':  
            curr= conn.cursor()
            curr.execute("select Date,sum(`forecast`.`Quantity`) from botdb.forecast inner join botdb.masterdb on `forecast`.`master`=`masterdb`.`Cat Cd10 Description` where `masterdb`.`Brand Description`= '%s' and `masterdb`.`Varietal/ Flavor Description`= '%s' and `masterdb`.`Size Description`= '%s' and year(`forecast`.`Date`)=%d group by Date;"%(brand,varietal,size,int(year)))
            print("sql done")
            quantity= curr.fetchall()
            curr.execute("select sum(`forecast`.`Quantity`) from botdb.forecast inner join botdb.masterdb on `forecast`.`master`=`masterdb`.`Cat Cd10 Description` where `masterdb`.`Brand Description`= '%s' and `masterdb`.`Varietal/ Flavor Description`= '%s' and `masterdb`.`Size Description`= '%s' and year(`forecast`.`Date`)=%d;"%(brand,varietal,size,int(year)))
            cumsum=curr.fetchall()
            resu = [[ i for i, j in quantity ],[ j for i, j in quantity ]]
            data=pd.DataFrame(resu)
            data=data.transpose()
            data.columns=['date','quantity']
            data=data.sort_values(by='date')
            data.date=data.date.apply(lambda x: x.strftime("%b %y"))
            plt.plot(data.date.values, data.quantity.values,"r-")
            plt.tick_params(axis='x',which='both',bottom=False,top=False,labelbottom=False)
            plt.grid(True, linestyle='-.')
            cellText = [data.quantity.values]
            the_table = plt.table(cellText=cellText, rowLoc='right', rowLabels=['shipment'],
                             colLabels=data.date.values,
                             colLoc='center', loc='bottom')
            plt.savefig("tablegraph.jpg")
            res = ("The Sales Forecast for %s %s %s for %s is %d"%(brand, varietal,size,year,int(cumsum[0][0])))
            img="tablegraph.jpg"
            file_upload(channel,img)
            
            response['context']['brand']=None
            response['context']['varietal']=None
            response['context']['month']=None
            response['context']['year']=None
            response['context']['size']=None
            response['context']['currentIntent']=None
    except:
        pass
    
    #############################forecast for brand varietal and year##################################
    
    try:
        if response['context']['currentIntent'] == 'forecast' and brand.strip() != '' and size.strip() == '' and varietal.strip() != '' and year.strip() != '' and month.strip() == '':  
            curr= conn.cursor()
            curr.execute("select Date,sum(`forecast`.`Quantity`) from botdb.forecast inner join botdb.masterdb on `forecast`.`master`=`masterdb`.`Cat Cd10 Description` where `masterdb`.`Brand Description`= '%s' and `masterdb`.`Varietal/ Flavor Description`= '%s' and year(`forecast`.`Date`)=%d group by Date;"%(brand,varietal,int(year)))
            print("sql done")
            quantity= curr.fetchall()
            curr.execute("select sum(`forecast`.`Quantity`) from botdb.forecast inner join botdb.masterdb on `forecast`.`master`=`masterdb`.`Cat Cd10 Description` where `masterdb`.`Brand Description`= '%s' and `masterdb`.`Varietal/ Flavor Description`= '%s' and year(`forecast`.`Date`)=%d;"%(brand,varietal,int(year)))
            cumsum=curr.fetchall()
            resu = [[ i for i, j in quantity ],[ j for i, j in quantity ]]
            data=pd.DataFrame(resu)
            data=data.transpose()
            data.columns=['date','quantity']
            data=data.sort_values(by='date')
            data.date=data.date.apply(lambda x: x.strftime("%b %y"))
            plt.plot(data.date.values, data.quantity.values,"b-")
            plt.tick_params(axis='x',which='both',bottom=False,top=False,labelbottom=False)
            plt.grid(True, linestyle='-.')
            cellText = [data.quantity.values]
            the_table = plt.table(cellText=cellText, rowLoc='right', rowLabels=['shipment'],
                             colLabels=data.date.values,
                             colLoc='center', loc='bottom')
            plt.savefig("tablegraph.jpg", dpi=300)
            res = ("The Sales Forecast for %s %s for %s is %d"%(brand, varietal,year,int(cumsum[0][0])))
            img="tablegraph.jpg"
            file_upload(channel,img)
            plt.close()
            response['context']['brand']=None
            response['context']['varietal']=None
            response['context']['month']=None
            response['context']['year']=None
            response['context']['size']=None
            response['context']['currentIntent']=None
    except:
        pass
  
    #############################forecast for brand size and year##################################
    
    try:
        if response['context']['currentIntent'] == 'forecast' and brand.strip() != '' and size.strip() != '' and varietal.strip() == '' and year.strip() != '' and month.strip() == '':  
            curr= conn.cursor()
            curr.execute("select Date,sum(`forecast`.`Quantity`) from botdb.forecast inner join botdb.masterdb on `forecast`.`master`=`masterdb`.`Cat Cd10 Description` where `masterdb`.`Brand Description`= '%s' and `masterdb`.`Size Description`= '%s' and year(`forecast`.`Date`)=%d group by Date;"%(brand,size,int(year)))
            print("sql done")
            quantity= curr.fetchall()
            curr.execute("select sum(`forecast`.`Quantity`) from botdb.forecast inner join botdb.masterdb on `forecast`.`master`=`masterdb`.`Cat Cd10 Description` where `masterdb`.`Brand Description`= '%s' and `masterdb`.`Size Description`= '%s' and year(`forecast`.`Date`)=%d;"%(brand,size,int(year)))
            cumsum=curr.fetchall()
            resu = [[ i for i, j in quantity ],[ j for i, j in quantity ]]
            data=pd.DataFrame(resu)
            data=data.transpose()
            data.columns=['date','quantity']
            data=data.sort_values(by='date')
            data.date=data.date.apply(lambda x: x.strftime("%b %y"))
            plt.plot(data.date.values, data.quantity.values,"k-")
            plt.tick_params(axis='x',which='both',bottom=False,top=False,labelbottom=False)
            plt.grid(True, linestyle='-.')
            cellText = [data.quantity.values]
            the_table = plt.table(cellText=cellText, rowLoc='right', rowLabels=['shipment'],
                             colLabels=data.date.values,
                             colLoc='center', loc='bottom')
            plt.savefig("tablegraph.jpg")
            res = ("The Sales Forecast for %s %s for %s is %d"%(brand,size,year,int(cumsum[0][0])))
            img="tablegraph.jpg"
            file_upload(channel,img)
            plt.close()
            response['context']['brand']=None
            response['context']['varietal']=None
            response['context']['month']=None
            response['context']['year']=None
            response['context']['size']=None
            response['context']['currentIntent']=None
    except:
        pass
 

    #############################forecast for brand and year##################################
    
    try:
        if response['context']['currentIntent'] == 'forecast' and brand.strip() != '' and size.strip() == '' and varietal.strip() == '' and year.strip() != '' and month.strip() == '':  
            curr= conn.cursor()
            curr.execute("select Date,sum(`forecast`.`Quantity`) from botdb.forecast inner join botdb.masterdb on `forecast`.`master`=`masterdb`.`Cat Cd10 Description` where `masterdb`.`Brand Description`= '%s' and year(`forecast`.`Date`)=%d group by Date;"%(brand,int(year)))
            print("sql done")
            quantity= curr.fetchall()
            curr.execute("select sum(`forecast`.`Quantity`) from botdb.forecast inner join botdb.masterdb on `forecast`.`master`=`masterdb`.`Cat Cd10 Description` where `masterdb`.`Brand Description`= '%s' and year(`forecast`.`Date`)=%d;"%(brand,int(year)))
            cumsum=curr.fetchall()
            resu = [[ i for i, j in quantity ],[ j for i, j in quantity ]]
            data=pd.DataFrame(resu)
            data=data.transpose()
            data.columns=['date','quantity']
            data=data.sort_values(by='date')
            data.date=data.date.apply(lambda x: x.strftime("%b %y"))
            plt.plot(data.date.values, data.quantity.values,"g-")
            plt.tick_params(axis='x',which='both',bottom=False,top=False,labelbottom=False)
            plt.grid(True, linestyle='-.')
            cellText = [data.quantity.values]
            the_table = plt.table(cellText=cellText, rowLoc='right', rowLabels=['shipment'],
                             colLabels=data.date.values,
                             colLoc='center', loc='bottom')
            plt.savefig("tablegraph.jpg", dpi=300)
            res = ("The Sales Forecast for %s for %s is %d"%(brand,year,int(cumsum[0][0])))
            img="tablegraph.jpg"
            file_upload(channel,img)
            plt.close()
            response['context']['brand']=None
            response['context']['varietal']=None
            response['context']['month']=None
            response['context']['year']=None
            response['context']['size']=None
            response['context']['currentIntent']=None
    except:
        pass

    #############################forecast for size and year##################################
    
    try:
        if response['context']['currentIntent'] == 'forecast' and brand.strip() == '' and size.strip() != '' and varietal.strip() == '' and year.strip() != '' and month.strip() == '':  
            curr= conn.cursor()
            curr.execute("select Date,sum(`forecast`.`Quantity`) from botdb.forecast inner join botdb.masterdb on `forecast`.`master`=`masterdb`.`Cat Cd10 Description` where `masterdb`.`Size Description`= '%s' and year(`forecast`.`Date`)=%d group by Date;"%(size,int(year)))
            print("sql done")
            quantity= curr.fetchall()
            curr.execute("select sum(`forecast`.`Quantity`) from botdb.forecast inner join botdb.masterdb on `forecast`.`master`=`masterdb`.`Cat Cd10 Description` where `masterdb`.`Size Description`= '%s' and year(`forecast`.`Date`)=%d;"%(size,int(year)))
            cumsum=curr.fetchall()
            resu = [[ i for i, j in quantity ],[ j for i, j in quantity ]]
            data=pd.DataFrame(resu)
            data=data.transpose()
            data.columns=['date','quantity']
            data=data.sort_values(by='date')
            data.date=data.date.apply(lambda x: x.strftime("%b %y"))
            plt.plot(data.date.values, data.quantity.values,"r-")
            plt.tick_params(axis='x',which='both',bottom=False,top=False,labelbottom=False)
            plt.grid(True, linestyle='-.')
            cellText = [data.quantity.values]
            the_table = plt.table(cellText=cellText, rowLoc='right', rowLabels=['shipment'],
                             colLabels=data.date.values,
                             colLoc='center', loc='bottom')
            plt.savefig("tablegraph.jpg")
            res = ("The Sales Forecast for %s for %s is %d"%(size,year,int(cumsum[0][0])))
            img="tablegraph.jpg"
            file_upload(channel,img)
            plt.close()
            response['context']['brand']=None
            response['context']['varietal']=None
            response['context']['month']=None
            response['context']['year']=None
            response['context']['size']=None
            response['context']['currentIntent']=None
    except:
        pass
    
    #############################forecast for varietal and year##################################
    
    try:
        if response['context']['currentIntent'] == 'forecast' and brand.strip() == '' and size.strip() == '' and varietal.strip() != '' and year.strip() != '' and month.strip() == '':  
            curr= conn.cursor()
            curr.execute("select Date,sum(`forecast`.`Quantity`) from botdb.forecast inner join botdb.masterdb on `forecast`.`master`=`masterdb`.`Cat Cd10 Description` where `masterdb`.`Varietal/ Flavor Description`= '%s' and year(`forecast`.`Date`)=%d group by Date;"%(varietal,int(year)))
            print("sql done")
            quantity= curr.fetchall()
            curr.execute("select sum(`forecast`.`Quantity`) from botdb.forecast inner join botdb.masterdb on `forecast`.`master`=`masterdb`.`Cat Cd10 Description` where `masterdb`.`Varietal/ Flavor Description`= '%s' and year(`forecast`.`Date`)=%d;"%(varietal,int(year)))
            cumsum=curr.fetchall()
            resu = [[ i for i, j in quantity ],[ j for i, j in quantity ]]
            data=pd.DataFrame(resu)
            data=data.transpose()
            data.columns=['date','quantity']
            data=data.sort_values(by='date')
            data.date=data.date.apply(lambda x: x.strftime("%b %y"))
            plt.plot(data.date.values, data.quantity.values,"c-")
            plt.tick_params(axis='x',which='both',bottom=False,top=False,labelbottom=False)
            plt.grid(True, linestyle='-.')
            cellText = [data.quantity.values]
            the_table = plt.table(cellText=cellText, rowLoc='right', rowLabels=['shipment'],
                             colLabels=data.date.values,
                             colLoc='center', loc='bottom')
            plt.savefig("tablegraph.jpg")
            res = ("The Sales Forecast for %s for %s is %d"%(varietal,year,int(cumsum[0][0])))
            img="tablegraph.jpg"
            file_upload(channel,img)
            plt.close()
            response['context']['brand']=None
            response['context']['varietal']=None
            response['context']['month']=None
            response['context']['year']=None
            response['context']['size']=None
            response['context']['currentIntent']=None
    except:
        pass    
    
    #############################forecast for different cobinations with  month and year##################################
    
    try:
        if response['context']['currentIntent'] == 'forecast' and year.strip() != '' and month.strip() != '':
            print("entered year month block")
            if brand.strip()=='' and size.strip=='' and varietal.strip()=='':
                curr.execute("select sum(`forecast`.`Quantity`) from botdb.forecast inner join botdb.masterdb on `forecast`.`master`=`masterdb`.`Cat Cd10 Description` where year(`forecast`.`Date`)=%d and month(`forecast`.`Date`)=%d;"%(int(year),int(month)))
                print("sql done")
                quantity= curr.fetchall()
                
                res = ("The Sales Forecast for %s %s is %d"%(calendar.month_name[int(month)],year,int(quantity[0][0])))

            elif brand.strip()!='' and size.strip!='' and varietal.strip()=='':
                curr= conn.cursor()
                curr.execute("select sum(`forecast`.`Quantity`) from botdb.forecast inner join botdb.masterdb on `forecast`.`master`=`masterdb`.`Cat Cd10 Description` where `masterdb`.`Brand Description`= '%s' and `masterdb`.`Size Description`= '%s' and year(`forecast`.`Date`)=%d and month(`forecast`.`Date`)=%d;"%(brand,size,int(year),int(month)))
                quantity= curr.fetchall()
                res = ("The Sales Forecast for %s %s for %s %s is %d"%(brand,size,calendar.month_name[int(month)],year,int(quantity[0][0])))
            elif brand.strip()!='' and size.strip=='' and varietal.strip()=='':
                print("sql done")
                curr= conn.cursor()
                curr.execute("select sum(`forecast`.`Quantity`) from botdb.forecast inner join botdb.masterdb on `forecast`.`master`=`masterdb`.`Cat Cd10 Description` where `masterdb`.`Brand Description`= '%s' and year(`forecast`.`Date`)=%d and month(`forecast`.`Date`)=%d;"%(brand,int(year),int(month)))
                quantity= curr.fetchall()
                res = ("The Sales Forecast for %s for %s %s is %d"%(brand,calendar.month_name[int(month)],year,int(quantity[0][0])))
                    
            elif brand.strip()!='' and size.strip=='' and varietal.strip()!='':
                curr= conn.cursor()
                curr.execute("select sum(`forecast`.`Quantity`) from botdb.forecast inner join botdb.masterdb on `forecast`.`master`=`masterdb`.`Cat Cd10 Description` where `masterdb`.`Brand Description`= '%s' and `masterdb`.`Varietal/ Flavor Description`= '%s' and year(`forecast`.`Date`)=%d and month(`forecast`.`Date`)=%d;"%(brand,varietal,int(year),int(month)))
                quantity= curr.fetchall()
                res = ("The Sales Forecast for %s %s for %s %s is %d"%(brand,varietal,calendar.month_name[int(month)],year,int(quantity[0][0])))
            
            elif brand.strip()=='' and size.strip!='' and varietal.strip()=='':
                curr= conn.cursor()
                curr.execute("select sum(`forecast`.`Quantity`) from botdb.forecast inner join botdb.masterdb on `forecast`.`master`=`masterdb`.`Cat Cd10 Description` where `masterdb`.`Size Description`= '%s'and year(`forecast`.`Date`)=%d and month(`forecast`.`Date`)=%d;"%(size,int(year),int(month)))
                quantity= curr.fetchall()
                res = ("The Sales Forecast for %s for %s %s is %d"%(size,calendar.month_name[int(month)],year,int(quantity[0][0])))
            
            elif brand.strip()=='' and size.strip!='' and varietal.strip()!='':
                curr= conn.cursor()
                curr.execute("select sum(`forecast`.`Quantity`) from botdb.forecast inner join botdb.masterdb on `forecast`.`master`=`masterdb`.`Cat Cd10 Description` where `masterdb`.`Size Description`= '%s' and `masterdb`.`Varietal/ Flavor Description`= '%s' and year(`forecast`.`Date`)=%d and month(`forecast`.`Date`)=%d;"%(size,varietal,int(year),int(month)))
                quantity= curr.fetchall()
                res = ("The Sales Forecast for %s %s for %s %s is %d"%(varietal,size,calendar.month_name[int(month)],year,int(quantity[0][0])))
            
            elif brand.strip()=='' and size.strip=='' and varietal.strip()!='':
                curr= conn.cursor()
                curr.execute("select sum(`forecast`.`Quantity`) from botdb.forecast inner join botdb.masterdb on `forecast`.`master`=`masterdb`.`Cat Cd10 Description` where `masterdb`.`Varietal/ Flavor Description`= '%s' and year(`forecast`.`Date`)=%d and month(`forecast`.`Date`)=%d;"%(varietal,int(year),int(month)))
                quantity= curr.fetchall()
                res = ("The Sales Forecast for %s for %s %s is %d"%(varietal,calendar.month_name[int(month)],year,int(quantity[0][0])))
            print("end main if block")    
            response['context']['brand']=None
            response['context']['varietal']=None
            response['context']['month']=None
            response['context']['year']=None
            response['context']['size']=None
            response['context']['currentIntent']=None
    except:
        pass
    

    #############################forecast for only year##################################
    
    try:
        if response['context']['currentIntent'] == 'forecast' and brand.strip() == '' and size.strip() == '' and varietal.strip() == '' and year.strip() != '' and month.strip() == '':  
            curr= conn.cursor()
            curr.execute("select Date,sum(`forecast`.`Quantity`) from botdb.forecast inner join botdb.masterdb on `forecast`.`master`=`masterdb`.`Cat Cd10 Description` where year(`forecast`.`Date`)=%d group by Date;"%(int(year)))
            print("sql done")
            quantity= curr.fetchall()
            curr.execute("select sum(`forecast`.`Quantity`) from botdb.forecast inner join botdb.masterdb on `forecast`.`master`=`masterdb`.`Cat Cd10 Description` where year(`forecast`.`Date`)=%d;"%(int(year)))
            cumsum=curr.fetchall()
            resu = [[ i for i, j in quantity ],[ j for i, j in quantity ]]
            data=pd.DataFrame(resu)
            data=data.transpose()
            data.columns=['date','quantity']
            data=data.sort_values(by='date')
            data.date=data.date.apply(lambda x: x.strftime("%b %y"))
            plt.plot(data.date.values, data.quantity.values,"b-")
            plt.tick_params(axis='x',which='both',bottom=False,top=False,labelbottom=False)
            plt.grid(True, linestyle='-.')
            cellText = [data.quantity.values]
            the_table = plt.table(cellText=cellText, rowLoc='right', rowLabels=['shipment'],
                             colLabels=data.date.values,
                             colLoc='center', loc='bottom')
            plt.savefig("tablegraph.jpg")
            res = ("The Sales Forecast for %s is %d"%(year,int(cumsum[0][0])))
            img="tablegraph.jpg"
            file_upload(channel,img)
            plt.close()
            response['context']['brand']=None
            response['context']['varietal']=None
            response['context']['month']=None
            response['context']['year']=None
            response['context']['size']=None
            response['context']['currentIntent']=None
    except:
        pass
    

    #############################future shipments for only brand and year##################################
    
    try:
        if response['context']['currentIntent'] == 'futureshipments' and brand.strip() != '' and size.strip() == '' and varietal.strip() == '' and year.strip() == '' and month.strip() == '':  
            curr= conn.cursor()
            curr.execute("select Date,sum(`forecast`.`Quantity`) from botdb.forecast inner join botdb.masterdb on `forecast`.`master`=`masterdb`.`Cat Cd10 Description` where `masterdb`.`Brand Description`= '%s' and year(`forecast`.`Date`)>=year(current_date()) and  month(`forecast`.`Date`)>=month(current_date()) group by Date;"%(brand))
            print("sql done")
            quantity= curr.fetchall()
            curr.execute("select sum(`forecast`.`Quantity`) from botdb.forecast inner join botdb.masterdb on `forecast`.`master`=`masterdb`.`Cat Cd10 Description` where `masterdb`.`Brand Description`= '%s' and year(`forecast`.`Date`)>=year(current_date()) and  month(`forecast`.`Date`)>=month(current_date());"%(brand))
            cumsum=curr.fetchall()
            resu = [[ i for i, j in quantity ],[ j for i, j in quantity ]]
            data=pd.DataFrame(resu)
            data=data.transpose()
            data.columns=['date','quantity']
            data=data.sort_values(by='date')
            data.quantity=data.quantity.astype(int)
            data.date=data.date.apply(lambda x: x.strftime("%b %y"))
            ind = np.arange(len(data.quantity))

            
            # Plot data on chart
            plt.plot(data.date, data.quantity,"r-")
            plt.tick_params(axis='x',which='both',bottom=False,top=False,labelbottom=False)
            plt.grid(True, linestyle='-.')
            cellText = [data.quantity]
            the_table = plt.table(cellText=cellText, rowLoc='right', rowLabels=['shipment'],
                             colLabels=data.date,
                             colLoc='center', loc='bottom')
            plt.savefig("tablegraph.jpg")
            #plt.show()
            res = ("The Future shipment for %s is %d"%(brand,int(cumsum[0][0])))
            img="tablegraph.jpg"
            file_upload(channel,img)
            plt.close()
            response['context']['brand']=None
            response['context']['varietal']=None
            response['context']['month']=None
            response['context']['year']=None
            response['context']['size']=None
            response['context']['currentIntent']=None
    except:
        pass   

    #############################future shipments for brand size and year##################################
    
    try:
        if response['context']['currentIntent'] == 'futureshipments' and brand.strip() != '' and size.strip() != '' and varietal.strip() == '' and year.strip() == '' and month.strip() == '':  
            curr= conn.cursor()
            curr.execute("select Date,sum(`forecast`.`Quantity`) from botdb.forecast inner join botdb.masterdb on `forecast`.`master`=`masterdb`.`Cat Cd10 Description` where `masterdb`.`Brand Description`= '%s'  and `masterdb`.`Size Description`= '%s' and year(`forecast`.`Date`)>=year(current_date()) and  month(`forecast`.`Date`)>=month(current_date()) group by Date;"%(brand,size))
            print("sql done")
            quantity= curr.fetchall()
            curr.execute("select sum(`forecast`.`Quantity`) from botdb.forecast inner join botdb.masterdb on `forecast`.`master`=`masterdb`.`Cat Cd10 Description` where `masterdb`.`Brand Description`= '%s'  and `masterdb`.`Size Description`= '%s' and year(`forecast`.`Date`)>=year(current_date()) and  month(`forecast`.`Date`)>=month(current_date());"%(brand,size))
            cumsum=curr.fetchall()
            resu = [[ i for i, j in quantity ],[ j for i, j in quantity ]]
            data=pd.DataFrame(resu)
            data=data.transpose()
            data.columns=['date','quantity']
            data=data.sort_values(by='date')
            data.quantity=data.quantity.astype(int)
            data.date=data.date.apply(lambda x: x.strftime("%b %y"))
            ind = np.arange(len(data.quantity))

            
            # Plot data on chart
            plt.plot(data.date, data.quantity,"r-")
            plt.tick_params(axis='x',which='both',bottom=False,top=False,labelbottom=False)
            plt.grid(True, linestyle='-.')
            cellText = [data.quantity]
            the_table = plt.table(cellText=cellText, rowLoc='right', rowLabels=['shipment'],
                             colLabels=data.date,
                             colLoc='center', loc='bottom')
            plt.savefig("tablegraph.jpg")
            #plt.show()
            res = ("The Future shipment for %s %s is %d"%(brand,size,int(cumsum[0][0])))
            img="tablegraph.jpg"
            file_upload(channel,img)
            plt.close()
            response['context']['brand']=None
            response['context']['varietal']=None
            response['context']['month']=None
            response['context']['year']=None
            response['context']['size']=None
            response['context']['currentIntent']=None
    except:
        pass
    
    #############################future shipments for brand varietal and year##################################
    
    try:
        if response['context']['currentIntent'] == 'futureshipments' and brand.strip() != '' and size.strip() == '' and varietal.strip() != '' and year.strip() == '' and month.strip() == '':  
            curr= conn.cursor()
            curr.execute("select Date,sum(`forecast`.`Quantity`) from botdb.forecast inner join botdb.masterdb on `forecast`.`master`=`masterdb`.`Cat Cd10 Description` where `masterdb`.`Brand Description`= '%s'  and `Varietal/ Flavor Description`= %s and year(`forecast`.`Date`)>=year(current_date()) and  month(`forecast`.`Date`)>=month(current_date()) group by Date;"%(brand,varietal))
            print("sql done")
            quantity= curr.fetchall()
            curr.execute("select sum(`forecast`.`Quantity`) from botdb.forecast inner join botdb.masterdb on `forecast`.`master`=`masterdb`.`Cat Cd10 Description` where `masterdb`.`Brand Description`= '%s'  and `Varietal/ Flavor Description`= %s and year(`forecast`.`Date`)>=year(current_date()) and  month(`forecast`.`Date`)>=month(current_date());"%(brand,varietal))
            cumsum=curr.fetchall()
            resu = [[ i for i, j in quantity ],[ j for i, j in quantity ]]
            data=pd.DataFrame(resu)
            data=data.transpose()
            data.columns=['date','quantity']
            data=data.sort_values(by='date')
            data.quantity=data.quantity.astype(int)
            data.date=data.date.apply(lambda x: x.strftime("%b %y"))
            ind = np.arange(len(data.quantity))

            
            # Plot data on chart
            plt.plot(data.date, data.quantity,"r-")
            plt.tick_params(axis='x',which='both',bottom=False,top=False,labelbottom=False)
            plt.grid(True, linestyle='-.')
            cellText = [data.quantity]
            the_table = plt.table(cellText=cellText, rowLoc='right', rowLabels=['shipment'],
                             colLabels=data.date,
                             colLoc='center', loc='bottom')
            plt.savefig("tablegraph.jpg")
            #plt.show()
            res = ("The Future shipment for %s %s is %d"%(brand,varietal,int(cumsum[0][0])))
            img="tablegraph.jpg"
            file_upload(channel,img)
            plt.close()
            response['context']['brand']=None
            response['context']['varietal']=None
            response['context']['month']=None
            response['context']['year']=None
            response['context']['size']=None
            response['context']['currentIntent']=None
    except:
        pass

    #############################future shipments for brand size varietal and year##################################
    
    try:
        if response['context']['currentIntent'] == 'futureshipments' and brand.strip() != '' and size.strip() != '' and varietal.strip() != '' and year.strip() == '' and month.strip() == '':  
            curr= conn.cursor()
            curr.execute("select Date,sum(`forecast`.`Quantity`) from botdb.forecast inner join botdb.masterdb on `forecast`.`master`=`masterdb`.`Cat Cd10 Description` where `masterdb`.`Brand Description`= '%s' and `masterdb`.`Size Description`= '%s'  and `Varietal/ Flavor Description`= %s and year(`forecast`.`Date`)>=year(current_date()) and  month(`forecast`.`Date`)>=month(current_date()) group by Date;"%(brand,size,varietal))
            print("sql done")
            quantity= curr.fetchall()
            curr.execute("select sum(`forecast`.`Quantity`) from botdb.forecast inner join botdb.masterdb on `forecast`.`master`=`masterdb`.`Cat Cd10 Description` where `masterdb`.`Brand Description`= '%s' and `masterdb`.`Size Description`= '%s' and `Varietal/ Flavor Description`= %s and year(`forecast`.`Date`)>=year(current_date()) and  month(`forecast`.`Date`)>=month(current_date());"%(brand,size,varietal))
            cumsum=curr.fetchall()
            resu = [[ i for i, j in quantity ],[ j for i, j in quantity ]]
            data=pd.DataFrame(resu)
            data=data.transpose()
            data.columns=['date','quantity']
            data=data.sort_values(by='date')
            data.quantity=data.quantity.astype(int)
            data.date=data.date.apply(lambda x: x.strftime("%b %y"))
            ind = np.arange(len(data.quantity))

            
            # Plot data on chart
            plt.plot(data.date, data.quantity,"r-")
            plt.tick_params(axis='x',which='both',bottom=False,top=False,labelbottom=False)
            plt.grid(True, linestyle='-.')
            cellText = [data.quantity]
            the_table = plt.table(cellText=cellText, rowLoc='right', rowLabels=['shipment'],
                             colLabels=data.date,
                             colLoc='center', loc='bottom')
            plt.savefig("tablegraph.jpg")
            #plt.show()
            res = ("The Future shipment for %s %s %s is %d"%(brand,varietal,size,int(cumsum[0][0])))
            img="tablegraph.jpg"
            file_upload(channel,img)
            plt.close()
            response['context']['brand']=None
            response['context']['varietal']=None
            response['context']['month']=None
            response['context']['year']=None
            response['context']['size']=None
            response['context']['currentIntent']=None
    except:
        pass

    #############################Rest of the year shipments for only brand##################################
    
    try:
        if response['context']['currentIntent'] == 'futureyearshipments' and brand.strip() != '' and size.strip() == '' and varietal.strip() == '' and year.strip() == '' and month.strip() == '':  
            curr= conn.cursor()
            curr.execute("select Date,sum(`forecast`.`Quantity`) from botdb.forecast inner join botdb.masterdb on `forecast`.`master`=`masterdb`.`Cat Cd10 Description` where `masterdb`.`Brand Description`= '%s' and year(`forecast`.`Date`)=year(current_date()) and  month(`forecast`.`Date`)>=month(current_date()) group by Date;"%(brand))
            print("sql done")
            quantity= curr.fetchall()
            curr.execute("select sum(`forecast`.`Quantity`) from botdb.forecast inner join botdb.masterdb on `forecast`.`master`=`masterdb`.`Cat Cd10 Description` where `masterdb`.`Brand Description`= '%s' and year(`forecast`.`Date`)=year(current_date()) and  month(`forecast`.`Date`)>=month(current_date());"%(brand))
            cumsum=curr.fetchall()
            resu = [[ i for i, j in quantity ],[ j for i, j in quantity ]]
            data=pd.DataFrame(resu)
            data=data.transpose()
            data.columns=['date','quantity']
            data=data.sort_values(by='date')
            data.quantity=data.quantity.astype(int)
            data.date=data.date.apply(lambda x: x.strftime("%b %y"))
            ind = np.arange(len(data.quantity))

            
            # Plot data on chart
            plt.plot(data.date, data.quantity,"r-")
            plt.tick_params(axis='x',which='both',bottom=False,top=False,labelbottom=False)
            plt.grid(True, linestyle='-.')
            cellText = [data.quantity.values]
            the_table = plt.table(cellText=cellText, rowLoc='right', rowLabels=['shipment'],
                             colLabels=data.date.values,
                             colLoc='center', loc='bottom')
            plt.savefig("tablegraph.jpg")
            #plt.show()
            res = ("The cumulative shipments for this year for %s is %d"%(brand,int(cumsum[0][0])))
            img="tablegraph.jpg"
            file_upload(channel,img)
            plt.close()
            response['context']['brand']=None
            response['context']['varietal']=None
            response['context']['month']=None
            response['context']['year']=None
            response['context']['size']=None
            response['context']['currentIntent']=None
    except:
        pass   

    #############################Rest of the year shipments for brand size##################################
    
    try:
        if response['context']['currentIntent'] == 'futureyearshipments' and brand.strip() != '' and size.strip() != '' and varietal.strip() == '' and year.strip() == '' and month.strip() == '':  
            curr= conn.cursor()
            curr.execute("select Date,sum(`forecast`.`Quantity`) from botdb.forecast inner join botdb.masterdb on `forecast`.`master`=`masterdb`.`Cat Cd10 Description` where `masterdb`.`Brand Description`= '%s'  and `masterdb`.`Size Description`= '%s' and year(`forecast`.`Date`)=year(current_date()) and  month(`forecast`.`Date`)>=month(current_date()) group by Date;"%(brand,size))
            print("sql done")
            quantity= curr.fetchall()
            curr.execute("select sum(`forecast`.`Quantity`) from botdb.forecast inner join botdb.masterdb on `forecast`.`master`=`masterdb`.`Cat Cd10 Description` where `masterdb`.`Brand Description`= '%s'  and `masterdb`.`Size Description`= '%s' and year(`forecast`.`Date`)=year(current_date()) and  month(`forecast`.`Date`)>=month(current_date());"%(brand,size))
            cumsum=curr.fetchall()
            resu = [[ i for i, j in quantity ],[ j for i, j in quantity ]]
            data=pd.DataFrame(resu)
            data=data.transpose()
            data.columns=['date','quantity']
            data=data.sort_values(by='date')
            data.quantity=data.quantity.astype(int)
            data.date=data.date.apply(lambda x: x.strftime("%b %y"))
            ind = np.arange(len(data.quantity))

            
            # Plot data on chart
            plt.plot(data.date, data.quantity,"r-")
            plt.tick_params(axis='x',which='both',bottom=False,top=False,labelbottom=False)
            plt.grid(True, linestyle='-.')
            cellText = [data.quantity.values]
            the_table = plt.table(cellText=cellText, rowLoc='right', rowLabels=['shipment'],
                             colLabels=data.date.values,
                             colLoc='center', loc='bottom')
            plt.savefig("tablegraph.jpg")
            #plt.show()
            res = ("The cumulative shipments for this year for %s %s is %d"%(brand,size,int(cumsum[0][0])))
            img="tablegraph.jpg"
            file_upload(channel,img)
            plt.close()
            response['context']['brand']=None
            response['context']['varietal']=None
            response['context']['month']=None
            response['context']['year']=None
            response['context']['size']=None
            response['context']['currentIntent']=None
    except:
        pass
    
    #############################Rest of the year shipments for brand varietal##################################
    
    try:
        if response['context']['currentIntent'] == 'futureyearshipments' and brand.strip() != '' and size.strip() == '' and varietal.strip() != '' and year.strip() == '' and month.strip() == '':  
            curr= conn.cursor()
            curr.execute("select Date,sum(`forecast`.`Quantity`) from botdb.forecast inner join botdb.masterdb on `forecast`.`master`=`masterdb`.`Cat Cd10 Description` where `masterdb`.`Brand Description`= '%s'  and `Varietal/ Flavor Description`= '%s'  and year(`forecast`.`Date`)=year(current_date()) and  month(`forecast`.`Date`)>=month(current_date()) group by Date;"%(brand,varietal))
            print("sql done")
            quantity= curr.fetchall()
            curr.execute("select sum(`forecast`.`Quantity`) from botdb.forecast inner join botdb.masterdb on `forecast`.`master`=`masterdb`.`Cat Cd10 Description` where `masterdb`.`Brand Description`= '%s'  and `Varietal/ Flavor Description`= '%s'  and year(`forecast`.`Date`)=year(current_date()) and  month(`forecast`.`Date`)>=month(current_date());"%(brand,varietal))
            cumsum=curr.fetchall()
            resu = [[ i for i, j in quantity ],[ j for i, j in quantity ]]
            data=pd.DataFrame(resu)
            data=data.transpose()
            data.columns=['date','quantity']
            data=data.sort_values(by='date')
            data.quantity=data.quantity.astype(int)
            data.date=data.date.apply(lambda x: x.strftime("%b %y"))
            ind = np.arange(len(data.quantity))

            
            # Plot data on chart
            plt.plot(data.date, data.quantity,"r-")
            plt.tick_params(axis='x',which='both',bottom=False,top=False,labelbottom=False)
            plt.grid(True, linestyle='-.')
            cellText = [data.quantity.values]
            the_table = plt.table(cellText=cellText, rowLoc='right', rowLabels=['shipment'],
                             colLabels=data.date.values,
                             colLoc='center', loc='bottom')
            plt.savefig("tablegraph.jpg")
            #plt.show()
            res = ("The cumulative shipments for this year for %s %s is %d"%(brand,varietal,int(cumsum[0][0])))
            img="tablegraph.jpg"
            file_upload(channel,img)
            plt.close()
            response['context']['brand']=None
            response['context']['varietal']=None
            response['context']['month']=None
            response['context']['year']=None
            response['context']['size']=None
            response['context']['currentIntent']=None
    except:
        pass

    #############################Rest of the year shipments for brand size varietal ##################################
    
    try:
        if response['context']['currentIntent'] == 'futureyearshipments' and brand.strip() != '' and size.strip() != '' and varietal.strip() != '' and year.strip() == '' and month.strip() == '':  
            curr= conn.cursor()
            curr.execute("select Date,sum(`forecast`.`Quantity`) from botdb.forecast inner join botdb.masterdb on `forecast`.`master`=`masterdb`.`Cat Cd10 Description` where `masterdb`.`Brand Description`= '%s' and `masterdb`.`Size Description`= '%s'  and `Varietal/ Flavor Description`= '%s' and year(`forecast`.`Date`)=year(current_date()) and  month(`forecast`.`Date`)>=month(current_date()) group by Date;"%(brand,size,varietal))
            print("sql done")
            quantity= curr.fetchall()
            curr.execute("select sum(`forecast`.`Quantity`) from botdb.forecast inner join botdb.masterdb on `forecast`.`master`=`masterdb`.`Cat Cd10 Description` where `masterdb`.`Brand Description`= '%s' and `masterdb`.`Size Description`= '%s' and `Varietal/ Flavor Description`= '%s' and year(`forecast`.`Date`)=year(current_date()) and  month(`forecast`.`Date`)>=month(current_date());"%(brand,size,varietal))
            cumsum=curr.fetchall()
            resu = [[ i for i, j in quantity ],[ j for i, j in quantity ]]
            data=pd.DataFrame(resu)
            data=data.transpose()
            data.columns=['date','quantity']
            data=data.sort_values(by='date')
            data.quantity=data.quantity.astype(int)
            data.date=data.date.apply(lambda x: x.strftime("%b %y"))
            ind = np.arange(len(data.quantity))

            
            # Plot data on chart
            plt.plot(data.date, data.quantity,"b-")
            plt.tick_params(axis='x',which='both',bottom=False,top=False,labelbottom=False)
            plt.grid(True, linestyle='-.')
            cellText = [data.quantity.values]
            the_table = plt.table(cellText=cellText, rowLoc='right', rowLabels=['shipment'],
                             colLabels=data.date.values,
                             colLoc='center', loc='bottom')
            plt.savefig("tablegraph.jpg")
            #plt.show()
            res = ("The cumulative shipment for this year for %s %s %s is %d"%(brand,varietal,size,int(cumsum[0][0])))
            img="tablegraph.jpg"
            file_upload(channel,img)
            plt.close()
            response['context']['brand']=None
            response['context']['varietal']=None
            response['context']['month']=None
            response['context']['year']=None
            response['context']['size']=None
            response['context']['currentIntent']=None
    except:
        pass

    #############################Rest of the year shipments for size varietal ##################################
    
    try:
        if response['context']['currentIntent'] == 'futureyearshipments' and brand.strip() == '' and size.strip() != '' and varietal.strip() != '' and year.strip() == '' and month.strip() == '':  
            curr= conn.cursor()
            curr.execute("select Date,sum(`forecast`.`Quantity`) from botdb.forecast inner join botdb.masterdb on `forecast`.`master`=`masterdb`.`Cat Cd10 Description` where `masterdb`.`Size Description`= '%s'  and `Varietal/ Flavor Description`= '%s' and year(`forecast`.`Date`)=year(current_date()) and  month(`forecast`.`Date`)>=month(current_date()) group by Date;"%(size,varietal))
            print("sql done")
            quantity= curr.fetchall()
            curr.execute("select sum(`forecast`.`Quantity`) from botdb.forecast inner join botdb.masterdb on `forecast`.`master`=`masterdb`.`Cat Cd10 Description` where `masterdb`.`Size Description`= '%s' and `Varietal/ Flavor Description`= '%s' and year(`forecast`.`Date`)=year(current_date()) and  month(`forecast`.`Date`)>=month(current_date());"%(size,varietal))
            cumsum=curr.fetchall()
            resu = [[ i for i, j in quantity ],[ j for i, j in quantity ]]
            data=pd.DataFrame(resu)
            data=data.transpose()
            data.columns=['date','quantity']
            data=data.sort_values(by='date')
            data.quantity=data.quantity.astype(int)
            data.date=data.date.apply(lambda x: x.strftime("%b %y"))
            ind = np.arange(len(data.quantity))

            
            # Plot data on chart
            plt.plot(data.date, data.quantity,"g-")
            plt.tick_params(axis='x',which='both',bottom=False,top=False,labelbottom=False)
            plt.grid(True, linestyle='-.')
            cellText = [data.quantity.values]
            the_table = plt.table(cellText=cellText, rowLoc='right', rowLabels=['shipment'],
                             colLabels=data.date.values,
                             colLoc='center', loc='bottom')
            plt.savefig("tablegraph.jpg")
            #plt.show()
            res = ("The cumulative shipment for this year for %s %s is %d"%(varietal,size,int(cumsum[0][0])))
            img="tablegraph.jpg"
            file_upload(channel,img)
            plt.close()
            response['context']['brand']=None
            response['context']['varietal']=None
            response['context']['month']=None
            response['context']['year']=None
            response['context']['size']=None
            response['context']['currentIntent']=None
    except:
        pass

    #############################Rest of the year shipments for varietal ##################################
    
    try:
        if response['context']['currentIntent'] == 'futureyearshipments' and brand.strip() == '' and size.strip() == '' and varietal.strip() != '' and year.strip() == '' and month.strip() == '':  
            curr= conn.cursor()
            curr.execute("select Date,sum(`forecast`.`Quantity`) from botdb.forecast inner join botdb.masterdb on `forecast`.`master`=`masterdb`.`Cat Cd10 Description` where `Varietal/ Flavor Description`= '%s' and year(`forecast`.`Date`)=year(current_date()) and  month(`forecast`.`Date`)>=month(current_date()) group by Date;"%(varietal))
            print("sql done")
            quantity= curr.fetchall()
            curr.execute("select sum(`forecast`.`Quantity`) from botdb.forecast inner join botdb.masterdb on `forecast`.`master`=`masterdb`.`Cat Cd10 Description` where `Varietal/ Flavor Description`= '%s' and year(`forecast`.`Date`)=year(current_date()) and  month(`forecast`.`Date`)>=month(current_date());"%(varietal))
            cumsum=curr.fetchall()
            resu = [[ i for i, j in quantity ],[ j for i, j in quantity ]]
            data=pd.DataFrame(resu)
            data=data.transpose()
            data.columns=['date','quantity']
            data=data.sort_values(by='date')
            data.quantity=data.quantity.astype(int)
            data.date=data.date.apply(lambda x: x.strftime("%b %y"))
            ind = np.arange(len(data.quantity))

            
            # Plot data on chart
            plt.plot(data.date, data.quantity,"c-")
            plt.tick_params(axis='x',which='both',bottom=False,top=False,labelbottom=False)
            plt.grid(True, linestyle='-.')
            cellText = [data.quantity.values]
            the_table = plt.table(cellText=cellText, rowLoc='right', rowLabels=['shipment'],
                             colLabels=data.date.values,
                             colLoc='center', loc='bottom')
            plt.savefig("tablegraph.jpg")
            #plt.show()
            res = ("The cumulative shipment for this year for %s is %d"%(varietal,int(cumsum[0][0])))
            img="tablegraph.jpg"
            file_upload(channel,img)
            plt.close()
            response['context']['brand']=None
            response['context']['varietal']=None
            response['context']['month']=None
            response['context']['year']=None
            response['context']['size']=None
            response['context']['currentIntent']=None
    except:
        pass

    #############################Rest of the year shipments for size ##################################
    
    try:
        if response['context']['currentIntent'] == 'futureyearshipments' and brand.strip() == '' and size.strip() != '' and varietal.strip() == '' and year.strip() == '' and month.strip() == '':  
            curr= conn.cursor()
            curr.execute("select Date,sum(`forecast`.`Quantity`) from botdb.forecast inner join botdb.masterdb on `forecast`.`master`=`masterdb`.`Cat Cd10 Description` where `masterdb`.`Size Description`= '%s' and  year(`forecast`.`Date`)=year(current_date()) and  month(`forecast`.`Date`)>=month(current_date()) group by Date;"%(size))
            print("sql done")
            quantity= curr.fetchall()
            curr.execute("select sum(`forecast`.`Quantity`) from botdb.forecast inner join botdb.masterdb on `forecast`.`master`=`masterdb`.`Cat Cd10 Description` where `masterdb`.`Size Description`= '%s' and year(`forecast`.`Date`)=year(current_date()) and  month(`forecast`.`Date`)>=month(current_date());"%(size))
            cumsum=curr.fetchall()
            resu = [[ i for i, j in quantity ],[ j for i, j in quantity ]]
            data=pd.DataFrame(resu)
            data=data.transpose()
            data.columns=['date','quantity']
            data=data.sort_values(by='date')
            data.quantity=data.quantity.astype(int)
            data.date=data.date.apply(lambda x: x.strftime("%b %y"))
            ind = np.arange(len(data.quantity))

            
            # Plot data on chart
            plt.plot(data.date, data.quantity,"k-")
            plt.tick_params(axis='x',which='both',bottom=False,top=False,labelbottom=False)
            plt.grid(True, linestyle='-.')
            cellText = [data.quantity.values]
            the_table = plt.table(cellText=cellText, rowLoc='right', rowLabels=['shipment'],
                             colLabels=data.date.values,
                             colLoc='center', loc='bottom')
            plt.savefig("tablegraph.jpg")
            #plt.show()
            res = ("The cumulative shipment for this year for %s is %d"%(size,int(cumsum[0][0])))
            img="tablegraph.jpg"
            file_upload(channel,img)
            plt.close()
            response['context']['brand']=None
            response['context']['varietal']=None
            response['context']['month']=None
            response['context']['year']=None
            response['context']['size']=None
            response['context']['currentIntent']=None
    except:
        pass
     #############################current shipments for only brand and year##################################
    
    try:
        if response['context']['currentIntent'] == 'currentshipments' and brand.strip() != '' and size.strip() == '' and varietal.strip() == '' and year.strip() != '' and month.strip() == '':  
            curr= conn.cursor()
            curr.execute("select Date,sum(`forecast`.`Quantity`) from botdb.forecast inner join botdb.masterdb on `forecast`.`master`=`masterdb`.`Cat Cd10 Description` where `masterdb`.`Brand Description`= '%s' and if (year(current_date())>%d, year(`forecast`.`Date`)=%d ,year(`forecast`.`Date`)=%d and  month(`forecast`.`Date`)<month(current_date())) group by Date;"%(brand,int(year),int(year),int(year)))
            print("sql done")
            quantity= curr.fetchall()
            curr.execute("select sum(`forecast`.`Quantity`) from botdb.forecast inner join botdb.masterdb on `forecast`.`master`=`masterdb`.`Cat Cd10 Description` where `masterdb`.`Brand Description`= '%s' and if (year(current_date())>%d, year(`forecast`.`Date`)=%d ,year(`forecast`.`Date`)=%d and  month(`forecast`.`Date`)<month(current_date()));"%(brand,int(year),int(year),int(year)))
            cumsum=curr.fetchall()
            resu = [[ i for i, j in quantity ],[ j for i, j in quantity ]]
            data=pd.DataFrame(resu)
            data=data.transpose()
            data.columns=['date','quantity']
            data=data.sort_values(by='date')
            data.quantity=data.quantity.astype(int)
            data.date=data.date.apply(lambda x: x.strftime("%b %y"))
            ind = np.arange(len(data.quantity))


            # Plot data on chart
            plt.plot(data.date, data.quantity,"r-")
            plt.tick_params(axis='x',which='both',bottom=False,top=False,labelbottom=False)
            plt.grid(True, linestyle='-.')
            cellText = [data.quantity.values]
            the_table = plt.table(cellText=cellText, rowLoc='right', rowLabels=['shipment'],
                             colLabels=data.date.values,
                             colLoc='center', loc='bottom')
            plt.savefig("tablegraph.jpg")
            #plt.show()
            res = ("The shipment volume for %s for the year %d is %d"%(brand,int(year),int(cumsum[0][0])))
            img="tablegraph.jpg"
            file_upload(channel,img)
            plt.close()
            response['context']['brand']=None
            response['context']['varietal']=None
            response['context']['month']=None
            response['context']['year']=None
            response['context']['size']=None
            response['context']['currentIntent']=None
    except:
        pass

         #############################current shipments for only brand varietal and year##################################
    
    try:
        if response['context']['currentIntent'] == 'currentshipments' and brand.strip() != '' and size.strip() == '' and varietal.strip() != '' and year.strip() != '' and month.strip() == '':  
            curr= conn.cursor()
            curr.execute("select Date,sum(`forecast`.`Quantity`) from botdb.forecast inner join botdb.masterdb on `forecast`.`master`=`masterdb`.`Cat Cd10 Description` where `masterdb`.`Brand Description`= '%s' and `Varietal/ Flavor Description`= '%s' and if (year(current_date())>%d, year(`forecast`.`Date`)=%d ,year(`forecast`.`Date`)=%d and  month(`forecast`.`Date`)<month(current_date())) group by Date;"%(brand,varietal,int(year),int(year),int(year)))
            print("sql done")
            quantity= curr.fetchall()
            curr.execute("select sum(`forecast`.`Quantity`) from botdb.forecast inner join botdb.masterdb on `forecast`.`master`=`masterdb`.`Cat Cd10 Description` where `masterdb`.`Brand Description`= '%s' and `Varietal/ Flavor Description`= '%s'  and if (year(current_date())>%d, year(`forecast`.`Date`)=%d ,year(`forecast`.`Date`)=%d and  month(`forecast`.`Date`)<month(current_date()));"%(brand,varietal,int(year),int(year),int(year)))
            cumsum=curr.fetchall()
            resu = [[ i for i, j in quantity ],[ j for i, j in quantity ]]
            data=pd.DataFrame(resu)
            data=data.transpose()
            data.columns=['date','quantity']
            data=data.sort_values(by='date')
            data.quantity=data.quantity.astype(int)
            data.date=data.date.apply(lambda x: x.strftime("%b %y"))
            ind = np.arange(len(data.quantity))


            # Plot data on chart
            plt.plot(data.date, data.quantity,"r-")
            plt.tick_params(axis='x',which='both',bottom=False,top=False,labelbottom=False)
            plt.grid(True, linestyle='-.')
            cellText = [data.quantity.values]
            the_table = plt.table(cellText=cellText, rowLoc='right', rowLabels=['shipment'],
                             colLabels=data.date.values,
                             colLoc='center', loc='bottom')
            plt.savefig("tablegraph.jpg")
            #plt.show()
            res = ("The shipment volume for %s %s for the year %d is %d"%(brand,varietal,int(year),int(cumsum[0][0])))
            img="tablegraph.jpg"
            file_upload(channel,img)
            plt.close()
            response['context']['brand']=None
            response['context']['varietal']=None
            response['context']['month']=None
            response['context']['year']=None
            response['context']['size']=None
            response['context']['currentIntent']=None
    except:
        pass
    
         #############################current shipments for brand size and year##################################
    
    try:
        if response['context']['currentIntent'] == 'currentshipments' and brand.strip() != '' and size.strip() != '' and varietal.strip() == '' and year.strip() != '' and month.strip() == '':  
            curr= conn.cursor()
            curr.execute("select Date,sum(`forecast`.`Quantity`) from botdb.forecast inner join botdb.masterdb on `forecast`.`master`=`masterdb`.`Cat Cd10 Description` where `masterdb`.`Brand Description`= '%s' and `masterdb`.`Size Description`= '%s' and if (year(current_date())>%d, year(`forecast`.`Date`)=%d ,year(`forecast`.`Date`)=%d and  month(`forecast`.`Date`)<month(current_date())) group by Date;"%(brand,size,int(year),int(year),int(year)))
            print("sql done")
            quantity= curr.fetchall()
            curr.execute("select sum(`forecast`.`Quantity`) from botdb.forecast inner join botdb.masterdb on `forecast`.`master`=`masterdb`.`Cat Cd10 Description` where `masterdb`.`Brand Description`= '%s' and `masterdb`.`Size Description`= '%s'  and if (year(current_date())>%d, year(`forecast`.`Date`)=%d ,year(`forecast`.`Date`)=%d and  month(`forecast`.`Date`)<month(current_date()));"%(brand,size,int(year),int(year),int(year)))
            cumsum=curr.fetchall()
            resu = [[ i for i, j in quantity ],[ j for i, j in quantity ]]
            data=pd.DataFrame(resu)
            data=data.transpose()
            data.columns=['date','quantity']
            data=data.sort_values(by='date')
            data.quantity=data.quantity.astype(int)
            data.date=data.date.apply(lambda x: x.strftime("%b %y"))
            ind = np.arange(len(data.quantity))


            # Plot data on chart
            plt.plot(data.date, data.quantity,"r-")
            plt.tick_params(axis='x',which='both',bottom=False,top=False,labelbottom=False)
            plt.grid(True, linestyle='-.')
            cellText = [data.quantity.values]
            the_table = plt.table(cellText=cellText, rowLoc='right', rowLabels=['shipment'],
                             colLabels=data.date.values,
                             colLoc='center', loc='bottom')
            plt.savefig("tablegraph.jpg")
            #plt.show()
            res = ("The shipment volume for %s %s for the year %d is %d"%(brand,size,int(year),int(cumsum[0][0])))
            img="tablegraph.jpg"
            file_upload(channel,img)
            plt.close()
            response['context']['brand']=None
            response['context']['varietal']=None
            response['context']['month']=None
            response['context']['year']=None
            response['context']['size']=None
            response['context']['currentIntent']=None
    except:
        pass

    
         #############################current shipments for only brand size varietal and year##################################
    
    try:
        if response['context']['currentIntent'] == 'currentshipments' and brand.strip() != '' and size.strip() != '' and varietal.strip() != '' and year.strip() != '' and month.strip() == '':
            curr= conn.cursor()
            curr.execute("select Date,sum(`forecast`.`Quantity`) from botdb.forecast inner join botdb.masterdb on `forecast`.`master`=`masterdb`.`Cat Cd10 Description` where `masterdb`.`Brand Description`= '%s' and `Varietal/ Flavor Description`= '%s'  and `masterdb`.`Size Description`= '%s' and if (year(current_date())>%d, year(`forecast`.`Date`)=%d ,year(`forecast`.`Date`)=%d and  month(`forecast`.`Date`)<month(current_date())) group by Date;"%(brand,varietal,size,int(year),int(year),int(year)))
            print("sql done")
            quantity= curr.fetchall()
            curr.execute("select sum(`forecast`.`Quantity`) from botdb.forecast inner join botdb.masterdb on `forecast`.`master`=`masterdb`.`Cat Cd10 Description` where `masterdb`.`Brand Description`= '%s' and `masterdb`.`Size Description`= '%s' and `Varietal/ Flavor Description`= '%s' and if (year(current_date())>%d, year(`forecast`.`Date`)=%d ,year(`forecast`.`Date`)=%d and  month(`forecast`.`Date`)<month(current_date()));"%(brand,size,varietal,int(year),int(year),int(year)))
            cumsum=curr.fetchall()
            resu = [[ i for i, j in quantity ],[ j for i, j in quantity ]]
            data=pd.DataFrame(resu)
            data=data.transpose()
            data.columns=['date','quantity']
            data=data.sort_values(by='date')
            data.quantity=data.quantity.astype(int)
            data.date=data.date.apply(lambda x: x.strftime("%b %y"))
            ind = np.arange(len(data.quantity))


            # Plot data on chart
            plt.plot(data.date, data.quantity,"r-")
            plt.tick_params(axis='x',which='both',bottom=False,top=False,labelbottom=False)
            plt.grid(True, linestyle='-.')
            cellText = [data.quantity.values]
            the_table = plt.table(cellText=cellText, rowLoc='right', rowLabels=['shipment'],
                             colLabels=data.date.values,
                             colLoc='center', loc='bottom')
            plt.savefig("tablegraph.jpg")
            #plt.show()
            res = ("The shipment volume for %s %s %s for the year %d is %d"%(brand,varietal,size,int(year),int(cumsum[0][0])))
            img="tablegraph.jpg"
            file_upload(channel,img)
            plt.close()
            response['context']['brand']=None
            response['context']['varietal']=None
            response['context']['month']=None
            response['context']['year']=None
            response['context']['size']=None
            response['context']['currentIntent']=None
    except:
        pass
    
         #############################current shipments for only size varietal and year##################################
    
    try:
        if response['context']['currentIntent'] == 'currentshipments' and brand.strip() == '' and size.strip() != '' and varietal.strip() != '' and year.strip() != '' and month.strip() == '':  
            curr= conn.cursor()
            curr.execute("select Date,sum(`forecast`.`Quantity`) from botdb.forecast inner join botdb.masterdb on `forecast`.`master`=`masterdb`.`Cat Cd10 Description` where `Varietal/ Flavor Description`= '%s' and `masterdb`.`Size Description`= '%s' and if (year(current_date())>%d, year(`forecast`.`Date`)=%d ,year(`forecast`.`Date`)=%d and  month(`forecast`.`Date`)<month(current_date())) group by Date;"%(varietal,size,int(year),int(year),int(year)))
            print("sql done")
            quantity= curr.fetchall()
            curr.execute("select sum(`forecast`.`Quantity`) from botdb.forecast inner join botdb.masterdb on `forecast`.`master`=`masterdb`.`Cat Cd10 Description` where `masterdb`.`Size Description`= '%s' and `Varietal/ Flavor Description`= '%s' and if (year(current_date())>%d, year(`forecast`.`Date`)=%d ,year(`forecast`.`Date`)=%d and  month(`forecast`.`Date`)<month(current_date()));"%(size,varietal,int(year),int(year),int(year)))
            cumsum=curr.fetchall()
            resu = [[ i for i, j in quantity ],[ j for i, j in quantity ]]
            data=pd.DataFrame(resu)
            data=data.transpose()
            data.columns=['date','quantity']
            data=data.sort_values(by='date')
            data.quantity=data.quantity.astype(int)
            data.date=data.date.apply(lambda x: x.strftime("%b %y"))
            ind = np.arange(len(data.quantity))


            # Plot data on chart
            plt.plot(data.date, data.quantity,"r-")
            plt.tick_params(axis='x',which='both',bottom=False,top=False,labelbottom=False)
            plt.grid(True, linestyle='-.')
            cellText = [data.quantity.values]
            the_table = plt.table(cellText=cellText, rowLoc='right', rowLabels=['shipment'],
                             colLabels=data.date.values,
                             colLoc='center', loc='bottom')
            plt.savefig("tablegraph.jpg")
            #plt.show()
            res = ("The shipment volume for %s %s for the year %d is %d"%(varietal,size,int(year),int(cumsum[0][0])))
            img="tablegraph.jpg"
            file_upload(channel,img)
            plt.close()
            response['context']['brand']=None
            response['context']['varietal']=None
            response['context']['month']=None
            response['context']['year']=None
            response['context']['size']=None
            response['context']['currentIntent']=None
    except:
        pass

         #############################current shipments for only varietal and year##################################
    
    try:
        if response['context']['currentIntent'] == 'currentshipments' and brand.strip() == '' and size.strip() == '' and varietal.strip() != '' and year.strip() != '' and month.strip() == '':  
            curr= conn.cursor()
            curr.execute("select Date,sum(`forecast`.`Quantity`) from botdb.forecast inner join botdb.masterdb on `forecast`.`master`=`masterdb`.`Cat Cd10 Description` where `Varietal/ Flavor Description`= '%s' and if (year(current_date())>%d, year(`forecast`.`Date`)=%d ,year(`forecast`.`Date`)=%d and  month(`forecast`.`Date`)<month(current_date())) group by Date;"%(varietal,int(year),int(year),int(year)))
            print("sql done")
            quantity= curr.fetchall()
            curr.execute("select sum(`forecast`.`Quantity`) from botdb.forecast inner join botdb.masterdb on `forecast`.`master`=`masterdb`.`Cat Cd10 Description` where `Varietal/ Flavor Description`= '%s' and if (year(current_date())>%d, year(`forecast`.`Date`)=%d ,year(`forecast`.`Date`)=%d and  month(`forecast`.`Date`)<month(current_date()));"%(varietal,int(year),int(year),int(year)))
            cumsum=curr.fetchall()
            resu = [[ i for i, j in quantity ],[ j for i, j in quantity ]]
            data=pd.DataFrame(resu)
            data=data.transpose()
            data.columns=['date','quantity']
            data=data.sort_values(by='date')
            data.quantity=data.quantity.astype(int)
            data.date=data.date.apply(lambda x: x.strftime("%b %y"))
            ind = np.arange(len(data.quantity))


            # Plot data on chart
            plt.plot(data.date, data.quantity,"r-")
            plt.tick_params(axis='x',which='both',bottom=False,top=False,labelbottom=False)
            plt.grid(True, linestyle='-.')
            cellText = [data.quantity.values]
            the_table = plt.table(cellText=cellText, rowLoc='right', rowLabels=['shipment'],
                             colLabels=data.date.values,
                             colLoc='center', loc='bottom')
            plt.savefig("tablegraph.jpg")
            #plt.show()
            res = ("The shipment volume for %s for the year %d is %d"%(varietal,int(year),int(cumsum[0][0])))
            img="tablegraph.jpg"
            file_upload(channel,img)
            plt.close()
            response['context']['brand']=None
            response['context']['varietal']=None
            response['context']['month']=None
            response['context']['year']=None
            response['context']['size']=None
            response['context']['currentIntent']=None
    except:
        pass
    
         #############################current shipments for only size and year##################################
    
    try:
        if response['context']['currentIntent'] == 'currentshipments' and brand.strip() == '' and size.strip() != '' and varietal.strip() == '' and year.strip() != '' and month.strip() == '':  
            curr= conn.cursor()
            curr.execute("select Date,sum(`forecast`.`Quantity`) from botdb.forecast inner join botdb.masterdb on `forecast`.`master`=`masterdb`.`Cat Cd10 Description` where `masterdb`.`Size Description`= '%s' and if (year(current_date())>%d, year(`forecast`.`Date`)=%d ,year(`forecast`.`Date`)=%d and  month(`forecast`.`Date`)<month(current_date())) group by Date;"%(size,int(year),int(year),int(year)))
            print("sql done")
            quantity= curr.fetchall()
            curr.execute("select sum(`forecast`.`Quantity`) from botdb.forecast inner join botdb.masterdb on `forecast`.`master`=`masterdb`.`Cat Cd10 Description` where `masterdb`.`Size Description`= '%s' and if (year(current_date())>%d, year(`forecast`.`Date`)=%d ,year(`forecast`.`Date`)=%d and  month(`forecast`.`Date`)<month(current_date()));"%(size,int(year),int(year),int(year)))
            cumsum=curr.fetchall()
            resu = [[ i for i, j in quantity ],[ j for i, j in quantity ]]
            data=pd.DataFrame(resu)
            data=data.transpose()
            data.columns=['date','quantity']
            data=data.sort_values(by='date')
            data.quantity=data.quantity.astype(int)
            data.date=data.date.apply(lambda x: x.strftime("%b %y"))
            ind = np.arange(len(data.quantity))


            # Plot data on chart
            plt.plot(data.date, data.quantity,"r-")
            plt.tick_params(axis='x',which='both',bottom=False,top=False,labelbottom=False)
            plt.grid(True, linestyle='-.')
            cellText = [data.quantity.values]
            the_table = plt.table(cellText=cellText, rowLoc='right', rowLabels=['shipment'],
                             colLabels=data.date.values,
                             colLoc='center', loc='bottom')
            
            plt.savefig("tablegraph.jpg")
            #plt.show()
            
            res = ("The shipment volume for %s for the year %d is %d"%(size,int(year),int(cumsum[0][0])))
            img="tablegraph.jpg"
            file_upload(channel,img)
            
            plt.close()
            response['context']['brand']=None
            response['context']['varietal']=None
            response['context']['month']=None
            response['context']['year']=None
            response['context']['size']=None
            response['context']['currentIntent']=None
    except:
        pass
    
    
     #############################last x months shipments for only brand ##################################
    
    try:
        if response['context']['currentIntent'] == 'lastmonshipment' and brand.strip() != '' and size.strip() == '' and varietal.strip() == '' and year.strip() == '' and month.strip() == '':
            if number.strip()=='':
                number="1"
            curr= conn.cursor() 
            if int(number)>1:
                curr.execute("select Date,sum(Quantity) from botdb.forecast inner join botdb.masterdb on `forecast`.`master`=`masterdb`.`Cat Cd10 Description` where `masterdb`.`Brand Description`= '%s' and Date>=DATE_SUB(current_date(),INTERVAL %d MONTH) and Date<DATE_SUB(current_date(),INTERVAL 30 DAY) group by Date;"%(brand,int(number)+1))
                print("sql done")
                quantity= curr.fetchall()

                resu = [[ i for i, j in quantity ],[ j for i, j in quantity ]]
                data=pd.DataFrame(resu)
                data=data.transpose()
                data.columns=['date','quantity']
                data=data.sort_values(by='date')
                data.quantity=data.quantity.astype(int)
                data.date=data.date.apply(lambda x: x.strftime("%b %y"))
                ind = np.arange(len(data.quantity))

                # Plot data on chart
                plt.plot(data.date, data.quantity,"r-")
                plt.tick_params(axis='x',which='both',bottom=False,top=False,labelbottom=False)
                plt.grid(True, linestyle='-.')
                cellText = [data.quantity]
                the_table = plt.table(cellText=cellText, rowLoc='right', rowLabels=['shipment'],
                                 colLabels=data.date,
                                 colLoc='center', loc='bottom')
                plt.savefig("tablegraph.jpg")
                #plt.show()
                img="tablegraph.jpg"
                file_upload(channel,img)
                plt.close()
            curr= conn.cursor()
            curr.execute("select sum(Quantity) from botdb.forecast inner join botdb.masterdb on `forecast`.`master`=`masterdb`.`Cat Cd10 Description` where `masterdb`.`Brand Description`= '%s' and Date>=DATE_SUB(current_date(),INTERVAL %d MONTH) and Date<DATE_SUB(current_date(),INTERVAL 30 DAY);"%(brand,int(number)+1))
            cumsum=curr.fetchall()
            res = ("The cummulative last %d month's shipment for %s is %d"%(int(number),brand,int(cumsum[0][0])))
            
            response['context']['brand']=None
            response['context']['varietal']=None
            response['context']['month']=None
            response['context']['year']=None
            response['context']['size']=None
            response['context']['number']=None
            response['context']['currentIntent']=None
    except:
        pass    
    
     #############################last x months shipments for brand and varietal##################################
    
    try:
        if response['context']['currentIntent'] == 'lastmonshipment' and brand.strip() != '' and size.strip() == '' and varietal.strip() != '' and year.strip() == '' and month.strip() == '':
            if number.strip()=='':
                number="1"
            curr= conn.cursor() 
            if int(number)>1:
                curr.execute("select Date,sum(Quantity) from botdb.forecast inner join botdb.masterdb on `forecast`.`master`=`masterdb`.`Cat Cd10 Description` where `masterdb`.`Brand Description`= '%s' and `masterdb`.`Varietal/ Flavor Description`= '%s' and Date>=DATE_SUB(current_date(),INTERVAL %d MONTH) and Date<DATE_SUB(current_date(),INTERVAL 30 DAY) group by Date;"%(brand,varietal,int(number)+1))
                print("sql done")
                quantity= curr.fetchall()

                resu = [[ i for i, j in quantity ],[ j for i, j in quantity ]]
                data=pd.DataFrame(resu)
                data=data.transpose()
                data.columns=['date','quantity']
                data=data.sort_values(by='date')
                data.quantity=data.quantity.astype(int)
                data.date=data.date.apply(lambda x: x.strftime("%b %y"))
                ind = np.arange(len(data.quantity))

                # Plot data on chart
                plt.plot(data.date, data.quantity,"g-")
                plt.tick_params(axis='x',which='both',bottom=False,top=False,labelbottom=False)
                plt.grid(True, linestyle='-.')
                cellText = [data.quantity]
                the_table = plt.table(cellText=cellText, rowLoc='right', rowLabels=['shipment'],
                                 colLabels=data.date,
                                 colLoc='center', loc='bottom')
                plt.savefig("tablegraph.jpg")
                #plt.show()
                img="tablegraph.jpg"
                file_upload(channel,img)
            
            curr= conn.cursor()
            curr.execute("select sum(Quantity) from botdb.forecast inner join botdb.masterdb on `forecast`.`master`=`masterdb`.`Cat Cd10 Description` where `masterdb`.`Brand Description`= '%s' and `masterdb`.`Varietal/ Flavor Description`= '%s' and Date>=DATE_SUB(current_date(),INTERVAL %d MONTH) and Date<DATE_SUB(current_date(),INTERVAL 30 DAY);"%(brand,varietal,int(number)+1))
            cumsum=curr.fetchall()
            res = ("The cummulative last %d month's shipment for %s %s is %d"%(int(number),brand,varietal,int(cumsum[0][0])))
            plt.close()
            response['context']['brand']=None
            response['context']['varietal']=None
            response['context']['month']=None
            response['context']['year']=None
            response['context']['size']=None
            response['context']['number']=None
            response['context']['currentIntent']=None
    except:
        pass
    
     #############################last x months shipments for brand varietal and size##################################
    
    try:
        if response['context']['currentIntent'] == 'lastmonshipment' and brand.strip() != '' and size.strip() != '' and varietal.strip() != '' and year.strip() == '' and month.strip() == '':
            if number.strip()=='':
                number="1"
            curr= conn.cursor() 
            if int(number)>1:
                curr.execute("select Date,sum(Quantity) from botdb.forecast inner join botdb.masterdb on `forecast`.`master`=`masterdb`.`Cat Cd10 Description` where `masterdb`.`Brand Description`= '%s' and `masterdb`.`Size Description`= '%s' and `masterdb`.`Varietal/ Flavor Description`= '%s' and Date>=DATE_SUB(current_date(),INTERVAL %d MONTH) and Date<DATE_SUB(current_date(),INTERVAL 30 DAY) group by Date;"%(brand,size,varietal,int(number)+1))
                print("sql done")
                quantity= curr.fetchall()

                resu = [[ i for i, j in quantity ],[ j for i, j in quantity ]]
                data=pd.DataFrame(resu)
                data=data.transpose()
                data.columns=['date','quantity']
                data=data.sort_values(by='date')
                data.quantity=data.quantity.astype(int)
                data.date=data.date.apply(lambda x: x.strftime("%b %y"))
                ind = np.arange(len(data.quantity))

                # Plot data on chart
                plt.plot(data.date, data.quantity,"b-")
                plt.tick_params(axis='x',which='both',bottom=False,top=False,labelbottom=False)
                plt.grid(True, linestyle='-.')
                cellText = [data.quantity]
                the_table = plt.table(cellText=cellText, rowLoc='right', rowLabels=['shipment'],
                                 colLabels=data.date,
                                 colLoc='center', loc='bottom')
                plt.savefig("tablegraph.jpg")
                #plt.show()
                img="tablegraph.jpg"
                file_upload(channel,img)
            
            curr= conn.cursor()
            curr.execute("select sum(Quantity) from botdb.forecast inner join botdb.masterdb on `forecast`.`master`=`masterdb`.`Cat Cd10 Description` where `masterdb`.`Brand Description`= '%s' and `masterdb`.`Size Description`= '%s' and `masterdb`.`Varietal/ Flavor Description`= '%s' and Date>=DATE_SUB(current_date(),INTERVAL %d MONTH) and Date<DATE_SUB(current_date(),INTERVAL 30 DAY);"%(brand,size,varietal,int(number)+1))
            cumsum=curr.fetchall()
            res = ("The cummulative last %d month's shipment for %s %s %s is %d"%(int(number),brand,varietal,size,int(cumsum[0][0])))
            plt.close()
            response['context']['brand']=None
            response['context']['varietal']=None
            response['context']['month']=None
            response['context']['year']=None
            response['context']['size']=None
            response['context']['number']=None
            response['context']['currentIntent']=None
    except:
        pass     

     #############################last x months shipments for brand and size##################################
    
    try:
        if response['context']['currentIntent'] == 'lastmonshipment' and brand.strip() != '' and size.strip() != '' and varietal.strip() == '' and year.strip() == '' and month.strip() == '':
            if number.strip()=='':
                number="1"
            curr= conn.cursor() 
            if int(number)>1:
                curr.execute("select Date,sum(Quantity) from botdb.forecast inner join botdb.masterdb on `forecast`.`master`=`masterdb`.`Cat Cd10 Description` where `masterdb`.`Brand Description`= '%s' and `masterdb`.`Size Description`= '%s' and Date>=DATE_SUB(current_date(),INTERVAL %d MONTH) and Date<DATE_SUB(current_date(),INTERVAL 30 DAY) group by Date;"%(brand,size,int(number)+1))
                print("sql done")
                quantity= curr.fetchall()

                resu = [[ i for i, j in quantity ],[ j for i, j in quantity ]]
                data=pd.DataFrame(resu)
                data=data.transpose()
                data.columns=['date','quantity']
                data=data.sort_values(by='date')
                data.quantity=data.quantity.astype(int)
                data.date=data.date.apply(lambda x: x.strftime("%b %y"))
                ind = np.arange(len(data.quantity))

                # Plot data on chart
                plt.plot(data.date, data.quantity,"k-")
                plt.tick_params(axis='x',which='both',bottom=False,top=False,labelbottom=False)
                plt.grid(True, linestyle='-.')
                cellText = [data.quantity]
                the_table = plt.table(cellText=cellText, rowLoc='right', rowLabels=['shipment'],
                                 colLabels=data.date,
                                 colLoc='center', loc='bottom')
                plt.savefig("tablegraph.jpg")
                #plt.show()
                img="tablegraph.jpg"
                file_upload(channel,img)
            
            curr= conn.cursor()
            curr.execute("select sum(Quantity) from botdb.forecast inner join botdb.masterdb on `forecast`.`master`=`masterdb`.`Cat Cd10 Description` where `masterdb`.`Brand Description`= '%s' and `masterdb`.`Size Description`= '%s' and Date>=DATE_SUB(current_date(),INTERVAL %d MONTH) and Date<DATE_SUB(current_date(),INTERVAL 30 DAY);"%(brand,size,int(number)+1))
            cumsum=curr.fetchall()
            res = ("The cummulative last %d month's shipment for %s %s is %d"%(int(number),brand,size,int(cumsum[0][0])))
            plt.close()
            response['context']['brand']=None
            response['context']['varietal']=None
            response['context']['month']=None
            response['context']['year']=None
            response['context']['size']=None
            response['context']['number']=None
            response['context']['currentIntent']=None
    except:
        pass
 

     #############################last x months shipments for size##################################
    
    try:
        if response['context']['currentIntent'] == 'lastmonshipment' and brand.strip() == '' and size.strip() != '' and varietal.strip() == '' and year.strip() == '' and month.strip() == '':
            if number.strip()=='':
                number="1"
            curr= conn.cursor() 
            if int(number)>1:
                curr.execute("select Date,sum(Quantity) from botdb.forecast inner join botdb.masterdb on `forecast`.`master`=`masterdb`.`Cat Cd10 Description` where `masterdb`.`Size Description`= '%s' and Date>=DATE_SUB(current_date(),INTERVAL %d MONTH) and Date<DATE_SUB(current_date(),INTERVAL 30 DAY) group by Date;"%(size,int(number)+1))
                print("sql done")
                quantity= curr.fetchall()

                resu = [[ i for i, j in quantity ],[ j for i, j in quantity ]]
                data=pd.DataFrame(resu)
                data=data.transpose()
                data.columns=['date','quantity']
                data=data.sort_values(by='date')
                data.quantity=data.quantity.astype(int)
                data.date=data.date.apply(lambda x: x.strftime("%b %y"))
                ind = np.arange(len(data.quantity))

                # Plot data on chart
                plt.plot(data.date, data.quantity,"c-")
                plt.tick_params(axis='x',which='both',bottom=False,top=False,labelbottom=False)
                plt.grid(True, linestyle='-.')
                cellText = [data.quantity]
                the_table = plt.table(cellText=cellText, rowLoc='right', rowLabels=['shipment'],
                                 colLabels=data.date,
                                 colLoc='center', loc='bottom')
                plt.savefig("tablegraph.jpg")
                #plt.show()
                img="tablegraph.jpg"
                file_upload(channel,img)
            
            curr= conn.cursor()
            curr.execute("select sum(Quantity) from botdb.forecast inner join botdb.masterdb on `forecast`.`master`=`masterdb`.`Cat Cd10 Description` where `masterdb`.`Size Description`= '%s' and Date>=DATE_SUB(current_date(),INTERVAL %d MONTH) and Date<DATE_SUB(current_date(),INTERVAL 30 DAY);"%(size,int(number)+1))
            cumsum=curr.fetchall()
            res = ("The cummulative last %d month's shipment for %s is %d"%(int(number),size,int(cumsum[0][0])))
            plt.close()
            response['context']['brand']=None
            response['context']['varietal']=None
            response['context']['month']=None
            response['context']['year']=None
            response['context']['size']=None
            response['context']['number']=None
            response['context']['currentIntent']=None
    except:
        pass
    
     #############################last x months shipments for varietal and size##################################
    
    try:
        if response['context']['currentIntent'] == 'lastmonshipment' and brand.strip() == '' and size.strip() != '' and varietal.strip() != '' and year.strip() == '' and month.strip() == '':
            if number.strip()=='':
                number="1"
            curr= conn.cursor() 
            if int(number)>1:
                curr.execute("select Date,sum(Quantity) from botdb.forecast inner join botdb.masterdb on `forecast`.`master`=`masterdb`.`Cat Cd10 Description` where `masterdb`.`Varietal/ Flavor Description`= '%s' and `masterdb`.`Size Description`= '%s' and Date>=DATE_SUB(current_date(),INTERVAL %d MONTH) and Date<DATE_SUB(current_date(),INTERVAL 30 DAY) group by Date;"%(varietal,size,int(number)+1))
                print("sql done")
                quantity= curr.fetchall()

                resu = [[ i for i, j in quantity ],[ j for i, j in quantity ]]
                data=pd.DataFrame(resu)
                data=data.transpose()
                data.columns=['date','quantity']
                data=data.sort_values(by='date')
                data.quantity=data.quantity.astype(int)
                data.date=data.date.apply(lambda x: x.strftime("%b %y"))
                ind = np.arange(len(data.quantity))

                # Plot data on chart
                plt.plot(data.date, data.quantity,"y-")
                plt.tick_params(axis='x',which='both',bottom=False,top=False,labelbottom=False)
                plt.grid(True, linestyle='-.')
                cellText = [data.quantity]
                the_table = plt.table(cellText=cellText, rowLoc='right', rowLabels=['shipment'],
                                 colLabels=data.date,
                                 colLoc='center', loc='bottom')
                plt.savefig("tablegraph.jpg")
                #plt.show()
                img="tablegraph.jpg"
                file_upload(channel,img)
            
            curr= conn.cursor()
            curr.execute("select sum(Quantity) from botdb.forecast inner join botdb.masterdb on `forecast`.`master`=`masterdb`.`Cat Cd10 Description` where `masterdb`.`Varietal/ Flavor Description`= '%s' and `masterdb`.`Size Description`= '%s' and Date>=DATE_SUB(current_date(),INTERVAL %d MONTH) and Date<DATE_SUB(current_date(),INTERVAL 30 DAY);"%(varietal,size,int(number)+1))
            cumsum=curr.fetchall()
            res = ("The cummulative last %d month's shipment for %s %s is %d"%(int(number),varietal,size,int(cumsum[0][0])))
            plt.close()
            response['context']['brand']=None
            response['context']['varietal']=None
            response['context']['month']=None
            response['context']['year']=None
            response['context']['size']=None
            response['context']['number']=None
            response['context']['currentIntent']=None
    except:
        pass
    
     #############################last x months shipments for varietal##################################
    
    try:
        if response['context']['currentIntent'] == 'lastmonshipment' and brand.strip() == '' and size.strip() == '' and varietal.strip() != '' and year.strip() == '' and month.strip() == '':
            if number.strip()=='':
                number="1"
            curr= conn.cursor() 
            if int(number)>1:
                curr.execute("select Date,sum(Quantity) from botdb.forecast inner join botdb.masterdb on `forecast`.`master`=`masterdb`.`Cat Cd10 Description` where `masterdb`.`Varietal/ Flavor Description`= '%s' and Date>=DATE_SUB(current_date(),INTERVAL %d MONTH) and Date<DATE_SUB(current_date(),INTERVAL 30 DAY) group by Date;"%(varietal,int(number)+1))
                print("sql done")
                quantity= curr.fetchall()

                resu = [[ i for i, j in quantity ],[ j for i, j in quantity ]]
                data=pd.DataFrame(resu)
                data=data.transpose()
                data.columns=['date','quantity']
                data=data.sort_values(by='date')
                data.quantity=data.quantity.astype(int)
                data.date=data.date.apply(lambda x: x.strftime("%b %y"))
                ind = np.arange(len(data.quantity))

                # Plot data on chart
                plt.plot(data.date, data.quantity,"b-")
                plt.tick_params(axis='x',which='both',bottom=False,top=False,labelbottom=False)
                plt.grid(True, linestyle='-.')
                cellText = [data.quantity]
                the_table = plt.table(cellText=cellText, rowLoc='right', rowLabels=['shipment'],
                                 colLabels=data.date,
                                 colLoc='center', loc='bottom')
                plt.savefig("tablegraph.jpg")
                #plt.show()
                img="tablegraph.jpg"
                file_upload(channel,img)
            
            curr= conn.cursor()
            curr.execute("select sum(Quantity) from botdb.forecast inner join botdb.masterdb on `forecast`.`master`=`masterdb`.`Cat Cd10 Description` where `masterdb`.`Varietal/ Flavor Description`= '%s' and Date>=DATE_SUB(current_date(),INTERVAL %d MONTH) and Date<DATE_SUB(current_date(),INTERVAL 30 DAY);"%(varietal,int(number)+1))
            cumsum=curr.fetchall()
            res = ("The cummulative last %d month's shipment for %s is %d"%(int(number),varietal,int(cumsum[0][0])))
            plt.close()
            response['context']['brand']=None
            response['context']['varietal']=None
            response['context']['month']=None
            response['context']['year']=None
            response['context']['size']=None
            response['context']['number']=None
            response['context']['currentIntent']=None
    except:
        pass
    
     #############################inventory shipments for only brand ##################################
    
    try:
        if response['context']['currentIntent'] == 'inventory' and brand.strip() != '' and size.strip() == '' and varietal.strip() == '' and year.strip() == '':

            curr= conn.cursor() 
            if month.strip()=='all':
                print("not entered")
                curr.execute("select Date,sum(Balance) from botdb.inventory inner join botdb.masterdb on `inventory`.`Group`=`masterdb`.`Cat Cd10 Description` where `masterdb`.`Brand Description`= '%s' and year(`inventory`.`Date`)=year(current_date()) group by Date;"%(brand))
                print("sql done")
                quantity= curr.fetchall()

                resu = [[ i for i, j in quantity ],[ j for i, j in quantity ]]
                data=pd.DataFrame(resu)
                data=data.transpose()
                data.columns=['date','quantity']
                data=data.sort_values(by='date')
                data.quantity=data.quantity.astype(int)
                data.date=data.date.apply(lambda x: x.strftime("%b %y"))
                ind = np.arange(len(data.quantity))

                # Plot data on chart
                plt.plot(data.date, data.quantity,"r-")
                plt.tick_params(axis='x',which='both',bottom=False,top=False,labelbottom=False)
                plt.grid(True, linestyle='-.')
                cellText = [data.quantity.values]
                the_table = plt.table(cellText=cellText, rowLoc='right', rowLabels=['shipment'],
                                 colLabels=data.date.values,
                                 colLoc='center', loc='bottom')
                plt.savefig("tablegraph.jpg")
                #plt.show()
                img="tablegraph.jpg"
                file_upload(channel,img)
            
                curr= conn.cursor()
                curr.execute("select sum(Balance) from botdb.inventory inner join botdb.masterdb on `inventory`.`Group`=`masterdb`.`Cat Cd10 Description` where `masterdb`.`Brand Description`= '%s' and year(`inventory`.`Date`)=year(current_date());"%(brand))
                cumsum=curr.fetchall()
                res = ("The cummulative inventory for %s is %d"%(brand,int(cumsum[0][0])))
            elif month.strip()!='all':
                curr= conn.cursor()
                curr.execute("select sum(Balance) from botdb.inventory inner join botdb.masterdb on `inventory`.`Group`=`masterdb`.`Cat Cd10 Description` where `masterdb`.`Brand Description`= '%s' and year(`inventory`.`Date`)=year(current_date()) and month(`inventory`.`Date`)= %d;"%(brand,int(month)))
                cumsum=curr.fetchall()
                res = ("The cummulative inventory for %s for %s is %d"%(brand,calendar.month_name[int(month)],int(cumsum[0][0])))
            plt.close()
            response['context']['brand']=None
            response['context']['varietal']=None
            response['context']['month']=None
            response['context']['year']=None
            response['context']['size']=None
            response['context']['number']=None
            response['context']['currentIntent']=None
    except:
        pass
    
     #############################inventory shipments for brand and size##################################
    
    try:
        if response['context']['currentIntent'] == 'inventory' and brand.strip() != '' and size.strip() != '' and varietal.strip() == '' and year.strip() == '':

            curr= conn.cursor() 
            if month.strip()=='all':
                print("not entered")
                curr.execute("select Date,sum(Balance) from botdb.inventory inner join botdb.masterdb on `inventory`.`Group`=`masterdb`.`Cat Cd10 Description` where `masterdb`.`Brand Description`= '%s' and `masterdb`.`Size Description`= '%s' and year(`inventory`.`Date`)=year(current_date()) group by Date;"%(brand,size))
                print("sql done")
                quantity= curr.fetchall()

                resu = [[ i for i, j in quantity ],[ j for i, j in quantity ]]
                data=pd.DataFrame(resu)
                data=data.transpose()
                data.columns=['date','quantity']
                data=data.sort_values(by='date')
                data.quantity=data.quantity.astype(int)
                data.date=data.date.apply(lambda x: x.strftime("%b %y"))
                ind = np.arange(len(data.quantity))

                # Plot data on chart
                plt.plot(data.date, data.quantity,"r-")
                plt.tick_params(axis='x',which='both',bottom=False,top=False,labelbottom=False)
                plt.grid(True, linestyle='-.')
                cellText = [data.quantity.values]
                the_table = plt.table(cellText=cellText, rowLoc='right', rowLabels=['shipment'],
                                 colLabels=data.date.values,
                                 colLoc='center', loc='bottom')
                plt.savefig("tablegraph.jpg")
                #plt.show()
                img="tablegraph.jpg"
                file_upload(channel,img)
            
                curr= conn.cursor()
                curr.execute("select sum(Balance) from botdb.inventory inner join botdb.masterdb on `inventory`.`Group`=`masterdb`.`Cat Cd10 Description` where `masterdb`.`Brand Description`= '%s' and `masterdb`.`Size Description`= '%s' and year(`inventory`.`Date`)=year(current_date());"%(brand,size))
                cumsum=curr.fetchall()
                res = ("The cummulative inventory for %s %s is %d"%(brand,size,int(cumsum[0][0])))
            elif month.strip()!='all':
                print("single month")
                curr= conn.cursor()
                curr.execute("select sum(Balance) from botdb.inventory inner join botdb.masterdb on `inventory`.`Group`=`masterdb`.`Cat Cd10 Description` where `masterdb`.`Brand Description`= '%s' and `masterdb`.`Size Description`= '%s' and year(`inventory`.`Date`)=year(current_date()) and month(`inventory`.`Date`)= %d;"%(brand,size,int(month)))
                cumsum=curr.fetchall()
                print("sql done")
                res = ("The cummulative inventory for %s %s for %s is %d"%(brand,size,calendar.month_name[int(month)],int(cumsum[0][0])))
            plt.close()
            response['context']['brand']=None
            response['context']['varietal']=None
            response['context']['month']=None
            response['context']['year']=None
            response['context']['size']=None
            response['context']['number']=None
            response['context']['currentIntent']=None
    except:
        pass
    
    
     #############################inventory shipments for brand and varietal##################################
    
    try:
        if response['context']['currentIntent'] == 'inventory' and brand.strip() != '' and size.strip() == '' and varietal.strip() != '' and year.strip() == '':

            curr= conn.cursor() 
            if month.strip()=='all':
                print("not entered")
                curr.execute("select Date,sum(Balance) from botdb.inventory inner join botdb.masterdb on `inventory`.`Group`=`masterdb`.`Cat Cd10 Description` where `masterdb`.`Brand Description`= '%s' and `masterdb`.`Varietal/ Flavor Description`= '%s' and year(`inventory`.`Date`)=year(current_date()) group by Date;"%(brand,varietal))
                print("sql done")
                quantity= curr.fetchall()

                resu = [[ i for i, j in quantity ],[ j for i, j in quantity ]]
                data=pd.DataFrame(resu)
                data=data.transpose()
                data.columns=['date','quantity']
                data=data.sort_values(by='date')
                data.quantity=data.quantity.astype(int)
                data.date=data.date.apply(lambda x: x.strftime("%b %y"))
                ind = np.arange(len(data.quantity))

                # Plot data on chart
                plt.plot(data.date, data.quantity,"r-")
                plt.tick_params(axis='x',which='both',bottom=False,top=False,labelbottom=False)
                plt.grid(True, linestyle='-.')
                cellText = [data.quantity.values]
                the_table = plt.table(cellText=cellText, rowLoc='right', rowLabels=['shipment'],
                                 colLabels=data.date.values,
                                 colLoc='center', loc='bottom')
                plt.savefig("tablegraph.jpg")
                #plt.show()
                img="tablegraph.jpg"
                file_upload(channel,img)
            
                curr= conn.cursor()
                curr.execute("select sum(Balance) from botdb.inventory inner join botdb.masterdb on `inventory`.`Group`=`masterdb`.`Cat Cd10 Description` where `masterdb`.`Brand Description`= '%s' and `masterdb`.`Varietal/ Flavor Description`= '%s' and year(`inventory`.`Date`)=year(current_date());"%(brand,varietal))
                cumsum=curr.fetchall()
                res = ("The cummulative inventory for %s %s is %d"%(brand,varietal,int(cumsum[0][0])))
            elif month.strip()!='all':
                print("single month")
                curr= conn.cursor()
                curr.execute("select sum(Balance) from botdb.inventory inner join botdb.masterdb on `inventory`.`Group`=`masterdb`.`Cat Cd10 Description` where `masterdb`.`Brand Description`= '%s' and `masterdb`.`Varietal/ Flavor Description`= '%s' and year(`inventory`.`Date`)=year(current_date()) and month(`inventory`.`Date`)= %d;"%(brand,varietal,int(month)))
                cumsum=curr.fetchall()
                print("sql done")
                res = ("The cummulative inventory for %s %s for %s is %d"%(brand,varietal,calendar.month_name[int(month)],int(cumsum[0][0])))
            plt.close()
            response['context']['brand']=None
            response['context']['varietal']=None
            response['context']['month']=None
            response['context']['year']=None
            response['context']['size']=None
            response['context']['number']=None
            response['context']['currentIntent']=None
    except:
        pass
    
     #############################inventory shipments for size##################################
    
    try:
        if response['context']['currentIntent'] == 'inventory' and brand.strip() == '' and size.strip() != '' and varietal.strip() == '' and year.strip() == '':

            curr= conn.cursor() 
            if month.strip()=='all':
                print("not entered")
                curr.execute("select Date,sum(Balance) from botdb.inventory inner join botdb.masterdb on `inventory`.`Group`=`masterdb`.`Cat Cd10 Description` where `masterdb`.`Size Description`= '%s' and year(`inventory`.`Date`)=year(current_date()) group by Date;"%(size))
                print("sql done")
                quantity= curr.fetchall()

                resu = [[ i for i, j in quantity ],[ j for i, j in quantity ]]
                data=pd.DataFrame(resu)
                data=data.transpose()
                data.columns=['date','quantity']
                data=data.sort_values(by='date')
                data.quantity=data.quantity.astype(int)
                data.date=data.date.apply(lambda x: x.strftime("%b %y"))
                ind = np.arange(len(data.quantity))

                # Plot data on chart
                plt.plot(data.date, data.quantity,"r-")
                plt.tick_params(axis='x',which='both',bottom=False,top=False,labelbottom=False)
                plt.grid(True, linestyle='-.')
                cellText = [data.quantity.values]
                the_table = plt.table(cellText=cellText, rowLoc='right', rowLabels=['shipment'],
                                 colLabels=data.date.values,
                                 colLoc='center', loc='bottom')
                plt.savefig("tablegraph.jpg")
                #plt.show()
                img="tablegraph.jpg"
                file_upload(channel,img)
            
                curr= conn.cursor()
                curr.execute("select sum(Balance) from botdb.inventory inner join botdb.masterdb on `inventory`.`Group`=`masterdb`.`Cat Cd10 Description` where `masterdb`.`Size Description`= '%s' and year(`inventory`.`Date`)=year(current_date());"%(size))
                cumsum=curr.fetchall()
                res = ("The cummulative inventory for %s is %d"%(size,int(cumsum[0][0])))
            elif month.strip()!='all':
                print("single month")
                curr= conn.cursor()
                curr.execute("select sum(Balance) from botdb.inventory inner join botdb.masterdb on `inventory`.`Group`=`masterdb`.`Cat Cd10 Description` where `masterdb`.`Size Description`= '%s' and year(`inventory`.`Date`)=year(current_date()) and month(`inventory`.`Date`)= %d;"%(size,int(month)))
                cumsum=curr.fetchall()
                print("sql done")
                res = ("The cummulative inventory for %s for %s is %d"%(size,calendar.month_name[int(month)],int(cumsum[0][0])))
            plt.close()
            response['context']['brand']=None
            response['context']['varietal']=None
            response['context']['month']=None
            response['context']['year']=None
            response['context']['size']=None
            response['context']['number']=None
            response['context']['currentIntent']=None
    except:
        pass
    
    
     #############################inventory shipments for varietal##################################
    
    try:
        if response['context']['currentIntent'] == 'inventory' and brand.strip() == '' and size.strip() == '' and varietal.strip() != '' and year.strip() == '':

            curr= conn.cursor() 
            if month.strip()=='all':
                print("not entered")
                curr.execute("select Date,sum(Balance) from botdb.inventory inner join botdb.masterdb on `inventory`.`Group`=`masterdb`.`Cat Cd10 Description` where `masterdb`.`Varietal/ Flavor Description`= '%s' and year(`inventory`.`Date`)=year(current_date()) group by Date;"%(varietal))
                print("sql done")
                quantity= curr.fetchall()

                resu = [[ i for i, j in quantity ],[ j for i, j in quantity ]]
                data=pd.DataFrame(resu)
                data=data.transpose()
                data.columns=['date','quantity']
                data=data.sort_values(by='date')
                data.quantity=data.quantity.astype(int)
                data.date=data.date.apply(lambda x: x.strftime("%b %y"))
                ind = np.arange(len(data.quantity))

                # Plot data on chart
                plt.plot(data.date, data.quantity,"r-")
                plt.tick_params(axis='x',which='both',bottom=False,top=False,labelbottom=False)
                plt.grid(True, linestyle='-.')
                cellText = [data.quantity.values]
                the_table = plt.table(cellText=cellText, rowLoc='right', rowLabels=['shipment'],
                                 colLabels=data.date.values,
                                 colLoc='center', loc='bottom')
                plt.savefig("tablegraph.jpg")
                #plt.show()
                img="tablegraph.jpg"
                file_upload(channel,img)
            
                curr= conn.cursor()
                curr.execute("select sum(Balance) from botdb.inventory inner join botdb.masterdb on `inventory`.`Group`=`masterdb`.`Cat Cd10 Description` where `masterdb`.`Varietal/ Flavor Description`= '%s' and year(`inventory`.`Date`)=year(current_date());"%(varietal))
                cumsum=curr.fetchall()
                res = ("The cummulative inventory for %s is %d"%(varietal,int(cumsum[0][0])))
            elif month.strip()!='all':
                print("single month")
                curr= conn.cursor()
                curr.execute("select sum(Balance) from botdb.inventory inner join botdb.masterdb on `inventory`.`Group`=`masterdb`.`Cat Cd10 Description` where `masterdb`.`Varietal/ Flavor Description`= '%s' and year(`inventory`.`Date`)=year(current_date()) and month(`inventory`.`Date`)= %d;"%(varietal,int(month)))
                cumsum=curr.fetchall()
                print("sql done")
                res = ("The cummulative inventory for %s for %s is %d"%(varietal,calendar.month_name[int(month)],int(cumsum[0][0])))
            plt.close()
            response['context']['brand']=None
            response['context']['varietal']=None
            response['context']['month']=None
            response['context']['year']=None
            response['context']['size']=None
            response['context']['number']=None
            response['context']['currentIntent']=None
    except:
        pass
    
     #############################inventory shipments for size and varietal##################################
    
    try:
        if response['context']['currentIntent'] == 'inventory' and brand.strip() == '' and size.strip() != '' and varietal.strip() != '' and year.strip() == '':

            curr= conn.cursor() 
            if month.strip()=='all':
                print("not entered")
                curr.execute("select Date,sum(Balance) from botdb.inventory inner join botdb.masterdb on `inventory`.`Group`=`masterdb`.`Cat Cd10 Description` where `masterdb`.`Varietal/ Flavor Description`= '%s' and `masterdb`.`Size Description`= '%s' and year(`inventory`.`Date`)=year(current_date()) group by Date;"%(varietal,size))
                print("sql done")
                quantity= curr.fetchall()

                resu = [[ i for i, j in quantity ],[ j for i, j in quantity ]]
                data=pd.DataFrame(resu)
                data=data.transpose()
                data.columns=['date','quantity']
                data=data.sort_values(by='date')
                data.quantity=data.quantity.astype(int)
                data.date=data.date.apply(lambda x: x.strftime("%b %y"))
                ind = np.arange(len(data.quantity))

                # Plot data on chart
                plt.plot(data.date, data.quantity,"r-")
                plt.tick_params(axis='x',which='both',bottom=False,top=False,labelbottom=False)
                plt.grid(True, linestyle='-.')
                cellText = [data.quantity.values]
                the_table = plt.table(cellText=cellText, rowLoc='right', rowLabels=['shipment'],
                                 colLabels=data.date.values,
                                 colLoc='center', loc='bottom')
                plt.savefig("tablegraph.jpg")
                #plt.show()
                img="tablegraph.jpg"
                file_upload(channel,img)
            
                curr= conn.cursor()
                curr.execute("select sum(Balance) from botdb.inventory inner join botdb.masterdb on `inventory`.`Group`=`masterdb`.`Cat Cd10 Description` where `masterdb`.`Varietal/ Flavor Description`= '%s' and `masterdb`.`Size Description`= '%s' and year(`inventory`.`Date`)=year(current_date());"%(varietal,size))
                cumsum=curr.fetchall()
                res = ("The cummulative inventory for %s %s is %d"%(varietal,size,int(cumsum[0][0])))
            elif month.strip()!='all':
                print("single month")
                curr= conn.cursor()
                curr.execute("select sum(Balance) from botdb.inventory inner join botdb.masterdb on `inventory`.`Group`=`masterdb`.`Cat Cd10 Description` where `masterdb`.`Varietal/ Flavor Description`= '%s' and `masterdb`.`Size Description`= '%s' and year(`inventory`.`Date`)=year(current_date()) and month(`inventory`.`Date`)= %d;"%(varietal,size,int(month)))
                cumsum=curr.fetchall()
                print("sql done")
                res = ("The cummulative inventory for %s %s for %s is %d"%(varietal,size,calendar.month_name[int(month)],int(cumsum[0][0])))
            plt.close()
            response['context']['brand']=None
            response['context']['varietal']=None
            response['context']['month']=None
            response['context']['year']=None
            response['context']['size']=None
            response['context']['number']=None
            response['context']['currentIntent']=None
    except:
        pass
    
      #############################inventory shipments for brand size varietal##################################
    
    try:
        if response['context']['currentIntent'] == 'inventory' and brand.strip() != '' and size.strip() != '' and varietal.strip() != '' and year.strip() == '':

            curr= conn.cursor() 
            if month.strip()=='all':
                print("not entered")
                curr.execute("select Date,sum(Balance) from botdb.inventory inner join botdb.masterdb on `inventory`.`Group`=`masterdb`.`Cat Cd10 Description` where `masterdb`.`Brand Description`= '%s' and `masterdb`.`Varietal/ Flavor Description`= '%s' and `masterdb`.`Size Description`= '%s' and year(`inventory`.`Date`)=year(current_date()) group by Date;"%(brand,varietal,size))
                print("sql done")
                quantity= curr.fetchall()

                resu = [[ i for i, j in quantity ],[ j for i, j in quantity ]]
                data=pd.DataFrame(resu)
                data=data.transpose()
                data.columns=['date','quantity']
                data=data.sort_values(by='date')
                data.quantity=data.quantity.astype(int)
                data.date=data.date.apply(lambda x: x.strftime("%b %y"))
                ind = np.arange(len(data.quantity))

                # Plot data on chart
                plt.plot(data.date, data.quantity,"r-")
                plt.tick_params(axis='x',which='both',bottom=False,top=False,labelbottom=False)
                plt.grid(True, linestyle='-.')
                cellText = [data.quantity.values]
                the_table = plt.table(cellText=cellText, rowLoc='right', rowLabels=['shipment'],
                                 colLabels=data.date.values,
                                 colLoc='center', loc='bottom')
                plt.savefig("tablegraph.jpg")
                #plt.show()
                img="tablegraph.jpg"
                file_upload(channel,img)
            
                curr= conn.cursor()
                curr.execute("select sum(Balance) from botdb.inventory inner join botdb.masterdb on `inventory`.`Group`=`masterdb`.`Cat Cd10 Description` where `masterdb`.`Brand Description`= '%s' and `masterdb`.`Varietal/ Flavor Description`= '%s' and `masterdb`.`Size Description`= '%s' and year(`inventory`.`Date`)=year(current_date());"%(brand,varietal,size))
                cumsum=curr.fetchall()
                res = ("The cummulative inventory for %s %s %s is %d"%(brand,varietal,size,int(cumsum[0][0])))
            elif month.strip()!='all':
                print("single month")
                curr= conn.cursor()
                curr.execute("select sum(Balance) from botdb.inventory inner join botdb.masterdb on `inventory`.`Group`=`masterdb`.`Cat Cd10 Description` where `masterdb`.`Brand Description`= '%s' and `masterdb`.`Varietal/ Flavor Description`= '%s' and `masterdb`.`Size Description`= '%s' and year(`inventory`.`Date`)=year(current_date()) and month(`inventory`.`Date`)= %d;"%(brand,varietal,size,int(month)))
                cumsum=curr.fetchall()
                print("sql done")
                res = ("The cummulative inventory for %s %s %s for %s is %d"%(brand,varietal,size,calendar.month_name[int(month)],int(cumsum[0][0])))
            plt.close()
            response['context']['brand']=None
            response['context']['varietal']=None
            response['context']['month']=None
            response['context']['year']=None
            response['context']['size']=None
            response['context']['number']=None
            response['context']['currentIntent']=None
    except:
        pass
    
    
     #############################compare shipments for brand only##################################
    
    try:
        if response['context']['currentIntent'] == 'compareshipments' and response['context']['compyears']=='two years entered' and brand.strip() != '' and size.strip() == '' and varietal.strip() == '' and year1.strip() != '' and year2.strip()!='' and month.strip()!='':

            curr= conn.cursor() 
            if month.strip()=='all':
                print("not entered")
                curr.execute("select Date,sum(Quantity) from botdb.forecast inner join botdb.masterdb on `forecast`.`master`=`masterdb`.`Cat Cd10 Description` where `masterdb`.`Brand Description`= '%s' and year(`forecast`.`Date`)=%d group by Date;"%(brand,int(year1)))
                
                quantity1= curr.fetchall()
                resu = [[ i for i, j in quantity1 ],[ j for i, j in quantity1 ]]
                curr.execute("select Date,sum(Quantity) from botdb.forecast inner join botdb.masterdb on `forecast`.`master`=`masterdb`.`Cat Cd10 Description` where `masterdb`.`Brand Description`= '%s' and year(`forecast`.`Date`)=%d group by Date;"%(brand,int(year2)))
                quantity2= curr.fetchall()
                resu2 = [[ i for i, j in quantity2 ],[ j for i, j in quantity2 ]]
                data=pd.DataFrame(resu)
                data=data.append([resu2[1]])
                data=data.transpose()
                data.columns=['date','quantity1','quantity2']
                data=data.sort_values(by='date')
                data.quantity1=data.quantity1.astype(int)
                data.quantity2=data.quantity2.astype(int)
                data.date=data.date.apply(lambda x: x.strftime("%b %y"))
                #ind = np.arange(len(data.quantity))
                print("dataframe created")
                # Plot data on chart
                plt.plot(data.date, data.quantity1,"r-")
                plt.plot(data.date, data.quantity2,"b-")
                plt.tick_params(axis='x',which='both',bottom=False,top=False,labelbottom=False)
                plt.grid(True, linestyle='-.')
                plt.legend([year1,year2])
                cellText = [data.quantity1.values,data.quantity2.values]
                the_table = plt.table(cellText=cellText, rowLoc='right', rowLabels=[year1,year2],
                                 colLabels=data.date.values,
                                 colLoc='center', loc='bottom')
                plt.savefig("tablegraph.jpg")
                #plt.show()
                print("plot saved")
                img="tablegraph.jpg"
                file_upload(channel,img)
            
                res = ("Comparision for %s for %d vs %d"%(brand,int(year1),int(year2)))
            elif month.strip()!='all':
                print("single month")
                curr= conn.cursor()
                curr.execute("select sum(Quantity) from botdb.forecast inner join botdb.masterdb on `forecast`.`master`=`masterdb`.`Cat Cd10 Description` where `masterdb`.`Brand Description`= '%s' and year(`forecast`.`Date`)=%d and month(`forecast`.`Date`)=%d;"%(brand,int(year1),int(month)))
                value1=curr.fetchall()
                curr.execute("select sum(Quantity) from botdb.forecast inner join botdb.masterdb on `forecast`.`master`=`masterdb`.`Cat Cd10 Description` where `masterdb`.`Brand Description`= '%s' and year(`forecast`.`Date`)=%d and month(`forecast`.`Date`)=%d;"%(brand,int(year2),int(month)))
                value2=curr.fetchall()
                print("sql done")
                res = ("The shipment quantity for %s for %s is %d for %d and %d for %d"%(brand,calendar.month_name[int(month)],int(value1[0][0]),int(year1),int(value2[0][0]),int(year2)))
            plt.close()
            response['context']['brand']=None
            response['context']['varietal']=None
            response['context']['month']=None
            response['context']['year']=None
            response['context']['size']=None
            response['context']['number']=None
            response['context']['year1']=None
            response['context']['year2']=None
            response['context']['currentIntent']=None
    except:
        pass
    
     #############################compare shipments for brand and size ##################################
    
    try:
        if response['context']['currentIntent'] == 'compareshipments' and response['context']['compyears']=='two years entered' and brand.strip() != '' and size.strip() != '' and varietal.strip() == '' and year1.strip() != '' and year2.strip()!='' and month.strip()!='':

            curr= conn.cursor() 
            if month.strip()=='all':
                print("not entered")
                curr.execute("select Date,sum(Quantity) from botdb.forecast inner join botdb.masterdb on `forecast`.`master`=`masterdb`.`Cat Cd10 Description` where `masterdb`.`Brand Description`= '%s' and `masterdb`.`Size Description`= '%s' and year(`forecast`.`Date`)=%d group by Date;"%(brand,size,int(year1)))
                
                quantity1= curr.fetchall()
                resu = [[ i for i, j in quantity1 ],[ j for i, j in quantity1 ]]
                curr.execute("select Date,sum(Quantity) from botdb.forecast inner join botdb.masterdb on `forecast`.`master`=`masterdb`.`Cat Cd10 Description` where `masterdb`.`Brand Description`= '%s' and `masterdb`.`Size Description`= '%s' and year(`forecast`.`Date`)=%d group by Date;"%(brand,size,int(year2)))
                quantity2= curr.fetchall()
                resu2 = [[ i for i, j in quantity2 ],[ j for i, j in quantity2 ]]
                data=pd.DataFrame(resu)
                data=data.append([resu2[1]])
                data=data.transpose()
                data.columns=['date','quantity1','quantity2']
                data=data.sort_values(by='date')
                data.quantity1=data.quantity1.astype(int)
                data.quantity2=data.quantity2.astype(int)
                data.date=data.date.apply(lambda x: x.strftime("%b %y"))
                #ind = np.arange(len(data.quantity))
                print("dataframe created")
                # Plot data on chart
                plt.plot(data.date, data.quantity1,"r-")
                plt.plot(data.date, data.quantity2,"b-")
                plt.tick_params(axis='x',which='both',bottom=False,top=False,labelbottom=False)
                plt.grid(True, linestyle='-.')
                plt.legend([year1,year2])
                cellText = [data.quantity1.values,data.quantity2.values]
                the_table = plt.table(cellText=cellText, rowLoc='right', rowLabels=[year1,year2],
                                 colLabels=data.date.values,
                                 colLoc='center', loc='bottom')
                plt.savefig("tablegraph.jpg")
                #plt.show()
                print("plot saved")
                img="tablegraph.jpg"
                file_upload(channel,img)
            
                res = ("Comparision for %s %s for %d vs %d"%(brand,size,int(year1),int(year2)))
            elif month.strip()!='all':
                print("single month")
                curr= conn.cursor()
                curr.execute("select sum(Quantity) from botdb.forecast inner join botdb.masterdb on `forecast`.`master`=`masterdb`.`Cat Cd10 Description` where `masterdb`.`Brand Description`= '%s' and `masterdb`.`Size Description`= '%s' and year(`forecast`.`Date`)=%d and month(`forecast`.`Date`)=%d;"%(brand,size,int(year1),int(month)))
                value1=curr.fetchall()
                curr.execute("select sum(Quantity) from botdb.forecast inner join botdb.masterdb on `forecast`.`master`=`masterdb`.`Cat Cd10 Description` where `masterdb`.`Brand Description`= '%s' and `masterdb`.`Size Description`= '%s' and year(`forecast`.`Date`)=%d and month(`forecast`.`Date`)=%d;"%(brand,size,int(year2),int(month)))
                value2=curr.fetchall()
                print("sql done")
                res = ("The shipment quantity for %s %s for %s is %d for %d and %d for %d"%(brand,size,calendar.month_name[int(month)],int(value1[0][0]),int(year1),int(value2[0][0]),int(year2)))
            plt.close()
            response['context']['brand']=None
            response['context']['varietal']=None
            response['context']['month']=None
            response['context']['year']=None
            response['context']['size']=None
            response['context']['number']=None
            response['context']['year1']=None
            response['context']['year2']=None
            response['context']['currentIntent']=None
    except:
        pass
    
     #############################compare shipments for brand and varietal ##################################
    
    try:
        if response['context']['currentIntent'] == 'compareshipments' and response['context']['compyears']=='two years entered' and brand.strip() != '' and size.strip() == '' and varietal.strip() != '' and year1.strip() != '' and year2.strip()!='' and month.strip()!='':

            curr= conn.cursor() 
            if month.strip()=='all':
                print("not entered")
                curr.execute("select Date,sum(Quantity) from botdb.forecast inner join botdb.masterdb on `forecast`.`master`=`masterdb`.`Cat Cd10 Description` where `masterdb`.`Brand Description`= '%s' and `masterdb`.`Varietal/ Flavor Description`= '%s' and year(`forecast`.`Date`)=%d group by Date;"%(brand,varietal,int(year1)))
                
                quantity1= curr.fetchall()
                resu = [[ i for i, j in quantity1 ],[ j for i, j in quantity1 ]]
                curr.execute("select Date,sum(Quantity) from botdb.forecast inner join botdb.masterdb on `forecast`.`master`=`masterdb`.`Cat Cd10 Description` where `masterdb`.`Brand Description`= '%s' and `masterdb`.`Varietal/ Flavor Description`= '%s' and year(`forecast`.`Date`)=%d group by Date;"%(brand,varietal,int(year2)))
                quantity2= curr.fetchall()
                resu2 = [[ i for i, j in quantity2 ],[ j for i, j in quantity2 ]]
                data=pd.DataFrame(resu)
                data=data.append([resu2[1]])
                data=data.transpose()
                data.columns=['date','quantity1','quantity2']
                data=data.sort_values(by='date')
                data.quantity1=data.quantity1.astype(int)
                data.quantity2=data.quantity2.astype(int)
                data.date=data.date.apply(lambda x: x.strftime("%b %y"))
                #ind = np.arange(len(data.quantity))
                print("dataframe created")
                # Plot data on chart
                plt.plot(data.date, data.quantity1,"r-")
                plt.plot(data.date, data.quantity2,"b-")
                plt.tick_params(axis='x',which='both',bottom=False,top=False,labelbottom=False)
                plt.grid(True, linestyle='-.')
                plt.legend([year1,year2])
                cellText = [data.quantity1.values,data.quantity2.values]
                the_table = plt.table(cellText=cellText, rowLoc='right', rowLabels=[year1,year2],
                                 colLabels=data.date.values,
                                 colLoc='center', loc='bottom')
                plt.savefig("tablegraph.jpg")
                #plt.show()
                print("plot saved")
                img="tablegraph.jpg"
                file_upload(channel,img)
            
                res = ("Comparision for %s %s for %d vs %d"%(brand,varietal,int(year1),int(year2)))
            elif month.strip()!='all':
                print("single month")
                curr= conn.cursor()
                curr.execute("select sum(Quantity) from botdb.forecast inner join botdb.masterdb on `forecast`.`master`=`masterdb`.`Cat Cd10 Description` where `masterdb`.`Brand Description`= '%s' and `masterdb`.`Varietal/ Flavor Description`= '%s' and year(`forecast`.`Date`)=%d and month(`forecast`.`Date`)=%d;"%(brand,varietal,int(year1),int(month)))
                value1=curr.fetchall()
                curr.execute("select sum(Quantity) from botdb.forecast inner join botdb.masterdb on `forecast`.`master`=`masterdb`.`Cat Cd10 Description` where `masterdb`.`Brand Description`= '%s' and `masterdb`.`Varietal/ Flavor Description`= '%s' and year(`forecast`.`Date`)=%d and month(`forecast`.`Date`)=%d;"%(brand,varietal,int(year2),int(month)))
                value2=curr.fetchall()
                print("sql done")
                res = ("The shipment quantity for %s %s for %s is %d for %d and %d for %d"%(brand,varietal,calendar.month_name[int(month)],int(value1[0][0]),int(year1),int(value2[0][0]),int(year2)))
            plt.close()
            response['context']['brand']=None
            response['context']['varietal']=None
            response['context']['month']=None
            response['context']['year']=None
            response['context']['size']=None
            response['context']['number']=None
            response['context']['year1']=None
            response['context']['year2']=None
            response['context']['currentIntent']=None
    except:
        pass
 
     #############################compare shipments for brand size and varietal ##################################
    
    try:
        if response['context']['currentIntent'] == 'compareshipments' and response['context']['compyears']=='two years entered' and brand.strip() != '' and size.strip() != '' and varietal.strip() != '' and year1.strip() != '' and year2.strip()!='' and month.strip()!='':

            curr= conn.cursor() 
            if month.strip()=='all':
                print("not entered")
                curr.execute("select Date,sum(Quantity) from botdb.forecast inner join botdb.masterdb on `forecast`.`master`=`masterdb`.`Cat Cd10 Description` where `masterdb`.`Brand Description`= '%s' and `masterdb`.`Size Description`= '%s' and `masterdb`.`Varietal/ Flavor Description`= '%s' and year(`forecast`.`Date`)=%d group by Date;"%(brand,size,varietal,int(year1)))
                
                quantity1= curr.fetchall()
                resu = [[ i for i, j in quantity1 ],[ j for i, j in quantity1 ]]
                curr.execute("select Date,sum(Quantity) from botdb.forecast inner join botdb.masterdb on `forecast`.`master`=`masterdb`.`Cat Cd10 Description` where `masterdb`.`Brand Description`= '%s' and `masterdb`.`Size Description`= '%s' and `masterdb`.`Varietal/ Flavor Description`= '%s' and year(`forecast`.`Date`)=%d group by Date;"%(brand,size,varietal,int(year2)))
                quantity2= curr.fetchall()
                resu2 = [[ i for i, j in quantity2 ],[ j for i, j in quantity2 ]]
                data=pd.DataFrame(resu)
                data=data.append([resu2[1]])
                data=data.transpose()
                data.columns=['date','quantity1','quantity2']
                data=data.sort_values(by='date')
                data.quantity1=data.quantity1.astype(int)
                data.quantity2=data.quantity2.astype(int)
                data.date=data.date.apply(lambda x: x.strftime("%b %y"))
                #ind = np.arange(len(data.quantity))
                print("dataframe created")
                # Plot data on chart
                plt.plot(data.date, data.quantity1,"r-")
                plt.plot(data.date, data.quantity2,"b-")
                plt.tick_params(axis='x',which='both',bottom=False,top=False,labelbottom=False)
                plt.grid(True, linestyle='-.')
                plt.legend([year1,year2])
                cellText = [data.quantity1.values,data.quantity2.values]
                the_table = plt.table(cellText=cellText, rowLoc='right', rowLabels=[year1,year2],
                                 colLabels=data.date.values,
                                 colLoc='center', loc='bottom')
                plt.savefig("tablegraph.jpg")
                #plt.show()
                print("plot saved")
                img="tablegraph.jpg"
                file_upload(channel,img)
            
                res = ("Comparision for %s %s %s for %d vs %d"%(brand,varietal,size,int(year1),int(year2)))
            elif month.strip()!='all':
                print("single month")
                curr= conn.cursor()
                curr.execute("select sum(Quantity) from botdb.forecast inner join botdb.masterdb on `forecast`.`master`=`masterdb`.`Cat Cd10 Description` where `masterdb`.`Brand Description`= '%s' and `masterdb`.`Size Description`= '%s' and `masterdb`.`Varietal/ Flavor Description`= '%s' and year(`forecast`.`Date`)=%d and month(`forecast`.`Date`)=%d;"%(brand,size,varietal,int(year1),int(month)))
                value1=curr.fetchall()
                curr.execute("select sum(Quantity) from botdb.forecast inner join botdb.masterdb on `forecast`.`master`=`masterdb`.`Cat Cd10 Description` where `masterdb`.`Brand Description`= '%s' and `masterdb`.`Size Description`= '%s' and `masterdb`.`Varietal/ Flavor Description`= '%s' and year(`forecast`.`Date`)=%d and month(`forecast`.`Date`)=%d;"%(brand,size,varietal,int(year2),int(month)))
                value2=curr.fetchall()
                print("sql done")
                res = ("The shipment quantity for %s %s %s for %s is %d for %d and %d for %d"%(brand,varietal,size,calendar.month_name[int(month)],int(value1[0][0]),int(year1),int(value2[0][0]),int(year2)))
            plt.close()
            response['context']['brand']=None
            response['context']['varietal']=None
            response['context']['month']=None
            response['context']['year']=None
            response['context']['size']=None
            response['context']['number']=None
            response['context']['year1']=None
            response['context']['year2']=None
            response['context']['currentIntent']=None
    except:
        pass

    
     #############################compare shipments for size and varietal ##################################
    
    try:
        if response['context']['currentIntent'] == 'compareshipments' and response['context']['compyears']=='two years entered' and brand.strip() == '' and size.strip() != '' and varietal.strip() != '' and year1.strip() != '' and year2.strip()!='' and month.strip()!='':

            curr= conn.cursor() 
            if month.strip()=='all':
                print("not entered")
                curr.execute("select Date,sum(Quantity) from botdb.forecast inner join botdb.masterdb on `forecast`.`master`=`masterdb`.`Cat Cd10 Description` where `masterdb`.`Size Description`= '%s' and `masterdb`.`Varietal/ Flavor Description`= '%s' and year(`forecast`.`Date`)=%d group by Date;"%(size,varietal,int(year1)))
                
                quantity1= curr.fetchall()
                resu = [[ i for i, j in quantity1 ],[ j for i, j in quantity1 ]]
                curr.execute("select Date,sum(Quantity) from botdb.forecast inner join botdb.masterdb on `forecast`.`master`=`masterdb`.`Cat Cd10 Description` where `masterdb`.`Size Description`= '%s' and `masterdb`.`Varietal/ Flavor Description`= '%s' and year(`forecast`.`Date`)=%d group by Date;"%(size,varietal,int(year2)))
                quantity2= curr.fetchall()
                resu2 = [[ i for i, j in quantity2 ],[ j for i, j in quantity2 ]]
                data=pd.DataFrame(resu)
                data=data.append([resu2[1]])
                data=data.transpose()
                data.columns=['date','quantity1','quantity2']
                data=data.sort_values(by='date')
                data.quantity1=data.quantity1.astype(int)
                data.quantity2=data.quantity2.astype(int)
                data.date=data.date.apply(lambda x: x.strftime("%b %y"))
                #ind = np.arange(len(data.quantity))
                print("dataframe created")
                # Plot data on chart
                plt.plot(data.date, data.quantity1,"r-")
                plt.plot(data.date, data.quantity2,"b-")
                plt.tick_params(axis='x',which='both',bottom=False,top=False,labelbottom=False)
                plt.grid(True, linestyle='-.')
                plt.legend([year1,year2])
                cellText = [data.quantity1.values,data.quantity2.values]
                the_table = plt.table(cellText=cellText, rowLoc='right', rowLabels=[year1,year2],
                                 colLabels=data.date.values,
                                 colLoc='center', loc='bottom')
                plt.savefig("tablegraph.jpg")
                #plt.show()
                print("plot saved")
                img="tablegraph.jpg"
                file_upload(channel,img)
            
                res = ("Comparision for %s %s for %d vs %d"%(varietal,size,int(year1),int(year2)))
            elif month.strip()!='all':
                print("single month")
                curr= conn.cursor()
                curr.execute("select sum(Quantity) from botdb.forecast inner join botdb.masterdb on `forecast`.`master`=`masterdb`.`Cat Cd10 Description` where `masterdb`.`Size Description`= '%s' and `masterdb`.`Varietal/ Flavor Description`= '%s' and year(`forecast`.`Date`)=%d and month(`forecast`.`Date`)=%d;"%(size,varietal,int(year1),int(month)))
                value1=curr.fetchall()
                curr.execute("select sum(Quantity) from botdb.forecast inner join botdb.masterdb on `forecast`.`master`=`masterdb`.`Cat Cd10 Description` where `masterdb`.`Size Description`= '%s' and `masterdb`.`Varietal/ Flavor Description`= '%s' and year(`forecast`.`Date`)=%d and month(`forecast`.`Date`)=%d;"%(size,varietal,int(year2),int(month)))
                value2=curr.fetchall()
                print("sql done")
                res = ("The shipment quantity for %s %s for %s is %d for %d and %d for %d"%(varietal,size,calendar.month_name[int(month)],int(value1[0][0]),int(year1),int(value2[0][0]),int(year2)))
            plt.close()
            response['context']['brand']=None
            response['context']['varietal']=None
            response['context']['month']=None
            response['context']['year']=None
            response['context']['size']=None
            response['context']['number']=None
            response['context']['year1']=None
            response['context']['year2']=None
            response['context']['currentIntent']=None
    except:
        pass
    
     #############################compare shipments for size ##################################
    
    try:
        if response['context']['currentIntent'] == 'compareshipments' and response['context']['compyears']=='two years entered' and brand.strip() == '' and size.strip() != '' and varietal.strip() == '' and year1.strip() != '' and year2.strip()!='' and month.strip()!='':

            curr= conn.cursor() 
            if month.strip()=='all':
                print("not entered")
                curr.execute("select Date,sum(Quantity) from botdb.forecast inner join botdb.masterdb on `forecast`.`master`=`masterdb`.`Cat Cd10 Description` where `masterdb`.`Size Description`= '%s' and year(`forecast`.`Date`)=%d group by Date;"%(size,int(year1)))
                
                quantity1= curr.fetchall()
                resu = [[ i for i, j in quantity1 ],[ j for i, j in quantity1 ]]
                curr.execute("select Date,sum(Quantity) from botdb.forecast inner join botdb.masterdb on `forecast`.`master`=`masterdb`.`Cat Cd10 Description` where `masterdb`.`Size Description`= '%s' and year(`forecast`.`Date`)=%d group by Date;"%(size,int(year2)))
                quantity2= curr.fetchall()
                resu2 = [[ i for i, j in quantity2 ],[ j for i, j in quantity2 ]]
                data=pd.DataFrame(resu)
                data=data.append([resu2[1]])
                data=data.transpose()
                data.columns=['date','quantity1','quantity2']
                data=data.sort_values(by='date')
                data.quantity1=data.quantity1.astype(int)
                data.quantity2=data.quantity2.astype(int)
                data.date=data.date.apply(lambda x: x.strftime("%b %y"))
                #ind = np.arange(len(data.quantity))
                print("dataframe created")
                # Plot data on chart
                plt.plot(data.date, data.quantity1,"r-")
                plt.plot(data.date, data.quantity2,"b-")
                plt.tick_params(axis='x',which='both',bottom=False,top=False,labelbottom=False)
                plt.grid(True, linestyle='-.')
                plt.legend([year1,year2])
                cellText = [data.quantity1.values,data.quantity2.values]
                the_table = plt.table(cellText=cellText, rowLoc='right', rowLabels=[year1,year2],
                                 colLabels=data.date.values,
                                 colLoc='center', loc='bottom')
                plt.savefig("tablegraph.jpg")
                #plt.show()
                print("plot saved")
                img="tablegraph.jpg"
                file_upload(channel,img)
            
                res = ("Comparision for %s for %d vs %d"%(size,int(year1),int(year2)))
            elif month.strip()!='all':
                print("single month")
                curr= conn.cursor()
                curr.execute("select sum(Quantity) from botdb.forecast inner join botdb.masterdb on `forecast`.`master`=`masterdb`.`Cat Cd10 Description` where `masterdb`.`Size Description`= '%s' and year(`forecast`.`Date`)=%d and month(`forecast`.`Date`)=%d;"%(size,int(year1),int(month)))
                value1=curr.fetchall()
                curr.execute("select sum(Quantity) from botdb.forecast inner join botdb.masterdb on `forecast`.`master`=`masterdb`.`Cat Cd10 Description` where `masterdb`.`Size Description`= '%s' and year(`forecast`.`Date`)=%d and month(`forecast`.`Date`)=%d;"%(size,int(year2),int(month)))
                value2=curr.fetchall()
                print("sql done")
                res = ("The shipment quantity for %s for %s is %d for %d and %d for %d"%(size,calendar.month_name[int(month)],int(value1[0][0]),int(year1),int(value2[0][0]),int(year2)))
            plt.close()
            response['context']['brand']=None
            response['context']['varietal']=None
            response['context']['month']=None
            response['context']['year']=None
            response['context']['size']=None
            response['context']['number']=None
            response['context']['year1']=None
            response['context']['year2']=None
            response['context']['currentIntent']=None
    except:
        pass
    
     #############################compare shipments for varietal ##################################
    
    try:
        if response['context']['currentIntent'] == 'compareshipments' and response['context']['compyears']=='two years entered' and brand.strip() == '' and size.strip() == '' and varietal.strip() != '' and year1.strip() != '' and year2.strip()!='' and month.strip()!='':

            curr= conn.cursor() 
            if month.strip()=='all':
                print("not entered")
                curr.execute("select Date,sum(Quantity) from botdb.forecast inner join botdb.masterdb on `forecast`.`master`=`masterdb`.`Cat Cd10 Description` where `masterdb`.`Varietal/ Flavor Description`= '%s' and year(`forecast`.`Date`)=%d group by Date;"%(varietal,int(year1)))
                
                quantity1= curr.fetchall()
                resu = [[ i for i, j in quantity1 ],[ j for i, j in quantity1 ]]
                curr.execute("select Date,sum(Quantity) from botdb.forecast inner join botdb.masterdb on `forecast`.`master`=`masterdb`.`Cat Cd10 Description` where `masterdb`.`Varietal/ Flavor Description`= '%s' and year(`forecast`.`Date`)=%d group by Date;"%(varietal,int(year2)))
                quantity2= curr.fetchall()
                resu2 = [[ i for i, j in quantity2 ],[ j for i, j in quantity2 ]]
                data=pd.DataFrame(resu)
                data=data.append([resu2[1]])
                data=data.transpose()
                data.columns=['date','quantity1','quantity2']
                data=data.sort_values(by='date')
                data.quantity1=data.quantity1.astype(int)
                data.quantity2=data.quantity2.astype(int)
                data.date=data.date.apply(lambda x: x.strftime("%b %y"))
                #ind = np.arange(len(data.quantity))
                print("dataframe created")
                # Plot data on chart
                plt.plot(data.date, data.quantity1,"r-")
                plt.plot(data.date, data.quantity2,"b-")
                plt.tick_params(axis='x',which='both',bottom=False,top=False,labelbottom=False)
                plt.grid(True, linestyle='-.')
                plt.legend([year1,year2])
                cellText = [data.quantity1.values,data.quantity2.values]
                the_table = plt.table(cellText=cellText, rowLoc='right', rowLabels=[year1,year2],
                                 colLabels=data.date.values,
                                 colLoc='center', loc='bottom')
                plt.savefig("tablegraph.jpg")
                #plt.show()
                print("plot saved")
                img="tablegraph.jpg"
                file_upload(channel,img)
            
                res = ("Comparision for %s for %d vs %d"%(varietal,int(year1),int(year2)))
            elif month.strip()!='all':
                print("single month")
                curr= conn.cursor()
                curr.execute("select sum(Quantity) from botdb.forecast inner join botdb.masterdb on `forecast`.`master`=`masterdb`.`Cat Cd10 Description` where `masterdb`.`Varietal/ Flavor Description`= '%s' and year(`forecast`.`Date`)=%d and month(`forecast`.`Date`)=%d;"%(varietal,int(year1),int(month)))
                value1=curr.fetchall()
                curr.execute("select sum(Quantity) from botdb.forecast inner join botdb.masterdb on `forecast`.`master`=`masterdb`.`Cat Cd10 Description` where `masterdb`.`Varietal/ Flavor Description`= '%s' and year(`forecast`.`Date`)=%d and month(`forecast`.`Date`)=%d;"%(varietal,int(year2),int(month)))
                value2=curr.fetchall()
                print("sql done")
                res = ("The shipment quantity for %s for %s is %d for %d and %d for %d"%(varietal,calendar.month_name[int(month)],int(value1[0][0]),int(year1),int(value2[0][0]),int(year2)))
            plt.close()
            response['context']['brand']=None
            response['context']['varietal']=None
            response['context']['month']=None
            response['context']['year']=None
            response['context']['size']=None
            response['context']['number']=None
            response['context']['year1']=None
            response['context']['year2']=None
            response['context']['currentIntent']=None
    except:
        pass

   
   #################################################Code starts for OOS-Out oF Stock Data -Plant#########################################
    try:
        if response['context']['currentIntent'] == 'outOfStockList':
            try:
                plant = response['context']['plant']
                print(plant)
            except:
                plant="all"
            try:
                limit = response['context']['sys_number']
            except:
                limit =None
            
            
            curr= conn.cursor()
            val_exists = 0
            if(plant !="all"):
                curr.execute("select count(distinct `type of issue`) as val from oos_trends where  `type of issue`='{}' and \
                     STR_TO_DATE(`OOS Report`,'%m/%d/%Y') in (select max(STR_TO_DATE(`OOS Report`,'%m/%d/%Y')) \
                    from  oos_trends )".format(plant))
                val_exists = curr.fetchone()
                for k in val_exists:
                    val_exists = k
                    break
            if((val_exists == 1 and plant !="all") or (plant =="all")):
                if(limit!=None):
                    if(plant !="all"):
                        curr.execute(" select  `Master Code`,`Description`,`Size`,`Cases Short`, `Short on`, `bottling on`, \
                        `First Avail Date after Aging` from  (select `Master Code`,`Description`,`Size`,`Cases Short`,`bottling on`, \
                        `Short on`, `First Avail Date after Aging`, `type of issue`, STR_TO_DATE(`OOS Report`,'%m/%d/%Y') as oos_wk_date \
                        from oos_trends where `type of issue`='{}' and  STR_TO_DATE(`OOS Report`,'%m/%d/%Y') in \
                        (select max(STR_TO_DATE(`OOS Report`,'%m/%d/%Y')) from  oos_trends )  ORDER BY \
                        STR_TO_DATE(`OOS Report`,'%m/%d/%Y') DESC, `Cases Short` DESC  limit {} ) as oos ".format(plant,limit))
                    else:
                        curr.execute(" select  `Master Code`,`Description`,`Size`,`Cases Short`, `Short on`, `bottling on`,\
                        `First Avail Date after Aging` from  (select `Master Code`,`Description`,`Size`,`Cases Short`,`bottling on`, \
                        `Short on`, `First Avail Date after Aging`, `type of issue`, STR_TO_DATE(`OOS Report`,'%m/%d/%Y') as oos_wk_date \
                        from oos_trends where  STR_TO_DATE(`OOS Report`,'%m/%d/%Y') in (select max(STR_TO_DATE(`OOS Report`,'%m/%d/%Y')) \
                        from  oos_trends ) ORDER BY STR_TO_DATE(`OOS Report`,'%m/%d/%Y') DESC, `Cases Short` DESC \
                        limit {} ) as oos ".format(limit))
                else:
                    if(plant !="all"):
                        curr.execute("select  `Master Code`,`Description`,`Size`,`Cases Short`, `Short on`, `bottling on`, \
                        `First Avail Date after Aging` from  (select `Master Code`,`Description`,`Size`,`Cases Short`,`bottling on`, \
                        `Short on`, `First Avail Date after Aging`, `type of issue`, STR_TO_DATE(`OOS Report`,'%m/%d/%Y') as oos_wk_date \
                        from oos_trends where `type of issue`='{}' and  STR_TO_DATE(`OOS Report`,'%m/%d/%Y') in \
                        (select max(STR_TO_DATE(`OOS Report`,'%m/%d/%Y')) from  oos_trends ) \
                         ORDER BY STR_TO_DATE(`OOS Report`,'%m/%d/%Y') DESC, `Cases Short` DESC ) as oos ".format(plant))
                    else:
                        print('else')
                        curr.execute("select  `Master Code`,`Description`,`Size`,`Cases Short`, `Short on`, `bottling on`, \
                        `First Avail Date after Aging` from  (select `Master Code`,`Description`,`Size`,`Cases Short`,`bottling on`, \
                        `Short on`, `First Avail Date after Aging`, `type of issue`, STR_TO_DATE(`OOS Report`,'%m/%d/%Y') as oos_wk_date \
                         from oos_trends where STR_TO_DATE(`OOS Report`,'%m/%d/%Y') in (select max(STR_TO_DATE(`OOS Report`,'%m/%d/%Y')) \
                         from  oos_trends )  ORDER BY STR_TO_DATE(`OOS Report`,'%m/%d/%Y') DESC, `Cases Short` DESC ) as oos ")
                
                row_vals = curr.fetchall()
                print(is_not_empty(row_vals))
            
                if(is_not_empty(row_vals)):
                    
                    if(limit!=None):
                        if(plant !="all"):
                            curr.execute(" select  sum(`Cases Short`) as var  from  (select `Master Code`,`Cases Short` \
                            from oos_trends where `type of issue`='{}' and  STR_TO_DATE(`OOS Report`,'%m/%d/%Y') in \
                            (select max(STR_TO_DATE(`OOS Report`,'%m/%d/%Y')) from  oos_trends )  ORDER BY \
                            STR_TO_DATE(`OOS Report`,'%m/%d/%Y') DESC, `Cases Short` DESC  limit {} ) as oos ".format(plant,limit))
                        else:
                            curr.execute(" select  sum(`Cases Short`) as var  from  (select `Master Code`,`Cases Short` \
                            from oos_trends where  STR_TO_DATE(`OOS Report`,'%m/%d/%Y') in \
                            (select max(STR_TO_DATE(`OOS Report`,'%m/%d/%Y')) from  oos_trends )  ORDER BY \
                            STR_TO_DATE(`OOS Report`,'%m/%d/%Y') DESC, `Cases Short` DESC  limit {} ) as oos ".format(limit))
                    else:
                        if(plant !="all"):
                            curr.execute(" select  sum(`Cases Short`) as var  from  (select `Master Code`,`Cases Short` \
                            from oos_trends where `type of issue`='{}' and  STR_TO_DATE(`OOS Report`,'%m/%d/%Y') in \
                            (select max(STR_TO_DATE(`OOS Report`,'%m/%d/%Y')) from  oos_trends )  ORDER BY \
                            STR_TO_DATE(`OOS Report`,'%m/%d/%Y') DESC, `Cases Short` DESC  ) as oos  ".format(plant))
                        else:
                            print('else')
                            curr.execute(" select  sum(`Cases Short`) as var  from  (select `Master Code`,`Cases Short` \
                            from oos_trends where STR_TO_DATE(`OOS Report`,'%m/%d/%Y') in \
                            (select max(STR_TO_DATE(`OOS Report`,'%m/%d/%Y')) from  oos_trends )  ORDER BY \
                            STR_TO_DATE(`OOS Report`,'%m/%d/%Y') DESC, `Cases Short` DESC ) as oos ")
                    
                    count = curr.fetchone()
                    for k in count:
                        count = int(k)
                        break
                    print('count:: ',count)

                    data=row_vals
                    columns = []
                    rows=[]
                    for i in range(len(data)):
                        columns.append(data[i][1])
                        rows.append(data[i][3])
                    import matplotlib.pyplot as plt
                    import seaborn as sns

                    n_rows = len(data)

                    # Add a table at the bottom of the axes
                    colLabels=("Master", "Description","Size", "Cases_Short", "Short_On", "Bottling_On", "First_Available")
                    nrows, ncols = len(data)+1, len(colLabels)
                    hcell, wcell = 0.5, 1

                    #do the table
                    the_table = plt.table(cellText=data,
                          colLabels=colLabels,
                          loc='center',cellLoc = 'left')
                    #print(the_table.properties())
                    cellDict=the_table.get_celld()
                    for i in range(len(data)+1):
                        cellDict[(i,0)].set_width(0.2)
                        cellDict[(i,1)].set_width(0.3)
                        cellDict[(i,2)].set_width(0.2)
                        cellDict[(i,3)].set_width(0.1)
                        cellDict[(i,4)].set_width(0.1)
                        cellDict[(i,5)].set_width(0.1)
                        cellDict[(i,6)].set_width(0.1)

                    plt.axis('off')
                    plt.savefig("outOfStockList.jpg", dpi=300, bbox_inches = 'tight',pad_inches = 0)
                    #plt.tight_layout()


                    # Add a table at the bottom of the axes
                    #plt.show()
                    res="Total number of cases short for plant {} are:{} ".format(plant_full,count)
                    print('res',res)
                    img = 'outOfStockList.jpg'
                    file_upload(channel, img)
                    plt.close()
                else:
                    res = "There is no out of Stock data present for {} are: ".format(plant_full.upper())
            else:
                res = "There is no data present for Plant {} in current week.".format(plant_full.upper())
            response['context']['currentIntent'] =None
            response['context']['plant'] =None
            response['context']['sys_number'] =None
            #response['context']['masterCodeValue'] =None
    except:
        pass
    #################################################Code ends for OOS-Out oF Stock Data -Plant######################################
    
    #################################################Code starts for OOS-Out oF Stock Data -Specific################################
    try:
        if response['context']['currentIntent'] == 'outOfStockSpecific':
            try:
                print('try')
                masterCodeValue = response['context']['masterCodeValue']
            except:
                masterCodeValue = None
            
            curr= conn.cursor()
            print("heyy.....")
           
            if(masterCodeValue !=None):
                curr.execute(" Select count(distinct `Master Code`) as val from oos_trends where lower(`Master Code`)='{}' and \
                     STR_TO_DATE(`OOS Report`,'%m/%d/%Y') in \
                     (select max(STR_TO_DATE(`OOS Report`,'%m/%d/%Y')) from  oos_trends)".format(masterCodeValue))
                val_exists = curr.fetchone()
                for k in val_exists:
                    val_exists = k
                    break
                
            if(masterCodeValue == None):
                res = "Master Code is invalid"
            elif(val_exists == 1 and masterCodeValue !=None ):
                #By Master Code
                curr.execute("Select  `Master Code`,`Description`,`Size`,`Cases Short`, `Short on`, `bottling on`,\
                `First Avail Date after Aging` from (select `Master Code`,`Description`,`Size`,`Cases Short`,`bottling on`, \
                `Short on`, `First Avail Date after Aging`, `type of issue`, STR_TO_DATE(`OOS Report`,'%m/%d/%Y') as oos_wk_date  \
                from oos_trends  where lower(`master code`)='{}' and STR_TO_DATE(`OOS Report`,'%m/%d/%Y') in \
                (select max(STR_TO_DATE(`OOS Report`,'%m/%d/%Y'))   from  oos_trends ) \
                ORDER BY STR_TO_DATE(`OOS Report`,'%m/%d/%Y') DESC, `Cases Short` DESC  ) as oos".format(masterCodeValue))
                
                row_vals = curr.fetchall()

                if(is_not_empty(row_vals)):
                
                    curr.execute("Select  sum(`Cases Short`) as var  from  (select `Master Code`,`Description`,`Size`, \
                    `Cases Short`,`bottling on`, `Short on`,  `First Avail Date after Aging`, `type of issue`, \
                    STR_TO_DATE(`OOS Report`,'%m/%d/%Y') as oos_wk_date from oos_trends where lower(`master code`)='{}' \
                    and STR_TO_DATE(`OOS Report`,'%m/%d/%Y') in \
                    (select max(STR_TO_DATE(`OOS Report`,'%m/%d/%Y')) from  oos_trends ) \
                    ORDER BY STR_TO_DATE(`OOS Report`,'%m/%d/%Y') DESC, \
                    `Cases Short` DESC  ) as oos".format(masterCodeValue))
                    
                    print(masterCodeValue)
                    count = curr.fetchone()
                    for k in count:
                        count = int(k)
                        break
                    print('count:: ',count)

                    data=row_vals
                    columns = []
                    rows=[]
                    for i in range(len(data)):
                        columns.append(data[i][1])
                        rows.append(data[i][3])
                    #import matplotlib.pyplot as plt
                    #import seaborn as sns

                    n_rows = len(data)

                    # Add a table at the bottom of the axes
                    colLabels=("Master", "Description","Size", "Cases_Short", "Short_On", "Bottling_On", "First_Available")
                    nrows, ncols = len(data)+1, len(colLabels)
                    hcell, wcell = 0.5, 1

                    #do the table
                    the_table = plt.table(cellText=data,
                          colLabels=colLabels,
                          loc='center',cellLoc = 'left')
                    cellDict=the_table.get_celld()
                    for i in range(len(data)+1):
                        cellDict[(i,0)].set_width(0.2)
                        cellDict[(i,1)].set_width(0.3)
                        cellDict[(i,2)].set_width(0.2)
                        cellDict[(i,3)].set_width(0.1)
                        cellDict[(i,4)].set_width(0.1)
                        cellDict[(i,5)].set_width(0.1)
                        cellDict[(i,6)].set_width(0.1)
                    plt.axis('off')
                    plt.savefig("outOfStockSpecific.jpg", dpi=500, bbox_inches = 'tight',pad_inches = 0)

                    # Add a table at the bottom of the axes
                    #plt.show()
                    res="Total number of cases short for master code- {} are:{} ".format(masterCodeValue,count)
                    print('res',res)
                    img = 'outOfStockSpecific.jpg'
                    file_upload(channel, img)
                    plt.close()
                else:
                    res = "There is no out of Stock data present for {}".format(masterCodeValue.upper())
            else:
                res = "There is no data present for Master code {} in current week.".format(masterCodeValue.upper())
            response['context']['currentIntent'] =None
            #response['context']['plant'] =None
            #response['context']['sys_number'] =None
            response['context']['masterCodeValue'] =None
    except:
        pass
   #################################################Code ends for Out oF Stock Data -Specific ########################################
 
    #################################################Code starts for Out Of Stock Trend #########################################
    try:
        if response['context']['currentIntent'] == 'outOfStockTrend':
            print("Inside OOS Trend")
            val =''
            try:
                print('try')
                masterCodeValue = response['context']['masterCodeValue']
            except:
                masterCodeValue = None
            curr = conn.cursor() 
            print('mastercode:: ',masterCodeValue)
            print('brand:: ',brand)
            print('size:: ',size)
            print('plant ',plant)
            
            if(masterCodeValue !=None or brand !="" or  size !="" or plant !=None):
                if(masterCodeValue !=None):
                    curr.execute("Select `Week #`,sum(`Cases Short`) as var from oos_trends where `master code`='{}' \
                    group by `OOS Report` ".format(masterCodeValue))
                elif(brand !=""):
                    curr.execute("Select `Week #`,sum(`Cases Short`) as var from oos_trends where `Description` like '%{}%'\
                      group by `OOS Report` ".format(brand))
                elif(size !=""):
                    curr.execute(" Select `Week #`,sum(`Cases Short`) as var from oos_trends where `size` like '%{}%' \
                      group by `OOS Report` ".format(size))
                elif(plant !=None):
                    curr.execute("Select `Week #`,sum(`Cases Short`) as var from oos_trends where `type of issue`='{}'\
                      group by `OOS Report` ".format(plant))
            else:
                curr.execute("select `Week #`,sum(`Cases Short`) as var from oos_trends group by `OOS Report` ")

            row_vals = curr.fetchall()
            print(row_vals)
            
            if(is_not_empty(row_vals)):  
            # count total no of cases Short displayed in out of stock trends
                if(masterCodeValue !=None or brand !="" or  size !="" or plant !=None):
                    if(masterCodeValue !=None):
                        curr.execute("Select sum(`Cases Short`) as var from oos_trends  where `master code`='{}'".format(masterCodeValue))
                        val= masterCodeValue
                    elif(brand !=""):
                        curr.execute("Select sum(`Cases Short`) as var from oos_trends where `Description` like '%{}%' ".format(brand))
                        val= brand
                    elif(size !=""):
                        curr.execute(" Select sum(`Cases Short`) as var from oos_trends where `size` like '%{}%' ".format(size))
                        val= size
                    elif(plant !=None):
                        curr.execute("Select sum(`Cases Short`) as var from oos_trends where `type of issue`='{}' ".format(plant))
                        val= plant
                else:
                    print('inside else block')
                    curr.execute("select sum(`Cases Short`) as var from oos_trends")
                    
                count = curr.fetchone()
                for k in count:
                    count = int(k)
                    break
                #print(sql_query)
                print('count:: ',count)
                
                data=row_vals
                columns = []
                rows=[]
                for i in range(len(data)):
                    columns.append(data[i][0])
                    rows.append(data[i][1])
                print('columns ',columns)
                print('rows ',rows)
                
                import matplotlib.pyplot as plt
                import seaborn as sns
                
                # Get some pastel shades for the colors
                colors = plt.cm.BuPu(np.linspace(0, 0.5, len(rows)))
                n_rows = len(data)
                print('n_rows ',n_rows)
                #plt.figure(figsize=(16,12))
                plt.xticks(rotation=90)
                if(chart_type!=None):
                    df = pd.DataFrame( [[ij for ij in i] for i in data] )
                    df.rename(columns={0: 'Week_No', 1: 'Cases_Short'}, inplace=True);
                    df = pd.DataFrame({'value': list(df['Cases_Short'])},
                                  index=(list(df['Week_No'])))
                    print('df ',df)
                    plt.plot(df)
                else:
                    for row in range(n_rows):
                        sns.set()
                        plt.bar(columns, rows, align='center',  color=colors[row])
                    plt.xlabel('Week')
                    plt.ylabel('Cases Short')
                # Reverse colors and text labels to display the last value at the top.
                colors = colors[::-1]
                
                # Add a table at the bottom of the axes
                colLabels=("Week_No", "Cases_Short")
                nrows, ncols = len(data)+1, len(colLabels)
                hcell, wcell = 0.5, 1
                print('nrows ',nrows)
                print('ncols ',ncols)
                print('val ',val)
                if(val!=""):
                    plt.title('Out of Stock Trend for {}'.format(val))
                else:
                    plt.title('Out of Stock Trend')

                plt.savefig("OutOfStockTrend.jpg", dpi=500, bbox_inches = 'tight')
                print('yo')
                # Add a table at the bottom of the axes
                #plt.show()   
                if(masterCodeValue !=None):
                    res =" Total out of stock trend data displayed for master code {} is-{}".format(masterCodeValue,count)
                elif(brand !=""):
                    res =" Total out of stock trend data displayed for brand {} is-{}".format(brand,count)
                elif(size !=""):
                    res =" Total out of stock trend data displayed for size {} is-{}".format(size,count)
                elif(plant !=None):
                    res =" Total out of stock trend data for plant {} displayed is-{}".format(plant_full,count)
                else:
                    res =" Total out of stock trend data displayed is-{}".format(count)
                
                print(res)
                img = 'OutOfStockTrend.jpg'
                file_upload(channel, img)
                plt.close()
            else:
                res = "There is no trend present"
            response['context']['currentIntent'] =None
            response['context']['plant'] =None
            response['context']['masterCodeValue'] =None
            response['context']['brand'] =None
            response['context']['size'] =None
            response['context']['chart_type'] =None
            
    except:
        pass
    #################################################Code ends for oos -out of stock trend ##########################################
     #################################################Code starts for Customer Orders#######################################
    try:
        if response['context']['currentIntent'] == 'customerOrders':
            try:
                print('try week')
                weekValue = response['context']['week_value']
            except:
                weekValue = None
            try:
                print('try day')
                dayValue = response['context']['day_value']
            except:
                dayValue = None
            try:
                limit = response['context']['sys_number']
            except:
                limit =1
            print("weekValue::::: ",weekValue)
            print("dayValue:::::: ",dayValue)
            print("limit::::::::: ",limit)
            curr= conn.cursor()
            print("heyy.....")
             
            if(weekValue == None and dayValue == None):
                res = "Week is invalid"
            elif(weekValue !=None or dayValue!=None):
                print("inside else")
                
                if(weekValue !=None):
                    curr.execute(" Select   FORMAT( sum(qty),0) as qty from (select  date(`Date`) as dt, \
                    sum(`Quantity`) as qty, WEEK(date(`Date`),4) AS WEEK  from  `customerorders` \
                    where  date(`date`) <= NOW() group by WEEK(date(`Date`),4) \
                    order by WEEK(date(`Date`),4) DESC LIMIT {} ) asa ".format(limit))
                else:
                    curr.execute("Select FORMAT(sum(qty),0)  from (select  date(`Date`) as dt, sum(`Quantity`)  as qty \
                    from `customerorders`    WHERE date(`Date`) <= NOW()  group by date(`Date`) \
                    order by  date(`Date`)  DESC LIMIT {}) sd".format(limit))
                    
                count = curr.fetchone()
                for k in count:
                    count = k
                    break
                #print(sql_query)
                print('count:: ',count)
                
                #By Week
                if(weekValue !=None):
                    curr.execute("  Select CONCAT(dt,' (Wk# ', @rownum := @rownum + 1, ')') as Week , \
                    FORMAT(qty,0) as qty from (select  date(`Date`) as dt,sum(`Quantity`) as qty, WEEK(date(`Date`),4) AS WEEK \
                    from `customerorders`  where  date(`date`) <= NOW() group by WEEK(date(`Date`),4) \
                    order by WEEK(date(`Date`),4) DESC LIMIT {} ) asa CROSS JOIN (select @rownum := 0) r ".format(limit))
                    col1_value="Week"
                #By Day
                elif(dayValue!=None):
                    curr.execute("select  date(`Date`) as dt, FORMAT(sum(`Quantity`),0)  as qty from `customerorders` \
                    WHERE date(`Date`) <= NOW()  group by date(`Date`) order by  date(`Date`)  DESC LIMIT {} ".format(limit))
                    col1_value="Date"
                
                row_vals = curr.fetchall()
                print('row_vals:: ',row_vals)

                data=row_vals
                import matplotlib.pyplot as plt
                import seaborn as sns

                n_rows = len(data)
                

                # Add a table at the bottom of the axes
                colLabels=(col1_value, "Quantity")
                nrows, ncols = len(data)+1, len(colLabels)
                hcell, wcell = 0.5, 1

                #do the table
                the_table = plt.table(cellText=data,
                      colLabels=colLabels,
                      loc='center',cellLoc = 'center')
                cellDict=the_table.get_celld()
                for i in range(len(data)+1):
                    cellDict[(i,0)].set_width(0.3)
                    cellDict[(i,1)].set_width(0.2)
                plt.axis('off')
                #plt.title('Customer orders for last {} {}'.format(limit,col1_value))
                plt.savefig("customerOrders.jpg", dpi=500, bbox_inches = 'tight',pad_inches = 0)
                print('yo')

                # Add a table at the bottom of the axes
                plt.show()
                #res="Total number of cases short for master code- {} are:{} ".format(masterCodeValue,count)
                #res="Heyy"
                res =" Cumulative Quantity-{}".format(count)
                print('res',res)
                img = 'customerOrders.jpg'
                file_upload(channel, img)
                plt.close()
            else:
                res = "There is no data present for last few days/weeks."
            response['context']['currentIntent'] =None
            response['context']['week_value'] =None
            response['context']['day_value'] =None
            response['context']['sys_number'] =None
    except:
        pass
    #################################################Code ends for Customer Orders#######################################
###########################################################  Output   ###################################################################
    
    slack_output = slack_output + str(res)
    
    if slack_output == '' and brand.strip() == '' and size.strip() != '' and varietal.strip() != '' and year.strip() != '' and month.strip() != '':
        slack_output = 'Record for the given values for "' + str(brand) + '" does not exists. Please check'        
    
    if 'actions' in response:
        print("oops i went here")
        if response['actions'][0]['type'] == 'client':
            current_action = response['actions'][0]['name']
   
    return(context,slack_output,current_action)