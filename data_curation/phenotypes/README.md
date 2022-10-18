## Phenotype data curation  

This subdirectory contains the code used to curate phenotypic metadata for the cohorts in this study.  

Each cohort had its raw phenotype metadata standardized using `standardize_phenotypes.py`.  

Example usage is provided in `standardize_all_cohorts.sh`.  

Study-specific notes are provided below:  

### [BioMe Biobank](https://www.ncbi.nlm.nih.gov/projects/gap/cgi-bin/study.cgi?study_id=phs001644.v2.p2)  
* Phenotypes were downloaded directly from dbGaP accession [phs001644.v2.p2](https://www.ncbi.nlm.nih.gov/projects/gap/cgi-bin/study.cgi?study_id=phs001644.v2.p2)  
* Excluded 549 samples due to missing core descriptive metadata  
* Excluded 1,147 samples due to ambiguous/nonspecific ancestry labels  
* Excluded 1,865 samples due to BMI and WGS age differing by more than ±3 years  
After filtering, we retained a total of 8,489 samples.  
