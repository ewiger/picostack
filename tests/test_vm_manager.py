'''
Quick start with nose tests:

 sudo pip install nose
 cd tests/
 nosetests

'''
import os
import sys
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "picostack.settings")
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from picostack import vm_manager


def test_call_builder():
    ubuntu_kvm_builder = vm_manager.UbuntuKvm()
    call_str = ubuntu_kvm_builder.build_params()
    print call_str
    expected_str = '-usbdevice tablet -ballon virtio -boot c -m %(memory_size'\
        ')s -smp %(num_of_cores)s,cores=%(num_of_cores)s,sockets=1,threads=1'\
        ' -machine accel=kvm -no-shutdown  -hda %(disk_path)s -net user -net '\
        'nic,model=virtio -net nic,model=virtio -cpu qemu64'
    assert expected_str == call_str

