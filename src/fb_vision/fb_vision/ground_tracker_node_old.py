import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from sensor_msgs.msg import CompressedImage, Image
import torch
import torchvision.models.segmentation as seg
import torchvision.transforms.functional as TF
from torchvision.transforms import InterpolationMode
import numpy as np
import time
import cv2

import cv2
from cv_bridge import CvBridge

class GroundTrackerNode(Node):
    def __init__(self):
        super().__init__('ground_tracker_node')
        
        self.image_sub = self.create_subscription(
            CompressedImage,
            'camera/collector/image_raw/compressed',
            self.image_callback,
            1
        )
            
        self.mask_pub = self.create_publisher(Image, 'vision/ground_segmentation/mask', 10)
        self.vis_pub = self.create_publisher(CompressedImage, 'vision/ground_segmentation/visualization', 10)
        
        self.get_logger().info("Ground Tracker Node Initialized")

        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.device = device
        # self.model = seg.lraspp_mobilenet_v3_large(weights=None, num_classes=1).to(device)
        # self.model.load_state_dict(torch.load("./src/models/prl_segment_epoch_100.pth", map_location=self.device))
        # self.model.eval()
        self.size = 224

    def largest_mask_component_center(self, mask):
        # Ensure binary uint8
        mask = (mask > 0).astype(np.uint8)
        # Connected components
        num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(mask, connectivity=8)

        if num_labels <= 1:
            return (-1, -1)  # no foreground
        
        # stats[:, cv2.CC_STAT_AREA] gives area of each component
        areas = stats[1:, cv2.CC_STAT_AREA]  # skip background
        largest_idx = 1 + np.argmax(areas)
        # centroid of largest component
        cx, cy = centroids[largest_idx]

        return (cx, cy)

    def predict(self, image):
        # img = torch.from_numpy(image).float() / 255.0 # HWC
        # img = img.permute(2, 0, 1) # → CHW
        # img_square = TF.resize(img, [self.size, self.size], interpolation=InterpolationMode.BILINEAR)
        # input_tensor = img_square.unsqueeze(0).to(self.device) # → NCHW

        # with torch.no_grad():
        #     t0 = time.time()
        #     output = self.model(input_tensor)['out']
        #     print('Prediction time:', time.time() - t0, 's')
        #     output = torch.sigmoid(output).cpu().numpy().squeeze() > 0.5
        #     mask_square = (output.astype('uint8') * 255).astype('uint8')
        #     mask = cv2.resize(mask_square, (image.shape[1], image.shape[0]), interpolation=cv2.INTER_NEAREST)
        #     center = self.largest_mask_component_center(mask)
            
        #     vis = image.copy() 
        #     vis[mask > 0] = [0, 0, 255] # red overlay for mask
        #     # cross at the center of the largest component
        #     if center != (-1, -1):
        #         cv2.drawMarker(vis, (int(center[0]), int(center[1])), (0, 255, 0), markerType=cv2.MARKER_CROSS, markerSize=20, thickness=2)
        
        #     return mask, vis, center

        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image

        _, mask = cv2.threshold(gray, 100, 255, cv2.THRESH_BINARY)

        center = self.largest_mask_component_center(mask)

        vis = image.copy()
        vis[mask > 0] = [0, 0, 255] 
        
        if center != (-1, -1):
            cv2.drawMarker(
                vis,
                (int(center[0]), int(center[1])),
                (0, 255, 0),
                markerType=cv2.MARKER_CROSS,
                markerSize=20,
                thickness=2
            )

        return mask, vis, center

    def image_callback(self, msg):
        t0 = time.time()
        # self.get_logger().info("Received image data for processing")
        
        bridge = CvBridge()
        try:
            cv_image = bridge.compressed_imgmsg_to_cv2(msg, desired_encoding='bgr8')
        except Exception as e:
            self.get_logger().error(f"Error converting image: {e}")
            return
        
        mask, vis, center = self.predict(cv_image)

        mask_msg = bridge.cv2_to_imgmsg(mask, encoding='mono8')
        self.mask_pub.publish(mask_msg)
        vis_msg = bridge.cv2_to_compressed_imgmsg(vis)
        self.vis_pub.publish(vis_msg)

        print('Total time:', time.time() - t0, 's')


def main(args=None):
    rclpy.init(args=args)
    node = GroundTrackerNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()