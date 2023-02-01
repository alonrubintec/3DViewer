import numpy
import moderngl
import math

from PyQt5 import QtOpenGL, QtCore
from arcball import ArcBallUtil
from pyrr import Matrix44
from resource import shaders


def grid(size, steps):
    # Create grid parameters
    u = numpy.repeat(numpy.linspace(-size, size, steps), 2)
    v = numpy.tile([-size, size], steps)
    w = numpy.zeros(steps * 2)
    new_grid = numpy.concatenate([numpy.dstack([u, v, w]), numpy.dstack([v, u, w])])

    # Rotate grid
    lower_grid = 0.135
    rotation_matrix = numpy.array([
        [0, 0, 1],
        [1, 0, 0],
        [0, lower_grid, 0]
    ])
    return numpy.dot(new_grid, rotation_matrix)


class QGLControllerWidget(QtOpenGL.QGLWidget):
    def __init__(self, parent=None):
        self.parent = parent
        super(QGLControllerWidget, self).__init__(parent)

        # Initialize OpenGL parameters
        self.bg_color = (0.1, 0.1, 0.1, 0.1)
        self.color_alpha = 1.0
        self.new_color = (1.0, 1.0, 1.0, self.color_alpha)
        self.fov = 60.0
        self.camera_zoom = 2.0
        self.setMouseTracking(True)
        self.wheelEvent = self.update_zoom
        self.is_wireframe = False
        self.texture = None
        self.cell = 50
        self.size = 20
        self.grid = grid(self.size, self.cell)
        self.grid_alpha_value = 1.0

    def initializeGL(self):
        # Create a new OpenGL context
        self.ctx = moderngl.create_context()

        # Create the shader program
        self.prog = self.ctx.program(
            vertex_shader=shaders.vertex_shader,
            fragment_shader=shaders.fragment_shader
        )
        self.set_scene()

    def set_scene(self):
        # Setting shader parameters
        self.light = self.prog['Light']
        self.color = self.prog['Color']
        self.mvp = self.prog['Mvp']
        self.prog["Texture"].value = 0
        self.light.value = (1.0, 1.0, 1.0)
        self.color.value = (1.0, 1.0, 1.0, 1.0)

        # Setting mesh parameters
        self.mesh = None
        self.vbo = self.ctx.buffer(self.grid.astype('f4'))
        self.vao2 = self.ctx.simple_vertex_array(self.prog, self.vbo, 'in_position')

        # Setting ArcBall parameters
        self.arc_ball = ArcBallUtil(self.width(), self.height())
        self.center = numpy.zeros(3)
        self.scale = 1.0

    def paintGL(self):
        # OpenGL loop
        self.ctx.clear(*self.bg_color)
        self.ctx.enable(moderngl.BLEND)
        self.ctx.enable(moderngl.DEPTH_TEST | moderngl.CULL_FACE)
        self.ctx.wireframe = self.is_wireframe
        if self.mesh is None:
            return

        # Update projection matrix loop
        self.aspect_ratio = self.width() / max(1.0, self.height())
        proj = Matrix44.perspective_projection(self.fov, self.aspect_ratio, 0.1, 1000.0)
        lookat = Matrix44.look_at(
            (0.0, 0.0, self.camera_zoom),
            (0.0, 0.0, 0.0),
            (0.0, 1.0, 0.0),
        )
        self.arc_ball.Transform[3, :3] = -self.arc_ball.Transform[:3, :3].T @ self.center
        self.mvp.write((proj * lookat * self.arc_ball.Transform).astype('f4'))

        # Render mesh loop
        self.color.value = self.new_color
        self.vao.render()

        # Render grid loop
        self.color.value = (1.0, 1.0, 1.0, self.grid_alpha_value)
        self.vao2.render(moderngl.LINES)
        self.color.value = self.new_color

    def set_mesh(self, new_mesh):
        if new_mesh is None:
            self.set_scene()
            return
        self.mesh = new_mesh
        self.mesh.update_normals()

        # Creates an index buffer
        index_buffer = self.ctx.buffer(numpy.array(self.mesh.face_vertex_indices(), dtype="u4").tobytes())

        # Creates a list of vertex buffer objects (VBOs)
        vao_content = [(self.ctx.buffer(numpy.array(self.mesh.points(), dtype="f4").tobytes()), '3f', 'in_position'),
                       (self.ctx.buffer(numpy.array(self.mesh.vertex_normals(), dtype="f4").tobytes()), '3f', 'in_normal')]
        self.vao = self.ctx.vertex_array(self.prog, vao_content, index_buffer, 4)
        self.init_arcball()

    def init_arcball(self):
        # Create ArcBall
        self.arc_ball = ArcBallUtil(self.width(), self.height())
        mesh_points = self.mesh.points()
        bounding_box_min = numpy.min(mesh_points, axis=0)
        bounding_box_max = numpy.max(mesh_points, axis=0)
        self.center = 0.5*(bounding_box_max+bounding_box_min)
        self.scale = numpy.linalg.norm(bounding_box_max-self.center)
        self.arc_ball.Transform[:3, :3] /= self.scale
        self.arc_ball.Transform[3, :3] = -self.center/self.scale

    # -------------- GUI interface --------------
    def change_light_color(self, color, alpha=1):
        color = color + (alpha,)
        print(color)
        self.color.value = color
        self.new_color = color

    def update_alpha(self, alpha):
        self.color_alpha = (alpha*0.01)
        color_list = list(self.new_color)
        color_list[-1] = self.color_alpha
        self.new_color = tuple(color_list)

    def update_grid_alpha(self, alpha):
        self.grid_alpha_value = (alpha*0.01)

    def background_color(self, color):
        self.bg_color = color

    def update_fov(self, num):
        self.fov = num
        self.camera_zoom = self.camera_distance(num)
        self.update()

    @staticmethod
    def camera_distance(num):
        return 1 / (math.tan(math.radians(num / 2)))

    def update_grid_cell(self, cells):
        self.cell = cells
        self.grid = grid(self.size, self.cell)
        self.update_grid()

    def update_grid_size(self, size):
        self.size = size
        self.grid = grid(self.size, self.cell)
        self.update_grid()

    def update_grid(self):
        self.vbo = self.ctx.buffer(self.grid.astype('f4'))
        self.vao2 = self.ctx.simple_vertex_array(self.prog, self.vbo, 'in_position')

    def resizeGL(self, width, height):
        width = max(2, width)
        height = max(2, height)
        self.ctx.viewport = (0, 0, width, height)
        self.arc_ball.setBounds(width, height)
        return

    def make_wireframe(self):
        self.is_wireframe = True

    def make_solid(self):
        self.is_wireframe = False

    # Input handling
    def mousePressEvent(self, event):
        if event.buttons() & QtCore.Qt.LeftButton:
            self.arc_ball.onClickLeftDown(event.x(), event.y())
        elif event.buttons() & QtCore.Qt.RightButton:
            self.prev_x = event.x()
            self.prev_y = event.y()

    def mouseReleaseEvent(self, event):
        if event.buttons() & QtCore.Qt.LeftButton:
            self.arc_ball.onClickLeftUp()

    def mouseMoveEvent(self, event):
        if event.buttons() & QtCore.Qt.LeftButton:
            self.arc_ball.onDrag(event.x(), event.y())

    def update_zoom(self, event):
        self.camera_zoom += event.angleDelta().y() * 0.001
        if self.camera_zoom < 0.1:
            self.camera_zoom = 0.1
        self.update()

    def mouseMoveEvent(self, event):
        if event.buttons() & QtCore.Qt.LeftButton:
            self.arc_ball.onDrag(event.x(), event.y())
        elif event.buttons() & QtCore.Qt.RightButton:
            x_movement = event.x() - self.prev_x
            y_movement = event.y() - self.prev_y
            self.center[0] -= x_movement * 0.01
            self.center[1] += y_movement * 0.01
            self.update()
            self.prev_x = event.x()
            self.prev_y = event.y()