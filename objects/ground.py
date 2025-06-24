import numpy as np
from OpenGL.GL import *
import ctypes

def create_ground():
    size = 30.0
    normal = [0.0, 1.0, 0.0]
    color = [0.3, 0.25, 0.15]

    vertices = []

    positions = [
        [-size, 0.0, -size],
        [ size, 0.0, -size],
        [-size, 0.0,  size],
        [-size, 0.0,  size],
        [ size, 0.0, -size],
        [ size, 0.0,  size],
    ]

    for pos in positions:
        vertices += pos + normal + color

    vertices = np.array(vertices, dtype=np.float32)

    VAO = glGenVertexArrays(1)
    VBO = glGenBuffers(1)

    glBindVertexArray(VAO)
    glBindBuffer(GL_ARRAY_BUFFER, VBO)
    glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_STATIC_DRAW)

    stride = 9 * vertices.itemsize  # 3 pos + 3 norm + 3 col

    # Pozycje
    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(0))
    glEnableVertexAttribArray(0)

    # Normalne
    glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(3 * vertices.itemsize))
    glEnableVertexAttribArray(1)

    # Kolor
    glVertexAttribPointer(2, 3, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(6 * vertices.itemsize))
    glEnableVertexAttribArray(2)

    glBindBuffer(GL_ARRAY_BUFFER, 0)
    glBindVertexArray(0)

    return VAO, 6
