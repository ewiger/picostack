import os
import sys
import unittest

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "picostack.settings")
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from django.test import TestCase
from picostack.vms.models import Flavour, VmImage, VmInstance


class InstanceTestCase(TestCase):

    def setUp(self):
        vm_image = VmImage.objects.create(
            name='test_image',
            image_filename='test.img',
            disk_size=10,
        )
        vm_image.save()
        flavour = Flavour.objects.create(name='tiny')
        flavour.save()
        machine = VmInstance(
            name='test_vm',
            image=vm_image,
            flavour=flavour,
        )
        machine.save()

    def test_vm_basic(self):
        for machine in VmInstance.objects.all():
            #print machine.name
            assert machine.num_of_cores > 0

    def test_get_occupied_ports(self):
        # Make sure we have at least 1 mapped port.
        machine = VmInstance.objects.get(name='test_vm')
        machine.current_state = 'Running'
        machine.has_ssh = True
        machine.map_port('ssh', 10020)
        machine.save()
        # Test the routine.
        occupied_ports = VmInstance.get_all_occupied_ports()
        assert len(occupied_ports) > 0
        #print occupied_ports


if __name__ == "__main__":
    unittest.main()
