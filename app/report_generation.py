import datetime
from reportlab.pdfgen import canvas
from reportlab.platypus import Image, Paragraph, SimpleDocTemplate
from reportlab.lib.styles import getSampleStyleSheet


def build_pdf_report(sample_name, images, probabilities, ht_results):
  """
  For building pdf report from map displayed in mapviewer.
  See http://www.blog.pythonlibrary.org/2010/03/08/a-simple-step-by-step-reportlab-tutorial/
  for an example of using reportlab.

  :param sample_name: name of sample corresponding to images
  :param images:
  :param probabilities:
  :param ht_results: string containing results of hypothesis tests
  :return:
  """

  timestamp = datetime.datetime.now().strftime("%y%m%d_%H%M%S")
  report_fname = \
    "/mnt/c/Users/Jesse/Desktop/forensic-geolocation-master/deepspace/app/{}-{}.pdf".format(sample_name, timestamp)
  doc = SimpleDocTemplate(report_fname)
  Story = []

  # Add timestamp to top of document
  Story.append(Paragraph(timestamp, getSampleStyleSheet()["Normal"]))

  # Add images to document
  for image in images:
    print(image)
    Story.append(Image(image))

  # ToDo: Add probabilities to document
  Story.append(Paragraph(ht_results, getSampleStyleSheet()["Normal"]))

  doc.build(Story)
  return


if __name__ == "__main__":
  sample_name_ = "Costa RicaC"
  images_ = ["image.png"]
  probabilities_ = None
  build_pdf_report(sample_name_, images_, probabilities_)




