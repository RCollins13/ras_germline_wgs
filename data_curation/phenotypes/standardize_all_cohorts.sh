#!/usr/bin/env bash

# Phenotype curation for germline WGS of RAS-driven cancers
# 
# Copyright (c) 2022 Ryan L. Collins and the Van Allen Laboratory
# Distributed under terms of the GPL-2.0 License (see LICENSE)
# Contact: Ryan L. Collins <Ryan_Collins@dfci.harvard.edu>


# Set local parameters (RLC locals provided as example)
export WRKDIR=~/Desktop/Collins/VanAllen/RAS_projects/RAS_WGS
export OUTDIR=$WRKDIR/cohort_data/phenotypes
export CODE=$WRKDIR/ras_germline_wgs
cd $WRKDIR


# Process BioMe Biobank
$CODE/data_curation/phenotypes/standardize_phenotypes.py \
  --cohort biome \
  --outfile $OUTDIR/BioMe.phenotypes.tsv.gz \
  --gzip \
  $WRKDIR/dbGaP/BioMe_phs001644.v2.p2/manifests/PhenotypeFiles/phs001644.v2.pht009946.v2.p2.c1.TOPMed_CCDG_BioME_Subject_Phenotypes.HMB-NPU.txt.gz