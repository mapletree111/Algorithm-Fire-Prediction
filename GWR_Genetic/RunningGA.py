import pandas as pd
import fiona
import numpy as np
import geopandas as gpd
import sys, os
from string import maketrans
from Tkinter import Tk
import tkFileDialog as filedialog
#from Tkinter.filedialog import askopenfilename
from GeneticAlgorithm import FeatureSelectionGeneticAlgorithm
from VIF import ReduceVIF
from sklearn import linear_model

def GetFile(request,err):
    Tk().withdraw()
    print(request)
    file_path = filedialog.askopenfilename()
    if not file_path:
        print(err)
        sys.exit(0)
    return file_path

def OpenCSVFile(file_path):
    try:
        file = pd.read_csv(file_path, header=None)
    except pd.errors.ParserError:
        print("Error: Could not find the file "+str(file_path))
        sys.exit(1)
    return file


def OpenShpFile(file_path):
    try:
        shp = gpd.read_file(file_path)
    except fiona.errors.FionaValueError:
        print("Error: Could not find the file "+str(file_path))
        sys.exit(1)
    return shp

if __name__ == "__main__":
    independent_req = "Please select your .csv that has your independent variables (demographics)"
    independent_err = "No independent csv file selected, exiting..."
    dependent_req = "Please select your .csv that has your dependent variables (Calls)"
    dependent_err = "No dependent csv file selected, exiting..."
    shp_req = "Please select your shp file that contains the data set"
    shp_err = "No shp file selected, existing..."
    independent_file = GetFile(independent_req,independent_err)
    dependent_file = GetFile(dependent_req,dependent_err)
    shp_file = GetFile(shp_req,shp_err)

    print("Independent file: ", independent_file)
    print("Dependent file: ", dependent_file)
    print("Shp file: ", shp_file)

    independent = OpenCSVFile(independent_file)
    dependent = OpenCSVFile(dependent_file)
    shp = OpenShpFile(shp_file)

    reg = linear_model.LinearRegression()
    ga = FeatureSelectionGeneticAlgorithm()
    x_var = []
    y_var = []

    for x in independent[0]:
        x_var.append(str(x))

    for y in dependent[0]:
        y_var.append(str(y))
    X = shp[x_var]
    transformer = ReduceVIF()

    for call in range(0, len(y_var)):
        Y = shp[[y_var[call]]]
        X = transformer.fit_transform(X,Y)
        ga.fit(reg,'regression',X,Y,True,False)
        features, variable_names = ga.results(X)
        #ga.plot_progress()
        print(features)
        print(variable_names)
        print(len(variable_names))

    #Change to CENTLAT and CENTLONG when using taz files
        Coords = ['CENTLAT', 'CENTLONG']
        #Coords = ['INTPTLAT', 'INTPTLON']
    #Replace all symbol in variable names with comma
        #SYMBOLS = '{}()[].,:;+-*/&|<>=~$_\ !@#%^'
        #table = maketrans(",",SYMBOLS)
        stlist = [''.join(e for e in item if e.isalnum()) for item in variable_names]
        cat_list = ["c" + element for element in stlist]

        f_col = ['Calls','Latitude','Longtitude']
        f_col.extend(cat_list)


        codes = list(Y.columns.values)
        codes.extend(Coords)
        codes.extend(variable_names)

        temp_file = "temp_code_"+str(call)+".csv"

        cat_code = pd.DataFrame({'Category':f_col,'Code':codes})
        cat_code.to_csv(temp_file, sep=',', encoding='utf-8', index=False)
        #os.remove("temp_code.csv")
        #os.remove("qGlobalR2.csv")
        #os.remove("temp.csv")

