import glfw
from OpenGL.GL import *
from utils.shader_loader import load_shader
from objects.tree import create_tree
from objects.ground import create_ground
from utils.camera import Camera
from pyrr import Matrix44
import numpy as np
import random
import time

# Myszka
last_x, last_y = 400, 300
first_mouse = True

def main():
    global last_x, last_y, first_mouse

    if not glfw.init():
        return

    window = glfw.create_window(800, 600, "Procedural Forest", None, None)
    if not window:
        glfw.terminate()
        return

    glfw.make_context_current(window)

    # Ukrycie i zablokowanie kursora
    glfw.set_input_mode(window, glfw.CURSOR, glfw.CURSOR_DISABLED)

    # Obsługa myszki
    glfw.set_cursor_pos_callback(window, lambda win, xpos, ypos: mouse_callback(camera, xpos, ypos))

    camera = Camera()
    last_frame_time = time.time()

    glEnable(GL_DEPTH_TEST)

    shader_program = load_shader("shaders/vertex_shader.glsl", "shaders/fragment_shader.glsl")
    glUseProgram(shader_program)

    model_loc = glGetUniformLocation(shader_program, "model")
    view_loc = glGetUniformLocation(shader_program, "view")
    proj_loc = glGetUniformLocation(shader_program, "projection")
    yCoord_location = glGetUniformLocation(shader_program, "yCoord")

    projection = Matrix44.perspective_projection(
        fovy=45.0,
        aspect=800 / 600,
        near=0.1,
        far=100.0
    )
    glUniformMatrix4fv(proj_loc, 1, GL_FALSE, projection.astype('float32'))

    # Ziemia
    ground_vao, ground_vertex_count = create_ground()

    # 🌳 Lista losowych drzew
    trees = []
    for _ in range(20):
        vao, count, height = create_tree()
        x, z = random.uniform(-8, 8), random.uniform(-8, 8)
        trees.append((vao, count, height, x, z))

    while not glfw.window_should_close(window):
        current_time = time.time()
        delta_time = current_time - last_frame_time
        last_frame_time = current_time

        process_input(window, camera, delta_time)

        view = camera.get_view_matrix()
        glUniformMatrix4fv(view_loc, 1, GL_FALSE, view.astype('float32'))

        glClearColor(0.5, 0.7, 1.0, 1.0)  # niebo
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        # Rysuj ziemię
        ground_model = Matrix44.identity()
        glUniformMatrix4fv(model_loc, 1, GL_FALSE, ground_model.astype('float32'))
        glBindVertexArray(ground_vao)
        glDrawArrays(GL_TRIANGLES, 0, ground_vertex_count)

        # Rysuj drzewa
        for vao, count, height, x, z in trees:
            tree_model = Matrix44.from_translation([x, 0, z])
            glUniformMatrix4fv(model_loc, 1, GL_FALSE, tree_model.astype('float32'))
            glUniform1f(yCoord_location, height)
            glBindVertexArray(vao)
            glDrawArrays(GL_TRIANGLES, 0, count)

        glfw.swap_buffers(window)
        glfw.poll_events()

    glfw.terminate()

def process_input(window, camera, delta_time):
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
    yoffset = last_y - ypos  # odwrotnie – ekran (0,0) jest w lewym górnym

    last_x = xpos
    last_y = ypos

    camera.process_mouse_movement(xoffset, yoffset)

if __name__ == "__main__":
    main()
