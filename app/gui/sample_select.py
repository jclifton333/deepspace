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

import sys
THIS_DIR = os.path.dirname(os.path.abspath(__file__))
PKG_DIR = os.path.join(THIS_DIR, '..', '..')
sys.path.append(PKG_DIR)
from app.gui.map_viewer import MapViewerGUI

import sys
if sys.version_info[0] < 3:
  import Tkinter as Tk
  from Tkinter import messagebox
else:
  import tkinter as Tk
  from tkinter import messagebox


GEOJSON_DIRNAME = 'geojson'
GEOJSON_DIR = os.path.join(THIS_DIR, GEOJSON_DIRNAME)


class SampleSelectGUI(Tk.Frame):
  def __init__(self, master, controller):
    Tk.Frame.__init__(self, master)
    self.controller = controller

    # Create listbox
    self.master = master
    self.sample_listbox = Tk.Listbox(self, selectmode=Tk.SINGLE)
    self.sample_listbox.grid(row=0, column=0)
    self.fill_listbox()

    # Make button for displaying mapviewer for current selection
    Tk.Button(master=self, text="Display selection in mapviewer",
              command=self._open_in_mapviewer).grid(row=1, column=0)

    Tk.Button(master=self, text="Return to main menu",
              command=lambda: controller.show_frame("MainMenuGUI")).grid(row=2, column=0)

  def fill_listbox(self):
    # Fill listbox with entries
    self.sample_fname_list = [fname for fname in os.listdir(GEOJSON_DIR) if fname.endswith('.json')]
    self.sample_display_name_list = [fname.split('/')[-1].split('.json')[0] for fname in self.sample_fname_list]
    # self.sample_dictionary = {display_name: fname for display_name, fname in zip(self.sample_display_name_list,
    #                                                                              self.sample_fname_list)}
    for display_name in self.sample_display_name_list:
      self.sample_listbox.insert(Tk.END, display_name)

  def refresh(self):
    self.sample_listbox.delete(0, 'end')
    self.fill_listbox()

  def _open_in_mapviewer(self):
    selected_sample_ix = self.sample_listbox.curselection()[0]
    display_name = self.sample_display_name_list[selected_sample_ix]
    fname_to_open = self.sample_fname_list[selected_sample_ix]
    # fname_to_open = self.sample_dictionary[selected_sample_name]
    mapviewer_window = Tk.Toplevel(self)
    mapviewer = MapViewerGUI(mapviewer_window, fname_to_open, display_name)


if __name__ == "__main__":
  root = Tk.Tk()
  sample_select = SampleSelectGUI(root)
  root.mainloop()


