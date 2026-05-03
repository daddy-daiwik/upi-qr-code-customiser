import cv2
import sys
from pathlib import Path

def candidate_images(image):
    """Generate various preprocessed versions of the image to improve detection odds."""
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

def main():
    if len(sys.argv) < 2:
        print("Usage: python test_extract.py <path_to_image>")
        sys.exit(1)
        
    image_path = Path(sys.argv[1])
    
    if not image_path.exists():
        print(f"Error: File '{image_path}' not found.")
        sys.exit(1)
        
    print(f"Attempting to read QR code from: {image_path}")
    img = cv2.imread(str(image_path))
    
    if img is None:
        print("Error: Could not decode image.")
        sys.exit(1)
        
    detector = cv2.QRCodeDetector()
    decoded_data = None
    
    for idx, candidate in enumerate(candidate_images(img)):
        data, _, _ = detector.detectAndDecode(candidate)
        if data:
            print(f"[SUCCESS] Extracted on attempt #{idx + 1}")
            print(f"\n--- EXTRACTED DATA ---\n{data}\n----------------------")
            decoded_data = data
            break
            
    if not decoded_data:
        print("[FAILURE] Could not detect any QR code in the image.")
        sys.exit(1)

if __name__ == "__main__":
    main()
