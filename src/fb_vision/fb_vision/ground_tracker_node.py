import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from sensor_msgs.msg import Image
import torch
import torchvision.models.segmentation as seg
import torchvision.transforms.functional as TF
from torchvision.transforms import InterpolationMode
import numpy as np

import cv2
from cv_bridge import CvBridge

class GroundTrackerNode(Node):
    def __init__(self):
        super().__init__('ground_tracker_node')
        
        self.image_sub = self.create_subscription(
            Image,
            'camera/collector/image_raw',
            self.image_callback,
            10
        )
            
        self.mask_pub = self.create_publisher(Image, 'vision/ground_segmentation/mask', 10)
        self.vis_pub = self.create_publisher(Image, 'vision/ground_segmentation/visualization', 10)
        
        self.get_logger().info("Ground Tracker Node Initialized")

        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model = seg.deeplabv3_resnet50(weights=None, num_classes=1).to(self.device)
        self.model.load_state_dict(torch.load("./models/prl_segment_t04_epoch_100.pth", map_location=self.device))
        self.model.eval()
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
        img = torch.from_numpy(image).float() / 255.0 # HWC
        img = img.permute(2, 0, 1) # → CHW
        img_square = TF.resize(img, [self.size, self.size], interpolation=InterpolationMode.BILINEAR)
        input_tensor = img_square.unsqueeze(0).to(self.device) # → NCHW

        with torch.no_grad():
            output = self.model(input_tensor)['out']
            output = torch.sigmoid(output).cpu().numpy().squeeze() > 0.5
            mask_square = (output.astype('uint8') * 255).astype('uint8')
            mask = cv2.resize(mask_square, (image.shape[1], image.shape[0]), interpolation=cv2.INTER_NEAREST)
            center = self.largest_mask_component_center(mask)
            
            vis = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            vis[mask > 0] = [255, 0, 0] # red overlay for mask
            # cross at the center of the largest component
            if center != (-1, -1):
                cv2.drawMarker(vis, (int(center[0]), int(center[1])), (0, 255, 0), markerType=cv2.MARKER_CROSS, markerSize=20, thickness=2)
        
            return mask, vis, center

    def image_callback(self, msg):
        # self.get_logger().info("Received image data for processing")
        
        # Convert ROS Image message to OpenCV format
        bridge = CvBridge()
        try:
            cv_image = bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')
        except Exception as e:
            self.get_logger().error(f"Error converting image: {e}")
            return
        
        mask, vis, center = self.predict(cv_image)

        mask_msg = bridge.cv2_to_imgmsg(mask, encoding='mono8')
        self.mask_pub.publish(mask_msg)
        vis_msg = bridge.cv2_to_imgmsg(vis, encoding='rgb8')
        self.vis_pub.publish(vis_msg)


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