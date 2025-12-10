from django.contrib import admin
from blog.models import Category, Location, Post


# Register your models here.
admin.site.register(Category)
admin.site.register(Location)
admin.site.register(Post)
