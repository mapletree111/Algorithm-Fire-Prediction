This folder contains the contents of the GWR automation process, the Genetic algorithm implementation, as well as the prediction program.
	
Dependencies:
   -python vers 2.7
        +geopandas
         +UTM
         +Tkinter
    -R for Windows
         +spgwr
         +ggplot2
         +rlist
   
How to Install:
    Install anaconda 5.2 with python 2.7 from here:
    https://www.anaconda.com/download/
    *Note: Make sure that anaconda is included in the PATH environment variable in order to install packages correctly and for them to work with python 2.7

    Once anaconda finishes installing, run the "Anaconda Prompt" as an admin. Default location: (C:\ProgramData\Microsoft\Windows\Start Menu\Programs\Anaconda2 (64-bit))
    If you see the word "(base)" before C:\WINDOWS\system32> in your command prompt, type in "deactivate" and press enter.
    Now we can install the packages required:
    Copy and past the following commands into your Anaconda Prompt to install the required packages.
        Geopandas:
            conda install -c conda-forge geopandas
        
        Tkinter:
            conda install -c anaconda tk
        
        UTM:
            conda install -c conda-forge utm


    Install R 3.5.0 for Windows from here:
    https://cran.r-project.org/bin/windows/base/
    *Note: Make sure to also include the "C:\Program Files\R\R-3.5.0\bin" into your PATH environment to be able to use R packages

    Run the "R.exe" command line prompt as admin. Default location: (C:\Program Files\R\R-3.5.0\bin)
    Copy and paste the following commands to install the needed packages:
        Spgwr:
            install.packages("spgwr")
        
        ggplot2:
            install.packages("ggplot2")

        rlist:
            install.packages("rlist")

    *Note: You may have to follow the prompt during each installation and select your specific region to download the package from. I download my packages from the Oregon Site in the US.

How to run:
    RunningGA.py:
        python RunningGA.py
        *Note: This will prompt you to select 3 files.
            -The first file should include all your independent variables you want to investigate with the Genetic algorithm.
            -The second file should contain all of the call codes variables you want to compare teh independent varaible against.
            -The third file should contain the *.shp file that has the table which contains the variables from the first two files.
        Output: 
            temp_code_#.csv - A csv file that contains 2 columns. The first column is the alterned names for each independent variables kept by the GA. The second column is the codes associated with each name inside the *.shp file.
    
    GWR_Python.py:
        python GWR_Python.py <path_to_shp_file> <path_to_temp_code_#_csv>
        *Note: GWR_Python.py will need to be run with 2 command line arguments. 
            -The first is the path to your original *.shp file, similar to the one use in RunningGA.py.
            -The second argument contains the path to your temp_code_#.csv, which should have been the output of RunningGA.py
        Output:
            GWRmodel.csv - This is the model that will use in prediction.py to find the predicted number of calls.
            qGlobalR2.csv - This will contain the R-squared value of the GWR (Not R-squared adjusted). R-squared adjusted will be calculated and output on the screen.
            temp.csv - Temporary file that contains all variables and values that will be used by the lm_gwr.R script.
    
    prediction.py:
        python prediction.py
        *Note: This will prompt you to select 2 files.
            -The first file should be a csv with one column that contains the variables of the "future" variables that is in the same order as the past. (See GWRmodel.csv after the "X.intercept" for the order of past variable)
            -The scond file should be the *.shp file that contains the entire dataset with the future variables inside. (Make sure that the dataset also include the Taz number).
        Input:
            The program will ask for the year it is predicting on which the user must enter during execution.
        Output:
            year_prediction.csv - This csv contains 3 columns, a Taz, Prediction, and Year column. The prediction is the number of calls that happen within each Taz. The year is from the user input.
            
