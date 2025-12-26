import serial
import numpy as np
import cv2

# -------- CONFIG --------
SERIAL_PORT = "COM4"      # change if needed
BAUD = 115200
ROWS = 8
COLS = 8
UPSCALE = 40              # visualization size
MIN_DIST = 1              # mm (allow very small values)
MAX_DIST = 2000           # mm
# ------------------------

ser = serial.Serial(SERIAL_PORT, BAUD, timeout=1)

print("VL53L5CX Depth Map (tab/space separated)")
print("Press ESC to exit")

depth_rows = []

while True:
    try:
        raw = ser.readline().decode(errors="ignore")

        # Strip whitespace
        line = raw.strip()

        # Skip empty lines
        if not line:
            continue

        # Split by ANY whitespace (tabs or spaces)
        parts = line.split()

        # Expect exactly 8 values per row
        if len(parts) != COLS:
            continue

        # Convert to integers safely
        try:
            row = [int(p) for p in parts]
        except ValueError:
            continue

        depth_rows.append(row)

        # Once we collect 8 rows → full frame
        if len(depth_rows) == ROWS:
            depth = np.array(depth_rows, dtype=np.float32)
            depth_rows = []

            # Clamp invalid values
            depth = np.clip(depth, MIN_DIST, MAX_DIST)

            # Normalize for display
            depth_norm = ((depth - depth.min()) /
              (np.ptp(depth) + 1e-6) * 255).astype(np.uint8)

            # Upscale for visualization
            depth_big = cv2.resize(
                depth_norm,
                (COLS * UPSCALE, ROWS * UPSCALE),
                interpolation=cv2.INTER_CUBIC
            )

            # Apply color map
            depth_color = cv2.applyColorMap(depth_big, cv2.COLORMAP_JET)

            # Overlay numeric values (optional but useful)
            for r in range(ROWS):
                for c in range(COLS):
                    cv2.putText(
                        depth_color,
                        str(int(depth[r, c])),
                        (c * UPSCALE + 5, r * UPSCALE + 22),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.4,
                        (255, 255, 255),
                        1
                    )

            cv2.imshow("VL53L5CX Depth Map (8x8)", depth_color)

        if cv2.waitKey(1) & 0xFF == 27:
            break

    except Exception as e:
        print("Serial error:", e)

cv2.destroyAllWindows()
ser.close()
