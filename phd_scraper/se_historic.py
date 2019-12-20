#!/usr/bin/python
"""HTML scraper from SENAMHI historic data
This Python module scrape the Historic SENAMHI webpage
(https://web2.senamhi.gob.pe/descarga/?cod={}).
SENAMHI historic data considerated one format:

  SENAMHI_historic_data :['DATE','PREC','TX','TN']

Users need consideration that the entire dataset do not present control quality. 
The use of this data will be the sole responsibility of the user (See SENAMHI TERMS OF USE).

FUNCTIONS
------------------------------------------------------------
*download_senamhi_historic* is the main function. It permits you to download historic gauge meteorological data 
just specifying the station code. See more details in help(download_senamhi_historic).
All functions created in this module are mentioned bellow.

    AUXILIARY:
        generate_date: Show metadata from the gauge station.
    MAIN:
        download_senamhi_historic: Save SENAMHI HISTORIC DATA as a .CSV format.

MODE OF USE
------------------------------------------------------------
    $ cd ~/phd_scraper/phd_scraper/
    $ python3 se_historic.py --station_code 152204 --outfile cesar.csv
    
    >>> from phd_scraper import se_historic
    >>> se_historic.download(code='152204')

DISCLAIMER (Adapted from: https://github.com/ConorIA/senamhiR)
------------------------------------------------------------
The scripts outlined in this document is published under the GNU General Public License, 
version 3 (GPL-3.0). The GPL is an open source, copyleft license that allows for the modification 
and redistribution of original works.Programs licensed under the GPL come with NO WARRANTY.
In our case, a simple Python script isn’t likely to blow up your computer or kill your cat.
Nonetheless, it is always a good idea to pay attention to what you are doing, to ensure that 
you have downloaded the correct data, and that everything looks ship-shape.

WHAT TO DO IF SOMETHING DOESN'T WORK (Adapted from: https://github.com/ConorIA/senamhiR)
------------------------------------------------------------
If you run into an issue while you are using this script, you can email us and we can help you 
troubleshoot the issue. However, if the issue is related to the script and not your own 
fault, you should contribute back to the open source community by reporting the issue.
You can report any issues to us here on GitHub.

If that seems like a lot of work, just think about how much work it would have been to do
all the work this package does for you, or how much time went in to writing these functions … 
it is more than I’d like to admit!


SENAMHI TERMS OF USE (Adapted from: https://github.com/ConorIA/senamhiR)
------------------------------------------------------------
SENAMHI's terms of use are in https://senamhi.gob.pe/?p=terminos_condiciones, but
as of writing that link was redirecting to the SENAMHI home page. An archived version is available
in https://web.archive.org/web/20170822092538/http://senamhi.gob.pe/?p=terminos_condiciones.
The terms allow for the free and public access to information on the SENAMHI website, in
both for-profit and non-profit applications. However, SENAMHI stipulates that any use 
of the data must be accompanied by a disclaimer that SENAMHI is the proprietor of the 
information. The following text is recommended (official text in Spanish):

Official Spanish: Información recopilada y trabajada por el Servicio Nacional de Meteorología e
Hidrología del Perú. El uso que se le da a esta información es de mi (nuestra) entera responsabilidad.
English translation: This information was compiled and maintained by Peru’s National Meteorology 
and Hydrology Service (SENAMHI). The use of this data is of my (our) sole responsibility.
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
import numpy as np

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

def download(station_code, to_csv = None):
    """ Download station by station considering the station code
        - station_code: Station code
        - to_csv: String; Output filename.
    """
    response = \
        requests.get('https://web2.senamhi.gob.pe/descarga/?cod={}'.format(station_code))
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
    data_station.replace(to_replace=[None], value=np.nan, inplace=True)
    if to_csv is not None:
        data_station.to_csv(to_csv, index=False)
    return data_station

def main(arguments):
    parser = argparse.ArgumentParser(description=__doc__,
            formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('-s', '--station_code', help='Output file',
                            default=sys.stdout)
    parser.add_argument('-o', '--to_csv', help='Output file',
                        default=sys.stdout)
    args = parser.parse_args(arguments)    
    download(station_code=args.station_code,to_csv=args.outfile)
    
if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))