import argparse
from os.path import splitext

import geopandas as gpd
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler


"""
Runs K-means clustering on CSV or SHP file. Use the column labels listed in feature_file.
Values in columns must be able to be converted to numeric value (Instead of building date, use building year)

Usage:
python2 K-means.py data_file feature_file
 
"""

CSV = '.csv'
SHP = '.shp'


def get_feature_cols(feature_file):
    with open(feature_file, 'r') as feat_file:
        feature_cols = feat_file.readline().split(',')
        feature_cols = [x.strip() for x in feature_cols]
    return feature_cols


def write_to_file(df, file_type, feature_cols, file_name):
    # Rename columns so e.g. Residential 4 shows up as Res4
    # (rather than being trimmed in shapefile and given arbitrary numbering)
    number_cols = [x for x in feature_cols if any(char.isdigit() for char in x)]
    rename_cols = {x: (x[:3] + x[-1]) for x in number_cols}
    df.rename(columns=rename_cols, inplace=True)

    if file_type == SHP:
        df.to_file(file_name + "_kmeans.csv")
    elif file_type == CSV:
        df.to_csv(file_name + "_kmeans.csv")
    else:
        raise TypeError("Unknown dataframe type: {}".format(file_type))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('file_name', type=str,
                        help="The input data file. Must be .shp or .csv")
    parser.add_argument('feature_file', type=str,
                        help="The file containing the desired feature columns, separated by commas")

    args = parser.parse_args()
    full_file_path = args.file_name
    feature_file = args.feature_file

    suffix = '_B'
    file_name, file_type = splitext(full_file_path)

    if file_type == CSV:
        full_dataset = pd.read_csv(full_file_path)
    elif file_type == SHP:
        full_dataset = gpd.read_file(full_file_path)
    else:
        raise TypeError("Incorrect file type: {}. Only .csv or .shp accepted".format(file_type))

    feature_cols = get_feature_cols(feature_file)

    # Create a copy of the original dataset
    plot_data = full_dataset.copy(deep=True)

    # dataset is the subset of features to use in K-means.
    dataset = pd.DataFrame(full_dataset[feature_cols])
    print("Running Kmeans with the following variables\n{}".format(dataset.columns.values.tolist()))
    # Fill any NaN values with 0
    dataset.fillna(0, inplace=True)
    # Convert all remaining values to numeric
    dataset = dataset.apply(pd.to_numeric)

    # Standardize data
    scaler = StandardScaler()
    scaled_data = scaler.fit_transform(dataset)

    # ------------------------- Kmeans -------------------------

    clusters = range(4, 11)
    km_scores = {}
    km_cluster_centers = {}
    for n_clusters in clusters:
        print ('Running K-means with {} clusters'.format(n_clusters))
        # Fix the random state (original placement of clusters)
        # so we get consistent results
        kmeans = KMeans(n_clusters=n_clusters, random_state=1010)
        kmeans.fit(scaled_data)
        kmeans_label = 'km{}'.format(n_clusters)
        plot_data[kmeans_label] = kmeans.labels_
        score = -kmeans.score(scaled_data)
        km_scores[n_clusters] = score
        print('\tKmeans score: {}'.format(score))
        km_cluster_centers[n_clusters] = {
            num + 1: {feat: center for feat, center in zip(feature_cols, feat_list.tolist())}
            for num, feat_list in enumerate(scaler.inverse_transform(kmeans.cluster_centers_))}

    # ------------------------- PCA to Kmeans -------------------------
    # Borrows heavily from:
    # https://towardsdatascience.com/pca-using-python-scikit-learn-e653f8989e60

    # Run PCA
    orig_n_features = len(dataset.columns.values)
    explained_variances = [0.9, 0.8, 0.5, 0.4]
    components = []
    km_pca_scores = {}
    for explained_variance in explained_variances:
        # Run PCA
        pca = PCA(explained_variance, random_state=1010)
        principle_cmpnts = pca.fit_transform(scaled_data)
        num_cpnts = pca.n_components_
        components.append(num_cpnts)
        print('PCA with {} explained variance reduced number of features from {} to {}'
              .format(explained_variance, orig_n_features, num_cpnts))
        km_pca_scores[explained_variance] = {}
        for n_clusters in clusters:
            # Run K-means
            kmeans_pca = KMeans(n_clusters=n_clusters, random_state=1010)
            print ('\tRunning K-means with {} clusters'.format(n_clusters))
            kmeans_pca.fit(principle_cmpnts)
            kmeans_pca_label = 'km{}_pc{}' \
                .format(n_clusters, str(explained_variance)[1:])

            # Add labels to dataframe
            plot_data[kmeans_pca_label] = kmeans_pca.labels_
            km_pca_scores[explained_variance][n_clusters] = -kmeans_pca.score(principle_cmpnts)
            print('\t\tKmeans score: {}'.format(km_pca_scores[explained_variance][n_clusters]))

    # Build average squared distance dataframe
    asd_df = pd.DataFrame.from_dict(km_scores, orient='index')
    asd_df.columns = ['No PCA']

    asd_pca_df = pd.DataFrame.from_dict(km_pca_scores)
    var_cpt = dict(zip(explained_variances, components))
    asd_pca_df.columns = map(lambda x: "PCA {} exp_var, {} cpts".format(x, var_cpt[x]), asd_pca_df.columns)
    asd_pca_df = asd_pca_df[asd_pca_df.columns[::-1]]
    asd_pca_df.index.name = "Number of Clusters"

    full_asd_df = asd_df.merge(asd_pca_df, left_index=True, right_index=True)
    full_asd_df.index.name = "Number of Clusters"
    full_asd_df.to_csv(file_name + "_ASD" + suffix + ".csv")

    # Build centroid dataframe
    centers_df = pd.DataFrame.from_dict({(i, j): km_cluster_centers[i][j]
                                         for i in km_cluster_centers
                                         for j in km_cluster_centers[i]}, orient='index')

    # Reorder columns to original fature_cols order
    centers_df = centers_df[feature_cols]

    # Give indexes more descriptive names now so sorting of cluster numbers is preserved
    first_idx = centers_df.index.get_level_values(level=0).tolist()
    second_idx = centers_df.index.get_level_values(level=1).tolist()
    first_idx_map = {x: str(x) + " Clusters" for x in first_idx}
    second_idx_map = {x: "cluster " + str(x) for x in second_idx}
    centers_df.rename(first_idx_map, level=0, inplace=True)
    centers_df.rename(second_idx_map, level=1, inplace=True)

    # Round values
    centers_df = centers_df.round(decimals=4)
    centers_df.to_csv(file_name + "_centers" + suffix + ".csv")

    write_to_file(plot_data, file_type, feature_cols, file_name)


if __name__ == '__main__':
    main()
