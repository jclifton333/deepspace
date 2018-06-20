import os
import pandas as pd
from biom import load_table, Table
import json
import pdb

def main():

  # Reads in the DoD dust ASV data.
  # Converts this into a .biom file.
  
  reftable = load_table(os.path.join('..','data','processed','global','ITS.biom'))
  #allowed = list(reftable.ids())
  conv = pd.read_table('../data/raw/global/DoD_Global_Dust_ITS_final_tab.txt',header=1)
  labels = list(conv.columns.values)
  #cleaned = conv[allowed]
  cleaned = conv
  pdb.set_trace()

  # Deletes all the OTUs without any values left in the original.


  # Create a new OTU table with the original processed table's observation metadata 
  # and the new OTUs from the table above.

  
  obs_ids = list(map(lambda x: "Taxon " + str(x), range(1,cleaned.shape[0]+1)))
  newTab = Table(cleaned.as_matrix(),observation_ids = obs_ids, sample_ids = allowed)
  
  # Cuts the portion of the text in 
  refjstr = reftable.to_json('s')
  refcolstart = refjstr.find("columns")
  metadat = refjstr[refcolstart:len(refjstr)]
  newjstr = newTab.to_json(__file__)
  newcolstart = newjstr.find("columns")
  combjstr = newjstr[0:newcolstart] + metadat
  combj = json.loads(combjstr)
  newTab = Table.from_json(combj)

  processed_biom_fp = os.path.join(os.getcwd(),'final.biom')
  with open(processed_biom_fp, 'w') as f:
            newTab.to_json(generated_by=__file__, direct_io=f)

  # Log the conversion of dada into count data the models can make use of.


if __name__ == '__main__':
  main()