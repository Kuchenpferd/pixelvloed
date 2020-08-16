# The protocol for the UDP pixelvloed client and server

Pixelvloed allows clients to send up to a specific amount of pixels per message.
The amount of pixels depends on the protocol used. The maximum size of one pixelvloed packet is 1122 bytes.
Each pixelvloed packet contains a header and a data part. The header defines the protocol used and its data layout. The data describes the properties of the individual pixels. All values used in messages should be little endian.

Clients can switch between protocol versions at will between packets but not within packets.

The header of a pixelvloed packet consists of two bytes. The first byte defines the version of the protocol used. The second byte defines the protocol settings. Both are explained for each protocol below in the table.

The data of a pixelvloed packet contains information on which pixels should get what color. The representation of this information is heavily dependent on the protocol used and is explained below.

## Protocol: 0 (0x00)

Protocol 0 is the simplest and easiest to use. Full 24 bit colors can be used with optional alpha.

### Header

| Byte   | Bit     |   Contents                                                                    |
|--------|---------|-------------------------------------------------------------------------------|
| byte 0 | bit 7-0 | Protocol version. (For this protocol always 0x00.)                            |
| byte 1 | bit 7-1 | Not used.                                                                     |
|        | bit   0 | Alpha enable bit. (0: alpha is disabled. 1: alpha is enabled.)                |

### Data

The data describes the X and Y coordinates and the R, G, B and optional alpha color values. Multiple pixels can be send in one message.

#### Alpha disabled

- Bytes/pixel:    7
- Pixels/message: 160

| Byte   | Bit     |   Contents                                                                    |
|--------|---------|-------------------------------------------------------------------------------|
| byte 0 | bit 7-0 | Lowest 8 bits of the X coordinate of the pixel.                               |
| byte 1 | bit 7-0 | Highest 8 bits of the X coordinate of the pixel.                              |
| byte 2 | bit 7-0 | Lowest 8 bits of the Y coordinate of the pixel.                               |
| byte 3 | bit 7-0 | Highest 8 bits of the Y coordinate of the pixel.                              |
| byte 4 | bit 7-0 | R color value.                                                                |
| byte 5 | bit 7-0 | G color value.                                                                |
| byte 6 | bit 7-0 | B color value.                                                                |

#### Alpha enabled

- Bytes/pixel:    8
- Pixels/message: 140

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

## Protocol: 1 (0x01) Only supported on the C server

Protocol 1 compresses the coordinates so more pixels may be send in one message. Full 24 bit colors can be used with optinal alpha.

### Header

| Byte   | Bit     |   Contents                                                                    |
|--------|---------|-------------------------------------------------------------------------------|
| byte 0 | bit 7-0 | Protocol version. (For this protocol always 0x01.)                            |
| byte 1 | bit 7-1 | Not used.                                                                     |
|        | bit   0 | Alpha enable bit. (0: alpha is disabled. 1: alpha is enabled.)                |

### Data

The data describes the X and Y coordinates and the R, G, B and optional alpha color values. Multiple pixels can be send in one message.

#### Alpha disabled

- Bytes/pixel:    6
- Pixels/message: 186

| Byte   | Bit     |   Contents                                                                    |
|--------|---------|-------------------------------------------------------------------------------|
| byte 0 | bit 7-0 | Lowest 8 bits of the X coordinate of the pixel.                               |
| byte 1 | bit 3-0 | Highest 4 bits of the X coordinate of the pixel.                              |
| byte 1 | bit 7-4 | Lowest 4 bits of the Y coordinate of the pixel.                               |
| byte 2 | bit 7-0 | Highest 8 bits of the Y coordinate of the pixel.                              |
| byte 3 | bit 7-0 | R color value.                                                                |
| byte 4 | bit 7-0 | G color value.                                                                |
| byte 5 | bit 7-0 | B color value.                                                                |

#### Alpha enabled

- Bytes/pixel:    7
- Pixels/message: 160

| Byte   | Bit     |   Contents                                                                    |
|--------|---------|-------------------------------------------------------------------------------|
| byte 0 | bit 7-0 | Lowest 8 bits of the X coordinate of the pixel.                               |
| byte 1 | bit 3-0 | Highest 8 bits of the X coordinate of the pixel.                              |
| byte 1 | bit 7-4 | Lowest 8 bits of the Y coordinate of the pixel.                               |
| byte 2 | bit 7-0 | Highest 8 bits of the Y coordinate of the pixel.                              |
| byte 3 | bit 7-0 | R color value.                                                                |
| byte 4 | bit 7-0 | G color value.                                                                |
| byte 5 | bit 7-0 | B color value.                                                                |
| byte 6 | bit 7-0 | Alpha color value.                                                            |

## Protocol: 2 (0x02) Only supported on the C server

Protocol 2 compresses the coordinates and colors so more pixels may be send in one message. Only 8 bit colors can be used with optinal alpha.

### Header

| Byte   | Bit     |   Contents                                                                    |
|--------|---------|-------------------------------------------------------------------------------|
| byte 0 | bit 7-0 | Protocol version. (For this protocol always 0x02.)                            |
| byte 1 | bit 7-1 | Not used.                                                                     |
|        | bit   0 | Alpha enable bit. (0: alpha is disabled. 1: alpha is enabled.)                |

### Data

The data describes the X and Y coordinates and the R, G, B and optional alpha color values. Multiple pixels can be send in one message.

#### Alpha disabled

- Bytes/pixel:    4
- Pixels/message: 280

| Byte   | Bit     |   Contents                                                                    |
|--------|---------|-------------------------------------------------------------------------------|
| byte 0 | bit 7-0 | Lowest 8 bits of the X coordinate of the pixel.                               |
| byte 1 | bit 3-0 | Highest 4 bits of the X coordinate of the pixel.                              |
| byte 1 | bit 7-4 | Lowest 4 bits of the Y coordinate of the pixel.                               |
| byte 2 | bit 7-0 | Highest 8 bits of the Y coordinate of the pixel.                              |
| byte 3 | bit 7-5 | 3 bit R color value.                                                          |
| byte 3 | bit 4-2 | 3 bit G color value.                                                          |
| byte 3 | bit 1-0 | 2 bit B color value.                                                          |

#### Alpha enabled

- Bytes/pixel:    4
- Pixels/message: 280

| Byte   | Bit     |   Contents                                                                    |
|--------|---------|-------------------------------------------------------------------------------|
| byte 0 | bit 7-0 | Lowest 8 bits of the X coordinate of the pixel.                               |
| byte 1 | bit 3-0 | Highest 8 bits of the X coordinate of the pixel.                              |
| byte 1 | bit 7-4 | Lowest 8 bits of the Y coordinate of the pixel.                               |
| byte 2 | bit 7-0 | Highest 8 bits of the Y coordinate of the pixel.                              |
| byte 3 | bit 7-6 | 2 bit R color value.                                                          |
| byte 3 | bit 5-4 | 2 bit G color value.                                                          |
| byte 3 | bit 3-2 | 2 bit B color value.                                                          |
| byte 3 | bit 1-0 | 2 bit alpha color value.                                                      |

## Protocol: 3 (0x03) Only supported on the C server

Protocol 3 compresses the coordinates and colors so more pixels may be send in one message. Only 8 bit colors can be used with optinal alpha.

### Header

| Byte   | Bit     |   Contents                                                                    |
|--------|---------|-------------------------------------------------------------------------------|
| byte 0 | bit 7-0 | Protocol version. (For this protocol always 0x03.)                            |
| byte 1 | bit 7-5 | 3 bit R color value for all pixels in this message.                           |
|        | bit 4-2 | 3 bit G color value for all pixels in this message.                           |
|        | bit 1-0 | 2 bit B color value for all pixels in this message.                           |

### Data

The data describes the X and Y coordinates. Multiple pixels can be send in one message.

- Bytes/pixel:    3
- Pixels/message: 373

| Byte   | Bit     |   Contents                                                                    |
|--------|---------|-------------------------------------------------------------------------------|
| byte 0 | bit 7-0 | Lowest 8 bits of the X coordinate of the pixel.                               |
| byte 1 | bit 3-0 | Highest 4 bits of the X coordinate of the pixel.                              |
| byte 1 | bit 7-4 | Lowest 4 bits of the Y coordinate of the pixel.                               |
| byte 2 | bit 7-0 | Highest 8 bits of the Y coordinate of the pixel.                              |

# The Autodetection system, Only supported on the Python servers

A pixelvloed server should broadcast a package advertising its settings with the following string content

```
"%s:%f %s:%d %d*%d" % (PROTOCOL_PREAMBLE, PROTOCOL_VERSION, UDP_IP, UDP_PORT, width, height)
```

A client should listen for these packages, split it on spaces and check the preample and protocol_version to see if it is capable of speaking the requested protocol.

An example of a broadcasted packet would be:

```
pixelvloed:1.00 192.168.0.1:5005 1920*1080
```
