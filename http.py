import socket
import datetime
import copy
import urlparse
import select

import httplib 
import mimetools 

httpCodes = httplib.responses

LINE_END='\r\n'

class recSet:
  def __init__(self,elements):
    for e in elements:
      setattr(self,e,e)

methods = recSet( ("GET","POST","CONNECT") )


class httpException(Exception):
  pass


def simpleHttpAnswer(code=200,message='',version='1.1'):
  short = "Unknown"
  if code in httpCodes:
    short = httpCodes[code]
  
  return "HTTP/%s %d %s\r\n\r\n%s" % ( version, code, short, message )


def readBody(obj,timeout=1):
  cl = obj.headers.get("Content-length",None)
  if cl:
    #print "Content length : %s " % cl
    cl = int(cl)
    if cl == 0:
      obj.data = ''
      return
  else:
    #print "Unknown content length !"
    #print obj
    pass
  data = obj.con.readAll( timeout , size = cl )
  obj.body = data

class httpReq:
  def __init__(self,source=None):
    self.con = source 
    self.verb     = None
    self.resource = None
    self.version  = None
    self.headers  = None
    self.body     = None
    self.readQuery()


  def readQuery(self):
    firstLine = self.con.rfile.readline()
    if not firstLine or len(firstLine) < 3 :
      raise Exception("Connection closed [1]!")
    if not " HTTP/" in firstLine:
      raise httpException("Invalid query [%s]" % firstLine )
    firstLine = firstLine.rstrip(LINE_END)
    words = firstLine.split(' ')
    if len(words) != 3:
      raise httpException("Invalid format [%s] " % firstLine )
    self.verb, self.uri, self.version = words
    self.verb = self.verb.upper() # <- :)
    if not self.version.startswith("HTTP/"):
      raise httpException("HTTP/x.x required")
    self.path = self.uri 
    self.headers = mimetools.Message( self.con.rfile , 0 )    
    if self.verb == methods.CONNECT:
      return # skip body-read on connect :)
    readBody(self,1)

  def getUriPath(self):
    r = urlparse.urlparse(self.uri)
    s = ''
    s += r.path
    if len(r.params) > 0:
      s += ";%s" % r.params
    if len(r.query) > 0:
      s += "?%s" % r.query
    if len(r.fragment) > 0:
      s += "#%s" % r.fragment
    return s

  def getUriHost(self):
    r = urlparse.urlparse(self.uri)
    host = r.hostname 
    if r.port is None:
      if r.scheme == "http":
        port = 80
      elif r.scheme == "https":
        port = 443
      else:
        raise httpException("Unknow scheme")
    else:
      port = r.port 
    return (host,port)

  def fixPath(self):
    self.path = self.getUriPath()

  def __str__(self):
    return "[[ %s ]]\n %s %s %s\n%s\n\n%s\n\n" % ( self.uri , self.verb ,self.path , self.version , self.headers , self.body)


  def dumps(self):
    return "%s %s %s\n%s\n%s" % ( self.verb, self.path, self.version, self.headers, self.body)




class httpAns:
  def __init__(self,source):
    self.con = source
    self.status   = None
    self.headers  = None
    self.body     = None
    self.readAnswer()

  def readAnswer(self):
    firstLine = self.con.rfile.readline()
    self.status = firstLine.rstrip(LINE_END)
    self.headers = mimetools.Message( self.con.rfile , 0 )
    readBody(self,5)
  
  def setReqUrl(self,u):
    self.uri = u

  def __str__(self):
    return "[[ %s ]]%s" % (self.uri, self.dumps() )
  
  def dumps(self):
    return "%s\n%s\n%s" % (self.status, self.headers, self.body )



