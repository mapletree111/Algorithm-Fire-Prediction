
# Data Ingestion and Feature Extraction

This tool obtains data and extracts features for an arbitrary county/city in the United States.
Note that as of this writing (May 9, 2018) the tool only guarantees full functionality for 
Charlotte, NC. However, one can obtain Census demographics for any county in the U.S.

If you are unsure of the state or county code you need to use, you can get a list of states
with their codes with 
```aidl
ListStateCodes.py
```

Once you know the state code, you can find the county codes with:
```aidl
ListCountyCodes.py <state_code>
```

## Getting Started

To use this module, you will need the following libraries:

### Anaconda with Python 2.7
Though highly recommended, you can also run this module without Anaconda.
If you choose not to use Anaconda and you are on a Windows system, you may
find this blog helpful: http://geoffboeing.com/2014/09/using-geopandas-windows/
### rtree
Optional, but improves performance of some modules.
### Geopandas
Note that Geopandas has its own dependencies.
They should install automatically with Geopandas, if using Anaconda, but they will not be 
automatically installed with some configurations.
Please see the Geopandas webite for help, if you have problems.
Geopandas - http://geopandas.org/install.html 
### scikit-learn
scikit-learn also has dependencies in common with Geopandas.
See http://scikit-learn.org/stable/install.html for troubleshooting, if necessary.

### Examples:

Note: you can see a list of arguments by running 
```
python27 Main.py -h
```

The following are some example usages. Note that running
```
python27 src/Main.py 37 119 2012 
```
will obtain census demographics for Charlotte, NC for 2012;
however attempting to obtain the TAZ data for any other
year will not work because we have only been provided with
2015 TAZ data. At this time, only Census demographics are supported 
for years other than 2015. In addition, other Census state and
county codes are supported for Census demographics only.

Other examples:

Obtain a shapefile with demographics of Charlotte, NC with TAZ data:
```
python27 src/Main.py 37 119 2015 -t
```

Obtain a shapefile with demographics of Charlotte, NC with TAZ data 
and incident counts for each TAZ:
```
python27 src/Main.py 37 119 2015 -t -p Charlotte
```

## Running the tests

To test this tool:
 1. navigate to test/
 2. run python -m unittest discover


This will run a suite of tests to test each module in the pipeline
found in src/Main.py.

## Directory structure
The current version of the data ingestion tool utilizes locally stored data. 
Data has been stored in a directory structure for convenient access.
The folders contained in this module are organized as follows:

### CensusSF
Can be obtained with:
```aidl
Names.get_censusSF(state_code, level):
```
Contains state shapefiles from the U.S. Census. 
Naming follows Census convention. 
For example, North Carolina's shapefile broken up by tract is in tl_2017_37_tract 
(North Carolina's state code is 37).

### IncData
Can be obtained with:
```aidl
Names.get_inc_log_folder(state_code, city_name)
```
Contains incident logs for counting incidents.
Incident logs should be stored in the following manner:
IncData
--State
----City
------Yearly
State should match exactly the state name as it appears in src/CensusDicts.py.

### MATFiles
NOTE: The superMAT module ended up not being used in the final product.
It remains here in case it is useful for future development.

MAT files can be obtained with:
```aidl
Names.get_super_mat(state_code, city_name)
```
Contains Master Address Tables for a given city.
Files are stored under:
MATFiles
--State
----City

### ResponseSF
Can be obtained with:
```aidl
Names.get_response_zone_shapefile(state_code, city_name)
```
Contains shapefile of the outline of the response area.
Response shapefiles should be stored in the following manner:
IncData
--State
----City
State should match exactly the state name as it appears in src/CensusDicts.py.


### TazSF
Can be obtained with:
```aidl
Names.get_taz_shapefile(state_code, county_code, year)
```
Contains shapefile containing TAZ data.
TAZ shapefiles should be stored in the following manner:
IncData
--State
----City
State and county should match exactly the state name as it appears in src/CensusDicts.py.

### ZoningSF
Can be obtained with:
```aidl
Names.get_zoning_shapefile(state_code, county_code, year)
```
Contains shapefile containing TAZ data.
TAZ shapefiles should be stored in the following manner:
IncData
--State
----City
State and county should match exactly the state name as it appears in src/CensusDicts.py.

## Author

* **Brian Wiltse** - *Initial work*

