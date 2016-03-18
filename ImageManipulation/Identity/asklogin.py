from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext import ndb
from google.appengine.api import mail
from google.appengine.api import app_identity
from random import randint
import re
import random, string

def validateEmail(email):

    if len(email) > 7:
        if re.match("^.+\\@(\\[?)[a-zA-Z0-9\\-\\.]+\\.([a-zA-Z]{2,3}|[0-9]{1,3})(\\]?)$", email) != None:
            return 1
    return 0

def sendEmail(email,passcode):

    bodystr = passcode
    sender_address = "admin@" + app_identity.get_application_id() + ".appspotmail.com"
    mail.send_mail(sender=sender_address,to=email,subject="Secure Login Code!",body=bodystr)
    
def validatePasscode(UserID,pass_code):
    if pass_code in (Account1.query(Account1.id == UserID).fetch(1)[0].passcode):
        return 1
    return 0
        
class Account1(ndb.Model):
    key = ndb.StringProperty()
    id = ndb.StringProperty()
    passcode = ndb.StringProperty()
    
def randomwordgenerator(length):
    return ''.join(random.choice(string.lowercase) for i in range(length))

def generateHashCode(email):
    
    import hashlib
    return hashlib.md5(email.encode()).hexdigest()

class MainPage(webapp.RequestHandler):
    
    global UserID, randomgenerator
    def get(self):
        self.response.out.write("""<form>
  Choose your User name:<br>
  <input type="text" name="UserName" value="Enter your Email ID">
  <br><br>
  <input type="submit" value="Submit">
</form> 

<p>"Click the "Submit" button"</p>
""")
        if 'Passcode' in self.request.GET.keys():
            Passcode = self.request.GET['Passcode']
            global UserID, randomgenerator
#             self.response.out.write(validatePasscode(UserID,Passcode));
            if ((validatePasscode(UserID,Passcode[2:])==1) & (randomgenerator==Passcode[:2])):
                self.response.out.write("<h3>Enjoy!</h3>");
            else:
                self.response.out.write("<h3>Enter a valid Passcode and try again</h3>");
        if 'UserName' in self.request.GET.keys():
                UserID = self.request.GET['UserName']
                if (validateEmail(UserID)==0):
                    self.response.out.write("<h3>Enter a valid email ID</h3>");
#                 if (alreadyRegistered(UserID) is not None):
#                     self.response.out.write("<h3>User already Registered</h3>");
                if (validateEmail(UserID)==1):
#                     self.response.out.write(str(generateHashCode(UserID))[1:7])
                    rand_integer = 1*randint(0,25)
                    randomgenerator = randomwordgenerator(2)
                    sendEmail(UserID,randomgenerator+generateHashCode(UserID)[rand_integer:rand_integer+4])
#                     entity = Account1.get_by_id(UserID)
                    User = Account1(id=UserID, passcode=generateHashCode(UserID), key = UserID)
                    if not (Account1.query(Account1.id == UserID).fetch(1)):
                        self.response.out.write("<h3>Hurray</h3>")
                        User_Key = User.put();
                        self.response.out.write("<h3>We have emailed your secured code for future logins to your email ID</h3>");
                    self.response.out.write("""<form>
  Enter your Passcode:<br>
  <input type="text" name="Passcode" value="Enter your Passcode">
  <br><br>
  <input type="submit" value="Submit">
</form> 

<p>"Click the "Submit" button"</p>
""");
#                 self.response.out.write(alreadyRegistered(UserID));
#                 self.response.out.write(Account1.query(Account1.id == UserID).fetch(1)[0].passcode);                            
                
application = webapp.WSGIApplication([('/', MainPage)], debug=True)


def main():
    run_wsgi_app(application)


if __name__ == "__main__":
    main()
