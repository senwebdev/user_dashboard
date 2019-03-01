from django import forms
from django.contrib import admin
from django.contrib.admin.sites import NotRegistered
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from django.contrib.auth.models import User
from django.contrib.auth import admin as upstream
from django.core.validators import URLValidator

from haiku.env_settings import SITE_URL
from . import models


class EmailRequiredMixin(object):
    def __init__(self, *args, **kwargs):
        super(EmailRequiredMixin, self).__init__(*args, **kwargs)
        # make user email field required
        self.fields['email'].required = True


class MyUserCreationForm(EmailRequiredMixin, UserCreationForm):
    pass


class MyUserChangeForm(EmailRequiredMixin, UserChangeForm):
    pass


class UserAdmin(upstream.UserAdmin):
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2', 'email', 'first_name', 'last_name')}
         ),
    )
    form = MyUserChangeForm
    add_form = MyUserCreationForm
    list_display = ('username', 'email', 'activation_link',)

    def activation_link(self, obj):
        return SITE_URL + '/activation?token=' + str(obj.token.token)


class TemplateFieldsInline(admin.TabularInline):
    model = models.TemplateFields
    extra = 1


class TemplateForm(forms.ModelForm):
    class Meta:
        model = models.Template
        exclude = ['id']

    def clean(self):

        image_url = self.cleaned_data.get('image_url')
        server_image = self.cleaned_data.get('server_image')
        server_image_checkbox = self.cleaned_data.get('file_from_server')
        if not image_url and not server_image:
            self.add_error(None, 'Template must have Image URL or Server Image filled')

        if not image_url and server_image and not server_image_checkbox:
            self.add_error('file_from_server', 'If you want to use image from server, please click on this checkbox')

        if server_image_checkbox and not server_image:
            self.add_error('server_image',
                           'Show file from server as picture checkbox is filled but you didn\'t input any server image')

        template_url = self.cleaned_data.get('template_url') # Added for demo

        if image_url:
            validate = URLValidator()
            try:
                validate(image_url)
            except forms.ValidationError:
                self.add_error('image_url', 'This is not correct url.')

        video_url = self.cleaned_data.get('video_url')
        if video_url:
            validate = URLValidator()
            try:
                validate(video_url)
            except forms.ValidationError:
                self.add_error('video_url', 'This is not correct url.')

        return self.cleaned_data


class TemplateAdmin(admin.ModelAdmin):
    form = TemplateForm
    inlines = [
        TemplateFieldsInline,
    ]


try:
    admin.site.unregister(User)
except NotRegistered:
    pass

admin.site.register(User, UserAdmin)
admin.site.register(models.Category)
admin.site.register(models.Template, TemplateAdmin)
