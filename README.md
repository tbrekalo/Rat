# Rat
Python script for extracting and grouping alignments from single metagenomic assembly via pepulation reference.


## Usage
```
python3 rat [-h] [--threshold THRESHOLD] [--best_n BEST_N] [-t N_THREADS]
         assembly_fasta ref_dir out_dir

Takes a metagenomic assembly and a folder containing population fasta references.
                    Prints most promising overlaps to paf at specifed location.

                    Format: rat [options] <assembly.(fasta|fa)> <ref_dir> <out_dir>

positional arguments:
  assembly_fasta
  ref_dir
  out_dir

optional arguments:
  -h, --help            show this help message and exit
  --threshold THRESHOLD
                        Overlaps with lower length are discarded. Default: 10000
  --best_n BEST_N       Number of longest overlaps taken as valid matches. Default=10
  -t N_THREADS          Number of threads used by minimap. Default=3
```