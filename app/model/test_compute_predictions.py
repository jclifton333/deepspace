from compute_predictions import read_split_convert_compute
import os


dirname = os.path.dirname(os.path.abspath(__file__))
# fname = os.path.join(dirname, '../server/test-samples/final-global-sample-1_B.biom')
fname = os.path.join(dirname, '../server/test-samples/example.csv')
# fname = os.path.join(dirname, '../server/test-samples/GEOLOC0001_ModelFile.csv')
# fname = os.path.join(dirname, '../server/test-samples/DemoSetFinal_SPECIES__ModelFile_missed.csv')

if __name__ == '__main__':
  # names_of_samples_to_exclude = ["Costa RicaC", "Country10a", "Country10b", "Country11a", "Country11b",
  #                                "Country12aE", "Country1a", "Country1b", "Country2a", "Country2b",
  #                                "Country3a", "Country3b", "Country4a", "Country4b", "Country5a", "Country5b",
  #                                "Country6a", "Country6b", "Country7aA", "Country7bA", "Country8b", "Country9bD",
  #                                "DC-Mix1", "DC-Mix2", "DC-Mix3", "DC-Mix4", "EFG-Mix1", "EFG-Mix2", "EFG-Mix3",
  #                                "Env swab 1", "Env swab 2", "Env swab 3", "Env swab 4", "Env swab 5", "Env swab 6",
  #                                "Env tape 1", "Env tape 2"]
  names_of_samples_to_exclude = []
  read_split_convert_compute(fname, names_of_samples_to_exclude=names_of_samples_to_exclude)

