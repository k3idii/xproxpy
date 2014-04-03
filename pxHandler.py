import socket
import httplib
import time
import os
import urllib
import ssl
import subprocess 
import StringIO

import http

CERT_DIR   = "./cert/"
CERT_PATH  = "%s/domains/" % CERT_DIR
CERT_FILE  = "cert.pem"
CERT_CACHE = dict()

def getCertForHost(host):
  global CERT_CACHE
  cache = CERT_CACHE.get(host,None)
  #cached ?
  if cache :
    return cache
  fname = "%s/%s/%s" % (CERT_PATH,host,CERT_FILE)
  # exists ?
  if os.path.isfile( fname ):
    CERT_CACHE[host] = fname
    return fname
  # generate !
   
  print "SSL REQ %s " % host
  process = subprocess.Popen([ CERT_DIR+'/createCert.sh', host] )
  process.wait() 
  
  if os.path.isfile( fname ):
    CERT_CACHE[host] = fname
    return fname
  
  print "FAIL FAIL FAIL !"
  return None 



def wrapServerSocket(sock,certFile):
  sslSocket = ssl.wrap_socket(sock, server_side = True, certfile = certFile,
                                     ssl_version = ssl.PROTOCOL_SSLv23, 
                                     do_handshake_on_connect = False)
  return sslSocket

def wrapClientSocket(sock):
  return ssl.wrap_socket(sock)


class connection:
  def __init__(self,sock):
    self.socket = sock
    self.rfile = sock.makefile('rb',512)
    self.wfile = sock.makefile('wb',512)

  def readAll(self,timeout=1,size=None):
    data = ''
    data += self.rfile._rbuf.getvalue()
    self.rfile._rbuf = StringIO.StringIO()
    if size:
      #print 'Need %d bytes ' % size
      size -= len(data)
      #print 'Got %d bytes (%d left)' % ( len(data) , size )
      if size<=0:
        return data 
    
    self.socket.settimeout(timeout)
    chunkSize = 200
    
    if size and size < chunkSize :
      chunkSize = size 
      #print "Still need %d bytes " % size 

    while True:
      if size and size < chunkSize :
        chunkSize = size
      try:
        #print "Reading %d" % chunkSize
        part = self.socket.recv( chunkSize )
      except socket.timeout as e:
        #print "!!! timeout "
        break
      except Exception as e: # failsafe :)
        #print "!!! FAIL : %s " % `e`
        break

      if not part: # eof ?
        break

      if len(part) != chunkSize:
        # warning !
        pass

      data += part
      if size:
        size -= len(part)
      if size == 0:
        #print "GOT ALL !"
        break

    return data

  def sendAll(self,msg):
    self.socket.sendall(msg)


class connectionHandler():
    def __init__(self, sock, client_address, server, sslPeer=None):
      self.con = connection( sock )
      self.client = client_address 
      self.server = server 
      self.sslPeer = sslPeer 
      while self.processSingleRequest():
        print " DONG !"
      #print " << CLOSED !"

    def processSingleRequest(self):
      try:
        req = http.httpReq( source = self.con )
      except http.httpException as e:
        print "fail [%s]" % `e`
        return False
      except Exception as e:
        print "epic fail [%s]" % `e`
        return False
      #print " -> GOT REQ "
      if req.verb == http.methods.CONNECT:
        print " --> CONNECT ! -> SSL MODE !"
        if ":" in req.uri:
          host,port = req.uri.split(":")
        else:
          host = req.uri
          port = 443
        try:
          cert = getCertForHost( host ) 
          #print cert
          sslSocket = wrapServerSocket( self.con.socket, cert )
          self.con.sendAll( http.simpleHttpAnswer(200) )
          sslSocket.do_handshake()
        except Exception as e:
          print "SSL INIT for (%s) fail ! : %s " % ( `(host,port)` , `e` )
          return False
        child = connectionHandler(sslSocket,self.client,self.server, sslPeer = (host,int(port)) )
        return False  

      targetPeer = None
      clientSSL = False

      if self.sslPeer: 
        targetPeer = self.sslPeer
        clientSSL = True
      else:
        try:
          targetPeer = req.getUriHost()
        except Exception as e:
          self.con.sendAll( http.simpleHttpAnswer(400,"Invalid proxy request !") )
          print "FAIL : %s " % `e`
          return False
        req.fixPath()

      
      
      req = self.mangleRequest(req)
      binaryRequest = req.dumps()
      #print binaryRequest[:20]
      ans = None

      try:
        #print " -> conect "
        sock = socket.create_connection( targetPeer ) 
        if clientSSL:
          sock = wrapClientSocket( sock ) 
          #print "  -> SSL !"
        fwd = connection( sock ) 
      except Exception as e:
        print "fail to fwd connection to %s , reason: %s" % (`targetPeer`,`e`)
        return False
      try:  
        #print "  < - read "
        fwd.sendAll(binaryRequest)
        ans = http.httpAns( source = fwd ) 
      except Exception as e:
        print "Fail to send/recv data : %s " % `e`
        return False
      
      # ^_^ 
      ans.setReqUrl(req.uri)
      #mangle
      self.mangleAnswer(ans)
      answer = ans.dumps()
      #print answer[:20]
      #print '   - - > send back '
      self.con.sendAll( answer  )
      print " << send back answer >> "
      return False


    def mangleRequest(self,req):
      return req 
  
    def mangleAnswer(self,ans):
      return ans

 
