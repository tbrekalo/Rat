''' Module for plotting PAF alignments '''

import os
import sys
import operator

import seaborn
from matplotlib import pyplot

import mappy as mp


class PeakQSink:
    ''' Accepts mappy alignment objects but only 
        stores the one with hightest query_end - query_start value.

        On request, creates dot alignment plot '''

    # Defaults
    __X_DEF = 16
    __Y_DEF = 16

    def __init__(self, ref_name, x_dim=__X_DEF, y_dim=__Y_DEF):
        ''' Constructor

            Args:
                ref_name: reference name we are matching to 
                x_dim: x-axis dimension when plotting, default: __X_DEF
                y_dim: y-axis dimension when plotting, default: __Y_DEF
        '''
        self.ref_name = ref_name

        self.__q_name = None
        self.__peak_diff = 0
        self.__peak = None

        self.__x_dim = x_dim
        self.__y_dim = y_dim

    def consume(self, q_name, alignment):
        ''' Consumes new alignment and updates the peek accordingly.

            Args:
                q_name: query sequence name, not contained in aligment
                alignment: mappy alignment object  '''

        diff = abs(alignment.q_en - alignment.q_st)
        if diff > self.__peak_diff:
            self.__peak = alignment
            self.__q_name = q_name
            self.__peak_diff = diff

    def empty(self):
        ''' Returns True if there's a current peak value '''

        return self.__peak is None

    def plot(self, dest=os.getcwd()):
        ''' Plots the alignment with longest query match length

            Args:
                dest: destinatio folder, defaults to cwd

            Returns:
                png_path: relative file path to generated plot image

            Raises:
                RuntimeError if there's no peek value
         '''

        if self.__peak is None:
            raise RuntimeError('No values provided for peek selection')

        seaborn.set()
        seaborn.set_style('white')
        pyplot.figure(figsize=(self.__x_dim, self.__y_dim))

        peak = self.__peak

        pyplot.plot([peak.r_st, peak.r_en],
                    [peak.q_st, peak.q_en] if peak.strand > 0 else [peak.q_en, peak.q_st], '-')

        png_path = os.path.join(dest, self.__q_name + '.png')
        pyplot.savefig(png_path, format='png')
        pyplot.close()

        print('[Log] Ploted {} to {}'.format(
            self.__q_name, self.ref_name), file=sys.stderr)

        return png_path
