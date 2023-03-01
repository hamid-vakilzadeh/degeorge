import pandas as pd
import wrds
from pathlib import Path
import yaml

# create some folders
Path('input').mkdir(exist_ok=True)
Path('dataPrep').mkdir(exist_ok=True)


def prep_data():
    """
    :return: dataframe sample ready for Degeorge et al. (1999)
    """
    df_ibes_sumstat = pd.read_pickle('dataPrep/ibes_statsum_USD.pkl.gz')
    df_ibes_actpsum = pd.read_pickle('dataPrep/ibes_actpsum_USD.pkl.gz')

    df = df_ibes_actpsum.merge(df_ibes_sumstat, how='inner', on=['ticker', 'statpers'])
    df['year'] = pd.DatetimeIndex(df['anndats_act']).year
    df.sort_values(by=['ticker', 'statpers', 'anndats_act'], inplace=True)

    df.drop_duplicates(['ticker', 'anndats_act'], keep='last', inplace=True)
    df.dropna(subset=['ticker', 'fpedats'], inplace=True)

    df['fpeq'] = df['fpedats']
    df.reset_index(drop=True, inplace=True)
    df.sort_values(by=['ticker', 'fpedats'], inplace=True)
    df.set_index(['ticker', 'fpedats'], inplace=True)
    df['prior_year_EPS'] = np.nan

    for i in range(1, 5):
        lag_fpeq = df['fpeq'].groupby(level=["ticker"]).shift(i)
        lag_actual = df['actual'].groupby(level=["ticker"]).shift(i)
        df = df.join(lag_fpeq, rsuffix='_l')
        df = df.join(lag_actual, rsuffix='_l')
        df['diff'] = df['fpeq'] - df['fpeq_l']
        df['diff'] = df['diff'].dt.days
        df.loc[(df['diff'] >= 355) & (df['diff'] < 375), 'one_year_agp'] = df['actual_l']
        df['prior_year_EPS'].fillna(df['one_year_agp'], inplace=True)
        df = df.drop(columns=['fpeq_l', 'actual_l', 'one_year_agp', 'diff'])

    df['eps_n'] = df['actual'] * 100
    df['ferr_n'] = (df['actual'] - df['meanest']) * 100
    df['cheps_n'] = (df['actual'] - df['prior_year_EPS']) * 100

    # winsorize variables
    for column in ['eps_n', 'ferr_n', 'cheps_n']:
        column_name = column.split("_")[0]
        df[f'{column_name}_w'] = winsorize(df[f'{column_name}_n'], limits=[.01, .01])

    return df


if __name__ == '__main__':
    # establish a connection to WRDS Server (requires .pgpass)
    db = wrds.Connection(wrds_username=)
    db.list_tables(library='ibes')

    # I/B/E/S Summary History - Summary Statistics with Actuals (EPS for US Region)
    ibes_statsum_description = db.describe_table(library='ibes', table='statsum_epsus')
    ibes_statsum_USD = db.raw_sql("select * from ibes.statsum_epsus  "
                                  "where fpi='6' "
                                  "and measure='EPS' "
                                  "and curcode='USD' "
                                  "and curr_act ='USD'"
                                  "and actual is not null "
                                  "and medest is not null "
                                  "and meanest is not null "
                                  "and ticker is not null "
                                  "and statpers is not null "
                                  "and anndats_act is not null;")

    ibes_statsum_USD = pd.DataFrame(ibes_statsum_USD)

    # fix the date formatting for all the date columns
    for date in ['statpers', 'fpedats', 'actdats_act', 'anndats_act']:
        ibes_statsum_USD[f'{date}1'] = pd.to_datetime(ibes_statsum_USD[f'{date}'], infer_datetime_format=True).dt.date
        ibes_statsum_USD[f'{date}'] = ibes_statsum_USD[f'{date}1']
        ibes_statsum_USD.drop(columns=[f'{date}1'], inplace=True)

    # fix the time formatting for all the time columns
    for time_var in ['acttims_act', 'anntims_act']:
        ibes_statsum_USD[f'{time_var}1'] = \
            ibes_statsum_USD[f'{time_var}'].apply(lambda x: pd.Timestamp(x, unit='s').time())
        ibes_statsum_USD[f'{time_var}'] = ibes_statsum_USD[f'{time_var}1']
        ibes_statsum_USD.drop(columns=[f'{time_var}1'], inplace=True)

    # convert some float to int
    ibes_statsum_USD = ibes_statsum_USD.astype({'numest': 'int', 'numup': 'int', 'numdown': 'int', 'usfirm': 'int'})

    head_ibes_statsum_USD = ibes_statsum_USD.head(50)

    # save the database as a compressed pickle object
    ibes_statsum_USD.to_pickle('dataPrep/ibes_statsum_USD.pkl.gz')

    # I/B/E/S Summary History - Actuals + Pricing and Ancillary File (EPS for US Region)
    ibes_actpsum_description = db.describe_table(library='ibes', table='actpsum_epsus')

    ibes_actpsum_USD = db.raw_sql("select * from ibes.actpsum_epsus  "
                                  "where measure='EPS' "
                                  "and ticker is not null "
                                  "and statpers is not null "
                                  "and curcode='USD' "
                                  "and curr_price ='USD' "
                                  "and price is not null;")

    # fix the date formatting for all the date columns
    for date in ['statpers', 'fy0edats', 'int0dats', 'prdays']:
        ibes_actpsum_USD[f'{date}1'] = pd.to_datetime(ibes_actpsum_USD[f'{date}'], infer_datetime_format=True).dt.date
        ibes_actpsum_USD[f'{date}'] = ibes_actpsum_USD[f'{date}1']
        ibes_actpsum_USD.drop(columns=[f'{date}1'], inplace=True)

    # convert some float to int
    ibes_actpsum_USD = ibes_actpsum_USD.astype({'usfirm': 'int'})

    head_ibes_actpsum_USD = ibes_actpsum_USD.head(50)

    ibes_actpsum_USD.to_pickle('dataPrep/ibes_actpsum_USD.pkl.gz')

    # create database for Degeorge et al. (1999)
    df = prep_data()

    # drop unneeded variables
    sample = df.drop(columns=['cusip_x', 'oftic_x', 'cname_x', 'statpers', 'measure_x', 'fy0a',
                              'curcode_x', 'fvyrgro', 'fvyrsta', 'usfirm_x', 'fy0edats', 'int0a',
                              'int0dats', 'prdays', 'shout', 'iadiv', 'curr_price',
                              'cusip_y', 'oftic_y', 'cname_y', 'measure_y', 'fiscalp', 'fpi',
                              'estflag', 'curcode_y', 'numest', 'numup', 'numdown', 'medest',
                              'meanest', 'stdev', 'highest', 'lowest', 'usfirm_y', 'actual',
                              'actdats_act', 'acttims_act', 'anndats_act', 'anntims_act', 'curr_act', 'fpeq'])

    # save the data as a compressed pickle file
    sample.to_pickle('input/data.pkl.gz')
