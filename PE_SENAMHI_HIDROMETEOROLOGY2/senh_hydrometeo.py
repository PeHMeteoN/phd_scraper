#!/usr/bin/env python

"""HTML scraper from SENAMHI hidrometeorology data
URL: https://www.senamhi.gob.pe/mapas/mapa-estaciones-2/map_red_graf.php?
Version by: 0.0.1
Created by: Roy Yali <github.com/ryali93>
Modified by: Cesar Aybar <github.com/csaybar>
Comments:
    - Data obtained from highcharts :P     
"""

from __future__ import print_function

import os
import sys
import json
import pickle
import requests
import argparse
import traceback
from calendar import monthrange
from datetime import datetime

from bs4 import BeautifulSoup
import pandas as pd


## Create a pickle
#metadata_db = 'https://raw.githubusercontent.com/PeHMeteoN/ScrappingToolKit/master/PE_SENAMHI_HIDROMETEOROLOGY/senh_hist.json'    
#metadata_db = json.loads(requests.get(metadata_db).text)
#with open('senh_realtime.dictionary', 'wb') as config_dictionary_file:
#pickle.dump(metadata_db, config_dictionary_file)


def gaugestation_clasification(metadata_search_dict):
    
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
    
    return variables_by_typestation['%s_%s' % (var_01,var_02)]


def add_altitude(code, state, type_station, category_station, old_code=None):
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

def data_senamhi_realtime(station, year_month):
    cod = station["cod"]
    tipo_esta = station["ico"]
    estado = station["estado"]
    cod_old = station["cod_old"] if "cod_old" in station.keys() else ""
    cate_esta = station["cate"]
    altitud = station["alt"]
    
    url = "https://www.senamhi.gob.pe/mapas/mapa-estaciones-2/_dato_esta_tipo02.php"
    new_url = "{}?estaciones={}&CBOFiltro={}&t_e={}&estado={}&cod_old={}&cate_esta={}&alt={}".format(
            url, cod, year_month, tipo_esta, estado, cod_old, cate_esta, altitud)    
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

def download_data(station_code, date, specific=False, metadata_db="./senh_realtime.dictionary"):
    '''Download month by month and station by station from senamhi real-time dataset
       Args:
        - station_code: station new code
        - date: Date to download in the format %Y-%m-%d (e.g. 2019-01-10)
        - specific: Logical; Whether is True (False) the specific day (month) will be downloaded.    
        - metadata_db: Pickle object (List that contains dictionaries); Represent the metadata of the entire network.
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
    try:            
        total_df = data_senamhi_realtime(station = metadata_search_dict,year_month = date_senamhi_format)
        total_df.fecha = pd.to_datetime(total_df.fecha).dt.strftime('%Y-%m-%d').apply(str)
    except:        
        num_days = monthrange(date_datetime.year, date_datetime.month)[1]
        dates_list = [datetime(date_datetime.year, date_datetime.month, day) for day in range(1, num_days+1)]
        total_df = pd.DataFrame({},index=dates_list,columns=gaugestation_clasification(metadata_search_dict))
        total_df.DATE = dates_list                
        
    if specific:
        total_df = total_df[total_df.fecha == date]
    return total_df

def download_data_range(station_code, date,save_csv,metadata_db="./senh_realtime.dictionary"):
    seq_date = pd.date_range(start = date[0],
                             end = date[1],
                             freq = 'MS').tolist()
    range_date = [datetime.strftime(date, '%Y-%m-%d') for date in seq_date]    
    for month in range_date:
        print(month)        
        month = '2019-03-01'
        download_data(station_code = station_code,date = month)



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