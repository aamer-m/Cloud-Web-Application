# from __future__ import unicode_literals
# from __future__ import with_statement
from google.appengine.api import images
import PIL
from PIL import Image
import mimetypes
from StringIO import StringIO
import cStringIO
from google.appengine.api import urlfetch
from PIL import ImageEnhance
from google.appengine.ext import ndb
from google.appengine.ext import blobstore
from google.appengine.ext.webapp import blobstore_handlers
import os
import jinja2
import urllib
import lib.cloudstorage as gcs
import webapp2

JINJA_ENVIRONMENT = jinja2.Environment(
  loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
  extensions=['jinja2.ext.autoescape'],
  autoescape=True)


class ImageData(ndb.Model):
    imageKey = ndb.BlobKeyProperty()
    gColor = ndb.FloatProperty()
    gBrightness = ndb.FloatProperty()
    gContrast = ndb.FloatProperty()
    gSharpness = ndb.FloatProperty()
    gRotate = ndb.IntegerProperty()
    gImFLSelected = ndb.BooleanProperty()
    

# Entry point of the application
class MainPage(webapp2.RequestHandler):
    def get(self):
      template = JINJA_ENVIRONMENT.get_template('/html/index.html')
      self.response.write(template.render())


class CreateUploadImageHandler(webapp2.RequestHandler):
    def get(self):
#         self.response.headers.add_header("Cache-Control", "no-cache, no-store, must-revalidate, max-age=0")
#         self.response.headers.add_header("Expires","0")
        self.response.headers[b'Content-Type'] = b'text/plain'
        self.response.out.write(blobstore.create_upload_url('/upload_photo'))

class UploadHandler(blobstore_handlers.BlobstoreUploadHandler):
    def post(self):
        try:
            upload = self.get_uploads()[0]
            iR = ImageData(imageKey=upload.key(),
                           gColor = float(self.request.get('color')),
                           gBrightness = float(self.request.get('brightness')),
                           gContrast = float(self.request.get('contrast')),
                           gSharpness = float(self.request.get('sharpness')),
                           gRotate = int(self.request.get('rotate')),
                           gImFLSelected = bool(self.request.get('lucky')))
            iR.key = ndb.Key(ImageData, '123')
            iR.put()
            self.redirect('/view_photo/%s' % upload.key())
        except:
            self.error(500)

class ImageDownloadHandler(blobstore_handlers.BlobstoreDownloadHandler):
    def get(self, photo_key):
            if not blobstore.get(photo_key):
                self.error(404)
            else:
                try:
                    blob_info = blobstore.BlobInfo.get(photo_key)
                    im = Image.open(blob_info.open())
                    iR = ndb.Key(ImageData, '123').get()
                    mimeType = im.format
                    try:
                        
                        if iR.gImFLSelected:
                            img = images.Image(c)
                            img.im_feeling_lucky()
                            data = img.execute_transforms(output_encoding=images.JPEG)
                        else:
                            enh = ImageEnhance.Color(im) # 0 - 2 to be considered
                            out = enh.enhance(iR.gColor)
                            enh = ImageEnhance.Brightness(out) # 0 - black image, 1 - original image; Can give more than 1.0
                            out = enh.enhance(iR.gBrightness)
                            enh = ImageEnhance.Contrast(out) # 0 - solid grey image, 1 - original image
                            out = enh.enhance(iR.gContrast)
                            enh = ImageEnhance.Sharpness(out) # 0 - blurred image, 1 - original image, 2 - sharpened image
                            out = enh.enhance(iR.gSharpness) 
                            out = out.rotate(iR.gRotate, resample=Image.BICUBIC, expand=True)
                            buf = cStringIO.StringIO()
                            out.save(buf, mimeType)
                            data = buf.getvalue()
                            # print(images.get_serving_url(data))
                            filename = "/picpeck/"+im.filename
                            with gcs.open(filename, 'w') as f:
                                f.write(data)
                            blobstore_filename = "/gs"+filename
                            #this is needed if you want to continue using blob_keys.
                            ieurl = images.get_serving_url(blobstore.BlobKey(blobstore.create_gs_key(str(blobstore_filename))))
                        self.response.out.write('<img width="100%" height="100%" src="' + ieurl +'"/>')
                        self.response.out.write('<a style="float:right;position:absolute;top:8px;right:8px;width:48px;height:48px" href="' + ieurl + '">'+'<img style="width: 48px;height: 48px;" src="https://upload.wikimedia.org/wikipedia/commons/thumb/1/1e/Download-Icon.png/480px-Download-Icon.png"></a>')
                    except:
                        self.response.headers[b'Content-Type'] = b'text/plain'
                        self.response.out.write('Image size is too large. Can\'t handle')
                except:
                    self.error(500)

class ImageHandler(webapp2.RequestHandler):
    def post(self):
        gurl = self.request.get('imageURL')
        print("urlColor: " +self.request.get('color'))
        gcolor = float(self.request.get('color'))
        gbrightness = float(self.request.get('brightness'))
        gcontrast = float(self.request.get('contrast'))
        gsharpness = float(self.request.get('sharpness'))
        grotate = int(self.request.get('rotate'))
        gImFLSelected = bool(self.request.get('lucky'))
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
                filename = "/picpeck/"+im.filename
                with gcs.open(filename, 'w') as f:
                  f.write(data)
                blobstore_filename = "/gs"+filename
                #this is needed if you want to continue using blob_keys.
                ieurl = images.get_serving_url(blobstore.BlobKey(blobstore.create_gs_key(str(blobstore_filename))))
#             self.response.headers[b'Content-Type'] = b'image/' + mimeType
            self.response.out.write('<img width="100%" height="100%" src="' + ieurl +'"/>')
            self.response.out.write('<a style="float:right;position:absolute;top:8px;right:8px;width:48px;height:48px" href="' + ieurl + '">'+'<img style="width: 48px;height: 48px;" src="https://upload.wikimedia.org/wikipedia/commons/thumb/1/1e/Download-Icon.png/480px-Download-Icon.png"></a>')
        except:
            self.response.headers[b'Content-Type'] = b'text/plain'
            self.response.out.write('Image size is too large. Can\'t handle')


app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/imagehandler', ImageHandler),
    ('/createUploadHandler', CreateUploadImageHandler),
    ('/upload_photo', UploadHandler),
    ('/view_photo/([^/]+)?', ImageDownloadHandler),
], debug=True)