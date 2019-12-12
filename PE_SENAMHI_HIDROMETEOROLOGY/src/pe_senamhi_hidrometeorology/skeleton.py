# -*- coding: utf-8 -*-
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

MODE OF USE
------------------------------------------------------------

Version by: 0.0.1
Created by: Roy Yali <github.com/ryali93>
Modified by: Cesar Aybar <github.com/csaybar>
Comments:
    - Data obtained from highcharts :P     

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



"""
This is a skeleton file that can serve as a starting point for a Python
console script. To run this script uncomment the following lines in the
[options.entry_points] section in setup.cfg:

    console_scripts =
         fibonacci = pe_senamhi_hidrometeorology.skeleton:run

Then run `python setup.py install` which will install the command `fibonacci`
inside your current environment.
Besides console scripts, the header (i.e. until _logger...) of this file can
also be used as template for Python modules.

Note: This skeleton file can be safely removed if not needed!
"""

import argparse
import sys
import logging

from pe_senamhi_hidrometeorology import __version__

__author__ = "csaaybar & ryali"
__copyright__ = "csaaybar & ryali"
__license__ = "mit"

_logger = logging.getLogger(__name__)


def fib(n):
    """Fibonacci example function

    Args:
      n (int): integer

    Returns:
      int: n-th Fibonacci number
    """
    assert n > 0
    a, b = 1, 1
    for i in range(n-1):
        a, b = b, a+b
    return a


def parse_args(args):
    """Parse command line parameters

    Args:
      args ([str]): command line parameters as list of strings

    Returns:
      :obj:`argparse.Namespace`: command line parameters namespace
    """
    parser = argparse.ArgumentParser(
        description="Just a Fibonacci demonstration")
    parser.add_argument(
        "--version",
        action="version",
        version="PE_SENAMHI_HIDROMETEOROLOGY {ver}".format(ver=__version__))
    parser.add_argument(
        dest="n",
        help="n-th Fibonacci number",
        type=int,
        metavar="INT")
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
    _logger.debug("Starting crazy calculations...")
    print("The {}-th Fibonacci number is {}".format(args.n, fib(args.n)))
    _logger.info("Script ends here")


def run():
    """Entry point for console_scripts
    """
    main(sys.argv[1:])


if __name__ == "__main__":
    run()
