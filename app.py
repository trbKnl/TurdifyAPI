import io
from fastapi import FastAPI, File, UploadFile, Response, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from PIL import Image, ImageOps
import face_recognition

app = FastAPI()


# Constants
# PATH = "./"
PATH = "/app/"

def is_valid_image(image_buf: bytes) -> bool:
    """Check if image is a valid image"""
    try:
        Image.open(image_buf)
    except IOError:
        return False
    return True

def rotate_image(image_buf: bytes) -> bytes:
    try:
        with Image.open(image_buf) as im:
            im = ImageOps.exif_transpose(im)
            buf = io.BytesIO()
            im.save(buf, format="png")
            return buf
    except (AttributeError, KeyError, IndexError):
    # cases: image don't have getexif
        pass
    return image_buf

def detect_face_locations(image_buf: bytes) -> list:
    """Detect faces that may or may not be in in an image buffer"""
    image = face_recognition.load_image_file(image_buf)
    face_locations = face_recognition.face_locations(image)
    print(face_locations)
    return face_locations

def turdify_image(image_buf: bytes) -> bytes:
    """Paste turd emoji over detected faces in an image"""
    face_locations = detect_face_locations(image_buf)

    # Open the image buffer and the turd as PIL image
    with Image.open(image_buf) as im, Image.open(f"{PATH}/assets/turd.png") as turd:
        # Get the turd dimensions
        tw = float(turd.size[0])
        th = float(turd.size[1])

        for box in face_locations:
            # Resize the turd according to the size of the face,
            # and paste it over the face region
            x, y, a, b = box[::-1]
            basewidth = a - x
            ratio = float(basewidth) / tw
            turd_resized = turd.resize((int(tw * ratio), int(th*ratio)))
            im.paste(turd_resized, box=(x, int(b * 0.95)), mask=turd_resized)

        # Save the created image as png in a buffer and return
        buf = io.BytesIO()
        im.save(buf, format="png")
        buf.seek(0)       # Return to beginning of buffer
        data = buf.read() # Read all bytes until EOF
    return data


# curl -v -F 'my_file=@/home/turbo/pythontest/fastapitest/test.txt' http://127.0.0.1:8888/uploadfile/ > file.png
@app.post("/turdify/")
async def create_image(my_file: UploadFile = File(...)):

    contents = await my_file.read()  # Read file
    image_buf = io.BytesIO(contents) # Store in IO buffer
    if is_valid_image(image_buf):
        image_buf = rotate_image(image_buf)
        data = turdify_image(image_buf)  # Turdiy
        return Response(content=data, media_type="image/png")
    else:
        raise HTTPException(status_code=415, detail="Unsupported Media Type: File is not recognized as an image")



###################################################################################
# Serve the welcoming page at root

# Note: Statically serving at the root path takes over all subpaths
# causing /api/ to be taken over as well, this is not wanted. 
# I server the welcome page under /public
# Then redirect root to /public/index.html
app.mount("/public", StaticFiles(directory=f"{PATH}/welcomepage"), name="static")

@app.get("/")
async def root():
    return RedirectResponse(url="/public/index.html")


