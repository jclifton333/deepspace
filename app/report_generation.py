import datetime
from reportlab.pdfgen import canvas
from reportlab.platypus import Image, Paragraph, SimpleDocTemplate


def build_pdf_report(sample_name, images, probabilities):
  """
  For building pdf report from map displayed in mapviewer.
  See http://www.blog.pythonlibrary.org/2010/03/08/a-simple-step-by-step-reportlab-tutorial/
  for an example of using reportlab.

  :param sample_name: name of sample corresponding to images
  :param images:
  :param probabilities:
  :return:
  """

  report_fname = "{}.pdf".format(sample_name)
  doc = SimpleDocTemplate(report_fname)
  Story = []

  # Add timestamp to top of document
  timestamp = datetime.datetime.now().strftime("%y%m%d_%H%M%S")
  Story.append(Paragraph(timestamp))

  # Add images to document
  for image in images:
    Story.append(Image(image))

  # ToDo: Add probabilities to document

  doc.build(Story)
  doc.save()
  return


if __name__ == "__main":
  sample_name_ = "Costa RicaC"
  images_ = ["image.png"]
  probabilities_ = None
  build_pdf_report(sample_name_, images_, probabilities_)




