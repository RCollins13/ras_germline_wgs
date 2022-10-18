#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2022 Ryan L. Collins and the Van Allen Laboratory
# Distributed under terms of the GPL-2.0 License (see LICENSE)
# Contact: Ryan L. Collins <Ryan_Collins@dfci.harvard.edu>

"""
Standardize a table of raw phenotypes for a single cohort
"""


import argparse
import pandas as pd
import subprocess
from sys import stdout


# Define constants used in multiple cohorts
cohorts = 'icgc hmf proactive mesa copdgene biome ukbb aou'.split()
read_msg = '\n===STANDARDIZATION LOG===\n - Loaded phenotype data for {:,} total samples from {}.'
drop_msg = ' - Excluded {:,} samples due to {}. {:,} samples remaining.'
write_msg = 'Filtering completed. Retained a total of {:,} samples.\n'
pop_map = {'Hispanic_Latin_American' : 'AMR',
           'African-American_African' : 'AFR',
           'European_American' : 'EUR',
           'South_Asian' : 'SAS',
           'East_South-East_Asian' : 'EAS',
           'Native_American' : 'AMR'}


def process_biome(infile, max_age_diff_wgs_bmi=3, quiet=False):
    """
    Processing steps for BioMe Biobank
    """

    # Load data
    idf = pd.read_csv(infile, sep='\t', skiprows=8, comment='#')
    if not quiet:
        print(read_msg.format(idf.shape[0], infile))

    # Clean all numeric columns
    numeric_cols = 'age_at_bmi age_at_height age_at_weight weight height bmi ' + \
                   'age_at_dna_blood_draw_wgs'
    for column in numeric_cols.split():
        idf[column] = idf[column].apply(lambda x: str(x).replace('^[<>]', ''))
        idf[column] = pd.to_numeric(idf[column], errors='coerce')

    # Drop samples that don't have core descriptives defined
    missing_drop = (idf.SEX.isna() \
                    | idf.ancestry_group.isna() \
                    | idf.bmi.isna() \
                    | idf.age_at_bmi.isna() \
                    | idf.age_at_dna_blood_draw_wgs.isna())
    if not quiet:
        print(drop_msg.format(missing_drop.sum(), 
                              'missing core descriptive metadata',
                              (~missing_drop).sum()))
    idf = idf[~missing_drop]

    # Drop samples with nonspecific ancestry
    ancestry_drop = idf.ancestry_group.isin('Other Multiple_Selected'.split())
    if not quiet:
        print(drop_msg.format(ancestry_drop.sum(), 
                              'ambiguous/nonspecific ancestry labels',
                              (~ancestry_drop).sum()))
    idf = idf[~ancestry_drop]

    # Compute difference between WGS blood draw age and BMI age
    # Only retain those within ±(max_age_diff_wgs_bmi) years
    idf['age_delta'] = idf.age_at_dna_blood_draw_wgs - idf.age_at_bmi
    age_drop = abs(idf.age_delta) > max_age_diff_wgs_bmi
    if not quiet:
        print(drop_msg.format(age_drop.sum(), 
                              'BMI and WGS age differing by more than ±' + \
                              str(max_age_diff_wgs_bmi) + ' years',
                              (~age_drop).sum()))
    idf = idf[~age_drop]

    # Drop unnecessary columns
    drop_cols = 'MI CR ANGINA PAD CAD COPD age_at_bmi age_at_height ' + \
                'age_at_weight hispanic_subgroup age_delta'
    idf.drop(labels=drop_cols.split(), 
             axis=1, inplace=True)

    # Add extra column
    idf['cohort'] = 'BioMe'

    # Reformat column values
    idf['population'] = idf.ancestry_group.map(pop_map)

    # Rename columns
    idf.rename(columns={'dbGaP_Subject_ID' : 'dbGaP_ID',
                        'SUBJECT_ID' : 'original_ID',
                        'SEX' : 'sex',
                        'age_at_dna_blood_draw_wgs' : 'age'},
               inplace=True)

    # (Optionally) report filtering results
    if not quiet:
        print(write_msg.format(idf.shape[0]))

    # Reorder & return output columns
    ordered_cols = 'cohort dbGaP_ID original_ID age sex population bmi height weight'
    return idf[ordered_cols.split()]


def main():
    """
    Main block
    """
    parser = argparse.ArgumentParser(
             description=__doc__,
             formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('raw_phenotypes', help='Raw sample phenotypes .tsv')
    parser.add_argument('--cohort', choices=cohorts, required=True, 
                        help='input format style to expect')
    parser.add_argument('-o', '--outfile', default='stdout', help='path to curated ' +
                        'phenotype .tsv output [default: stdout]')
    parser.add_argument('-z', '--gzip', action='store_true', help='gzip outfile')
    parser.add_argument('-q', '--quiet', action='store_true', help='Suppress ' +
                        'verbose logging.')
    args = parser.parse_args()

    # Process input data based on specified cohort
    if args.cohort == 'biome':
        clean_df = process_biome(args.raw_phenotypes)

    # Write to outfile
    if args.outfile in '- stdout'.split():
        fout = stdout
        stream_out = True
    else:
        stream_out = False
        if args.outfile.endswith('.gz'):
            gzip = True
            fout_path = args.outfile.replace('.gz$', '')
        else:
            gzip = args.gzip
            fout_path = args.outfile
        fout = open(fout_path, 'w')
    clean_df.rename(columns={'cohort' : '#cohort'}).to_csv(fout, sep='\t', index=False)

    # Gzip, if optioned
    if gzip and not stream_out:
        subprocess.run(['gzip', '-f', fout_path])


if __name__ == '__main__':
    main()
