import numpy as np
import io

from flask import Flask     # For REST API suppprt
from flask import request
from flask_cors import CORS # To call the API with cross-origins
from matplotlib import pyplot as plt
import json
import base64
from PIL import Image
import cv2 as cv


app = Flask(__name__)
CORS(app)

### ROUTES AND PROCESSES

@app.route('/', methods=['GET', 'POST'])
def upload_image():
    '''
    Decodes the base64 encoded image, sent via API post request

    API JSON format:
    {
        image: BASE64CODE
    }
    
    ''' 

    # Eror handling
    if request.method != 'POST':
        print("Wrong request type. Use POST request instead.")
        return "Wrong request type. Use POST request instead."

    # Get POST message
    message = request.data

    # Convert json to python dict
    message = json.loads(message)

    # decode image, get format
    global img, img_format
    img, img_format = decode_image(message['image'])

    # Get spectrum
    global spectrum
    spectrum = get_spectrum(img)

    # Encode spectrum into bytes and base64
    encoded_image = encode_image(spectrum, img_format)

    # build message
    response = build_response_message(encoded_image, img_format)

    return response

@app.route('/filter/', methods=['GET', 'POST'])
def filter_Image():

    global high, low
    low = json.loads(request.data)['low']
    high = json.loads(request.data)['high']

    mod_spectrum = bandpassfilter_spectrum(spectrum,low,high)
    mod_image = get_image_from_spectrum(mod_spectrum)

    encoded_spectrum = encode_image(mod_spectrum, img_format)

    # Encode spectrum into bytes and base64
    encoded_image = encode_image(mod_image, img_format)

    response = {
        'newImage': encoded_image,
        'spectrumImage': encoded_spectrum
    }

    # build message
    response = json.dumps(response)

    return response



### DECODERS AND ENCODERS

def decode_image(img_base64, saveimg=False):

    # Clean up the data, save image format
    img_export = img_base64.split(';base64,')
    img_format = img_export[0].split('data:image/')[1]
    img_base64 = img_export[1]    

    #img_format = re.search(r'data:image/(.*);',img_export.group(0)).group(1)

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
        buffer.save('result.png')

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

def build_response_message (img_b64, img_format):

    # Dict
    response = {
        'image': img_b64
    }

    # Return as JSON
    return json.dumps(response)


### IMAGE PROCESSING METHODS

def get_spectrum(img):

    # Calculate the frequency spectrum with fast fourier transform
    f = np.fft.fft2(img)

    # Now shift the quadrants around so that low spatial frequencies are in
    # the center of the 2D fourier transformed image.
    fshift = np.fft.fftshift(f)

    # Calculate a 2D power spectrum
    psd_2D = np.abs( fshift )**2

    # Calculate the azimuthally averaged 1D power spectrum
    # psd_1D = radialProfile.azimuthalAverage(psd_2D)

    # Calculate the magnitude spectrum
    magnitude_spectrum = 20 * np.log(np.abs(fshift))

    # rescale to -1:+1 for display
    # fshift = (
    #     (
    #         (fshift - np.min(fshift)) * 2
    #     ) / np.ptp(fshift)  # 'ptp' = range
    # ) - 1

    return np.abs(magnitude_spectrum)


def get_image_from_spectrum(spec):

    # Reverse the fft shifting
    f = np.fft.ifftshift(spec)

    # Inverse the FFT
    img = np.fft.ifft2(f)

    # Make sure it contains only real numbers
    img = np.abs(img)

    return img


def bandpassfilter_spectrum(spec, low, high):
    mod_spectrum = spec.copy()
    mod_spectrum[mod_spectrum[:] < low] = 0.0
    mod_spectrum[mod_spectrum[:] > high] = 0.0
    return mod_spectrum

if __name__ == '__main__':
    app.run(debug=True)