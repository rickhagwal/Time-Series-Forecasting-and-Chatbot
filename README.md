# Chatbot-TWG-Natural Language Processing Based
IBM Watson NLP based Chatbot

i.)	Created an IBM Watson conversation service, which is an NLP- based chatbot, that I have to train in the manner such that it knows what user is asking from it, and gives correct response.  IBM Watson learns from its experience. We have integrated slack bot , which listens to Watson conversations, and responds with the appropriate answers provided by IBM Watson. 
Below is the config.py file, with Slack Configuration and Watson Configuartion(hidden)-

https://github.com/rickhagwal/Chatbot-TWG/blob/master/config.py


ii.)	Data Cleaning and preprocessing techniques on the raw data such as-
a)	Checking out the missing values
b)	Splitting data set into Training and Test set.
c)	Doing Feature Scaling.
d)	Detecting noise in data. e.g., Outliers
e)	Predicting and applying seasonality
Python libraries that I have used over here are: Pandas, Matplotlib, Numpy.

iii.)	Data Visualisation using ad-hoc analysis and presenting results in the form of Charts, tables, excel spreadsheets etc.

Below figures depicts Data Visualization using ad-hoc analysis and presenting results in the form of Charts, tables, excel spreadsheets etc.

Comparison of Stock for different years of some specific brand wine and other criterias-

![alt text](https://github.com/rickhagwal/Chatbot-TWG/blob/master/Comparison.jpg)

Comparing Inventory for different years of some specific brand wine and other criterias-

![alt text](https://github.com/rickhagwal/Chatbot-TWG/blob/master/tablegraph.jpg)

Out Of Stock Trend for Specific Brand-

![alt text](https://github.com/rickhagwal/Chatbot-TWG/blob/master/OOS-trend-for%20Franzia.jpg)

Out Of Stock Orders-

![alt text](https://github.com/rickhagwal/Chatbot-TWG/blob/master/outOfStockList.jpg)

Inventory-

![alt text](https://github.com/rickhagwal/Chatbot-TWG/blob/master/inventoryOutput.jpg)

Production Plan-

![alt text](https://github.com/rickhagwal/Chatbot-TWG/blob/master/table.jpg)


iv.)	Used Time Series Forecasting Model i.e., Prophet, to predict the future shipments of wines, belonging to a specific brand, size, varietal and master code respectively.

Below figure depicts how data looks like, before prediction of data.

![alt text](https://github.com/rickhagwal/Chatbot-TWG/blob/master/Daily%20Shipment%20Seasonality.jpg)

Below figure depicts what data looks like after prediction of data. Here, blackdots represents the actual data, and dark blue represents the forecasted data.

![alt text](https://github.com/rickhagwal/Chatbot-TWG/blob/master/Predicted%20Data.jpg)

Below figure represents the trend of data forecasted, along with holidays and weekly seasonality i.e., Seasonality Trends.

![alt text](https://github.com/rickhagwal/Chatbot-TWG/blob/master/Data%20forecasted%20for%20diff%20seasonalities.png)

Major challenge was to be able to predict which wine would go out of stock in the coming future, based upon history data. By applying time-series forecasting model, we could be able to do that. Just we need to do data preprocessing effectively, in order to make it efficient for every variety of wine. As for some wines, we are shipping almost daily, some of them we are shipping in regular time, some of them we are shipping irregularly etc.

v.)	Fetching data from MySQL database, and excel spreadsheets, to apply Machine Learning models to or used inside IBM Watson conversation based NLP service.


