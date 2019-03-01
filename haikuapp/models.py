from uuid import uuid4
from django.db import models
from django.contrib.auth.models import User, Group
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from haiku.settings import SITE_URL

User._meta.get_field('email')._unique = True


class Category(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=255, unique=True)
    description = models.CharField(max_length=255)
    image_url = models.ImageField(null=True, blank=True, upload_to='category')

    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.title

    def get_image_url(self):
        if self.image_url:
            return self.image_url.url
        else:
            return None


class Template(models.Model):
    UPLOAD_AMOUNT = (
        (0, 'No picture upload'),
        (1, 'Single picture upload'),
        (2, 'Multiple picture upload')
    )

    UPLOAD_REQUIRED = (
        (0, 'Picture upload not required'),
        (1, 'Picture upload required')
    )

    VERTICALS = (
        ('generic', 'generic'),
        ('gym', 'gym'),
        ('pharma', 'pharma'),
        ('food', 'food')
    )

    id = models.AutoField(primary_key=True)
    vertical = models.CharField(max_length=255, default='text', choices=VERTICALS)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    template_name = models.CharField(null=True, max_length=500, blank=True)
    description = models.CharField(max_length=255)
    server_image = models.ImageField(null=True, blank=True, upload_to='template')
    image_url = models.CharField(null=True, max_length=500, blank=True)
    preview_url = models.CharField(null=True, max_length=500, blank=True)
    file_from_server = models.BooleanField(default=True, verbose_name='Show file from server as picture')
    video_url = models.CharField(null=True, max_length=500, blank=True)
    upload_amount = models.IntegerField(default=0, null=False, choices=UPLOAD_AMOUNT)
    upload_required = models.BooleanField(default=True, choices=UPLOAD_REQUIRED)

    def __str__(self):
        return self.title

    def template_picture(self):
        if self.file_from_server and self.server_image:
            return self.server_image.url
        else:
            return self.image_url

  #Added for demo testing
    def template_video(self):
        return self.video_url
  #Added for demo testing
    def template_url(self):
        return self.preview_url


class TemplateFields(models.Model):
    VARIABLE_TYPE = (
        ('textarea', 'Textarea'),
        ('text', 'Text'),
        ('checkbox', 'Checkbox'),
        ('radio', 'Radio'),
        ('date', 'Date'),
        ('time', 'Time'),
        ('number', 'Number'),
        ('color', 'Color'),
        ('range', 'Range'),
        ('image', 'Image'),
        ('video', 'Video')
    )

    VARIABLE_REQUIRED = (
        (0, 'Not required'),
        (1, 'Required')
    )
    
    id = models.AutoField(primary_key=True)
    template = models.ForeignKey(Template, on_delete=models.CASCADE, related_name='fields')
    name = models.CharField(max_length=255)
    variable = models.CharField(max_length=255)
    varType = models.CharField(max_length=255, default='text', choices=VARIABLE_TYPE)
    varRequired = models.BooleanField()

    def __str__(self):
        return self.name


class Card(models.Model):
    
    id = models.AutoField(primary_key=True)
    template = models.ForeignKey(Template, on_delete=models.CASCADE)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, default=0)
    date_from = models.DateField(null=True, blank=True)
    date_to = models.DateField(null=True, blank=True)
    time_from = models.TimeField(null=True, blank=True)
    time_to = models.TimeField(null=True, blank=True)
    user_input = models.TextField(null=True, blank=True)


    def __str__(self):
        return str(self.id)


class CardField(models.Model):
    id = models.AutoField(primary_key=True)
    card = models.ForeignKey(Card, on_delete=models.CASCADE, related_name='fields')
    template_field = models.ForeignKey(TemplateFields, on_delete=models.CASCADE)
    variable = models.CharField(max_length=255)
    value = models.CharField(max_length=255)

    def __str__(self):
        return self.value


class ImageCard(models.Model):
    id = models.AutoField(primary_key=True)
    card = models.ForeignKey(Card, on_delete=models.CASCADE, related_name='images')
    image_url = models.ImageField(null=True, blank=True, upload_to='images')

    def __str__(self):
        return str(self.id)

    def get_image_url(self):
        if self.image_url:
            return self.image_url.url
        else:
            return None



class UserActivate(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, unique=True, related_name='token')
    token = models.CharField(max_length=255, unique=True, blank=False, null=False)

    def activation_link(self):
        return SITE_URL + '/activation?token=' + str(self.token)

    def __str__(self):
        return str(self.id)


@receiver(pre_save, sender=User)
def set_new_user_inactive(sender, instance, **kwargs):
    if instance._state.adding is True and instance.is_superuser is False:
        instance.is_active = False


@receiver(post_save, sender=User)
def save_profile(sender, instance, created, **kwargs):
    user = instance
    if created:
        us = UserActivate(user=user)
        us.user = user
        us.token = uuid4()
        us.save()
        instance.groups.add(Group.objects.get(name='generic'))