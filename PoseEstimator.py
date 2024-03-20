import cv2
from ultralytics import YOLO
from cvzone.PoseModule import PoseDetector


class PoseEstimator:
    def __init__(
        self, model_path="yolov8s-pose.pt", screen_width=1920, screen_height=1080
    ):
        self.model = YOLO(model_path).to("cpu")
        self.keypoint_connections = [
            (0, 1),
            (0, 2),
            (1, 3),
            (2, 4),
            (5, 6),
            (5, 7),
            (6, 8),
            (7, 9),
            (8, 10),
            (5, 11),
            (6, 12),
            (11, 12),
            (11, 13),
            (12, 14),
            (13, 15),
            (14, 16),
        ]
        self.screen_width = screen_width
        self.screen_height = screen_height

    def draw_bbox(self, image, bbox, confidence, class_name="person"):
        x1, y1, x2, y2 = bbox
        cv2.rectangle(image, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2)
        text = f"Class: {class_name} Confidence: {confidence:.2f}"
        cv2.putText(
            image,
            text,
            (int(x1), int(y1) - 5),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (255, 255, 255),
            1,
        )

    def draw_body_pose(self, image, keypoints, connections):
        for kpt in keypoints:
            item = []
            for i in range(17):
                if i < len(kpt):
                    x, y = int(kpt[i][0]), int(kpt[i][1])
                    if (x, y) != (0, 0):
                        cv2.circle(
                            image, (x, y), radius=5, color=(0, 255, 0), thickness=-1
                        )
                        item.append([x, y])
                    else:
                        item.append([0, 0])
            print(item)
            for start_idx, end_idx in connections:
                if start_idx < len(kpt) and end_idx < len(kpt):
                    start_point = (int(kpt[start_idx][0]), int(kpt[start_idx][1]))
                    end_point = (int(kpt[end_idx][0]), int(kpt[end_idx][1]))
                    if start_point != (0, 0) and end_point != (0, 0):
                        cv2.line(
                            image, start_point, end_point, (255, 0, 0), thickness=2
                        )

    def predict(self, image):
        # img = cv2.resize(image, (self.screen_width, self.screen_height))
        results = self.model(image)
        result_keypoint = results[0].keypoints.xy.cpu().numpy()
        self.draw_body_pose(image, result_keypoint, self.keypoint_connections)
        if len(results[0].boxes.xyxy) > 0 and len(results[0].boxes.conf) > 0:
            self.draw_bbox(
                image,
                results[0].boxes.xyxy[0].cpu().numpy(),
                results[0].boxes.conf[0].cpu().item(),
            )
        return image


if __name__ == "__main__":
    cap = cv2.VideoCapture(0)
    estimator = PoseEstimator()

    while True:
        isSuccess, img = cap.read()
        if not isSuccess:
            break
        output_img = estimator.predict(img)
        cv2.imshow("Image Show", output_img)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()
