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

        self.declare_parameter("threshold", -1)
        self.threshold = self.get_parameter("threshold").get_parameter_value().integer_value
        self.get_logger().info(f"Threshold: {self.threshold}")
        if self.threshold == -1:
            self.calibrated = False
        else:
            self.calibrated = True
            self.get_logger().info(f"Skipping calibration.")

        self.debug = False

    def put_text_box(self, img, text_lines):
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 0.4
        thickness = 1

        padding = 2
        x = 0
        y = 0

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
    
    def get_model_mask(self, image):
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

        return model_mask
    
    def get_calibrated_threshold(self, image):
        model_mask = self.get_model_mask(image)

        def _iou(a, b):
            a = a.astype(bool)
            b = b.astype(bool)
            inter = np.logical_and(a, b).sum()
            union = np.logical_or(a, b).sum()
            return inter / (union + 1e-6)

        best_t = 0
        best_score = -1

        for t in range(0, 256, 5):
            mask, _ = self.get_fast_mask_and_best_center(image, t, save=f"image_{t}.png")

            score = _iou(mask, model_mask)
            print(t, score)

            if score > best_score:
                best_score = score
                best_t = t

        print(f"Calibrated threshold: {best_t}, IoU: {best_score:.4f}")

        return best_t, model_mask
    
    def _save_ellipses_visual(self, image, ellipse_mask, output_path="image.png"):
        contours, _ = cv2.findContours(ellipse_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        vis = image.copy()
        cv2.drawContours(vis, contours, -1, (0, 255, 0), 2)
        cv2.imwrite(output_path, vis)
    
    def _fill_all_holes(self, mask):
        mask = (mask > 0).astype(np.uint8) * 255
        h, w = mask.shape[:2]
        flood = mask.copy()
        ff_mask = np.zeros((h + 2, w + 2), np.uint8)
        cv2.floodFill(flood, ff_mask, (0, 0), 255)
        flood_inv = cv2.bitwise_not(flood)
        filled = mask | flood_inv

        return filled
   
    def _largest_component_mask(self, mask):
        mask = (mask > 0).astype(np.uint8)

        num_labels, labels, stats, _ = cv2.connectedComponentsWithStats(
            mask, connectivity=8
        )

        # no foreground found
        if num_labels <= 1:
            return np.zeros_like(mask)

        # skip background (0), find largest component
        areas = stats[1:, cv2.CC_STAT_AREA]
        largest_idx = 1 + np.argmax(areas)

        # build output mask
        largest_mask = np.zeros_like(mask)
        largest_mask[labels == largest_idx] = 255

        return largest_mask

    def _detect_ellipses(self, mask):
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        ellipse_mask = np.zeros_like(mask)
        best_center = (-1, -1)
        max_area = 0

        for cnt in contours:
            if len(cnt) < 5:
                continue

            ellipse = cv2.fitEllipse(cnt)
            (cx, cy), (MA, ma), angle = ellipse

            ellipse_area = np.pi * (MA/2) * (ma/2)

            if ellipse_area < 200 + cy/240*300:
                continue

            contour_area = cv2.contourArea(cnt)
            fill_ratio = contour_area / ellipse_area if ellipse_area > 0 else 0

            if 0.5 < fill_ratio < 1.3:
                cv2.ellipse(ellipse_mask, ellipse, 255, -1)

                if ellipse_area > max_area:
                    max_area = ellipse_area
                    best_center = (int(cx), int(cy))

        return best_center, ellipse_mask

    def get_fast_mask_and_best_center(self, image, threshold, save=''):
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image
        gray = cv2.GaussianBlur(gray, (3,3), 0)

        _, mask = cv2.threshold(gray, threshold, 255, cv2.THRESH_BINARY)
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3,3))
        mask = cv2.dilate(mask, kernel, iterations=3)
        mask = cv2.erode(mask, kernel, iterations=3)
        mask = self._fill_all_holes(mask)
        
        largest_mask = self._largest_component_mask(mask)
        center, ellipse_mask = self._detect_ellipses(largest_mask)
        if save:
            self._save_ellipses_visual(image, ellipse_mask, output_path='/ros2_ws/src/fb_vision/log/' + save)

        return ellipse_mask, center

    # def get_center_from_mask(self, mask):
    #     mask = (mask > 0).astype(np.uint8)
    #     num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(mask, connectivity=8)

    #     if num_labels <= 1:
    #         return (-1, -1)
        
    #     areas = stats[1:, cv2.CC_STAT_AREA]  # skip background
    #     largest_idx = 1 + np.argmax(areas)
        
    #     cx, cy = centroids[largest_idx]

    #     return (int(cx), int(cy))
    
    def predict(self, image):
        if self.debug:
            _, model_mask = self.get_calibrated_threshold(image)
        elif not self.calibrated:
            self.threshold, _ = self.get_calibrated_threshold(image)
            self.calibrated = True
            
        mask, center = self.get_fast_mask_and_best_center(image, self.threshold)

        vis = image.copy()
        vis[mask > 0] = [0, 0, 255] 
        if self.debug:
            vis[model_mask > 0] = [255, 0, 0]
        vis = self.put_text_box(vis, ['threshold: ' + str(self.threshold), f'center: {center}'])

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