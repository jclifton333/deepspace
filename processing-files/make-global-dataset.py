# -*- coding: utf-8 -*-
import os
import logging
import time

import click
import dotenv
import googlemaps

import pdb

import pandas as pd
import numpy as np

from biom import load_table
from utils import biom_summarize_table

@click.command()
@click.option('--min-counts', default=3000, type=int)
def main(min_counts):
    """
    Runs data processing scripts to turn raw data (from data/raw)
    into cleaned data ready to be analyzed (saved in data/processed).
    """
    logger = logging.getLogger(__name__)
    logger.info('making final data set from raw data')

    # Build interim metadata
    raw_metadata_fp = os.path.join(raw_dir, 'metadata-final-modified.csv')
    dateparse = lambda x: pd.datetime.strptime(x, '%d-%b-%y')
    #df = pd.read_csv(raw_metadata_fp, encoding = "ISO-8859-1", index_col='SampleID',
    #        parse_dates=['Date'], date_parser=dateparse)
    df = pd.read_csv(raw_metadata_fp, encoding = "ISO-8859-1", index_col='SampleID')
    df.rename(columns={'Latitude': 'lat', 'Longitude': 'lon'}, inplace=True)
    df = df[['lat', 'lon']]
    df['lat'] = df['lat'].map(to_decimal_degrees)
    df['lon'] = df['lon'].map(to_decimal_degrees)
    df.index.names = ['#SampleID']
    df.dropna(inplace=True)
    # Query Google Maps API for reverse geocoding: use a point's lat, lon to find
    # address which includes country, state, county, city, postal_code, ...

    # First we retrieve the Google Maps API Key stored in .env in project_dir
    # You must edit the .env file to include your own Google API key! More info:
    # https://developers.google.com/maps/documentation/geocoding/get-api-key
    # dotenv.load_dotenv(os.path.join(project_dir, '.env'))
    dotenv.load_dotenv('env')
    gmaps = googlemaps.Client(key=os.environ.get('GOOGLE_API_KEY'))

    # Next we process the results array returned by Google Maps into usable
    # pieces of the address, specifically, all names in area_names
    area_names = [
            'country',
            'administrative_area_level_1',
            'administrative_area_level_2',
            'administrative_area_level_3',
            'administrative_area_level_4',
            'administrative_area_level_5',
            'locality'
            ]
    areas = pd.DataFrame(index=df.index, columns=area_names, dtype=str)
    area_names = set(area_names)
    print("Querying Google Maps API for country, ..., locality of each point")
    for id_, lat, lon in df[['lat', 'lon']].itertuples():
        print("Retrieving areas for sample point w/ id: {}".format(id_))
        time.sleep(0.15)  # 10 queries per second (Google Maps API requires <50 qps)
        try:
          response = gmaps.reverse_geocode((lat, lon))
        except:
          print("reverse geocode didn't work")
          print('lat: {} lon: {}'.format(type(lat), type(lon)))
        if response:
            result = response[0]  # extract areas from top result
            for address_component in result['address_components']:
                area_name = set(address_component['types']).intersection(area_names)
                if area_name:
                    areas.set_value(id_, area_name, address_component['long_name'])
    
    df = pd.concat([df, areas], axis=1)
    
    # There is disputed territory w/ Turkey on the island of Cyprus and Google 
    # Maps does not return 'Cyprus' for lat, lon in this territory. However, we
    # say any points on this island are from Cyprus.
    is_cyprus = df['lat'].between(34.39, 35.85) & df['lon'].between(32.00, 34.89)
    df['country'][is_cyprus] = 'Cyprus'

    interim_metadata_fp = os.path.join(interim_dir, 'metadata.txt')
    df.to_csv(interim_metadata_fp, sep='\t')

    # Make interim biom data (raw biom data with sample metadata)
    click.echo("Making interim BIOM files from raw")
    md = df.to_dict(orient='index')
    biom_src = {
            'final':'final.biom'
#           'combined':'plant_fungal_combined.biom'}
#            'ITS': 'DOD_global_dust_ITS_otu_table_wTax.biom',
#            '16S':'DoD_16S_otu_table_wTax_noChloroMito.biom',
#            'trnL': 'otu.table.trnl.unoise2.sintax.taxfilt.mc8.biom',
#            'data2-fungal':'100ITS.biom'
        }
    biom_files = []
    md_sample_ids = df['SampleID']
    for barcode_sequence, biom_file in list(biom_src.items()):
        # Add sample metadata to biom
        raw_biom_fp = os.path.join(raw_dir, biom_file)
        interim_biom_file = barcode_sequence + '.biom'
        biom_files.append(interim_biom_file)
        interim_biom_fp = os.path.join(interim_dir, interim_biom_file)
        table = load_table(raw_biom_fp)

        # Make sure we only get sample ids in both md and table
        table_sample_ids = table.ids(axis='sample')
        overlapping_sample_ids = np.intersect1d(md_sample_ids, table_sample_ids)
        overlap_filter = lambda values, id_, md: id_ in overlapping_sample_ids
        table = table.filter(overlap_filter, axis='sample')

        table.add_metadata(md, axis='sample')
        with open(interim_biom_fp, 'w') as f:
            table.to_json(generated_by=__file__, direct_io=f)

        # Also produce biom summary text files
        summary_file = barcode_sequence + '-summary.txt'
        raw_summary_fp = os.path.join(raw_dir, summary_file)
        interim_summary_fp = os.path.join(interim_dir, summary_file)
        biom_summarize_table(raw_biom_fp, raw_summary_fp)
        biom_summarize_table(interim_biom_fp, interim_summary_fp)

    # If we examine the interim summary files we notice there are many
    # samples with very few counts. Let's filter by samples with a
    # minimum number of sequence reads, given by the min_count option

    # Make processed biom data (interim biom data filtered by a few conditions)

    # If we examine the interim summary files we notice there are many samples 
    # with very few counts. Let's filter by samples with a minimum number of 
    # sequence reads, given by the min_counts option
    at_or_exceeds_min_count = lambda values, id_, md: sum(values) >= min_counts
    # We also remove any samples that, perhaps due to error in lat, lon records,
    # do not fall in the study's list of countries.
    valid_countries = [
            'Mexico',
            'Colombia',
            'Costa Rica',
            'Trinidad and Tobago',
            'Uruguay',
            'Argentina',
            'Ghana',
            'South Africa',
            'Nigeria',
            'Czechia',
            'Croatia',
            'Hungary',
            'Jordan',
            'Macedonia (FYROM)',
            'Cyprus',
            'Turkey',
            'Azerbaijan',
            #'Bahrain',
            'Kuwait',
            'Qatar',
            'Oman',
            'Georgia',
            'Pakistan',
            'Kazakhstan',
            'Malaysia',
            'New Zealand',
            'Australia',
            'South Korea',
            'Vietnam'
            ]
    # in_valid_country = lambda values, id_, md: md['country'] in valid_countries

    click.echo("Making processed BIOM files from interim")
    for biom_file in biom_files:
        interim_biom_fp = os.path.join(interim_dir, biom_file)
        table = load_table(interim_biom_fp)
        table.filter(at_or_exceeds_min_count, axis='sample', inplace=True)
        # table.filter(in_valid_country, axis='sample', inplace=True)
        processed_biom_fp = os.path.join(processed_dir, biom_file)
        with open(processed_biom_fp, 'w') as f:
            table.to_json(generated_by=__file__, direct_io=f)
        
        # Also produce biom summary text files
        summary_file = biom_file.partition('.')[0] + '-summary.txt'
        biom_summarize_table(processed_biom_fp, os.path.join(processed_dir, summary_file))


def to_decimal_degrees(x):
    if is_float(x):
        # Already in decimal form
        return float(x)
    elif is_float(x[:-1]):
        # In decimal form with cardinal direction
        last_char = x[-1]
        dec = float(x[:-1])
        return dec * (-1 if last_char in ['S', 'W'] else 1)
    elif '°' in x:
        # In degree form (DMS)
        x = x.replace('°', '')
        xs = x.split()
        last_char = xs[-1]
        dms = xs[:-1]
        dec = 0.0
        for n, d in enumerate(dms):
            dec += float(d) / 60 ** n
        return dec * (-1 if last_char in ['S', 'W'] else 1)
    else:
        return ValueError


def is_float(x):
    try:
        float(x)
        return True
    except ValueError:
        return False


if __name__ == '__main__':
    log_fmt = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logging.basicConfig(level=logging.INFO, format=log_fmt)

    # Define paths to various data directories
    # project_dir = os.path.join(os.path.dirname(__file__), os.pardir, os.pardir)
    project_dir = os.path.join(os.path.dirname(__file__), os.pardir)
    data_dir = os.path.join(project_dir, 'data')
    raw_dir = os.path.join(data_dir, 'raw', 'global')
    interim_dir = os.path.join(data_dir, 'interim', 'global')
    processed_dir = os.path.join(data_dir, 'processed', 'global')
    print('raw dir: ', raw_dir)
    main()
