import pandas as pd
import numpy as np
import scipy.stats as stats

# Show the entire rows and columns
desired_width = 1000
pd.set_option('display.width', 1000)
np.set_printoptions(linewidth=1000)
pd.set_option('display.max_columns', 10)

states = {'OH': 'Ohio', 'KY': 'Kentucky', 'AS': 'American Samoa', 'NV': 'Nevada', 'WY': 'Wyoming', 'NA': 'National',
          'AL': 'Alabama', 'MD': 'Maryland', 'AK': 'Alaska', 'UT': 'Utah', 'OR': 'Oregon', 'MT': 'Montana',
          'IL': 'Illinois', 'TN': 'Tennessee', 'DC': 'District of Columbia', 'VT': 'Vermont', 'ID': 'Idaho',
          'AR': 'Arkansas', 'ME': 'Maine', 'WA': 'Washington', 'HI': 'Hawaii', 'WI': 'Wisconsin', 'MI': 'Michigan',
          'IN': 'Indiana', 'NJ': 'New Jersey', 'AZ': 'Arizona', 'GU': 'Guam', 'MS': 'Mississippi',
          'PR': 'Puerto Rico', 'NC': 'North Carolina', 'TX': 'Texas', 'SD': 'South Dakota',
          'MP': 'Northern Mariana Islands', 'IA': 'Iowa', 'MO': 'Missouri', 'CT': 'Connecticut',
          'WV': 'West Virginia', 'SC': 'South Carolina', 'LA': 'Louisiana', 'KS': 'Kansas', 'NY': 'New York',
          'NE': 'Nebraska', 'OK': 'Oklahoma', 'FL': 'Florida', 'CA': 'California', 'CO': 'Colorado',
          'PA': 'Pennsylvania', 'DE': 'Delaware', 'NM': 'New Mexico', 'RI': 'Rhode Island', 'MN': 'Minnesota',
          'VI': 'Virgin Islands', 'NH': 'New Hampshire', 'MA': 'Massachusetts', 'GA': 'Georgia',
          'ND': 'North Dakota', 'VA': 'Virginia'}


# Data frame of towns well formatted
def get_list_of_university_towns():

    # Load university towns data
    data = pd.read_csv('C:/PythonAssignments/university_towns.txt', sep='\n', header=None, engine='python')
    university_towns = pd.DataFrame(columns=['State', 'RegionName'])
    # Separate data into 2 columns: states and region names
    i = 0
    k = 0
    while i < len(data):
        j = i + 1
        while not (not (j < len(data)) or ('[edit]' in str(data.iloc[j]))):
            university_towns.loc[k] = [data.loc[i].values[0]] + [data.loc[j].values[0]]
            j = j + 1
            k = k + 1
        i = j
    # Data cleaning
    university_towns['State'] = university_towns['State'].str.replace(r'\[.*', '')
    university_towns['State'] = university_towns.State.replace(' ', '')
    university_towns['RegionName'] = university_towns['RegionName'].str.replace(r'\(.*', '')
    university_towns['RegionName'] = university_towns.RegionName.replace(' ', '')

    return university_towns


# Recession start time
def get_recession_start():
    gdp = pd.ExcelFile('C:/PythonAssignments/gdplev.xls').parse('Sheet1')
    gdp = gdp.iloc[219:286][['Unnamed: 4', 'Unnamed: 6']].copy().reset_index(drop=True)
    for i in range(len(gdp) - 1):
        if (gdp.iloc[i - 2, 1] > gdp.iloc[i - 1, 1]) and (gdp.iloc[i - 1, 1] > gdp.iloc[i, 1]):
            recession_quarter = gdp.iloc[i - 3, 0]
    return recession_quarter


# Recession end time
def get_recession_end():
    gdp = pd.ExcelFile('C:/PythonAssignments/gdplev.xls').parse('Sheet1')
    gdp = gdp.iloc[219:286][['Unnamed: 4', 'Unnamed: 6']].copy()
    start = get_recession_start()
    start_index = gdp[gdp['Unnamed: 4'] == start].index.tolist()[0]
    gdp = gdp.loc[start_index:]
    for i in range(len(gdp)):
        if (gdp.iloc[i - 2, 1] < gdp.iloc[i - 1, 1]) and (gdp.iloc[i - 1, 1] < gdp.iloc[i, 1]):
            return gdp.iloc[i, 0]


# Recession bottom
def get_recession_bottom():
    gdp = pd.ExcelFile('C:/PythonAssignments/gdplev.xls').parse('Sheet1')
    gdp = gdp.iloc[219:286][['Unnamed: 4', 'Unnamed: 6']].copy()

    start = get_recession_start()
    start_index = gdp[gdp['Unnamed: 4'] == start].index.tolist()[0]

    end = get_recession_end()
    end_index = gdp[gdp['Unnamed: 4'] == end].index.tolist()[0]

    gdp = gdp.loc[start_index: end_index + 1]
    bottom = gdp['Unnamed: 6'].min()
    bottom_index = gdp[gdp['Unnamed: 6'] == bottom].index.tolist()[0]
    return gdp.loc[bottom_index][0]


# Housing data format to quarters
def convert_housing_data_to_quarters():

    # Load data and select the required data
    housing_data = pd.read_csv('C:/PythonAssignments/City_Zhvi_AllHomes.csv')
    housing_data = housing_data.replace({'State': states})
    housing_data.set_index(['State', 'RegionName'], inplace=True)
    housing_data = housing_data.loc[:, '2000-01': '2016-08']

    # Format data by quarter
    housing_data_by_quarter = pd.DataFrame(index=housing_data.index)
    nbRow, nbCol = housing_data.shape
    i = 0
    while i < nbCol:

        # Find the quarter
        if housing_data.columns[i][5:7] in ['01', '02', '03']:
            quarter = '1'
        elif housing_data.columns[i][5:7] in ['04', '05', '06']:
            quarter = '2'
        elif housing_data.columns[i][5:7] in ['07', '08', '09']:
            quarter = '3'
        else:
            quarter = '4'

        # Fill the new data frame
        labelName = housing_data.columns[i][0:4] + 'q' + quarter
        if i + 2 < nbCol:
            housing_data_by_quarter[labelName] = housing_data.iloc[:, i: i + 3].mean(axis=1)
            i = i + 3
        else:
            housing_data_by_quarter[labelName] = housing_data.iloc[:, i:].mean()
            i = i + 2
    return housing_data_by_quarter


def run_ttest():

    # Get the house prices between the recession start and the recession bottom
    recession_start = get_recession_start()
    recession_bottom = get_recession_bottom()
    housing_data = convert_housing_data_to_quarters()
    housing_data['price_ratio'] = np.nan_to_num(housing_data[recession_start] / housing_data[recession_bottom])
    housing_data = housing_data[[recession_start, recession_bottom, 'price_ratio']].reset_index()
    univ_city_list = get_list_of_university_towns()

    # Group towns into university towns and non university towns
    univ_city_list['University'] = 'Yes'
    houses = housing_data.join(univ_city_list['University'])
    univ_city = houses.loc[houses['University'] == 'Yes']
    non_univ_city = houses.loc[houses['University'].isnull()]

    # T-test for comparing the university town values to the non-university towns values
    st, p = stats.ttest_ind(univ_city['price_ratio'], non_univ_city['price_ratio'])
    # Test if groups are different
    different = False
    if p < 0.01:
        different = True

    # Check which group is better
    if univ_city['price_ratio'].mean() > non_univ_city['price_ratio'].mean():
        better = 'university town'
    else:
        better = 'non university town'

    return different, p, better


print(run_ttest())
