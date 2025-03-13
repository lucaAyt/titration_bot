import re

import pandas as pd
import numpy as np


# Reorganise data to ensure metal and acid titrations can be distinguished
def characterise_metal_acid_titrations(data):
    data['volume_change'] = data.titrant.apply(lambda x: float(re.match('[0-9.]+', x).group()))
    # data.drop(columns=['titrant'], inplace=True)
    data.titrant = data.titrant.apply(lambda x: re.search('[a-z]+', x).group() if re.search('[a-z]+', x) else 'm')

    return data


def merge_data_titration_params(data, dict_titrations_exps):
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


# Analyse data
def track_data(df, wl): return df.loc[df['Wavelength nm.'] >= 250, 'Abs.'].max() if wl == 'max' \
    else df.loc[df['Wavelength nm.'] == wl]['Abs.'].mean()  # Mean because sometimes there is a duplicate


# Track diff with max peak !!
def tracking_df(df, wls, exps, wl_0='max', complex_tit=True):
    dict_df = {}
    for wl in wls:
        tracking_data = df[np.isin(df.name, exps)] \
            .groupby(['g_h', 'name', 'guest_name']) \
            .apply(lambda x: track_data(x, wl) / (track_data(x, wl_0)) if complex_tit else track_data(x, wl)) \
            .unstack(['name', 'guest_name']) \
            .apply(lambda x: x - x.loc[0])

        # print(tracking_data)
        # tracking_data = construct_init_follow_up_titration(tracking_data, guests) \
        #                   .dropna(how='all', axis=0) \
        #                   .apply(lambda x: x - x.loc[0])

        dict_df[str(wl)] = tracking_data

    return dict_df


def combine_track_data(data, dict_tracking_data):
    list_track_data = []
    for wl, wl_track_data in dict_tracking_data.items():
        wl_track_data_long = wl_track_data.melt(ignore_index=False).reset_index().dropna(how='any', axis=0)
        wl_track_data_long['wl_track'] = wl
        list_track_data.append(wl_track_data_long)

    wl_track_data_long = pd.concat(list_track_data, axis=0, ignore_index=True)

    df = data.merge(wl_track_data_long,
                    on=[col for col in wl_track_data_long.columns if 'value' not in col and 'wl' not in col])
    return df
