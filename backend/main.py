import io
import numpy as np

# REST API
from flask import Flask  # For REST API suppprt
from flask import request
from flask_cors import CORS  # To call the API with cross-origins

# Encode and decode message
import json
import base64

# Encode and decode image
from PIL import Image
import cv2 as cv

# Custom classes and methods
import FrequencyImage as fi

### Settings
dev = False

app = Flask(__name__)
CORS(app)

progresses = []


### ROUTES AND PROCESSES

@app.route('/', methods=['GET', 'POST'], endpoint='init')
def init_image():
    '''
    Decodes the base64 encoded image, sent via REST post request.

    API JSON format:
    {
        image: BASE64CODE
    }
    
    '''

    # Error handling
    if request.method != 'POST':
        print("Wrong request type. Use POST request instead.")
        return "Wrong request type. Use POST request instead."

    ### 1. decode the message content
    if dev:
        print('-------------------------------------')

    # Get POST message
    message = request.data

    # Convert json to python dict
    message = json.loads(message)

    # decode image, get format
    img, img_format = decode_image(message['image'])

    val_low = message['val_low']
    val_high = message['val_high']
    freq_low = message['freq_low']
    freq_high = message['freq_high']
    filter_type = message['filter_type']

    ### 2 + 3 . Build the spectrum image and the modified image

    prog_Id = len(progresses)
    freq_image = fi.FrequencyImage(prog_Id, img, img_format, freq_low, freq_high, val_low, val_high, filter_type)
    progresses.append(freq_image)
    spectrum_img = freq_image.get_spectrum()
    mod_img = freq_image.get_mod_img()

    ### 4. Prepare response message
    encoded_spectrum_img = encode_image(spectrum_img, img_format, saveimg=False)
    encoded_mod_img = encode_image(mod_img, img_format, saveimg=False)

    response = {
        'imageResult': encoded_mod_img,
        'spectrumImage': encoded_spectrum_img,
        'progId': prog_Id
    }

    response = make_response(response)

    return response

@app.route('/filter/', methods=['GET', 'POST'])
def filter_Image():
    global prog_Id, progresses

    ### 1. decode the message content

    # Get POST message
    message = request.data

    # Convert json to python dict
    message = json.loads(message)

    val_low = message['val_low']
    val_high = message['val_high']
    freq_low = message['freq_low']
    freq_high = message['freq_high']
    filter_type = message['filter_type']

    try:
        notch_image, notch_image_format = decode_image(message['notch_image'])
    except:
        notch_image = None
        notch_image_format = None

    # Check if notch image is given
    if notch_image == "":
        print('no notch filter image found. set to None')
        notch_image = None

    prog_Id = message['progId']

    if dev:
        print('-------------------------------------')
        print('Start filtering, prog. ID: {}'.format(prog_Id))

    # Get correct progress
    freq_img = progresses[prog_Id]

    ### 2. Modify spectrum
    freq_img.filter_spectrum(freq_low, freq_high, val_low, val_high, filter_type, notch_image)
    mod_spectrum = freq_img.get_spectrum()

    ### 3. Get image from new spectrum
    mod_image = freq_img.get_mod_img()

    ### 4. Prepare response message
    encoded_spectrum = encode_image(mod_spectrum, freq_img.img_format)
    encoded_mod_img = encode_image(mod_image, freq_img.img_format)

    response = {
        'imageResult': encoded_mod_img,
        'spectrumImage': encoded_spectrum
    }

    # build message
    response = make_response(response)

    return response


### DECODERS AND ENCODERS

def decode_image(img_base64, saveimg=False):
    # Clean up the data, save image format
    img_export = img_base64.split(';base64,')
    img_format = img_export[0].split('data:image/')[1]
    img_base64 = img_export[1]

    # img_format = re.search(r'data:image/(.*);',img_export.group(0)).group(1)

    # Open data as byte string
    img_byte = base64.b64decode(img_base64)

    # Open stream, load entire image as a string stream
    buffer = io.BytesIO(img_byte)

    # Open base64 as image file
    img = Image.open(buffer).convert('L')

    # Convert read image file to numpy array
    img = np.array(img)

    # save image
    if saveimg:
        img.save('received.png')

    return img, img_format


def encode_image(img, img_format, saveimg=False):
    # Save array as image file
    if saveimg:
        buffer = Image.fromarray(np.uint8(img))
        filename = str(np.abs(hash(str(img))))
        buffer.save('enc_' + filename + '.png')

    # Fix JPEG => JPG file ending
    if img_format == 'jpeg':
        img_format == 'jpg'

    # Encode array as file
    retval, img_output_64 = cv.imencode('.' + img_format, img)

    # Encode file as base64
    img_data64 = base64.b64encode(img_output_64).decode('utf-8')

    # Format base64 string for HTML frontend
    img_base64 = 'data:image/' + img_format + ';base64,' + img_data64

    return img_base64


def make_response(message):
    # Return as JSON
    return json.dumps(message)


######## MAIN

if __name__ == '__main__':
    app.run(debug=True)
