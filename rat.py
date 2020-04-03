import os
import re
import sys
import argparse

import mappy as mp

import util

# Dummy: Listeria_monocytogenes_complete_genome.fasta


class Rat:
    ''' Slices metegenomic accembly into contings matching references.
    '''

    @staticmethod
    def __init_parser():
        ''' Initializes command line argument parser '''

        parser = argparse.ArgumentParser(
            description='''Takes a metagenomic assembly and a folder containing population fasta references.
                    Prints most promising overlaps to stdout.\n\n

                    Format: rat [options] <assembly.(fasta|fa)> <ref_dir> <out_dir>''',
            formatter_class=argparse.RawTextHelpFormatter)

        parser.add_argument('--threshold', type=int, dest='threshold', action='store', default=int(1e4),
                            help='Overlaps with lower length are discarded. Default: 10 000')
        parser.add_argument('--top', type=int, dest='top', action='store', default=5,
                            help='Number of longest overlaps taken as valid matches. Default=5')
        parser.add_argument('-t', type=int, dest='n_threads', action='store', default=1,
                            help='Number of threads used by minimap. Default=1, Max=3')

        parser.add_argument('assembly_fasta', nargs=1, type=str)
        parser.add_argument('ref_dir', nargs=1, type=str)
        parser.add_argument('out_dir', nargs=1, type=str)

        return parser


    def __parse_args(self, args_raw):
        ''' Parses args from list or command line 
            and initializes Rat config, parameters ''' 

        args = self.__parser.parse_args(args_raw)

        self.__conf = {
            'n_threads': args.n_threads,
            'threshold': args.threshold,
            'top': args.top,
        }



        self.__assembly_fasta = args.assembly_fasta[0]
        self.__ref_dir = args.ref_dir[0]
        self.__out_dir = args.out_dir[0]

    def __init__(self, args=None):
        ''' Initializes Rat and parses arguments
        
            Args:
                args: List of arguments to be parsed.
                        Default: None, propagates to command line.

         '''

        self.__parser = self.__init_parser()
        self.__parse_args(args)


    def run(self):
        fasta_re = r'\S+.(fasta|fa)'
        for filename in os.listdir(self.__ref_dir):
            if not re.match(fasta_re, filename):
                print('[WARNING] Skipping {}.'.format(filename), file=sys.stderr)
            print(filename)