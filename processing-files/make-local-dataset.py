# -*- coding: utf-8 -*-
import os
import logging
import json

import pandas as pd

from biom import load_table
from utils import biom_summarize_table

def main():
    """ 
    Runs data processing scripts to turn raw data (from data/raw)
    into cleaned data ready to be analyzed (saved in data/processed).
    """
    logger = logging.getLogger(__name__)
    logger.info('making final data set from raw data')

    # Process population per North Carolina county
    raw_pop_fp = os.path.join(raw_dir, 'PEP_2016_PEPANNRES.csv')
    pop = pd.read_csv(raw_pop_fp, dtype={'GEO.id2': str}) 
    pop.set_index('GEO.id2', drop=True, inplace=True)
    new_cols = {'respop7{}'.format(year) : str(year) for year in range(2010, 2017)}
    new_cols['GEO.display-label'] = 'county'
    pop.rename(columns=new_cols, inplace=True)
    new_cols = list(new_cols.values())
    new_cols.sort()
    pop = pop[new_cols]
    pop['county'] = pop['county'].map(lambda x: x[:x.find(',')])
    pop.set_index('county', drop=True, inplace=True)
    processed_pop_fp = os.path.join(processed_local_dir, 'nc-county-pop-2010-2016.csv')
    pop.to_csv(processed_pop_fp)

    # Load processed BIOM tables at national level and filter to only NC samples
    only_nc_triangle = lambda values, id_, md: md['state'] == 'North Carolina' and md['county'] in ['Wake County', 'Orange County', 'Durham County']
    biom_files = ['ITS-outdoor.biom', 'ITS-indoor.biom', '16S-outdoor.biom', '16S-indoor.biom']
    for biom_file in biom_files:
        from_biom_fp = os.path.join(processed_national_dir, biom_file)
        table = load_table(from_biom_fp)
        table.filter(only_nc_triangle, axis='sample', inplace=True)
        
        to_biom_fp = os.path.join(processed_local_dir, biom_file)
        generated_by = "Transformation of {0} applied by {1}".format(from_biom_fp, __file__)
        with open(to_biom_fp, 'w') as f:
            table.to_json(generated_by=generated_by, direct_io=f)
        
        # Also produce biom summary text files 
        summary_file = biom_file.partition('.')[0] + '-summary.txt'
        biom_summarize_table(to_biom_fp, os.path.join(processed_local_dir, summary_file))


if __name__ == '__main__':
    log_fmt = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logging.basicConfig(level=logging.INFO, format=log_fmt)

    # Define paths to various data directories
    # project_dir = os.path.join(os.path.dirname(__file__), os.pardir, os.pardir)
    project_dir = os.path.join(os.path.dirname(__file__), os.pardir)
    data_dir = os.path.join(project_dir, 'data')
    raw_dir = os.path.join(data_dir, 'raw', 'local')
    processed_local_dir = os.path.join(data_dir, 'processed', 'local')
    processed_national_dir = os.path.join(data_dir, 'processed', 'national')

    main()
