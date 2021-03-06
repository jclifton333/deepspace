import click

import numpy as np
import pandas as pd
import os
from sklearn.metrics import confusion_matrix
import readline
import rpy2.robjects as ro
from rpy2.robjects import r, pandas2ri
import pdb
pandas2ri.activate()

#@click.command()
#@click.option('--centroid')
#@click.option('--centroid-fp')
#@click.option('--title', default='')
#@click.option('--model', default=None)
#@click.argument('input_')
#@click.argument('output')
def plot_confusion_matrix(input_, output, centroid='country', centroid_fp=os.getcwd() + '/data/external/global/country-centroids-final.csv', title='', model='DeepSpace'):
    if not isinstance(input_, str):
      input_ = str(input_, 'utf-8')
    if not isinstance(centroid_fp, str):
      centroid_fp = centroid_fp.decode('utf-8')
    results = pd.read_csv(input_)
    if model:
        results = results[results['model'] == model]
    centroids_df = pd.read_csv(centroid_fp, index_col=centroid)
    centroids_df.sort_values(by=['lon', 'lat'], inplace=True)
    centroids = centroids_df.index.values
    results = results[['true_' + centroid, 'pred_' + centroid]].dropna()
    results.loc[np.isin(results.true_country, ['Djibouti', 'Somalia']), 'true_country'] = \
      'Djibouti-Somalia'
    cnf_mat = confusion_matrix(results['true_' + centroid].as_matrix(),
                               results['pred_' + centroid].as_matrix(),
                               labels=centroids)
    ro.globalenv['centroid'] = centroid
    ro.globalenv['centroids'] = centroids
    ro.globalenv['cnf_mat'] = cnf_mat
    ro.globalenv['title'] = title
    ro.globalenv['output'] = output
    r("""
    library(ggplot2)
    library(reshape2)
    library(viridis)
    theme_set(theme_minimal() + 
        theme(axis.text.x = element_text(angle = 45, hjust = 1)))
    
    rownames(cnf_mat) <- centroids
    colnames(cnf_mat) <- centroids
    df <- melt(cnf_mat)
    
    df[df == 0] <- NA
    df$Var1 <- ordered(df$Var1, levels = rev(centroids))
    df$high <- df$value >= 10

    p <- ggplot(df, aes(x = Var2, y = Var1))
    p <- p + geom_tile(aes(fill = factor(value)))
    p <- p + geom_text(aes(label = value, color = high))
    p <- p + scale_color_manual(values = c('black', 'white'))
    p <- p + scale_fill_viridis(discrete = TRUE, direction = -1)
    p <- p + labs(title = title,
        x = paste('Predicted', centroid, 'of origin'),
        y = paste('True', centroid, 'of origin'))
    p <- p + guides(fill = FALSE, color = FALSE)
    p <- p + coord_equal()
    p
    ggsave(output, width = 12, height = 12)
    """)

if __name__ == '__main__':
    input_dict = {'coarse': os.getcwd() + '/final-coarse-cross-val.csv',
                   'mixed': os.getcwd() + '/final-mixed-cross-val.csv',
		  'fine': os.getcwd() + '/final-fine-cross-val.csv'}
    for name, fp in input_dict.items():
      output = 'final-{}.png'.format(name)
      # output = 'final-{}.png'.format(name)
      plot_confusion_matrix(fp, output)
