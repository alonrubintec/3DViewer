from PyQt5 import QtWidgets, QtCore, uic
from PyQt5.QtGui import QIcon
from OpenGL.GLUT import *
from engine import QGLControllerWidget
import functions as f
import argparse


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        # Load UI file
        QtWidgets.QMainWindow.__init__(self)
        uic.loadUi("%s/resource/3DView02.ui" % os.path.dirname(__file__), self)

        # Create openGL context
        self.openGL = QGLControllerWidget(self)
        self.openGL.setGeometry(0, 37, 870, 731)
        timer = QtCore.QTimer(self)
        timer.setInterval(20)  # refresh speed in milliseconds
        timer.timeout.connect(self.openGL.updateGL)
        timer.start()

        # Load button
        load_icon = QIcon("%s/resource/load.png" % os.path.dirname(__file__))
        self.load_button.setIcon(load_icon)

        self.load_button.clicked.connect(self.load_file)
        self.actionLoad.triggered.connect(self.load_file)

        # Menubar Buttons
        self.actionQuit.triggered.connect(lambda: f.exit_app())
        self.actionClose.triggered.connect(lambda: f.close_file(self.openGL, self.obj_path_label, self.obj_name_label))
        self.actionAbout.triggered.connect(lambda: f.show_message_box())

        # Buttons
        self.wireframe_color.clicked.connect(lambda: f.get_color(self.wireframe_color, f.set_button_color, "wire", self.openGL))
        self.background_color.clicked.connect(lambda: f.get_color(self.background_color, f.set_button_color, "background", self.openGL))

        # Settings Sliders
        self.fov_slider.valueChanged.connect(lambda: f.change_slider(self.fov_slider, self.fov_slider_value, self.openGL, "fov"))
        self.fov_slider_value.textChanged.connect(lambda: f.update_slider(self.fov_slider, self.fov_slider_value))
        self.grid_slider.valueChanged.connect(lambda: f.change_slider(self.grid_slider, self.grid_slider_value, self.openGL, "na"))
        self.grid_slider_value.textChanged.connect(lambda: f.update_slider(self.grid_slider, self.grid_slider_value))

        # Settings Sliders
        self.wireframe_slider.valueChanged.connect(lambda: f.change_slider(self.wireframe_slider, self.wireframe_slider_value, self.openGL, "wireframe"))
        self.wireframe_slider_value.textChanged.connect(lambda: f.update_slider(self.wireframe_slider, self.wireframe_slider_value))

        # Settings radio buttons
        self.wireframe_radio.toggled.connect(lambda: self.openGL.make_wireframe())
        self.solid_radio.toggled.connect(lambda: self.openGL.make_solid())

        # Grid settings
        self.grid_cell.textChanged.connect(lambda: f.update_grid_size(self.grid_cell, self.openGL, "cell"))
        self.grid_size.textChanged.connect(lambda: f.update_grid_size(self.grid_size, self.openGL, "size"))
        self.grid_slider.valueChanged.connect(lambda: f.change_slider(self.grid_slider, self.grid_slider_value, self.openGL, "grid"))
        self.grid_slider_value.textChanged.connect(lambda: f.update_slider(self.grid_slider, self.grid_slider_value))

    def load_file(self, scene=None):
        if isinstance(scene, str):
            f.open_file(scene, self.openGL, self.obj_path_label, self.obj_name_label, self.uv2_label, self.material_label, self.drawcalls_label, self.vertices_label, self.triangles_label, self.edges_label)
        else:
            f.open_file_ask(self.openGL, self.obj_path_label, self.obj_name_label, self.uv2_label, self.material_label, self.drawcalls_label, self.vertices_label, self.triangles_label, self.edges_label)


def get_parser():
    parser = argparse.ArgumentParser(description='3D Viewer', add_help=False)

    parser.add_argument('--version', action='version', version='%(prog)s 1.0')

    parser.add_argument('--scene', type=str, required=False, default=None, help='Scene to open')

    return parser


if __name__ == '__main__':
    args = get_parser().parse_args()

    app = QtWidgets.QApplication(sys.argv)
    win = MainWindow()
    win.show()

    if args.scene is not None:
        if os.path.exists(args.scene):
            QtCore.QCoreApplication.processEvents()
            win.load_file(args.scene)
        else:
            print('File not found: "%s"' % args.scene)

    sys.exit(app.exec_())
