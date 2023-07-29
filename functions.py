from PyQt5.QtWidgets import QColorDialog, QMessageBox
from PyQt5 import QtWidgets
from OpenGL.GLUT import *
import openmesh
import re


def open_file_ask(opengl_obj, obj_path, obj_name, uv_label, material_label, drawcalls_label, vertices_label, triangles_label, edges_label):
    file_name = QtWidgets.QFileDialog.getOpenFileName(
        None, 'Open file', '', "Mesh files (*.obj *.stl *.ply *.off *.om)")
    if not file_name[0]:
        return
    open_file(file_name[0], opengl_obj, obj_path, obj_name, uv_label, material_label, drawcalls_label, vertices_label, triangles_label, edges_label)


def open_file(file_name, opengl_obj, obj_path, obj_name, uv_label, material_label, drawcalls_label, vertices_label, triangles_label, edges_label):
    mesh = openmesh.read_trimesh(file_name)
    opengl_obj.set_mesh(mesh)
    set_name(file_name, obj_path, obj_name)
    set_file_info(mesh, vertices_label, triangles_label, edges_label)

    _, file_extension = os.path.splitext(file_name)
    file_format = file_extension.replace(".", "")
    if file_format == "obj":
        has_uv(file_name, uv_label)
        materials(file_name, material_label)
        draw_calls(file_name, drawcalls_label)


def set_name(file_name, obj_path, obj_name):
    file_path = os.path.normpath(file_name)
    ob_name = os.path.basename(file_name)
    obj_path.setText(file_path)
    obj_name.setText(ob_name)


def set_file_info(mesh, vertices_label, triangles_label, edges_label):
    vertex_count = mesh.n_vertices()
    triangle_count = mesh.n_faces()
    edges_count = mesh.n_edges()
    vertices_label.setText(str(vertex_count))
    triangles_label.setText(str(triangle_count))
    edges_label.setText(str(edges_count))


def has_uv(file_path, has_label):
    with open(file_path, "r") as file:
        contents = file.read()
        if "vt" in contents:
            has_label.setText(str("Yes"))
        else:
            has_label.setText(str("No"))


def materials(file_path, material_label):
    with open(file_path, "r") as file:
        contents = file.read()
        num = set(re.findall(r'usemtl (\S+)', contents))
        material_label.setText(str(len(num)))


def draw_calls(file_path, drawcalls_label):
    with open(file_path, "r") as file:
        contents = file.read()
        draw = tuple(re.findall(r'usemtl (\S+)', contents))
        if len(draw) > 1:
            drawcalls_label.setText(str(len(draw)))
        else:
            drawcalls_label.setText(str(1))


def get_color(button, button_color, btn_name, openGL):
    color_dialog = QColorDialog()
    color = color_dialog.getColor()
    if color.isValid():
        r, g, b, a = color.getRgb()
        color = f"rgb({r}, {g}, {b})"
        button_color(button, color)
        if btn_name == "background":
            openGL.background_color((r / 255, g / 255, b / 255))
        if btn_name == "wire":
            openGL.change_light_color((r/255, g/255, b/255))


def set_button_color(button, color):
    button.setStyleSheet(f"background-color: {color};"
                         f"border-radius: 2px"
                         )


def change_slider(slider, line, openGL, btn_name=""):
    value = slider.value()
    line.setText(str(value))
    if btn_name == "fov":
        value = slider.value()
        openGL.update_fov(value)

    if btn_name == "wireframe":
        value = slider.value()
        openGL.update_alpha(value)

    if btn_name == "grid":
        value = slider.value()
        openGL.update_grid_alpha(value)


def update_slider(slider, line):
    value = int(line.text())
    slider.setValue(value)


def update_grid_size(text, openGL, btn_name):
    value = int(text.text())
    if btn_name == "cell":
        openGL.update_grid_cell(value)
    if btn_name == "size":
        openGL.update_grid_size(value)


def close_file(openGL, obj_path, obj_name):
    openGL.set_mesh(None)
    obj_path.setText("")
    obj_name.setText("")


def show_message_box():
    title = "About Qt 3DViewer"
    message = "Qt 3DViewer is a compact tool for \n" \
              "viewing 3D models in a user friendly way\n" \
              "Designed and Developed by Alon Rubin.\n\n" \
              "Powered by: Python 3.9, Qt Designer,\n " \
              "PyQt5, OpenGL, OpenMesh and ModernGL.\n\n" \
              "Movement:\n" \
              "•  Left mouse button to rotate\n" \
              "•  Mouse wheel to zoom\n" \
              "•  Right mouse button to pan."
    msg = QMessageBox()
    msg.setStyleSheet("""
                      QMessageBox {
                      background-color: rgb(56, 56, 56);
                      letter-spacing: 0.4cm;
                      font-size: 14px;
                      color: rgb(145, 145, 145);
                      }
                      width: 60px;
                      color: rgb(200, 200, 200);
                      background-color: rgb(56, 56, 56);
                      padding: 10px;
                      width: 60px;
                      """
                      )
    msg.setWindowTitle(title)
    msg.setText(message)
    msg.setStandardButtons(QMessageBox.Close)
    msg.exec_()


def exit_app():
    sys.exit()
