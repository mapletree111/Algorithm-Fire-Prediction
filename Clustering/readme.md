
# Kmeans Clustering

Run a K-means clustering analysis on a .shp or .csv file. Specify features to cluster on in a comma-delimited 
text file. Features must be convertible to numeric values using pd.to_numeric. Note, this means you can
cluster on "Built Year", but not on "Built Date" because "1/1/1990" is not convertible to a numeric value.

The program assumes all rows with empty cells in the feature columns have been removed.

## Getting Started

Please see the instructions for installing dependencies in the root directory.

### Examples:

Note: you can see a list of arguments by running 
```
python27 Kmeans.py -h
```
Usages:
These commands can be used to generate the Kmeans output currently (as of 5.22.18) in the repository.
```
python27 KMeans.py ../Apartments/Apartments_Corrected.csv ../Apartments/apartment_features.txt

```
```
python27 Kmeans.py ../AssistedLivingData/AssistedLiving_ParcelDataMerged.csv ../AssistedLivingData/assisted_living_features.txt

```

## Output
The program will output three files in the directory of the input data.

###filename_kmeans
The original dataset with columns indicating the assigned labels to each sample for each run of Kmeans
Note: this will be a directory if the input file is a shapefile.

###filename_ASD
Contains a table with Average Squared Distance measurements for each run of Kmeans.

###filename_centers
Contains a table with cluster centers for each run of Kmeans.

## Author

* **Brian Wiltse** - *Initial work*

