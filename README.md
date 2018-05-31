# FOSPEX - Fourier Spectrum Explorer
An interactive application to explore the fourier spectrum of an image and find possible notch filters.

![Demo image](demo-img.png)

Used core frameworks and libraries:

- Frontend: NPM, Vue.js, Quasar
- Backend: FLASK

## Frontend

To run frontend, enter
```bash
cd frontend
quasar dev
```

## Backend

Make sure you have installed all requirements: 

```bash
cd backend
pip install -r requirements.txt
``

To run the backend, enter
```bash
FLASK_APP=main.py flask run
```

## Thery: Fourier transformation and frequency spectrum

There is a lot of explanation in the internet. Some of useful resources are:

- Aditi Majumder, M. Gopi: Introduction to Visual Computing. Core Concepts in Computer Vision, Graphics, and Image Processing (2018)
- [Ritchie Vink: Understanding the Fourier Transform by example](https://www.ritchievink.com/blog/2017/04/23/understanding-the-fourier-transform-by-example/)
- [Paul Bourke: Image filter](http://paulbourke.net/miscellaneous/imagefilter/)
- [K Hong: Signal Processing with NumPy II - Image Fourier Transform : FFT & DFT](http://www.bogotobogo.com/python/OpenCV_Python/python_opencv3_Signal_Processing_with_NumPy_Fourier_Transform_FFT_DFT_2.php)
- [Jessica Lu: Fourier Transforms of Images in Python](http://www.astrobetter.com/blog/2010/03/03/fourier-transforms-of-images-in-python/)