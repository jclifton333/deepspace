"""
This first screen the user sees when the app starts.  Should include buttons to navigate to 1) sample upload + model
fitting and 2) sample selection (for mapviewer).
"""
from mpl_toolkits.basemap import Basemap
# from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
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
from app.gui.sample_upload import SampleUploadGUI
from app.gui.sample_select import SampleSelectGUI

if sys.version_info[0] < 3:
  import Tkinter as Tk
  from Tkinter import messagebox
else:
  import tkinter as Tk
  from tkinter import messagebox


class MainMenuGUI(Tk.Frame):
  def __init__(self, master, controller):
    Tk.Frame.__init__(self, master, width=275, height=200)
    self.master = master
    self.controller = controller

    # Main menu label
    label = Tk.Label(self, text="DustBuster geolocation tool")

    # Navigation buttons
    run_model_button = Tk.Button(self, text="Run model on new sample",
                                 command=lambda: controller.show_frame("SampleUploadGUI"))
    display_sample_button = Tk.Button(self, text="Display sample in map viewer",
                                      command=lambda: controller.show_frame("SampleSelectGUI"))

    label.grid(row=0)
    run_model_button.grid(row=1, sticky="nsew")
    display_sample_button.grid(row=2, sticky="nsew")

    # label.place(relx=0.5, rely=0.6, anchor=Tk.CENTER)
    # run_model_button.place(relx=0.5, rely=0.56, anchor=Tk.CENTER)
    # display_sample_button.place(relx=0.5, rely=0.44, anchor=Tk.CENTER)
