#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'Thesis.ui'
#
# Created by: PyQt5 UI code generator 5.5.1
#
# WARNING! All changes made in this file will be lost!

import sys
import copy
import rospy
import numpy as np
import threading
import tf
from cv_bridge import CvBridge
from darknet_ros_msgs.msg import BoundingBoxes
import pyrealsense2 as rs
from sensor_msgs.msg import Image
import moveit_commander
import moveit_msgs.msg
import geometry_msgs.msg
from geometry_msgs.msg import PointStamped
from math import pi
from std_msgs.msg import String
from darknet_ros_msgs.msg import BoundingBoxes
from moveit_commander.conversions import pose_to_list
from PyQt5 import QtCore, QtGui, QtWidgets
from movegroup_interface import PandaMoveGroupInterface
from extended_planning_scene_interface import ExtendedPlanningSceneInterface
from tf.transformations import euler_from_quaternion, quaternion_from_euler
import utils

# import tfui


laser_rostopic = "/robot/rear_laser/filtered_scan"
intel_realsense_camera_tf = "camera_color_optical_frame"
robot_base_tf = "robot_base_footprint"
panda_tf = "world"

placeposition = [-0.529092784633, -0.376418745152, 0.275439616317]


class YoloNode:
    def __init__(self, camera):
        self.name = [None] * 5
        self.pixelxmid = [0] * 5
        self.pixelymid = [0] * 5
        self.coord = [[0.0] * 3 for i in range(5)]
        self.tfcoord = [0.0] * 3
        self.camera = camera
        self.listener = tf.TransformListener()
        self.objecttop = [0.0] * 3

    def callback(self, data):
        boundingboxes = data.bounding_boxes

        for i in range(len(boundingboxes)):
            if i < 5:
                self.name[i] = boundingboxes[i].Class
                self.pixelxmid[i] = int((boundingboxes[i].xmax + boundingboxes[i].xmin) / 2)
                self.pixelymid[i] = int((boundingboxes[i].ymin + boundingboxes[i].ymax) / 2)
        # self.resolveCoord()
        # self.tf()
        # self.printCoord()
    def gettopcoord(self, index):
        point = self.camera.deproject(self.pixelxmid[index], self.pixelymid[index])
        self.objecttop = point

    def resolveCoord(self):
        for i in range(len(self.name)):
            if self.name[i] is not None:
                point = self.camera.deproject(self.pixelxmid[i], self.pixelymid[i])
                self.coord[i] = point

    def printCoord(self):
        for i in range(len(self.name)):
            if self.name[i] is not None:
                print(
                    self.name[i]
                    + ": "
                    + " x: "
                    + str(self.coord[i][0])
                    + " y: "
                    + str(self.coord[i][1])
                    + " z: "
                    + str(self.coord[i][2])
                )

    def transform_point(self):
        x, y, z = self.objecttop
        pointstamp = PointStamped()
        pointstamp.header.frame_id = intel_realsense_camera_tf
        pointstamp.header.stamp = rospy.Time()
        pointstamp.point.x = x
        pointstamp.point.y = y
        pointstamp.point.z = z
        transformed_stampedpoint = self.listener.transformPoint(panda_tf, pointstamp)
        self.tfcoord[0] = transformed_stampedpoint.point.x - 0.05
        self.tfcoord[1] = transformed_stampedpoint.point.y + 0.01
        self.tfcoord[2] = transformed_stampedpoint.point.z + 0.2



class RealSenseNode:
    def __init__(self):
        self.pub = rospy.Publisher("/camera/color/image_raw", Image, queue_size=1)
        self.pipeline = rs.pipeline()
        self.config = rs.config()
        self.config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)
        self.config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)
        self.align = rs.align(rs.stream.color)
        self.profile = self.pipeline.start(self.config)

    def publisher(self):
        while not rospy.is_shutdown():
            self.frames = self.pipeline.wait_for_frames()
            self.frames = self.align.process(self.frames)
            self.color_frame = self.frames.get_color_frame()
            self.depth_frame = self.frames.get_depth_frame()
            npcolor = np.asanyarray(self.color_frame.get_data())
            bridge = CvBridge()
            image_message = bridge.cv2_to_imgmsg(npcolor, encoding="bgr8")
            self.pub.publish(image_message)

    def deproject(self, x, y):
        color_intrin = self.color_frame.profile.as_video_stream_profile().intrinsics
        udist = self.depth_frame.get_distance(x, y)
        point1 = rs.rs2_deproject_pixel_to_point(color_intrin, [x, y], udist)
        return point1


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(800, 600)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.layoutWidget = QtWidgets.QWidget(self.centralwidget)
        self.layoutWidget.setGeometry(QtCore.QRect(390, 240, 311, 95))
        self.layoutWidget.setObjectName("layoutWidget")
        self.gridLayout = QtWidgets.QGridLayout(self.layoutWidget)
        self.gridLayout.setObjectName("gridLayout")
        self.pushButton = QtWidgets.QPushButton(self.layoutWidget)
        self.pushButton.setObjectName("pushButton")
        self.pushButton.clicked.connect(self.moveup)
        self.gridLayout.addWidget(self.pushButton, 0, 1, 1, 1)
        self.pushButton_4 = QtWidgets.QPushButton(self.layoutWidget)
        self.pushButton_4.setObjectName("pushButton_4")
        self.pushButton_4.clicked.connect(self.moveleft)
        self.gridLayout.addWidget(self.pushButton_4, 1, 0, 1, 1)
        self.pushButton_5 = QtWidgets.QPushButton(self.layoutWidget)
        self.pushButton_5.setObjectName("pushButton_5")
        self.pushButton_5.clicked.connect(self.homebutton)
        self.gridLayout.addWidget(self.pushButton_5, 1, 1, 1, 1)
        self.pushButton_3 = QtWidgets.QPushButton(self.layoutWidget)
        self.pushButton_3.setObjectName("pushButton_3")
        self.pushButton_3.clicked.connect(self.moveright)
        self.gridLayout.addWidget(self.pushButton_3, 1, 2, 1, 1)
        self.pushButton_2 = QtWidgets.QPushButton(self.layoutWidget)
        self.pushButton_2.setObjectName("pushButton_2")
        self.pushButton_2.clicked.connect(self.movedown)
        self.gridLayout.addWidget(self.pushButton_2, 2, 1, 1, 1)
        self.pushButton_10 = QtWidgets.QPushButton(self.layoutWidget)
        self.pushButton_10.setObjectName("pushButton_10")
        self.pushButton_10.clicked.connect(self.movebackward)
        self.gridLayout.addWidget(self.pushButton_10, 0, 2, 1, 1)
        self.pushButton_11 = QtWidgets.QPushButton(self.layoutWidget)
        self.pushButton_11.setObjectName("pushButton_11")
        self.pushButton_11.clicked.connect(self.moveforward)
        self.gridLayout.addWidget(self.pushButton_11, 2, 0, 1, 1)
        self.splitter = QtWidgets.QSplitter(self.centralwidget)
        self.splitter.setGeometry(QtCore.QRect(70, 170, 231, 171))
        self.splitter.setOrientation(QtCore.Qt.Vertical)
        self.splitter.setObjectName("splitter")
        self.comboBox = QtWidgets.QComboBox(self.splitter)
        self.comboBox.setObjectName("comboBox")
        # self.comboBox.addItem("")
        # self.comboBox.addItem("")
        # self.comboBox.addItem("")
        self.comboBox.setEnabled(False)
        self.pushButton_13 = QtWidgets.QPushButton(self.splitter)
        self.pushButton_13.setObjectName("pushButton_13")
        self.pushButton_13.clicked.connect(self.hor_orient)
        self.pushButton_14 = QtWidgets.QPushButton(self.splitter)
        self.pushButton_14.setObjectName("pushButton_14")
        self.pushButton_14.clicked.connect(self.vert_orient)
        self.pushButton_6 = QtWidgets.QPushButton(self.splitter)
        self.pushButton_6.setObjectName("pushButton_6")
        self.pushButton_6.clicked.connect(self.release)
        self.pushButton_7 = QtWidgets.QPushButton(self.splitter)
        self.pushButton_7.setObjectName("pushButton_7")
        self.pushButton_7.clicked.connect(self.grasp)
        self.splitter_2 = QtWidgets.QSplitter(self.centralwidget)
        self.splitter_2.setGeometry(QtCore.QRect(70, 410, 621, 27))
        self.splitter_2.setOrientation(QtCore.Qt.Horizontal)
        self.splitter_2.setObjectName("splitter_2")
        self.pushButton_8 = QtWidgets.QPushButton(self.splitter_2)
        self.pushButton_8.setObjectName("pushButton_8")
        self.pushButton_8.clicked.connect(self.loadobjects)
        self.pushButton_9 = QtWidgets.QPushButton(self.splitter_2)
        self.pushButton_9.setObjectName("pushButton_9")
        self.pushButton_9.clicked.connect(self.pickobject)
        self.pushButton_12 = QtWidgets.QPushButton(self.splitter_2)
        self.pushButton_12.setObjectName("pushButton_12")
        self.pushButton_12.clicked.connect(self.place)
        self.splitter_3 = QtWidgets.QSplitter(self.centralwidget)
        self.splitter_3.setGeometry(QtCore.QRect(110, 480, 621, 21))
        self.splitter_3.setOrientation(QtCore.Qt.Horizontal)
        self.splitter_3.setObjectName("splitter_3")
        self.radioButton = QtWidgets.QRadioButton(self.splitter_3)
        self.radioButton.setChecked(True)
        self.radioButton.setObjectName("radioButton")
        self.buttonGroup = QtWidgets.QButtonGroup(MainWindow)
        self.buttonGroup.setObjectName("buttonGroup")
        self.buttonGroup.addButton(self.radioButton)
        self.radioButton_2 = QtWidgets.QRadioButton(self.splitter_3)
        self.radioButton_2.setObjectName("radioButton_2")
        self.buttonGroup.addButton(self.radioButton_2)
        self.radioButton_3 = QtWidgets.QRadioButton(self.splitter_3)
        self.radioButton_3.setObjectName("radioButton_3")
        self.buttonGroup.addButton(self.radioButton_3)
        MainWindow.setCentralWidget(self.centralwidget)

        self.panda = PandaMoveGroupInterface()
        self.pickflag = False
        self.scene = ExtendedPlanningSceneInterface()
        self.placeoffset = 0.0

        rospy.sleep(2)
        self.loadconstraints()

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.pushButton.setText(_translate("MainWindow", "UP"))
        self.pushButton_4.setText(_translate("MainWindow", "LEFT"))
        self.pushButton_5.setText(_translate("MainWindow", "HOME"))
        self.pushButton_3.setText(_translate("MainWindow", "RIGHT"))
        self.pushButton_2.setText(_translate("MainWindow", "DOWN"))
        self.pushButton_10.setText(_translate("MainWindow", "STRAIGHT"))
        self.pushButton_11.setText(_translate("MainWindow", "BACK"))
        # self.comboBox.setItemText(0, _translate("MainWindow", "Object 1"))
        # self.comboBox.setItemText(1, _translate("MainWindow", "Object 2"))
        # self.comboBox.setItemText(2, _translate("MainWindow", "Object 3"))
        self.pushButton_13.setText(_translate("MainWindow", "Horizontal Gripper"))
        self.pushButton_14.setText(_translate("MainWindow", "Rotate Gripper"))
        self.pushButton_6.setText(_translate("MainWindow", "Open Gripper"))
        self.pushButton_7.setText(_translate("MainWindow", "Close Gripper"))
        self.pushButton_8.setText(_translate("MainWindow", "Load Objects"))
        self.pushButton_9.setText(_translate("MainWindow", "Pick Object"))
        self.pushButton_12.setText(_translate("MainWindow", "Place"))
        self.radioButton.setText(_translate("MainWindow", "Slow"))
        self.radioButton_2.setText(_translate("MainWindow", "Medium"))
        self.radioButton_3.setText(_translate("MainWindow", "Fast"))

    def homebutton(self):
        if self.pickflag is True:
            self.pickflag = False
        jvposition = [
            1.634550363302231,
            -1.3411260843149029,
            0.9899407725726057,
            -2.554722122957723,
            0.9527293026895343,
            1.4631178311427895,
            -0.26157099916206467,
        ]

        self.panda._arm_group.go(jvposition, wait=True)
        self.panda._arm_group.stop()

    def grasp(self):
        self.panda.close_gripper()

    def release(self):
        self.panda.open_gripper()

    def vert_orient(self):
        self.panda.rotate_gripper()

    def hor_orient(self):
        self.panda.hor_gripper()

    def moveup(self):
        self.setspeed()
        group = self.panda._arm_group
        wpose = group.get_current_pose().pose
        waypoint = []
        wpose.position.z += self.speed  # move up (z)
        waypoint.append(copy.deepcopy(wpose))
        plan, fraction = group.compute_cartesian_path(waypoint, 0.01, 0.0)
        self.panda.execute_plan(plan)

    def movedown(self):
        self.setspeed()
        group = self.panda._arm_group
        wpose = group.get_current_pose().pose
        waypoint = []
        wpose.position.z -= self.speed  # move down (z)
        waypoint.append(copy.deepcopy(wpose))
        plan, fraction = group.compute_cartesian_path(waypoint, 0.01, 0.0)
        self.panda.execute_plan(plan)

    def moveright(self):
        self.setspeed()
        group = self.panda._arm_group
        wpose = group.get_current_pose().pose
        waypoint = []
        wpose.position.y += self.speed  # move up (z)
        waypoint.append(copy.deepcopy(wpose))
        plan, fraction = group.compute_cartesian_path(waypoint, 0.01, 0.0)
        self.panda.execute_plan(plan)

    def moveleft(self):
        self.setspeed()
        group = self.panda._arm_group
        wpose = group.get_current_pose().pose
        waypoint = []
        wpose.position.y -= self.speed  # move up (z)
        waypoint.append(copy.deepcopy(wpose))
        plan, fraction = group.compute_cartesian_path(waypoint, 0.01, 0.0)
        self.panda.execute_plan(plan)

    def moveforward(self):
        self.setspeed()
        group = self.panda._arm_group
        wpose = group.get_current_pose().pose
        waypoint = []
        wpose.position.x += self.speed  # move up (z)
        waypoint.append(copy.deepcopy(wpose))
        plan, fraction = group.compute_cartesian_path(waypoint, 0.01, 0.0)
        self.panda.execute_plan(plan)

    def movebackward(self):
        self.setspeed()
        group = self.panda._arm_group
        wpose = group.get_current_pose().pose
        waypoint = []
        wpose.position.x -= self.speed  # move up (z)
        waypoint.append(copy.deepcopy(wpose))
        plan, fraction = group.compute_cartesian_path(waypoint, 0.01, 0.0)
        self.panda.execute_plan(plan)

    def addscene(self):
        posebox1 = utils.create_pose_stamped_msg([0.5, 0.0, 0.2], quaternion_from_euler(0.0, 0.0, 0.0))
        posebox2 = utils.create_pose_stamped_msg([0.0, 0.5, 0.2], quaternion_from_euler(0.0, 0.0, 0.0))
        objectpose = utils.create_pose_stamped_msg([0.5, 0.0, 0.5], quaternion_from_euler(0.0, 0.0, 0.0))
        sizebox1 = [0.2, 0.4, 0.4]
        sizebox2 = [0.4, 0.2, 0.4]
        sizeobject = [0.02, 0.02, 0.2]
        stat = self.scene.add_box("box1", posebox1, sizebox1)
        if stat:
            stat2 = self.scene.add_box("box2", posebox2, sizebox2)
            if stat2:
                stat3 = self.scene.add_box("object1", objectpose, sizeobject)
                if stat3 is False:
                    rospy.loginfo("Could not add object to scene!!")
            else:
                rospy.loginfo("Could not add box2 to scene!!")
        else:
            rospy.loginfo("Could not add box1 to scene!!")

    def loadobjects(self):
        self.comboBox.setEnabled(True)
        self.comboBox.clear()
        self.comboBox.addItems(self.yolonode.name)

    def scanobjects(self):
        self.camera = RealSenseNode()
        self.yolonode = YoloNode(self.camera)
        rospy.Subscriber("/darknet_ros/bounding_boxes", BoundingBoxes, self.yolonode.callback)
        while not rospy.is_shutdown():
            self.camera.publisher()

    def pickobject(self):
        self.pickflag = True
        self.setspeed()
        self.panda.open_gripper(wait=True)
        rospy.sleep(0.5)
        objectchoice = str(self.comboBox.currentText())
        for i in range(len(self.yolonode.name)):
            if self.yolonode.name[i] == objectchoice:
                self.yolonode.gettopcoord(i)
                self.yolonode.transform_point()
                print(self.yolonode.name[i])
                print(self.yolonode.pixelxmid[i], self.yolonode.pixelymid[i])
                print(self.yolonode.objecttop)
                print(self.yolonode.tfcoord)
                self.panda.pick(self.yolonode.tfcoord)
                break
        # self.panda.close_gripper(wait = True)
        # rospy.sleep(1)
        # self.moveup()
    def place(self):
        self.homebutton()
        rospy.sleep(1)
        waypoint = []
        currpos = self.panda._arm_group.get_current_pose().pose
        xdiff = placeposition[0] - currpos.position.x
        ydiff = placeposition[1] - currpos.position.y
        zdiff = placeposition[2] - currpos.position.z

        currpos.position.x += xdiff
        currpos.position.y += ydiff
        currpos.position.z += (zdiff + 0.35)
        waypoint.append(copy.deepcopy(currpos))

        currpos.position.z -= (0.3 - self.placeoffset)
        waypoint.append(copy.deepcopy(currpos))


        plan, fraction = self.panda._arm_group.compute_cartesian_path(waypoint, 0.01, 0.0)
        self.panda.execute_plan(plan)
        rospy.sleep(0.5)
        self.panda.open_gripper(wait = True)

        self.placeoffset += 0.05




    def setspeed(self):
        if self.radioButton.isChecked():
            rbchoice = 0.01
        elif self.radioButton_2.isChecked():
            rbchoice = 0.03
        elif self.radioButton_3.isChecked():
            rbchoice = 0.05
        else:
            rospy.loginfo("Invalid panda speed set!!")
        self.speed = rbchoice

    def loadconstraints(self):
        posepole = utils.create_pose_stamped_msg([0.55, 0.25, 0.3], quaternion_from_euler(0.0, 0.0, 0.0))
        # posepole2 = utils.create_pose_stamped_msg([-0.03, -0.3, 0.0], quaternion_from_euler(0.0, 0.0, 0.0))
        sizepole = [0.02, 0.02, 1.0]
        # sizepole2 = [0.02, 0.02, 3.0]
        p1 = self.scene.add_box("pole1", posepole, sizepole)
        # if(p1):
        #     p2 = scene.add_box("pole2", posepole2, sizepole2)
        #     if(not p2):
        #         rospy.loginfo("Constraint pole 2 could not be added!!")
        if not p1:
            rospy.loginfo("Camera pole could not be added!!")

    def gethomejointvalues(self):
        group = self.panda._arm_group
        wpose = group.get_current_pose().pose
        print(wpose)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    x = threading.Thread(target=ui.scanobjects)
    x.setDaemon(True)
    x.start()
    sys.exit(app.exec_())
