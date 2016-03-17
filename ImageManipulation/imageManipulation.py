from __future__ import unicode_literals
from __future__ import with_statement
from google.appengine.api import images
from google.appengine.api import files
import PIL
from PIL import Image
import mimetypes
from StringIO import StringIO
import cStringIO
from google.appengine.api import urlfetch
import ImageEnhance
import logging
from google.appengine.ext import ndb
from google.appengine.ext import blobstore
import os
import jinja2
import urllib
import lib.cloudstorage as gcs
import webapp2

JINJA_ENVIRONMENT = jinja2.Environment(
  loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
  extensions=['jinja2.ext.autoescape'],
  autoescape=True)

# class ImageData(ndb.Model):
#     imageKey = ndb.BlobKeyProperty()

# Entry point of the application
class MainPage(webapp2.RequestHandler):
    def get(self):
      template = JINJA_ENVIRONMENT.get_template('index.html')
      self.response.write(template.render())

class ImageHandler(webapp2.RequestHandler):
    def post(self):
        isURL = self.request.get('choice-image') == "image-url"
        if isURL:
            gurl = self.request.get('imageURL')
        else:
            gurl = self.request.get('imageFile')
        gcolor = float(self.request.get('color'))
        gbrightness = float(self.request.get('brightness'))
        gcontrast = float(self.request.get('contrast'))
        gsharpness = float(self.request.get('sharpness'))
        grotate = int(self.request.get('rotate'))
        gImFLSelected = bool(self.request.get('lucky'))
        if len(gurl) > 0:
          c = urlfetch.fetch(gurl).content
          im = Image.open(StringIO(c))
          mimeType = im.format
          try:
            if gImFLSelected:
                img = images.Image(c)
                img.im_feeling_lucky()
                data = img.execute_transforms(output_encoding=images.JPEG)
            else: 
                enh = ImageEnhance.Color(im) # 0 - 2 to be considered
                out = enh.enhance(gcolor)
                enh = ImageEnhance.Brightness(out) # 0 - black image, 1 - original image; Can give more than 1.0
                out = enh.enhance(gbrightness)
                enh = ImageEnhance.Contrast(out) # 0 - solid grey image, 1 - original image
                out = enh.enhance(gcontrast)
                enh = ImageEnhance.Sharpness(out) # 0 - blurred image, 1 - original image, 2 - sharpened image
                out = enh.enhance(gsharpness) 
                out = out.rotate(grotate, resample=Image.BICUBIC, expand=True)
                buf = cStringIO.StringIO()
                out.save(buf, mimeType)
                data = buf.getvalue()
                # print(images.get_serving_url(data))
                filename = "/picpeck/"+"somefile."+mimeType
                with gcs.open(filename, 'w') as f:
                  f.write(data)
                blobstore_filename = "/gs"+filename
                #this is needed if you want to continue using blob_keys.
                print images.get_serving_url(blobstore.BlobKey(blobstore.create_gs_key(str(blobstore_filename))))
            self.response.headers[b'Content-Type'] = b'image/' + mimeType
            self.response.out.write(data)
          except:
            self.response.headers[b'Content-Type'] = b'text/plain'
            self.response.out.write('Image size is too large. Can\'t handle')
        else:
          self.response.headers[b'Content-Type'] = b'text/plain'
          self.response.out.write('URL/file missing please input the fields')


app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/imagehandler', ImageHandler),
], debug=True)