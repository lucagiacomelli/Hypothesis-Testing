import pandas as pd
import numpy as np
from scipy.stats import ttest_ind


class Data:
    
    def __init__(self, first_dataset, second_dataset, third_dataset):
        # Use this dictionary to map state names to two letter acronyms
        self.first_dataset = first_dataset
        self.second_dataset = second_dataset
        self.third_dataset = third_dataset
        self.states = {'OH': 'Ohio', 'KY': 'Kentucky', 'AS': 'American Samoa', 'NV': 'Nevada', 'WY': 'Wyoming', 'NA': 'National', 'AL': 'Alabama', 'MD': 'Maryland', 'AK': 'Alaska', 'UT': 'Utah', 'OR': 'Oregon', 'MT': 'Montana', 'IL': 'Illinois', 'TN': 'Tennessee', 'DC': 'District of Columbia', 'VT': 'Vermont', 'ID': 'Idaho', 'AR': 'Arkansas', 'ME': 'Maine', 'WA': 'Washington', 'HI': 'Hawaii', 'WI': 'Wisconsin', 'MI': 'Michigan', 'IN': 'Indiana', 'NJ': 'New Jersey', 'AZ': 'Arizona', 'GU': 'Guam', 'MS': 'Mississippi', 'PR': 'Puerto Rico', 'NC': 'North Carolina', 'TX': 'Texas', 'SD': 'South Dakota', 'MP': 'Northern Mariana Islands', 'IA': 'Iowa', 'MO': 'Missouri', 'CT': 'Connecticut', 'WV': 'West Virginia', 'SC': 'South Carolina', 'LA': 'Louisiana', 'KS': 'Kansas', 'NY': 'New York', 'NE': 'Nebraska', 'OK': 'Oklahoma', 'FL': 'Florida', 'CA': 'California', 'CO': 'Colorado', 'PA': 'Pennsylvania', 'DE': 'Delaware', 'NM': 'New Mexico', 'RI': 'Rhode Island', 'MN': 'Minnesota', 'VI': 'Virgin Islands', 'NH': 'New Hampshire', 'MA': 'Massachusetts', 'GA': 'Georgia', 'ND': 'North Dakota', 'VA': 'Virginia'}
        self.university_towns = self.get_list_of_university_towns(first_dataset)


    # This method import and clean the data from Wikipedia page on college towns in the US
    # We create a DataFrame of towns and the states
    def get_list_of_university_towns(self, fileName):
        ut = pd.read_table('university_towns.txt')
        df_utowns = pd.DataFrame(ut)
        df_utowns['State'] = '0'
        df_utowns['RegionName'] = '0'
        df_utowns = df_utowns.set_index('Alabama[edit]')
        current_state = df_utowns.index.name
        for town in df_utowns.index:
            if '[edit]' in town:
                current_state = town
            else:
                df_utowns['State'].loc[town] = current_state
                df_utowns['RegionName'].loc[town] = town
        df_utowns = df_utowns.reset_index()
        df = df_utowns[(df_utowns['State'] != '0')]
        df = (df[['State', 'RegionName']])
        df['State'] = df['State'].replace('\s*\[.*', '', regex=True)
        df['RegionName'] = df['RegionName'].replace('\s*\(.*', '', regex=True)
        #print(df)
        return df
    

    def read_gdp(self, fileName):
        GDPs = pd.read_excel(fileName, skiprows=7)
        df = GDPs[['Unnamed: 4', 'Unnamed: 6']]
        df = df[(df['Unnamed: 4'] >= '2000q1')].dropna()
        df = df.reset_index().drop('index', axis=1)
        df = (df.rename(columns={'Unnamed: 4': 'YQuarters', 'Unnamed: 6':'GDP'}))
        return df

    def get_recession_start(self):
        '''Returns the year and quarter of the recession start time as a 
        string value in a format such as 2005q3'''
        df = self.read_gdp(self.second_dataset)
        df['diff'] = 0
        count = 0
        rec_start = 0
        for i in range(1, len(df.index)):
            df['diff'].iloc[i] = (df['GDP'].iloc[i]-df['GDP'].iloc[i-1])
            if df['diff'].iloc[i] < 0:
                count = count+1
            else:
                count = 0
            if count == 2:
                rec_start = i-2
        return df['YQuarters'].iloc[rec_start]

    def get_recession_end(self):
        '''Returns the year and quarter of the recession end time as a 
        string value in a format such as 2005q3'''
        
        start = self.get_recession_start()
        df = self.read_gdp(self.second_dataset)
        df['diff'] = 0
        index_start = df[(df['YQuarters'] == start)].index[0]
        count = 0
        for i in range(index_start, len(df.index)):
            df['diff'].iloc[i] = (df['GDP'].iloc[i]-df['GDP'].iloc[i-1])
            if df['diff'].iloc[i] > 0:
                count = count+1
            else:
                count = 0
            if count == 2:
                rec_end = i
                break   
        return df['YQuarters'].iloc[rec_end]


    def get_recession_bottom(self):
        '''Returns the year and quarter of the recession bottom time as a 
        string value in a format such as 2005q3'''
        start = self.get_recession_start()
        end = self.get_recession_end()
        df = self.read_gdp(self.second_dataset)
        index_start = df[(df['YQuarters'] == start)].index[0]
        index_end = df[(df['YQuarters'] == end)].index[0]
        
        recession = df['GDP'][index_start:index_end+1]
        bottom = np.min(recession)
        #print(recession)
        #print(bottom)
        rec_bottom = df[(df['GDP'] == bottom)].index[0]
        return df['YQuarters'].iloc[rec_bottom]
