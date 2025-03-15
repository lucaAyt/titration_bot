# TODO: Delete this parser

import os
import json
import pandas as pd

# from ami_utils import parse as pa


# Read in .txt files from UV-Vis Shimadzu
def get_uvvis_df(path): return pd.read_csv(path, skiprows=lambda x: x in [0, 2], sep='\t') \
    .set_index('Wavelength nm.') \
    .rename(columns={'Abs.': os.path.basename(os.path.normpath(path)).split('_')[-1].rstrip('.txt').lstrip('0')}) \
    .rename(columns={'': '0'}) \
    .astype(float)


# Concat each read and indicate files not read
def parse_uvvis(df: pd.DataFrame, path: str) -> pd.DataFrame:
    if '.txt' in path[-4:]:

        df = pd.concat([df, get_uvvis_df(path)], axis=1).dropna(how='all', axis=1)

    else:
        print(f'Not reading: {path}')

    return df


# Construct uvvis data dataframe via walk through paths
def get_data(exp_names):
    path = os.path.join(os.path.dirname(__file__), '', '../..', '..', '..', 'Documents', 'UV_Vis')
    if not os.path.exists(path):
        path = os.path.join(os.path.dirname(__file__), '', '../..', 'data', 'UV_Vis')

    dict_df = {}
    for root, dirs, files in os.walk(path):
        df = pd.DataFrame()
        name = [name for name in exp_names if name in root]
        if name:
            for f in sorted(files):
                df = parse_uvvis(df, os.path.join(root, f))
        if not df.empty:
            dict_df[name[0]] = df

    return dict_df


def get_exp_reps(exp_names):
    # Load config json

    cnfg_path = os.path.join(os.path.dirname(__file__), '', '../../config', 'config.json')
    cnfg = json.load(open(cnfg_path))

    reps = []
    for t in cnfg['titrations']:
        if t['name'] in exp_names:
            if t['exps']:
                reps.append(t['exps'])
            else:
                reps.append(t['name'])

    return [*sum(reps, [])]
