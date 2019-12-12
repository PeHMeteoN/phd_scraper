#!/usr/bin/env python
"""HTML scraper from SENAMHI hidrometeorology data
This Python module scrape the hydrometeorology SENAMHI webpage 
(https://www.senamhi.gob.pe/mapas/mapa-estaciones-2/map_red_graf.php?). 
SENAMHI considerated five different gauge station classes with the 
following variables:

    - 'meteo_manual_realtime':['DATE','TX','TN','HUM','PREC_D'],
    - 'meteo_manual_deferred':['DATE','TX','TN','HUM','PREC_D'],
    - 'meteo_automatic':['DATE','HOUR','TEMP','PREC_H','HUM','W_DIR','W_VEL'],
    - 'hidro_manual_realtime':['DATE','LEVEL_06','LEVEL_10','LEVEL_14','LEVEL_18'],
    - 'hidro_manual_deferred':['DATE','HOUR','LEVEL','PREC_H']

Users need considerated that the entire dataset do not present control quality. The use of 
this data will be the sole responsibility of the user (See SENAMHI TERMS OF USE).

FUNCTIONS
------------------------------------------------------------
*download_data_range* is the main function. It permits you to download gauge meteorological data 
just specifying the station code and a date interval. See more details in help(download_data_range).
All functions created in this module are mentioned bellow.
    AUXILIARY:
        show_message: Show metadata from the gauge station.
        gaugestation_clasification: Return the meteorological variables according to the gauge station class.
        add_altitude: Add altitude (to the metadata dictionary). This step is extremely necessary to make queries (.php?..).
        data_senamhi_realtime: Transform SENAMHI HTML tables into pd.DataFrame.
        complete_monthly_data: Complete missing dates with np.NaN.
        download_data: Save SENAMHI HTML as a .CSV format.
    MAIN:
        download_data_range: Save SENAMHI HTML as a .CSV format considering a date interval.

MODE OF USE
------------------------------------------------------------
SIMPLE USERS:
    $ cd ~/ScrappingToolKit/PE_SENAMHI_HIDROMETEOROLOGY/src/
    $ python3 senh_hydrometeo.py --station_code 100090 --init_date 2019-01-01 --last_date 2019-02-02
ADVANCED USERS:
    $ cd ~/ScrappingToolKit/PE_SENAMHI_HIDROMETEOROLOGY/src/
    $ python3 senh_hydrometeo.py --station_code 100090 --init_date 2019-01-01 --last_date 2019-02-02
     --completedata False --quiet True --to_csv test.csv

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
import json
import logging
import requests
import argparse
import traceback
from datetime import datetime

import pickle
import numpy as np
import pandas as pd
from bs4 import BeautifulSoup
from calendar import monthrange

__version__ = '0.0.1'
__author__ = "csaaybar & ryali"
__copyright__ = "csaaybar & ryali"
__license__ = "GPL-3.0"

_logger = logging.getLogger(__name__)


## Create a pickle
#metadata_db = 'https://raw.githubusercontent.com/PeHMeteoN/ScrappingToolKit/master/PE_SENAMHI_HIDROMETEOROLOGY/senh_hist.json'    
#metadata_db = json.loads(requests.get(metadata_db).text)
#with open('senh_realtime.dictionary', 'wb') as config_dictionary_file:
#pickle.dump(metadata_db, config_dictionary_file)

def show_message(station_code, metadata_db="../../data/senh_realtime.dictionary"):
    '''Show metadata from the gauge station.
    (meteo_manual_realtime, meteo_manual_deferred, meteo_automatic, hidro_manual_realtime, hidro_manual_deferred)
    Args:
    -station_code: SENAMHI new code of the gauge station
    -metadata_db: Pickle object (List that contains dictionaries); Represent the metadata of the entire network.
    '''

    with open(metadata_db, 'rb') as config_dictionary_file: 
        metadata_db = pickle.load(config_dictionary_file)     
    #Search metadata for the station_code
    metadata_search = [dic for dic in metadata_db if dic['cod'] == str(station_code)]
    if len(metadata_search) != 1:
        raise Exception("Duplicated station_code .. please fixed before continuing.")
    metadata_search_dict = metadata_search[0]
    metadata_df = pd.DataFrame(metadata_search_dict,index=range(0,1)).melt()
    print(metadata_df)
    return 0

def gaugestation_clasification(station_code,return_type=True, metadata_db="../../data/senh_realtime.dictionary"): 
    '''Return the meteorological variables according to the gauge station class.
    Args:
    -station_code: Return the meteorological variables according to the gauge station class.
    -return_type: Logical; Whether it is True the variables names are returned, but it is just returned the station class code.
    -metadata_db: Pickle object (List that contains dictionaries); Represent the metadata of the entire network.
    '''

    #Read metadata DB
    with open(metadata_db, 'rb') as config_dictionary_file: 
        metadata_db = pickle.load(config_dictionary_file) 
    
    #Search metadata for the station_code
    metadata_search = [dic for dic in metadata_db if dic['cod'] == str(station_code)]
    if len(metadata_search) != 1:
        raise Exception("Duplicated station_code .. please fixed before continuing.")
    metadata_search_dict = metadata_search[0]

    variables_by_typestation = {
    'meteo_manual_realtime':['DATE','TX','TN','HUM','PREC_D'],
    'meteo_manual_deferred':['DATE','TX','TN','HUM','PREC_D'],
    'meteo_automatic':['DATE','HOUR','TEMP','PREC_H','HUM','W_DIR','W_VEL'],
    'hidro_manual_realtime':['DATE','LEVEL_06','LEVEL_10','LEVEL_14','LEVEL_18'],
    'hidro_manual_deferred':['DATE','HOUR','LEVEL','PREC_H']
    }

    if metadata_search_dict['ico'] == 'M':
        var_01 = 'meteo'
    elif metadata_search_dict['ico'] == 'H':
        var_01 = 'hidro'
    else:
        raise Exception("gaugestation_clasification: 'ico' key is neither 'D' nor 'H'")

    if metadata_search_dict['estado'] == 'DIFERIDO':
        var_02 = 'manual_deferred'
    elif metadata_search_dict['estado'] == 'REAL':
        var_02 = 'manual_realtime'
    elif metadata_search_dict['estado'] == 'AUTOMATICA':
        var_02 = 'automatic'
    else:
        raise Exception("gaugestation_clasification: 'estado' key do not match with 'DIFERIDO', 'READL' or 'AUTOMATICA'.")
    
    if return_type:
        return variables_by_typestation['%s_%s' % (var_01,var_02)]
    else:
        return '%s_%s' % (var_01,var_02)

def add_altitude(code, state, type_station, category_station, old_code=None):
    '''Add altitude (to the metadata dictionary). This step is extremely necessary to make queries (.php?..).
    Args:
    -code: Station code (SENAMHI new code's format)
    -state: METEOROLOGICA o HIDROLOGICA.
    -type_station: DIFERIDO, REALTIME and AUTOMATICO.    
    -old_code: Station code (SENAMHI old code's format)
    '''    
    if state == "AUTOMATICA":
        url = "https://www.senamhi.gob.pe/mapas/mapa-estaciones-2/map_red_graf.php?cod={}&estado={}&tipo_esta={}&cate={}".format(code, state, type_station, category_station)
    else:
        url = "https://www.senamhi.gob.pe/mapas/mapa-estaciones-2/map_red_graf.php?cod={}&estado={}&tipo_esta={}&cate={}&cod_old={}".format(code, state, type_station, category_station, old_code)
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    for s in soup.find_all("td"):
        if len(s) > 0:
            if "msnm" in s.text:
                alt = s.text.split(" ")[0]
    return alt

def data_senamhi_realtime(station, year_month, quiet=False):
    ''' Transform SENAMHI HTML tables into pd.DataFrame.
    Args:
    -station: Metadata of the gauge station as a dictionary
    -year_month: %Y%m Date format (it is SENAMHI format)
    -quiet: Logical. Suppress info message.
    '''
    cod = station["cod"]
    tipo_esta = station["ico"]
    estado = station["estado"]
    cod_old = station["cod_old"] if "cod_old" in station.keys() else ""
    cate_esta = station["cate"]
    altitud = station["alt"]
    
    url = "https://www.senamhi.gob.pe/mapas/mapa-estaciones-2/_dato_esta_tipo02.php"
    new_url = "{}?estaciones={}&CBOFiltro={}&t_e={}&estado={}&cod_old={}&cate_esta={}&alt={}".format(
            url, cod, year_month, tipo_esta, estado, cod_old, cate_esta, altitud)    
    if not quiet:
        print(new_url)
    s = requests.get(new_url)
    html = s.text
    soup = BeautifulSoup(html, 'html.parser')
    tables = [
        [
            [td.get_text(strip=True) for td in tr.find_all('td')] 
            for tr in table.find_all('tr')
        ] 
        for table in soup.find_all('table')
    ]
    
    if tipo_esta == "M":
        if estado == "AUTOMATICA":
            cols = ["fecha", "hora", "temp", "pp", "humedad", "dir_viento", "vel_viento"]
            df = pd.DataFrame(tables[1][1:], columns=cols)
        else:
            cols = ["fecha", "temp_max", "temp_min", "hum_relativa", "pp"]
            df = pd.DataFrame(tables[1][2:], columns=cols)
    elif tipo_esta == "H":
        if estado == "AUTOMATICA":
            cols = ["fecha", "hora", "nivel", "pp"]
            df = pd.DataFrame(tables[1][1:], columns=cols)
        else:
            cols = ["fecha", "nivel_06", "nivel_10", "nivel_14", "nivel_18"]
            df = pd.DataFrame(tables[1][2:], columns=cols)
    return df

def complete_monthly_data(station_data,station_class):
    '''Complete missing dates with np.NaN.
    Args:
    - station_data: Station monthly data in pd.DataFrame format.
    - station_class: String; Indicate the class of the gauge station.
    '''
    match_arg = station_class.split('_')[-1]
    if match_arg == 'automatic':
        # Creating a complete time serie
        complete_date = station_data['DATE']+" "+station_data['HOUR']+':00'
        station_data['DATETIME'] = pd.to_datetime(complete_date)       
        station_data.drop(['DATE','HOUR'],inplace=True,axis = 1)
        year_month = station_data['DATETIME'].map(lambda x: '%s_%02d'%(x.year,x.month)).mode()[0]
        year, month = map(lambda x:int(x), year_month.split('_'))
        last_day = monthrange(year, month)[1]
        ## Init & Last date
        init_day_dt = datetime(year, month, 1, hour=0)
        last_day_dt = datetime(year, month, last_day, hour=23)        
        # Merge all fill with None
        df = pd.DataFrame(
            data = pd.date_range(start = init_day_dt,
                                 end=last_day_dt,
                                 freq='H'),
            columns= ['DATETIME']).\
                merge(station_data,on=['DATETIME'],how='outer').fillna(np.NaN)
        df_HOUR = df.DATETIME.dt.strftime('%H:%M:%S')
        df_DATE = df.DATETIME.dt.strftime('%Y-%m-%d')
        df.drop(['DATETIME'],inplace=True,axis = 1)
        df = pd.concat([pd.DataFrame({'DATE':df_DATE, 'HOUR':df_HOUR}),df],axis=1).reset_index(drop = True)
        return df
    elif match_arg == 'realtime' or match_arg == 'deferred':
        # Creating a complete time serie
        year_month = pd.to_datetime(station_data['DATE']).map(lambda x: '%s_%02d'%(x.year,x.month)).mode()[0]
        year, month = map(lambda x:int(x), year_month.split('_'))
        last_day = monthrange(year, month)[1]
        ## Init & Last date
        init_day_dt = datetime(year, month, 1)
        last_day_dt = datetime(year, month, last_day)        
        # Merge all fill with None
        station_data['DATE'] = pd.to_datetime(station_data['DATE'])
        df = pd.DataFrame(
            data = pd.date_range(start = init_day_dt,
                                 end=last_day_dt,
                                 freq='D'),
            columns= ['DATE']).\
                merge(station_data,on=['DATE'],how='outer').fillna(np.NaN)        
        return df
    else:
        raise Exception('station_class do not match with deferred, realtime or automatic')

def download_data(station_code, date, completedata=True, specific=False, metadata_db="../../data/senh_realtime.dictionary", quiet=False):
    '''Download month by month and station by station the senamhi real-time dataset
       Args:
        - station_code: station new code.
        - date: Date to download in the format %Y-%m-%d (e.g. 2019-01-10).
        - completedata: Logical; Whether it is True the missing dates will be completed with np.NaN.
        - specific: Logical; Whether it is True (False) the specific day (month) will be downloaded.    
        - metadata_db: Pickle object (List that contains dictionaries); Represent the metadata of the entire network.
        - quiet: Logical. Suppress info message.
    '''    
    #Read metadata DB
    with open(metadata_db, 'rb') as config_dictionary_file: 
        metadata_db = pickle.load(config_dictionary_file) 
    
    #Search metadata for the station_code
    metadata_search = [dic for dic in metadata_db if dic['cod'] == str(station_code)]
    if len(metadata_search) != 1:
        raise Exception("Duplicated station_code .. please fixed before continuing.")
    metadata_search_dict = metadata_search[0]
    
    ## add altitude
    if "cod_old" in metadata_search_dict.keys():
        alt = add_altitude(metadata_search_dict["cod"],
                           metadata_search_dict["estado"],
                           metadata_search_dict["ico"],
                           metadata_search_dict["cate"],
                           metadata_search_dict["cod_old"])
    else:
        alt = add_altitude(metadata_search_dict["cod"], 
                           metadata_search_dict["estado"], 
                           metadata_search_dict["ico"], 
                           metadata_search_dict["cate"])
    metadata_search_dict["alt"] = alt

    #Fix date
    date_datetime = datetime.strptime(date,"%Y-%m-%d")
    date_senamhi_format = "%s%02d" % (date_datetime.year,date_datetime.month)

    #Get Data    
    gaugestation_columns = gaugestation_clasification(str(station_code))
    try:            
        total_df = data_senamhi_realtime(station = metadata_search_dict,year_month = date_senamhi_format,quiet=quiet)
        total_df.fecha = pd.to_datetime(total_df.fecha).dt.strftime('%Y-%m-%d').apply(str)        
        total_df.columns = gaugestation_columns
        total_df.replace({'S/D':np.NaN},inplace=True)
        if completedata:
            station_class = gaugestation_clasification(station_code,return_type=False)
            total_df = complete_monthly_data(total_df,station_class)
        else:
            pass               
    except:        
        num_days = monthrange(date_datetime.year, date_datetime.month)[1]
        dates_list = [datetime(date_datetime.year, date_datetime.month, day) for day in range(1, num_days+1)]
        total_df = pd.DataFrame({},index=dates_list,columns=gaugestation_columns)        
        total_df.DATE = dates_list                

    if specific:
        total_df = total_df[total_df.DATE == date]
    return total_df

def download_data_range(station_code, init_date, last_date, completedata=True, specific=False, to_csv = None, metadata_db="../../data/senh_realtime.dictionary", quiet=False):
    '''Download month by month and station by station the senamhi real-time dataset
       Args:
        - station_code: station new code.
        - init_date: Init date to start to download. Use the format %Y-%m-%d (e.g. 2019-01-10).
        - last_date: Last date to start to download. Use the format %Y-%m-%d (e.g. 2019-01-10).
        - completedata: Logical; Whether it is True the missing dates will be completed with np.NaN.
        - specific: Logical; Whether it is True (False) the specific day (month) will be downloaded.    
        - to_csv: String; Output filename.
        - metadata_db: Pickle object (List that contains dictionaries); Represent the metadata of the entire network.
        - quiet: Logical. Suppress info message.
    '''        
    seq_date = pd.date_range(start = init_date,
                             end = last_date,
                             freq = 'MS').tolist()
    if specific:
        range_date = [init_date]
    else:
        range_date = [datetime.strftime(date, '%Y-%m-%d') for date in seq_date]    

    if not quiet:
        show_message(station_code)
    
    station_data_complete = pd.DataFrame({})
    for month in range_date:
        print('Processing: ' + month)
        station_data = download_data(station_code = station_code,date = month, quiet=quiet, completedata=completedata,specific=specific)        
        station_data_complete = pd.concat([station_data_complete,station_data]).reset_index(drop = True)            
    
    if to_csv is not None:
        station_data_complete.to_csv(to_csv, index=False)
    else:
        print(station_data_complete)
        #return station_data_complete
        
def parse_args(args):
    """Parse command line parameters
    Args:
      args ([str]): command line parameters as list of strings

    Returns:
      :obj:`argparse.Namespace`: command line parameters namespace
    """
    parser = argparse.ArgumentParser(
        description="Download SENAMHI hydrometeorological data")
    parser.add_argument(
        "--version",
        action="version",
        version="PE_SENAMHI_HIDROMETEOROLOGY {ver}".format(ver=__version__))
    parser.add_argument(
        "--station_code",
        dest="station_code",
        help="New Code of the gauge station",
        type=str,
        metavar="STR")
    parser.add_argument(
        "--init_date",
        dest="init_date",
        help="target init date",
        type=str,
        metavar="STR")
    parser.add_argument(
        "--last_date",
        dest="last_date",
        help="target last date",
        type=str,
        metavar="STR")    
    parser.add_argument(
        "--completedata",
        dest="completedata",
        help="Complete missing days(hours) with NA",
        type=bool,
        default=True,
        metavar="BOOL")
    parser.add_argument(
        "--specific",
        dest="specific",
        help="Return data just for the specific day",
        default=False,
        type=bool,
        metavar="BOOL")
    parser.add_argument(
        "--to_csv",
        dest="to_csv",
        help="Specific output dirfile to save data (as *.CSV)",
        default=None,
        type=str,
        metavar="STR")
    parser.add_argument(
        "--metadata_db",
        dest="metadata_db",
        help="Filedir: Dataset which contains metadata of gauge stations.",
        default="../../data/senh_realtime.dictionary",
        type=str,
        metavar="str")
    parser.add_argument(
        "--quiet",
        dest="quiet",
        help="Display message",
        default=False,
        type=str,
        metavar="str")
    parser.add_argument(
        "-v",
        "--verbose",
        dest="loglevel",
        help="set loglevel to INFO",
        action="store_const",
        const=logging.INFO)
    parser.add_argument(
        "-vv",
        "--very-verbose",
        dest="loglevel",
        help="set loglevel to DEBUG",
        action="store_const",
        const=logging.DEBUG)
    return parser.parse_args(args)


def setup_logging(loglevel):
    """Setup basic logging
    Args:
      loglevel (int): minimum loglevel for emitting messages
    """
    logformat = "[%(asctime)s] %(levelname)s:%(name)s:%(message)s"
    logging.basicConfig(level=loglevel, stream=sys.stdout,
                        format=logformat, datefmt="%Y-%m-%d %H:%M:%S")


def main(args):
    """Main entry point allowing external calls

    Args:
      args ([str]): command line parameter list
    """
    args = parse_args(args)
    setup_logging(args.loglevel)
    _logger.debug("Starting download...")    
    download_data_range(args.station_code,args.init_date, args.last_date, args.completedata, 
                        args.specific, args.to_csv, args.metadata_db, args.quiet)
    _logger.info("Script ends here")

def run():
    """Entry point for console_scripts
    """    
    main(sys.argv[1:])


if __name__ == "__main__":
    run()
