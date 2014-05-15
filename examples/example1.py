from rpack import pack, coverage, Rect
import random
import pyglet
from pyglet import gl
from pyglet.window import mouse

def draw_rects(done, colors):
    gl.glBegin(gl.GL_QUADS)
    for rect in done:
        gl.glColor3f(*colors[rect.rel])
        gl.glVertex2f(rect.x, rect.y)
        gl.glVertex2f(rect.x+rect.width, rect.y)
        gl.glVertex2f(rect.x+rect.width, rect.y+rect.height)
        gl.glVertex2f(rect.x, rect.y+rect.height)
    gl.glEnd()

"""
rects = [
    Rect(50, 100, 0),
    Rect(100, 50, 1),
    Rect(32, 32, 2),
    Rect(200, 13, 3),
    Rect(250, 125, 4),
    Rect(13, 17, 5),
    Rect(55, 35, 6),
    Rect(33, 330, 7),
    Rect(29, 23, 8),
    Rect(64, 128, 9),
    Rect(128, 32, 10),
    Rect(96, 96, 11)
]
"""

# 32x32
rcount = 800
rects = [Rect(32, 32, i) for i in range(rcount)]

ocount = 40
from_size = 5
to_size = 300
other = [Rect(
    random.randint(from_size, to_size),
    random.randint(from_size, to_size),
    i
) for i in range(ocount)]
rects.extend(other)

colors = []
for r in rects:
    colors.append((
        random.uniform(0.1, 1),
        random.uniform(0.1, 1),
        random.uniform(0.1, 1)
    ))

done = pack(rects)
cover, size = coverage(done)
print cover, size
window = pyglet.window.Window(1400, 800, resizable=True)

delta_x = 0
delta_y = 0

@window.event
def on_draw():
    window.clear()
    gl.glLoadIdentity()
    gl.glTranslatef(delta_x, delta_y, 0)
    gl.glScalef(0.5, 0.5, 1.0)
    draw_rects(done, colors)

@window.event
def on_mouse_drag(x, y, dx, dy, button, modifiers):
    if button == mouse.LEFT:
        global delta_x
        global delta_y
        delta_x += dx
        delta_y += dy

pyglet.app.run()
