"""
Read the player list of a StarCraft 1.16 replay.

A replay's sections are PKWare DCL "implode" compressed; `explode` is a port
of zlib's contrib/blast.c. Only the header is read: the players watching a
replay together in a LAN game can be at most as many as the replay's players.
"""
import struct
from typing import List

_LITLEN = [11, 124, 8, 7, 28, 7, 188, 13, 76, 4, 10, 8, 12, 10, 12, 10, 8, 23, 8, 9, 7, 6, 7, 8, 7, 6, 55, 8, 23,
           24, 12, 11, 7, 9, 11, 12, 6, 7, 22, 5, 7, 24, 6, 11, 9, 6, 7, 22, 7, 11, 38, 7, 9, 8, 25, 11, 8, 11, 9, 12,
           8, 12, 5, 38, 5, 38, 5, 11, 7, 5, 6, 21, 6, 10, 53, 8, 7, 24, 10, 27, 44, 253, 253, 253, 252, 252, 252,
           13, 12, 45, 12, 45, 12, 61, 12, 45, 44, 173]
_LENLEN = [2, 35, 36, 53, 38, 23]
_DISTLEN = [2, 20, 53, 230, 247, 151, 248]
_BASE = [3, 2, 4, 5, 6, 7, 8, 9, 10, 12, 16, 24, 40, 72, 136, 264]
_EXTRA = [0, 0, 0, 0, 0, 0, 0, 0, 1, 2, 3, 4, 5, 6, 7, 8]

HEADER_SIZE = 0x279
PLAYERS_OFFSET = 0xA1
PLAYER_SIZE = 36


def _huffman(compact):
    lengths = []
    for b in compact:
        lengths += [b & 15] * ((b >> 4) + 1)
    count = [0] * 14
    for n in lengths:
        count[n] += 1
    offs = [0] * 14
    for n in range(1, 13):
        offs[n + 1] = offs[n] + count[n]
    symbol = [0] * len(lengths)
    for s, n in enumerate(lengths):
        if n:
            symbol[offs[n]] = s
            offs[n] += 1
    return count, symbol


_LIT, _LEN, _DIST = _huffman(_LITLEN), _huffman(_LENLEN), _huffman(_DISTLEN)


class _Bits:
    def __init__(self, data):
        self.data, self.pos, self.buf, self.left = data, 0, 0, 0

    def bit(self):
        if self.left == 0:
            self.buf, self.left = self.data[self.pos], 8
            self.pos += 1
        b = self.buf & 1
        self.buf >>= 1
        self.left -= 1
        return b

    def bits(self, n):
        return sum(self.bit() << i for i in range(n))

    def decode(self, table):
        count, symbol = table
        code = first = index = 0
        for n in range(1, 14):
            code |= self.bit() ^ 1  # codes are stored bit-inverted
            if code < first + count[n]:
                return symbol[index + code - first]
            index += count[n]
            first = (first + count[n]) << 1
            code <<= 1
        raise ValueError("invalid code in replay")


def explode(data: bytes) -> bytes:
    s = _Bits(data)
    coded_literals, dict_bits = s.bits(8), s.bits(8)
    out = bytearray()
    while True:
        if s.bit():
            sym = s.decode(_LEN)
            length = _BASE[sym] + s.bits(_EXTRA[sym])
            if length == 519:  # end of stream
                return bytes(out)
            shift = 2 if length == 2 else dict_bits
            dist = (s.decode(_DIST) << shift) + s.bits(shift) + 1
            for _ in range(length):
                out.append(out[-dist])
        else:
            out.append(s.decode(_LIT) if coded_literals else s.bits(8))


def _section(f, size: int) -> bytes:
    _checksum, chunks = struct.unpack("<II", f.read(8))
    out = bytearray()
    for _ in range(chunks):
        (length,) = struct.unpack("<I", f.read(4))
        data = f.read(length)
        expected = min(8192, size - len(out))
        out += data if length == expected else explode(data)
    return bytes(out[:size])


def replay_players(path: str) -> List[str]:
    """Names of the human and computer players of a replay."""
    with open(path, "rb") as f:
        _section(f, 4)  # replay id
        header = _section(f, HEADER_SIZE)
    names = []
    for i in range(12):
        rec = header[PLAYERS_OFFSET + PLAYER_SIZE * i: PLAYERS_OFFSET + PLAYER_SIZE * (i + 1)]
        player_type, name = rec[8], rec[11:].split(b"\0")[0]
        if player_type in (1, 2) and name:  # computer, human
            names.append(name.decode("cp949", "replace"))
    return names
