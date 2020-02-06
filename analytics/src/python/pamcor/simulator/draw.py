from .bitmaps import BITMAPS, PLAYER_LEFT, \
    PLAYER_RIGHT, PLAYER_UP, PLAYER_DOWN, \
    GHOST, GHOST_VULNERABLE
import numpy as np
from PIL import Image
from pamcor.common.maze import SOLID, \
    GHOST, PLAYER
from scipy.ndimage import gaussian_filter


def draw_maze(maze):
    mw = maze.width()
    mh = maze.height()
    data = maze.get_data()
    th, tw = BITMAPS[SOLID].shape
    im = np.zeros((mh * th, mw * tw), dtype=np.uint8)

    for y, row in enumerate(data):
        for x, cell_type in enumerate(row):
            if cell_type in {GHOST, PLAYER}:
                continue
            im[(y * th):((y + 1) * th),
                (x * tw):((x + 1) * tw)] = \
                BITMAPS[cell_type]

    return im


def blit(tgt_im, src_im, x, y):
    sh, sw = src_im.shape
    th, tw = tgt_im.shape

    x_0, x_1 = 0, sw
    y_0, y_1 = 0, sh

    if x + sw >= tw:
        x_1 = tw - x
    elif x < 0:
        x_0 = -x
        x = 0

    if y + sh > th:
        y_1 = th - y
    elif y < 0:
        y_0 = -y
        y = 0

    sw = x_1 - x_0
    sh = y_1 - y_0

    if sw <= 0 or sh <= 0:
        return

    tgt_im[y:(y + sh), x:(x + sw)] |= \
        src_im[y_0:y_1, x_0:x_1]


def draw_player(sim_state, im):
    maze = sim_state.maze
    th, tw = BITMAPS[SOLID].shape
    e = sim_state.player
    x = np.round(e.pos[0] * tw).astype(np.int)
    y = np.round(e.pos[1] * th).astype(np.int)

    move_dir = tuple(e.last_move_dir) \
        if e.last_move_dir is not None \
        else None
    if move_dir == (0, -1):
        src_im = BITMAPS[PLAYER_UP]
    elif move_dir == (0, 1):
        src_im = BITMAPS[PLAYER_DOWN]
    elif move_dir == (-1, 0):
        src_im = BITMAPS[PLAYER_LEFT]
    else:
        src_im = BITMAPS[PLAYER_RIGHT]

    blit(im, src_im, x, y)


def draw_ghosts(sim_state, im):
    maze = sim_state.maze
    th, tw = BITMAPS[SOLID].shape
    for e in sim_state.ghosts:
        src_im = BITMAPS[GHOST_VULNERABLE] \
            if sim_state.power_pill_active \
            else BITMAPS[GHOST]
        x = np.round(e.pos[0] * tw).astype(np.int)
        y = np.round(e.pos[1] * th).astype(np.int)
        blit(im, src_im, x, y)


def draw_entities(sim_state, im):
    draw_ghosts(sim_state, im)
    draw_player(sim_state, im)


def draw_state(sim_state, width, height):
    im = draw_maze(sim_state.maze)

    draw_entities(sim_state, im)

    # im = gaussian_filter(im, [11, 0])
    # im = gaussian_filter(im, [0, 11])

    pil_im = Image.fromarray(im)
    pil_im = pil_im.resize((width, height), resample=Image.NEAREST)
    im = np.array(pil_im)

    return im, pil_im
