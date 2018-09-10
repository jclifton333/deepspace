import os
import click

import numpy as np
import pandas as pd
import pickle as pkl
from scipy import stats

from biom import load_table

from models.points import SpatialPoints
from models.deepspace import SpatialClassifier, Geolocator

from keras.models import Sequential
from keras.layers.core import Dense, Dropout, Activation
from keras.optimizers import Adam
from keras.utils import np_utils

import argparse
import pdb

np.random.seed(881)  # for reproducibility


def fit_global_final(seeds, dnn_epochs, dnn_batch_size):
        
    def fit_dnn(sp, partition, sample_weight, model_fname):
        model = Sequential()
        model.add(Dense(2048, input_shape=(sp.shape[1], )))
        model.add(Activation('relu'))
        model.add(Dropout(0.3))
        model.add(Dense(1024))
        model.add(Activation('relu'))
        model.add(Dropout(0.3))
        model.add(Dense(1024))
        model.add(Activation('relu'))
        model.add(Dropout(0.3))
        model.add(Dense(partition.shape[0]))
        model.add(Activation('softmax'))
        model.compile(loss='categorical_crossentropy', optimizer=Adam(), 
                metrics=['accuracy'])
        clf = SpatialClassifier(model, partition)
        clf.fit(sp, model_fname, to_categorical=True, sample_weight=sample_weight, 
                epochs=dnn_epochs, batch_size=dnn_batch_size, verbose=True)
        return clf

    area_names = ['locality', 'country', 'administrative_area_level_2', 'administrative_area_level_3',
                  'administrative_area_level_4', 'administrative_area_level_5']
    coord_names = ['lat, lon']

    # Load partition data
    partitions_fname = 'partitions/{}-partitions.p'.format(seeds)
    partitions_dict = pkl.load(open(partitions_fname, 'rb'))
    part_nums = list(partitions_dict.keys())
    
     # Load biom data
    train_table = load_table('final-global-data/final.biom').pa()
    taxa_threshold = 0.0
    eliminate_exceptionally_rare_taxa = lambda values_, id_, md: np.mean(values_ > 0) > taxa_threshold
    train_table.filter(eliminate_exceptionally_rare_taxa, axis='observation')
    sp_train = SpatialPoints.from_biom_table(train_table, verbose=True,
                                             coord_names=coord_names, area_names=area_names, ids_name='ids')

    # Save OTUs that are used in model
    otus_to_keep_fname = 'global-otus.txt'
    otus_to_keep = train_table.ids(axis='observation')
    with open(otus_to_keep_fname) as file:
        t_separated_otus = ''
        for otu in otus_to_keep:
          t_separated_otus += '{}\t'.format(otu)
        file.write()

    sample_weights = None

    if seeds == 'none':
        pass         
    else:
        model_name = 'dnn'
        # Train a model_name classifier on every partition
        partition_counter = 0
        with click.progressbar(part_nums, label='Fitting {}'.format(model_name)) as bar:
            for part_num in bar:
                coords_values = partitions_dict[part_num]
                coords, values = coords_values['coords'], coords_values['values']
                part = SpatialPoints(coords=coords, values=values)
                model_fname = 'fitted-models/{}/final-{}-{}.h5'.format(seeds, seeds, partition_counter)
                fit_dnn(sp_train, part, sample_weights, model_fname)
                partition_counter += 1


if __name__ == '__main__':
    SEEDS = 'mixed'
    DNN_EPOCHS = 5
    DNN_BATCH_SIZE = 64

    fit_global_final(SEEDS, DNN_EPOCHS, DNN_BATCH_SIZE)

