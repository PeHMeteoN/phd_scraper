[![Python 3.6](https://img.shields.io/badge/python-3.6-blue.svg)](https://www.python.org/downloads/release/python-360/)
[![PyPI version](https://badge.fury.io/py/phd-scraper.svg)](https://pypi.org/project/phd-scraper/)
[![Build Status](https://travis-ci.org/csaybar/phd_scraper.svg?branch=master)](https://travis-ci.org/csaybar/phd_scraper)

# phd_scraper

**phd_scraper** is a tool to download daily and hourly LatinAmerica Hydrometeorological datasets using Python. Currently phd_scraper support the following websites:

  - [Historic Data SENAMHI-PERU](https://web2.senamhi.gob.pe/descarga/?cod=100090).
  - [Hidrometeorology Data SENAMHI-PERU ](https://www.senamhi.gob.pe/mapas/mapa-estaciones-2/map_red_graf.php?)

Users need to regard that the entire dataset does not present control quality.
The use of this data will be the sole responsibility of the user (see below).

#### DISCLAIMER (Adapted from: https://github.com/ConorIA/senamhiR)

The scripts outlined in this document is published under the GNU General Public License, 
version 3 (GPL-3.0). The GPL is an open source, copyleft license that allows for the modification 
and redistribution of original works.Programs licensed under the GPL come with NO WARRANTY.
In our case, a simple Python script isn’t likely to blow up your computer or kill your cat.
Nonetheless, it is always a good idea to pay attention to what you are doing, to ensure that 
you have downloaded the correct data, and that everything looks ship-shape.

#### WHAT TO DO IF SOMETHING DOESN'T WORK (Adapted from: https://github.com/ConorIA/senamhiR)

If you run into an issue while you are using this script, you can email us and we can help you 
troubleshoot the issue. However, if the issue is related to the script and not your own 
fault, you should contribute back to the open source community by reporting the issue.
You can report any issues to us here on GitHub.

If that seems like a lot of work, just think about how much work it would have been to do
all the work this package does for you, or how much time went in to writing these functions … 
it is more than I’d like to admit!


#### SENAMHI TERMS OF USE (Adapted from: https://github.com/ConorIA/senamhiR)

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


## Installation

**muggles**

```sh
pip install phd_scraper
```

**hipsters**

```sh
wget https://github.com/PeHMeteoN/phd_scraper/archive/master.zip
unzip master && cd phd_scraper-master
python setup.py install
```


## Usage

### SENAMHI - [hydrometeorological](https://www.senamhi.gob.pe/mapas/mapa-estaciones-2/): Hydrometeorological data throughout Peru.


|    **Parameters**    |    **Description**       |
|:--------------------:|:------------------------:|
| *station_code*| station new code        |
| *init_date*   | Init date to start to download |
| *last_date*   | Last date to start to download | 
| *completedata*| Whether it is True the missing dates will be completed with np.NaN |
| *to_csv*      | Output filename |
| *metadata_db* | Represent the metadata of the entire network (see phd_scraper.create_metadata) |

**Basic Usage**

```
from phd_scraper import se_hydrometeo
se_hydrometeo.download(station_code=100090, init_date=2019-01-01, last_date=2019-02-02)
```

**Console mode**

```
$ cd ~/phd_scraper/phd_scraper/
$ python3 se_hydrometeo.py --station_code 100090 --init_date 2019-01-01 --last_date 2019-02-02 --to_csv test.csv

```
### SENAMHI - [historic](https://web2.senamhi.gob.pe/descarga/?cod=152204)

|    **Parameters**    |    **Description**       |
|:--------------------:|:------------------------:|
| *station_code*       | station new code |
| *to_csv*             | String; Output filename.|

**Basic Usage**

```
from phd_scraper import se_historic
se_historic.download(code='152204')
```

**Console mode**

```
$ cd ~/phd_scraper/phd_scraper/
$ python3 se_historic.py --station_code 152204 --outfile test.csv
```
