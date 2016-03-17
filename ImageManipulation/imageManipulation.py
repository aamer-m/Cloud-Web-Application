from google.appengine.api import images
import PIL
from PIL import Image
import mimetypes
from StringIO import StringIO
import cStringIO
from google.appengine.api import urlfetch
import ImageEnhance
import webapp2


# Entry point of the application
class MainPage(webapp2.RequestHandler):
    def get(self):
        self.response.out.write('<html><head><link rel="stylesheet" type="text/css" href="stylesheets/style.css"></head><body>')
        self.response.out.write("""
        <form method="POST" action="/upload_photo" target="otp">
        <h1>Image Enhancement</h1></br></br>
        <center><input type="radio" name="choice-image" id="choice-image-url" value="image-url" checked="checked">
        <label for="choice-image-url">Image-URL</label>

        <input type="radio" name="choice-image" id="choice-image-file" value="image-file">
        <label for="choice-image-file">Image-File</label>

        <label id="image-url">Image URL: <input type="url" name="imageURL" placeholder="Enter an image URL here"></label>

        <label id="image-file">Image File: <input type="file" name="imageFile" accept="image/*" placeholder="Choose an image file"></label><br>

        <label>Rotate: <input type="range" name="rotate" min="0" max="360" value="0" step="5"  onchange="showValue(this.name, this.value)"/>
        <span id="rotate">0</span></label><br>
        <script type="text/javascript">
        function showValue(identity, newValue)
        {
            document.getElementById(identity).innerHTML=newValue
        }
        </script>
        <label>Color: <input type="range" name="color" min="-2" max="2" value="1" step="0.1" onchange="showValue(this.name, this.value)" />
        <span id="color">1</span></label><br>

        <label>Contrast: <input type="range" name="contrast" min="0" max="3" value="1" step="0.1" onchange="showValue(this.name, this.value)" />
        <span id="contrast">1</span></label><br>
        
        <label>Sharpness: <input type="range" name="sharpness" min="-2" max="2" value="1" step="0.1" onchange="showValue(this.name, this.value)" />
        <span id="sharpness">1</span></label><br>
        
        
        <label>Brightness: <input type="range" name="brightness" min="0" max="4" value="1" step="0.1" onchange="showValue(this.name, this.value)" />
        <span id="brightness">1</span></label><br>

        <h5><label><input type="checkbox" name="lucky" value="I'm Feeling Lucky"/> If you have any problem setting the values, Select this and we will get you a "I'm Feeling Lucky" image <label></h5>
        
        <input type="submit" name="submit"  value="submit"/><br>
        <iframe name="otp" frameborder="0" width="100%" height="100%"></iframe>
        </center>
        </form>
        </body>
        </html>""")

class ImageHandler(webapp2.RequestHandler):
    def post(self):
        gurl = self.request.get('imageURL')
        gcolor = float(self.request.get('color'))
        gbrightness = float(self.request.get('brightness'))
        gcontrast = float(self.request.get('contrast'))
        gsharpness = float(self.request.get('sharpness'))
        grotate = int(self.request.get('rotate'))
        gImFLSelected = bool(self.request.get('lucky'))
        c = urlfetch.fetch(gurl).content
        im = Image.open(StringIO(c))
        mimeType = im.format
        if gImFLSelected:
            img = images.Image(c)
            print('helo')
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
    
            
        self.response.headers['Content-Type'] = 'image/' + mimeType
        self.response.out.write(data)
        

app = webapp2.WSGIApplication([
    ('/', MainPage), 
    ('/upload_photo', ImageHandler),
], debug=True)