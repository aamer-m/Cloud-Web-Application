Image Manipulation Web App
==========================

URL: http://pic-peck.appspot.com/
------------------------------------

> Created a Google App Engine application 
> to perform image manipulations submitted by the user
> using URL with additional parameters. User can rotate
> the image, change the Contrast, Sharpness, Brightness and
> i_m_feeling_lucky feature provided by Image API which adjusts
> image contrasts and color levels.

## The page hits are observed for the web-site using memcache

# Customized access management using OTP (One Time Passcode) authentication mechanism

### Highlights:
**unique passcode** | **expires when session ends** | **passcodes emailed** | **uses MD5 hascode with random padding**

- The user is allowed to enter a valid email id, if the email format is not correct, user is notified and prompted again
- When a valid email is entered by the user, he gets a 6-digit alpha-numeric passcode to his email immediately
- User can then enter this one-time passcode(OTP) to login into the website
- User cannot re-use this passcode for future logins. It is valid only for **ONE** time and expires when session ends
- The passcode is generated by manipulating the MD5 hash code and adding a random padding which is valid only for the user session. This makes the authentication mechanism a **robust** and **secure** one

# Used AppEngine web services
 - Image Transformation API (with PIL)
 - Google Cloud Datastore
   - NDB Datastore API
 - *
 - *


# Version
1.0

# Example
An Sample image url is submitted by the user.

 - Image:
![alt bat]

 - Web app homepage
![image homepage]

 - Web app output
![image result]
