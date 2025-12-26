import cv2
import numpy as np
import urllib.request

CAM_URL = "http://10.98.95.1/capture"   # <-- change IP

print("Showing ESP32-CAM stream. Press ESC to exit.")

while True:
    try:
        # Get single JPEG frame
        resp = urllib.request.urlopen(CAM_URL, timeout=1)
        img_np = np.frombuffer(resp.read(), dtype=np.uint8)
        frame = cv2.imdecode(img_np, cv2.IMREAD_COLOR)

        if frame is None:
            continue

        cv2.imshow("ESP32-CAM", frame)

        if cv2.waitKey(1) & 0xFF == 27:   # ESC key
            break

    except Exception as e:
        print("Camera error:", e)

cv2.destroyAllWindows()
