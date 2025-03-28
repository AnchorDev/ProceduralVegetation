import glfw
from OpenGL.GL import *
from utils.shader_loader import load_shader

def main():
    if not glfw.init():
        return

    window = glfw.create_window(800, 600, "Procedural Forest", None, None)
    if not window:
        glfw.terminate()
        return

    glfw.make_context_current(window)

    shader_program = load_shader("shaders/vertex_shader.glsl", "shaders/fragment_shader.glsl")
    glUseProgram(shader_program)

    while not glfw.window_should_close(window):
        glClearColor(0.5, 0.7, 1.0, 1.0)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        glfw.swap_buffers(window)
        glfw.poll_events()

    glfw.terminate()

if __name__ == "__main__":
    main()
