import biom
import numpy as np
import pandas as pd
import pdb


def count_countries(fname, metadata_fname):
  biom_table = biom.load_table(fname)
  metadata = pd.read_csv(metadata_fname)
  country_count_dict = {}
  for sample_id in biom_table.ids(axis='sample'):
    country = metadata['country'].values[np.where(metadata['SampleID'] == sample_id)][0]
    # sample_metadata = biom_table.metadata(sample_id, 'sample')
    # country = sample_metadata['country']
    if country in country_count_dict.keys():
      country_count_dict[country] += 1
    else:
      country_count_dict[country] = 1
  return country_count_dict


if __name__ == '__main__':
  final_fname = '/mnt/c/Users/Jesse/Desktop/forensic-geolocation-master/deepspace/data/processed/global/final.biom'
  metadata_fname_ = \
    '/mnt/c/Users/Jesse/Desktop/forensic-geolocation-master/deepspace/data/raw/global/metadata-final-modified.csv'
  country_count_dict_ = count_countries(final_fname, metadata_fname_)
  print(country_count_dict_)
  # for k, v in country_count_dict_.values():
  #   print(k, v)
