import numpy as np
import ctypes
import random
from OpenGL.GL import *

def spherical_to_cartesian(r, phi, theta):
    """Przekształca współrzędne sferyczne na kartezjańskie."""
    x = r * np.sin(phi) * np.cos(theta)
    y = r * np.cos(phi)
    z = r * np.sin(phi) * np.sin(theta)
    return [x, y, z]

def generate_cylinder(radius, height, segments, color):
    """Generuje low‑poly cylinder jako zestaw trójkątów."""
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
    """Generuje low‑poly stożek jako zestaw trójkątów."""
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
    """Drzewo typu cone: cylinder + stożek."""
    # parametry proceduralne
    trunk_h = random.uniform(0.6, 1.5)
    trunk_r = random.uniform(0.05, 0.15)
    crown_h = random.uniform(0.7, 1.5)
    crown_r = random.uniform(0.3, 0.7)
    segs    = random.randint(6, 12)

    # generujemy meshe
    t_verts, t_cols = generate_cylinder(trunk_r, trunk_h, segs, [0.55, 0.27, 0.07])
    c_verts, c_cols = generate_cone(trunk_r + crown_r, crown_h, segs, trunk_h, [0.1, 0.6, 0.1])

    verts = np.array(t_verts + c_verts, dtype=np.float32)
    cols  = np.array(t_cols  + c_cols,  dtype=np.float32)

    # upload do GPU
    VAO = glGenVertexArrays(1)
    VBO = glGenBuffers(1)
    glBindVertexArray(VAO)
    glBindBuffer(GL_ARRAY_BUFFER, VBO)
    # pozycje + kolory w jednym VBO
    data = np.hstack([verts.reshape(-1,3), cols.reshape(-1,3)]).astype(np.float32)
    glBufferData(GL_ARRAY_BUFFER, data.nbytes, data, GL_STATIC_DRAW)

    # aPos
    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 6 * 4, ctypes.c_void_p(0))
    glEnableVertexAttribArray(0)
    # aColor
    glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 6 * 4, ctypes.c_void_p(3 * 4))
    glEnableVertexAttribArray(1)

    glBindBuffer(GL_ARRAY_BUFFER, 0)
    glBindVertexArray(0)
    return VAO, len(verts) // 3, trunk_h

def create_sphere_tree():
    """Drzewo typu sphere: cylinder + kilka małych elipsoid tworzących koronę."""
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

    # KORONA – kilka "kulek"
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
    """Domyślnie zwraca drzewo typu stożkowego."""
    return create_cone_tree()
