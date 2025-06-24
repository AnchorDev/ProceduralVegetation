import numpy as np
import ctypes
import random
from OpenGL.GL import *

def normalize(v):
    norm = np.linalg.norm(v)
    return v / norm if norm > 0 else v

def compute_normal(v0, v1, v2):
    a = np.array(v1) - np.array(v0)
    b = np.array(v2) - np.array(v0)
    normal = np.cross(a, b)
    return normalize(normal)

def create_triangle(v0, v1, v2, color):
    normal = compute_normal(v0, v1, v2)
    return [
        *v0, *normal, *color,
        *v1, *normal, *color,
        *v2, *normal, *color,
    ]

def create_cone_tree():
    trunk_height = random.uniform(0.3, 0.5)
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
        y0 = 0
        y1 = trunk_height
        color = [0.55, 0.27, 0.07]

        # 2 trójkąty boków
        vertices += create_triangle([x0, y0, z0], [x1, y0, z1], [x0, y1, z0], color)
        vertices += create_triangle([x1, y0, z1], [x1, y1, z1], [x0, y1, z0], color)

    # === STOŻKI ===
    base_y = trunk_height
    lower_radius = crown_radius * 1.2
    lower_height = crown_height * 0.5
    upper_radius = crown_radius
    upper_height = crown_height * 0.6
    overlap = lower_height * 0.4

    # Dolny stożek
    for i in range(segments):
        a = 2 * np.pi * i / segments
        b = 2 * np.pi * (i + 1) / segments
        x0, z0 = np.cos(a) * lower_radius, np.sin(a) * lower_radius
        x1, z1 = np.cos(b) * lower_radius, np.sin(b) * lower_radius
        y_base = base_y
        y_tip = base_y + lower_height
        color = [0.1, 0.6, 0.1]
        vertices += create_triangle([x0, y_base, z0], [x1, y_base, z1], [0, y_tip, 0], color)

    # Górny stożek
    upper_base = base_y + lower_height - overlap
    for i in range(segments):
        a = 2 * np.pi * i / segments
        b = 2 * np.pi * (i + 1) / segments
        x0, z0 = np.cos(a) * upper_radius, np.sin(a) * upper_radius
        x1, z1 = np.cos(b) * upper_radius, np.sin(b) * upper_radius
        y_base = upper_base
        y_tip = upper_base + upper_height
        color = [0.1, 0.6, 0.1]
        vertices += create_triangle([x0, y_base, z0], [x1, y_base, z1], [0, y_tip, 0], color)

    vertices = np.array(vertices, dtype=np.float32)
    return prepare_tree_vao(vertices), len(vertices) // 9, upper_base + upper_height

def create_sphere_tree():
    trunk_h = random.uniform(0.6, 1.5)
    trunk_r = random.uniform(0.05, 0.15)
    segments = random.randint(6, 12)
    vertices = []

    # PIEŃ
    for i in range(segments):
        θ = 2 * np.pi * i / segments
        θn = 2 * np.pi * (i + 1) / segments
        x0, z0 = np.cos(θ) * trunk_r, np.sin(θ) * trunk_r
        x1, z1 = np.cos(θn) * trunk_r, np.sin(θn) * trunk_r
        color = [0.55, 0.27, 0.07]
        vertices += create_triangle([x0, 0, z0], [x1, 0, z1], [x0, trunk_h, z0], color)
        vertices += create_triangle([x1, 0, z1], [x1, trunk_h, z1], [x0, trunk_h, z0], color)

    # KORONA
    blobs = random.randint(4, 8)
    for _ in range(blobs):
        r_blob = random.uniform(0.2, 0.4)
        off_x, off_y, off_z = [random.uniform(-0.2, 0.2), random.uniform(0.0, 0.4), random.uniform(-0.2, 0.2)]
        rings, segs = 6, 8
        for i in range(rings):
            φ1 = np.pi * i / rings
            φ2 = np.pi * (i + 1) / rings
            for j in range(segs):
                θ1 = 2 * np.pi * j / segs
                θ2 = 2 * np.pi * (j + 1) / segs
                p1 = spherical(r_blob, φ1, θ1)
                p2 = spherical(r_blob, φ1, θ2)
                p3 = spherical(r_blob, φ2, θ2)
                p4 = spherical(r_blob, φ2, θ1)
                color = [0.1, 0.6 + random.uniform(0, 0.4), 0.1]
                for tri in ((p1, p2, p3), (p1, p3, p4)):
                    tri_trans = [[v[0] + off_x, v[1] + trunk_h + off_y, v[2] + off_z] for v in tri]
                    vertices += create_triangle(*tri_trans, color)

    vertices = np.array(vertices, dtype=np.float32)
    return prepare_tree_vao(vertices), len(vertices) // 9, trunk_h + 0.8

def spherical(r, phi, theta):
    return [
        r * np.sin(phi) * np.cos(theta),
        r * np.cos(phi),
        r * np.sin(phi) * np.sin(theta)
    ]

def create_palm_tree():
    trunk_height = random.uniform(2.5, 4.0)
    trunk_radius = random.uniform(0.05, 0.08)
    segments = 10
    vertices = []

    # PIEŃ
    for i in range(segments):
        θ = 2 * np.pi * i / segments
        θn = 2 * np.pi * (i + 1) / segments
        x0, z0 = np.cos(θ) * trunk_radius, np.sin(θ) * trunk_radius
        x1, z1 = np.cos(θn) * trunk_radius, np.sin(θn) * trunk_radius
        color = [0.6, 0.4, 0.2]
        vertices += create_triangle([x0, 0, z0], [x1, 0, z1], [x0, trunk_height, z0], color)
        vertices += create_triangle([x1, 0, z1], [x1, trunk_height, z1], [x0, trunk_height, z0], color)

    # LIŚCIE
    top = trunk_height
    for i in range(6):
        angle = 2 * np.pi * i / 6
        add_palm_leaf(vertices, top, angle)

    vertices = np.array(vertices, dtype=np.float32)
    return prepare_tree_vao(vertices), len(vertices) // 9, trunk_height + 0.5

def add_palm_leaf(vertices, top_y, angle):
    segments = 10
    length = random.uniform(1.0, 2.0)
    max_width = 0.3
    color = [0.1, 0.6, 0.1]

    dir = np.array([np.cos(angle), 0, np.sin(angle)])
    up = np.array([0, 1, 0])
    side = np.cross(dir, up)

    for i in range(segments):
        t1 = i / segments
        t2 = (i + 1) / segments
        w1 = max_width * (1 - t1)
        w2 = max_width * (1 - t2)
        p1 = dir * (length * t1)
        p2 = dir * (length * t2)
        y1 = top_y - t1 * 0.5
        y2 = top_y - t2 * 0.5
        c1 = np.array([p1[0], y1, p1[2]])
        c2 = np.array([p2[0], y2, p2[2]])
        l1 = c1 + side * w1
        l2 = c2 + side * w2
        r1 = c1 - side * w1
        r2 = c2 - side * w2
        vertices += create_triangle(l1, l2, r2, color)
        vertices += create_triangle(l1, r2, r1, color)

def prepare_tree_vao(vertices):
    VAO = glGenVertexArrays(1)
    VBO = glGenBuffers(1)
    glBindVertexArray(VAO)
    glBindBuffer(GL_ARRAY_BUFFER, VBO)
    glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_STATIC_DRAW)

    stride = 9 * 4
    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(0))
    glEnableVertexAttribArray(0)
    glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(3 * 4))
    glEnableVertexAttribArray(1)
    glVertexAttribPointer(2, 3, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(6 * 4))
    glEnableVertexAttribArray(2)

    glBindBuffer(GL_ARRAY_BUFFER, 0)
    glBindVertexArray(0)
    return VAO
