from django.contrib import admin
from picostack.vms.models import Flavour, VmImage, VmInstance


class VmInstanceAdmin(admin.ModelAdmin):
    pass


admin.site.register(Flavour)
admin.site.register(VmImage)
admin.site.register(VmInstance, VmInstanceAdmin)

