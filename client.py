#!/usr/bin/python
"""This is the client for Pixelvloed

https://github.com/janklopper/pixelvloed

We've given you an example of a function that randomly places randomly colored
pixels somewhere on the screen.

# Copy the function RandomFill,
# give it a new name by replacing the word "RandomFill" By your own name
# Think of your own creative pixel packages.

Then you can run the client with the -e flag (for effect)

./client.py -e MyColorPusher
"""

__version__ = 0.4
__author__ = "Jan Klopper <jan@underdark.nl>"

import random
from vloed import PixelVloedClient, Packet, RGBPixel, MAX_PIXELS

def RandomFill(screen, width, height):
  """Generates a random number of pixels with a random color"""
  for _x in xrange(1, MAX_PIXELS): # lets loop over the amount of pixels
    pixel = RGBPixel(random.randint(0, width), # select a random position on the width of the screen
                     random.randint(0, height), # select a random position on the height of the screen
                     random.randint(0, 255), # select a random value for red
                     random.randint(0, 255), # select a random value for green
                     random.randint(0, 255) # select a random value for blue
                     )
    screen.show(pixel) # lets push the pixel to the screen!

def RunClient(options):
  """Discover the servers and start sending to the first one"""
  client = PixelVloedClient(True, # start as soon as we find a server
                            options.debug, # show debugging output
                            options.ip, # ip of the server, None for autodetect
                            options.port, # port of the server None for autodetect
                            options.width, # Screen pixels wide, None for autodetect
                            options.height  # Screen pixels height, None for autodetect
                            )

  # Lets create a screen which buffers the pixels we add to it, and sends them to the actual screen.
  screen = Packet(client)
  # loop the effect until we cancel by pressing ctrl+c / exit the program

  while screen:

    # add some pixels to the screen with our functions
    # the width/height are read from the client's config
    options.effect(screen, client.width, client.height)

if __name__ == '__main__':
  # if this script is called from the command line, and thus not imported
  # start a client and start sending messages
  import optparse
  parser = optparse.OptionParser()
  parser.add_option('-v', action="store_true", dest="debug", default=False,
                    help="Enable debugging output")
  parser.add_option('-i', action="store", dest="ip", default=None,
                    help="Ip of the server, leave empty for auto-discovery")
  parser.add_option('-p', action="store", dest="port", default=None, type="int",
                    help="Port of the server, leave empty for default")
  parser.add_option('-x', action="store", dest="width", default=None,
                    type="int", help="Width of the server's screen")
  parser.add_option('-y', action="store", dest="height", default=None,
                    type="int", help="Height of the server's screen")
  parser.add_option('-e', action="store", dest="effect", default='RandomFill',
                    type="str", help="Which effect to run.")
  options, remainder = parser.parse_args()

  # we run the effect that has been given trough the -e flag.
  # This defaults to RandomFill
  options.effect = locals()[options.effect]

  try:
    RunClient(options)
  except KeyboardInterrupt:
    print('Closing client')
