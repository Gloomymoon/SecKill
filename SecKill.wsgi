import sys
import os

#Expand Python classes path with your app's path
sys.path.insert(0, u"D:\\tomcat\\webapps\\SecKill")

from manage import app

#Put logging code (and imports) here ...

#Initialize WSGI app object
application = app