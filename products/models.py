from django.db import models
from django.core.validators import MinValueValidator
from django.utils.text import slugify
from django.utils.html import format_html
from sorl.thumbnail import get_thumbnail
from django.urls import reverse

class NewsletterSubscriber(models.Model):
    email = models.EmailField(unique=True)
    subscribed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ['name']

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name='products',
        null=True,  # Temporary to handle existing data
        blank=True  # Allows empty in forms
    )
    description = models.TextField()
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0.01)]
    )
    image = models.ImageField(upload_to='product_images/', blank=True, null=True)
    stock = models.PositiveIntegerField(default=0)
    available = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    def image_preview(self, obj):
        if obj.image:
            try:
                # Create or retrieve a cached 50x50 thumbnail
                thumb = get_thumbnail(obj.image, '50x50', crop='center', quality=80)
                return format_html('<img src="{}" width="50" height="50" />', thumb.url)
            except Exception:
                return "(Invalid image)"
        return "(No image)"

    image_preview.short_description = 'Preview'

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("products:detail_with_slug", kwargs={"pk": self.pk, "slug": self.slug})

# Meta is an inner class inside a Django model used to configure metadata (extra settings) for that model.
    class Meta:
        ordering = ['-created_at'] # Always orders products by newest first in queries.
        verbose_name_plural = "Products" # Shows "Products" as the plural name in Django admin.

# Automatically generates a URL slug from the product name if it’s missing.
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)