import sqlite3
import pandas as pd
import numpy as np

DATABASE = 'bart.db'
FILES = ['plza.csv', 'mont.csv']

def parse_time(timestamp):

    try:
        dt = pd.to_datetime(float(timestamp), unit='s')
        return dt.tz_localize('UTC').tz_convert('US/Pacific')
    except (AttributeError, ValueError):
        return pd.NaT

def define_weekday(obs_time):

    if obs_time.weekday() < 5:
        return 0
    elif obs_time.weekday() == 5:
        return 1
    elif obs_time.weekday() == 6:
        return 2

def time2minute_of_day(obs_time):

    return obs_time.time().hour * 60 + obs_time.time().minute

def parse_data(file_name, date_parser=parse_time, time_col=['time']):

    return pd.read_csv(file_name, parse_dates=time_col, date_parser=date_parser)

def csv2sql(conn, files):

    output_cols = ['dest', 'dir', 'etd', 'station', 'minute_of_day', 'day_of_week']
    conn.execute("DROP TABLE IF EXISTS etd")

    for sta_file in files:
        df = parse_data(sta_file)
        df['station'] = sta_file.split('.')[0]
        df['day_of_week'] = df['time'].apply(lambda x: define_weekday(x))
        df['etd'] = df['etd'].replade('Leaving', 0).dropna().astype(np.int)
        df['minute_of_day'] = df['time'].apply(time2minute_of_day)
        df[output_cols].to_sql('etd', conn, index=False, if_exists='append')

    conn.cursor().execute(

    )
    conn.commit()
    conn.close()

if __name__ == '__main__':
    conn = sqlite3.connect(DATABASE)
    csv2sql(conn, FILES)
