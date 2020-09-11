import geopandas as gpd
import pandas as pd
import subprocess
import utm
import sys

def execute(shp,temp):
    categories = pd.read_csv(temp)
    cat_dict = categories.to_dict()
    num_var = categories.shape[0]-3
    world = gpd.read_file(shp)

    num = 0
    for key, value in cat_dict['Category'].items():
        if 'Calls' == value:
            break
        num = num+1

    count = 0
    listcall = []
    for w in world[cat_dict['Code'][num]]:
        listcall.append(w)
        count=count+1

    num = 0
    listlat = []
    listlong = []
    for key, value in cat_dict['Category'].items():
        if 'Longtitude' == value:
            break
        num = num+1
    for v in world[cat_dict['Code'][num]]:
        listlong.append(float(v))
    num = 0
    for key, value in cat_dict['Category'].items():
        if 'Latitude' == value:
            break
        num = num+1
    for u in world[cat_dict['Code'][num]]:
        listlat.append(float(u))

    xcords = []
    ycords = []
    for cord in range (0, len(listlat)):
        xcords.append(utm.from_latlon(listlat[cord], listlong[cord])[0])
        ycords.append(utm.from_latlon(listlat[cord], listlong[cord])[1])


    num = 0
    listvar = []
    listname = []
    for key, value in cat_dict['Category'].items():
        if value != 'Latitude' and value != 'Longtitude' and value != 'Calls':
            listname.append(value)
            listvar.append(cat_dict['Code'][num])
        num = num+1

    #Creating a big list to contain all the values that will be found
    primarylist = []
    for key in listvar:
        sublist = []
        for x in world[key]:
            sublist.append(x)
        primarylist.append(sublist)

    #Creates a dataframe using pandas with the already calculated values
    df = pd.DataFrame({'Calls':listcall, 'Latitude':listlat, 'Longtitude':listlong, 'x':xcords, 'y':ycords})
    num = 0
    for name in listname:
        df.insert(0,name,primarylist[num])
        num=num+1
    df.to_csv('temp.csv', sep=',')



    #Run R Script as a subprocess
    #R_script = 'example_script.R'
    R_script = 'lm_gwr.R'
    cmd = ['Rscript', R_script] + listname
    x = subprocess.check_output(cmd, universal_newlines=True)
    print(x) #Checks on the process of the R script if anything prints out

    #Open the output file from the R sqaure script and calculate adjusted R-squared value
    qp = "qGlobalR2.csv"
    r2 = pd.read_csv(qp)
    for x in r2['x']:
        r2_val = float(x)

    #Calculate adjusted r-squared value using formula
    adjR2 = 1-((1-r2_val)*(count-1)/(count-num_var-1))
    print("GWR R-squared: ", r2_val)
    print("GWR adjusted R-squared: ", adjR2)

print("Command line argument structure:\n First: Contains path to shp file\n Second: Contains path to temp_code_#.csv (output from RunningGA.py)")
if(len(sys.argv) != 3):
    sys.exit(0)
else:
    execute(sys.argv[1], sys.argv[2])