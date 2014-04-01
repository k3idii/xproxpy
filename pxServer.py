import SocketServer
import BaseHTTPServer
import threading 

class ThreadedHTTPProxyServer(SocketServer.ThreadingMixIn, SocketServer.TCPServer):
  allow_reuse_address = True

class ProxyServer():    
  def __init__(self, args , handler ):
    self.args = args 

    listenAddress = args.listen 

    if ":" not in listenAddress:
      raise Exception("Bad listen address format")
    h,p = listenAddress.split(":")
    if h is '' or h == '*':
      h = '0.0.0.0'
    p = int(p)
    self.proxyServer_port = p
    self.proxyServer_host = h
    self.handler = handler 
    print "Server %s listening on port %d" % (self.proxyServer_host, self.proxyServer_port)
    self.server = ThreadedHTTPProxyServer((self.proxyServer_host, self.proxyServer_port), self.handler )
    self.server.parent = self

  def startThread(self):
    server_thread = threading.Thread(target = self.serverLoop )
    server_thread.setDaemon(True)
    server_thread.start()
    return server_thread 

  def serverLoop(self):
    self.server.serve_forever()

  def shutdown(self):
    self.server.shutdown()

