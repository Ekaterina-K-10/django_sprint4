from django.contrib import admin
from blog.models import Category, Location, Post, Comment


# Register your models here.
admin.site.register(Category)
admin.site.register(Location)
admin.site.register(Post)
admin.site.register(Comment)
