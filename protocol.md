# The PixelVloed UDP protocol for client and server

PixelVloed lets you update pixels on a screen by sending UDP packets.

About PixelVloed packets:
 - The maximum packet size is 1122 bytes.
 - There are four different protocols that encode pixels differently.
 - The number of pixels that can be sent with each packet varies for each protocol.
 - In all four protocols, the header is two bytes and the first byte determines protocol version.
 - Clients can switch between protocol versions at will between packets but not within packets.
 - All values used in messages should be little endian.

## Protocols

The four protocols in summary:
 - Protocol 0: 16-bit X/Y coordinates, 24-bit RGB with optional 8-bit alpha.
 - Protocol 1: 12-bit X/Y coordinates, 24-bit RGB with optional 8-bit alpha.
 - Protocol 2: 12-bit X/Y coordinates, 8-bit RGB or 6-bit RGB and 2-bit alpha.
 - Protocol 3: 12-bit X/Y coordinates, 8-bit RGB (no alpha), uses one color for all pixels.

## Protocol 0

Protocol 0 is the simplest and easiest to use. Full 24 bit colors can be used with optional alpha.

### Header

| Byte   | Bit     |   Contents                                                                    |
|--------|---------|-------------------------------------------------------------------------------|
| byte 0 | bit 7-0 | Protocol version. (For this protocol always 0x00.)                            |
| byte 1 | bit 7-1 | Not used.                                                                     |
|        | bit   0 | Alpha enable bit. (0: alpha is disabled. 1: alpha is enabled.)                |

So either `\x00\x00` for no alpha, or `\x00\x01` for alpha.

### Data

Each pixel is encoded with 7 bytes when alpha is disabled, 8 bytes when alpha is enabled.

The data part of a packet is an array of such sequences of bytes.

 - 2 bytes for the X coordinate
 - 2 bytes for the Y coordinate
 - 1 byte for R (red)
 - 1 byte for G (green)
 - 1 byte for B (blue)
 - Optionally 1 byte for A (alpha)

Pixels per message:
 - 160 when alpha is disabled
 - 140 when alpha is enabled

### Pixel layout (alpha disabled)

| Byte   | Bit     |   Contents                                                                    |
|--------|---------|-------------------------------------------------------------------------------|
| byte 0 | bit 7-0 | Lowest 8 bits of the X coordinate of the pixel.                               |
| byte 1 | bit 7-0 | Highest 8 bits of the X coordinate of the pixel.                              |
| byte 2 | bit 7-0 | Lowest 8 bits of the Y coordinate of the pixel.                               |
| byte 3 | bit 7-0 | Highest 8 bits of the Y coordinate of the pixel.                              |
| byte 4 | bit 7-0 | R color value.                                                                |
| byte 5 | bit 7-0 | G color value.                                                                |
| byte 6 | bit 7-0 | B color value.                                                                |

Here is an example of one packet that contains one pixel:

```
00000000 00000000 00000001 10000001 00000001 00001111 10000000 00000000 00000000
```

An explanation of this packet:

 - `00000000 00000000` signify protocol 0 with alpha disabled.
 - `00000001 10000001` signify first pixel's *X = 2^8 + 2^7 + 2`1 = 385*.
 - `00000001 00001111` signify first pixel's *Y = 2^8 + 2^3 + 2^2 + 2^1 + 2^0 = 271*.
 - `10000000` signifies first pixel's *R = 127*.
 - `00000000` signifies first pixel's *G = 0*.
 - `00000000` signifies first pixel's *B = 0*.

### Pixel layout (alpha enabled)

| Byte   | Bit     |   Contents                                                                    |
|--------|---------|-------------------------------------------------------------------------------|
| byte 0 | bit 7-0 | Lowest 8 bits of the X coordinate of the pixel.                               |
| byte 1 | bit 7-0 | Highest 8 bits of the X coordinate of the pixel.                              |
| byte 2 | bit 7-0 | Lowest 8 bits of the Y coordinate of the pixel.                               |
| byte 3 | bit 7-0 | Highest 8 bits of the Y coordinate of the pixel.                              |
| byte 4 | bit 7-0 | R color value.                                                                |
| byte 5 | bit 7-0 | G color value.                                                                |
| byte 6 | bit 7-0 | B color value.                                                                |
| byte 7 | bit 7-0 | Alpha color value.                                                            |

Here is the same example for one packet that contains one pixel:

```
00000000 00000000 00000001 10000001 00000001 00001111 10000000 00000000 00000000 10101010
P=0      A=off    X=385             Y=271             R=127    G=0      B=0      A=170
```

 - `10101010` signifies first pixel's *A = 2^7 + 2^5 + 2^3 + 2^1 = 170*, or *170/255 = 66,67%* transparent.

## Protocol 1

**Only supported on the C server.**

Protocol 1 is the same as protocol 0, except it only uses 12 bits per X/Y coordinate.

This uses fewer bytes when displays have *2^12 = 4096* pixels or less.

Full 24-bit colors can be used with optional alpha.

### Header

| Byte   | Bit     |   Contents                                                                    |
|--------|---------|-------------------------------------------------------------------------------|
| byte 0 | bit 7-0 | Protocol version. (For this protocol always 0x01.)                            |
| byte 1 | bit 7-1 | Not used.                                                                     |
|        | bit   0 | Alpha enable bit. (0: alpha is disabled. 1: alpha is enabled.)                |

### Data

Each pixel is encoded with 6 bytes when alpha is disabled, 7 bytes when alpha is enabled.

Pixels per message:
 - 186 when alpha is disabled
 - 160 when alpha is enabled

### Pixel layout (alpha disabled)

| Byte   | Bit     |   Contents                                                                    |
|--------|---------|-------------------------------------------------------------------------------|
| byte 0 | bit 7-0 | Lowest 8 bits of the X coordinate of the pixel.                               |
| byte 1 | bit 3-0 | Highest 4 bits of the X coordinate of the pixel.                              |
| byte 1 | bit 7-4 | Lowest 4 bits of the Y coordinate of the pixel.                               |
| byte 2 | bit 7-0 | Highest 8 bits of the Y coordinate of the pixel.                              |
| byte 3 | bit 7-0 | R color value.                                                                |
| byte 4 | bit 7-0 | G color value.                                                                |
| byte 5 | bit 7-0 | B color value.                                                                |

### Pixel layout (alpha enabled)

| Byte   | Bit     |   Contents                                                                    |
|--------|---------|-------------------------------------------------------------------------------|
| byte 0 | bit 7-0 | Lowest 8 bits of the X coordinate of the pixel.                               |
| byte 1 | bit 3-0 | Highest 4 bits of the X coordinate of the pixel.                              |
| byte 1 | bit 7-4 | Lowest 4 bits of the Y coordinate of the pixel.                               |
| byte 2 | bit 7-0 | Highest 8 bits of the Y coordinate of the pixel.                              |
| byte 3 | bit 7-0 | R color value.                                                                |
| byte 4 | bit 7-0 | G color value.                                                                |
| byte 5 | bit 7-0 | B color value.                                                                |
| byte 6 | bit 7-0 | Alpha color value.                                                            |

## Protocol 2

**Only supported on the C server.**

Protocol 2 is the same as protocol 1, except it only uses a single byte to represent color.

Pixels per message:
 - 280 when alpha is disabled
 - 280 when alpha is enabled

The reason why alpha doesn't use more space is that colors are degraded.

### Header

| Byte   | Bit     |   Contents                                                                    |
|--------|---------|-------------------------------------------------------------------------------|
| byte 0 | bit 7-0 | Protocol version. (For this protocol always 0x02.)                            |
| byte 1 | bit 7-1 | Not used.                                                                     |
|        | bit   0 | Alpha enable bit. (0: alpha is disabled. 1: alpha is enabled.)                |

### Data

The data describes the X and Y coordinates and the R, G, B and optional alpha color values. Multiple pixels can be send in one message.

### Pixel layout (alpha disabled)

| Byte   | Bit     |   Contents                                                                    |
|--------|---------|-------------------------------------------------------------------------------|
| byte 0 | bit 7-0 | Lowest 8 bits of the X coordinate of the pixel.                               |
| byte 1 | bit 3-0 | Highest 4 bits of the X coordinate of the pixel.                              |
| byte 1 | bit 7-4 | Lowest 4 bits of the Y coordinate of the pixel.                               |
| byte 2 | bit 7-0 | Highest 8 bits of the Y coordinate of the pixel.                              |
| byte 3 | bit 7-5 | 3 bit R color value.                                                          |
| byte 3 | bit 4-2 | 3 bit G color value.                                                          |
| byte 3 | bit 1-0 | 2 bit B color value.                                                          |

### Pixel layout (alpha enabled)

| Byte   | Bit     |   Contents                                                                    |
|--------|---------|-------------------------------------------------------------------------------|
| byte 0 | bit 7-0 | Lowest 8 bits of the X coordinate of the pixel.                               |
| byte 1 | bit 3-0 | Highest 4 bits of the X coordinate of the pixel.                              |
| byte 1 | bit 7-4 | Lowest 4 bits of the Y coordinate of the pixel.                               |
| byte 2 | bit 7-0 | Highest 8 bits of the Y coordinate of the pixel.                              |
| byte 3 | bit 7-6 | 2 bit R color value.                                                          |
| byte 3 | bit 5-4 | 2 bit G color value.                                                          |
| byte 3 | bit 3-2 | 2 bit B color value.                                                          |
| byte 3 | bit 1-0 | 2 bit alpha color value.                                                      |

## Protocol 3

**Only supported on the C server.**

Protocol 3 is different from the previous protocols:
 - All pixels will be colored with the same 8-bit RGB color.
 - No optional alpha channel is available in this protocol.

### Header

| Byte   | Bit     |   Contents                                                                    |
|--------|---------|-------------------------------------------------------------------------------|
| byte 0 | bit 7-0 | Protocol version. (For this protocol always 0x03.)                            |
| byte 1 | bit 7-5 | 3 bit R color value for all pixels in this message.                           |
|        | bit 4-2 | 3 bit G color value for all pixels in this message.                           |
|        | bit 1-0 | 2 bit B color value for all pixels in this message.                           |

### Data

Pixels per message: 373

| Byte   | Bit     |   Contents                                                                    |
|--------|---------|-------------------------------------------------------------------------------|
| byte 0 | bit 7-0 | Lowest 8 bits of the X coordinate of the pixel.                               |
| byte 1 | bit 3-0 | Highest 4 bits of the X coordinate of the pixel.                              |
| byte 1 | bit 7-4 | Lowest 4 bits of the Y coordinate of the pixel.                               |
| byte 2 | bit 7-0 | Highest 8 bits of the Y coordinate of the pixel.                              |

# The auto-detection system

**Only supported on the Python servers.**

A pixelvloed server should broadcast a package advertising its settings with the following string content:

```
"%s:%f %s:%d %d*%d" % (PROTOCOL_PREAMBLE, PROTOCOL_VERSION, UDP_IP, UDP_PORT, width, height)
```

A client should listen for these packages, split it on spaces and check the
preample and version fields to see if it is capable of speaking the requested
protocol.

An example of a broadcasted packet would be:

```
pixelvloed:1.00 192.168.0.1:5005 1920*1080
```
