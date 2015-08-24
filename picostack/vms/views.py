import urllib
from urlparse import urlparse
from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django import forms
from django.forms.models import modelformset_factory, ModelForm
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from picostack.vms.models import (VmInstance, VM_IS_LAUNCHED,
                                  VM_IS_TERMINATING, VM_IS_TRASHED)
import picostack.settings


class VmInstanceForm(ModelForm):
    class Meta:
        model = VmInstance
        fields = [
            'name', 'current_state', 'image', 'flavour',
            'has_ssh', 'has_rdp', 'has_vnc',
            # 'ssh_mapping', 'rdp_mapping', 'vnc_mapping',
        ]


DefaultVmInstancesFormSet = modelformset_factory(model=VmInstance,
                                                 form=VmInstanceForm,
                                                 # No empty forms..
                                                 extra=0)


class VmInstancesFormSet(DefaultVmInstancesFormSet):

    def enumerate_forms(self):
        return enumerate(self.forms)


def get_vm_instance(request, submit_id):
    # Initialize form set and pick the index.
    formset = VmInstancesFormSet(
        request.POST, request.FILES,
        queryset=VmInstance.objects.all(),
    )
    form_index = int(request.POST[submit_id][len(submit_id):])
    assert form_index < len(formset.forms) and form_index >= 0
    # Obtain corresponding model instance without saving anything.
    form = formset.forms[form_index]
    assert form.is_valid()
    return form.save(commit=False)


def get_view_context():
    # Instantiate form for each instance to pass to template.
    vm_instances_formset = VmInstancesFormSet()
    # Make list of column headers for the template.
    columns = list()
    if vm_instances_formset.total_form_count() > 0:
        columns = [field.label_tag for field
                   in vm_instances_formset.forms[0].visible_fields()]
    return {
        'formset': vm_instances_formset,
        'columns': columns,
    }


def get_novnc_prefix(request):
    # Build NOVNC URL
    abs_url = request.build_absolute_uri('/')
    parsed_url = urlparse(abs_url)
    novnc_params = picostack.settings.NOVNC_PARAMS
    netloc = parsed_url.netloc
    params = {}
    params['host'] = parsed_url.hostname
    if novnc_params['sockify_port'] is not None:
        params['port'] = novnc_params['sockify_port']
    novnc_url = '{scheme}://{netloc}/{path}{params}'.format(
        scheme=parsed_url.scheme,
        netloc=netloc,
        path='novnc',
        params='?%s&%s' % (urllib.urlencode(params),
                           urllib.urlencode({'path': 'websockify?token='}))
    )
    return novnc_url


#
# Views
#
def logout_view(request):
    logout(request)
    return HttpResponseRedirect('/instances/')


def get_connection_details(request):
    if 'name' not in request.GET:
        raise Exception('Missing instance name')
    try:
        vm_instance = VmInstance.objects.get(name=request.GET['name'])
    except VmInstance.DoesNotExist:
        return HttpResponse('# Error. VM was not found by name: %s' %
                            request.GET['name'])
    hostname = request.get_host()
    if ':' in hostname:
        hostname = hostname[:hostname.index(':')]

    connection_str = 'ssh -T %s' % hostname
    port_mapping_template = '-L %d:localhost:%d'
    mappings = list()
    if vm_instance.has_vnc:
        mappings.append(port_mapping_template %
                        (vm_instance.vnc_mapping,
                         vm_instance.vnc_mapping))
    if vm_instance.has_ssh:
        mappings.append(port_mapping_template %
                        (vm_instance.ssh_mapping,
                         vm_instance.ssh_mapping))
    if vm_instance.has_rdp:
        mappings.append(port_mapping_template %
                        (vm_instance.rdp_mapping,
                         vm_instance.rdp_mapping))
    return HttpResponse(' '.join([connection_str] + mappings + ['\n']))


@login_required
def manage_instances(request):
    # TODO: handle errors
    # If the form has been submitted, handle the POST request per action.
    if request.method == 'POST':
        if '_save' in request.POST:
            formset = VmInstancesFormSet(
                request.POST, request.FILES,
                queryset=VmInstance.objects.all(),
            )
            if formset.is_valid():
                formset.save()  # FIXME: do we need to save?
        elif '_start' in request.POST:
            vm_instance = get_vm_instance(request, submit_id='_start')
            # Schedule VM for start.
            vm_instance.change_state(VM_IS_LAUNCHED)
        elif '_stop' in request.POST:
            vm_instance = get_vm_instance(request, submit_id='_stop')
            # Schedule VM for stop.
            vm_instance.change_state(VM_IS_TERMINATING)
        elif '_trash' in request.POST:
            vm_instance = get_vm_instance(request, submit_id='_trash')
            # Schedule VM for complete removal.
            vm_instance.change_state(VM_IS_TRASHED)
        return HttpResponseRedirect('/instances/')
    # Otherwise view instances. Render the template as response.
    return render(request, 'instances/view.html', get_view_context())


@login_required
def list_instances(request):
    # Render the template as response.
    context = get_view_context()
    context.update({
        'connect_url': request.build_absolute_uri('/connect_instance/'),
        'novnc_url': get_novnc_prefix(request),
    })
    return render(request, 'instances/list.html', context)


@login_required
def novnc(request):
    return render(request, 'novnc.html', {})
