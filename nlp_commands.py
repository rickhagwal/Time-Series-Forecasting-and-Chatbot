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
from datetime import datetime
from matplotlib import pyplot as plt
import seaborn as sns
import matplotlib.pylab as pl
from slack_commands import slack_tiles, message_buttons,file_upload
import six
import fbprophet
from math import ceil
import re
import dateutil.parser

def is_not_empty(any_structure):
    if any_structure:
        print('Structure is not empty.')
        return True
    else:
        print('Structure is empty.')
        return False

def set_align_for_column(table, col, align):
    #print(table._cells)
    cells = [key for key in table._cells if key[1] == col]
    #print('cells are:: ')
    for cell in cells:
        #print(table._cells[cell])
        table._cells[cell]._loc = align
        #print('yo')
        #print(table._cells[cell]._loc)
     
        
    #from forecast table
def part_sql_query(month,brand,size,varietal,temp_year,specificType):
    
    if specificType == 'inventory':
        part_query = " SUM(Balance) AS qty FROM \
        inventory inner join `masterdb` on `inventory`.`Group`=`masterdb`.`Cat Cd10 Description` \
        WHERE  year(`inventory`.`Date`)={} "
    else:
        if specificType !='orders':
            part_query = " SUM(`Quantity`) AS qty FROM \
            `forecast` inner join `masterdb` on `forecast`.`master`=`masterdb`.`Cat Cd10 Description` \
            WHERE  year(`forecast`.`Date`)={} "
        else:
            part_query = " SUM(`Quantity`) AS qty FROM \
            `customerorders` inner join `masterdb` on `customerorders`.`Group`=`masterdb`.`Cat Cd10 Description` \
            WHERE  year(`customerorders`.`Date`)={} "
    
    if month=='ytd' or month == 'actual' : #ytd or actual shipments
        if specificType == 'inventory':
            part_query = part_query + "  and  month(`inventory`.`Date`)< month(NOW()) "
        else:
            #temp_year =='2019' and
            if specificType !='orders':
                part_query = part_query + "  and  month(`forecast`.`Date`)< month(NOW()) "
            else:
                part_query = part_query + "  and  month(`customerorders`.`Date`)< month(NOW()) "
    elif month=='roy' : #rest of the year shipments
        #temp_year =='2019' and
        if specificType == 'inventory':
            part_query = part_query + "  and  month(`inventory`.`Date`)>= month(NOW()) "
        else:
            if specificType !='orders':
                part_query = part_query + "  and  month(`forecast`.`Date`)>= month(NOW()) "
            else:
                part_query = part_query + "  and  month(`customerorders`.`Date`)>= month(NOW()) "
    elif month!='all': #particular month wise
        if specificType == 'inventory':
            part_query = part_query + "  and  month(`inventory`.`Date`)={} "
        else:
            if specificType !='orders':
                part_query = part_query + "  and  month(`forecast`.`Date`)={} "
            else:
                part_query = part_query + "  and  month(`customerorders`.`Date`)={} "
        
    if(brand != '' or size != '' or varietal != ''):
        if(brand != ''):
            part_query = part_query +" and `masterdb`.`Brand Description`= '{}'  "
        if(size != ''):
            part_query = part_query +" and `masterdb`.`Size Description`= '{}'  "
        if(varietal != ''):
            part_query = part_query +" and `masterdb`.`Varietal/ Flavor Description`= '{}'  "
    
    return part_query

def execute_sql_queries(curr,sql_query_final,weekDayValue,pastFutureValue,limit,masterCodeValue,brand,size,varietal,
                        uniquevar,month,value):
    print('#################inside execute_sql_queries#########################')
    
    #if month.strip()!='all' and month.strip()!='ytd':
        #curr.execute(sql_query.format(valyr.get("value") ,month.strip()))
    #else:
        #curr.execute(sql_query.format(valyr.get("value")))
    print(curr,' ',sql_query_final,' ',weekDayValue,' ',pastFutureValue,' ',limit,' ',masterCodeValue,' ',brand,' ',size,' ',varietal,' ',
                        uniquevar,' ',month,' ',value)   
    print('*************************sql_query_final*************************')
    print(sql_query_final)                
    if(curr!=''):
        print('inside if')
        print(value)
        print(brand)
        print(size)
        print(varietal)
        #master code
        if(masterCodeValue!=None):
            curr.execute(sql_query_final.format(limit,masterCodeValue))

        elif(brand.strip() != '' or size.strip() != '' or varietal.strip() != ''):
            #all present
            if(brand.strip() != '' and size.strip() != '' and varietal.strip() != ''):
                print('all')
                if(pastFutureValue =='last' or pastFutureValue =='next'):
                    curr.execute(sql_query_final.format(limit,brand.strip(),size.strip(),varietal.strip()))
                elif (month.strip()!='all' and month.strip()!='ytd' and month.strip()!='roy' and month.strip()!='month'):
                    curr.execute(sql_query_final.format(value ,month.strip(),brand.strip(),size.strip(),varietal.strip()))
                elif(month.strip()=='all' or month.strip()=='ytd' or month.strip()=='roy'):
                    curr.execute(sql_query_final.format(value,brand.strip(),size.strip(),varietal.strip()))
                else:
                    curr.execute(sql_query_final.format(brand.strip(),size.strip(),varietal.strip()))

            #single present    
            elif(brand.strip() != '' and size.strip() == '' and varietal.strip() == ''):
                print('brand')
                if(pastFutureValue =='last' or pastFutureValue =='next'):
                    print('inside 1')
                    curr.execute(sql_query_final.format(limit,brand))
                elif (month.strip()!='all' and month.strip()!='ytd' and month.strip()!='roy' and month.strip()!='month'):
                    print('inside 2')
                    print('value ',value)
                    print('month ',month)
                    print('brand ',brand)
                    curr.execute(sql_query_final.format(value ,month.strip(),brand.strip()))
                elif(month.strip()=='all' or month.strip()=='ytd' or month.strip()=='roy'):
                    print('inside 3')
                    curr.execute(sql_query_final.format(value,brand.strip()))
                else:
                    print('else brand')
                    curr.execute(sql_query_final.format(brand))

            elif(brand.strip() == '' and size.strip() != '' and varietal.strip() == ''):
                print('size')
                print('heyy')
                if(pastFutureValue =='last' or pastFutureValue =='next'):
                    curr.execute(sql_query_final.format(limit,size.strip()))
                elif ( month!='all' and month!='ytd' and month!='roy' and month.strip()!='month'):
                    curr.execute(sql_query_final.format(value ,month,size.strip()))
                elif(month.strip()=='all' or month.strip()=='ytd' or month.strip()=='roy'):
                    print('elif')
                    curr.execute(sql_query_final.format(value,size.strip()))
                else:
                    curr.execute(sql_query_final.format(size.strip()))

            elif(brand.strip() == '' and size.strip() == '' and varietal.strip() != ''):
                print('varietal')
                if(pastFutureValue =='last' or pastFutureValue =='next'):
                    curr.execute(sql_query_final.format(limit,varietal.strip()))
                elif (month.strip()!='all' and month.strip()!='ytd' and month.strip()!='month' and month.strip()!='roy'):
                    curr.execute(sql_query_final.format(value ,month.strip(),varietal.strip()))
                elif(month.strip()=='all'  or month.strip()=='ytd' or month.strip()=='roy'):
                    curr.execute(sql_query_final.format(value,varietal.strip()))
                else:
                    curr.execute(sql_query_final.format(varietal.strip()))

            #double present    
            elif(brand.strip() != '' and size.strip() != '' and varietal.strip() == ''):
                print('brand size')
                if(pastFutureValue =='last' or pastFutureValue =='next'):
                    curr.execute(sql_query_final.format(limit,brand.strip(),size.strip()))
                elif (month.strip()!='all' and month.strip()!='ytd' and month.strip()!='month' and month.strip()!='roy'):
                    curr.execute(sql_query_final.format(value ,month.strip(),brand.strip(),size.strip()))
                elif(month.strip()=='all' or month.strip()=='ytd' or month.strip()=='roy'):
                    curr.execute(sql_query_final.format(value,brand.strip(),size.strip()))
                else:
                    curr.execute(sql_query_final.format(brand.strip(),size.strip()))

            elif(brand.strip() == '' and size.strip() != '' and varietal.strip() != ''):
                print('size varietal')
                if(pastFutureValue =='last' or pastFutureValue =='next'):
                    curr.execute(sql_query_final.format(limit,size.strip(),varietal.strip()))
                elif (month.strip()!='all' and month.strip()!='ytd' and month.strip()!='month' and month.strip()!='roy'):
                    curr.execute(sql_query_final.format(value ,month.strip(),size.strip(),varietal.strip()))
                elif(month.strip()=='all' or month.strip()=='ytd' or month.strip()=='roy'):
                    curr.execute(sql_query_final.format(value,size.strip(),varietal.strip()))
                else:
                    curr.execute(sql_query_final.format(size.strip(),varietal.strip()))

            elif(brand.strip() != '' and size.strip() == '' and varietal.strip() != ''):
                print('brand varietal')
                print(sql_query_final)
                if(pastFutureValue =='last' or pastFutureValue =='next'):
                    curr.execute(sql_query_final.format(limit,brand.strip(),varietal.strip()))
                elif (month.strip()!='all' and month.strip()!='ytd' and month.strip()!='month' and month.strip()!='roy'):
                    curr.execute(sql_query_final.format(value ,month.strip(),brand.strip(),varietal.strip()))
                elif(month.strip()=='all' or month.strip()=='ytd' or month.strip()=='roy'):
                    curr.execute(sql_query_final.format(value,brand.strip(),varietal.strip()))
                else:
                    curr.execute(sql_query_final.format(brand.strip(),varietal.strip()))
        else:
            print('else')
            if(pastFutureValue =='last' or pastFutureValue =='next'):
                curr.execute(sql_query_final.format(limit))
            elif (month.strip()!='all' and month.strip()!='ytd' and month.strip()!='month' and month.strip()!='roy'):
                curr.execute(sql_query_final.format(value ,month.strip()))
            elif(month.strip()=='all' or month.strip()=='ytd' or month.strip()=='roy'):
                print('over here')
                print(value)
                curr.execute(sql_query_final.format(value))
            else:
                curr.execute(sql_query_final)
    if(uniquevar =="count"):
        count = curr.fetchone()
        for k in count:
            count = k
            break
        print('count:: ',count)
        return count
    else:
        row_vals = curr.fetchall()
        print('row_vals ',row_vals)
        return row_vals
    
    
def variation(brand,size,varietal):
    print('inside variation')
    print(brand)
    print(size)
    print(varietal)
    statement=''
    if brand.strip()!='':
        if statement!='':
            statement+=" and "
            statement+=("`masterdb`.`Brand Description`= '%s'"%(brand))
        else:
            statement+=("`masterdb`.`Brand Description`= '%s'"%(brand))
    if size.strip()!='':
        if statement!='':
            statement+=" and "
            statement+=("`masterdb`.`Size Description`= '%s'"%(size))
        else:
            statement+=("`masterdb`.`Size Description`= '%s'"%(size))
    if varietal.strip()!='':
        if statement!='':
            statement+=" and "
            statement+=("`masterdb`.`Varietal/ Flavor Description`= '%s'"%(varietal))
        else:
            statement+=("`masterdb`.`Varietal/ Flavor Description`= '%s'"%(varietal))
    print('statement ',statement)
    return statement


def location(x):
    locations={1000:'RIPON',5000:'LIVERMORE',3000:'WESTFIELD',5560:'CNP',5670:'VARNI',6032:'CUTLER',9033:'FREEFLOW'}
    return locations[x]

def week_of_month(dt):
    """ Returns the week of the month for the specified date.
    """

    first_day = dt.replace(day=1)

    dom = dt.day
    adjusted_dom = dom + first_day.weekday()

    return int(ceil(adjusted_dom/7.0))

def handle_command(message, channel, message_user,context):
    """
        NLP analysis on top of the conversation
    """
    current_action = '' # Intialize current action to empty
    slack_output = ''   # Intialize Slack output to empty
    
  # Send message to Assistant service.
    response = service.message(
    workspace_id = workspace_id,
    input = {'text': message},
    context = context).get_result()
       
    try:
        slack_output = ''.join(response['output']['text'])
    except:
        slack_output = ''
    
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
        period = str(response['context']['period'])    
    except:
        period = ''
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
    try:
        year3 = str(response['context']['year3'])    
    except:
        year3 = ''
    try:
        whse = str(response['context']['whse'])    
    except:
        whse = ''
    try:
        view = str(response['context']['view'])    
    except:
        view = ''
    try:
        timeperiod = str(response['context']['timeperiod'])    
    except:
        timeperiod = ''
    try:
        masterCodeValue = response['context']['masterCodeValue']
    except:
        masterCodeValue = ''
        
    try:
        outputtype = response['context']['outputtype']
    except:
        outputtype = ''
   #######################################code starts#######################################
    
    try:
        plant = response['context']['plant']
    except:
        plant = None
        
    try:
        chart_type = response['context']['chart_type']
    except:
        chart_type = None
        
    try:
        #print('try week')
        weekDayValue = response['context']['week_day_value']
    except:
        weekDayValue = None
       
    try:
        pastFutureValue = response['context']['past_future_value']
    except:
        pastFutureValue = None
    
    try:
        yearMonthValue = response['context']['year_month_value']
    except:
        yearMonthValue = None
        
    #specific_type
    
    try:
        brandType = response['context']['brand_type']
    except:
        brandType = None
        
    try:
        sizeType = response['context']['size_type']
    except:
        sizeType = None
    
    try:
        varietalType = response['context']['varietal_type']
    except:
        varietalType = None
    
    try:
        specificType = response['context']['specific_type']
    except:
        specificType = None
        
            
    print('plant ',plant)
    print('chart_type ',chart_type)
    print('weekDayValue ',weekDayValue)
    print('pastFutureValue ',pastFutureValue)
    print('year1 ',year1)
    print('year2 ',year2)
    print('year3 ',year3)
    print('outputtype:: ',outputtype)
    print('brandType ',brandType)
    print('sizeType ',sizeType)
    print('varietalType ',varietalType)
    #print('yearMonthValue ',yearMonthValue)
    
    
    if plant =="SC":
        plant_full = "Livermore"
    elif plant == "SR":
        plant_full ="Ripon"
    elif plant =="W":
        plant_full ="Westfield"
    else:
        plant_full = "all"
    print('plant_full ',plant_full)
    
    #
    
    ####################################### code ends#######################################
    
    
    print(brand)
    print(size)
    print(varietal)
    print(year)
    print(month)
    print(number)
    print(timeperiod)
    print(year1)
    print(year2)
    print(whse)
    print(view)
    res = ''
    
    ###############################################################
    ###########  data search  ###########
    ###############################################################
    try:
        print('try var')
        var=variation(brand,size,varietal)
    except:
        var=''
    
    print(var)
    
    
     #############################inventory for brand/size/varietal conbination detailed##################################
    
    try:
        if response['context']['currentIntent'] == 'inventory2' and var.strip()!='' and year.strip() == '' and outputtype.strip()=='detailed':

            curr= conn.cursor() 
            if month.strip()=='all':
                print("detailed report inventory all months")
                curr.execute("select `inventory`.`Group`,`Brand Description`,`Size Description`,`Varietal/ Flavor Description`,Date,sum(Balance) from inventory inner join masterdb on `inventory`.`Group`=`masterdb`.`Cat Cd10 Description` where %s and year(`inventory`.`Date`)=year(current_date()) group by `inventory`.`Group`;"%(var))
                print("sql done")
                quantity= curr.fetchall()
                if len(quantity)<1:
                    res="The requested record doesn't exist. Try again with vaild data"
                else:
                    df=pd.DataFrame(quantity)
                    df.columns=['Group','Brand','Size','Varietal','Date','Balance']
                    df.Date=df.Date.apply(lambda x: x.strftime("%m/%d/%Y"))
                    df.to_excel("sheet_output.xlsx",index=False)
                    file="sheet_output.xlsx"
                    file_upload(channel,file)

            elif month.strip()!='all':
                curr= conn.cursor()
                curr.execute("select `inventory`.`Group`,`Brand Description`,`Size Description`,`Varietal/ Flavor Description`,Date,sum(Balance) from inventory inner join masterdb on `inventory`.`Group`=`masterdb`.`Cat Cd10 Description` where %s and year(`inventory`.`Date`)=year(current_date()) and month(`inventory`.`Date`)= %d group by `inventory`.`Group`;"%(var,int(month)))
                print("sql done")
                quantity= curr.fetchall()
                if len(quantity)<1:
                    res="The requested record doesn't exist. Try again with vaild data"
                else:
                    df=pd.DataFrame(quantity)
                    df.columns=['Group','Brand','Size','Varietal','Date','Balance']
                    df.Date=df.Date.apply(lambda x: x.strftime("%m/%d/%Y"))
                    df.to_excel("sheet_output.xlsx",index=False)
                    file="sheet_output.xlsx"
                    file_upload(channel,file)
            response['context']['brand']=None
            response['context']['varietal']=None
            response['context']['month']=None
            response['context']['year']=None
            response['context']['size']=None
            response['context']['number']=None
            response['context']['currentIntent']=None
            response['context']['outputtype']=None
    except:
        pass
    

     #############################inventory for brand/size/varietal conbination summary##################################
    
    try:
        if response['context']['currentIntent'] == 'inventory' and var.strip()!='' :
            print("entered summary block inventory")
            #print(outputtype)
            if specificType != '':
                curr= conn.cursor() 
                print('Month:: ',month.strip())
                
                try:
                    specificType = response['context']['specificType']
                except:
                    specificType = ''
                
                print('specificType ',specificType)
                if month.strip()!='':
                    print("not entered")
                    #all months inventory
                    if month.strip()=='all':
                        curr.execute("select Date,sum(Balance) from inventory inner join masterdb on `inventory`.`Group`=`masterdb`.`Cat Cd10 Description` where %s and year(`inventory`.`Date`)=year(current_date()) group by Date order by Date;"%(var))
                        print("sql done")
                    elif month.strip()!='all':
                        curr.execute("select Date,sum(Balance) from inventory inner join masterdb on `inventory`.`Group`=`masterdb`.`Cat Cd10 Description` where %s and year(`inventory`.`Date`)=year(current_date()) and month(`inventory`.`Date`)= %d group by Date order by Date;"%(var,int(month)))
                        print("sql done")
                    quantity= curr.fetchall()
                    print("quantity::: ",quantity)
                    if len(quantity)<1:
                        res="The requested record doesn't exist. Try again with vaild data"
                    else:
                        print('else')
                        if month.strip()=='all':
                            print('all')
                            curr.execute("select Date,sum(Quantity) from forecast inner join masterdb on `forecast`.`master`=`masterdb`.`Cat Cd10 Description` where %s and year(`forecast`.`Date`)=year(current_date())  group by Date order by Date;"%(var))
                            print("sql done")
                        elif month.strip()!='all':
                            print('not all')
                            curr.execute("select Date,sum(Quantity) from forecast inner join masterdb on `forecast`.`master`=`masterdb`.`Cat Cd10 Description` where %s and year(`forecast`.`Date`)=year(current_date()) and month(`forecast`.`Date`)= %d group by Date order by Date;"%(var,int(month)))
                            print("sql done")
                        quantity2 = curr.fetchall()
                        print("quantity2::: ",quantity2)
                    
                        resu = [[ i for i, j in quantity ],[ j for i, j in quantity ]]
                        resu2 = [[ i for i, j in quantity2 ],[ j for i, j in quantity2 ]]
                        data=pd.DataFrame(resu)
                        data=data.transpose()
                        data.columns=['date','quantity']
                        data=data.sort_values(by='date')
                        data.quantity=data.quantity.astype(int)
                        data.date=data.date.apply(lambda x: x.strftime("%b %y"))
                        print('data:: ',data)
                        #ind = np.arange(len(data.quantity))
                        #data2
                        data2=pd.DataFrame(resu2)
                        data2=data2.transpose()
                        data2.columns=['date','quantity']
                        data2=data2.sort_values(by='date')
                        data2.quantity=data2.quantity.astype(int)
                        data2.date=data2.date.apply(lambda x: x.strftime("%b %y"))
                        print('data2:: ',data2)
                        
                        
                        data3 = pd.DataFrame(columns=['date','quantity'])
                        #data3.columns=['date','quantity']
                        data3['date'] = data2['date']
                        print('data3:: ',data3)
                        print('yo')
                        print((data['quantity'] / data2['quantity']) *30)
                        data3['quantity'] = data['quantity'] / data2['quantity']
                        if specificType == 'inventorydoh':
                            data3['quantity'] = data3['quantity'] * 30
                        data3['quantity'] = data3['quantity'].round(3)
                        data3=data3.fillna(0)
                        print('values:: ',data3)
                        
                        #data=data3
                        columns = []
                        rows=[]
                        #for i in range(len(data)):
                        #    columns.append(data[i][1])
                        #   rows.append(data[i][3])

                        n_rows = len(data3)
                        print('n_rows:: ',n_rows)

                        # Add a table at the bottom of the axes
                        #colLabels=("Date", "Balance")
                        #nrows, ncols = len(data3)+1, len(colLabels)
                        #hcell, wcell = 0.5, 1
                        
                        #print('nrows ',nrows,'ncols ',ncols)

                        #do the table
                        #the_table = plt.table(cellText=data3,
                        #       loc='center',cellLoc = 'left')
                        #print('the_table:: ',the_table)
                        
                        print('cellcolumn :: ',data3.quantity.values)
                        print('cellrow :: ',data3.date.values)
                        #, rowLoc='right', rowLabels=['shipment'],
                                        # colLabels=data3.date.values,
                                        # colLoc='center', loc='bottom'
                        #the_table = plt.table(cellText=data3.quantity.values)
                        
                        colLabels=("Date", "Balance")
                        nrows, ncols = len(data3)+1, len(colLabels)
                        hcell, wcell = 0.5, 1
                        
                        print('data3.values:: ',data3.values)

                        #do the table
                        the_table = plt.table(cellText=data3.values,
                              colLabels=colLabels,
                              loc='center',cellLoc = 'center')
                        
                        #the_table = plt.table(cellText=data,
                        #  colLabels=colLabels,
                        #  loc='center',cellLoc = 'left')
                        #print(the_table.properties())
                        #cellDict=the_table.get_celld()
                        
                        
                        #print(the_table.properties())
                        #cellDict=the_table.get_celld()
                        #for i in range(len(data3)+1):
                         #   cellDict[(i,0)].set_width(0.2)
                         #   cellDict[(i,1)].set_width(0.3)
                        
                        print('wohooo')
                        plt.axis('off')
                        plt.savefig("inventoryOutput.jpg", dpi=300, bbox_inches = 'tight',pad_inches = 0)
                        #plt.tight_layout()


                        # Add a table at the bottom of the axes
                        #plt.show()
                        #res="Total number of cases short for plant {} are:{} ".format(plant_full,count)
                        #print('res',res)
                        img = 'inventoryOutput.jpg'
                        file_upload(channel, img)
                        plt.close()
                        #ind = np.arange(len(data2.quantity))
                    #if len(cumsum)<1:
                     #   res="The requested record doesn't exist. Try again with vaild data"
                    #else:
                   #     res = ("The cummulative inventory for %s %s %s for %s is %s"%(brand,varietal,size,calendar.month_name[int(month)],f'{int(cumsum[0][0]):,}'))
                plt.close()
                response['context']['brand']=None
                response['context']['varietal']=None
                response['context']['month']=None
                response['context']['year']=None
                response['context']['size']=None
                response['context']['number']=None
                response['context']['currentIntent']=None
                response['context']['specificType']=None
    except:
        pass

         
############################################### recommend production for brand size varietal #############################################
    try:
        if response['context']['currentIntent'] == 'recommend_production' and brand.strip() != '' and size.strip() != '' and varietal.strip() != '' and number.strip()!='':
            print('entered recommend production bsv')
            target=int(number)
            curr=conn.cursor()
            print('brand ',brand)
            print('varietal ',varietal)
            print('size ',size)
            curr.execute("select `Group` from masterdb where `Brand Description`='%s' and `Varietal/ Flavor Description`='%s' and `Size Description`='%s' limit 1;"%(brand,varietal,size))
            mastercode=curr.fetchall()
            print('mastercode ',mastercode)
            curr.execute("select Date,sum(Balance) from inventory where `Group`='%s' and month(Date)>=month(current_date()) and year(Date)=year(current_date()) group by `Group`,Date;"%(mastercode[0][0]))
            inventory= curr.fetchall()
            print('inventory ',inventory)
            curr.execute("select Date1,sum(Schedule2) from production where `Group`='%s' and month(Date1)>=month(current_date()) and year(Date1)>=year(current_date()) group by `Group`,Date1;"%(mastercode[0][0]))
            production= curr.fetchall()
            print('production ',production)
            curr.execute("select Date,sum(Quantity) from customerorders where `Group`='%s' and Date<current_date() group by `Group`,Date;"%(mastercode[0][0]))
            shipments=curr.fetchall()
            print('shipments ',shipments)
            curr.execute("select Date,sum(Quantity) from customerorders where `Group`='%s' and month(Date)=month(current_date()) and year(Date)=year(current_date()) and Date<current_date() group by `Group`,Date;"%(mastercode[0][0]))
            currorders=curr.fetchall()
            print('currorders ',currorders)
            print("queries sucessful")
            
            if len(shipments)<1 or len(inventory)<1 or len(production)<1:
                res="Could not generate recommendations. Insufficient data."
            else:
                ship = [[ i.strftime("%Y-%m-%d") for i, j in shipments],[ j for i, j in shipments] ]
                shp_data=pd.DataFrame(ship)
                shp_data=shp_data.transpose()
                shp_data.columns=['ds','y']
                #prophet model
                prophet=fbprophet.Prophet()
                prophet.fit(shp_data)
                future = prophet.make_future_dataframe(periods=120) 
                forecast = prophet.predict(future)
                #forecast from today
                forecastdf=forecast[['ds','yhat']]
                forecastdf.columns=['ds','shipments']
                forecastdf['ds']=pd.to_datetime(forecastdf.ds)
                forecastdf=forecastdf.loc[(forecastdf.ds.dt.date>=datetime.date.today())]
                forecastdf['ds']=forecastdf['ds'].apply(lambda x:x.strftime('%Y-%m-%d'))
                forecastdf['shipments']=forecastdf['shipments'].apply(lambda x: 0 if int(x)<0 else x)
                print("forecast done")
                #firm orders for current month til date
                order = [[ i.strftime("%Y-%m-%d") for i, j in currorders],[ j for i, j in currorders] ]
                ord_data=pd.DataFrame(order)
                ord_data=ord_data.transpose()
                ord_data.columns=['ds','shipments']
                ord_data['ds']=pd.to_datetime(ord_data.ds)
                ord_data=ord_data.append(forecastdf)
                print("orders done")
                #monthly forecast df
                forecast_monthly=ord_data.copy()
                forecast_monthly['ds']=pd.to_datetime(forecast_monthly.ds)
                forecast_monthly['ds']=forecast_monthly['ds'].apply(lambda x: x.strftime("%y %m"))
                forecast_monthly['shipments']=forecast_monthly.shipments.astype(int)
                forecast_monthly=forecast_monthly.groupby(['ds'])[['shipments']].sum()
                print("summation done")
                #inventory df
                inv = [[ i.strftime("%Y-%m-%d") for i, j in inventory],[ j for i, j in inventory] ]
                inv_data=pd.DataFrame(inv)
                inv_data=inv_data.transpose()
                inv_data.columns=['ds','inventory']
                inv_data['inventory']=inv_data.inventory.astype(int)
                inv_monthly=inv_data.copy()
                inv_monthly['ds'] =pd.to_datetime(inv_monthly.ds)
                inv_monthly['ds']=inv_monthly['ds'].apply(lambda x: x.strftime("%y %m"))
                inv_monthly=inv_monthly.groupby(['ds'])[['inventory']].sum()
                print("inventory done")
                #production df
                pro = [[ i.strftime("%Y-%m-%d") for i, j in production],[ j for i, j in production] ]
                pro_data=pd.DataFrame(pro)
                pro_data=pro_data.transpose()
                pro_data.columns=['ds','Production']
                pro_data['Production']=pro_data.Production.astype(int)
                pro_monthly=pro_data.copy()
                pro_monthly['ds'] =pd.to_datetime(pro_monthly.ds)
                pro_monthly['ds']=pro_monthly['ds'].apply(lambda x: x.strftime("%y %m"))
                pro_monthly=pro_monthly.groupby(['ds'])[['Production']].sum()
                print("prduction done")
                #merging all dfs
                newdf=pd.merge(pro_monthly, inv_monthly, on='ds', how='outer')
                newdf=pd.merge(newdf,forecast_monthly,on='ds', how='outer')
                newdf=newdf.fillna(0)
                newdf=newdf.sort_values('ds')
                newdf['Recommended Production']=newdf['Production']
                print("newdf done")
                for i in range(1,len(newdf)):
                    newdf['inventory'][i]=newdf['inventory'][i-1]+newdf['Production'][i-1]-newdf['shipments'][i-1]
                for i in range(len(newdf)-1):
                    newdf['Recommended Production'][i]= target*newdf['shipments'][i+1] + newdf['shipments'][i]-newdf['inventory'][i]
                print("formulas done")
                newdf=newdf[['Production','Recommended Production']].head(3)
                newdf.index=pd.to_datetime(newdf.index,format='%y %m')
                newdf.index=newdf.index.map(lambda x : x.strftime("%b %y"))
                row_colors=['#f1f1f2', 'w']
                header_columns=0
                bbox=[0, 0, 1, 1]
                font_size=14
                header_color='#3CAEA3'
                edge_color='w'
                plt.axis('off')
                mpl_table = plt.table(cellText=newdf.values,bbox=bbox,colLabels=newdf.columns,rowLabels=newdf.index,loc='center',cellLoc='center')
                mpl_table.auto_set_font_size(False)
                mpl_table.set_fontsize(font_size)
                for k, cell in six.iteritems(mpl_table._cells):
                    cell.set_edgecolor(edge_color)
                    if k[0] == 0 or k[1] < header_columns:
                        cell.set_text_props(weight='bold', color='w',)
                        cell.set_facecolor(header_color)
                    else:
                        cell.set_facecolor(row_colors[k[0]%len(row_colors) ])
                plt.tight_layout()

                plt.title("%s %s %s PRODUCTION RECOMMENDATIONS"%(brand,varietal,size))
                plt.savefig("table.jpg",bbox_inches='tight', pad_inches = 0.5)
                img="table.jpg"
                file_upload(channel,img)
                plt.close()
            
            response['context']['brand']=None
            response['context']['varietal']=None
            response['context']['month']=None
            response['context']['year']=None
            response['context']['size']=None
            response['context']['number']=None
            response['context']['whse']=None
            response['context']['period']=None
            response['context']['view']=None
            response['context']['timeperiod']=None
            response['context']['currentIntent']=None
    except:
        pass
 


 ############################################### recommend production for mastercode ############################################
    try:
        if response['context']['currentIntent'] == 'recommend_production' and masterCodeValue.strip() != '' and number.strip()!='':
            print('entered recommend production mastercode')
            target=int(number)
            curr=conn.cursor()
            curr.execute("select `Group` from masterdb where `Group`= '%s' limit 1;"%(masterCodeValue))
            mastercode=curr.fetchall()
            if len(mastercode)<1:
                res= "Please try again with a valid Mastercode."
            else:
                curr.execute("select Date,sum(Balance) from inventory where `Group`='%s' and year(Date)>=year(current_date()) and  month(Date)>=month(current_date()) group by `Group`,Date;"%(mastercode[0][0]))
                inventory= curr.fetchall()
                curr.execute("select Date1,sum(Schedule2) from production where `Group`='%s' and month(Date1)>=month(current_date()) and year(Date1)>=year(current_date()) group by `Group`,Date1;"%(mastercode[0][0]))
                production= curr.fetchall()
                curr.execute("select Date,sum(Quantity) from customerorders where `Group`='%s' and Date<current_date() group by `Group`,Date;"%(mastercode[0][0]))
                shipments=curr.fetchall()
                curr.execute("select Date,sum(Quantity) from customerorders where `Group`='%s' and month(Date)=month(current_date()) and year(Date)=year(current_date()) and Date<current_date() group by `Group`,Date;"%(mastercode[0][0]))
                currorders=curr.fetchall()
                print("queries sucessful")
                if len(shipments)<1 or len(inventory)<1 or len(production)<1:
                    res="Could not generate recommendations. Insufficient data."
                else:
                    ship = [[ i.strftime("%Y-%m-%d") for i, j in shipments],[ j for i, j in shipments] ]
                    shp_data=pd.DataFrame(ship)
                    shp_data=shp_data.transpose()
                    shp_data.columns=['ds','y']
                    #prophet model
                    prophet=fbprophet.Prophet()
                    prophet.fit(shp_data)
                    future = prophet.make_future_dataframe(periods=120) 
                    forecast = prophet.predict(future)
                    #forecast from today
                    forecastdf=forecast[['ds','yhat']]
                    forecastdf.columns=['ds','shipments']
                    forecastdf['ds']=pd.to_datetime(forecastdf.ds)
                    forecastdf=forecastdf.loc[(forecastdf.ds.dt.date>=datetime.date.today())]
                    forecastdf['ds']=forecastdf['ds'].apply(lambda x:x.strftime('%Y-%m-%d'))
                    forecastdf['shipments']=forecastdf['shipments'].apply(lambda x: 0 if int(x)<0 else x)
                    #firm orders for current month til date
                    order = [[ i.strftime("%Y-%m-%d") for i, j in currorders],[ j for i, j in currorders] ]
                    ord_data=pd.DataFrame(order)
                    ord_data=ord_data.transpose()
                    ord_data.columns=['ds','shipments']
                    ord_data['ds']=pd.to_datetime(ord_data.ds)
                    ord_data=ord_data.append(forecastdf)
                    #monthly forecast df
                    forecast_monthly=ord_data.copy()
                    forecast_monthly['ds']=pd.to_datetime(forecast_monthly.ds)
                    forecast_monthly['ds']=forecast_monthly['ds'].apply(lambda x: x.strftime("%y %m"))
                    forecast_monthly['shipments']=forecast_monthly.shipments.astype(int)
                    forecast_monthly=forecast_monthly.groupby(['ds'])[['shipments']].sum()
                    #inventory df
                    inv = [[ i.strftime("%Y-%m-%d") for i, j in inventory],[ j for i, j in inventory] ]
                    inv_data=pd.DataFrame(inv)
                    inv_data=inv_data.transpose()
                    inv_data.columns=['ds','inventory']
                    inv_data['inventory']=inv_data.inventory.astype(int)
                    inv_monthly=inv_data.copy()
                    inv_monthly['ds'] =pd.to_datetime(inv_monthly.ds)
                    inv_monthly['ds']=inv_monthly['ds'].apply(lambda x: x.strftime("%y %m"))
                    inv_monthly=inv_monthly.groupby(['ds'])[['inventory']].sum()
                    #production df
                    pro = [[ i.strftime("%Y-%m-%d") for i, j in production],[ j for i, j in production] ]
                    pro_data=pd.DataFrame(pro)
                    pro_data=pro_data.transpose()
                    pro_data.columns=['ds','Production']
                    pro_data['Production']=pro_data.Production.astype(int)
                    pro_monthly=pro_data.copy()
                    pro_monthly['ds'] =pd.to_datetime(pro_monthly.ds)
                    pro_monthly['ds']=pro_monthly['ds'].apply(lambda x: x.strftime("%y %m"))
                    pro_monthly=pro_monthly.groupby(['ds'])[['Production']].sum()
                    #merging all dfs
                    newdf=pd.merge(pro_monthly, inv_monthly, on='ds', how='outer')
                    newdf=pd.merge(newdf,forecast_monthly,on='ds', how='outer')
                    newdf=newdf.fillna(0)
                    newdf=newdf.sort_values('ds')
                    newdf['Recommended Production']=newdf['Production']
                    for i in range(1,len(newdf)):
                        newdf['inventory'][i]=newdf['inventory'][i-1]+newdf['Production'][i-1]-newdf['shipments'][i-1]
                    for i in range(len(newdf)-1):
                        newdf['Recommended Production'][i]= target*newdf['shipments'][i+1] + newdf['shipments'][i]-newdf['inventory'][i]
                    newdf=newdf[['Production','Recommended Production']].head(3)
                    newdf.index=pd.to_datetime(newdf.index,format='%y %m')
                    newdf.index=newdf.index.map(lambda x : x.strftime("%b %y"))
                    curr=conn.cursor()
                    curr.execute("select `Brand Description`,`Size Description`,`Varietal/ Flavor Description` from masterdb where `Group`= '%s' limit 1;"%(masterCodeValue))
                    specs=curr.fetchall()
                    row_colors=['#f1f1f2', 'w']
                    header_columns=0
                    bbox=[0, 0, 1, 1]
                    font_size=14
                    header_color='#3CAEA3'
                    edge_color='w'
                    plt.axis('off')
                    mpl_table = plt.table(cellText=newdf.values,bbox=bbox,colLabels=newdf.columns,rowLabels=newdf.index,loc='center',cellLoc='center')
                    mpl_table.auto_set_font_size(False)
                    mpl_table.set_fontsize(font_size)
                    for k, cell in six.iteritems(mpl_table._cells):
                        cell.set_edgecolor(edge_color)
                        if k[0] == 0 or k[1] < header_columns:
                            cell.set_text_props(weight='bold', color='w',)
                            cell.set_facecolor(header_color)
                        else:
                            cell.set_facecolor(row_colors[k[0]%len(row_colors) ])
                    plt.tight_layout()

                    plt.title("%s %s %s PRODUCTION RECOMMENDATIONS"%(specs[0][0],specs[0][2],specs[0][1]))
                    plt.savefig("table.jpg",bbox_inches='tight', pad_inches = 0.5)
                    img="table.jpg"
                    file_upload(channel,img)
                    plt.close()
            
            response['context']['brand']=None
            response['context']['varietal']=None
            response['context']['month']=None
            response['context']['year']=None
            response['context']['size']=None
            response['context']['number']=None
            response['context']['whse']=None
            response['context']['period']=None
            response['context']['view']=None
            response['context']['timeperiod']=None
            response['context']['masterCodeValue']=None
            response['context']['currentIntent']=None
    except:
        pass
    
    
    
         #################################################Code starts for OOS-Out oF Stock Data -Plant###################################
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
                print('val_exists ',val_exists)
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
                print('heyy')
                print(is_not_empty(row_vals))
            
                if(is_not_empty(row_vals)):
                    print('is_not_empty ')
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
   
    ##################Code starts for Customer Orders and x months/weeks/days production for brand/size/varietal####################
    try:
        if response['context']['currentIntent'] == 'customerOrders':
            print('customerorders')
            try:
                limit = response['context']['sys_number']
            except:
                limit =1
                
            try:
                masterCodeValue = response['context']['masterCodeValue']
            except:
                masterCodeValue = None
            
            print('mastercode:: ',masterCodeValue)
            print('month:: ',month)
            print('limit:: ',limit)
            print('outputtype:: ',outputtype)
            
            curr= conn.cursor()
             
            if(weekDayValue == None):
                res = "Invalid phrase"
            elif(weekDayValue !=None):
                print("inside else")
                
                if(weekDayValue =='week'):
                    part_query = " SELECT FORMAT(SUM(qty),0)  from  ("
                    #,WEEK(date(`Date`),4) AS WEEK
                    if outputtype =='detailed':
                        
                        if specificType == 'production':
                            sql_query = "  select `production`.`Group` as grp "
                        else:
                            sql_query = "  select `customerorders`.`Group` as grp "
                        
                        if specificType == 'production':
                            sql_query = sql_query +" , `masterdb`.`Brand Description` , `masterdb`.`Size Description`, \
                            `masterdb`.`Varietal/ Flavor Description` , date(`Date1`) as dt,sum(`Schedule2`) as qty from `production` \
                        inner join `masterdb` on `production`.`Group`=`masterdb`.`Cat Cd10 Description` where  "
                        else:
                            sql_query = sql_query +" , `masterdb`.`Brand Description` , `masterdb`.`Size Description`, \
                        `masterdb`.`Varietal/ Flavor Description` , date(`Date`) as dt,sum(`Quantity`) as qty from `customerorders` \
                        inner join `masterdb` on `customerorders`.`Group`=`masterdb`.`Cat Cd10 Description` where  "
                         
                    else:
                        if specificType == 'production':
                            sql_query=" select date(`Date1`) as dt,sum(`Schedule2`) as qty \
                        from `production` inner join `masterdb` on `production`.`Group`=`masterdb`.`Cat Cd10 Description` where  "
                        else:
                            sql_query=" select date(`Date`) as dt,sum(`Quantity`) as qty \
                        from `customerorders` inner join `masterdb` on `customerorders`.`Group`=`masterdb`.`Cat Cd10 Description` where  "
                        
                    #past few weeks
                    if(pastFutureValue =='last'):
                        if specificType == 'production':
                            sql_query = sql_query + "  date(`Date1`)  >=DATE_SUB(DATE_ADD(CURDATE(), INTERVAL - WEEKDAY(CURDATE()) DAY) \
                        ,INTERVAL {} WEEK) and date(`Date1`)<DATE_SUB(DATE_ADD(CURDATE(), INTERVAL - WEEKDAY(CURDATE()) DAY),INTERVAL 1 DAY) "
                        else:
                            sql_query = sql_query + "  date(`Date`)  >=DATE_SUB(DATE_ADD(CURDATE(), INTERVAL - WEEKDAY(CURDATE()) DAY) \
                        ,INTERVAL {} WEEK) and date(`Date`)<DATE_SUB(DATE_ADD(CURDATE(), INTERVAL - WEEKDAY(CURDATE()) DAY),INTERVAL 1 DAY) "
                        
                    #next few weeks
                    elif(pastFutureValue =='next'):
                        if specificType == 'production':
                            sql_query = sql_query + " week(date(`Date1`),4) >= \
                            week(DATE_ADD(CURDATE(), INTERVAL - WEEKDAY(CURDATE()) DAY)) \
                            and date(`Date1`)<=DATE_ADD(DATE_ADD(CURDATE(), INTERVAL - WEEKDAY(CURDATE()) DAY),INTERVAL {} WEEK) \
                            and  date(`Date1`)>=DATE_ADD(CURDATE(), INTERVAL - WEEKDAY(CURDATE()) DAY)  "
                        else:
                            sql_query = sql_query + " week(date(`Date`),4)>=week(DATE_ADD(CURDATE(), INTERVAL - WEEKDAY(CURDATE()) DAY)) \
                        and date(`Date`)<=DATE_ADD(DATE_ADD(CURDATE(), INTERVAL - WEEKDAY(CURDATE()) DAY),INTERVAL {} WEEK) \
                        and  date(`Date`)>=DATE_ADD(CURDATE(), INTERVAL - WEEKDAY(CURDATE()) DAY)  "
                        
                    if(masterCodeValue!=None):
                        if specificType == 'production':
                            sql_query = sql_query +" and  `production`.Group = '{}'  "
                        else:
                            sql_query = sql_query +" and  `customerorders`.Group = '{}'  "
                    
                    elif(brand.strip() != '' or size.strip() != '' or varietal.strip() != ''):
                        if(brand.strip() != ''):
                            sql_query = sql_query +" and `masterdb`.`Brand Description`= '{}'  "
                        if(size.strip() != ''):
                            sql_query = sql_query +" and `masterdb`.`Size Description`= '{}'  "
                        if(varietal.strip() != ''):
                            sql_query = sql_query +" and `masterdb`.`Varietal/ Flavor Description`= '{}'  "
                    else:
                        sql_query = sql_query +" "
                    
                    if outputtype =='detailed':
                        if specificType == 'production':
                            sql_query = sql_query + " GROUP BY `production`.`Group`, WEEK(date(`Date1`),4) \
                            order by `production`.`Group`, date(`Date1`) "
                        else:
                             sql_query = sql_query + " GROUP BY `customerorders`.`Group`, WEEK(date(`Date`),4) \
                        order by `customerorders`.`Group`, date(`Date`) "
                    else:
                        if specificType == 'production':
                            sql_query = sql_query + " GROUP BY WEEK(date(`Date1`),4) order by date(`Date1`) "
                        else:
                            sql_query = sql_query + " GROUP BY WEEK(date(`Date`),4) order by date(`Date`) "
                    
                    if(pastFutureValue =='last'):
                        sql_query = sql_query + " DESC  "
                    
                    sql_query_final = part_query + sql_query +  " )asa "
                    print(sql_query_final)
                    
                elif(weekDayValue =='day'):
                    #yo
                    part_query = " SELECT FORMAT(SUM(qty),0)  from  ("
                    
                    if outputtype =='detailed':
                        if specificType == 'production':
                            sql_query="  select `production`.`Group` as grp "
                        else:
                            sql_query="  select `customerorders`.`Group` as grp "
                        
                        if specificType == 'production':
                            sql_query = sql_query +" , `masterdb`.`Brand Description` , `masterdb`.`Size Description`, \
                        `masterdb`.`Varietal/ Flavor Description` , date(`Date1`) as dt,sum(`Schedule2`) as qty  from `production` \
                        inner join `masterdb` on `production`.`Group`=`masterdb`.`Cat Cd10 Description` where  "
                        else:
                            sql_query = sql_query +" , `masterdb`.`Brand Description` , `masterdb`.`Size Description`, \
                        `masterdb`.`Varietal/ Flavor Description` , date(`Date`) as dt,sum(`Quantity`) as qty  from `customerorders` \
                        inner join `masterdb` on `customerorders`.`Group`=`masterdb`.`Cat Cd10 Description` where  "
                        
                    else:
                        if specificType == 'production':
                            sql_query = " select date(`Date1`) as dt, sum(`Schedule2`)  as qty from `production` \
                    inner join `masterdb` on `production`.`Group`=`masterdb`.`Cat Cd10 Description` where "
                        else:
                            sql_query = " select date(`Date`) as dt, sum(`Quantity`)  as qty from `customerorders` \
                    inner join `masterdb` on `customerorders`.`Group`=`masterdb`.`Cat Cd10 Description` where "
                            
                    #past few days
                    if(pastFutureValue =='last'):
                        if specificType == 'production':
                            sql_query = sql_query + " date(`Date1`)>=DATE_SUB(CURDATE(),INTERVAL {} DAY) and date(`Date1`)<=CURDATE()  "
                        else:
                            sql_query = sql_query + " date(`Date`)>=DATE_SUB(CURDATE(),INTERVAL {} DAY) and date(`Date`)<=CURDATE()  "
                            
                    #next few days
                    elif(pastFutureValue =='next'):
                        if specificType == 'production':
                            sql_query = sql_query + " date(`Date1`)>=CURDATE() and date(`Date1`)<DATE_ADD(CURDATE(),INTERVAL {} DAY)  "
                        else:
                            sql_query = sql_query + " date(`Date`)>=CURDATE() and date(`Date`)<DATE_ADD(CURDATE(),INTERVAL {} DAY)  "
                    
                    if(masterCodeValue!=None):
                        if specificType == 'production':
                            sql_query = sql_query +" and  `production`.Group = '{}'  "
                        else:
                            sql_query = sql_query +" and  `customerorders`.Group = '{}'  "
                        
                    elif(brand.strip() != '' or size.strip() != '' or varietal.strip() != ''):
                        if(brand.strip() != ''):
                            sql_query = sql_query +" and `masterdb`.`Brand Description`= '{}'  "
                        if(size.strip() != ''):
                            sql_query = sql_query +" and `masterdb`.`Size Description`= '{}'  "
                        if(varietal.strip() != ''):
                            sql_query = sql_query +" and `masterdb`.`Varietal/ Flavor Description`= '{}'  "
                    else:
                        sql_query = sql_query +" "
                    
                    if outputtype =='detailed':
                        if specificType == 'production':
                            sql_query = sql_query + " GROUP BY `production`.`Group`, date(`Date1`) \
                        order by `production`.`Group`, date(`Date1`) "
                        else:
                            sql_query = sql_query + " GROUP BY `customerorders`.`Group`, date(`Date`) \
                        order by `customerorders`.`Group`, date(`Date`) "
                    else:
                        if specificType == 'production':
                            sql_query = sql_query + " group by date(`Date1`) order by  date(`Date1`) "
                        else:
                            sql_query = sql_query + " group by date(`Date`) order by  date(`Date`) "
                    
                    if(pastFutureValue =='last'):
                        sql_query = sql_query + "DESC  "
                     
                    sql_query_final = part_query + sql_query +  " )asa "
                    print(sql_query_final)
                
                elif(weekDayValue =='month'):
                    
                    part_query = " SELECT FORMAT(SUM(qty),0)  from  ( "
                   
                    if outputtype =='detailed':
                        if specificType == 'orders' or pastFutureValue =='current' :
                            sql_query=" select `customerorders`.`Group` as grp "
                        elif specificType == 'production':
                            sql_query=" select `production`.`Group` as grp "
                        else:
                            sql_query=" select `forecast`.`master` as grp "
                            
                        if specificType == 'production':
                            sql_query = sql_query +" , `masterdb`.`Brand Description` , `masterdb`.`Size Description`, \
                            `masterdb`.`Varietal/ Flavor Description` , \
                            CONCAT(MONTHNAME (date(`Date1`)), ',', year (date(`Date1`)) ),sum(`Schedule2`) as qty "
                        else:
                            sql_query = sql_query +" , `masterdb`.`Brand Description` , `masterdb`.`Size Description`, \
                            `masterdb`.`Varietal/ Flavor Description` , \
                            CONCAT(MONTHNAME (date(`Date`)), ',', year (date(`Date`)) ),sum(`Quantity`) as qty "
                        
                        if specificType == 'orders' or pastFutureValue =='current' :
                            sql_query = sql_query +  " from `customerorders` \
                            inner join `masterdb` on `customerorders`.`Group` = `masterdb`.`Cat Cd10 Description` where  "
                        elif specificType == 'production':
                            sql_query= sql_query +  " from `production` \
                            inner join `masterdb` on `production`.`Group` = `masterdb`.`Cat Cd10 Description` where  "
                        else:
                            sql_query= sql_query + " from `forecast` \
                            inner join `masterdb` on `forecast`.`master` = `masterdb`.`Cat Cd10 Description` where  "
                            
                        #sql_query= sql_query + "from `customerorders` \
                        #inner join `masterdb` on `customerorders`.`Group`=`masterdb`.`Cat Cd10 Description` where  "
                    else:
                        if specificType == 'orders' or pastFutureValue =='current' :
                            sql_query = " select CONCAT(MONTHNAME (date(`Date`)), ',', year (date(`Date`)) ), \
                            sum(`Quantity`)  as qty from `customerorders` \
                            inner join `masterdb` on `customerorders`.`Group`=`masterdb`.`Cat Cd10 Description` where "
                        elif specificType == 'production':
                            sql_query=  " select CONCAT(MONTHNAME (date(`Date1`)), ',', year (date(`Date1`)) ), \
                            sum(`Schedule2`)  as qty from `production` \
                            inner join `masterdb` on `production`.`Group`=`masterdb`.`Cat Cd10 Description` where "
                        else:
                            sql_query = " select CONCAT(MONTHNAME (date(`Date`)), ',', year (date(`Date`)) ), \
                            sum(`Quantity`)  as qty from `forecast` \
                            inner join `masterdb` on `forecast`.`master`=`masterdb`.`Cat Cd10 Description` where "
                        
                    #sql_query = " SELECT "
                    #if outputtype =='detailed':
                    #    sql_query = sql_query + " `customerorders`.`Group`, "
                    #sql_query = sql_query + " MONTHNAME (date(`Date`)) as Month, SUM(`Quantity`) AS qty "
                    
                    #sql_query = sql_query + "FROM `customerorders` \
                    #inner join `masterdb` on `customerorders`.`Group`=`masterdb`.`Cat Cd10 Description` WHERE "
                    
                    #past few months
                    if(pastFutureValue =='last'):
                        if specificType == 'production':
                            sql_query = sql_query + " Date1 >= \
                        DATE_SUB( DATE_SUB(LAST_DAY(CURDATE()),INTERVAL DAY(LAST_DAY(CURDATE()))-1 DAY), INTERVAL {} MONTH ) \
                        AND Date1 <=  DATE_SUB(CURDATE(), INTERVAL 1 DAY) "
                        else:
                            sql_query = sql_query + " Date >= \
                        DATE_SUB( DATE_SUB(LAST_DAY(CURDATE()),INTERVAL DAY(LAST_DAY(CURDATE()))-1 DAY), INTERVAL {} MONTH ) \
                        AND Date <=  DATE_SUB(CURDATE(), INTERVAL 1 DAY)   "
                        
                    #next few months
                    elif(pastFutureValue =='next'):
                        if specificType == 'production':
                            sql_query = sql_query + " Date1 >= CURDATE() AND Date1 <= LAST_DAY(CURDATE()+ INTERVAL {} MONTH)  "
                        else:
                            sql_query = sql_query + " Date >= CURDATE() AND Date <= LAST_DAY(CURDATE()+ INTERVAL {} MONTH)  "
                        
                    #current month
                    elif(pastFutureValue =='current'):
                        if specificType == 'production':
                            sql_query = sql_query + " Date1 BETWEEN DATE_FORMAT(CURDATE() ,'%Y-%m-01') AND LAST_DAY(CURDATE())  "
                        else:
                            sql_query = sql_query + " Date BETWEEN DATE_FORMAT(CURDATE() ,'%Y-%m-01') AND LAST_DAY(CURDATE())  "
                    
                    
                    #added starts
                    if(masterCodeValue!=None):
                        if specificType == 'orders' or pastFutureValue =='current' :
                            sql_query = sql_query +" and  `customerorders`.Group` = '{}'  "
                        elif specificType == 'production':
                            sql_query = sql_query +" and  `production`.Group` = '{}'  "
                        else:
                            sql_query = sql_query +" and  `forecast`.`master`= '{}'  "
                        
                    
                    elif(brand.strip() != '' or size.strip() != '' or varietal.strip() != ''):
                        if(brand.strip() != ''):
                            sql_query = sql_query +" and `masterdb`.`Brand Description`= '{}'  "
                        if(size.strip() != ''):
                            sql_query = sql_query +" and `masterdb`.`Size Description`= '{}'  "
                        if(varietal.strip() != ''):
                            sql_query = sql_query +" and `masterdb`.`Varietal/ Flavor Description`= '{}'  "
                    else:
                        sql_query = sql_query +" "
                    #added ends
                    
                    if outputtype =='detailed':
                        if specificType == 'orders' or pastFutureValue =='current' :
                            sql_query = sql_query + " GROUP BY `customerorders`.`Group`, month( date(`Date`)) \
                        order by `customerorders`.`Group`, date(`Date`) "
                        elif specificType == 'production':
                            sql_query = sql_query + " GROUP BY `production`.`Group`, month( date(`Date1`)) \
                        order by `production`.`Group`, date(`Date1`) "
                        else:
                            sql_query = sql_query + " GROUP BY `forecast`.`master`, month( date(`Date`)) \
                        order by `forecast`.`master`, date(`Date`) "
                        
                    else:
                        if specificType == 'production':
                            sql_query = sql_query + " GROUP BY month( date(`Date1`)) order by  date(`Date1`) "
                        else:
                            sql_query = sql_query + " GROUP BY month( date(`Date`)) order by  date(`Date`) "
                    
                    if(pastFutureValue =='last'):
                        sql_query = sql_query + "DESC "
                    
                    sql_query_final = part_query + sql_query +  " )asa " 
                    print(' ****************before execute_sql_queries**************************** ')
                    print(sql_query_final)
                uniquevar = "count"
                ######################################here st
                count =execute_sql_queries(curr,sql_query_final,weekDayValue,pastFutureValue,limit,masterCodeValue,brand,size,
                                              varietal,uniquevar,'month','value')
                ########################## here ends                             
                #count
                #count = curr.fetchone()
                #for k in count:
                    #count = k
                    #break
                print('count inside customerorders:: ',count)
                
                #By Week
                if(weekDayValue =='week'):
                    print(weekDayValue)
                    
                    col1_value="Week"
                    print(col1_value)
                #By Day
                elif(weekDayValue=='day'):
                    col1_value="Day"
                    print(col1_value)
                
                # elif(weekDayValue =='month'): 
                elif(weekDayValue=='month'):
                    col1_value="Month"
                print(sql_query)    
                sql_query_final = sql_query 
                print(' ****************before--2-- execute_sql_queries**************************** ')
                print(sql_query_final)
                uniquevar = "list"
                ######################################here st
                row_vals =execute_sql_queries(curr,sql_query_final,weekDayValue,pastFutureValue,limit,masterCodeValue,brand,size,
                                              varietal,uniquevar,'month','value')
                ########################## here ends       
                
                #print('row_vals 0::: ',row_vals[0])
                #print('row_vals 1::: ',row_vals[1])
                #data2 = pd.DataFrame(row_vals[0] + row_vals[1])
                #print('----------------------data2--------------------------')
                #print(data2)
                
                data=row_vals
                print('----------------------data----------------------------')
                print(data)

                n_rows = len(data)
                
                #writer = pd.ExcelWriter('custorders_data.xlsx')
                #data.to_excel(writer,'Sheet1',index=True)
                #writer.save()
                
                #print('DataFrame is written successfully to Excel File.')
                
                
                print('yo')
                print(weekDayValue)
                if(weekDayValue =='week' or weekDayValue =='day' or weekDayValue =='month'):
                    if(masterCodeValue!=None):
                        res = " Cumulative Quantity for {} {} {} {} for {} is {} ".format(pastFutureValue,limit,weekDayValue,specificType,masterCodeValue,count)
                    elif(brand.strip() != '' or size.strip() != '' or varietal.strip() != ''):
                        res = " Cumulative Quantity for {} {} {} {} for {} {} {} is {} ".format(pastFutureValue,limit,weekDayValue,specificType,brand.strip(),varietal.strip(),size.strip(),count) 
                    else:
                        print(limit)
                        res = " Cumulative Quantity for {} {} {} {} is {} ".format(pastFutureValue,limit,weekDayValue,specificType,count)
                    
                print('res ',res)
                
                if outputtype =='summary':
                    #Summary
                    # Add a table at the bottom of the axes
                    colLabels=(col1_value, "Quantity")
                    nrows, ncols = len(data)+1, len(colLabels)
                    hcell, wcell = 0.5, 1

                    #do the table
                    the_table = plt.table(cellText=data,
                          colLabels=colLabels,
                          loc='center',cellLoc = 'center')

                    print('data ',data)

                    cellDict=the_table.get_celld()
                    for i in range(len(data)+1):
                        cellDict[(i,0)].set_width(0.3)
                        cellDict[(i,1)].set_width(0.2)
                    plt.axis('off')
                    #plt.title('Customer orders for last {} {}'.format(limit,col1_value))
                    plt.savefig("customerOrders.jpg", dpi=500, bbox_inches = 'tight',pad_inches = 0)

                    plt.tight_layout()
                    print('yo')
                    plt.close()
                    img = 'customerOrders.jpg'
                    file_upload(channel, img)
                
                elif outputtype =='detailed':
                    #Detailed
                    print('detailed')
                    
                    df=pd.DataFrame(data)
                    df.columns=['Group','Brand','Size','Varietal',col1_value,'Quantity']
                    df["Quantity"] = pd.to_numeric(df["Quantity"])
                    #data.quantity=data.quantity.astype(int)
                    #df.Date=df.Date.apply(lambda x: x.strftime("%m/%d/%Y"))
                    df.to_excel("orders_detailed.xlsx",index=False)
                    file="orders_detailed.xlsx"
                    file_upload(channel,file)
                    #df = df.infer_objects()
                    #df["Quantity"] = pd.to_numeric(df["Quantity"])
                    #print('df.columns ',df.columns.dtypes)
                    
                    #writer = pd.ExcelWriter('cust_orders_detailed.xlsx')
                    #data.to_excel(writer,'Sheet1',index=True)
                    #writer.save()
                    
                # Add a table at the bottom of the axes
                #plt.show()
                #res ="Cumulative Quantity-{}".format(count)
                print('res',res)
                
            else:
                res = "There is no data present for last few days/weeks."
            #print('::::::::::::::::::::::::::::::hey before response context starts::::::::::::::::::::::::::::::')
            response['context']['currentIntent'] =None
            response['context']['week_day_value'] =None
            response['context']['past_future_value'] =None
            response['context']['sys_number'] =None
            
            response['context']['brand'] =None
            response['context']['size'] =None
            response['context']['varietal'] =None
            response['context']['masterCodeValue'] =None
            response['context']['outputtype'] =None
            response['context']['month'] =None
            response['context']['specific_type'] = None
            #print('outputtype at end:::: ',response['context']['outputtype'])
    except:
        pass
     ##################Code ends for Customer Orders and x months/weeks/days production for brand/size/varietal####################
    
    #############################compare 2 or more years Customer orders and inventory and forecast starts###########################
    
    ####1
    # 
    try:
        print('heyy 1:::::::::::::')
        print(yearMonthValue)
        #and yearMonthValue != None
        if response['context']['currentIntent'] == 'compareCustomerOrders' or response['context']['currentIntent'] == 'compareCustomerOrdersYearwise' or response['context']['currentIntent'] == 'customerOrdersYearly':
            curr= conn.cursor()
            
            try:
                print('try')
                yearvalues = response['context']['yearvalues']
            except:
                yearvalues = []
            print('yearvalues::: ',yearvalues)
            try:
                month = str(response['context']['month_re'])
                print('month ',month)
            except:
                month = 'all'
            
            #if yearMonthValue!=None:
            try:
                number = response['context']['sys_number']
                print('number ',number)
            except:
                number = ''
                print('number except ',number)
            print('number ',number)
                
            print(month)
            print(yearMonthValue)
            
            print(yearvalues)
            print(year)
            
            print(outputtype)
            
            #yearvalues
            #const = len(yearvalues)
            #print(len(yearvalues))
            quantity =[]
            years = []
            resu = []
            columns = ['date']
            
            k=0
            
            temp_yearvalues = yearvalues
            print('#####################yearvalues before::::::::::::::::::::::::::::::################')
            print(yearvalues)
            print('then')
            if yearvalues == None or yearvalues == []:
                if year != '':
                    if year == 'current':
                        now = datetime.datetime.now()
                        year = str(now.year)
                    print('year inside ',year)
                    dictvalues = {}
                    yearvalues = []
                    dictvalues = dict([ ('value', year)])
                    yearvalues.append(dictvalues)
                elif number!='' and yearMonthValue.strip() =='years':
                    print('yo')
                    dictvalues = {}
                    yearvalues = []
                    print(yearvalues)
                    #sql_query = "select year from years where year <= year(NOW()) order by year limit {}"
                    #curr.execute(sql_query.format(number))
                    #print('sql_query ',sql_query)
                    if pastFutureValue == 'last':
                        val = ['2019','2018','2017']
                    elif pastFutureValue == 'next':
                        val = ['2019','2020','2021']
                    print(val[1])
                    i=0
                    #val = curr.fetchall()
                    #print('val ',val)
                    #print(range(number))
                    while i < number:
                        dictvalues = dict([ ('value', val[i])])
                        yearvalues.append(dictvalues)
                        i+=1
                    print('before::')
                    print(yearvalues)
                    print('reverse:: ')
                    if pastFutureValue == 'last':
                        print(yearvalues.reverse())
            print('out')
            print(yearvalues)
            print('#####################length is:: ############################')
            print(len(yearvalues))
            
            print('year ',year)
            #yearvalues = set(yearvalues)
            print('yearvalues before:: ',yearvalues)

            #list_set = set(yearvalues)
            #print(list_set)
            #yearvalues = (list(list_set)) 
            
            #uniqueValues = list()
            #duplicateValues = list()
            
            #for valyr in yearvalues :
            #    if valyr.get("value") not in uniqueValues :
            #        uniqueValues.append(valyr.get("value"))
            #print('##################################################uniqueValues############################################### ')
            #print(uniqueValues)
            #print('##################################################duplicateValues############################################### ')
            #print(duplicateValues)
            #print('yearvalues after:: ',yearvalues)
            
            for valyr in yearvalues:
                print(k, " :: ", valyr.get("value"))
                if valyr.get("value") == 'current':
                    now = datetime.datetime.now()
                    #year = str(now.year)
                    valyr["value"] = str(now.year)
                print('current year:::: ',valyr.get("value"))
                if len(yearvalues) == 1:
                    print('inside len function')
                    print(month.strip())
                    print(brand.strip())
                    print(size.strip())
                    print(varietal.strip())
                    sql_query = "SELECT "
                    temp_year = valyr.get("value")
                    print('****************************************temp_year***************************')
                    print(temp_year)
                    print(specificType)
                    #if temp_year == '2019':
                    part_query = part_sql_query(month.strip(),brand.strip(),size.strip(),varietal.strip(),temp_year,specificType)
                    print("if len yearvalues is 1::: ",part_query)
                    sql_query_final = sql_query + part_query
                    print('sql_query_final::::: ',sql_query_final)
                    value = valyr.get("value")

                    uniquevar = 'count'
                    print('value ',value)
                    row_vals =execute_sql_queries(curr,sql_query_final,None,None,None,None,brand,size,
                                                  varietal,uniquevar,month,value)
                    count = row_vals
                    print('count:: ',count)
                
                print('brandType ',brandType)
                print('sizeType ',sizeType)
                print('varietalType ',varietalType)
                
                #select Date,sum(Balance) from inventory inner join masterdb on `inventory`.`Group`=`masterdb`.`Cat Cd10 Description` where %s and year(`inventory`.`Date`)=year(current_date()) group by Date
                
                #from inventory inner join masterdb on `inventory`.`Group`=`masterdb`.`Cat Cd10 Description` where %s and year(`inventory`.`Date`)=year(current_date()) group by `inventory`.`Group`
                
                #sql_query = "SELECT MONTHNAME (date(`Date`)) as Month,  "
                temp_year = valyr.get("value")
                if outputtype == 'summary' or response['context']['currentIntent'] != 'customerOrdersYearly':
                    if specificType == 'inventory':
                        sql_query = " SELECT date_format(`inventory`.`Date`, '%b') as Month,  "
                    else:
                        if specificType !='orders':
                            sql_query = " SELECT date_format(`forecast`.`Date`, '%b') as Month,  "
                        else:
                            sql_query = " SELECT date_format(`customerorders`.`Date`, '%b') as Month,  "
                elif outputtype == 'detailed':
                    if specificType == 'inventory':
                        sql_query = "select `inventory`.`Group`,`Brand Description`, \
                        `Varietal/ Flavor Description`,`Size Description`, \
                        date_format(`inventory`.`Date`, '%b') as Month, "
                    else:
                        sql_query = " SELECT `forecast`.`master`, `masterdb`.`Brand Description` , \
                        `masterdb`.`Varietal/ Flavor Description`, `masterdb`.`Size Description`, \
                        date_format(`forecast`.`Date`, '%b') as Month,   "
            
                if brandType == 'brand':
                    sql_query = sql_query + " `masterdb`.`Brand Description`,  "
                if sizeType == 'size':
                    sql_query = sql_query + " `masterdb`.`Size Description`,  "
                if varietalType == 'varietal':
                    sql_query = sql_query + " `masterdb`.`Varietal/ Flavor Description`,  "
                
                print('****************************************temp_year***************************')
                print(temp_year)
                print(specificType)
                part_query = part_sql_query(month.strip(),brand.strip(),size.strip(),varietal.strip(),temp_year,specificType)
                print("if len yearvalues is > 1::: ",part_query)
                sql_query = sql_query + part_query
                    
                sql_query = sql_query + " GROUP BY month( date(`Date`))  "
                
                if outputtype == 'detailed':
                    if specificType == 'inventory':
                        sql_query = sql_query + " , `inventory`.`Group` HAVING qty!=0  "
                    else:
                        sql_query = sql_query + " , `forecast`.`master` HAVING qty!=0  "
                
                if brandType == 'brand':
                    sql_query = sql_query+ " , `masterdb`.`Brand Description`   "
                if sizeType == 'size':
                    sql_query = sql_query + " , `masterdb`.`Size Description`   "
                if varietalType == 'varietal':
                    sql_query =  sql_query +" , `masterdb`.`Varietal/ Flavor Description` "
                
                sql_query = sql_query+ " ORDER BY month( date(`Date`))  "
                
                if outputtype == 'detailed':
                    if specificType == 'inventory':
                        sql_query = sql_query + " , `inventory`.`Group`  "
                    else:
                        sql_query = sql_query + " , `forecast`.`master`  "
                    
                if brandType == 'brand':
                    sql_query = sql_query+ "  ,`masterdb`.`Brand Description` "
                if sizeType == 'size':
                    sql_query = sql_query + "  ,`masterdb`.`Size Description` "
                if varietalType == 'varietal':
                    sql_query =  sql_query +"  ,`masterdb`.`Varietal/ Flavor Description` "
                
                print(sql_query)
                value = valyr.get("value")
                sql_query_final = sql_query
                print('sql_query_final::::::: ',sql_query_final)
                uniquevar = 'list'
                print('value ',value)
                row_vals = execute_sql_queries(curr,sql_query_final,None,None,None,None,brand,size,
                                              varietal,uniquevar,month,value)
                print('###############################row_vals############################################# ')
                print(row_vals)
                quantity.append(row_vals)
                if outputtype == 'summary'  or response['context']['currentIntent'] != 'customerOrdersYearly':
                    resu.append( [[ i for i, j in quantity[k] ],[ j for i, j in quantity[k] ]])
                    print('resu[k] ',resu[k])
                    print('#####################################################')
                    if k==0:
                        data=pd.DataFrame(resu[k])
                        #print('0 ',len(data.date))
                        years.append(valyr.get("value"))
                    else:
                        #print('else ',len(resu[k][0]))
                        data=data.append([resu[k][1]])
                        years.append(valyr.get("value"))
                    print('data ',data)
                    columns.append('quantity'+str(k))
                    k = k+1
                    print('------***************data*********************************-------')
                    print(data)
                elif outputtype == 'detailed':
                    #resu.append( [[ i for i, j in quantity[k] ],[ j for i, j in quantity[k] ]])
                    print('row_vals ',row_vals)
                    print('***************************************************************************************************')
                    data_new = pd.DataFrame(row_vals)
                    #data_new["Quantity"] = pd.to_numeric(data_new["Quantity"])
                    #data_new = quantity
                    #data_new = data_new.transpose()
                    #data_new = data_new.fillna(0)
                    print('------***************data_new*********************************-------')
                    print(data_new)
            if outputtype == 'summary' or response['context']['currentIntent'] != 'customerOrdersYearly':
                print('********************************data w/o total*********************************')
                print(data)
                data['total'] = data.sum(axis = 1, skipna = True) 
                print(data['total'][0])
                print(data['total'][1])
                print('********************************data with total*********************************')
                data=data.transpose()
                data = data.fillna(0)
                print(data)
                data.columns=columns
                print(data)
                print('year ',year)
                cellText=[]
                k=0
                colors =["r-","b-","g-","y-","p-","brown-"]
            
                #starts
                for valyr in yearvalues:
                    #loop for this starts
                    variable = 'quantity'+str(k)
                    data[variable]=data[variable].astype(int)
                    print('***************data.variable***************')
                    print(data[variable])
                    data_new = pd.DataFrame()
                    data_new = data[:-1]
                    cellText.append(data_new[variable].values)
                    if month.strip()=='all' or month.strip()=='ytd' or month.strip()=='roy' :
                        print('**********************************data_new*********************************')
                        print(data_new)
                        plt.plot(data_new.date, data_new[variable],colors[k])
                    k= k+1
                #ends
                print(data_new)
                print('################starts#############################')
                print(data)
                print(data['date'].iloc[-1])
                data['date'].iloc[-1] = 'Total'
                print(data['date'].iloc[-1])
                print(data)
                print('################ends#############################')
                if month.strip()=='all' or month.strip()=='ytd' or month.strip()=='roy':
                    print('ho')
                    print('year ',year)
                    plt.tick_params(axis='x',which='both',bottom=False,top=False,labelbottom=False)
                    plt.grid(True, linestyle='-.')
                    #starts
                    print(years)
                    plt.legend(years)
                    print('hooooo')
                    print(data_new)
                    print('-------------')
                    print(years)
                    the_table = plt.table(cellText=cellText, rowLoc='right', rowLabels=years,
                                             colLabels=data_new.date.values,
                                             colLoc='center', loc='bottom')
                    print('**********************data[-1]************************')
                    #data = data.reset_index()
                    #print(data.iloc[-1].transpose())
                    #the_table.append(data.iloc[[-1]].transpose())
                    #print(the_table)
                else:
                    the_table = plt.table(cellText=cellText, rowLabels=years,
                                             colLabels=data_new.date.values,
                                             colLoc='center', loc='center')


                    cellDict=the_table.get_celld()
                    print(len(data_new.transpose()))
                    for i in range(len(data_new.transpose())):
                        print('i:: ',i)
                        print(cellDict[(i,0)])
                        cellDict[(i,0)].set_width(0.2)
                    #plt.tight_layout()
                    print('yo')
                variable=''
                print('year ',year)
                k=0
                for k in range(len(years)):
                    if k==0:
                        variable = years[k]
                    else:
                        variable = variable+ ' vs ' + years[k]
                    k+=1
                month_abre = ''
                print('variable ',variable)
                print('before')
                if month.strip()!='all' and month.strip()!='ytd' and month.strip()!='roy':
                    month_abre = datetime.date(2019,int(month.strip()),1).strftime('%b')
                print('before 1')
                print('length:: ',len(years))
                if len(years) == 1 and (temp_yearvalues=='' or temp_yearvalues==None):
                    year = variable
                print('year ',year)
                print('temp_yearvalues ',temp_yearvalues)
                print('yoooo')
                #if year != '' and (temp_yearvalues=='' or temp_yearvalues==None):
                specificType = specificType.upper()
                #####################here
            if len(yearvalues) == 1:
                if month.strip()=='ytd' or month.strip()=='roy':
                    print('inside ytd roy block')
                    var_month = month.strip().upper()
                    res = "{} {} {} {} {} {} is {}".format(year,var_month,specificType,brand,varietal,size,count)
                else:
                    print('inside all block')
                    res = "{} {} {} {} {} is {}".format(year,specificType,brand,varietal,size,count)
            elif number!='' and yearMonthValue =='years':
                print('inside if block-2')
                if month.strip()=='ytd' or month.strip()=='roy':
                    month = month.strip().upper()
                    res = " {} {} {} for {} {} years {} {} {}".format(month_abre,month.strip(),specificType,pastFutureValue,number,brand,varietal,size)
                else:
                    res = "Comparing {} {} for {} {} years {} {} {}".format(month_abre,specificType,pastFutureValue,number,brand,varietal,size)
            elif len(yearvalues)>1:
                print('inside if block-2')
                if month.strip()=='ytd' or month.strip()=='roy':
                    month = month.strip().upper()
                    res = " {} {} {} for   {} {} {} {}".format(month_abre,month.strip(),specificType,variable,brand,varietal,size)
                else:
                    res = "Comparing {} {} for  {} {} {} {}".format(month_abre,specificType,variable,brand,varietal,size)
            else:
                print('inside else block')
                res = "Comparing {} {} {} {} {} {}".format(variable,month_abre,specificType,brand,varietal,size)
             
            if outputtype != 'detailed':
                plt.title(res)
                plt.subplots_adjust(bottom=0.3)
                if month.strip().upper()!='ALL' and month.strip().upper()!='YTD'  and month.strip().upper()!='ROY' :
                    plt.axis('off')
                plt.savefig("tablegraph.jpg", dpi=300)
                print("plot saved")
                img="tablegraph.jpg"
                file_upload(channel,img)
                plt.close()    
            elif outputtype == 'detailed':
                sql_query = " "
                #Detailed
                print('#####################detailed##############################')
                print('##############data_new################################')
                print(data_new)
                df = pd.DataFrame()
                df = data_new
                print('df-1 ',df)
                df.columns=['Group','Brand','Varietal','Size','Month','Quantity']
                print('df-2 ',df)
                df["Quantity"] = pd.to_numeric(df["Quantity"])
                df.to_excel("orders_yearly_detailed.xlsx",index=False)
                file="orders_yearly_detailed.xlsx"
                file_upload(channel,file)
                print('res',res)
            response['context']['brand']=None
            response['context']['size']=None
            response['context']['varietal']=None
            response['context']['month_re']=None
            response['context']['year']=None
            response['context']['number']=None
            response['context']['currentIntent']=None
            response['context']['outputtype']=None
            response['context']['past_future_value']=None
            response['context']['year_month_value']=None
            response['context']['week_day_value']=None
            response['context']['brand_type']=None
            response['context']['size_type']=None
            response['context']['varietal_type']=None
            response['context']['yearvalues']=None
            response['context']['sys_number']=None
            response['context']['specific_type'] = None
            
    except:
        pass
    
    #############################compare 2 or more years Customer orders and inventory and forecast ends###########################
    
############################################### when next producing for brand size varietal-by me #######################################
    try:
        if response['context']['currentIntent'] == 'nextlastproduction':
            #print('entered when next last varietal')
            frames = ''
            result = ''
            
            detailed_df=pd.DataFrame()
            
            from datetime import datetime, timedelta
            previous_Date = datetime.strftime(datetime.now() - timedelta(1), '%Y-%m-%d')
            print('previous_Date ',previous_Date)
            #if whse.strip()=='noselect':
            curr=conn.cursor()
            #print('hooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooo')
            #print('inside nextlastproduction')
            var = variation(brand,size,varietal)
            
            #curr.execute("select DATE_ADD(Date1, INTERVAL - WEEKDAY(Date1) DAY) as dt    from `production`   where  `Date1` >= CURDATE() and    `Date1` <= DATE_ADD( CURDATE(),INTERVAL 3 WEEK )  and `LINE` !='M'    group by DATE_ADD(Date1, INTERVAL - WEEKDAY(Date1) DAY)   order by DATE_ADD(Date1, INTERVAL - WEEKDAY(Date1) DAY) DESC ")
            
            curr.execute("select Date1 as dt  from `production` inner join masterdb on `production`.`Group`=`masterdb`.`Cat Cd10 Description` where  `Date1` >= CURDATE() and    `Date1` <= DATE_ADD( CURDATE(),INTERVAL 3 WEEK )  and `LINE` !='M'    group by WEEK(date(`Date1`))   order by WEEK(date(`Date1`)) DESC ")
            
            next_dates_in_wks = curr.fetchall()
            
            curr.execute("Select distinct production.Group, \
            concat(masterdb.`Description`,'-',masterdb.`Size Description`) as descr from production inner join masterdb \
            on production.Group = masterdb.`Cat Cd10 Description` where {} and production.Group like 'M%'".format(var))
            
            group_codes = curr.fetchall()
            #print('group_codes ',group_codes)
            #print('--------------starts----------------')
            #print('group_codes[0] ',group_codes.loc[0])
            #print('--------------ends----------------')
            df = pd.DataFrame(group_codes)
            df.reset_index()
            new_df = pd.DataFrame()
            #print(df[0])
            #print('---------------')
            
            
            #print('next_dates_in_wks ')
            #print(next_dates_in_wks)
            #print('----****----')
            
            next_dates_in_wks_df = pd.DataFrame(next_dates_in_wks)
            next_dates_in_wks_df.reset_index()
            #print('next_dates_in_wks_df::::: ',next_dates_in_wks_df)
            #print('----------------')
            #print(next_dates_in_wks_df[0].iloc[0])
            #print(next_dates_in_wks_df[0].iloc[1])
            #print(next_dates_in_wks_df[0].iloc[2])
            #print(next_dates_in_wks_df[0].iloc[3])
            #print('----------------')
            #print(next_dates_in_wks_df.iloc[0])
            #print('----------------')
            #print(next_dates_in_wks_df.loc[0])
            #print('----------------')
            #print(next_dates_in_wks_df[[0]])
            #print('----------------')
            #print('ohhh yeahhh')
            List = []
            
            
            #print('len:: ',len(next_dates_in_wks_df))
            for i in range(len(next_dates_in_wks_df)):
                #print('i ',next_dates_in_wks_df[0].iloc[i])
                #print('j ',next_dates_in_wks_df.loc[[i]])
                List.append(next_dates_in_wks_df[0].iloc[i])
            #print('wooooo')
            #print('List ',List)
            #print('----****----')
            #next_dates_in_wks_df_tr = next_dates_in_wks_df.transpose()
            #print('next_dates_in_wks_df_1  ', next_dates_in_wks_df_tr[0])
            #print('next_dates_in_wks_df_2  ', next_dates_in_wks_df_tr.iloc[0])
            #print('next_dates_in_wks_df_tr ',next_dates_in_wks_df_tr)
            #print('next_dates_in_wks_df_3  ', next_dates_in_wks_df_tr.iloc[[0]])
            #print(next_dates_in_wks_df[0])
            #for i in next_dates_in_wks_df:
            #    data_df.columns.append(next_dates_in_wks_df[0].iloc[i])
            
            new_list = []
            for j in range(len(List)):
                new_list.append( List[j].strftime('%Y-%m-%d'))
                #["%s"%(i.strftime("%b %d")) for i in quantity1 ]
            
            #print('new_list ',new_list)
            new_list_rev = new_list.reverse()
            #print('df[0] ',df[0])
            
            #print('**********************************new_list*************************** ',new_list)
            data_df = pd.DataFrame(columns = new_list, index = df[0])
            #data_df_new = pd.DataFrame(columns = new_list_rev, index = df[0])
            #print('******************data_df_new********************')
            #print(data_df_new)
            #data_df.columns = List
            #print('****************data_df***************')
            #print(data_df)
            #print('****************data_df.columns***************')
            #print(data_df.columns)
            #print('---------------')
            #print('List ',List)
            #print('---------------')
            #next_dates_in_wks_df = pd.DataFrame(next_dates_in_wks)
            #next_dates_in_wks_df.reset_index()
            #next_dates_in_wks_df = 
            #print('next_dates_in_wks_df::::: ',next_dates_in_wks_df)
            #print(next_dates_in_wks_df.transpose())
            #print('var ',var)
            
            #resultdf = pd.DataFrame()
            #resultdf.set_index(df[0])
            #print('resultdf ',resultdf)
            #print('-------')
            for master in df[0]:
                #print(master)
                if outputtype =='detailed':
                    sql_query = "  select `production`.`Date1`, `production`.`LINE`, coalesce(sum(`Schedule2`),0) as produced, \
                    `production`.`PRODUCT`, `production`.`DESCRIPTION`,`production`.`SIZE / PACK`, \
                    `production`.`WHSE`, `production`.`WeekNum`,`production`.`Month`,`production`.`Group` "
                else:
                    sql_query = "  select DATE_SUB(CURDATE(), INTERVAL 1 DAY) as dt, coalesce(sum(`Schedule2`),0) as produced  "

                sql_query = sql_query +"  from `production` inner join masterdb   \
                on `production`.`Group`=`masterdb`.`Cat Cd10 Description`   where \
                `Date1` >= DATE_SUB( DATE_ADD(CURDATE(), INTERVAL - WEEKDAY(CURDATE()) DAY),INTERVAL 4 WEEK )   \
                AND `Date1` <= DATE_SUB(CURDATE(), INTERVAL 1 DAY)  and `LINE` !='M'  "

                if(whse.strip()!='noselect'):
                    sql_query = sql_query +" and `WHSE` = {} "

                #if(brand.strip() != '' or size.strip() != '' or varietal.strip() != ''):
                #    if(brand.strip() != ''):
                #        sql_query = sql_query +" and `masterdb`.`Brand Description`= '{}'  "
                #    if(size.strip() != ''):
                #        sql_query = sql_query +" and `masterdb`.`Size Description`= '{}'  "
                #    if(varietal.strip() != ''):
                #         sql_query = sql_query +" and `masterdb`.`Varietal/ Flavor Description`= '{}'  "
                #else:
                #    sql_query = sql_query +" "

                if outputtype =='detailed':
                    sql_query = sql_query + " and production.Group = '{}'   group by `production`.`Group`, \
                    WEEK(date(`Date1`)) order by `production`.`Group`, WEEK(date(`Date1`))";
                else:
                    sql_query = sql_query + " and production.Group = '{}'  ";
                #else:
                    #sql_query = sql_query + " and production.Group = '{}'  group by  WEEK(date(`Date1`)) order by  WEEK(date(`Date1`)) DESC";

                #print('sql_query')
                #print(sql_query)
                #print('----------------------------')

                #starts
                if(whse.strip()!='noselect'):
                    print('whse.strip() ',whse.strip())
                    curr.execute(sql_query.format(whse.strip(),master))
                else:
                    curr.execute(sql_query.format(master))
                   
                #ends

                #curr.execute("select Description,startDate,endDate,Schedule2 from(with recursive data1 as(SELECT `production`.`Group` as Mastercode,Date1,sum(Schedule2) as Schedule2,row_number() OVER (PARTITION BY `production`.`Group` ORDER BY Date1) as seqNo FROM production inner join masterdb on `production`.`Group`=`masterdb`.`Cat Cd10 Description` WHERE `masterdb`.`Brand Description`='%s' and`masterdb`.`Size Description`='%s' and `masterdb`.`Varietal/ Flavor Description`= '%s' and Date1>=current_date() group by Date1,`production`.`Group`), r_cte as ( SELECT Mastercode, Date1,Schedule2,seqNo,Date1 as startDate FROM data1 WHERE seqNo = 1 union all SELECT d.Mastercode, d.Date1,d.Schedule2,d.seqNo, (CASE WHEN c.Date1 = DATE_ADD(d.Date1,interval -1 day) THEN c.startDate ELSE d.Date1 END) as startDate FROM data1 d INNER JOIN r_cte c ON c.Mastercode= d.Mastercode AND c.seqNo = d.seqNo - 1) SELECT Mastercode,startDate,MAX(Date1) as endDate,seqNo,sum(Schedule2) as Schedule2 FROM r_cte GROUP BY Mastercode,startDate) mytable inner join masterdb on mytable.Mastercode=`masterdb`.`Cat Cd10 Description` where seqNo=1;"%(brand,size,varietal))
                quantity1= curr.fetchall()
                print('%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%')
                print('#################quantity1 sql_query#############')
                print(sql_query)

                if outputtype =='detailed':
                    sql_query = "  select `production`.`Date1`, `production`.`LINE`, coalesce(sum(`Schedule2`),0) as produced, \
                    `production`.`PRODUCT`, `production`.`DESCRIPTION`,`production`.`SIZE / PACK`, \
                    `production`.`WHSE`, `production`.`WeekNum`,`production`.`Month`,`production`.`Group` "
                else:
                    sql_query = "  select `Date1` as dt, coalesce(sum(`Schedule2`),0) as produced  "

                sql_query = sql_query +"   from `production` inner join masterdb   \
                on `production`.`Group`=`masterdb`.`Cat Cd10 Description` where \
                `Date1` >= CURDATE() and `Date1` <= DATE_ADD( CURDATE(),INTERVAL 4 WEEK )  and `LINE` !='M'  "

                if(whse.strip()!='noselect'):
                    sql_query = sql_query +" and `WHSE` = {} "

                if outputtype =='detailed':
                    sql_query = sql_query + "  and production.Group = '{}' group by `production`.`Group`, \
                     WEEK(date(`Date1`)) order by `production`.`Group`, WEEK(date(`Date1`)) ";
                else:
                    sql_query = sql_query + "  and production.Group = '{}'  group by  WEEK(date(`Date1`)) order by  WEEK(date(`Date1`)) ";

                #print('sql_query')
                #print(sql_query)
                #print('----------------------------')

                #starts
                if(whse.strip()!='noselect'):
                    print('whse.strip() ',whse.strip())
                    curr.execute(sql_query.format(whse.strip(),master))
                else:
                    curr.execute(sql_query.format(master))

                #curr.execute("select Description,startDate,endDate,Schedule2 from(with recursive data1 as(SELECT `production`.`Group` as Mastercode,Date1,sum(Schedule2) as Schedule2,row_number() OVER (PARTITION BY `production`.`Group` ORDER BY Date1 DESC) as seqNo FROM production inner join masterdb on `production`.`Group`=`masterdb`.`Cat Cd10 Description` WHERE `masterdb`.`Brand Description`='%s' and`masterdb`.`Size Description`='%s' and `masterdb`.`Varietal/ Flavor Description`= '%s' and Date1<=current_date() group by Date1,`production`.`Group`), r_cte as ( SELECT Mastercode, Date1,Schedule2,seqNo,Date1 as endDate FROM data1 WHERE seqNo = 1 union all SELECT d.Mastercode, d.Date1,d.Schedule2,d.seqNo, (CASE WHEN c.Date1 = DATE_ADD(d.Date1,interval 1 day) THEN c.endDate ELSE d.Date1 END) as endDate FROM data1 d INNER JOIN r_cte c ON c.Mastercode= d.Mastercode AND c.seqNo = d.seqNo - 1) SELECT Mastercode,endDate,MAX(Date1) as startDate,seqNo,sum(Schedule2) as Schedule2 FROM r_cte GROUP BY Mastercode,endDate) mytable inner join masterdb on mytable.Mastercode=`masterdb`.`Cat Cd10 Description` where seqNo=1;"%(brand,size,varietal))
                quantity2= curr.fetchall()
                print('%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%')
                print('#################quantity2 sql_query#############')
                print(sql_query)
                #print("sqls done")
                #print('quantity1 len ',len(quantity1))
                #print('quantity2 len ',len(quantity2))
                resu_quantity1 = pd.DataFrame(quantity1)
                resu_quantity2 = pd.DataFrame(quantity2)
                resu_quantity1.reset_index()
                resu_quantity2.reset_index()
                #print('resu_quantity1 ',resu_quantity1)
                #print('resu_quantity2 ',resu_quantity2)
                
                #print('List::: ',List)
                
                
                temp_list =[]
                if outputtype =='summary':
                    #print('inside summary')
                    if len(quantity1)<1 and len(quantity2)<1:
                        print('do nothing')
                        #res="The requested record doesn't exist. Try again with vaild data"
                    else:
                        resu = [[ i for i, j in quantity2 ],[ j for i, j in quantity2 ]]
                        resu2 = [[ i for i, j in quantity1 ],[ j for i, j in quantity1 ]]
                        data = pd.DataFrame(resu2)
                        #print('resu')
                        #print(resu)
                        #print('data')
                        #print(data)
                        data2 = pd.DataFrame(resu)
                        #print('resu2.j:: ')
                        #print(resu2.j)
                        
                        #print('data2::: ')
                        #print(data2)
                        
                        #print('data2 at locations:: ')
                        #print(data2[0].iloc[0].strftime('%Y-%m-%d'))
                        #print(data2[1].iloc[0].strftime('%Y-%m-%d'))
                        #print(data2[2].iloc[0].strftime('%Y-%m-%d'))
                        #print(data2[3].iloc[0].strftime('%Y-%m-%d'))
                       
                        #print('len list ',len(List))
                        #print('data:::::')
                        print(data[0])
                        print(data.iloc[0])
                        
                        
                        #print('qtys are::: ')
                        
                        for i in range(len(data2.loc[0])):
                            for j in range(len(List)):
                                d = List[j].strftime('%Y-%m-%d')
                                #print('d ',d)
                                #d = List[j].strftime('%b %d')
                                #print(d)
                                #print('--------')
                                b = data2[i].iloc[0].strftime('%Y-%m-%d')
                                #print('************each row locn********************* ',data_df.loc[master]) 
                                #print(b)
                                #print('--------')
                                #print(b>= d)
                                if b >= d:
                                    #print('if ',b)
                                    #print(data2[i].iloc[1])
                                    #data_df.loc[master] = data2[i].iloc[1]
                                    data_df.at[master,d]=data2[i].iloc[1]
                                    #temp_list.append( List[j].strftime('%b %d'))
                                    #temp_list.append(data2[i].iloc[1])
                                    break
                                #else:
                                    #temp_list.append(0)
                                    #print('else',0)
                        
                        
                        for i in range(len(data.loc[0])):
                            d = previous_Date
                            #print('d ',d)
                            b = data[i].iloc[0].strftime('%Y-%m-%d')
                            #print(b)
                            if b <= d:
                                data_df.at[master,d]=data[i].iloc[1]
                                break
                        #print('********************data_df************************** ',data_df)
                        #print('resu2')
                        #print(resu2)
                        #print('data2')
                        #print(data2)
                        combined_data = [data , data2]
                        #print('combined_data')
                        #print(combined_data)
                        frames = pd.concat(combined_data, axis=1,  ignore_index=True)
                        #print('frames ')
                        #print(frames)
                        
                        frames_df = pd.DataFrame()
                        frames_df = frames
                        new_header = frames_df.iloc[0]
                        #print('**********************************new_header*************************** ',new_header)
                        #frames_df = frames_df.drop(list(frames_df))
                        #print('part frames_df ')
                        #print(frames_df.columns.values)
                        #print('--------starts---------')
                        #print(frames_df)
                        frames_df['Master'] = master
                        frames_df.set_index(['Master'])
                        #print(frames_df.loc[1,:])
                        #print(frames_df.loc[[1]])
                        #print(frames_df.iloc[[1,1]])
                        #print('--------ends---------')
                        #print('frames ',frames)
                        #print('before part result')
                        #print(result)
                        #print('frames condition')
                        #print(frames!='')
                        #print('result condition')
                        #print(len(resultdf))
                        #print('new_df before')
                        #print(new_df)
                        #print(result)
                        #if len(result) == 0:
                            #print('if')
                        #df.loc[master] = pd.concat(combined_data, axis=1,  ignore_index=True)
                        #df = [[df]]
                        new_df= new_df.append(frames_df)
                            #print('frames if')
                        #print('new_df after')
                        #print(new_df)
                            #result = frames
                            #print('result if')
                            #print(result)
                        #else:
                            #print('else')
                            #resultdf.loc[master] = pd.concat(combined_data, axis=1,  ignore_index=True)
                            #print('frames else')
                           # print(resultdf)
                            #result =result.append( pd.concat(frames, axis=1,  ignore_index=True))
                            #print('result else')
                            #result = result.fillna(0)
                            #print(result)
                            #print(temp_res)
                            #result = result.append(temp_res, ignore_index=True)
                            #print('after result ',result)
                        #data=data.append(resu)
                        #print('frames after')
                        #print(frames)
                        #print('overall frames')
                        #print(frames)
                        #print(data)
                        #print('wohoooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooo')
                        
                        #data=data.transpose()
                        #data.columns=['LAST','PRODUCED','NEXT\n (WEEK\n START\n DATE)','PLANNED']
                        #frames = frames.fillna(0)
                        #data.PLANNED=data.PLANNED.astype(int)
                        #data.PRODUCED=data.PRODUCED.astype(int)
                        #print("table created")

                        
                elif outputtype =='detailed':
                    #print('inside detailed')
                    if len(quantity1)<1 and len(quantity2)<1:
                        res="The requested record doesn't exist. Try again with vaild data"
                    else:
                        resu = [[ "%s"%(i.strftime("%b %d")) for i, j, k, l, m, n, o, p, q, r in quantity2 ],
                                [ j for i, j, k, l, m, n, o, p, q, r in quantity2 ],[ k for i, j, k, l, m, n, o, p, q, r in quantity2 ],
                                [ l for i, j, k, l, m, n, o, p, q, r in quantity2 ],
                               [ m for i, j, k, l, m, n, o, p, q, r in quantity2 ],[ n for i, j, k, l, m, n, o, p, q, r in quantity2 ],
                               [ o for i, j, k, l, m, n, o, p, q, r in quantity2 ],[ p for i, j, k, l, m, n, o, p, q, r in quantity2 ],
                               [ q for i, j, k, l, m, n, o, p, q, r in quantity2 ],[ r for i, j, k, l, m, n, o, p, q, r in quantity2 ]]

                        resu2 = [[ "%s"%(i.strftime("%b %d")) for i, j, k, l, m, n, o, p, q, r in quantity1 ],
                                [ j for i, j, k, l, m, n, o, p, q, r in quantity1 ],[ k for i, j, k, l, m, n, o, p, q, r in quantity1 ],
                                [ l for i, j, k, l, m, n, o, p, q, r in quantity1 ],
                               [ m for i, j, k, l, m, n, o, p, q, r in quantity1 ],[ n for i, j, k, l, m, n, o, p, q, r in quantity1 ],
                               [ o for i, j, k, l, m, n, o, p, q, r in quantity1 ],[ p for i, j, k, l, m, n, o, p, q, r in quantity1 ],
                               [ q for i, j, k, l, m, n, o, p, q, r in quantity1 ],[ r for i, j, k, l, m, n, o, p, q, r in quantity1 ]]

                        #print('data')
                        #print(data)
                        #print('data for resu 1')
                        #print('**********************resu*********************')
                        #print(resu)
                        tr_resu = np.transpose(resu)
                        tr_resu2 = np.transpose(resu2)
                        #print('reversed list')
                        #print(list(reversed(tr_resu2)))
                        arr = np.concatenate((tr_resu2, tr_resu), axis=0)
                        
                        #print('arr ',arr)
                        #print('********************************overall data********************************')

                        #Detailed
                        #print('$$$$$$$$$$$$$$$$$$$detailed data$$$$$$$$$$$$$$$$$$$$$$$$$$')
                        #print('data ',arr)
                        data = pd.DataFrame(arr)
                        detailed_df = detailed_df.append(data, ignore_index=True)
                        print('detailed_df ',detailed_df)
                        #df=pd.DataFrame(data=arr)
                        
            
            #print('yo starts')
            if outputtype =='summary':
                data_df = data_df.reset_index()
                df = df.reset_index()
                #print('df[1] ',df[1])
                data_df['Description'] = df[1]
                #print('data_df[Description] ',data_df['Description'])
                data_df = data_df.rename(columns={0: 'Master'})

                print('data_df$$$$$$$$$$$$$$$$$ ',data_df)

                #print('sorted data_df ',sorted(data_df))
                #colLabels=("Master", "Description","Size", "Cases_Short", "Short_On", "Bottling_On", "First_Available")
                 #       nrows, ncols = len(data)+1, len(colLabels)
                  #      hcell, wcell = 0.5, 1

                #do the table
                #the_table = plt.table(cellText=data,
                 #             colLabels=colLabels,
                 #             loc='center',cellLoc = 'left')

                #print('data_df.columns ********** ',data_df.columns)

                #print('####data_df yooooooooo####')
                #print(data_df_new)

                #data_df.columns = 
                row_colors=['#f1f1f2', 'w']
                header_columns=0
                #print('hoo 1')
                bbox=[0, 1, 1, 1, 1]
                #print('hoo 2')
                font_size=10
                header_color='#40466e'
                edge_color='w'
                fig=plt.figure(figsize=(20,20))

                #,colLabels=data.columns
                #print('before')
                data_df = data_df.fillna(0)
                data_df = data_df.drop(['Master'], axis=1)
                #print('data_Df.columns:::: ',data_df.columns)
                #cols = []
                values_column = []
                #temp_list = []
                print('yooooooo')
                previous_Date = datetime.strftime(datetime.now() - timedelta(1), '%Y-%m-%d')
                print('previous_Date ',previous_Date)
                values_column.append('Description')
                #temp_list.append('Description')
                print('values_column ',values_column)
                values_column.append(previous_Date)
                #values_column.append(previous_Date)
                #temp_list.append( previous_Date.strftime('%b %d'))

                #print('values_column ',values_column)
                #print('data_df ',data_df)
                #print('data_df ',data_df.loc[:, data_df.columns != previous_Date])
                for col in data_df.loc[:, data_df.columns != previous_Date]:
                    #print(col)
                    #print(col != 'Description')
                    #print(col != previous_date)
                    if col != 'Description' :
                        #print('col ',col)
                        #temp_col = col.apply(str)
                        #print(temp_col)
                        #print(datetime.datetime(temp_col))
                        #print('yo ',datetime.strftime(col.apply(str),'%B %d'))
                        values_column.append(col)
                        #.dt.strftime('%B %d')
                        #temp_list.append( col.strftime('%b %d'))
                #print('values_column::: ',values_column)
                print('values_column ',values_column)
                
                
                
               # for value in data_df.columns:
                   # if value != 'Description':
                     #   print(value)
                   #     #print(value.strftime('%y'))
                      #  print('hoooo')
                     #   print(type(value))
                       # print('value:: ',datetime.strptime(value, '%B %d'))
                        
                print('List ',List)
                print(values_column[1:])
                #y = data_df.loc[:, data_df.columns != 'Description']
                #print([datetime.strptime(x, '%m/%d/%Y') for x in values_column[1:]])
                values_column_dt = [datetime.strptime(x, '%Y-%m-%d') for x in values_column[1:]]
                values_column_dt = values_column_dt
                
                values_column_new_dt = []
                values_column_new_dt.append('Description')
                for j in range(len(values_column_dt)):
                    values_column_new_dt.append( values_column_dt[j].strftime('%b_%d'))
                
                print('values_column_new_dt:: ',values_column_new_dt)
                
                data_df = data_df[values_column]
                print('data_df.columns before ',data_df.columns)
                data_df.columns = values_column_new_dt
                print('data_df.columns after ',data_df.columns)
                data_df = data_df[values_column_new_dt]
                print('hoo')
                r,c = data_df.shape
                
                #for j in range(len(values_column)):
                    #print(values_column)
                    #print(j)
                    #if j != 0:
                        #print('if')
                        #print(datetime.timestamp(values_column[j]))
                        #print(datetime.strptime(values_column[j], '%Y-%m-%d'))
                        #d = List[j].strftime('%B %d')
                        #d = parse(values_column[j]).strftime('%b %d')
                        #print('d ',d)
                  #  print('inside')
                  #  print('1 ',value)
                  #  if value != 'Description':
                  #      print('if')
                   #     print(type(value))
                   #     date_object = datetime.strptime(value, '%b %d')
                   #     print('date_object::: ',date_object)
                print('yo')
                mpl_table = plt.table(cellText=np.vstack([['', 'Last 30 Days', 'Current week', 'Week #', 'Week #', 'Week #'], data_df.columns, data_df.values]),cellColours=[['none']*c]*(2 + r),colLoc='center', loc='center')
                #, rowLabels=['production'], colLabels=data.date
                #print('mpl_table ',mpl_table)
                print('afterwards')

                mpl_table.auto_set_font_size(False)
                mpl_table.set_fontsize(font_size)



                set_align_for_column(mpl_table, col=0, align="left")
                set_align_for_column(mpl_table, col=1, align="right")
                set_align_for_column(mpl_table, col=2, align="right")
                set_align_for_column(mpl_table, col=3, align="right")
                set_align_for_column(mpl_table, col=4, align="right")
                set_align_for_column(mpl_table, col=5, align="right")

                for k, cell in six.iteritems(mpl_table._cells):
                    cell.set_edgecolor(edge_color)
                    if k[0] == 1 or k[0] == 0 or k[1] < header_columns:
                        cell.set_text_props(weight='bold', color='w')
                        cell.set_facecolor(header_color)
                    else:
                        #print('k[0] ',k[0])
                        #print('k[1] ',k[1])
                        cell.set_facecolor(row_colors[k[0]%len(row_colors) ])
                #set_pad_for_column(col=0, pad=0.01)
                plt.title("%s %s %s Production Plan"%(brand,varietal,size))

                #cellDict=mpl_table.get_celld()
                #for i in range(len(data_df)+1):
                #    cellDict[(i,0)].set_width(0.5)
                #    cellDict[(i,1)].set_width(0.3)
                #    cellDict[(i,2)].set_width(0.3)
                #    cellDict[(i,3)].set_width(0.3)
                #    cellDict[(i,4)].set_width(0.3)
                #    cellDict[(i,5)].set_width(0.3)
                #print(mpl_table)
                #print('before')
                #print(mpl_table._cells[0])
                #plt.tight_layout()
                #print('after')
                #plt.savefig("table.jpg", dpi=300)
                plt.axis('off')
                #plt.tight_layout()
                plt.savefig("table.jpg",bbox_inches='tight', pad_inches = 0)



                #the_table = plt.table(cellText=data,
                  #            colLabels=colLabels,
                  #            loc='center',cellLoc = 'left')
                        #print(the_table.properties())
                   #     cellDict=mpl_table.get_celld()


                        #plt.axis('off')
                        #plt.savefig("outOfStockList.jpg", dpi=300, bbox_inches = 'tight',pad_inches = 0)


                #print('ha')

                #plt.savefig("table.jpg")
                img="table.jpg"
                #print("table saved")
                file_upload(channel,img)
                plt.close()
            
            if outputtype =='detailed':
            
                #detailed_df = detailed_df.append(detailed_df, ignore_index=True)
                            #print(df)
                detailed_df.columns=['Week','LINE','Schedule','PRODUCT','DESCRIPTION','SIZE/PACK','WHSE', 'WeekNum','Month','Group']
                detailed_df.to_excel("next_last_production_detailed.xlsx",index=False)
                file="next_last_production_detailed.xlsx"
                file_upload(channel,file)
            #print('yo ends')
            
            response['context']['brand']=None
            response['context']['varietal']=None
            response['context']['month']=None
            response['context']['year']=None
            response['context']['size']=None
            response['context']['number']=None
            response['context']['whse']=None
            response['context']['period']=None
            response['context']['view']=None
            response['context']['timeperiod']=None
            response['context']['currentIntent']=None
            response['context']['outputtype']=None
    except:
        pass
    
    
    
    
##########################################################  Output   ###################################################################
    
    slack_output = slack_output + str(res)
    
    if slack_output == '' and brand.strip() == '' and size.strip() != '' and varietal.strip() != '' and year.strip() != '' and month.strip() != '':
        slack_output = 'Record for the given values for "' + str(brand) + '" does not exists. Please check'        
    
    if 'actions' in response:
        print("oops i went here")
        if response['actions'][0]['type'] == 'client':
            current_action = response['actions'][0]['name']
   
    return(context,slack_output,current_action)