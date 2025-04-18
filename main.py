import glfw
from OpenGL.GL import *
from utils.shader_loader import load_shader
from objects.tree import create_cone_tree, create_sphere_tree
from objects.ground import create_ground
from utils.camera import Camera
from pyrr import Matrix44
import random
import time

# --- Myszka: globalne zmienne ---
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

    # Ukrycie i zablokowanie kursora
    glfw.set_input_mode(window, glfw.CURSOR, glfw.CURSOR_DISABLED)

    # Kamera
    camera = Camera()
    last_frame_time = time.time()

    # Callback myszy
    glfw.set_cursor_pos_callback(window, lambda w, x, y: mouse_callback(camera, x, y))

    glEnable(GL_DEPTH_TEST)

    # Ładujemy shadery
    shader_program = load_shader("shaders/vertex_shader.glsl",
                                 "shaders/fragment_shader.glsl")
    glUseProgram(shader_program)

    # Pobieramy lokalizacje uniformów
    model_loc = glGetUniformLocation(shader_program, "model")
    view_loc  = glGetUniformLocation(shader_program, "view")
    proj_loc  = glGetUniformLocation(shader_program, "projection")

    # Ustawiamy stały projection
    projection = Matrix44.perspective_projection(
        fovy=45.0, aspect=800/600, near=0.1, far=100.0
    )
    glUniformMatrix4fv(proj_loc, 1, GL_FALSE, projection.astype('float32'))

    # Tworzymy ziemię
    ground_vao, ground_count = create_ground()

    # Generujemy 20 drzew losowo stożkowych lub „kulistych”
    trees = []
    for _ in range(30):
        if random.random() < 0.5:
            vao, count, height = create_cone_tree()
        else:
            vao, count, height = create_sphere_tree()
        x = random.uniform(-8, 8)
        z = random.uniform(-8, 8)
        trees.append((vao, count, height, x, z))

    # Główna pętla renderowania
    while not glfw.window_should_close(window):
        now = time.time()
        delta = now - last_frame_time
        last_frame_time = now

        process_input(window, camera, delta)

        # Aktualizujemy widok z kamery
        view = camera.get_view_matrix()
        glUniformMatrix4fv(view_loc, 1, GL_FALSE, view.astype('float32'))

        # Czyszczenie
        glClearColor(0.5, 0.7, 1.0, 1.0)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        # Rysujemy ziemię
        glUniformMatrix4fv(model_loc, 1, GL_FALSE, Matrix44.identity().astype('float32'))
        glBindVertexArray(ground_vao)
        glDrawArrays(GL_TRIANGLES, 0, ground_count)

        # Rysujemy drzewa
        for vao, count, height, x, z in trees:
            m = Matrix44.from_translation([x, 0.0, z])
            glUniformMatrix4fv(model_loc, 1, GL_FALSE, m.astype('float32'))
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
    yoffset = last_y - ypos  # odwrotnie, bo Y rośnie w dół

    last_x = xpos
    last_y = ypos

    camera.process_mouse_movement(xoffset, yoffset)

if __name__ == "__main__":
    main()
