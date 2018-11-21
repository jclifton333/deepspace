import os
import shutil

import numpy as np
import pandas as pd
import pickle as pkl
import sys
import logging
import pdb
import datetime

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
PKG_DIR = os.path.join(THIS_DIR, '..', '..')
sys.path.append(PKG_DIR)
from app.model.write_to_geojson import write_reg_dict_to_geojson
from app.model.get_reg_dict import get_reg_dict
from app.model.models.points import SpatialPoints
from app.model.models.deepspace import SpatialClassifier, Geolocator

from biom import load_table
import pandas as pd

from keras.models import load_model
import keras.backend as K

import re

np.random.seed(881)  # for reproducibility
logging.getLogger().setLevel(logging.INFO)
DIR = os.path.dirname(os.path.abspath(__file__))


def string_is_positive_integer(string):
  """
   Check if string is a positive integer.

  :param string:
  :return:
  """
  try:
    val = int(string)
    if val >= 0:
      return True
    else:
      return False
  except ValueError:
    return False


def split_taxon_name(string):
  """
  Split "Taxon[integer]" into "Taxon", "[integer]"
  """
  found_integer_at_end = False
  for i, s in enumerate(string):
    if string_is_positive_integer(s):
      break
  taxon_part = string[:i]
  number_part = string[i:]
  if taxon_part == 'Taxon_':  # I do this so I don't have to change the existing files formatted as 'Taxon_[integer]'.
    taxon_part = 'Taxon'
  return [taxon_part, number_part]


def get_int_from_str(str):
  """
  Return integer in string, for getting partition number from filename.
  """
  int_label = int(re.search(r'\d+', str).group())
  return int_label


def read_split_convert_compute(fname, names_of_samples_to_exclude=[]):
  # Create reports directory if it doesn't exist
  reports = os.path.join(DIR, '..', 'reports')
  if not os.path.exists(reports):
    os.makedirs(reports)

  # Make temporary directory for split csvs and bioms
  tmp = os.path.join(DIR, 'tmp')
  if not os.path.exists(tmp):
    os.makedirs(tmp)

  # Split into biom files and run model on each
  res_dict = {}
  biom_fnames, sample_names, dropped_otus = \
    read_split_convert_csv_to_biom(fname, names_of_samples_to_exclude=names_of_samples_to_exclude)
  for biom_fname, sample_name in zip(biom_fnames, sample_names):
    res_string = compute_predictions(biom_fname, sample_name, dropped_otus)
    res_dict[sample_name] = res_string

  # Get rid of tmp directory
  shutil.rmtree(tmp)
  return res_dict


def read_split_convert_csv_to_biom(fname, names_of_samples_to_exclude=[]):
  MIN_COUNT = 3000  # Don't analyze samples with count below MIN_COUNT

# Get list of OTUs that should be kept
  keep_otu_fp = os.path.join(DIR, 'global-otus.txt')
  OTUs_to_keep_str = open(keep_otu_fp, 'r')
  OTUs_to_keep_list = OTUs_to_keep_str.read().split('\n')[:-1]  # Leave off '\n' at the end

  # Get sample data and get rid of rows with taxa that we can't include
  dropped_otus = []
  dropped_samples = []
  logging.info('Reading input csv or xlsx.')
  logging.info('fname: {}'.format(fname))
  if fname.endswith(".csv"):
    df = pd.read_csv(fname, index_col=0)
  elif fname.endswith(".xlsx"):
    df = pd.read_excel(fname, index_col=0)

  for ix in df.index:
    if ix not in OTUs_to_keep_list:
      dropped_otus.append(ix)
      df.drop(ix, axis=0, inplace=True)

  # ToDo: Get sorting right
  # Get taxa numbers from strings - ASSUMES LAST DIGIT ENCOUNTERED IS CORRECT NUMBER
  # Subtract 1 because taxa are 1-indexed
  taxa_numbers = [[int(s) - 1 for s in split_taxon_name(taxa_str) if s.isdigit()][-1] for taxa_str in df.index]
  sorted_taxa_ixs = np.argsort(taxa_numbers)
  df = df.iloc[sorted_taxa_ixs]

  # Make temporary directory for split csvs and bioms
  tmp = os.path.join(DIR, 'tmp')
  if not os.path.exists(tmp):
    os.makedirs(tmp)

  biom_fnames = []
  sample_names = []
  logging.info('Converting input sample data to individual .biom files.')
  names_of_samples_to_keep = [colname for colname in df.columns.values if colname not in names_of_samples_to_exclude]
  for col_number, colname in enumerate(names_of_samples_to_keep):
    # ToDo: What about duplicate rows??
    # ToDo: What about non-numeric inputs etc?
    sample_df = pd.DataFrame({colname: [0]*len(OTUs_to_keep_list), 'otus': OTUs_to_keep_list})
    sample_df.set_index('otus', inplace=True)
    sample_df.loc[df.index, colname] = df[colname].astype(int)

    # Split off sample column and save to tsv
    basename = 'sample-{}_otus.txt'.format(colname)
    sample_fname = os.path.join(tmp, basename)
    if sample_fname not in os.listdir(tmp):
      sample_df.to_csv(sample_fname, header=True, sep='\t')
    else:
      logging.info("File {} already in tmp".format(basename))
    total_count = np.sum(sample_df[colname])

    if total_count < MIN_COUNT:
      dropped_samples.append(colname)
      logging.info("Sample {} has count below min count of {}; it won't be analyzed.".format(colname, MIN_COUNT))
    else:
      # Convert to biom
      basename = 'sample-{}_otus.biom'.format(colname)
      biom_sample_fname = os.path.join(tmp, basename)
      if basename not in os.listdir(tmp):
        logging.info("Converting sample {} to biom.".format(colname))
        string_to_execute = 'biom convert -i "{}" -o "{}" --table-type="OTU table" --to-json'.format(sample_fname,
                                                                                                     biom_sample_fname)
        os.system(string_to_execute)
      else:
        logging.info("biom file {} already in tmp".format(basename))

      biom_fnames.append(biom_sample_fname)
      sample_names.append(colname)

  # Log dropped samples
  timestamp = datetime.datetime.now().strftime("%y%m%d_%H%M%S")
  fname_base = fname.split('/')[-1].split('.csv')[0]
  dropped_samples_basename = '{}-dropped-samples-{}.txt'.format(fname_base, timestamp)

  dropped_samples_fname = os.path.join(DIR, '../reports', dropped_samples_basename)
  with open(dropped_samples_fname, 'w') as file:
    for word in dropped_samples:
      file.write(word + '\n')

  return biom_fnames, sample_names, dropped_otus


def compute_predictions(biom_fname, sample_name, dropped_otus):
  logging.info("Computing prediction for sample at {}.".format(biom_fname))

  area_names = ['locality', 'country', 'administrative_area_level_2', 'administrative_area_level_3',
                'administrative_area_level_4', 'administrative_area_level_5']
  coord_names = ['lat', 'lon']
  domain_fp = os.path.join(DIR, 'domain-final.csv')
  keep_otu_fp = os.path.join(DIR, 'global-otus.txt')
  seeds = 'mixed'
  regions = [0.5, 0.75, 0.9]

  logging.info('Loading data to predict')
  pred_table = load_table(biom_fname).pa()
  # OTUs_to_keep_str = open(keep_otu_fp, 'r')
  # OTUs_to_keep_list = OTUs_to_keep_str.read().split('\t')[:-1]  # Leave off '\n' at the end
  # keep_otu_filter = lambda values, id_, md: id_ in OTUs_to_keep_list
  # pred_table = pred_table.filter(keep_otu_filter, axis='observation', inplace=False)
  sp_pred = SpatialPoints.from_biom_table(pred_table, verbose=True,
                                          coord_names=coord_names, area_names=area_names, ids_name='ids')
  logging.info('Loading domain data')
  df = pd.read_csv(domain_fp, index_col='domain')
  domain = SpatialPoints(coords=df[coord_names], areas=df[area_names])

  logging.info('Loading partition data')
  partitions_dict_fname = os.path.join(DIR, 'partitions/{}-partitions.p'.format(seeds))
  partitions_dict = pkl.load(open(partitions_dict_fname, 'rb'))

  logging.info('Computing likelihoods')
  dirname = os.path.join(DIR, 'fitted-models/{}'.format(seeds))
  # dirname = 'E:/'
  likelihoods = []
  # models = [File for File in os.listdir(dirname) if
  #           File.endswith(".h5")]  # Get all files with .h5 extension (these are the fitted models)
  # if not models:
  #   logging.info('No models of type {}.  Cannot compute predictions.'.format(seeds))
  #   return
  # else:
  for model_name in os.listdir(dirname):
    if model_name.endswith(".h5"):
    # for model_name in models:
      # Get partition and corresponding model
      partition_num = get_int_from_str(model_name)
      coords_values = partitions_dict[partition_num]
      coords, values = coords_values['coords'], coords_values['values']
      model_name = dirname + '/' + model_name
      part = SpatialPoints(coords=coords, values=values)
      model = load_model(model_name)
      logging.info('Computing partition {}'.format(partition_num))
      # Construct classifier object and get likelihod
      sp_clf = SpatialClassifier(model, part)
      lik = sp_clf.evaluate_likelihood(sp_pred.values, domain)
      likelihoods.append(lik)
      K.clear_session()

  # Get prediction regions
  logging.info('Getting prediction regions')
  likelihood_test = pd.concat(likelihoods, axis=1)
  geo = Geolocator(domain)
  probs = likelihood_test.sum(axis=1).transform(lambda x: x / x.sum())
  sp_pred_regs = geo.predict_regions(likelihood_test, regions)

  logging.info('Sample outputs to json')
  # Output geojsons
  reg_dict_dict = get_reg_dict(domain, sp_pred_regs, probs, sample_name)
  res_string = write_reg_dict_to_geojson(reg_dict_dict, seeds, dropped_otus)
  return res_string


if __name__ == '__main__':
  logging.info('sys argv {}'.format(sys.argv))
  fname = sys.argv[1]
  read_split_convert_compute(fname)
