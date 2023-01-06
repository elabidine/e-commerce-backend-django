from core.models import User
from store.models import Product
from django.contrib import admin
from django.contrib.contenttypes.admin import GenericTabularInline
from store.admin import ProductAdmin, ProductAdminImage
from tags.models import TaggedItem
from django.contrib.auth.admin import UserAdmin as BaseUseer

@admin.register(User)
class UserAdmin(BaseUseer):
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("username", "password1", "password2","email","first_name","last_name"),
            },
        ),
    )

class TagInline(GenericTabularInline):
    autocomplete_fields = ['tag']
    model = TaggedItem


class CustomProductAdmin(ProductAdmin):
    inlines = [TagInline,ProductAdminImage]


admin.site.unregister(Product)
admin.site.register(Product, CustomProductAdmin)
