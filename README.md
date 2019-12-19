[![Python 3.6](https://img.shields.io/badge/python-3.6-blue.svg)](https://www.python.org/downloads/release/python-360/)
[![PyPI version](https://badge.fury.io/py/phd-scraper.svg)](https://pypi.org/project/phd-scraper/)

# phd_scraper

## Description

This package offers a complete module that makes download daily and hourly LatinAmerica Hydrometeorological datasets unpainless.

## Mode of use

### SENAMHI - [hydrometeorological](https://www.senamhi.gob.pe/mapas/mapa-estaciones-2/)

```
$ cd ~/phd_scraper/phd_scraper/
$ python3 se_hydrometeo.py --station_code 100090 --init_date 2019-01-01 --last_date 2019-02-02

```

```
from phd_scraper import se_hydrometeo
se_hydrometeo.download(station_code=100090, init_date=2019-01-01, last_date=2019-02-02)
```
### SENAMHI - [historic](https://web2.senamhi.gob.pe/descarga/?cod=152204)

```
$ cd ~/phd_scraper/phd_scraper/
$ python3 se_historic.py --station_code 152204 --outfile test.csv
```

```
from phd_scraper import se_historic
se_historic.download(code='152204')
```
