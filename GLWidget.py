import OpenGL.GL as GL
from OpenGL import GLU
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QOpenGLWidget
from PyQt5.QtGui import QPainter, QColor
from PyQt5.QtCore import Qt
from URDF_load import URDF_load
from urdfpy import Geometry
import numpy as np



class GLWidget(QOpenGLWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.rotX: float = 0.0
        self.rotY: float = 0.0
        self.rotZ: float = 0.0
        self.quad: GLU = GLU.gluNewQuadric()
        self.rocket = URDF_load("Rocket_URDF/Rocket_URDF/urdf/Rocket_URDF.urdf")
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_OpaquePaintEvent, False)
        self.setAutoFillBackground(False)


    def initializeGL(self):
        GL.glClearColor(0.12,0.12,0.12,0.0)
        GL.glEnable(GL.GL_DEPTH_TEST)


    def setRotX(self, val: float) -> None:
        self.rotX = val
        self.update()

    def setRotY(self, val: float) -> None:
        self.rotY = val
        self.update()

    def setRotZ(self, val: float) -> None:
        self.rotZ = val
        self.update()

    def resizeGL(self, height: int, width: int) -> None:
        GL.glViewport(0, 0, width, height)
        GL.glMatrixMode(GL.GL_PROJECTION)

        GL.glLoadIdentity()
        aspect_ratio: float = width / float(height)

        GLU.gluPerspective(45.0, aspect_ratio, 1.0, 100.0)
        GL.glMatrixMode(GL.GL_MODELVIEW)

    def paintGL(self) -> None:


        GL.glPushMatrix()

        GL.glTranslate(0.0, 0.0, -80.0)
        GL.glScale(20.0, 20.0, 0.0)
        GL.glRotate(self.rotX, 1.0, 0.0, 0.0)
        GL.glRotate(self.rotY, 0.0, 1.0, 0.0)
        GL.glRotate(self.rotZ, 0.0, 0.0, 1.0)

        GL.glTranslate(0.0, 0.0, -0.5)

        # GLU.gluCylinder(self.quad, 0.5, 0.5, 1, 32, 32)  # quad base(rad) top(rad) height slices
        # Stacks
        self.draw_urdf_file()
        # draw coordinate axis

        self.draw_axis()

        # FINALLY WE pop the current matrix from the model-view stack
        GL.glPopMatrix()

    def draw_urdf_file(self) -> None:
        # LINK OF THE URDF FILE (rigid obj)
        for link in self.rocket.rocket.links:
            # visual of the urdf
            for visual in link.visuals:
                self.draw_rocket(visual.geometry)

    @staticmethod
    def draw_rocket(rocket: Geometry) -> None:
        # our mesh is the .stl which are in a list
        for mesh in rocket.meshes:
            vertices = np.array(mesh.vertices, dtype=np.float32)
            # faces are 2D format arrays so we need to flatten it so opengl can process it
            faces = np.array(mesh.faces.flatten(), dtype=np.int32)
            vertex_color = np.array(mesh.visual.vertex_colors, dtype=np.float32)
            # so this is just to translate the rocket to the origin pt
            translation_vector = np.array([0.0, 0.0, 0.5], dtype=np.float32)
            vertices = vertices + translation_vector
            # THIS IS OUR MESH OF OUR URDF aka our .stl file to draw the rocket
            # this is how we draw the urdf

            GL.glEnableClientState(GL.GL_VERTEX_ARRAY)
            GL.glEnableClientState(GL.GL_COLOR_ARRAY)
            GL.glVertexPointer(3, GL.GL_FLOAT, 0, vertices)
            GL.glColorPointer(3, GL.GL_FLOAT, 0, vertex_color)
            GL.glDrawElements(GL.GL_TRIANGLES, len(faces), GL.GL_UNSIGNED_INT, faces)
            GL.glDisableClientState(GL.GL_VERTEX_ARRAY)
            GL.glDisableClientState(GL.GL_COLOR_ARRAY)

    @staticmethod
    def draw_axis() -> None:
        GL.glLineWidth(2.0)
        GL.glBegin(GL.GL_LINES)
        # this is our x-axis
        GL.glColor3f(1.0, 0.0, 0.0)
        GL.glVertex3f(0.0, 0.0, 0.5)
        GL.glVertex3f(2.0, 0.0, 0.5)

        # this is our y
        GL.glColor3f(0.0, 1.0, 0.0)
        GL.glVertex3f(0.0, 0.0, 0.5)
        GL.glVertex3f(0.0, 3.0, 0.5)

        # and finally z
        GL.glColor3f(0.0, 0.0, 1.0)
        GL.glVertex3f(0.0, 0.0, 0.5)
        GL.glVertex3f(0.0, 0.0, 2.0)

        GL.glEnd()
