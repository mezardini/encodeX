from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APIClient
from .models import EncodedImage
from PIL import Image


class SteganographyAppTests(TestCase):
    def setUp(self):
        # Create a sample image for testing
        self.sample_image = SimpleUploadedFile(
            "test_image.jpg", b"file_content", content_type="image/jpeg")

    def test_encode_image_api(self):
        client = APIClient()

        # Test encoding API endpoint
        response = client.post(
            '/api/encodeimage/', {'image': self.sample_image, 'message': 'Hello, steganography!'})
        self.assertEqual(response.status_code, 201)  # 201 Created

        # Verify that the EncodedImage object was created
        encoded_image = EncodedImage.objects.first()
        self.assertIsNotNone(encoded_image)

    def test_decode_image_api(self):
        # Encode an image with a message for testing
        encoded_image = EncodedImage.objects.create(
            image=self.sample_image,
            message='Hello, steganography!'
        )

        client = APIClient()

        # Test decoding API endpoint
        response = client.get(f'/api/decodeimage/')
        self.assertEqual(response.status_code, 200)  # 200 OK

        # Verify the decoded message
        expected_message = 'Hello, steganography!'
        self.assertEqual(response.data['message'], expected_message)

    def tearDown(self):
        # Clean up created files
        EncodedImage.objects.all().delete()

        # Clean up sample image file
        self.sample_image.close()
