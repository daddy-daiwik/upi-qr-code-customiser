import qrcode
from PIL import Image
import segno


data = ""

qr = segno.make(data, error='h')
qr.to_artistic(
    background='inr.jpeg',
    target='prabir-qr.png',
    scale=10,
    dark="#000000",
    light="#FFFFFF"
)

# qr_img.save("styled_qr.png")