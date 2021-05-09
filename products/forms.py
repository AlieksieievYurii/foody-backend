from django.core.exceptions import ValidationError
from django.forms import ModelForm

from products.models import ProductImage


class ProductImageForm(ModelForm):
    def clean_is_default(self):
        if self.cleaned_data['is_default'] and ProductImage.objects.filter(product=self.cleaned_data['product'],
                                                                           is_default=True):
            raise ValidationError('Image with "default image" already exist', code='invalid')
        return self.instance.is_default

    class Meta:
        model = ProductImage
        fields = '__all__'
