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
import random

from mingus.midi import fluidsynth
from os.path import isfile

class Alarm(object):
  '''
  A simple alarm clock written in Python.
  
  Example:
    import capriccio
    
    t = datetime.datetime.now() + datetime.timedelta(seconds=10)
    a = Alarm(t, "alarm.mp3") 
    
    # The above plays alarm.mp3, or you could use Alarm(t, 0) to let capriccio generate note sequences in real time given an instrument number.
    # Make sure a is retained, or else when the main thread ends, this alarm will also be released.
    
    a.destroy() # Stop the alarm clock.
    
  '''
  
  def __init__(self, timestamp, tune, is_random = False):
    '''
    Initialize an alarm clock.
    
    Args:
      timestamp (datetime): The timestamp on which the alarm will sound.
      tune (str): The filename of the alarm audio file, or if is_random==True, the instrument number.
      is_random (bool): if sound generator should be used instead of an audio file.
        
    '''
    self.should_stop = True
    
    now = datetime.datetime.now()
    delay = (timestamp - now).total_seconds()
    
    if delay > 0:
      print "Scheduling an alarm clock at %s, which is in %.1f seconds." % (timestamp, delay)
    else:
      print "Scheduling an alarm clock at %s, which is %.1f seconds earlier than current time %s. This alarm is not set." % (timestamp, delay, now)
      return
    
    if is_random == False:
      self.alarm_thread = threading.Timer(delay, self.__play_sound__, (tune,))
    else:
      self.alarm_thread = threading.Timer(delay, self.__generate_sound__, (int(tune),))
      
    self.alarm_thread.start()
    
    
  def destroy(self):
    '''
    Stop the alarm clock, whether or not it has actually occured
    '''
    self.should_stop = True
    if hasattr(self, 'p'):
      self.p.delete()
      
    if hasattr(self, 'sg'):
      self.sg.stop()
      
    self.alarm_thread.cancel()
    self.alarm_thread.join()
     
  
  def __generate_sound__(self, instrument):
    '''
    Play generated note sequences on a given instrument.
    
    Args:
      instrument (int): The instrument used by SoundGen. (Not identical to GM 1 Sound Set)
    
    '''
    self.sg = SoundGen(instrument)
    self.sg.play()
    
     
  def __play_sound__(self, tune):
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


class SoundGen(object):
  '''
  Synthesize note sequences with mingus and fluidsynth.
  '''
  # L = low, H = high
  kNoteNone = int(-1)
  kNoteLB = int(59)
  kNoteC = int(60)
  kNoteCs = kNoteDf = int(61)
  kNoteD = int(62)
  kNoteDs = kNoteEf = int(63)
  kNoteE = int(64)
  kNoteF = int(65)
  kNoteFs = kNoteGf = int(66)
  kNoteG = int(67)
  kNoteGs = kNoteAf = int(68)
  kNoteA = int(69)
  kNoteAs = kNoteBf = int(70)
  kNoteB = int(71)
  kNoteHC = int(72)
  kNoteHCs = kNoteHDf = int(73)
  kNoteHD = int(74)
  kNoteHDs = kNoteHEf = int(75)
  kNoteHE = int(76)
  kSameNoteMultiplier = 3
  
  OneBeatLength = 0.5 # 1 beat is _ seconds

  def __init__(self, instrument = 0):
    self.should_stop = False
    
    if instrument == 1: # Pipe: Pan Flute
      self.__set_instrument__(75, 0.5)
    elif instrument == 2: # Brass: French Horn
      self.__set_instrument__(60, 0.3)
    elif instrument == 3: # Synth Lead: Lead 8 (bass + lead)
      self.__set_instrument__(87, 0.2)
    elif instrument == 4: # Synth Effects: FX 3 (crystal)
      self.__set_instrument__(98, 0.3)
    elif instrument == 5: # Percussive: Steel Drums
      self.__set_instrument__(114, 0.2)
    elif instrument == 6: # Sound Effects: Bird Tweet (Calm but prob no a good wake up alarm)
      self.__set_instrument__(123, 0.5)
    elif instrument == 7: # Sound Effects: Gunshot (ANNOYING~)
      self.__set_instrument__(127, 0.2)
    elif instrument == 8: # Ensemble: String Ensemble 2
      self.__set_instrument__(49, 0.4)
    elif instrument == 9: # Pipe: Piccolo
      self.__set_instrument__(72, 0.4)
    else: # Default: Piano: Electric Grand Piano
      self.__set_instrument__(2, 0.3)
    
  def __set_instrument__(self, instrument, beat_length):
    self.instrument = instrument
    self.OneBeatLength = beat_length
  
  def play(self):
    fluidsynth.init('/usr/share/sounds/sf2/FluidR3_GM.sf2','alsa')
    fluidsynth.set_instrument(0, self.instrument) # Use channel 0
    
    self.previous = int(SoundGen.kNoteNone) # Previously played note
    
    self.shift = random.randint(-10, 5) # Allow the key to be shifted
    
    beat_tracker = int(0) # 4/4 time.
    while self.should_stop == False:
      v = random.randint(65,75)
      if beat_tracker % 8 == 0:
        # First beat, strong
        v = random.randint(85,95)
      elif (beat_tracker - 4) % 8 == 0:
        # Third beat, semi-strong
        v = random.randint(75,85)
      elif beat_tracker % 2 == 1:
        # Off-beat, very soft
        v = random.randint(55,65)
      
      # Random note length
      possible_lengths = [4] + [2] * 10 + [1] * 4 # 4 is 2 beats, 2 is 1 beat, 1 is half-beat
      if beat_tracker % 2 == 1: # avoid non-half-beat if currently in half-beat
        possible_lengths += [1] * 20 # Add weight to half-beat
      length = random.choice(possible_lengths)
      beat_tracker+=length
    
      if self.previous != SoundGen.kNoteNone:
        fluidsynth.stop_Note(self.previous+self.shift, 0)
      self.previous = SoundGen.__next_note__(self.previous)
      fluidsynth.play_Note(self.previous+self.shift,0,v);
      time.sleep(length * self.OneBeatLength)
    
  def stop(self):
    self.should_stop = True;
    if self.previous != SoundGen.kNoteNone: # Won't actually kill SoundGen just yet, but at least will stop the sound instantly.
      fluidsynth.stop_Note(self.previous+self.shift, 0)
    
  @staticmethod
  def __next_note__(previous):
    # I know, tons of magic numbers and so difficult to read. Will fix.
    if (previous == SoundGen.kNoteNone):
      choices = [SoundGen.kNoteC, SoundGen.kNoteD, SoundGen.kNoteE, SoundGen.kNoteF, SoundGen.kNoteG, SoundGen.kNoteA, SoundGen.kNoteB, SoundGen.kNoteC]
    else:
      if (previous == SoundGen.kNoteLB):
        choices = [SoundGen.kNoteC] * 10 + [SoundGen.kNoteD] + [SoundGen.kNoteG]
      elif (previous == SoundGen.kNoteC):
        choices = [SoundGen.kNoteC, SoundGen.kNoteD, SoundGen.kNoteE, SoundGen.kNoteF, SoundGen.kNoteG] + [SoundGen.kNoteE] * 2 + [SoundGen.kNoteG] * 3
      elif (previous == SoundGen.kNoteD):
        choices = [SoundGen.kNoteC, SoundGen.kNoteE, SoundGen.kNoteF, SoundGen.kNoteG, SoundGen.kNoteA] * SoundGen.kSameNoteMultiplier + [SoundGen.kNoteC, SoundGen.kNoteG] * 2 + [SoundGen.kNoteD]
      elif (previous == SoundGen.kNoteE):
        choices = [SoundGen.kNoteC, SoundGen.kNoteD, SoundGen.kNoteF, SoundGen.kNoteG, SoundGen.kNoteHC] * SoundGen.kSameNoteMultiplier + [SoundGen.kNoteC] * 2 + [SoundGen.kNoteG] * 2 + [SoundGen.kNoteE]
      elif (previous == SoundGen.kNoteF):
        choices = [SoundGen.kNoteC, SoundGen.kNoteD, SoundGen.kNoteE, SoundGen.kNoteG, SoundGen.kNoteA, SoundGen.kNoteHC] * SoundGen.kSameNoteMultiplier + [SoundGen.kNoteF]
      elif (previous == SoundGen.kNoteG):
        choices = [SoundGen.kNoteC, SoundGen.kNoteD, SoundGen.kNoteE, SoundGen.kNoteF, SoundGen.kNoteA, SoundGen.kNoteB, SoundGen.kNoteHC, SoundGen.kNoteHD, SoundGen.kNoteHE] * SoundGen.kSameNoteMultiplier + [SoundGen.kNoteC] * 2 + [SoundGen.kNoteE] * 2 + [SoundGen.kNoteG]
      elif (previous == SoundGen.kNoteA):
        choices = [SoundGen.kNoteE, SoundGen.kNoteF, SoundGen.kNoteG, SoundGen.kNoteB, SoundGen.kNoteHC, SoundGen.kNoteHD, SoundGen.kNoteHE] * SoundGen.kSameNoteMultiplier + [SoundGen.kNoteHC] * 2 + [SoundGen.kNoteA]
      elif (previous == SoundGen.kNoteB):
        choices = [SoundGen.kNoteE, SoundGen.kNoteF, SoundGen.kNoteG, SoundGen.kNoteA, SoundGen.kNoteHC, SoundGen.kNoteHD] * SoundGen.kSameNoteMultiplier + [SoundGen.kNoteG] * 2 + [SoundGen.kNoteHC] * 2 + [SoundGen.kNoteB]
      elif (previous == SoundGen.kNoteHC):
        choices = [SoundGen.kNoteE, SoundGen.kNoteF, SoundGen.kNoteG, SoundGen.kNoteA, SoundGen.kNoteB, SoundGen.kNoteHD, SoundGen.kNoteHE] * SoundGen.kSameNoteMultiplier + [SoundGen.kNoteG] * 3 + [SoundGen.kNoteE] * 3 + [SoundGen.kNoteHC]
      elif (previous == SoundGen.kNoteHD):
        choices = [SoundGen.kNoteG, SoundGen.kNoteB, SoundGen.kNoteHC, SoundGen.kNoteHE] * SoundGen.kSameNoteMultiplier + [SoundGen.kNoteB] * 2 + [SoundGen.kNoteG] * 2 + [SoundGen.kNoteHD]
      elif (previous == SoundGen.kNoteHE):
        choices = [SoundGen.kNoteG, SoundGen.kNoteHC] * SoundGen.kSameNoteMultiplier * 3 + [SoundGen.kNoteHC] * 2 + [SoundGen.kNoteG] * 2 + [SoundGen.kNoteHE]
    
    return random.choice(choices)


def main(argv):

  try:
    opts, args = getopt.getopt(argv,"hd:t:i:",["delay=","tune=","instrument="])
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
    elif opt in ("-i", "--instrument"):
      i = arg
    else:
      assert False, "Unhandled option"
  
  if "d" not in locals():
    print_usage()
    sys.exit(6)
    
  if "t" not in locals() and "i" not in locals():
    print_usage()
    sys.exit(6)
  
  if "t" in locals():
    a = Alarm(d,t)
  else:
    a = Alarm(d,i,True)
  
  try:
    while True:
      time.sleep(0.05)
  except KeyboardInterrupt:
    a.destroy()


def print_usage():
  print "capriccio.py -d <delay in seconds> -t <audio filename>\ncaprioccio.py -d <delay in seconds> -i <instrument id>"


if __name__ == "__main__":
  main(sys.argv[1:])
