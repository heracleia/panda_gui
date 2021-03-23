#!/usr/bin/env python

import rospy
from darknet_ros_msgs.msg import BoundingBoxes
import pyrealsense2 as rs

class ObjectDetails:
    def __init__(self, boundingboxes):
        self.name = []
        self.pixelxmid = []
        self.pixelymid = []
        for i in range(3):
            self.name.append(boundingboxes[i].Class)
            self.pixelxmid.append((boundingboxes[i].xmin + boundingboxes[i].xmax) / 2)
            self.pixelymid.append((boundingboxes[i].ymin + boundingboxes[i].ymax) / 2)
    def deproject_point(self):
        pipeline = rs.pipeline()
        config = rs.config()
        colorizer = rs.colorizer()
        config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 60)
        config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 60)
        align = rs.align(rs.stream.color)
        profile = pipeline.start(config)
        frames = pipeline.wait_for_frames()
        frames = align.process(frames)
        color_frame = frames.get_color_frame()
        depth_frame = frames.get_depth_frame()
        # color_image = np.asanyarray(color_frame.get_data())
        # depth_image = np.asanyarray(depth_frame.get_data())
        color_intrin = color_frame.profile.as_video_stream_profile().intrinsics
        # colorized_depth = np.asanyarray(colorizer.colorize(depth_frame).get_data())
        # x = 394
        # y = 326
        udist = depth_frame.get_distance(self.pixelxmid[0], self.pixelymid[0])
        point1 = rs.rs2_deproject_pixel_to_point(color_intrin, [self.pixelxmid[0], self.pixelymid[0]], udist)
        print(point1)

def callback(data):
    bb1 = ObjectDetails(data.bounding_boxes)

def listener():
    rospy.init_node('bblistener', anonymous = True)
    rospy.Subscriber("/darknet_ros/bounding_boxes", BoundingBoxes, callback)

    # rospy.spin()

if __name__ == '__main__':
    listener()
