"""
Here we define the controller for the app.  We want to be able to stack Frames on top of each other in order to switch
between main menu, sample upload menu, and sample select menu, following
https://stackoverflow.com/questions/7546050/switch-between-two-frames-in-tkinter.
"""

from mpl_toolkits.basemap import Basemap
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib.figure import Figure
import numpy as np
import json
import geopy
import os
import shutil
from geopy.distance import VincentyDistance, vincenty
import matplotlib.pyplot as plt

import sys
THIS_DIR = os.path.dirname(os.path.abspath(__file__))
PKG_DIR = os.path.join(THIS_DIR, '..', '..')
IMAGE_DIR = os.path.join(THIS_DIR, '..', 'images')
sys.path.append(PKG_DIR)

from app.gui.sample_upload import SampleUploadGUI
from app.gui.sample_select import SampleSelectGUI
from app.gui.main_menu import MainMenuGUI

if sys.version_info[0] < 3:
  import Tkinter as Tk
  from Tkinter import messagebox
else:
  import tkinter as Tk
  from tkinter import messagebox


class GUIController(Tk.Tk):
  def __init__(self):
    Tk.Tk.__init__(self)

    # the container is where we'll stack a bunch of frames
    # on top of each other, then the one we want visible
    # will be raised above the others
    container = Tk.Frame(self)
    container.pack(side="top", fill="both", expand=True)
    container.grid_rowconfigure(0, weight=1)
    container.grid_columnconfigure(0, weight=1)

    self.frames = {}
    for F in (MainMenuGUI, SampleUploadGUI, SampleSelectGUI):
      page_name = F.__name__
      frame = F(master=container, controller=self)
      self.frames[page_name] = frame

      # put all of the pages in the same location;
      # the one on the top of the stacking order
      # will be the one that is visible.
      frame.grid(row=0, column=0, sticky="nsew")

    self.show_frame("MainMenuGUI")

    # Clean out images directory
    for file in os.listdir(IMAGE_DIR):
      if file.endswith(".png"):
        file_path = os.path.join(IMAGE_DIR, file)
        if os.path.isfile(file_path):
          os.unlink(file_path)

  def show_frame(self, page_name):
    frame = self.frames[page_name]
    frame.tkraise()
    if page_name == "SampleSelectGUI":
      frame.refresh()


if __name__ == "__main__":
  app = GUIController()
  app.mainloop()

