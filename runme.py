#!/usr/bin/env python
import argparse 
import time

import pxServer
import pxHandler 


def main():
  P = argparse.ArgumentParser(description='== magix proxy ==')
  P.add_argument("--config" , default="routes.cfg", help="...")
  P.add_argument("--listen" , default="0.0.0.0:8888", help="Listen address, def: 0.0.0.0:8888 ")
  P.add_argument("--proxy"  , default=None , help="Second-level proxy ")
  P.add_argument("--verbose" , default=False, action='store_true', help="Be verbose")
  args = P.parse_args()
  
  srv = pxServer.ProxyServer( args, pxHandler.connectionHandler ) 
  try:
    srv.startThread()
    while True:
          time.sleep(1)
  except KeyboardInterrupt as e:
    print "KeyboardInterrutp !"
    srv.shutdown()

  #srv.serverLoop()


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
      print "Error !"
      print `e`

    print "Bye !"

