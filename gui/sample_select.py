"""
Interface for selecting sample output to display in map viewer.
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
from .map_viewer import MapViewerGUI


import sys
if sys.version_info[0] < 3:
  import Tkinter as Tk
  from Tkinter import messagebox
else:
  import tkinter as Tk
  from tkinter import messagebox

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
GEOJSON_DIRNAME = 'geojson'
GEOJSON_DIR = os.path.join(THIS_DIR, GEOJSON_DIRNAME)


class SampleSelectGUI(object):
  def __init__(self, master):
    # Create listbox
    self.master = master
    self.sample_listbox = Tk.Listbox(self.master, selectmode=Tk.SINGLE)
    self.sample_listbox.grid(row=0, column=0)

    # Fill listbox with entries
    self.sample_fname_list = [fname for fname in os.listdir(GEOJSON_DIR) if fname.endswith('.json')]
    self.sample_display_name_list = [fname.split('/')[-1].split('.csv')[0] for fname in self.sample_fname_list]
    self.sample_dictionary = {display_name: fname for display_name, fname in zip(self.sample_display_name_list,
                                                                                 self.sample_fname_list)}
    for display_name in self.sample_display_name_list:
      self.sample_listbox.insert(Tk.END, display_name)

    # Make button for displaying mapviewer for current selection
    Tk.Button(master=self.master, text="Display selection in mapviewer",
              command=self._open_in_mapviewer).grid(row=1, column=0)

  def _open_in_mapviewer(self):
    selected_sample_name = self.sample_listbox.curselection()
    fname_to_open = self.sample_dictionary[selected_sample_name]
    mapviewer_window = Tk.Toplevel(self.master)
    mapviewer = MapViewerGUI(mapviewer_window, fname_to_open)


if __name__ == "__main__":
  root = Tk.Tk()
  sample_select = SampleSelectGUI(root)
  root.mainloop()


