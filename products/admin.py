from django.contrib import admin
from .models import Category, Product, NewsletterSubscriber
from .forms import ProductForm
from django.utils.html import format_html
from django.db.models import Count
from sorl.thumbnail import get_thumbnail

@admin.register(NewsletterSubscriber)
class NewsletterAdmin(admin.ModelAdmin):
    list_display = ("email", "subscribed_at")
    search_fields = ("email",)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'product_count')
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.annotate(_product_count=Count('products'))  # requires related_name='products'

    def product_count(self, obj):
        return obj._product_count

    product_count.admin_order_field = '_product_count'
    product_count.short_description = 'Products'


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    form = ProductForm  # Uses your custom form
    prepopulated_fields = {'slug': ('name',)}
    list_display = (
        'name',
        'category',
        'price',
        'stock',
        'image_preview',
        'available',
        'created_at',
        "is_featured",
    )
    list_filter = ('category', 'available', 'created_at',"is_featured")
    search_fields = ('name',)
    list_editable = ('price', 'stock', 'available',"is_featured")
    readonly_fields = ('image_preview', 'created_at', 'updated_at')
    date_hierarchy = 'created_at'
    fieldsets = (
        (None, {
            'fields': ('name', 'slug', 'category', 'description','image')
        }),
        ('Pricing', {
            'fields': ('price', 'stock')
        }),
        ('Status', {
            'fields': ('available',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )

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

    # For better UX in large databases
    autocomplete_fields = ['category']
    show_full_result_count = False


