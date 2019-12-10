#!/usr/bin/python
# -*- coding: utf-8 -*-

"""HTML scraper from SENAMHI historic data
URL: https://web2.senamhi.gob.pe/descarga/?cod={}
Version by: 0.0.1
Created by: Roy Yali <github.com/ryali93>
Modified by: Cesar Aybar <github.com/csaybar>
Comments:
    - Data obtained from highcharts :P     
"""

from __future__ import print_function

import os
import sys
import re
import json
import requests
import argparse

from bs4 import BeautifulSoup
import pandas as pd

stationgeo = \
    'https://raw.githubusercontent.com/PeHMeteoN/ScrappingToolKit/master/PE_SENAMHI_HISTORIC/senh_hist.json'


def generate_date(df, field_dates):
    """ Function for generate dates considering the last day of the year
        df: pd.DataFrame SENAMHI HISTORIC station
        field_dates: Column name
    """

    fy = list(df[field_dates])[0]
    len_first_year = len(df[df[field_dates] == fy])
    date_rng_fy = \
        pd.date_range(start='1/1/{}'.format(df[field_dates][0]),
                      end='31/12/{}'.format(df[field_dates][0]),
                      freq='D')
    dates_first_year = \
        pd.date_range(start=date_rng_fy[-len_first_year],
                      end='31/12/{}'.format(df[field_dates][0]),
                      freq='D')

    ly = list(df[field_dates])[-1]
    len_last_year = len(df[df[field_dates] == ly])
    date_rng_ly = pd.date_range(start='1/1/{}'.format(ly),
                                end='31/12/{}'.format(ly), freq='D')
    dates_last_year = pd.date_range(start='1/1/{}'.format(ly),
                                    end=date_rng_ly[len_last_year - 1],
                                    freq='D')

    dates = pd.date_range(start=date_rng_fy[-len_first_year],
                          end=date_rng_ly[len_last_year - 1], freq='D')
    df[field_dates] = dates
    return df


def download_data(code=157317,  output="./test.csv"):
    """ Download station by station considering the station code
        code: Station code (saved as a *.json)
    """

    response = \
        requests.get('https://web2.senamhi.gob.pe/descarga/?cod={}'.format(code))
    soup = BeautifulSoup(response.text, 'html.parser')
    highcharts_header = [s.text for s in soup.find_all('script',
                         {'type': 'text/javascript'})]
    highcharts_header = highcharts_header[1].replace('\n', ''
            ).replace('\r', '').replace('\t', '').replace('null', 'None'
            )  # removing \n\r\t
    highcharts_header = re.findall("\[.*?]", highcharts_header)
    data_station = [z for z in highcharts_header if len(z) > 100]  # Select date and values

    # Date

    date = re.findall("(categories: \[.*?])", highcharts_header[0])[0]
    date = (date.split(':')[1])[2:-2]
    date_list = [int(z) for z in date.replace("'", '').split(',')]

    # Values
    # #Precipitation

    prec = re.findall("(data: \[.*?])", data_station[1])[0]
    prec = (prec.split(':')[1])[2:-2]
    prec_values = []
    for pp in prec.split(','):
        if pp == 'None':
            prec_values.append(None)
        else:
            prec_values.append(float(pp))

    # #Tmax

    temp_max = (data_station[2])[1:-2]
    tmax_values = []
    for temp in temp_max.split(','):
        if temp == 'None':
            tmax_values.append(None)
        else:
            tmax_values.append(float(temp))

    # #Tmin

    temp_min = (data_station[3])[1:-2]
    tmin_values = []
    for temp in temp_min.split(','):
        if temp == 'None':
            tmin_values.append(None)
        else:
            tmin_values.append(float(temp))

    dicc_station = {
        'DATE': date_list,
        'PREC': prec_values,
        'TX': tmax_values,
        'TN': tmin_values,
        }

    data_station = generate_date(pd.DataFrame(dicc_station), 'DATE')    
    data_station.to_csv(output, index=False)
    return 0

def main(arguments):
    parser = argparse.ArgumentParser(description=__doc__,
            formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('-s', '--station_code', help='Output file',
                            default=sys.stdout)
    parser.add_argument('-o', '--outfile', help='Output file',
                        default=sys.stdout)
    args = parser.parse_args(arguments)    
    download_data(code=args.station_code,output=args.outfile)
    
if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))