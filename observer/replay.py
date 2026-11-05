"""
Read and rewrite the game settings of a StarCraft 1.16 replay.

A replay's sections are PKWare DCL "implode" compressed; `explode` is a port
of zlib's contrib/blast.c. How many can watch a replay together in a LAN game
depends on the game type it was recorded with, so a One on One replay is
rewritten as a Melee one (same game rules) to let more than two watch it.
"""
import struct
import zlib

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
GAME_TYPE_OFFSETS = (0x3C, 0x81)  # the game type, and again in the game template
MELEE, ONE_ON_ONE = 0x02, 0x04
# the rest of a Melee game's template (as in a recorded Melee replay) where
# One on One differs: victory condition, restriction flags, allies enabled
MELEE_TEMPLATE = {0x89: 0x01, 0x8F: 0x03, 0x90: 0x01}
HUMAN_SLOT = 0x06  # owner of a map's start slot (CHK OWNR)


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


def _skip_section(f):
    _checksum, chunks = struct.unpack("<II", f.read(8))
    for _ in range(chunks):
        (length,) = struct.unpack("<I", f.read(4))
        f.seek(length, 1)


def _game_type(header: bytes) -> int:
    return struct.unpack_from("<H", header, GAME_TYPE_OFFSETS[0])[0]


def _read(path: str):
    """The replay id section as stored, the header, and the stored rest."""
    with open(path, "rb") as f:
        _section(f, 4)
        id_end = f.tell()
        f.seek(0)
        id_section = f.read(id_end)
        header = _section(f, HEADER_SIZE)
        return id_section, header, f.read()


def map_players(path: str) -> int:
    """Start slots for humans on the replay's map."""
    with open(path, "rb") as f:
        _section(f, 4)  # replay id
        _section(f, HEADER_SIZE)
        _section(f, 4)  # commands size
        _skip_section(f)
        (map_size,) = struct.unpack("<I", _section(f, 4))
        chk = _section(f, map_size)
    pos = 0
    while pos + 8 <= len(chk):
        name, size = chk[pos:pos + 4], struct.unpack_from("<i", chk, pos + 4)[0]
        if name == b"OWNR":
            return chk[pos + 8:pos + 16].count(HUMAN_SLOT)
        pos += 8 + size
    raise ValueError(f"{path}: map has no OWNR section")


def is_one_on_one(path: str) -> bool:
    return _game_type(_read(path)[1]) == ONE_ON_ONE


def replay_seats(path: str, as_melee: bool = False) -> int:
    """How many viewers can join a LAN game of this replay.

    A replay lobby shows 8 open slots, but One on One replays admit only 2
    (a third viewer gets "Unable to join game", even with the seats byte
    raised); other game types admit the recorded game's seats (Melee: the
    map's players, Use Map Settings: 8). as_melee: the seats once a One on
    One replay is rewritten by write_as_melee.
    """
    header = _read(path)[1]
    if _game_type(header) != ONE_ON_ONE:
        return header[MAX_PLAYERS_OFFSET]
    return map_players(path) if as_melee else 2


def write_as_melee(src: str, dst: str):
    """Copy a One on One replay as a Melee one, which more viewers can join.

    Only the header's game settings change; its section is stored
    uncompressed (a chunk as long as its data), with the checksum BW keeps:
    the inverted CRC-32 of the data.
    """
    id_section, header, rest = _read(src)
    header = bytearray(header)
    for offset in GAME_TYPE_OFFSETS:
        struct.pack_into("<H", header, offset, MELEE)
    for offset, value in MELEE_TEMPLATE.items():
        header[offset] = value
    header[MAX_PLAYERS_OFFSET] = map_players(src)
    with open(dst, "wb") as f:
        f.write(id_section)
        f.write(struct.pack("<III", zlib.crc32(header) ^ 0xFFFFFFFF, 1, len(header)))
        f.write(header)
        f.write(rest)
