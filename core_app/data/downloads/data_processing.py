import pandas as pd
from TradeSeeker import time as t
from datetime import datetime
from alpaca_trade_api.rest import REST

class Data(t.TimeRange):
    """ 
    
Data class contains data pipeline methods; starting with method for getting the api keys down to methods for getting processed
data. At the initialization of the class, you will need to specify the timezone you want (note that the timezone of the data is   utc)for the start range. Keep in mind the specified_timezone attribute is an attribute inherited from TimeRange() cloass.  Also you would have to specify the activity types. It has to be filled if you want to call the structure_data and 
and get_processed_data methods. 

    """
    live_AK = 'AKQRCX9RA3ZXRCHDOI4X'
    live_SK = 'M55nxDt2OBadA4AniR6hZEDmxTe7yWOKBH1RsVIb'
    live_URL = 'https://api.alpaca.markets'
    paper_AK = 'PKZCGZWP6J6NZ66OE4R0'
    paper_SK = 'ZK83PAcyrkKSr7smkDCdDXpl9pevUA2T4VD7ufD7'
    paper_URL = 'https://paper-api.alpaca.markets'
    
    def __init__(self, specified_timezone, activity_type, trade_type):
        super().__init__(specified_timezone)
        self.activity_type = activity_type
        self.trade_type = trade_type
    
    def get_apikey(self):
        """
        This method return the api authentication keys for either paper or live trading
        
        Inputs: trade_type (to be specified during the class initialization)
        Returns: It returns api key, secret key and end point url for either live or paper trading. 
        """
        
        if self.trade_type == 'live':
            return self.live_AK,self.live_SK,self.live_URL
        elif self.trade_type == 'paper':
            return  self.paper_AK, self.paper_SK,self.paper_URL 
        else:
            raise AttributeError('Specified trade type is not correct. Only live or paper trad type is allowed')
        
    def get_data(self):
        """
        This method gets trades data from through the api. You specify the activity type eg FILL,MISC etc you would like.
        Inputs: activity_type (to be specified during class initialization), get_starttime() method. 
        Returns: It returns a dataframe of all the specified activity in one's alpaca account. 
        """
        self.api_key, self.secret_key, self.url = self.get_apikey()
        self.api = REST(self.api_key, self.secret_key, self.url)
        
        self.activity_start_time = pd.to_datetime(self.get_starttime(365, 'd').strftime('%Y-%m-%d %H:%M:%S'))
        self.activities = []
        self.previous_page_token= None
        
        while True:
            self.page = self.api.get_activities(
                                         activity_types = self.activity_type,
                                           after = self.activity_start_time,
                                           page_token = self.previous_page_token,
                                            )

            if self.page:
                self.activities.append(self.page)
                self.previous_page_token = self.page[-1].id
            else:
                break
        
        self.activity_df =  pd.DataFrame([activity._raw for nested in self.activities for activity in nested])
        return self.activity_df
    
    
    def clean_data(self):
        """
        This method cleans up the data retrieved from the get_data method. 
        Inputs: get_data() method
        Returns: A cleaned dataframe. 
        
        """
        self.dataframe = self.get_data()
        
        # generating date and time field from transaction_time field
        self.dataframe['date'] = self.dataframe['transaction_time'].str.split(
                                                                'T', expand = True)[0]
        self.dataframe['time'] = self.dataframe['transaction_time'].str.split(
                                                     'T', expand = True)[1].replace(
                                                                                   'Z', '', regex = True)
        #reconstructing the transaction_time field for easier processing
        self.dataframe['transaction_time']  = pd.to_datetime(self.dataframe['date'] + ' ' + self.dataframe['time'])
        
        self.dataframe['price'] = self.dataframe.price.astype(float)
        self.dataframe['qty'] = self.dataframe.qty.astype(int)
        
        self.dataframe = self.dataframe.rename(columns = {'qty': 'shares_qty', 'price':'original_price'})
        self.dataframe = self.dataframe.drop(['id','type','leaves_qty', 'order_id', 'cum_qty','order_status'], axis = 1).copy()
        
        return self.dataframe
    
    def structure_data(self): 
        """
        This method performs some transformations on the cleaned data.
        Inputs: clean_data() method.
        Returns: A dataframe that is a transformed version of the cleaned data. 
        """
        self.dataframe = self.clean_data()
        self.df_append = pd.DataFrame()
        self.stock_list = list(self.dataframe.symbol.unique())
        
        for symbol in self.stock_list:
            self.stock = self.dataframe[self.dataframe.symbol == symbol].reset_index(drop = True)
            self.stock['agg_price'] = round(self.stock.shares_qty * self.stock.original_price, 3)
            
            #  calculating values for total share sold and mean share price
            self.total_share_sold = self.stock.loc[self.stock.side == 'sell', 'shares_qty'].sum()
            self.mean_share_price =  round((self.stock.loc[self.stock.side == 'buy', 
                                                      'agg_price'].sum())/(self.stock.loc[self.stock.side == 'buy',
                                                                                     'shares_qty']).sum(), 3)
            
            self.stock_buy = self.stock[self.stock.side == 'buy']
            self.stock_bought_only = self.stock_buy.copy()
            
            self.stock_bought_only['shares_sold'] = self.total_share_sold
            self.stock_bought_only['mean_share_price'] = self.mean_share_price
            
            #sorting by transaction for easy calculation of stock left for sale
            self.stock_bought_only.sort_values('transaction_time',ascending = True, inplace = True)
            # getting the cumulative shares per stock. This is to enable some easy processing in later stages.
            self.stock_bought_only['cum_shares'] = self.stock_bought_only.shares_qty.cumsum()
        
            self.df_append = self.df_append.append(self.stock_bought_only)
            
        self.new_df =self.df_append.copy()

        #cum_share_sub field is created inorder to track whether our calculation on the next stock to sell
        # should be substracting cum shares from the share sold or just taking the value of the share qty.
        #if it is positive, it means there are still shares in the stock that should be sold, hence the ss_identifier will be 1
        # if is 0 or -ve, it means the shares for that particular stock is fully sold out and hence its ss_identifier value will be 0
        
        self.new_df['cum_shares_sub'] = self.new_df.cum_shares - self.new_df.shares_sold 
        self.new_df['ss_identifier'] = (self.new_df.shares_sold < self.new_df.cum_shares).astype(int) #sts means stock_to_sell
        self.new_df = self.new_df.drop(['agg_price'], axis = 1)
        return self.new_df

        
    def get_processed_data(self):
        """ This method returns the processed data which is fed to the trade logic 
        to determine if a stock should be sold or not """
        
        self.dataframe = self.structure_data()
        self.df_append = pd.DataFrame()
        self.stock_list = list(self.dataframe.symbol.unique())
    
        for symbol in self.stock_list:
            self.stock = self.dataframe[self.dataframe.symbol == symbol].reset_index(drop = True)
             # the shifted_col helps with the computation of shares_left_tosell.
            self.stock['shifted_col'] = self.stock.ss_identifier.shift(periods = -1, axis = 0, fill_value = 0)
        
            for i in range(len(self.stock)):
                self.ss_identifier = self.stock.loc[i, 'ss_identifier']
                self.shifted_col = self.stock.loc[i, 'shifted_col'] 

            # determines how much shares left for sale for each stock bought
                if (self.ss_identifier == 0) & (self.shifted_col == 0):
                    self.stock.loc[(self.stock.ss_identifier == 0) & (self.stock.shifted_col == 0),'shares_left_tosell'] = 0
                
                elif (self.ss_identifier == 1) & (self.shifted_col == 1):
                    self.stock.loc[(self.stock.ss_identifier == 1) & (self.stock.shifted_col == 1),
                          'shares_left_tosell'] = self.stock.loc[i, 'cum_shares_sub']
            
                elif (self.ss_identifier == 1) & (self.shifted_col == 0):
                    self.stock.loc[(self.stock.ss_identifier == 1) & (self.stock.shifted_col == 0),
                          'shares_left_tosell'] = self.stock.loc[i, 'shares_qty']
            self.df_append = self.df_append.append(self.stock)
        
        self.new_df = self.df_append
        
        #drop rows that have sold out their shares
        self.new_df = self.df_append[self.df_append.shares_left_tosell != 0].copy()
        
        self.new_df['min_sell_time'] = self.new_df['transaction_time'] + pd.Timedelta(1, 'd')
        self.new_df['min_price_1wk'] = self.new_df['mean_share_price']  + (self.new_df['mean_share_price'] * 0.025)
        self.new_df['desired_price_1wk'] = self.new_df['mean_share_price']  + (self.new_df['mean_share_price'] * 0.05)
        self.new_df['must_sell_price'] = self.new_df['mean_share_price']  + (self.new_df['mean_share_price'] * 0.2)
        self.new_df['min_price_2wk'] = self.new_df['mean_share_price']  + (self.new_df['mean_share_price'] * 0.015)
        self.new_df['desired_price_2wk'] = self.new_df['mean_share_price']  + (self.new_df['mean_share_price'] * 0.05)
        
        self.new_df = self.new_df.drop(['ss_identifier', 'shifted_col', 'cum_shares_sub'], axis = 1).reset_index(drop = True)
        return self.new_df
