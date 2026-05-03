from pathlib import Path
import sys

import cv2
from pyzbar.pyzbar import decode


def candidate_images(image):
    yield image

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    yield gray

    resized = cv2.resize(image, None, fx=2, fy=2, interpolation=cv2.INTER_NEAREST)
    yield resized

    resized_gray = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)
    yield resized_gray

    _, threshold = cv2.threshold(resized_gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    yield threshold
    yield cv2.bitwise_not(threshold)


def print_decoded(decoded):
    for item in decoded:
        print(item.data.decode())


image_path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("pra1.jpeg")
img = cv2.imread(str(image_path))

if img is None:
    print(f"Image not found: {image_path}")
    raise SystemExit(1)

for candidate in candidate_images(img):
    decoded = decode(candidate)
    if decoded:
        print_decoded(decoded)
        raise SystemExit(0)

detector = cv2.QRCodeDetector()
for candidate in candidate_images(img):
    data, _, _ = detector.detectAndDecode(candidate)
    if data:
        print(data)
        raise SystemExit(0)

print("No QR detected")