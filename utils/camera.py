import numpy as np
from pyrr import Vector3, matrix44

class Camera:
    def __init__(self, position=Vector3([0.0, 0.5, 2.0]), yaw=-90.0, pitch=0.0):
        self.position = position
        self.front = Vector3([0.0, 0.0, -1.0])
        self.up = Vector3([0.0, 1.0, 0.0])
        self.right = Vector3([1.0, 0.0, 0.0])

        self.yaw = yaw
        self.pitch = pitch
        self.speed = 2.5
        self.sensitivity = 0.1

        self.update_vectors()

    def get_view_matrix(self):
        return matrix44.create_look_at(self.position, self.position + self.front, self.up)

    def process_keyboard(self, direction, delta_time):
        velocity = self.speed * delta_time
        if direction == "FORWARD":
            self.position += self.front * velocity
        if direction == "BACKWARD":
            self.position -= self.front * velocity
        if direction == "LEFT":
            self.position -= self.right * velocity
        if direction == "RIGHT":
            self.position += self.right * velocity

    def process_mouse_movement(self, xoffset, yoffset):
        xoffset *= self.sensitivity
        yoffset *= self.sensitivity

        self.yaw += xoffset
        self.pitch += yoffset

        if self.pitch > 89.0:
            self.pitch = 89.0
        if self.pitch < -89.0:
            self.pitch = -89.0

        self.update_vectors()

    def update_vectors(self):
        front = Vector3([
            np.cos(np.radians(self.yaw)) * np.cos(np.radians(self.pitch)),
            np.sin(np.radians(self.pitch)),
            np.sin(np.radians(self.yaw)) * np.cos(np.radians(self.pitch))
        ])
        self.front = front.normalized
        self.right = Vector3(np.cross(self.front, Vector3([0.0, 1.0, 0.0]))).normalized
        self.up = Vector3(np.cross(self.right, self.front)).normalized
