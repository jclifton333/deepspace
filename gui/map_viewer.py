"""
Sample GUI with Basemap figure, from
https://stackoverflow.com/questions/35164123/using-basemap-as-a-figure-in-a-python-gui.

Adapting heatmap stuff from
http://bagrow.com/dsv/heatmap_basemap.html
"""
from mpl_toolkits.basemap import Basemap
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib.figure import Figure
import numpy as np
import json
import geopy
from geopy.distance import VincentyDistance
import matplotlib.pyplot as plt


import sys
if sys.version_info[0] < 3:
    import Tkinter as Tk
else:
    import tkinter as Tk


def get_destination_coords(lat, lon, bearing, distance):
  """
  Used to get a point on HT circle.
  :param lat:
  :param lon:
  :param bearing: in degrees
  :param distance: in km
  :return:
  """
  origin = geopy.Point(lat, lon)
  destination = VincentyDistance(kilometers=distance).destination(origin, bearing)
  return destination.latitude, destination.longitude


def get_coords_and_probs_from_json(json_fname):
  with open(json_fname) as f:
    data = json.load(f)

  lats, lons, probs = [], [], []

  for features in data['features']:
    coords = features['geometry']['coordinates'][0]
    lon, lat = np.mean(np.array(coords), axis=0)
    lats.append(lat)
    lons.append(lon)
    prob = features['properties']['probability']
    probs.append(prob)

  lats = np.array(lats)
  lons = np.array(lons)
  probs = np.array(probs)

  return lats, lons, probs


class MapViewerGUI(object):
  def __init__(self, master):
    self.master = master
    master.title("Map viewer")

    # Get lats longs and values for making heatmap
    # fname = master.geojson_filename
    fname = "Costa RicaC.json"
    self.lats, self.lons, self.probs = get_coords_and_probs_from_json(fname)


    # Create GUI
    self.draw_basemap()
    self.canvas.show()

    self.ht_frame = Tk.Frame(master=self.master)
    self.ht_frame.grid(row=0, column=0, sticky="n")
    Tk.Label(master=self.ht_frame, text="Lat").grid(row=0, column=0)
    Tk.Label(master=self.ht_frame, text="Lon").grid(row=1, column=0)
    Tk.Label(master=self.ht_frame, text="Radius").grid(row=2, column=0)
    self.e1 = Tk.Entry(master=self.ht_frame)
    self.e2 = Tk.Entry(master=self.ht_frame)
    self.e3 = Tk.Entry(master=self.ht_frame)
    self.e1.grid(row=0, column=1)
    self.e2.grid(row=1, column=1)
    self.e3.grid(row=2, column=1)
    Tk.Button(master=self.ht_frame, text='Hypothesis test',
              command=self._ht).grid(row=4, column=0)

    # Toolbar
    self.toolbarFrame = Tk.Frame(master=self.master)
    self.toolbarFrame.grid(row=1, column=2)
    toolbar = NavigationToolbar2TkAgg(self.canvas, self.toolbarFrame)
    toolbar.update()
    # canvas._tkcanvas.grid(row=1, column=2)

    # Quit button
    button = Tk.Button(master=self.master, text='Quit', command=self._quit)
    button.grid(row=2, column=2)

  def draw_basemap(self):
    """
    For drawing underlying map and probabilities associated to the geojson for this window.

    :return:
    """
    # Make heatmap
    fig = Figure(figsize=(5, 4), dpi=100)
    self.ax = fig.add_subplot(111)
    self.m = Basemap(projection='cyl',llcrnrlat=-90,urcrnrlat=90,\
                     llcrnrlon=-180,urcrnrlon=180,resolution='c', ax=self.ax)

    x, y = self.m(self.lons, self.lats)
    self.formatted_lons = np.compress(np.logical_or(x < 1.e20, y < 1.e20), x)
    self.formatted_lats = np.compress(np.logical_or(x < 1.e20, y < 1.e20), y)
    CS = self.m.hexbin(self.formatted_lons, self.formatted_lats, C=self.probs)
    self.m.drawcoastlines()

    # Display in GUI
    self.master.wm_title("Embedding in TK")
    self.master.columnconfigure(2, weight=1)
    self.master.rowconfigure(0, weight=1)
    # Frame for hypothesis test
    # a tk.DrawingArea
    self.canvas = FigureCanvasTkAgg(fig, master=self.master)
    self.canvas.get_tk_widget().grid(row=0, column=2, sticky="nwse")
    # self.canvas.get_tk_widget().grid(row=0, column=2)

  def _ht(self):
    print('hypothesis test')
    self.ax.clear()
    self.draw_basemap()

    # Plot circle
    center_lat = float(self.e1.get())
    center_lon = float(self.e2.get())
    radius = float(self.e3.get())
    # center_lat = 0.0
    # center_lon = 0.0
    # radius = 1000
    circlept_lat, circlept_lon = get_destination_coords(center_lat, center_lon, 60, radius)
    x, y = self.m(center_lat, center_lon)
    x2, y2 = self.m(circlept_lat, circlept_lon)
    # x2, y2 = m(center_lat, center_lon + 10)
    basemap_radius = np.linalg.norm(np.array([x, y]) - np.array([x2, y2]))
    circle = plt.Circle((x, y), basemap_radius, fill=False)
    self.ax.add_patch(circle)

    self.canvas.draw()

  # Quit button
  def _quit(self):
    self.master.quit()     # stops mainloop
    self.master.destroy()  # this is necessary on Windows to prevent
                           # Fatal Python Error: PyEval_RestoreThread: NULL tstate


if __name__ == '__main__':
  root = Tk.Tk()
  map_viewer_ = MapViewerGUI(root)
  root.mainloop()