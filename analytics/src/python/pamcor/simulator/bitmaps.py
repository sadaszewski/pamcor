import numpy as np
from pamcor.common.maze import Maze, \
    SOLID, PILL, POWER_PILL, EMPTY, \
    GHOST, PLAYER, BARRIER


TILE_WIDTH = 5
TILE_HEIGHT = 5


_SOLID = \
'\
*****\
*****\
*****\
*****\
*****'

_PILL = \
'\
     \
  *  \
 *** \
  *  \
     '

_POWER_PILL = \
'\
  *  \
 *** \
*****\
 *** \
  *  '

_EMPTY = \
'\
     \
     \
     \
     \
     '

_GHOST = \
'\
 *** \
*****\
* * *\
*****\
* * *'


_GHOST_VULNERABLE = \
'\
 *** \
*   *\
** **\
* * *\
** **'


_PLAYER_RIGHT = \
'\
 ****\
***  \
*    \
***  \
 ****'

_PLAYER_LEFT = \
'\
**** \
  ***\
    *\
  ***\
**** '

_PLAYER_UP = \
'\
*   *\
*   *\
** **\
** **\
 *** '

_PLAYER_DOWN = \
'\
 *** \
** **\
** **\
*   *\
*   *'

_BARRIER = \
'\
     \
     \
*****\
     \
     '

PLAYER_LEFT = 10
PLAYER_RIGHT = 11
PLAYER_UP = 12
PLAYER_DOWN = 13
GHOST_VULNERABLE = 14

BITMAPS = {
    SOLID: _SOLID,
    PILL: _PILL,
    POWER_PILL: _POWER_PILL,
    EMPTY: _EMPTY,
    GHOST: _GHOST,
    PLAYER: _PLAYER_RIGHT,
    BARRIER: _BARRIER,

    PLAYER_UP: _PLAYER_UP,
    PLAYER_DOWN: _PLAYER_DOWN,
    PLAYER_LEFT: _PLAYER_LEFT,
    PLAYER_RIGHT: _PLAYER_RIGHT,
    GHOST_VULNERABLE: _GHOST_VULNERABLE
}

for k in list(BITMAPS.keys()):
    v = list(BITMAPS[k])
    v = list(map(lambda a: a != ' ', v))
    #print(k, np.array(v, dtype='<c'))
    BITMAPS[k] = np.array(v, dtype=np.uint8) \
        .reshape((int(len(v) ** 0.5),) * 2) * 255

#BITMAPS = {k: np.array(v).reshape((int(len(v) ** 0.5),) * 2) \
#    for k, v in BITMAPS.items()}
