# Utility functions which are case specific
import re

import pandas as pd
import numpy as np


def characterise_metal_acid_titrations(data: pd.DataFrame) -> pd.DataFrame:
    """
    Name of data parsed (from UV/Vis) will have a suffix indicating what kind of titrant was added so data can be
    assoc. with the correct titrant.
    Here that data will be characterised based upon the suffix provided and a new column with titrant added.

    :param data: dataframe of data from instrument
    :return: original dataframe with titrant column added
    """
    data['volume_change'] = data.titrant.apply(lambda x: float(re.match('[0-9.]+', x).group()))
    data.titrant = data.titrant.apply(lambda x: re.search('[a-z]+', x).group() if re.search('[a-z]+', x) else 'm')

    return data


def merge_data_titration_params(data: pd.DataFrame, dict_titrations_exps: dict) -> pd.DataFrame:
    """
    Data parsed from instrument (UV/Vis) is merged with the parameters of the titration designed
    on volume change which should match experiment with design.

    :param data: dataframe of data from instrument
    :param dict_titrations_exps: experiment name with titration objects housing titration design
    :return: dataframe where data received from instrument is merged with titration parameters in design
    """
    data = characterise_metal_acid_titrations(data)

    list_df = []
    for exp in data.name.unique():

        # Merge titration with data of each experiment and populate concat list
        for k, v in dict_titrations_exps.items():
            if k.casefold() in exp.casefold():
                data_exp = data.loc[data.name == exp]
                for titrations in v[0]:
                    df = titrations.df_params
                    list_df.append(
                        df.loc[:, ['volume_change', 'g_h', 'guest_name', 'host_name', 'rank']] \
                            .merge(data_exp, how='inner', on=["volume_change"]))

    new_data = pd.concat(list_df, axis=0).fillna(method='bfill')

    return new_data


# TODO: Double check what exactly this returns
def track_data(df, wl):
    """
    Gets the absorbance at specified wavelength for each spectra in dataframe. Helper function for below.
    :param df: dataframe containing UV/Vis information
    :param wl: wavelength to monitor at
    :return: the absorbance
    """
    return df.loc[df['Wavelength nm.'] >= 250, 'Abs.'].max() if wl == 'max' \
        else df.loc[df['Wavelength nm.'] == wl]['Abs.'].mean()  # Mean because sometimes there is a duplicate


def tracking_df(df: pd.DataFrame, wls: list[str], exps: list[str], wl_0='max', complex_tit=True) -> dict:
    """
    Tracks difference in absorbance of each spectra with absorbance of initial at specified wavelength.
    Also can compare two different wavelengths (like MLCT and pi-pi*).
    :param df: UV/Vis data
    :param wls: list of wavelegnths to monitor at (normally MLCT)
    :param exps: experiment names
    :param wl_0: wavelength to compare with
    :param complex_tit: Boolean indicating whether complex titration is being monitored or not
    :return:
    """
    dict_df = {}
    for wl in wls:
        tracking_data = df[np.isin(df.name, exps)] \
            .groupby(['g_h', 'name', 'guest_name']) \
            .apply(lambda x: track_data(x, wl) / (track_data(x, wl_0)) if complex_tit else track_data(x, wl)) \
            .unstack(['name', 'guest_name']) \
            .apply(lambda x: x - x.loc[0])

        dict_df[str(wl)] = tracking_data

    return dict_df


def combine_track_data(data: pd.DataFrame, dict_tracking_data: dict) -> pd.DataFrame:
    """
    Combine data tracked above with original dataframe
    :param data: original dataframe containing all parameters and data from UV/Vis
    :param dict_tracking_data: result of tracking data
    :return: original dataframe with additional column of wavelengths tracked
    """
    list_track_data = []
    for wl, wl_track_data in dict_tracking_data.items():
        wl_track_data_long = wl_track_data.melt(ignore_index=False).reset_index().dropna(how='any', axis=0)
        wl_track_data_long['wl_track'] = wl
        list_track_data.append(wl_track_data_long)

    wl_track_data_long = pd.concat(list_track_data, axis=0, ignore_index=True)

    df = data.merge(wl_track_data_long,
                    on=[col for col in wl_track_data_long.columns if 'value' not in col and 'wl' not in col])
    return df
