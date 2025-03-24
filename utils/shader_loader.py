from OpenGL.GL import *

def load_shader(vertex_path, fragment_path):
    with open(vertex_path, 'r') as f:
        vertex_code = f.read()
    with open(fragment_path, 'r') as f:
        fragment_code = f.read()

    vertex_shader = glCreateShader(GL_VERTEX_SHADER)
    glShaderSource(vertex_shader, vertex_code)
    glCompileShader(vertex_shader)

    if glGetShaderiv(vertex_shader, GL_COMPILE_STATUS) != GL_TRUE:
        print(glGetShaderInfoLog(vertex_shader))

    fragment_shader = glCreateShader(GL_FRAGMENT_SHADER)
    glShaderSource(fragment_shader, fragment_code)
    glCompileShader(fragment_shader)

    if glGetShaderiv(fragment_shader, GL_COMPILE_STATUS) != GL_TRUE:
        print(glGetShaderInfoLog(fragment_shader))

    shader_program = glCreateProgram()
    glAttachShader(shader_program, vertex_shader)
    glAttachShader(shader_program, fragment_shader)
    glLinkProgram(shader_program)

    if glGetProgramiv(shader_program, GL_LINK_STATUS) != GL_TRUE:
        print(glGetProgramInfoLog(shader_program))

    glDeleteShader(vertex_shader)
    glDeleteShader(fragment_shader)

    return shader_program
