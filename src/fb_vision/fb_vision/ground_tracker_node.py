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
            
        self.center_pub = self.create_publisher(String, 'vision/ground_segmentation/center', 10)
        self.vis_pub = self.create_publisher(CompressedImage, 'vision/ground_segmentation/visualization', 10)
        
        self.get_logger().info("Ground Tracker Node Initialized")
        self.get_logger().info("Waiting for images...")

        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.device = device
        self.size = 224
        self.model = seg.lraspp_mobilenet_v3_large(weights=None, num_classes=1).to(device)
        self.model.load_state_dict(torch.load("./src/models/prl_segment_epoch_100.pth", map_location=self.device))
        self.model.eval()

        self.calibrated = False
        self.threshold = 225

        self.debug = False #True

    def put_text_box(self, img, text_lines):
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 0.4
        thickness = 1

        padding = 2
        x = 0
        y = 0

        line_height = 0

        widths = []
        heights = []

        for text in text_lines:
            (tw, th), baseline = cv2.getTextSize(text, font, font_scale, thickness)
            widths.append(tw)
            heights.append(th + baseline)

        box_w = max(widths) + padding * 2
        box_h = sum(heights) + padding * (len(text_lines) + 1)

        cv2.rectangle(
            img,
            (x, y),
            (x + box_w, y + box_h),
            (0, 0, 0),
            -1
        )

        y_offset = y + padding

        for i, text in enumerate(text_lines):
            (tw, th), baseline = cv2.getTextSize(text, font, font_scale, thickness)

            text_org = (x + padding, y_offset + th)

            cv2.putText(
                img,
                text,
                text_org,
                font,
                font_scale,
                (255, 255, 255),
                thickness,
                cv2.LINE_AA
            )

            y_offset += th + baseline + padding

        return img

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

        return (int(cx), int(cy))
    
    def calibrate_threshold_iou(self, image):
        img = torch.from_numpy(image).float() / 255.0
        img = img.permute(2, 0, 1)

        img_square = TF.resize(
            img,
            [self.size, self.size],
            interpolation=InterpolationMode.BILINEAR
        )

        input_tensor = img_square.unsqueeze(0).to(self.device)

        with torch.no_grad():
            output = self.model(input_tensor)['out']
            output = torch.sigmoid(output).cpu().numpy().squeeze()

        model_mask = (output > 0.5).astype(np.uint8)

        model_mask = cv2.resize(
            model_mask,
            (image.shape[1], image.shape[0]),
            interpolation=cv2.INTER_NEAREST
        )

        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        def iou(a, b):
            a = a.astype(bool)
            b = b.astype(bool)
            inter = np.logical_and(a, b).sum()
            union = np.logical_or(a, b).sum()
            return inter / (union + 1e-6)

        best_t = 0
        best_score = -1

        for t in range(0, 256, 5):
            mask = self.binarize(image, t)

            score = iou(mask, model_mask)
            print(t, score)

            if score > best_score:
                best_score = score
                best_t = t

        self.threshold = best_t

        print(f"Calibrated threshold: {best_t}, IoU: {best_score:.4f}")

        self.calibrated = True
        return best_t, model_mask
    
    def fill_all_holes(self, mask):
        mask = (mask > 0).astype(np.uint8) * 255
        h, w = mask.shape[:2]
        flood = mask.copy()
        ff_mask = np.zeros((h + 2, w + 2), np.uint8)
        cv2.floodFill(flood, ff_mask, (0, 0), 255)
        flood_inv = cv2.bitwise_not(flood)
        filled = mask | flood_inv

        return filled

    def binarize(self, image, threshold):
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image
        gray = cv2.GaussianBlur(gray, (3,3), 0)

        _, mask = cv2.threshold(gray, threshold, 255, cv2.THRESH_BINARY)
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3,3))
        mask = cv2.dilate(mask, kernel, iterations=1)
        mask = cv2.erode(mask, kernel, iterations=1)
        mask = cv2.erode(mask, kernel, iterations=1)
        mask = cv2.dilate(mask, kernel, iterations=1)
        mask = self.fill_all_holes(mask)
        return mask

    def predict(self, image):
        if not self.calibrated or self.debug:
            _, model_mask = self.calibrate_threshold_iou(image)
            
        mask = self.binarize(image, self.threshold)

        center = self.largest_mask_component_center(mask)

        vis = image.copy()
        vis[mask > 0] = [0, 0, 255] 
        if self.debug:
            vis[model_mask > 0] = [255, 0, 0]
        vis = self.put_text_box(vis, ['thresh: ' + str(self.threshold), f'center: {center}'])

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
        # self.get_logger().info("Received image data for processing")
        
        bridge = CvBridge()
        try:
            cv_image = bridge.compressed_imgmsg_to_cv2(msg, desired_encoding='bgr8')
        except Exception as e:
            self.get_logger().error(f"Error converting image: {e}")
            return
        
        mask, vis, center = self.predict(cv_image)

        center_msg = String(data=' '.join(map(str, center)))
        self.center_pub.publish(center_msg)
        vis_msg = bridge.cv2_to_compressed_imgmsg(vis)
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