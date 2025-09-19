from django.contrib import admin

from .models import Product, Category, ProductImage


# Register your models here.
class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 5


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'price', 'available', 'created', 'updated', 'discount', 'description']
    list_filter = ['available', 'created', 'updated']
    list_editable = ['price', 'available', 'discount', 'description']
    prepopulated_fields = {'slug': ('name',)}
    inlines = [ProductImageInline]


