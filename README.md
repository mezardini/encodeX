# encodeX

encodeX is a Django Rest Framework (DRF) project that provides API endpoints for encoding and decoding messages in images using steganography.

## Table of Contents
- [Installation](#installation)
- [Usage](#usage)
- [API Endpoints](#api-endpoints)
- [Contributing](#contributing)
- [License](#license)

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/mezardini/encodeX.git
   cd encodeX

2. Install dependencies, apply migrations and run:

    ```bash
    pip install -r requirements.txt
    python manage.py migrate
    python manage.py runserver


## Usage

1. To encode a message in an image, make a POST request to the /api/encodeimage/ endpoint. Provide an image file and the message to be encoded as form data.
   Example curl:

   ```bash
   curl -X POST -H "Content-Type: multipart/form-data" 
   -F "image=@/path/to/your/image.jpg" 
   -F "message=Hello, steganography!" 
   http://localhost:8000/api/encodeimage/



2. To decode a message from an encoded image, make a POST request to the /api/decodeimage/ endpoint. Provide the encoded image file as form data.
  Example using curl:
  
    ```bash
    curl -X POST -H "Content-Type: multipart/form-data" \
    -F "image=@/path/to/your/encoded_image.png" \
    http://localhost:8000/api/decodeimage/


## API Endpoints
Encode a Message:

POST /api/encode/: Upload an image and a message to encode the message in the image.
Decode an Image:

POST /api/decode/: Upload an encoded image to decode the message.



