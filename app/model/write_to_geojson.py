import json
import os
import pandas as pd
import numpy as np
import datetime
import pdb


def write_reg_dict_to_geojson(reg_dict_dict, seeds, dropped_otus):
  """
  :param reg_dict_dict: dictionary of sample_id:reg_dict pairs to write to geojson
  :param seeds:
  :param model_type:
  :return:
  """

  # Create directory in which to save geojsons
  DIR = os.path.dirname(os.path.abspath(__file__))
  json_output_fp = os.path.join(DIR, '../gui/geojson')
  if not os.path.exists(json_output_fp):
    os.makedirs(json_output_fp)

  # Loop thru dictionary to save each reg_dict
  sample_id = 0

  for sample_id, reg_dict in reg_dict_dict.items():
    json_fp = os.path.join(json_output_fp, '{}.json'.format(sample_id))
    with open(json_fp, 'w') as f:
      json.dump(reg_dict, f)

    # Save report to text file
    # Read off probabilities and centroids
    features_list = reg_dict['features']
    probs_and_centroids = []
    for feature in features_list:
      probability = feature['properties']['probability']
      coordinates = np.array(feature['geometry']['coordinates'][0])
      centroid = (np.mean(coordinates[:, 0]), np.mean(coordinates[:, 1]))
      country = feature['properties']['country']
      probs_and_centroids.append((probability, country, centroid))
    probs_and_centroids = sorted(probs_and_centroids, key=lambda x: x[0], reverse=True)

    # Save to tsv
    probs_and_centroids_dict = {'probs': [], 'lat': [], 'lon': [], 'country': []}
    for prob, country, centroid in probs_and_centroids:
      probs_and_centroids_dict['probs'].append(prob)
      # probs_and_centroids_dict['lat'].append(centroid[0])
      # probs_and_centroids_dict['lon'].append(centroid[1])
      probs_and_centroids_dict['lat'].append(centroid[1])
      probs_and_centroids_dict['lon'].append(centroid[0])
      probs_and_centroids_dict['country'].append(country)
    probs_and_centroids__df = pd.DataFrame(probs_and_centroids_dict)
    # timestamp = datetime.datetime.now().strftime("%y%m%d_%H%M%S")
    timestamp = reg_dict["timestamp"]
    basename = '{}-probabilities-{}.txt'.format(sample_id, timestamp)
    probs_and_centroids_fname = os.path.join(DIR, '../reports', basename)
    probs_and_centroids__df.to_csv(probs_and_centroids_fname, sep='\t')

    dropped_otus_basename = '{}-dropped-otus-{}.txt'.format(sample_id, timestamp)
    dropped_otus_fname = os.path.join(DIR, '../reports', dropped_otus_basename)
    with open(dropped_otus_fname, 'w') as file:
      for word in dropped_otus:
        file.write(word + '\n')

    # Return probs and lat/lons as string, this will be used in pdf report
    f = open(probs_and_centroids_fname, "r")
    raw_probs_string = f.read()

  return raw_probs_string

