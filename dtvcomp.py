#!/usr/bin/env python
tbl = [0] * 256
for i in range(256):
    register = i
    register = register << (32 - 8)
    for j in range(8):
        if register & 0x80000000 != 0:
            register = (register << 1) ^ 0x4c11db7
        else:
            register = (register << 1)
    tbl[i] = register & 0xffffffff

def crc32mpeg2(in_data):
    global tbl
    if isinstance(in_data, str):
        in_data = bytearray(in_data, 'utf-8')
    register = 0xffffffff
    for octet in in_data:
        tblidx = ((register >> (32 - 8)) ^ octet) & 0xff
        register = ((register << 8) ^ tbl[tblidx]) & 0xffffffff
    return register

f1 = open('channels.txt', 'r', encoding='utf-8')
bindata = bytearray()
numchannels = 0
for line in f1:
    channel = eval(line)
    nameb = bytearray(channel[0].encode('utf-8'))
    for i in range(len(nameb)):
        nameb[i] ^= 0x37
    channel[1] = bytearray(channel[1])
    numchannels += 1
    channel[1][-72:-68] = numchannels.to_bytes(4, 'big')
    bindata += b'\x01' + len(nameb).to_bytes(4, 'little') + nameb + channel[1]
bindata = bytearray(b'\x00\x00\x00\x06') + numchannels.to_bytes(4, 'big') + bindata
rc = ((len(bindata) + 12) & 0xff) ^ 0xd6
for i in range(len(bindata)):
    bindata[i] ^= rc
bindata = b'\x00\x00\x00\x13' + bindata
crc = crc32mpeg2(bindata).to_bytes(4, 'big')
f2 = open('dtv_mw_s1', 'wb')
f2.write((len(bindata) + 4).to_bytes(4, 'big'))
f2.write(crc)
f2.write(bindata)
f2.close()
