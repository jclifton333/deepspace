from compute_predictions import read_split_convert_compute
import os


dirname = os.path.dirname(os.path.abspath(__file__))
fname = os.path.join(dirname, "sample-samples", "single-sample.csv")
# fname = os.path.join(dirname, '../server/test-samples/DemoSetFinal_SPECIES__ModelFile_missed.csv')

if __name__ == '__main__':
  names_of_samples_to_exclude = []
  read_split_convert_compute(fname, names_of_samples_to_exclude=names_of_samples_to_exclude)

