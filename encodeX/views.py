from rest_framework import generics
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser
from .models import EncodedImage
from .serializers import EncodedImageSerializer
from PIL import Image


def encode_image(image, message):
    
    img = Image.open(image)

    # Convert the message to binary
    hex_message = message.encode('utf-8').hex()

    # Ensure the image has enough space to store the message
    if len(hex_message) > img.width * img.height:
        raise ValueError("Message is too long for the given image size.")

    # Encode the message in the least significant bit (LSB) of each pixel
    data_index = 0
    for y in range(img.height):
        for x in range(img.width):
            pixel = list(img.getpixel((x, y)))
            for i in range(3):  # Iterate over RGB channels
                if data_index < len(hex_message):
                    pixel[i] = pixel[i] & ~1 | int(hex_message[data_index])
                    data_index += 1
            img.putpixel((x, y), tuple(pixel))

    # Return the encoded image
    return img


def decode_image(img):
    # Convert the image to grayscale for simplicity
    img = img.convert('L')

    binary_message = ""
    for y in range(img.height):
        for x in range(img.width):
            pixel = img.getpixel((x, y))
            binary_message += str(pixel & 1)

    # Convert binary message to characters
    message = ''.join(chr(int(binary_message[i:i + 8], 2))
                      for i in range(0, len(binary_message), 8))
    return message


class EncodeImageView(generics.CreateAPIView):
    queryset = EncodedImage.objects.all()
    serializer_class = EncodedImageSerializer

    def perform_create(self, serializer):
        image = self.request.data['image']
        message = self.request.data['message']

        # Encode the message in the image
        encoded_image = encode_image(image, message)

        # Save the encoded image
        serializer.save(image=encoded_image)


class DecodeImageView(generics.CreateAPIView):
    queryset = EncodedImage.objects.all()
    serializer_class = EncodedImageSerializer
    parser_classes = [MultiPartParser]

    def create(self, request, *args, **kwargs):
        image = request.data.get('image')

        # Ensure 'image' field is present in the request
        if not image:
            return Response({'error': 'Please provide an image for decoding.'}, status=400)

        # Decode the message from the image
        decoded_message = decode_image(image)

        # Create a new instance with the decoded message
        serializer = self.get_serializer(data={'message': decoded_message})
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=201, headers=headers)
