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
  with open(fname) as f:
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

    # Make heatmap
    fig = Figure(figsize=(5, 4), dpi=100)
    ax = fig.add_subplot(111)
    m = Basemap(projection='cyl',llcrnrlat=-90,urcrnrlat=90,\
                llcrnrlon=-180,urcrnrlon=180,resolution='c', ax=ax)

    x, y = m(self.lons, self.lats)
    x = np.compress(np.logical_or(x < 1.e20, y < 1.e20), x)
    y = np.compress(np.logical_or(x < 1.e20, y < 1.e20), y)
    CS = m.hexbin(x, y, C=self.probs)
    m.drawcoastlines()

    # Create GUI

    root = Tk.Tk()
    root.wm_title("Embedding in TK")


    # Frame for hypothesis test
    def _ht(self, fig, canvas):
      print('hypothesis test')
      canvas.get_tk_widget().destroy()

      # Make heatmap
      newfig = Figure(figsize=(5, 4), dpi=100)
      ax = newfig.add_subplot(111)

      m = Basemap(projection='cyl', llcrnrlat=-90, urcrnrlat=90, \
                  llcrnrlon=-180, urcrnrlon=180, resolution='c', ax=ax)

      x, y = m(lons, lats)
      x = np.compress(np.logical_or(x < 1.e20, y < 1.e20), x)
      y = np.compress(np.logical_or(x < 1.e20, y < 1.e20), y)
      CS = m.hexbin(x, y, C=probs)
      m.drawcoastlines()

      # Plot circle
      lat = float(e1.get())
      lon = float(e2.get())
      radius = float(e3.get())
      circlept_lat, circlept_lon = get_destination_coords(lat, lon, 0, radius)
      x, y = m(lat, lon)
      x2, y2 = m(circlept_lat, circlept_lon)
      circle = plt.Circle((x, y), y2-y, fill=False)
      ax.add_patch(circle)

      canvas = FigureCanvasTkAgg(fig, master=root)
      canvas.get_tk_widget().grid(row=0, column=2)
      canvas.show()

    # a tk.DrawingArea
    canvas = FigureCanvasTkAgg(fig, master=root)
    canvas.get_tk_widget().grid(row=0, column=2)
    canvas.show()

    frame = Tk.Frame(master=root)
    frame.grid(row=0, column=0, sticky="n")
    Tk.Label(master=root, text="Lat").grid(row=0, column=0)
    Tk.Label(master=root, text="Lon").grid(row=1, column=0)
    Tk.Label(master=root, text="Radius").grid(row=2, column=0)
    e1 = Tk.Entry(master=frame)
    e2 = Tk.Entry(master=frame)
    e3 = Tk.Entry(master=frame)
    e1.grid(row=0, column=1)
    e2.grid(row=1, column=1)
    e3.grid(row=2, column=1)
    Tk.Button(master=root, text='Hypothesis test', command=(lambda f=fig, c=canvas: _ht(f, c))).grid(row=4, column=0)

    # Toolbar
    toolbarFrame = Tk.Frame(master=root)
    toolbarFrame.grid(row=1, column=2)
    toolbar = NavigationToolbar2TkAgg(canvas, toolbarFrame)
    toolbar.update()
    # canvas._tkcanvas.grid(row=1, column=2)


    # Quit button
    def _quit():
      root.quit()     # stops mainloop
      root.destroy()  # this is necessary on Windows to prevent
                      # Fatal Python Error: PyEval_RestoreThread: NULL tstate


    button = Tk.Button(master=root, text='Quit', command=_quit)
    button.grid(row=2, column=2)

Tk.mainloop()