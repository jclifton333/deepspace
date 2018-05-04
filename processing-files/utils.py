# -*- coding: utf-8 -*-
import subprocess

def biom_summarize_table(input, output):
    subprocess.call("biom summarize-table -i {0} -o {1}".format(input, output), shell=True)
