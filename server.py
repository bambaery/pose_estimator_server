import io
import cv2
import numpy as np
from fastapi import FastAPI, WebSocket
from fastapi.responses import StreamingResponse
from PIL import Image
from PoseEstimator import PoseEstimator  # Importing the PoseEstimator class from the previous code

app = FastAPI()
pose_estimator = PoseEstimator()  # Initialize PoseEstimator

def array_to_bytes(image_array):
    # Convert NumPy array to bytes
    image_pil = Image.fromarray(image_array)
    img_byte_arr = io.BytesIO()
    image_pil.save(img_byte_arr, format="JPEG")
    return img_byte_arr.getvalue()

def bytes_to_array(image_bytes):
    # Convert bytes to NumPy array
    image_pil = Image.open(io.BytesIO(image_bytes))
    return np.array(image_pil)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        try:
            data = await websocket.receive_bytes()
            img_array = bytes_to_array(data)
            processed_img = pose_estimator.predict(img_array)
            processed_img_bytes = array_to_bytes(processed_img)
            await websocket.send_bytes(processed_img_bytes)
        except Exception as e:
            print("An error occurred:", e)
            break

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)