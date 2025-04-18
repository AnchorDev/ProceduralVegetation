import numpy as np
from OpenGL.GL import *
import ctypes
import random

def generate_cylinder(radius, height, segments, color):
    vertices = []
    colors = []

    angle_step = 2 * np.pi / segments

    for i in range(segments):
        theta = i * angle_step
        next_theta = (i + 1) * angle_step

        # dolna podstawa
        vertices += [
            0.0, 0.0, 0.0,
            radius * np.cos(next_theta), 0.0, radius * np.sin(next_theta),
            radius * np.cos(theta), 0.0, radius * np.sin(theta)
        ]
        colors += color * 3

        # górna podstawa
        vertices += [
            0.0, height, 0.0,
            radius * np.cos(theta), height, radius * np.sin(theta),
            radius * np.cos(next_theta), height, radius * np.sin(next_theta)
        ]
        colors += color * 3

        # bok (dwie ściany)
        vertices += [
            radius * np.cos(theta), 0.0, radius * np.sin(theta),
            radius * np.cos(theta), height, radius * np.sin(theta),
            radius * np.cos(next_theta), height, radius * np.sin(next_theta),

            radius * np.cos(theta), 0.0, radius * np.sin(theta),
            radius * np.cos(next_theta), height, radius * np.sin(next_theta),
            radius * np.cos(next_theta), 0.0, radius * np.sin(next_theta)
        ]
        colors += color * 6

    return vertices, colors

def generate_cone(radius, height, segments, y_offset, color):
    vertices = []
    colors = []

    angle_step = 2 * np.pi / segments
    tip = [0.0, y_offset + height, 0.0]

    for i in range(segments):
        theta = i * angle_step
        next_theta = (i + 1) * angle_step

        base1 = [radius * np.cos(theta), y_offset, radius * np.sin(theta)]
        base2 = [radius * np.cos(next_theta), y_offset, radius * np.sin(next_theta)]

        vertices += base1 + base2 + tip
        colors += color * 3

    return vertices, colors


def create_tree():
    # Losowe parametry drzewa
    trunk_height = random.uniform(0.6, 1.5)
    trunk_radius = random.uniform(0.05, 0.15)
    crown_height = random.uniform(0.7, 1.5)
    crown_radius = random.uniform(0.3, 0.7)
    segments = random.randint(6, 12)

    vertices = []

    # Pień – cylinder (prosty: tylko ściany boczne jako trójkąty)
    for i in range(segments):
        angle = 2 * np.pi * i / segments
        next_angle = 2 * np.pi * (i + 1) / segments

        x0, z0 = np.cos(angle) * trunk_radius, np.sin(angle) * trunk_radius
        x1, z1 = np.cos(next_angle) * trunk_radius, np.sin(next_angle) * trunk_radius

        # Dolna trójkątna ścianka pnia (brązowy)
        vertices += [x0, 0, z0, 0.55, 0.27, 0.07]
        vertices += [x1, 0, z1, 0.55, 0.27, 0.07]
        vertices += [x0, trunk_height, z0, 0.55, 0.27, 0.07]

        # Górna trójkątna ścianka pnia (brązowy)
        vertices += [x1, 0, z1, 0.55, 0.27, 0.07]
        vertices += [x1, trunk_height, z1, 0.55, 0.27, 0.07]
        vertices += [x0, trunk_height, z0, 0.55, 0.27, 0.07]

    # Korona – stożek (zielony)
    for i in range(segments):
        angle = 2 * np.pi * i / segments
        next_angle = 2 * np.pi * (i + 1) / segments

        x0, z0 = np.cos(angle) * crown_radius, np.sin(angle) * crown_radius
        x1, z1 = np.cos(next_angle) * crown_radius, np.sin(next_angle) * crown_radius

        # Trójkąt – ściana stożka
        vertices += [x0, trunk_height, z0, 0.1, 0.6, 0.1]
        vertices += [x1, trunk_height, z1, 0.1, 0.6, 0.1]
        vertices += [0, trunk_height + crown_height, 0, 0.1, 0.6, 0.1]

    vertices = np.array(vertices, dtype=np.float32)

    VAO = glGenVertexArrays(1)
    VBO = glGenBuffers(1)

    glBindVertexArray(VAO)
    glBindBuffer(GL_ARRAY_BUFFER, VBO)
    glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_STATIC_DRAW)

    # Pozycje
    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 6 * vertices.itemsize, ctypes.c_void_p(0))
    glEnableVertexAttribArray(0)

    # Kolory
    glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 6 * vertices.itemsize, ctypes.c_void_p(3 * vertices.itemsize))
    glEnableVertexAttribArray(1)

    glBindBuffer(GL_ARRAY_BUFFER, 0)
    glBindVertexArray(0)

    return VAO, len(vertices) // 6, trunk_height
