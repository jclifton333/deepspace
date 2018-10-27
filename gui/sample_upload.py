from tkinter import *
import tkinter.filedialog
from tkinter import messagebox
import csv


class Window:
  def __init__(self, master):
    self.filename = ""
    csvfile = Label(root, text="File").grid(row=1, column=0)
    bar = Entry(master).grid(row=1, column=1)

    # Buttons
    y = 7
    self.cbutton = Button(root, text="OK", command=self.process_csv)
    y += 1
    self.cbutton.grid(row=10, column=3, sticky=W + E)
    self.bbutton = Button(root, text="Browse", command=self.browsecsv)
    self.bbutton.grid(row=1, column=3)
    self.run_model_button = Button(root, text="Run model", command=self.run_model)
    self.run_model_button.grid(row=11, column=3)

    self.csv_fname_to_analyze = None

  def run_model(self):
    if self.csv_fname_to_analyze is None:
      run_model_message = \
        "No data uploaded. Nothing will happen."
      messagebox.showinfo("Running model", run_model_message)
    else:
      run_model_message = \
        "Running model on samples in {}.  This will take about 7 minutes per sample.".format(self.csv_fname_to_analyze)
      messagebox.showinfo("Running model", run_model_message)

  def browsecsv(self):
    from tkinter.filedialog import askopenfilename

    Tk().withdraw()
    self.filename = askopenfilename()

  def process_csv(self):
    if self.filename:
      self.csv_fname_to_analyze = self.filename

root = Tk()
window = Window(root)
root.mainloop()