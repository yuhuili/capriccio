'''
MIT License

Copyright (c) 2016 Yuhui Li

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
'''

'''
capriccio.py

Created by Yuhui Li on 2016-08-12.

https://yuhuili.com
https://github.com/yuhuili
'''
import pyglet
import threading
import time
import datetime
import sys, getopt

from os.path import isfile

class Alarm(object):
  '''
  A simple alarm clock written in Python.
  
  Example:
    import capriccio
    
    t = datetime.datetime.now() + datetime.timedelta(seconds=10)
    a = Alarm(t, "alarm.mp3")
    
    # Make sure a is retained, or else when the main thread ends, this alarm will also be released.
    
    a.destroy() # Stop the alarm clock.
    
  '''
  def __init__(self, timestamp, tune):
    '''
    Initialize an alarm clock.
    
    Args:
      timestamp (datetime): The timestamp on which the alarm will sound.
      tune (str): The filename of the alarm audio file.
        
    '''
    self.should_stop = True
    
    now = datetime.datetime.now()
    delay = (timestamp - now).total_seconds()
    
    if delay > 0:
      print "Scheduling an alarm clock at %s, which is in %.1f seconds." % (timestamp, delay)
    else:
      print "Scheduling an alarm clock at %s, which is %.1f seconds earlier than current time %s. This alarm is not set." % (timestamp, delay, now)
      return
    
    self.alarm_thread = threading.Timer(delay, self.__play_sound, (tune,))
    self.alarm_thread.start()
    
    
  def destroy(self):
    '''
    Stop the alarm clock, whether or not it has actually occured
    '''
    self.should_stop = True
    if hasattr(self, 'p'):
      self.p.delete()
      
    self.alarm_thread.cancel()
    self.alarm_thread.join()
     
     
  def __play_sound(self, tune):
    '''
    Play the audio file continuously, until the alarm is cancelled by calling destroy()
    
    Args:
      tune (str): The filename of the alarm audio file.
      
    '''
    music = pyglet.media.load(tune)
    sg = pyglet.media.SourceGroup(music.audio_format, None)
    sg.loop = True
    sg.queue(music)

    self.p = pyglet.media.Player()
    self.p.queue(sg)
    self.p.play()

    v=float(0)
    while v<1 and self.should_stop == False:
      v+=0.05
      self.p.volume = v;
      time.sleep(0.2)
      

def main(argv):

  try:
    opts, args = getopt.getopt(argv,"hd:t:",["delay=","tune="])
  except getopt.GetoptError:
    print_usage()
    sys.exit(1)
  for opt, arg in opts:
    if opt == "-h":
      print_usage()
      sys.exit(0)
    elif opt in ("-d", "--delay"):
      try:
        float(arg)
      except ValueError:
        print "Illegal delay value. Expecting a positive float value, got %s" % arg
        sys.exit(3)
      
      if float(arg)<0:
        print "Illegal delay value. Expecting a positive float value, got %s" % arg
        sys.exit(4)
        
      d = datetime.datetime.now()+datetime.timedelta(seconds=float(arg))
    elif opt in ("-t", "--tune"):
      if not isfile(arg):
        print "Tune file %s does not exist." % arg
        sys.exit(5)
      t = arg
    else:
      assert False, "Unhandled option"
  
  if "d" not in locals():
    print_usage()
    sys.exit(6)
    
  if "d" not in locals():
    print_usage()
    sys.exit(6)
  
  a = Alarm(d,t)
  
  try:
    while True:
      time.sleep(0.05)
  except KeyboardInterrupt:
    a.destroy()


def print_usage():
  print "capriccio.py -d <delay in seconds> -t <audio filename>"


if __name__ == "__main__":
  main(sys.argv[1:])