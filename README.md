# capriccio
------
A simple alarm clock module written in Python.

## Dependencies
------
[pyglet](http://www.pyglet.org), for playing audio. Pyglet also requires [AVbin](http://avbin.github.io/AVbin/Home/Home.html) to decode mp3 files.

## Example
------
    import capriccio
    
    t = datetime.datetime.now() + datetime.timedelta(seconds=10)
    a = capriccio.Alarm(t, "alarm.mp3")
    
    # Make sure a is retained, or else when the main thread ends, this alarm will also be released.
    
    a.destroy() # Stop the alarm clock.

or to run it directly, use

    $ python capriccio.py -d <delay in seconds> -t <audio filename>

## License
------
capriccio is released under the MIT license. See LICENSE for details.

Audio files within `Sounds` directory are released under a Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License.
