#!/usr/bin/env python

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
import argparse



def main(arguments):

    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('infile', help="Input file", type=argparse.FileType('r'))
    parser.add_argument('-o', '--outfile', help="Output file",
                        default=sys.stdout, type=argparse.FileType('w'))

    args = parser.parse_args(arguments)

    print(args)

if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))