import sys
import os
THIS_DIR = os.path.dirname(os.path.abspath(__file__))
PKG_DIR = os.path.join(THIS_DIR, '..', '..')
sys.path.append(PKG_DIR)
from app.model.compute_predictions import read_split_convert_compute

if sys.version_info[0] < 3:
  import Tkinter as Tk
  from Tkinter import messagebox
else:
  import tkinter as Tk
  from tkinter import messagebox

import tkinter.filedialog
from tkinter import messagebox
import csv


class SampleUploadGUI(Tk.Frame):
  def __init__(self, master, controller):
    Tk.Frame.__init__(self, master)
    self.controller = controller

    self.filename = ""
    self.csv_fname_to_analyze = None
    self.master = master
    csvfile = Tk.Label(self, text="File").grid(row=1, column=0)
    bar = Tk.Entry(self).grid(row=1, column=1)

    # Buttons
    y = 7
    self.cbutton = Tk.Button(self, text="OK", command=self.process_csv)
    y += 1
    self.cbutton.grid(row=10, column=3, sticky="we")
    self.bbutton = Tk.Button(self, text="Browse", command=self.browsecsv)
    self.bbutton.grid(row=1, column=3)
    self.run_model_button = Tk.Button(self, text="Run model", command=self.run_model)
    self.run_model_button.grid(row=11, column=3)
    self.return_to_menu_button = Tk.Button(self, text="Return to main menu",
                                           command=lambda: controller.show_frame("MainMenuGUI")).grid(row=12, column=3)

  def run_model(self):
    if self.csv_fname_to_analyze is None:
      run_model_message = \
        "No data uploaded. Nothing will happen."
      messagebox.showinfo("Running model", run_model_message)
    else:
      run_model_message = \
        "Running model on samples in {}.  This will take about 7 minutes per sample.".format(self.csv_fname_to_analyze)
      messagebox.showinfo("Running model", run_model_message)
      res_dict = read_split_convert_compute(self.csv_fname_to_analyze)

  def browsecsv(self):
    from tkinter.filedialog import askopenfilename

    Tk.Tk().withdraw()
    self.filename = askopenfilename()

  def process_csv(self):
    if self.filename:
      self.csv_fname_to_analyze = self.filename


if __name__ == "__main__":
  root = Tk.Tk()
  window = SampleUploadGUI(root)
  root.mainloop()
