from django.shortcuts import render
from django.http import HttpResponseRedirect
from django import forms
from django.forms.models import modelformset_factory, ModelForm
from picostack.vms.models import VmInstance


class VmInstanceForm(ModelForm):
    class Meta:
        model = VmInstance
        fields = ['name', 'current_state', 'image', 'flavour']
    #current_state = forms.ChoiceField(widget = forms.TextInput(attrs={'readonly':'readonly'}))


def manage_instances(request):
    VmInstancesFormSet = modelformset_factory(model=VmInstance,
                                              form=VmInstanceForm,
                                              # No empty forms..
                                              extra=0)
    # If the form has been submitted...
    if request.method == 'POST':
        # Process the data in form.cleaned_data
        # ...
        if '_save' in request.POST:
            return HttpResponseRedirect('/save/')
        elif '_start' in request.POST:
            return HttpResponseRedirect('/start/')
        elif '_stop' in request.POST:
            return HttpResponseRedirect('/stop/')
        elif '_trash' in request.POST:
            return HttpResponseRedirect('/trash/')
        return HttpResponseRedirect('/thanks/')  # Redirect after POST
        # # ContactForm was defined in the previous section
        # form = VmInstanceForm(request.POST)  # A form bound to the POST data
        # # if form.is_valid():  # All validation rules pass
        # return HttpResponseRedirect('/trash/')
    else:
        vm_instances_formset = VmInstancesFormSet()
        columns = list()
        if vm_instances_formset.total_form_count > 0:
            columns = [field.label_tag for field
                       in vm_instances_formset.forms[0].visible_fields()]

    return render(request, 'instances.html', {
        'formset': vm_instances_formset,
        'columns': columns,
    })
