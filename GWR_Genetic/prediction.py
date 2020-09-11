import geopandas as gpd
import pandas as pd
import sys, logging
from RunningGA import GetFile, OpenCSVFile, OpenShpFile


if __name__ =="__main__":
    logging.warning("Please make sure that the variables you are using to predict on (i.e. Future)\nis in the same order as you see in GWRmodel.csv after the column \"X.Intercept\" !!!\n ")
    future_req = "Please select your .csv that has your FUTURE independent variables (demographics)"
    future_err = "No Future file selected, exiting ..."
    future_file = GetFile(future_req,future_err)
    shp_req = "Please select your shp file that contains the data set"
    shp_err = "No shp file selected, existing..."
    shp_file = GetFile(shp_req,shp_err)
    future = OpenCSVFile(future_file)
    shp = OpenShpFile(shp_file)
    #Reads in the last output from R script
    gwr_model = pd.read_csv("./GWRmodel.csv")

    userInput = input("Enter the year of the prediction: ")

    try:
        year = int(userInput)
    except ValueError:
        print("Error: Input must be an integer")
        sys.exit(0)

    x_var = []
    #Creates list of all the future variables
    for x in future[0]:
        x_var.append(str(x))
    #Grabs the taz information in the shp file
    taz_location = shp[['TAZ']]
    #Grabs all the future values for each future variable in the shp file.
    future_X = shp[x_var]

   
    shrink_model = gwr_model.iloc[:,3:(future_X.shape[1]+3)].copy()
    x_intercept = gwr_model.iloc[:,2].copy()

    #multiplies all columns in shrink_model with future_X
    slope_df = pd.DataFrame(shrink_model.values*future_X.values, columns=future_X.columns, index=future_X.index)

    #concatenate the newly calculated dataframe with the x-intercepts from x_intercept
    final_frame = pd.concat([slope_df, x_intercept], axis=1)

    #Sums up each row to create the prediction number, this number represents the number of call per row
    final_frame['Prediction'] = final_frame.sum(axis=1)
    
    #Concatenate the prediction column with the taz column 
    result = pd.concat([taz_location,final_frame['Prediction']],axis=1)

    #Concatenate the Year provided to the dataframe with taz, and prediction
    result['Year'] = year

    #Export to CSV file
    filename = str(year)+'_'+"prediction.csv"
    result.to_csv(filename, sep=',', encoding='utf-8', index=False)

    #Prints the total of the Prediction column
    print("Total predicted calls:", result['Prediction'].sum())