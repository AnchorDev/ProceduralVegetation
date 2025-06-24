import glfw
import numpy as np
import random
import time
import ctypes
from math import sin, cos, pi
from OpenGL.GL import *
from pyrr import Matrix44, Vector3

from utils.shader_loader import load_shader
from utils.camera import Camera
from objects.tree import create_cone_tree, create_sphere_tree, create_palm_tree
from objects.ground import create_ground

# Myszka
last_x, last_y = 400, 300
first_mouse = True

def main():
    global last_x, last_y, first_mouse

    # Inicjalizacja GLFW
    if not glfw.init():
        return
    window = glfw.create_window(800, 600, "Procedural Forest", None, None)
    if not window:
        glfw.terminate()
        return
    glfw.make_context_current(window)
    glfw.set_input_mode(window, glfw.CURSOR, glfw.CURSOR_DISABLED)

    # Kamera
    camera = Camera()
    last_frame_time = time.time()

    glfw.set_cursor_pos_callback(window, lambda w, x, y: mouse_callback(camera, x, y))

    glEnable(GL_DEPTH_TEST)

    # Shadery i światło
    shader_program = load_shader("shaders/vertex_shader.glsl", "shaders/fragment_shader.glsl")
    glUseProgram(shader_program)

    light_dir = Vector3([1.0, -1.0, -0.3])
    light_color = Vector3([1.0, 1.0, 0.9])

    glUniform3fv(glGetUniformLocation(shader_program, "lightDir"), 1, light_dir)
    glUniform3fv(glGetUniformLocation(shader_program, "lightColor"), 1, light_color)

    model_loc = glGetUniformLocation(shader_program, "model")
    view_loc  = glGetUniformLocation(shader_program, "view")
    proj_loc  = glGetUniformLocation(shader_program, "projection")

    projection = Matrix44.perspective_projection(45.0, 800 / 600, 0.1, 100.0)
    glUniformMatrix4fv(proj_loc, 1, GL_FALSE, projection.astype('float32'))

    # Obiekty
    ground_vao, ground_count = create_ground()
    sun_vao, sun_count = create_sun()

    # Drzewa
    trees = []
    for _ in range(500):
        r = random.random()
        if r < 0.33:
            vao, count, height = create_cone_tree()
        elif r < 0.66:
            vao, count, height = create_sphere_tree()
        else:
            vao, count, height = create_palm_tree()
        x = random.uniform(-20, 20)
        z = random.uniform(-20, 20)
        trees.append((vao, count, height, x, z))

    # Pętla główna
    while not glfw.window_should_close(window):
        now = time.time()
        delta = now - last_frame_time
        last_frame_time = now

        process_input(window, camera, delta)

        view = camera.get_view_matrix()
        glUniformMatrix4fv(view_loc, 1, GL_FALSE, view.astype('float32'))

        glClearColor(0.5, 0.7, 1.0, 1.0)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        # Rysuj ziemię
        glUniformMatrix4fv(model_loc, 1, GL_FALSE, Matrix44.identity().astype('float32'))
        glBindVertexArray(ground_vao)
        glDrawArrays(GL_TRIANGLES, 0, ground_count)

        # Rysuj słońce
        sun_distance = 50.0
        sun_pos = -light_dir.normalized * sun_distance
        sun_model = Matrix44.from_translation(sun_pos)
        glUniformMatrix4fv(model_loc, 1, GL_FALSE, sun_model.astype('float32'))
        glBindVertexArray(sun_vao)
        glDrawArrays(GL_TRIANGLES, 0, sun_count)

        # Rysuj drzewa
        for vao, count, height, x, z in trees:
            m = Matrix44.from_translation([x, 0.0, z])
            glUniformMatrix4fv(model_loc, 1, GL_FALSE, m.astype('float32'))
            glBindVertexArray(vao)
            glDrawArrays(GL_TRIANGLES, 0, count)

        glfw.swap_buffers(window)
        glfw.poll_events()

    glfw.terminate()


def process_input(window, camera, delta_time):
    if glfw.get_key(window, glfw.KEY_ESCAPE) == glfw.PRESS:
        glfw.set_window_should_close(window, True)
    if glfw.get_key(window, glfw.KEY_W) == glfw.PRESS:
        camera.process_keyboard("FORWARD", delta_time)
    if glfw.get_key(window, glfw.KEY_S) == glfw.PRESS:
        camera.process_keyboard("BACKWARD", delta_time)
    if glfw.get_key(window, glfw.KEY_A) == glfw.PRESS:
        camera.process_keyboard("LEFT", delta_time)
    if glfw.get_key(window, glfw.KEY_D) == glfw.PRESS:
        camera.process_keyboard("RIGHT", delta_time)


def mouse_callback(camera, xpos, ypos):
    global last_x, last_y, first_mouse
    if first_mouse:
        last_x, last_y = xpos, ypos
        first_mouse = False

    xoffset = xpos - last_x
    yoffset = last_y - ypos
    last_x = xpos
    last_y = ypos

    camera.process_mouse_movement(xoffset, yoffset)


def create_sun():

    latitude_bands = 20
    longitude_bands = 20
    radius = 2.0  # większy promień

    vertices = []

    for lat in range(latitude_bands):
        theta1 = lat * pi / latitude_bands
        theta2 = (lat + 1) * pi / latitude_bands

        for lon in range(longitude_bands):
            phi1 = lon * 2 * pi / longitude_bands
            phi2 = (lon + 1) * 2 * pi / longitude_bands

            # 4 wierzchołki segmentu
            x1 = sin(theta1) * cos(phi1)
            y1 = cos(theta1)
            z1 = sin(theta1) * sin(phi1)

            x2 = sin(theta2) * cos(phi1)
            y2 = cos(theta2)
            z2 = sin(theta2) * sin(phi1)

            x3 = sin(theta2) * cos(phi2)
            y3 = cos(theta2)
            z3 = sin(theta2) * sin(phi2)

            x4 = sin(theta1) * cos(phi2)
            y4 = cos(theta1)
            z4 = sin(theta1) * sin(phi2)

            p1 = (x1, y1, z1)
            p2 = (x2, y2, z2)
            p3 = (x3, y3, z3)
            p4 = (x4, y4, z4)

            for tri in [(p1, p2, p3), (p1, p3, p4)]:
                for vx in tri:
                    nx, ny, nz = vx
                    color = (1.0, 1.0, 0.0)
                    vertices += [vx[0] * radius, vx[1] * radius, vx[2] * radius,
                                 nx, ny, nz,
                                 *color]

    vertices = np.array(vertices, dtype=np.float32)

    vao = glGenVertexArrays(1)
    vbo = glGenBuffers(1)

    glBindVertexArray(vao)
    glBindBuffer(GL_ARRAY_BUFFER, vbo)
    glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_STATIC_DRAW)

    stride = 9 * 4
    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(0))         # position
    glEnableVertexAttribArray(0)

    glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(3 * 4))     # normal
    glEnableVertexAttribArray(1)

    glVertexAttribPointer(2, 3, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(6 * 4))     # color
    glEnableVertexAttribArray(2)

    glBindBuffer(GL_ARRAY_BUFFER, 0)
    glBindVertexArray(0)

    return vao, len(vertices) // 9



if __name__ == "__main__":
    main()
