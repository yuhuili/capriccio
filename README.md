# capriccio
A simple alarm clock module written in Python. You could set the alarm audio to any audio file, or let capriccio generate new music everyday~

## Dependencies
[pyglet](http://www.pyglet.org), for playing audio. Pyglet also requires [AVbin](http://avbin.github.io/AVbin/Home/Home.html) to decode mp3 files.

[mingus](https://github.com/bspaans/python-mingus), for SoundGen, capriccio's sound generator.

## Example (with an audio file)
```python
import capriccio

t = datetime.datetime.now() + datetime.timedelta(seconds=10)
a = capriccio.Alarm(t, "alarm.mp3")

# Make sure a is retained, or else when the main thread ends, this alarm will also be released.

a.destroy() # Stop the alarm clock.
```
    
## Example (let capriccio automatically generate music)
```python
import capriccio

t = datetime.datetime.now() + datetime.timedelta(seconds=10)
a = capriccio.Alarm(t, 0, True)

# Make sure a is retained, or else when the main thread ends, this alarm will also be released.

a.destroy() # Stop the alarm clock.
```

or to run it directly, use
```
$ python capriccio.py -d <delay in seconds> -t <audio filename>
$ python capriccio.py -d <delay in seconds> -i <instrument id>
```

## Available instruments
Currently the following instruments are available for SoundGen:

| id |              Name           | MiDi |
| -----------------------:|:---------------------------:| ---- |
| * | Electric Grand Piano | 3 |
| 1 | Pan Flute | 76 |
| 2 | French Horn | 61 |
| 3 | Lead 8 (bass + lead) | 88 |
| 4 | FX 3 (crystal) | 99 |
| 5 | Steel Drums | 115 |
| 6 | Bird Tweet | 124 |
| 7 | Gunshot | 128 |
| 8 | String Ensemble 2 | 50 |
| 9 | Piccolo | 73 |

*: Default (anything not in the list)

## License
capriccio is released under the MIT license. See LICENSE for details.

Audio files within `Sounds` directory are released under a Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License.
