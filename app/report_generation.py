import datetime
from reportlab.pdfgen import canvas
from reportlab.platypus import Image, Paragraph, SimpleDocTemplate, Table
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch


def build_pdf_report(sample_name, images, probabilities, ht_results):
  """
  For building pdf report from map displayed in mapviewer.
  See http://www.blog.pythonlibrary.org/2010/03/08/a-simple-step-by-step-reportlab-tutorial/
  for an example of using reportlab.

  :param sample_name: name of sample corresponding to images
  :param images:
  :param probabilities:
  :param ht_results: list of tuples (ht image name, string of ht results)
  :return:
  """

  timestamp = datetime.datetime.now().strftime("%y%m%d_%H%M%S")
  report_fname = \
    "/mnt/c/Users/Jesse/Desktop/forensic-geolocation-master/deepspace/app/reports/pdfs/{}-{}.pdf".format(sample_name,
                                                                                                         timestamp)
  doc = SimpleDocTemplate(report_fname)
  Story = []

  # Add timestamp to top of document
  Story.append(Paragraph(timestamp, getSampleStyleSheet()["Normal"]))

  # Add images to document
  for image in images:
    Story.append(Image(image, 6*inch, 4*inch))

  # Add hypothesis test images and results
  Story.append(Paragraph("Hypothesis test results: ", getSampleStyleSheet()["Normal"]))
  if len(ht_results) == 0:
    Story.append(Paragraph("No hypothesis tests to report", getSampleStyleSheet()["Normal"]))
  else:
    for image, result_str in ht_results:
      Story.append(Image(image, 6*inch, 4*inch))
      Story.append(Paragraph(result_str, getSampleStyleSheet()["Normal"]))

  # Add table of probs and coordinates
  Story.append(Paragraph("Point probabilities: \n", getSampleStyleSheet()["Normal"]))
  Story.append(Table(probabilities))

  doc.build(Story)
  return


if __name__ == "__main__":
  sample_name_ = "Costa RicaC"
  images_ = ["image.png"]
  probabilities_ = None
  build_pdf_report(sample_name_, images_, probabilities_)




