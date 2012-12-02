#!/usr/bin/env python
import time

class Timer:
  """ simple class to see how fast things run """
  timer = None

  def __enter__( self ):
    self.reset("")
    return self

  def __exit__( self, *args ):
    print "Took: %0.3f ms" % ( time.time() - self.timer )

  def __init__( self, message="" ):
    self.reset(message)

  def stop( self ):
    print "Took: %0.3f ms" % ( time.time() - self.timer )
  
  def reset( self, message="" ):
    if message != "":
      print message
    self.timer = time.time()
