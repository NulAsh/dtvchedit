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

f1 = open('dtv_mw_s1', 'rb')
d = f1.read()
f1.close()
len1 = int.from_bytes(d[:4], 'big')
if len1 + 4 == len(d):
    print('Length OK')
else:
    print('Length error')
    exit(1)
xor1 = (len(d) & 0xff) ^ 0xd6
realcrc = crc32mpeg2(d[8:])
readcrc = int.from_bytes(d[4:8], 'big')
if realcrc == readcrc:
    print('CRC OK')
else:
    print('CRC error')
    print('From header: ' + hex(readcrc))
    print('Calculated:  ' + hex(realcrc))
    exit(2)
tmp = int.from_bytes(d[8:12], 'big')
if tmp == 19:
    print('bigint[0008:000C]=0x13, everything fine')
else:
    print('Warning: bigint[0008:000C]=' + hex(tmp) + ', not 0x13, maybe something wrong')
d = bytearray(d[0xc:])
for i in range(len(d)):
    d[i] ^= xor1
tmp = int.from_bytes(d[:4], 'big')
if tmp == 6:
    print('decoded_bigint[0000:0004]=6, everything fine')
else:
    print('Warning: decoded_bigint[0000:0004]=' + hex(tmp) + ', not 0x6, maybe something wrong')
numchannels = int.from_bytes(d[4:8], 'big')
print('Found', numchannels, 'channels')
f2 = open('channels.txt', 'w', encoding='utf-8')
bidx = 8
for i in range(numchannels):
    if d[bidx] != 1:
        print('d['+str(bidx)+'] != 1 - something wrong')
    lenname = int.from_bytes(d[bidx + 1:bidx + 5], 'little')
    binrcd = d[bidx:bidx + lenname + d[bidx + lenname + 9] * 7 + 121]
    nameb = binrcd[5:5 + lenname]
    for j in range(len(nameb)):
        nameb[j] ^= 0x37
    s = str(nameb, 'utf-8')
    print(str(binrcd[-69]) + '. ' + s)
    f2.write(repr([s,binrcd[lenname + 5:]])+'\n')
    bidx += len(binrcd)
