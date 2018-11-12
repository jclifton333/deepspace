import os
import pandas as pd
import datetime
import pdb


def get_reg_dict(domain, sp_pred_regs, probs, sample_id_str_):
  """
  :param domain:
  :param sp_pred_regs:
  :param sample_id_str_: string for name of sample, from header of user-input csv
  :return reg_dict_dict: dictionary of sample_id:reg_dict pairs
  """
  DIR = os.path.dirname(os.path.abspath(__file__))
  # domain_geom_fp = os.path.join(DIR, 'domain-final-hex.csv')
  domain_geom_fp = os.path.join(DIR, 'domain-final-hex-2.csv')

  domain_geometry = pd.read_csv(domain_geom_fp)
  domain_geom_dict = {id_: {} for id_ in domain_geometry.domain.unique()}
  for id_, subdf in domain_geometry.groupby('domain'):
    coords = subdf[['lon', 'lat']].as_matrix().tolist()
    domain_geom_dict[id_] = {'type': 'Polygon', 'coordinates': [coords]}

  # Write probability region results to JSON files for interactive 
  # visualization with HTML + CSS + JS (Leaflet.js & D3.js)

  reg_dict_dict = {}
  timestamp = datetime.datetime.now().strftime("%y%m%d_%H%M%S")
  for sample_id, sp_pred_reg in sp_pred_regs.items():

    # This initializes confidence region assignment of each cell in domain 
    # to 1; will be overwritten for cells at lower confidence levels 
    df_reg = pd.DataFrame(1.0, index=domain.ids, columns=['reg'])
    regs = list(map(float, sp_pred_reg.keys()))
    regs.sort(reverse=True)
    for reg in regs:
      sp_pred_ids = sp_pred_reg[str(reg)].ids
      for id_ in sp_pred_ids:
        df_reg.set_value(id_, 'reg', reg)
    features_list = [
      {
        'type': 'Feature',
        # 'properties': {'id': str(id_), 'probability': float(probs[id_])},
        'properties': {'id': str(sample_id_str_), 'probability': float(probs[id_]), 'reg': df_reg['reg'][id_],
                       'country': domain.areas.country[id_]},
        'geometry': domain_geom_dict[id_]
      }    
      for id_, reg_s in df_reg.iterrows()
    ]
    reg_dict = {
      'type': 'FeatureCollection', 
      'crs': {'type': 'name', 'properties': {'name': 'urn:ogc:def:crs:OGC:1.3:CRS84'}},
      'features': features_list,
      'timestamp': timestamp
    }
    reg_dict_dict[sample_id] = reg_dict
  return reg_dict_dict



