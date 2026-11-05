"""
Read the game settings of a StarCraft 1.16 replay.

A replay's sections are PKWare DCL "implode" compressed; `explode` is a port
of zlib's contrib/blast.c. Only the header is read: how many can watch a
replay together in a LAN game depends on the game type it was recorded with.
"""
import struct

_LITLEN = [11, 124, 8, 7, 28, 7, 188, 13, 76, 4, 10, 8, 12, 10, 12, 10, 8, 23, 8, 9, 7, 6, 7, 8, 7, 6, 55, 8, 23,
           24, 12, 11, 7, 9, 11, 12, 6, 7, 22, 5, 7, 24, 6, 11, 9, 6, 7, 22, 7, 11, 38, 7, 9, 8, 25, 11, 8, 11, 9, 12,
           8, 12, 5, 38, 5, 38, 5, 11, 7, 5, 6, 21, 6, 10, 53, 8, 7, 24, 10, 27, 44, 253, 253, 253, 252, 252, 252,
           13, 12, 45, 12, 45, 12, 61, 12, 45, 44, 173]
_LENLEN = [2, 35, 36, 53, 38, 23]
_DISTLEN = [2, 20, 53, 230, 247, 151, 248]
_BASE = [3, 2, 4, 5, 6, 7, 8, 9, 10, 12, 16, 24, 40, 72, 136, 264]
_EXTRA = [0, 0, 0, 0, 0, 0, 0, 0, 1, 2, 3, 4, 5, 6, 7, 8]

HEADER_SIZE = 0x279
MAX_PLAYERS_OFFSET = 0x39  # seats of the recorded game: 2 (1on1), the map's players (Melee), 8 (UMS)
GAME_TYPE_OFFSET = 0x3C
ONE_ON_ONE = 0x04


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


def replay_seats(path: str) -> int:
    """How many viewers can join a LAN game of this replay.

    A replay lobby shows 8 open slots, but One on One replays admit only 2
    (a third viewer gets "Unable to join game", even with the seats byte
    raised); other game types admit the recorded game's seats (Melee: the
    map's players, Use Map Settings: 8).
    """
    with open(path, "rb") as f:
        _section(f, 4)  # replay id
        header = _section(f, HEADER_SIZE)
    game_type = struct.unpack_from("<H", header, GAME_TYPE_OFFSET)[0]
    return 2 if game_type == ONE_ON_ONE else header[MAX_PLAYERS_OFFSET]

