"""
This first screen the user sees when the app starts.  Should include buttons to navigate to 1) sample upload + model
fitting and 2) sample selection (for mapviewer).
"""
from mpl_toolkits.basemap import Basemap
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib.figure import Figure
import numpy as np
import json
import geopy
import os
from geopy.distance import VincentyDistance, vincenty
import matplotlib.pyplot as plt

import sys
THIS_DIR = os.path.dirname(os.path.abspath(__file__))
PKG_DIR = os.path.join(THIS_DIR, '..', '..')
sys.path.append(PKG_DIR)
from deepspace.gui.sample_upload import SampleUploadGUI
from deepspace.gui.sample_select import SampleSelectGUI

if sys.version_info[0] < 3:
  import Tkinter as Tk
  from Tkinter import messagebox
else:
  import tkinter as Tk
  from tkinter import messagebox


class MainMenuGUI(object):
  def __init__(self, master):
    self.master = master

    # Navigation buttons
    Tk.Button(master=self.master, text="Run model on new sample",
              command=self._navigate_to_sample_upload).grid(row=0, column=0)
    Tk.Button(master=self.master, text="Select sample to view in map",
              command=self._navigate_to_sample_select).grid(row=1, column=0)

  def _navigate_to_sample_upload(self):
    pass

  def _navigate_to_sample_select(self):
    pass
