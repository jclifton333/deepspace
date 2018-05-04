# -*- coding: utf-8 -*-
import os
import logging
import json
import time

import click
import dotenv
import googlemaps

import pandas as pd

from biom import load_table
from utils import biom_summarize_table

@click.command()
@click.option('--min-counts', default=1, type=int)
def main(min_counts):
    """ 
    Runs data processing scripts to turn raw data (from data/raw)
    into cleaned data ready to be analyzed (saved in data/processed).
    """
    logger = logging.getLogger(__name__)
    logger.info('making final data set from raw data')

    # Process population per state
    print("Processing population file")
    raw_pop_fp = os.path.join(raw_dir, 'PEP_2016_PEPANNRES.csv')
    pop = pd.read_csv(raw_pop_fp, dtype={'GEO.id2': str})
    pop.set_index('GEO.id2', drop=True, inplace=True)
    geo_ids = ['{:02d}'.format(i+1) for i in range(56)]  # states ids range 01 to 56
    geo_ids = list(set(geo_ids).intersection(set(pop.index)))  # remove missing vals
    geo_ids.sort()
    pop = pop.loc[geo_ids]
    new_cols = {'respop7{}'.format(year) : str(year) for year in range(2010, 2017)}
    new_cols['GEO.display-label'] = 'state'
    pop.rename(columns=new_cols, inplace=True)
    new_cols = list(new_cols.values())
    new_cols.sort()
    pop = pop[new_cols]
    pop.set_index('state', drop=True, inplace=True)
    processed_pop_fp = os.path.join(processed_dir, 'state-pop-2010-2016.csv')
    pop.to_csv(processed_pop_fp)

    # Build interim metadata
    print("Building interim metadata file")
    raw_metadata_fp = os.path.join(raw_dir, 'Master_dataset_20Dec13.csv')
    df = pd.read_csv(raw_metadata_fp, dtype={'Conf_code': str},
            usecols=['Conf_code', 'latitude', 'longitude'])
    new_cols = {
            'Conf_code': '#SampleID',  # necessary for biom add-metadata to work
            'latitude': 'lat', 
            'longitude': 'lon'
            }
    df.rename(columns=new_cols, inplace=True)
    df.set_index('#SampleID', drop=True, inplace=True)
    df = df[~df.index.duplicated(keep='first')]  # remove duplicate ids
    df.dropna(inplace=True)  # remove samples with missing lat or lon

    # Query Google Maps API for reverse geocoding: use a point's lat, lon to find 
    # address which includes country, state, county, city, postal_code, ...
    
    # First we retrieve the Google Maps API Key stored in .env in project_dir
    # You must edit the .env file to include your own Google API key! More info:
    # https://developers.google.com/maps/documentation/geocoding/get-api-key
    dotenv.load_dotenv(os.path.join(project_dir, '.env'))
    gmaps = googlemaps.Client(key=os.environ.get('GOOGLE_API_KEY'))

    # Next we process the results array returned by Google Maps into usable 
    # pieces of the address, specifically, all names in area_names
    area_names = [
            'country', 'administrative_area_level_1', 
            'administrative_area_level_2', 'locality'
            ]
    areas = pd.DataFrame(index=df.index, columns=area_names, dtype=str)
    area_names = set(area_names)
    print("Querying Google Maps API for city, county, state of each point")
    for id_, lat, lon in df.itertuples():
        print("Retrieving areas for sample point w/ id: {}".format(id_))
        time.sleep(0.15)  # 10 queries per second (Google Maps API requires <50 qps)
        response = gmaps.reverse_geocode((lat, lon))
        result = response[0]  # extract areas from top result
        for address_component in result['address_components']:
            area_name = set(address_component['types']).intersection(area_names)
            if area_name:
                areas.set_value(id_, area_name, address_component['long_name'])
    
    # Finish by replacing some of the names with aliases specific to USA data
    # and concatenate 
    area_alias = {
            'administrative_area_level_1': 'state',
            'administrative_area_level_2': 'county',
            'locality': 'city'
            }
    areas.rename(columns=area_alias, inplace=True)

    df = pd.concat([df, areas], axis=1) 

    interim_metadata_fp = os.path.join(interim_dir, 'metadata.txt')
    df.to_csv(interim_metadata_fp, sep='\t')

    # Split each biom on location of sample collection: outdoor vs. indoor
    md = df.to_dict(orient='index')
    biom_src = {
            'ITS': 'ITS_otu_table_wTax.biom',
            '16S': '16S_otu_table_wTax.biom'
        }
    loc_name = {
            'O': 'outdoor',
            'I': 'indoor'
        } 
    is_not_control = lambda values, id_, md: any([id_.endswith('.' + loc) for loc in loc_name.keys()])
    group_by_loc = lambda id_, md: id_[-1]
    biom_files = []

    print("Processing raw BIOM files to interim files")
    for barcode_sequence, biom_file in list(biom_src.items()):
        raw_biom_fp = os.path.join(raw_dir, biom_file)
        summary_file = barcode_sequence + '-summary.txt'
        biom_summarize_table(raw_biom_fp, os.path.join(raw_dir, summary_file))
        
        table = load_table(raw_biom_fp)
        table.filter(is_not_control, axis='sample', inplace=True)
        loc_tables = table.partition(group_by_loc, axis='sample')
        
        for loc, loc_table in loc_tables:
            interim_biom_file = '{0}-{1}.biom'.format(barcode_sequence, loc_name[loc])
            biom_files.append(interim_biom_file)
            
            # Remove location tags from home ID and add sample metadata
            sample_ids = loc_table.ids(axis='sample')
            for i, id_ in enumerate(sample_ids):
                sample_ids[i] = id_.partition('.')[0]
            loc_table.add_metadata(md, axis='sample')
            
            interim_biom_fp = os.path.join(interim_dir, interim_biom_file)
            generated_by = "Transformation of {0} applied by {1}".format(raw_biom_fp, __file__)
            with open(interim_biom_fp, 'w') as f:
                loc_table.to_json(generated_by=generated_by, direct_io=f)
            
            # Also produce biom summary text file
            summary_file = interim_biom_file.partition('.')[0] + '-summary.txt'
            biom_summarize_table(interim_biom_fp, os.path.join(interim_dir, summary_file))

    # Make processed biom data (interim biom data filtered by a few conditions)
    
    # If we examine the interim summary files we notice there are many
    # samples with very few counts. Let's filter by samples with a
    # minimum number of sequence reads, given by the min_count option
    at_or_exceeds_min_count = lambda values, id_, md: sum(values) >= min_counts

    # We also remove any samples that do not belong to the continental US. 
    # In other words, remove samples from Alaska and Hawaii.
    in_continental_usa = lambda values, id_, md: md['state'] not in ['Alaska', 'Hawaii']
    
    print("Processing interim BIOM files to final files")
    for biom_file in biom_files:
        interim_biom_fp = os.path.join(interim_dir, biom_file)
        table = load_table(interim_biom_fp)
        table.filter(at_or_exceeds_min_count, axis='sample', inplace=True)
        table.filter(in_continental_usa, axis='sample', inplace=True)
        
        processed_biom_fp = os.path.join(processed_dir, biom_file)
        generated_by = "Transformation of {0} applied by {1}".format(interim_biom_fp, __file__)
        with open(processed_biom_fp, 'w') as f:
            table.to_json(generated_by=generated_by, direct_io=f)
        
        # Also produce biom summary text files 
        summary_file = biom_file.partition('.')[0] + '-summary.txt'
        biom_summarize_table(processed_biom_fp, os.path.join(processed_dir, summary_file))

    print("Done.")


if __name__ == '__main__':
    log_fmt = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logging.basicConfig(level=logging.INFO, format=log_fmt)

    # Define paths to various data directories
    project_dir = os.path.join(os.path.dirname(__file__), os.pardir, os.pardir)
    data_dir = os.path.join(project_dir, 'data')
    raw_dir = os.path.join(data_dir, 'raw', 'national')
    interim_dir = os.path.join(data_dir, 'interim', 'national')
    processed_dir = os.path.join(data_dir, 'processed', 'national')

    main()
