import os

import numpy as np
import pandas as pd
import pickle as pkl

from biom import load_table
from models.points import SpatialPoints

import argparse
import pdb

np.random.seed(881)  # for reproducibility


def create_global_partitions(domain_fp):
  df = pd.read_csv(domain_fp, index_col='domain')
  coord_names = ['lat', 'lon']
  area_names = ['locality', 'country', 'administrative_area_level_2', 'administrative_area_level_3',
                'administrative_area_level_4', 'administrative_area_level_5']
  domain = SpatialPoints(coords=df[coord_names], areas=df[area_names])

  # Load biom data
  train_table = load_table('data/processed/global/final.biom').pa()

  # Set number of partitions and number
  n_samples = train_table.shape[1]
  seed_vec_mixed = [np.round(x * n_samples).astype(int) for x in np.arange(0.05, 0.5, step=0.05)]
  seed_vec_coarse = seed_vec_mixed[:2]
  seed_vec_fine = seed_vec_mixed[-2:]

  # Create partitions
  def create_seed_partitions(seed_name, seed_vec, seed_num_partitions):
    n_seeds = np.random.choice(seed_vec, size=seed_num_partitions)
    parts = [domain.sample(n_seed, reset_index=True) for n_seed in n_seeds]
    partition_dict = {}
    for i in range(seed_num_partitions):
      part = parts[i]
      partition_dict[i] = {'coords': part.coords, 'values': part.values}
    partitions_dict_fname = '{}-partitions.p'.format(seed_name)
    pkl.dump(partition_dict, open(partitions_dict_fname, 'wb'))

  create_seed_partitions('mixed', seed_vec_mixed, 50)
  create_seed_partitions('coarse', seed_vec_coarse, 50)
  create_seed_partitions('fine', seed_vec_fine, 50)


if __name__ == '__main__':
  domain_fp = 'data/external/global/domain-final.csv'
  create_global_partitions(domain_fp)

