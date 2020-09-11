def sum_two_columns(a, b):
    """
    Sums two (Geo)Series (columns in a DataFrame)
    :param a: A Series (DataFrame column) to combine
    :param b: Another Series to combine
    :return: A combined column with summed elements
    """
    return a.combine(b, lambda s1, s2: s1 + s2)


def sum_features(df, col_dict):
    """
    Creates columns that represent a sum of existing columns in a given DataFrame.
    :param df: Dataframe to modify
    :param col_dict: Dict mapping {New_column: [old_col1, old_col2, ...]
    :return: Dataframe with old columns summed into new columns
    """
    for new_col, lst in col_dict.iteritems():
        df[new_col] = reduce(sum_two_columns, [df[col] for col in lst])

    # Drop lower-level features
    df.drop([el for lst in col_dict.itervalues() for el in lst], axis=1, inplace=True)

    return df
