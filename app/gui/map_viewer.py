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
import os
import json
import geopy
from geopy.distance import VincentyDistance, vincenty
import matplotlib.pyplot as plt
import datetime
from reportlab.pdfgen import canvas
from reportlab.platypus import Image, Paragraph, SimpleDocTemplate
from reportlab.lib.styles import getSampleStyleSheet

import sys
THIS_DIR = os.path.dirname(os.path.abspath(__file__))
PKG_DIR = os.path.join(THIS_DIR, '..', '..')
sys.path.append(PKG_DIR)
from app.report_generation import build_pdf_report

if sys.version_info[0] < 3:
    import Tkinter as Tk
    from Tkinter import messagebox
else:
    import tkinter as Tk
    from tkinter import messagebox


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


IMAGES_DIR = os.path.join(THIS_DIR, "..", "images")

class MapViewerGUI(object):
  def __init__(self, master, json_fname, sample_name):
    self.master = master
    master.title("Map viewer")

    # Get lats longs and values for making heatmap
    fname = os.path.join("geojson", json_fname)
    self.lats, self.lons, self.probs = get_coords_and_probs_from_json(fname)

    # Initialize stuff for pdf report generation
    self.image_fnames = []  # Filenames for images to be included in PDF report
    self.ht_results_data = None
    self.probs_and_coords_data = \
      np.array([np.array([np.round(lat, decimals=3), np.round(lon, decimals=3), np.round(prob, decimals=3)])
                for lat, lon, prob in zip(self.lats, self.lons, self.probs)])
    self.probs_and_coords_data = self.probs_and_coords_data[(-self.probs_and_coords_data[:, -1]).argsort()]
    self.probs_and_coords_data = \
      [["Lat", "Lon", "Prob"]] + [[float(row[0]), float(row[1]), float(row[2])] for row in self.probs_and_coords_data]
    self.view_counter = 0

    # Create GUI
    self.map_title = sample_name
    self.draw_basemap()
    self.canvas.show()
    base_map_fname = os.path.join(IMAGES_DIR, "{}.png".format(self.map_title))
    self.fig.savefig(base_map_fname)
    self.image_fnames.append(os.path.abspath(base_map_fname))

    # HT input
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

    # Clear HT
    Tk.Button(master=self.ht_frame, text="Reset", command=self._reset_map).grid(row=5, column=0)

    # Add view to report
    Tk.Button(master=self.ht_frame, text="Add view to PDF report",
              command=self._add_view_to_report).grid(row=6, column=0)

    # Generate PDF
    Tk.Button(master=self.ht_frame, text="Generate PDF report", command=self._generate_pdf_report).grid(row=7, column=0)

    # Quit button
    button = Tk.Button(master=self.master, text='Quit', command=self._quit)
    button.grid(row=2, column=2)

  def _generate_pdf_report(self):
    build_pdf_report(self.map_title, self.image_fnames, self.probs_and_coords_data, self.ht_results_data)

  def sum_probabilities_in_circle(self, lat, lon, radius):
    """
    For 'hypothesis testing'.

    :param lat:
    :param lon:
    :param radius: In km.
    :return:
    """
    prob_sum = 0.0
    for ix, (lat_, lon_, prob) in enumerate(zip(self.lats, self.lons, self.probs)):
      if vincenty((lat, lon), (lat_, lon_)).kilometers < radius:
        prob_sum += prob
    return prob_sum

  def draw_basemap(self):
    """
    For drawing underlying map and probabilities associated to the geojson for this window.

    :return:
    """
    # Make heatmap
    self.fig = Figure(figsize=(5, 4), dpi=100)
    self.ax = self.fig.add_subplot(111)
    self.ax.set_title(self.map_title)
    self.m = Basemap(projection='cyl',llcrnrlat=-90,urcrnrlat=90,\
                     llcrnrlon=-180,urcrnrlon=180,resolution='c', ax=self.ax)

    x, y = self.m(self.lons, self.lats)
    self.formatted_lons = np.compress(np.logical_or(x < 1.e20, y < 1.e20), x)
    self.formatted_lats = np.compress(np.logical_or(x < 1.e20, y < 1.e20), y)
    CS = self.m.hexbin(self.formatted_lons, self.formatted_lats, C=self.probs)
    self.m.drawcoastlines()
    self.m.drawcountries()

    # Display in GUI
    self.master.wm_title("Embedding in TK")
    self.master.columnconfigure(2, weight=1)
    self.master.rowconfigure(0, weight=1)
    # Frame for hypothesis test
    # a tk.DrawingArea
    self.canvas = FigureCanvasTkAgg(self.fig, master=self.master)
    self.canvas.get_tk_widget().grid(row=0, column=2, sticky="nwse")
    # self.canvas.get_tk_widget().grid(row=0, column=2)

    # Toolbar
    self.toolbarFrame = Tk.Frame(master=self.master)
    self.toolbarFrame.grid(row=1, column=2)
    toolbar = NavigationToolbar2TkAgg(self.canvas, self.toolbarFrame)
    toolbar.update()

  def _add_view_to_report(self):
    # Save image
    view_fname = os.path.join(IMAGES_DIR, "{}-view-{}.png".format(self.map_title, self.view_counter))
    self.fig.savefig(view_fname)
    self.image_fnames.append(os.path.abspath(view_fname))
    self.view_counter += 1

  def _ht(self):
    self.ax.clear()
    self.draw_basemap()

    # Plot circle
    center_lat = float(self.e1.get())
    center_lon = float(self.e2.get())
    radius = float(self.e3.get())
    circlept_lat, circlept_lon = get_destination_coords(center_lat, center_lon, 60, radius)
    x, y = self.m(center_lat, center_lon)
    x2, y2 = self.m(circlept_lat, circlept_lon)
    # x2, y2 = m(center_lat, center_lon + 10)
    basemap_radius = np.linalg.norm(np.array([x, y]) - np.array([x2, y2]))
    circle = plt.Circle((x, y), basemap_radius, fill=False)
    self.ax.add_patch(circle)
    self.canvas.draw()

    # Save image
    ht_map_fname = os.path.join(IMAGES_DIR, "{}-{}-{}-{}.png".format(self.map_title, center_lat, center_lon, radius))
    self.fig.savefig(ht_map_fname)
    self.image_fnames.append(os.path.abspath(ht_map_fname))

    # Add probabilities in circle
    sum_prob = np.round(self.sum_probabilities_in_circle(center_lat, center_lon, radius), decimals=3)
    hypothesis_test_result = \
      "Lat: {}\nLon: {}\n Radius: {}km\n Probability: {}".format(center_lat, center_lon, radius, sum_prob)
    messagebox.showinfo("Hypothesis test result", hypothesis_test_result)

    # Add to hypothesis test results
    if self.ht_results_data is None:
      self.ht_results_data = \
        [["Center lat", "Center lon", "Radius (km)", "Probability"],
         [float(center_lat), float(center_lon), float(radius), float(sum_prob)]]
    else:
      self.ht_results_data.append([float(center_lat), float(center_lon), float(radius)])

  def _reset_map(self):
    self.ax.clear()
    self.draw_basemap()
    self.canvas.show()

  # Quit button
  def _quit(self):
    self.master.quit()     # stops mainloop
    self.master.destroy()  # this is necessary on Windows to prevent
                           # Fatal Python Error: PyEval_RestoreThread: NULL tstate


if __name__ == '__main__':
  root = Tk.Tk()
  map_viewer_ = MapViewerGUI(root)
  root.mainloop()
