import re
import sys
import argparse
import logging
import os
from pkg_resources import require
from pyevmasm import disassemble_all

from .cfg import CFG

logging.basicConfig()
logger = logging.getLogger("evm-cfg-builder")

def output_to_dot(d, filename, functions):
    if not os.path.exists(d):
        os.makedirs(d)
    filename = os.path.basename(filename)
    filename = os.path.join(d, filename+ '_')
    for function in functions:
        function.output_to_dot(filename)

def parse_args():
    parser = argparse.ArgumentParser(description='evm-cfg-builder',
                                     usage="evm-cfg-builder contract.evm [flag]")

    parser.add_argument('filename',
                        help='contract.evm')

    parser.add_argument('--export-dot',
                        help='Export the functions to .dot files in the directory',
                        action='store',
                        dest='dot_directory',
                        default='')

    parser.add_argument('--version',
                        help='displays the current version',
                        version=require('evm-cfg-builder')[0].version,
                        action='version')


    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        sys.exit(1)
    args = parser.parse_args()
    return args

def main():

    l = logging.getLogger('evm-cfg-builder')
    l.setLevel(logging.INFO)
    args = parse_args()

    with open(args.filename) as f:
        bytecode = f.read().replace('\n', '')

    cfg = CFG(bytecode)

    for function in cfg.functions:
        logger.info(function)

    if args.dot_directory:
        output_to_dot(args.dot_directory, args.filename, cfg.functions)


if __name__ == '__main__':
    main()
