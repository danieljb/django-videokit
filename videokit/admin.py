
from django.contrib.contenttypes import generic
from django.contrib import messages
from django.contrib import admin

from django.utils.translation import ugettext_lazy as _

from videokit.models import EncodingStatus
from videokit.production.models import EncodingSpecificationBase, EncodingFilterScaling, EncodingFilterCropping


def process_encodingmodel(modeladmin, request, queryset):
    status = []
    for obj in queryset:
        s = obj.process()
        if s:
            messages.success(request, _("Successfully processed %s") % str(obj))
        else:
            messages.error(request, _("Error processing %s") % str(obj))
    
process_encodingmodel.short_description = _("Process videos with specifications from marked instances.")


class EncodingStatusInlineAdmin(generic.GenericStackedInline):
    model = EncodingStatus
    ct_field = 'content_type'
    ct_fk_field = 'object_id'
    
    fieldsets = (
        ('Status', {
            'fields': ('status', ('task_id', 'specification'), 'creation_date', 'protocoll', 'content_type', 'object_id',),
        }),
    )
    
    extra = 1
    max_count = 1
    
    readonly_fields = ('status', 'task_id', 'specification', 'creation_date', 'protocoll', 'content_type', 'object_id',)
    

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
    

class EncodingSpecificationBaseAdmin(admin.ModelAdmin):
    
    inlines = [
        EncodingFilterScalingInlineAdmin,
        EncodingFilterCroppingInlineAdmin,
    ]
    
    prepopulated_fields = {'identifier': ('name',),}
    readonly_fields = ('creation_date',)
    
    def save_model(self, request, obj, form, change):
        if not obj.identifier:
            obj.identifier = slugify(obj.name)
        super(EncodingSpecificationBaseAdmin, self).save_model(request, obj, form, change)
    
