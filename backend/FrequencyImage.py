import numpy as np
from numpy import linalg

from matplotlib import pyplot as plt
from math import sqrt

### Settings
dev = False

def circle_kernel(width = 100, height = 100, radius = 50, max_val=255):

    # Get center
    a, b = np.round(width / 2), np.round(height / 2)

    y,x = np.ogrid[-a:width-a, -b:height-b]
    mask = x*x + y*y <= radius*radius

    array = np.zeros((width, height))
    array[mask] = max_val
    return array



def disk_kernel(width = 100, height = 100, inner_radius = 20, outer_radius = 5, max_val=255):

    # Get center
    a, b = np.round(width / 2), np.round(height / 2)

    y,x = np.ogrid[-a:width-a, -b:height-b]
    mask = (x*x + y*y <= outer_radius*outer_radius) & (x*x + y*y >= inner_radius * inner_radius)

    array = np.zeros((width, height))
    array[mask] = max_val
    return array

def gaussian_filter(kernel_size=10, sigma=5):

    # Build kernel based on sigma
    rows, cols = kernel_size
    kernel = np.zeros((rows, cols))


### FrequencyImage class

class FrequencyImage:

    def __init__(self, prog_id, img, img_format, freq_low=0.0, freq_high=255.0, val_low=0.0, val_high=100.0, filter_type='bandpass'):

        self.prog_id = prog_id

        self.img = img
        self.img_format = img_format

        self.spectrum = np.array([])
        self.mod_spectrum = np.array([])

        self.freq_high = freq_high
        self.freq_low = freq_low

        self.val_high = val_high
        self.val_low = val_low

        self.filter_type = filter_type
        

        self.mod_img = np.array([])

        # Preprocess
        self.set_spectrum(self.img)


    ### SETTERS


    def set_freq_high(self, freq_high):
        self.freq_high = freq_high



    def set_freq_high(self, freq_low):
        self.freq_low = freq_low
    


    def set_mod_img(self):

        # TODO: De-normalize image

        # reverse power of 2 and np.log
        fshift = np.sqrt(self.mod_spectrum)
        fshift = np.exp(fshift)
        # Inverse the fft shifting & FFT
        frequencies = np.fft.ifftshift(fshift)
        mod_img = np.fft.ifft2(frequencies)

        self.mod_img = np.abs(mod_img)

        



    def set_spectrum(self, img):

        # Calculate the frequency spectrum with fast fourier transform
        frequencies = np.fft.fft2(img)
        
        # Now shift the quadrants around so that freq_low spatial frequencies are in
        # the center of the 2D fourier transformed image.
        fshift = np.fft.fftshift(frequencies)

        fshift = np.log(fshift)
        fshift = fshift ** 2

        # TODO: scale spectrum to be quadratic
        

        # Return results
        if dev:
            print('---------- SPECTRUM RESULTS -----------')
            print('Image metrics:')
            print('Size of image: {}'.format(np.shape(img)))
            print('Min: {}, max: {}'.format(np.min(img), np.max(img)))
            print('Median: {}, meam: {}'.format(np.median(img), np.mean(img)))
            print('\n')
            print('Spectrum metrics:')
            print('Format of fourier transformation: {}'.format(np.shape(fshift)))
            print('Min: {}, max: {}'.format(np.min(fshift), np.max(fshift)))
            print('Median: {}, meam: {}'.format(np.median(fshift), np.mean(fshift)))
            print('\n')

        self.spectrum = fshift
        self.mod_spectrum = fshift

        self.filter_spectrum(self.freq_low, self.freq_high, self.val_low, self.val_high, self.filter_type)


    
    def filter_spectrum(self, freq_low, freq_high, val_low, val_high, filter_type='bandpass'):

        if dev:
            print('Filter with these settings:\nFreq high: {}\nFreq low: {}\nval high: {}\nval low: {}\nInverse: {}'.format(freq_low, freq_high, val_low, val_high, filter_type))

        # Set val_low and val_high
        self.val_low = val_low
        self.val_high = val_high

        self.freq_low = freq_low
        self.freq_high = freq_high

        self.filter_type = filter_type

        # Reset spectrum
        if dev:
            print('Is mod_spectrum equal to spectrum? {}'.format(np.array_equal(self.mod_spectrum, self.spectrum)))
            print('Reset the spectrum...')
        mod_spectrum = np.copy(self.spectrum)
        if dev:
            print('Is mod_spectrum equal to spectrum? {}'.format(np.array_equal(mod_spectrum, self.spectrum)))

        min_val = np.min(mod_spectrum.real)
        if min_val < 0:
            min_val = 0

        max_val = np.max(mod_spectrum.real)

        if dev:
            print('Spectrum: Min val: {} \nMax val: {}'.format(np.min(mod_spectrum), np.max(mod_spectrum)))


        # Filter
        # if filter_type:
        #     mod_spectrum[mod_spectrum[:] > val_low] = 0.0
        #     mod_spectrum[mod_spectrum[:] < max_val * val_high / 1000] = 0.0
        # else:
        #     mod_spectrum[mod_spectrum[:] < val_low] = 0.0
        #     mod_spectrum[mod_spectrum[:] > max_val * val_high / 1000] = 0.0

        # Make filter_type filter mask
        if filter_type == 'bandpass':
            kernel = disk_kernel(np.shape(mod_spectrum)[0], np.shape(mod_spectrum)[1], max_val * val_low / 100 * 2, max_val *  val_high / 100 * 2, max_val=1.0)
        else:
            kernel = disk_kernel(np.shape(mod_spectrum)[0], np.shape(mod_spectrum)[1], max_val * val_high / 100 * 2, max_val * val_low / 100 * 2, max_val=1.0)
            

        mod_spectrum *= kernel

        self.mod_spectrum = mod_spectrum

        # Get center of spectrum
        # shape = np.shape(self.mod_spectrum)
        # width = shape[0]
        # height = shape[1]

        # center = [width / 2 , height / 2]

        # # Calculate euclidean distance and compare for each point
        # for idx, value in enumerate(self.mod_spectrum):
        #     dist = np.linalg.norm(center,idx)
        #     if dist < width * height * freq_low / 100 or dist > width * height * freq_high / 100:
        #         self.mod_spectrum[idx] = 0

        self.set_mod_img()


    ### GETTERS


    def get_spectrum (self):
        return np.abs(self.mod_spectrum)

    def get_mod_img (self):
        return self.mod_img

    def get_prog_Id (self):
        return self.prog_id