from django.shortcuts import render
from django.http import HttpResponseRedirect
from django import forms
from django.forms.models import modelformset_factory, ModelForm
from picostack.vms.models import (VmInstance, VM_IS_LAUNCHED,
                                  VM_IS_TERMINATING, VM_IS_TRASHED)


class VmInstanceForm(ModelForm):
    class Meta:
        model = VmInstance
        fields = [
            'name', 'current_state', 'image', 'flavour',
            'has_ssh', 'has_rdp', 'has_vnc',
            #'ssh_mapping', 'rdp_mapping', 'vnc_mapping',
        ]
    #current_state = forms.ChoiceField(widget = forms.TextInput(attrs={'readonly':'readonly'}))


def manage_instances(request):
    VmInstancesFormSet = modelformset_factory(model=VmInstance,
                                              form=VmInstanceForm,
                                              # No empty forms..
                                              extra=0)
    def get_vm_instance(submit_id):
        # Initialize form set and pick the index.
            formset = VmInstancesFormSet(
                request.POST, request.FILES,
                queryset=VmInstance.objects.all(),
            )
            form_index = int(request.POST[submit_id][len(submit_id):]) - 1
            assert form_index < len(formset.forms) and form_index >= 0
            # Obtain corresponding model instance without saving anything.
            form = formset.forms[form_index]
            assert form.is_valid()
            return form.save(commit=False)
            # Submit VM for launching.
            vm_instance.change_state(VM_IS_LAUNCHED)
    # If the form has been submitted...
    # TODO: handle errors
    if request.method == 'POST':
        if '_save' in request.POST:
            formset = VmInstancesFormSet(
                request.POST, request.FILES,
                queryset=VmInstance.objects.all(),
            )
            if formset.is_valid():
                formset.save()  # FIXME: do we need to save?
        elif '_start' in request.POST:
            vm_instance = get_vm_instance(submit_id='_start')
            # Schedule VM for start.
            vm_instance.change_state(VM_IS_LAUNCHED)
        elif '_stop' in request.POST:
            vm_instance = get_vm_instance(submit_id='_stop')
            # Schedule VM for stop.
            vm_instance.change_state(VM_IS_TERMINATING)
        elif '_trash' in request.POST:
            vm_instance = get_vm_instance(submit_id='_trash')
            # Schedule VM for complete removal.
            vm_instance.change_state(VM_IS_TRASHED)
        return HttpResponseRedirect('/instances/')

    else:
        vm_instances_formset = VmInstancesFormSet()
        columns = list()
        if vm_instances_formset.total_form_count() > 0:
            columns = [field.label_tag for field
                       in vm_instances_formset.forms[0].visible_fields()]

    return render(request, 'instances.html', {
        'formset': vm_instances_formset,
        'columns': columns,
    })
