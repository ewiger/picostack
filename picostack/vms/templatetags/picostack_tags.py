from django import template
import picostack


register = template.Library()


@register.simple_tag
def picostack_version():
    return picostack.__version__
