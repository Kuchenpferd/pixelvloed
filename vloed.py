#!/usr/bin/python
"""This is a udp / binary version of PixelFlut

Inspired by the PixelFlut beamer on eth0:winter 2016 and
code from https://github.com/defnull/pixelflut/
"""

__version__ = 0.3
__author__ = "Jan Klopper <jan@underdark.nl>"

import pygame
from pygame import locals as pygamelocals
import struct
import time
import socket

from gevent import spawn, monkey
from gevent.server import DatagramServer
from gevent.queue import Queue

monkey.patch_all()
UDP_IP = "127.0.0.1"
UDP_PORT = 5005
DISCOVER_PORT = 5006
PROTOCOL_VERSION = 1
MAX_PROTOCOL_VERSION = 1
PROTOCOL_PREAMBLE = "pixelvloed"
MAX_PIXELS = 140

class Canvas(object):
  """PixelVloed display class"""

  def __init__(self, queue, width=1366, height=768, debug=False):
    """Init the pixelVloed server"""
    self.debug = debug
    self.pixeloffset = 2
    self.fps = 30
    self.screen = None
    self.udp_ip = UDP_IP
    self.udp_port = UDP_PORT
    self.width = width
    self.height = height
    self.canvas()
    self.set_title()
    self.queue = queue
    self.limit = MAX_PIXELS
    self.pixels = None
    self.broadcastsocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    self.broadcastsocket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    self.broadcastsocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

  @staticmethod
  def set_title(text=None):
    """Sets the window title"""
    title = 'PixelVloed %0.02f' % __version__
    if text:
      title += ' ' + text
    pygame.display.set_caption(title)

  def canvas(self):
    """Init the pygame canvas"""
    pygame.init()
    pygame.mixer.quit()
    self.screen = pygame.display.set_mode((self.width, self.height),
                                          pygamelocals.DOUBLEBUF)

  def clear(self, r=0, g=0, b=0): # pylint: disable=C0103
    """ Fill the entire screen with a solid colour (default: black)"""
    self.screen.fill((r, g, b))

  def Pixel(self, x, y, r, g, b, a=255): # pylint: disable=C0103
    """Print a pixel to the screen"""
    try:
      self.pixels[x][y] = (r*256*256) + (g*256) + b
    except IndexError:
      pass

  def CanvasUpdate(self):
    """Updates the screen according to self.fps"""
    lasttime = time.time()
    lastbroadcast = time.time()
    changed = False
    while True:
      changed = self.Draw() or changed
      if time.time() - lastbroadcast > 2:
        lastbroadcast = time.time()
        self.SendDiscoveryPacket()

      if time.time() - lasttime >= 1.0 / self.fps and changed:
        self.pixels = None # release the lock on these pixels so we can flip
        pygame.display.flip()
        changed = False
        lasttime = time.time()
      else:
        time.sleep(1.0 / self.fps)

  def Draw(self):
    """Draws pixels specified in the received packages in the queue"""
    if self.queue.empty():
      # indicat that nothing was done, and w can skip flipping the screen
      return False
    #access the pixel array and lock it
    self.pixels = pygame.surfarray.pixels2d(self.screen)
    returntime = time.time() + (1.0 / self.fps)
    # while we have stuff in the queue, and its not our next time to draw a
    # frame, lets process packets from the queue
    while time.time() < returntime and not self.queue.empty():
      try:
        data = self.queue.get()
        preamble = struct.unpack_from("<?", data)[0]
        protocol = struct.unpack_from("<B", data, 1)[0]
        packetformat = ("<2H4B" if preamble else "<2H3B")
        pixellength = (8 #xx,yy,r,g,b,a
                       if preamble else
                       7 #xx,yy,r,g,b
                       )
        pixelcount = min(((len(data)-1) / pixellength),
                         self.limit)
        if self.debug:
          print '%d pixels received, protocol V %d' % (pixelcount, protocol)
        for i in xrange(0, pixelcount):
          pixel = struct.unpack_from(
              packetformat,
              data,
              self.pixeloffset + (i*pixellength))
          if self.debug:
            print pixel
          self.Pixel(*pixel)
      except Exception as error:
        if self.debug:
          # All exceptions will be printed, but won't result in a crash.
          print error
    # indicate that we have been drawing stuff
    return True

  def SendDiscoveryPacket(self):
    """Lets send out our ip/port/resolution to any listening clients"""
    self.broadcastsocket.sendto(
        '%s:%f %s:%d %d*%d' % (PROTOCOL_PREAMBLE, PROTOCOL_VERSION,
                               UDP_IP, UDP_PORT,
                               self.width, self.height),
        ('<broadcast>', DISCOVER_PORT))
    if self.debug:
      print 'sending discovery packet'

  def __del__(self):
    """Clean up any sockets we created"""
    self.broadcastsocket.close()

class PixelVloedServer(DatagramServer):
  """PixelVloed server class"""

  def __init__(self, *args, **kwargs):
    """Set up some vars for this instance"""
    self.queue = Queue()
    pixelcanvas = Canvas(self.queue)
    __request_processing_greenlet = spawn(pixelcanvas.CanvasUpdate)
    DatagramServer.__init__(self, *args, **kwargs)

  def handle(self, data, _address):
    """Is called by the DataGramServer whenever an udp package is received"""
    self.queue.put(data)

class PixelVloedClient(object):
  """Sets up a client

  Arguments:
    firstserver: (bool) False, select the first server immediately
    debug: (bool) False
    ip: (str) None
    port: (int) None
    width: (int) 640
    height: (int) 480

  Listens for servers if no ip is given
  """

  def __init__(self, firstserver=False, debug=False,
               ip=None, port=None,
               width=640, height=480):
    self.sleep = 0.01
    self.debug = debug
    if not ip:
      servers = False
      while servers == False:
        servers = self.DiscoverServers(firstserver)
      self.ipaddress = servers[0]['ip']
      self.port = servers[0]['port']
      self.width = servers[0]['width']
      self.height = servers[0]['height']

      if self.debug:
        print ('displaying on %(ip)s:%(port)d, %(width)d*%(height)dpx' %
            servers[0])
    else:
      self.ipaddress = ip
      self.port = port
      self.width = width
      self.height = height
      if self.debug:
        print ('displaying on %(ip)s:%(port)d, %(width)d*%(height)dpx' %
            self)
    self.sock = socket.socket(socket.AF_INET, # Internet
                              socket.SOCK_DGRAM) # UDP

  def Sleep(self, duration=None):
    """Sleeps the designated amount of time"""
    time.sleep(duration if duration else self.sleep)

  def SendPacket(self, message, sleep=True):
    """Sends the message to the udp server

    Arguments:
      message: (str, 140)
      sleep:  (bool) True, should the client sleep for a while?
    """
    self.sock.sendto(message, (self.ipaddress, self.port))
    if sleep:
      self.Sleep()

  @staticmethod
  def DiscoverServers(returnfirst=False, timeout=5):
    """Discover servers that send out the pixelfvloed preample"""
    discoverysock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    discoverysock.bind(('', DISCOVER_PORT))
    starttime = time.time()
    servers = []
    foundhash = {}
    while (time.time() - timeout) < starttime:
      data, _addr = discoverysock.recvfrom(1024)
      try:
        if data.startswith(PROTOCOL_PREAMBLE):
          dataset = data.split(' ')
          if float(dataset[0].split(':')[1]) <= MAX_PROTOCOL_VERSION:
            ipaddress = dataset[1].split(':')[0]
            port = int(dataset[1].split(':')[1])
            width = int(dataset[2].split('*')[0])
            height = int(dataset[2].split('*')[1])
            if data not in foundhash:
              newserver = {'ip': ipaddress,
                           'port': port,
                           'width': width,
                           'height': height}
              foundhash[data] = True
              print 'New pixelvloed screen found: %r' % newserver
              servers.append(newserver)
              if returnfirst:
                return servers
      except:
        pass
    if servers:
      return servers
    return False

def NewMessage():
  """Creates a new message with the correct max size, rgb mode and version"""
  message = MaxSizeList(MAX_PIXELS+2)
  message.append(SetRGBAMode(False))
  message.append(SetVersionBit())
  return message

def RGBPixel(x, y, r, g, b, a=None): # pylint: disable=C0103
  """Generates the packed data for a pixel"""
  if a:
    return struct.pack("<2H4B", x, y, r, g, b, a)
  return struct.pack("<2H3B", x, y, r, g, b)

def SetRGBAMode(mode):
  """Generate the rgb/rgba bit"""
  return struct.pack("<?", mode)

def SetVersionBit(protocol=1):
  """Generate the Version bit"""
  return struct.pack("<B", protocol)

class MaxSizeList(list):
  """A list that raises an indexError when it reaches the designated max size"""
  def __init__(self, maxcount=100):
    """Inits a list with a maxcount

    Arguments:
      maxcount: (int) 100
    """
    self.maxsize = maxcount
    super(MaxSizeList, self).__init__()

  def append(self, item):
    """Appends an item to the list"""
    super(MaxSizeList, self).append(item)
    if self.__len__() == self.maxsize:
      raise IndexError('max size reached')

def RunServer():
  """Runs a pixelvloed server"""
  PixelVloedServer('%s:%d' %(UDP_IP, UDP_PORT)).serve_forever()

if __name__ == '__main__':
  RunServer()
