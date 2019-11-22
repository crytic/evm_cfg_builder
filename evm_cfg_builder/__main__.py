import json
import re
import sys
import argparse
import logging
import os
from pkg_resources import require

from crytic_compile import cryticparser, CryticCompile, InvalidCompilation, is_supported
from .known_hashes.known_hashes import known_hashes

from .cfg import CFG

logging.basicConfig()
logger = logging.getLogger("evm-cfg-builder")

def output_to_dot(d, filename, cfg):
    if not os.path.exists(d):
        os.makedirs(d)
    filename = os.path.basename(filename)
    filename = os.path.join(d, filename+ '_')
    cfg.output_to_dot(filename)
    for function in cfg.functions:
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
                        default='crytic-export/evm')

    parser.add_argument('--disable-optimizations',
                        help='Disable the CFG recovery optimizations',
                        action='store_true',
                        dest='disable_optimizations',
                        default=False)

    parser.add_argument('--disable-cfg',
                        help='Disable the CFG recovery',
                        action='store_true',
                        dest='disable_cfg',
                        default=False)

    parser.add_argument('--export-abi',
                        help="Export the contract's ABI",
                        action='store',
                        dest='export_abi',
                        default=None)

    parser.add_argument('--version',
                        help='displays the current version',
                        version=require('evm-cfg-builder')[0].version,
                        action='version')

    cryticparser.init(parser)

    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        sys.exit(1)
    args = parser.parse_args()
    return args

def _run(bytecode, filename, args):

    optimization_enabled = False
    if args.disable_optimizations:
        optimization_enabled = True

    cfg = CFG(bytecode, optimization_enabled=optimization_enabled, compute_cfgs=not args.disable_cfg)

    for function in cfg.functions:
        logger.info(function)

    if args.dot_directory:
        output_to_dot(args.dot_directory, filename, cfg)

    if args.export_abi:
        export = []
        for function in cfg.functions:
            export.append({
                'hash_id': hex(function.hash_id),
                'start_addr': hex(function.start_addr),
                'signature': function.name if function.name != hex(function.hash_id) else None,
                'attributes': function.attributes
            })

        with open(args.export_abi, 'w') as f:
            json.dump(export, f)


def main():

    l = logging.getLogger('evm-cfg-builder')
    l.setLevel(logging.INFO)
    args = parse_args()

    if is_supported(args.filename):
        filename = args.filename
        del args.filename
        try:
            cryticCompile = CryticCompile(filename, **vars(args))
            for contract in cryticCompile.contracts_names:
                bytecode_init = cryticCompile.bytecode_init(contract)
                if bytecode_init:
                    for signature, hash in cryticCompile.hashes(contract).items():
                        known_hashes[hash] = signature
                    logger.info(f'Analyze {contract}')
                    _run(bytecode_init, f'{filename}-{contract}-init', args)
                    runtime_bytecode = cryticCompile.bytecode_runtime(contract)
                    if runtime_bytecode:
                        _run(runtime_bytecode,  f'{filename}-{contract}-runtime', args)
                    else:
                        logger.info('Runtime bytecode not available')
        except InvalidCompilation as e:
            logger.error(e)

    else:
        with open(args.filename, 'rb') as f:
            bytecode = f.read()
        logger.info(f'Analyze {args.filename}')
        _run(bytecode, args.filename, args)




if __name__ == '__main__':
    main()
