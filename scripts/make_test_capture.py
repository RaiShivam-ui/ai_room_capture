from pathlib import Path
import cv2
import numpy as np


OUT = Path("data/captures/photos/test_room")
OUT.mkdir(parents=True, exist_ok=True)


def make_image(index, shift_x, shift_y):
    image = np.full((700, 1000, 3), 235, dtype=np.uint8)

    # Floor
    cv2.rectangle(image, (0, 430), (999, 699), (190, 190, 190), -1)

    # Back wall
    cv2.rectangle(image, (80, 100), (920, 430), (220, 220, 220), -1)

    # Window
    cv2.rectangle(image, (230, 180), (430, 330), (160, 190, 210), -1)
    cv2.rectangle(image, (230, 180), (430, 330), (40, 40, 40), 4)

    # Door
    cv2.rectangle(image, (620, 160), (790, 430), (120, 90, 60), -1)
    cv2.rectangle(image, (620, 160), (790, 430), (40, 40, 40), 4)

    # Simple furniture/features
    cv2.rectangle(image, (300, 350), (520, 430), (100, 120, 140), -1)
    cv2.circle(image, (550, 380), 35, (80, 100, 80), -1)

    matrix = np.float32([
        [1, 0, shift_x],
        [0, 1, shift_y],
    ])

    image = cv2.warpAffine(image, matrix, (1000, 700))

    cv2.putText(
        image,
        f"TEST ROOM {index}",
        (30, 50),
        cv2.FONT_HERSHEY_SIMPLEX,
        1,
        (30, 30, 30),
        2,
    )

    return image


for i, (x, y) in enumerate(
    [(0, 0), (-80, 5), (-160, 10)],
    start=1,
):
    cv2.imwrite(
        str(OUT / f"room_{i}.jpg"),
        make_image(i, x, y),
    )

print(f"Created test capture: {OUT}")