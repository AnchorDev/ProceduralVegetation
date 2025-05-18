import numpy as np
import ctypes
import random
from OpenGL.GL import *

def spherical_to_cartesian(r, phi, theta):
    x = r * np.sin(phi) * np.cos(theta)
    y = r * np.cos(phi)
    z = r * np.sin(phi) * np.sin(theta)
    return [x, y, z]

def generate_cylinder(radius, height, segments, color):
    verts = []
    cols = []
    angle_step = 2 * np.pi / segments
    for i in range(segments):
        θ = i * angle_step
        θn = (i + 1) * angle_step

        # dolna podstawa
        verts += [0, 0, 0,
                  radius * np.cos(θn), 0, radius * np.sin(θn),
                  radius * np.cos(θ),  0, radius * np.sin(θ)]
        cols += color * 3

        # górna podstawa
        verts += [0, height, 0,
                  radius * np.cos(θ), height, radius * np.sin(θ),
                  radius * np.cos(θn), height, radius * np.sin(θn)]
        cols += color * 3

        # boki (2 trójkąty)
        verts += [
            radius * np.cos(θ),  0,          radius * np.sin(θ),
            radius * np.cos(θ),  height,     radius * np.sin(θ),
            radius * np.cos(θn), height,     radius * np.sin(θn),

            radius * np.cos(θ),  0,          radius * np.sin(θ),
            radius * np.cos(θn), height,     radius * np.sin(θn),
            radius * np.cos(θn), 0,          radius * np.sin(θn)
        ]
        cols += color * 6

    return verts, cols

def generate_cone(radius, height, segments, y_offset, color):
    verts = []
    cols = []
    angle_step = 2 * np.pi / segments
    tip = [0.0, y_offset + height, 0.0]
    for i in range(segments):
        θ  = i * angle_step
        θn = (i + 1) * angle_step

        b1 = [radius * np.cos(θ),  y_offset, radius * np.sin(θ)]
        b2 = [radius * np.cos(θn), y_offset, radius * np.sin(θn)]

        verts += b1 + b2 + tip
        cols  += color * 3

    return verts, cols

def create_cone_tree():
    trunk_height = random.uniform(0.3, 0.5)  # niski pień
    trunk_radius = random.uniform(0.05, 0.12)
    crown_height = random.uniform(1.0, 1.6)
    crown_radius = random.uniform(0.5, 0.8)
    segments = random.randint(8, 12)

    vertices = []

    # === PIEŃ ===
    for i in range(segments):
        angle = 2 * np.pi * i / segments
        next_angle = 2 * np.pi * (i + 1) / segments
        x0, z0 = np.cos(angle) * trunk_radius, np.sin(angle) * trunk_radius
        x1, z1 = np.cos(next_angle) * trunk_radius, np.sin(next_angle) * trunk_radius

        # Ściany boczne
        vertices += [x0, 0, z0, 0.55, 0.27, 0.07]
        vertices += [x1, 0, z1, 0.55, 0.27, 0.07]
        vertices += [x0, trunk_height, z0, 0.55, 0.27, 0.07]

        vertices += [x1, 0, z1, 0.55, 0.27, 0.07]
        vertices += [x1, trunk_height, z1, 0.55, 0.27, 0.07]
        vertices += [x0, trunk_height, z0, 0.55, 0.27, 0.07]

    # === DWA STOŻKI ===
    lower_radius = crown_radius * 1.2
    lower_height = crown_height * 0.5
    upper_radius = crown_radius
    upper_height = crown_height * 0.6

    base_y = trunk_height
    overlap = lower_height * 0.4

    # Dolny stożek
    for i in range(segments):
        angle = 2 * np.pi * i / segments
        next_angle = 2 * np.pi * (i + 1) / segments
        x0, z0 = np.cos(angle) * lower_radius, np.sin(angle) * lower_radius
        x1, z1 = np.cos(next_angle) * lower_radius, np.sin(next_angle) * lower_radius

        vertices += [x0, base_y, z0, 0.1, 0.6, 0.1]
        vertices += [x1, base_y, z1, 0.1, 0.6, 0.1]
        vertices += [0, base_y + lower_height, 0, 0.1, 0.6, 0.1]

    # Górny stożek
    upper_base_y = base_y + lower_height - overlap
    for i in range(segments):
        angle = 2 * np.pi * i / segments
        next_angle = 2 * np.pi * (i + 1) / segments
        x0, z0 = np.cos(angle) * upper_radius, np.sin(angle) * upper_radius
        x1, z1 = np.cos(next_angle) * upper_radius, np.sin(next_angle) * upper_radius

        vertices += [x0, upper_base_y, z0, 0.1, 0.6, 0.1]
        vertices += [x1, upper_base_y, z1, 0.1, 0.6, 0.1]
        vertices += [0, upper_base_y + upper_height, 0, 0.1, 0.6, 0.1]

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

    total_height = upper_base_y + upper_height
    return VAO, len(vertices) // 6, total_height

def add_palm_leaf_feathered(vertices, top_y, angle, min_length=1.0, max_length=2.0):
    segment_count = 12
    length = random.uniform(min_length, max_length)
    curve_factor = 1.5
    max_width = 0.4
    feather_size = 0.15

    direction = np.array([np.cos(angle), 0, np.sin(angle)])
    up = np.array([0, 1, 0])
    side = np.cross(direction, up)

    prev_left = None
    prev_right = None

    for i in range(segment_count + 1):
        t = i / segment_count
        segment_length = length * t

        curve_y = top_y - (t ** 2) * curve_factor
        width = max_width * (1 - t)

        center = direction * segment_length
        center = np.array([center[0], curve_y, center[2]])

        left = center + side * width
        right = center - side * width

        # Ząbki
        feather_dir = np.cross(side, direction)
        feather_strength = feather_size * (1 - t)

        feather_left = left + feather_dir * feather_strength
        feather_right = right + feather_dir * feather_strength

        color = [0.1, 0.6, 0.1]

        if i > 0:
            vertices += [
                *prev_left, *color,
                *left, *color,
                *right, *color,

                *prev_left, *color,
                *right, *color,
                *prev_right, *color
            ]

            if t < 0.9:
                vertices += [
                    *left, *color,
                    *feather_left, *color,
                    *prev_left, *color,

                    *right, *color,
                    *feather_right, *color,
                    *prev_right, *color
                ]

        prev_left = left
        prev_right = right



def create_palm_tree():
    trunk_height = random.uniform(2.5, 4.0)
    trunk_radius = random.uniform(0.05, 0.08)
    segments = 10
    vertices = []

    # === PIEŃ ===
    for i in range(segments):
        θ = 2 * np.pi * i / segments
        θn = 2 * np.pi * (i + 1) / segments
        x0, z0 = np.cos(θ) * trunk_radius, np.sin(θ) * trunk_radius
        x1, z1 = np.cos(θn) * trunk_radius, np.sin(θn) * trunk_radius

        # dwa trójkąty na bok
        vertices += [
            x0, 0, z0, 0.6, 0.4, 0.2,
            x1, 0, z1, 0.6, 0.4, 0.2,
            x0, trunk_height, z0, 0.6, 0.4, 0.2,

            x1, 0, z1, 0.6, 0.4, 0.2,
            x1, trunk_height, z1, 0.6, 0.4, 0.2,
            x0, trunk_height, z0, 0.6, 0.4, 0.2,
        ]

    # === LIŚCIE ===
    top = trunk_height

    leaf_count = 6
    for i in range(leaf_count):
        angle = 2 * np.pi * i / leaf_count
        add_palm_leaf_feathered(vertices, top, angle)

    vertices = np.array(vertices, dtype=np.float32)

    VAO = glGenVertexArrays(1)
    VBO = glGenBuffers(1)

    glBindVertexArray(VAO)
    glBindBuffer(GL_ARRAY_BUFFER, VBO)
    glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_STATIC_DRAW)

    #position
    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 6 * 4, ctypes.c_void_p(0))
    glEnableVertexAttribArray(0)

    #color
    glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 6 * 4, ctypes.c_void_p(12))
    glEnableVertexAttribArray(1)

    glBindBuffer(GL_ARRAY_BUFFER, 0)
    glBindVertexArray(0)

    return VAO, len(vertices) // 6, trunk_height




def create_sphere_tree():
    trunk_h = random.uniform(0.6, 1.5)
    trunk_r = random.uniform(0.05, 0.15)
    segs    = random.randint(6, 12)

    vertices = []
    # PIEŃ
    for i in range(segs):
        θ  = 2 * np.pi * i / segs
        θn = 2 * np.pi * (i+1) / segs
        x0, z0 = np.cos(θ)*trunk_r, np.sin(θ)*trunk_r
        x1, z1 = np.cos(θn)*trunk_r,np.sin(θn)*trunk_r
        # dwa trójkąty
        vertices += [x0,0,z0, 0.55,0.27,0.07,
                     x1,0,z1, 0.55,0.27,0.07,
                     x0,trunk_h,z0, 0.55,0.27,0.07]
        vertices += [x1,0,z1, 0.55,0.27,0.07,
                     x1,trunk_h,z1, 0.55,0.27,0.07,
                     x0,trunk_h,z0, 0.55,0.27,0.07]

    # KORONA"
    blobs = random.randint(4, 8)
    for _ in range(blobs):
        r_blob = random.uniform(0.2, 0.4)
        off_x = random.uniform(-0.2, 0.2)
        off_y = random.uniform(0.0, 0.4)
        off_z = random.uniform(-0.2, 0.2)
        rings = 6
        segs_s = 8
        for i in range(rings):
            φ1 = np.pi * i / rings
            φ2 = np.pi * (i+1) / rings
            for j in range(segs_s):
                θ1 = 2*np.pi * j / segs_s
                θ2 = 2*np.pi * (j+1) / segs_s
                p1 = spherical_to_cartesian(r_blob, φ1, θ1)
                p2 = spherical_to_cartesian(r_blob, φ1, θ2)
                p3 = spherical_to_cartesian(r_blob, φ2, θ2)
                p4 = spherical_to_cartesian(r_blob, φ2, θ1)
                for tri in ((p1,p2,p3),(p1,p3,p4)):
                    for px in tri:
                        x, y, z = px[0]+off_x, px[1]+trunk_h+off_y, px[2]+off_z
                        vertices += [x, y, z, 0.1, 0.6 + random.uniform(0.0,0.4), 0.1]

    vertices = np.array(vertices, dtype=np.float32)

    VAO = glGenVertexArrays(1)
    VBO = glGenBuffers(1)
    glBindVertexArray(VAO)
    glBindBuffer(GL_ARRAY_BUFFER, VBO)
    glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_STATIC_DRAW)

    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 6 * 4, ctypes.c_void_p(0))
    glEnableVertexAttribArray(0)
    glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 6 * 4, ctypes.c_void_p(3 * 4))
    glEnableVertexAttribArray(1)

    glBindBuffer(GL_ARRAY_BUFFER, 0)
    glBindVertexArray(0)
    return VAO, len(vertices) // 6, trunk_h

def create_tree():
    return create_cone_tree()
