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


    # This method imports and cleans the data from Wikipedia page on college towns in the US
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
    

    # This method imports and cleans the data from the Bureau of Economic Analysis, US Department of Commerce, and describes
    # the GDP over time of the United States in current dollars in quarterly intervals
    def read_gdp(self, fileName):
        GDPs = pd.read_excel(fileName, skiprows=7)
        df = GDPs[['Unnamed: 4', 'Unnamed: 6']]
        df = df[(df['Unnamed: 4'] >= '2000q1')].dropna()
        df = df.reset_index().drop('index', axis=1)
        df = (df.rename(columns={'Unnamed: 4': 'YQuarters', 'Unnamed: 6':'GDP'}))
        return df

    #This method converts the housing data to quarters and returns it as mean 
    #values in a dataframe.
    def convert_housing_data_to_quarters(self, fileName):
        housing = pd.read_csv(fileName)
        housing = housing.set_index(['State','RegionName'])
        
        #we delete the first 4 columns, then other 45 columns because 
        #from April 1996 to January 2000 there are 45 months
        housing = housing.drop(housing.columns[:49], axis=1)
        housing = housing.reset_index()
        df = housing[['State', 'RegionName']]
        
        #print(df)
        for i in range (2000, 2016):
            #print(housing[[str(i)+'-01',str(i)+'-02',str(i)+'-03']])
            df[str(i)+'q1'] = housing[[str(i)+'-01',str(i)+'-02',str(i)+'-03']].mean(axis=1)
            df[str(i)+'q2'] = housing[[str(i)+'-04',str(i)+'-05',str(i)+'-06']].mean(axis=1)
            df[str(i)+'q3'] = housing[[str(i)+'-07',str(i)+'-08',str(i)+'-09']].mean(axis=1)
            df[str(i)+'q4'] = housing[[str(i)+'-10',str(i)+'-11',str(i)+'-12']].mean(axis=1)
        
        i=2016
        df[str(i)+'q1'] = housing[[str(i)+'-01',str(i)+'-02',str(i)+'-03']].mean(axis=1)
        df[str(i)+'q2'] = housing[[str(i)+'-04',str(i)+'-05',str(i)+'-06']].mean(axis=1)
        df[str(i)+'q3'] = housing[[str(i)+'-07',str(i)+'-08']].mean(axis=1)
        
        df_states = pd.DataFrame(list(states.items()), columns=['ST','StateName'])
            
        merged = pd.merge(df, df_states, how='inner', left_on='State', right_on='ST')
        merged = merged.set_index(['StateName','RegionName'])
        merged = merged.drop(merged.columns[[0,68]], axis=1)   
        return merged


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



    '''First creates new data showing the decline or growth of housing prices
    between the recession start and the recession bottom. Then runs a ttest
    comparing the university town values to the non-university towns values, 
    return whether the alternative hypothesis (that the two groups are the same)
    is true or not as well as the p-value of the confidence. 
    
    Return the tuple (different, p, better) where different=True if the t-test is
    True at a p<0.01 (we reject the null hypothesis), or different=False if 
    otherwise (we cannot reject the null hypothesis). The variable p should
    be equal to the exact p value returned from scipy.stats.ttest_ind(). The
    value for better should be either "university town" or "non-university town"
    depending on which has a lower mean price ratio (which is equivilent to a
    reduced market loss).'''
    def run_ttest(self):
        start = self.get_recession_start() 
        bottom = self.get_recession_bottom() 
        end = self.get_recession_end() 
        hdf = self.convert_housing_data_to_quarters(self.third_dataset)
        uni_towns= self.get_list_of_university_towns()
        #print(uni_towns)
        gdp = read_gdp()
        index_start = gdp[(gdp['YQuarters'] == start)].index[0]
        qrt_bfr_rec_start = gdp['YQuarters'].iloc[(index_start-1)]
        
        hdf['PriceRatio'] = hdf[qrt_bfr_rec_start].div(hdf[bottom])
        
        # We separate the university towns from non-university towns,
        # using the dictionary for the states
        df_states = pd.DataFrame(list(states.items()), columns=['ST','State'])
            
        uni_towns_with_state = pd.merge(uni_towns, df_states, how='inner', left_on='State', right_on='State')
        tuple_list = []
        for i in range(len(uni_towns_with_state['State'])):
            tuple_list.append((uni_towns_with_state['State'].iloc[i], uni_towns_with_state['RegionName'].iloc[i]))
        
        university_towns = hdf.loc[tuple_list]
        non_university_towns = hdf.loc[~hdf.index.isin(tuple_list)]
        pvalue = ttest_ind(university_towns['PriceRatio'].dropna(),non_university_towns['PriceRatio'].dropna())    
        different = pvalue.pvalue < 0.01
        better = ''
        if non_university_towns['PriceRatio'].mean() < university_towns['PriceRatio'].mean():
            better="non-university town"
        else:
            better='university town'
        tuple_result = (different, pvalue.pvalue, better)
        return tuple_result