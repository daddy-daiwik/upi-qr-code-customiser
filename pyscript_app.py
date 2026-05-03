import asyncio
import base64
import io

from js import document, console, Uint8Array, window, FileReader, Image, jsQR
from pyodide.ffi import create_proxy
import segno

extracted_upi = ""
uploaded_logo_bytes = None

def process_image_with_jsqr(event):
    global extracted_upi
    
    img = event.target
    canvas = document.getElementById("canvas")
    ctx = canvas.getContext("2d", {"willReadFrequently": True})
    
    canvas.width = img.width
    canvas.height = img.height
    ctx.drawImage(img, 0, 0, img.width, img.height)
    
    # Try decoding
    imageData = ctx.getImageData(0, 0, canvas.width, canvas.height)
    # create options object for jsQR
    from js import Object
    options = Object.new()
    options.inversionAttempts = "attemptBoth"
    
    code = jsQR(imageData.data, imageData.width, imageData.height, options)
    
    # Basic Preprocessing 1: Thresholding
    if not code:
        data = imageData.data
        for i in range(0, len(data), 4):
            avg = (data[i] + data[i+1] + data[i+2]) / 3
            threshold = 255 if avg > 128 else 0
            data[i] = threshold
            data[i+1] = threshold
            data[i+2] = threshold
        ctx.putImageData(imageData, 0, 0)
        code = jsQR(imageData.data, imageData.width, imageData.height, options)
        
    # Basic Preprocessing 2: 2x scale
    if not code:
        canvas.width = img.width * 2
        canvas.height = img.height * 2
        ctx.imageSmoothingEnabled = False
        ctx.drawImage(img, 0, 0, canvas.width, canvas.height)
        imageData = ctx.getImageData(0, 0, canvas.width, canvas.height)
        code = jsQR(imageData.data, imageData.width, imageData.height, options)
    
    if code:
        extracted_upi = code.data
        document.getElementById("extracted-text").textContent = extracted_upi
        document.getElementById("extraction-result").classList.remove("hidden")
        document.getElementById("step-customize").classList.remove("hidden")
        generate_qr_proxy(None)
    else:
        window.alert("Could not detect a QR code in the uploaded image. Please try a clearer image.")

def on_reader_load(event):
    data_url = event.target.result
    img = Image.new()
    # Need to keep a reference to proxy to prevent garbage collection before onload fires
    global process_proxy
    process_proxy = create_proxy(process_image_with_jsqr)
    img.onload = process_proxy
    img.src = data_url

async def handle_qr_upload(event):
    file_list = event.target.files
    if file_list.length == 0:
        return
    
    file = file_list.item(0)
    reader = FileReader.new()
    
    # We must use global proxy so it doesn't get garbage collected
    global reader_proxy
    reader_proxy = create_proxy(on_reader_load)
    reader.onload = reader_proxy
    reader.readAsDataURL(file)

async def handle_logo_upload(event):
    global uploaded_logo_bytes
    file_list = event.target.files
    if file_list.length == 0:
        return
        
    file = file_list.item(0)
    document.getElementById("logo-filename").textContent = file.name
    
    array_buffer = await file.arrayBuffer()
    u8array = Uint8Array.new(array_buffer)
    uploaded_logo_bytes = u8array.to_py()
    
    # Auto-generate the QR code once the background image is uploaded
    generate_qr_proxy(None)
    
def generate_qr(event):
    global extracted_upi, uploaded_logo_bytes
    if not extracted_upi:
        return
        
    color_dots = document.getElementById("color-dots").value
    color_bg = document.getElementById("color-bg").value
    
    qr = segno.make(extracted_upi, error='h')
    out = io.BytesIO()
    
    if uploaded_logo_bytes:
        logo_io = io.BytesIO(uploaded_logo_bytes)
        try:
            qr.to_artistic(background=logo_io, target=out, kind='png', scale=10, dark=color_dots, light=color_bg)
        except Exception as e:
            window.alert(f"Failed to generate artistic QR: {str(e)}")
            qr.save(out, kind='png', scale=10, dark=color_dots, light=color_bg)
    else:
        qr.save(out, kind='png', scale=10, dark=color_dots, light=color_bg)
        
    b64_str = base64.b64encode(out.getvalue()).decode('utf-8')
    img_src = f"data:image/png;base64,{b64_str}"
    
    preview_div = document.getElementById("qr-preview")
    preview_div.innerHTML = f'<img src="{img_src}" alt="Generated QR" style="max-width: 100%; max-height: 100%; border-radius: 8px;">'
    preview_div.classList.remove("qr-placeholder")
    
    document.getElementById("download-btn").disabled = False
    document.getElementById("download-btn").setAttribute("data-url", img_src)

def download_qr(event):
    img_src = event.target.getAttribute("data-url")
    if not img_src:
        return
        
    a = document.createElement("a")
    a.href = img_src
    a.download = "my-custom-upi-qr.png"
    a.click()

upload_proxy = create_proxy(handle_qr_upload)
document.getElementById("qr-upload").addEventListener("change", upload_proxy)

logo_proxy = create_proxy(handle_logo_upload)
document.getElementById("logo-upload").addEventListener("change", logo_proxy)

generate_qr_proxy = create_proxy(generate_qr)
document.getElementById("generate-btn").addEventListener("click", generate_qr_proxy)
document.getElementById("color-dots").addEventListener("input", generate_qr_proxy)
document.getElementById("color-bg").addEventListener("input", generate_qr_proxy)

download_qr_proxy = create_proxy(download_qr)
document.getElementById("download-btn").addEventListener("click", download_qr_proxy)

loading_el = document.getElementById("pyscript-loading")
if loading_el:
    loading_el.style.display = "none"
