import pdb
import pandas as pd
import numpy as np
import geopy
from geopy.distance import VincentyDistance, vincenty


def get_destination_coords(lat, lon, bearing, distance):
  """
  :param lat:
  :param lon:
  :param bearing: in degrees
  :param distance: in km
  :return:
  """
  origin = geopy.Point(lat, lon)
  destination = VincentyDistance(kilometers=distance).destination(origin, bearing)
  return destination.latitude, destination.longitude


def get_hexagon_coords(lat, lon, distance):
  bearings = [60, 120, 180, 240, 300, 360]
  coords_list = []
  for b in bearings:
    coords_list.append(get_destination_coords(lat, lon, b, distance))
  return np.array(coords_list)


def get_pairwise_distances(lat_lon_pairs):
  num_points = len(lat_lon_pairs)
  dist_mat = np.empty((num_points, num_points,))
  dist_mat[:] = 1e10
  for i in range(num_points):
    for j in range(i+1, num_points):
      d = vincenty(lat_lon_pairs[i], lat_lon_pairs[j]).km
      dist_mat[i,j] = dist_mat[j,i] = d
  return dist_mat


def get_hexagons_for_list(lat_lon_pairs, domain_ids):
  dist_mat = get_pairwise_distances(lat_lon_pairs)
  n_domain = len(lat_lon_pairs)
  if n_domain > 1:
    hex_df = pd.DataFrame.from_dict({'domain': [], 'lat':[], 'lon':[]})
    for i in range(n_domain):
      lat, lon = lat_lon_pairs[i]
      dist = np.min((np.min(dist_mat[i,:]) / 2, 100))
      hex_coords = get_hexagon_coords(lat, lon, dist)
      max_dist = np.sort(np.unique(get_pairwise_distances(list(zip(hex_coords[:,0], hex_coords[:,1])))))[-2]
      if max_dist > 1000:
        pdb.set_trace()
      domain_hex_df = pd.DataFrame.from_dict({'domain': [np.array(domain_ids)[i]]*6, 'lat': hex_coords[:,0],
                                              'lon': hex_coords[:,1]})
      hex_df = hex_df.append(domain_hex_df)
  else: # I think this is redundant but oh well
    lat, lon = lat_lon_pairs[0]
    hex_coords = get_hexagon_coords(lat, lon, 100)
    hex_df = pd.DataFrame.from_dict({'domain':  [np.array(domain_ids)[0]]*6, 'lat': hex_coords[:,0],
                                              'lon': hex_coords[:,1]})
  return hex_df


def get_hexagons_from_domain_df(domain_df):
  countries = domain_df['country'].unique()
  hex_df = pd.DataFrame.from_dict({'domain': [], 'lat':[], 'lon':[]})
  for country in countries:
    print('Country: {}'.format(country))
    sub_df = domain_df.loc[domain_df['country'] == country, ]
    country_hexagons = get_hexagons_for_list(list(zip(sub_df['lat'], sub_df['lon'])), sub_df.domain)
    hex_df = hex_df.append(country_hexagons)
    hex_df.domain = pd.to_numeric(hex_df.domain, downcast='integer')
  return hex_df


if __name__ == '__main__':
  domain_df = pd.read_csv('../data/external/global/domain-final.csv')
  hex_df = get_hexagons_from_domain_df(domain_df)
  hex_df.to_csv('../data/external/global/domain-final-hex.csv')





