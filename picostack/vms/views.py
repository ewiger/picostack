from django.shortcuts import render
from django import forms
from django.http import HttpResponseRedirect


class InstancesForm(forms.Form):
    subject = forms.CharField(max_length=100)
    message = forms.CharField()
    sender = forms.EmailField()
    cc_myself = forms.BooleanField(required=False)


def instances(request):
    # If the form has been submitted...
    if request.method == 'POST':
        # ContactForm was defined in the previous section
        form = InstancesForm(request.POST)  # A form bound to the POST data
        if form.is_valid():  # All validation rules pass
            # Process the data in form.cleaned_data
            # ...
            return HttpResponseRedirect('/thanks/')  # Redirect after POST
    else:
        form = InstancesForm()  # An unbound form

    return render(request, 'instances.html', {
        'form': form,
    })
