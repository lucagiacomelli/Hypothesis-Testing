from data import Data
import pandas as pd
import numpy as np
from scipy.stats import ttest_ind

d = Data('university_towns.txt','gdplev.xls', 'City_Zhvi_AllHomes.csv')

print(d.university_towns)
print('recession start at ' + str(d.get_recession_start()))
print('recession ends at ' + str(d.get_recession_end()))
print('recession bottom at ' + str(d.get_recession_bottom()))