from django.db import models




class EncodedImage(models.Model):
    image = models.ImageField(upload_to='images/')
    message = models.TextField()

    def __str__(self):
        return f"EncodedImage id={self.id}"
