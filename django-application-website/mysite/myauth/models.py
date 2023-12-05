from django.db import models
from django.contrib.auth.models import User


def avatar_directory_path(instance: "Profile", filename: str) -> str:
    return "profile/profile_{pk}/avatar/{filename}".format(
        pk=instance.user.pk,
        filename=filename,
    )


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    city = models.CharField(max_length=36, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    avatar = models.ImageField(null=True, blank=True, upload_to=avatar_directory_path)

