import numpy as np
from OpenGL.GL import *
import ctypes

def create_ground():
    size = 10.0
    vertices = np.array([
        # positions           # colors (brown)
        -size, 0.0, -size,     0.3, 0.25, 0.15,
         size, 0.0, -size,     0.3, 0.25, 0.15,
        -size, 0.0,  size,     0.3, 0.25, 0.15,

        -size, 0.0,  size,     0.3, 0.25, 0.15,
         size, 0.0, -size,     0.3, 0.25, 0.15,
         size, 0.0,  size,     0.3, 0.25, 0.15,
    ], dtype=np.float32)

    VAO = glGenVertexArrays(1)
    VBO = glGenBuffers(1)

    glBindVertexArray(VAO)
    glBindBuffer(GL_ARRAY_BUFFER, VBO)
    glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_STATIC_DRAW)

    # Position attribute
    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 6 * vertices.itemsize, ctypes.c_void_p(0))
    glEnableVertexAttribArray(0)

    # Color attribute
    glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 6 * vertices.itemsize, ctypes.c_void_p(3 * vertices.itemsize))
    glEnableVertexAttribArray(1)

    glBindBuffer(GL_ARRAY_BUFFER, 0)
    glBindVertexArray(0)

    return VAO, 6  # 6 vertices (2 triangles)
