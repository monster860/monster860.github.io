from pymclevel import TAG_Byte
from pymclevel import TAG_Int
from pymclevel import TAG_Compound
from pymclevel import TAG_Short
from pymclevel import TAG_Double
from pymclevel import TAG_String
from pymclevel import TAG_Float
from pymclevel import TAG_Long
import types
import math

displayName = "Create Paint Command Blocks"

inputs = (
    ("Center X", "string"),
    ("Center Z", "string"),
    ("Player Direction", ("+x", "-x", "+z", "-z")),
    ("Distance", "string"),
    ("Test X", "string"),
    ("Test Y", "string"),
    ("Test Z", "string")
)

def perform(level, box, options):
    centerx = int(options["Center X"])
    centerz = int(options["Center Z"])
    direction = options["Player Direction"];
    distance = float(options["Distance"])
    tx = int(options["Test X"])
    ty = int(options["Test Y"])
    tz = int(options["Test Z"])
    angleAdjust = 0;
    if direction == "-x":
        angleAdjust = 90
    elif direction == "+x":
        angleAdjust = -90
    elif direction == "-z":
        angleAdjust = 180

    mx = (box.minx - (centerx - 64))
    my = (box.minz + 1 - (centerz - 64))

    if True:
        for x in xrange(0, 16):
            for z in xrange(0, 16):
                if True:
                    rxm=int( math.ceil(math.degrees(math.atan2(my+ (z*4)   -48.64,distance*128))))
                    rx= int(math.floor(math.degrees(math.atan2(my+((z+1)*4)-48.64,distance*128))))
                    rym=int( math.ceil(math.degrees(math.atan2(mx+ (x*4)   -64,   distance*128)) + angleAdjust))
                    ry= int(math.floor(math.degrees(math.atan2(mx+((x+1)*4)-64,   distance*128)) + angleAdjust))
                    addCommandBlock(level, box.minx+x, box.miny-1, box.minz+z+1, "execute @p[x={0},y={1},z={2},r=1,rxm={3},rx={4},rym={5},ry={6},score_PaintBlack_min=1] ~ ~ ~ fill {7} {8} {9} {10} {11} {12} wool 15".format(tx, ty, tz, rxm, rx, rym, ry, (x*4)+box.minx,box.miny,(z*4)+box.minz+1,(x*4)+3+box.minx,box.miny,(z*4)+3+box.minz+1))
                    addCommandBlock(level, box.minx+x, box.miny-3, box.minz+z+1, "execute @p[x={0},y={1},z={2},r=1,rxm={3},rx={4},rym={5},ry={6},score_PaintWhite_min=1] ~ ~ ~ fill {7} {8} {9} {10} {11} {12} wool 0".format(tx, ty, tz, rxm, rx, rym, ry, (x*4)+box.minx,box.miny,(z*4)+box.minz+1,(x*4)+3+box.minx,box.miny,(z*4)+3+box.minz+1))


def addCommandBlock(level, x, y, z, command):
    chunk = level.getChunk(x/16, z/16)
    te = level.tileEntityAt(x, y, z)
    if te != None:
        chunk.TileEntities.remove(te)
    control = TAG_Compound()
    control["Command"] = TAG_String(command)
    control["id"] = TAG_String(u'Control')
    control["CustomName"] = TAG_String(u'@')
    control["x"] = TAG_Int(x)
    control["y"] = TAG_Int(y)
    control["z"] = TAG_Int(z)
    chunk.TileEntities.append(control)
    chunk.dirty = True
    level.setBlockAt(x, y, z, 137)
    level.setBlockDataAt(x, y, z, 0)
    chunk.dirty = True
