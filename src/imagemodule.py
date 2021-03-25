#!/usr/bin/env python

import rospy
import numpy as np
from cv_bridge import CvBridge
from darknet_ros_msgs.msg import BoundingBoxes
import pyrealsense2 as rs
from sensor_msgs.msg import Image


class YoloNode:
    def __init__(self, camera):
        self.name = []
        self.pixelxmid = []
        self.pixelymid = []
        self.coord = []
        self.camera = camera


    def callback(self, data):
        boundingboxes = data.bounding_boxes
        for i in range(len(boundingboxes)):
             self.name.append(boundingboxes[i].Class)
             self.pixelxmid.append((boundingboxes[i].xmin + boundingboxes[i].xmax) / 2)
             self.pixelymid.append((boundingboxes[i].ymin + boundingboxes[i].ymax) / 2)
        self.resolveCoord()
        self.printCoord()

    def resolveCoord(self):
        for i in range(len(self.name)):
            self.coord.append(self.camera.deproject(self.pixelxmid[i], self.pixelymid[i]))

    def printCoord(self):
        for i in range(len(self.name)):
            print(self.name[i] + ": " + " x: " + str(self.coord[i][0]) + " y: " + str(self.coord[i][1]) + " z: " + str(self.coord[i][2]))





class RealSenseNode:
    def __init__(self):
        self.pub = rospy.Publisher('/camera/color/image_raw', Image, queue_size = 1)
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


if __name__ == '__main__':
    rospy.init_node('bblistener', anonymous = True)
    camera = RealSenseNode()
    yolonode = YoloNode(camera)
    rospy.Subscriber("/darknet_ros/bounding_boxes", BoundingBoxes, yolonode.callback)
    camera.publisher()
    rospy.spin()
