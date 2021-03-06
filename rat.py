import os
import re
import sys
import argparse
import operator

from collections import namedtuple

import mappy as mp

from util import check_path, create_clean_dir
from vepar import PeakSink


class _PafHolder():
    ''' List wrapper for PAF alignments '''

    Query = namedtuple('Query', ['len', 'alignments'])

    def __init__(self, ref_name, ovlp_dir):
        self.ref_name = ref_name
        self.out_dir = create_clean_dir(ovlp_dir, ref_name)

        self.queries = {}
        self.__peak = PeakSink(
            ref_name, lambda q_name: self.queries[q_name].alignments)

    def add_alignment(self, q_name, q_len, alignment):
        if q_name not in self.queries:
            self.queries[q_name] = _PafHolder.Query(q_len, [])

        # TODO: Tie in one method
        self.__peak.consume(q_name, alignment)
        self.queries[q_name].alignments.append(alignment)

    def dump_paf(self):
        dest_paf = os.path.join(self.out_dir, 'overlaps.paf')
        print('[Log]: Writing overlaps {}'.format(dest_paf), file=sys.stderr)

        def fmt_paf(q_name, q_len, align):
            return '{} {} {}'.format(q_name, q_len, str(align).rsplit('cg:')[0])

        with open(dest_paf, 'w+') as dist:
            for q_name, data in self.queries.items():
                for paf in map(lambda a: fmt_paf(q_name, data.len, a), data.alignments):
                    dist.write(paf + '\n')

    def gen_plot(self):
        if not self.__peak.empty():
            self.__peak.plot(self.out_dir)


class Rat:
    ''' Slices metegenomic accembly into contings matching references.
    '''

    # Defaults
    __THRESHOLD = int(1e4)
    __N_THREADS = 3
    __BEST_N = 10

    @staticmethod
    def __init_parser():
        ''' Initializes command line argument parser '''

        parser = argparse.ArgumentParser(
            description='''Takes a metagenomic assembly and a folder containing population fasta references.
                    Prints most promising overlaps to paf at specified location.\n\n

                    Format: rat [options] <assembly.(fasta|fa)> <ref_dir> <out_dir>''',
            formatter_class=argparse.RawTextHelpFormatter)

        parser.add_argument('--threshold', type=int, dest='threshold', action='store', default=Rat.__THRESHOLD,
                            help='Overlaps with lower length are discarded. Default: {}'.format(Rat.__THRESHOLD))
        parser.add_argument('--best_n', type=int, dest='best_n', action='store', default=Rat.__BEST_N,
                            help='Number of longest overlaps taken as valid matches. Default={}'.format(Rat.__BEST_N))
        parser.add_argument('-t', type=int, dest='n_threads', action='store', default=Rat.__N_THREADS,
                            help='Number of threads used by minimap. Default=3')

        parser.add_argument('assembly_fasta', nargs=1, type=str)
        parser.add_argument('ref_dir', nargs=1, type=str)
        parser.add_argument('out_dir', nargs=1, type=str)

        return parser

    def __parse_args(self, args_raw):
        ''' Parses args from list or command line 
            and initializes Rat config, parameters '''

        args = self.__parser.parse_args(args_raw)

        self.__n_threads = args.n_threads
        self.__threshold = args.threshold
        self.__best_n = args.best_n

        self.__assembly_fasta = check_path(args.assembly_fasta[0])
        self.__ref_dir = check_path(args.ref_dir[0])
        self.__out_dir = check_path(args.out_dir[0])

    def __create_aligner(self, seq_path):
        ''' Creates a minimap2 aligner via mappy binding

            Params:
                seq_path: Path to reference sequence

            Returns:
                mappy.Aligner()

            Raises:
                Exception if fail to create aligner

        '''

        aligner = mp.Aligner(
            fn_idx_in=seq_path,
            n_threads=self.__n_threads,
            preset=self.__preset,
            best_n=self.__best_n,

            # TODO: Extra flags
        )

        if not aligner:
            raise Exception('Filed to create index for{}'.format(
                self.__assembly_fasta))

        return aligner

    def __init_asm(self):
        ''' Loads contings from fasta assembly into a dictionary

            Returns:
                asm: {seq_id: seq} dictionary
        '''

        asm = {}
        for name, seq, _ in mp.fastx_read(self.__assembly_fasta):
            asm[name] = seq

        return asm

    def __init__(self, args=None):
        ''' Initializes Rat and parses arguments

            Args:
                args: List of arguments to be parsed.
                        Default: None, propagates to command line.

         '''

        self.__parser = self.__init_parser()
        self.__parse_args(args)

        self.__asm = self.__init_asm()

        # Asm to ref mapping
        self.__preset = 'asm20'

        self.__ovlp_dir = create_clean_dir(
            self.__out_dir, 'rat_overlaps', True)

    def __map_to(self, ref_name, ref_path):
        ''' Maps assembly to reference sequence.

            Args:
                ref_name: reference genome name
                ref_path: path to reference fasta file

            Returns:
                pafs: _PafHolder with all conting matches
        '''

        aligner = self.__create_aligner(ref_path)
        pafs = _PafHolder(ref_name, self.__ovlp_dir)

        for q_name, q_str in self.__asm.items():
            for hit in aligner.map(q_str):
                pafs.add_alignment(q_name, len(q_str), hit)

        return pafs

    def run(self):
        fasta_re = r'\S+.(fasta|fa)'
        def get_seq_path(seq): return os.path.join(self.__ref_dir, seq)

        for file_name in os.listdir(self.__ref_dir):
            ref_path = get_seq_path(file_name)
            ref_name = file_name.split('.')[0]
            if not re.match(fasta_re, ref_path):
                print('[WARNING] Skipping {}.'.format(
                    ref_name), file=sys.stderr)

            pafs = self.__map_to(ref_name, ref_path)

            pafs.dump_paf()
            pafs.gen_plot()
