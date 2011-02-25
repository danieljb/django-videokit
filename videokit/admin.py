
from django.contrib import admin
from django.contrib.contenttypes import generic

from videokit.models import EncodingPreset, EncodingFilterScaling, EncodingFilterCropping


class EncodingFilterScalingInlineAdmin(admin.StackedInline):
    model = EncodingFilterScaling
    
    fieldsets = (
        ('Definition', {
            'fields': (('width', 'height'),),
        }),
    )
    
    extra = 1
    max_count = 1
    

class EncodingFilterCroppingInlineAdmin(admin.StackedInline):
    model = EncodingFilterCropping

    fieldsets = (
        ('Definition', {
            'fields': (('left', 'right',), ('top', 'bottom',)),
        }),
    )

    extra = 1
    max_count = 1
    

class EncodingPresetAdmin(admin.ModelAdmin):
    
    inlines = [
        EncodingFilterScalingInlineAdmin,
        EncodingFilterCroppingInlineAdmin,
    ]
    
    list_display = ('title', 'slug',)
    
    fieldsets = (
        ('Filter', {
            'fields': (('title', 'slug',), 'output_file',)
        }),
        ('Meta', {
            'classes': ('collapse',),
            'fields': ('creation_date',),
        })
    )
    
    prepopulated_fields = {'slug': ('title',),}
    readonly_fields = ('creation_date',)
    
    def save_model(self, request, obj, form, change):
        if not obj.slug:
            obj.slug = slugify(obj.title)
        super(EncodingPresetAdmin, self).save_model(request, obj, form, change)
    

admin.site.register(EncodingPreset, EncodingPresetAdmin)