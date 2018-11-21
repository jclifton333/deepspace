import sys
import pandas as pd
import os
import pdb
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


def string_is_positive_integer(string):
  """
   Check if string is a positive integer.

  :param string:
  :return:
  """
  try:
    val = int(string)
    if val >= 0:
      return True
    else:
      return False
  except ValueError:
    return False

def split_taxon_name(string):
  """
  Split "Taxon[integer]" into "Taxon", "[integer]"
  """
  found_integer_at_end = False
  for i, s in string:
    if string_is_positive_integer(s):
      break
  return [string[:i], string[i:]]

  


TAXON_ERROR = "-Taxon name formatted incorrectly."
INTEGER_ERROR = "-Incorrect data type in count data; they should all be positive integers."


def check_uploaded_file_for_errors(df):
  """
  Check that uploaded file is of correct format.

  :param df:
  :return:
  """
  error_dictionary = {
    TAXON_ERROR: False, INTEGER_ERROR: False

  }

  # Make sure index is of form Taxon[integer]
  for taxon_name in df.index:
    split_name = split_taxon_name(taxon_name)
    if len(split_name) > 1:
      if split_name[0] != 'Taxon':
        if not error_dictionary[TAXON_ERROR]:
          error_dictionary[TAXON_ERROR] = True
      if not string_is_positive_integer(split_name[-1]):
        if not error_dictionary[TAXON_ERROR]:
          error_dictionary[TAXON_ERROR] = True
    else:
      if not error_dictionary[TAXON_ERROR]:
        error_dictionary[TAXON_ERROR] = True

  # Make sure count data are all positive integers
  for col in df.columns.values:
    for entry in df[col]:
      if not string_is_positive_integer(entry):
        if not error_dictionary[INTEGER_ERROR]:
          error_dictionary[INTEGER_ERROR] = True

  return error_dictionary


class SampleUploadGUI(Tk.Frame):
  EXISTING_SAMPLE_WARNING = \
    "File contains column names corresponding to samples that have already been analyzed.\nRunning model will overwrite existing results for these samples names."

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
    self.cbutton = Tk.Button(self, text="Load", command=self.process_csv)
    y += 1
    self.cbutton.grid(row=10, column=3, sticky="we")
    self.bbutton = Tk.Button(self, text="Browse", command=self.browsecsv)
    self.bbutton.grid(row=1, column=3)
    self.run_model_button = Tk.Button(self, text="Run model", command=self.run_model)
    self.run_model_button.grid(row=11, column=3)
    self.return_to_menu_button = Tk.Button(self, text="Return to main menu",
                                           command=lambda: controller.show_frame("MainMenuGUI")).grid(row=12, column=3)

    # For checking whether already-analyzed sample is being uploaded
    self.existing_json_filenames = [json_fname.split(".json")[0] for json_fname in
                                    os.listdir(os.path.join(THIS_DIR, "geojson"))]

  def run_model(self):
    if self.csv_fname_to_analyze is None:
      run_model_message = \
        "No data uploaded. Nothing will happen."
      messagebox.showinfo("Running model", run_model_message)
    else:
      run_model_message = \
        "Running model on samples in {}.  This will take about 7 minutes per sample.".format(self.csv_fname_to_analyze)
      messagebox.showinfo("Running model", run_model_message)
      read_split_convert_compute(self.csv_fname_to_analyze)
      messagebox.showinfo("", "Model finished running.")

  def browsecsv(self):
    from tkinter.filedialog import askopenfilename

    Tk.Tk().withdraw()
    self.filename = askopenfilename()

  def process_csv(self):
    if self.filename:
      if self.filename.endswith(".csv") or self.filename.endswith(".xlsx"):
        if self.filename.endswith(".csv"):
          df = pd.read_csv(self.filename, index_col=0)
        elif self.filename.endswith(".xlsx"):
          df = pd.read_excel(self.filename, index_col=0)

        # Alert user if there are any column names corresponding to already-analyzed samples
        for colname in df.columns.values:
          if colname in self.existing_json_filenames:
            messagebox.showwarning("Existing sample", self.EXISTING_SAMPLE_WARNING)
            break

        # Check for formatting errors in uploaded file
        error_dict = check_uploaded_file_for_errors(df)
        if not error_dict[TAXON_ERROR] and not error_dict[INTEGER_ERROR]:
          self.csv_fname_to_analyze = self.filename
          messagebox.showinfo("Successful upload", "Ready to run model on {}".format(self.csv_fname_to_analyze))
        else:
          error_string = "Formatting errors in uploaded file:\n"
          if error_dict[TAXON_ERROR]:
            error_string += TAXON_ERROR
            error_string += "\n"
          if error_dict[INTEGER_ERROR]:
            error_string += INTEGER_ERROR
          messagebox.showerror("Formatting error", error_string)
      else:
        messagebox.showerror("File type error", "Wrong file type.  Must upload .csv or .xslx.")

    def refresh(self):
      self.filename = ""
      # For checking whether already-analyzed sample is being uploaded
      self.existing_json_filenames = [json_fname.split(".json")[0] for json_fname in
                                      os.listdir(os.path.join(THIS_DIR, "geojson"))]


if __name__ == "__main__":
  root = Tk.Tk()
  window = SampleUploadGUI(root)
  root.mainloop()
