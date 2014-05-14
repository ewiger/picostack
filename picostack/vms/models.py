from django.db import models
from picostack.errors import DataModelError


VM_IN_CLONING = 'C'
# After cloning instance state is set to 'stopped'
VM_IS_STOPPED = 'S'
VM_IS_LAUNCHED = 'L'
VM_IS_RUNNING = 'R'
VM_HAS_FAILED = 'F'
VM_IS_TERMINATING = 'T'
VM_IS_TRASHED = 'W'
# If instance is removed, it has no state but is just deleted from the DB.

VM_STATES = (
    (VM_IN_CLONING, 'InCloning'),
    (VM_IS_STOPPED, 'Stopped'),
    (VM_IS_RUNNING, 'Running'),
    (VM_IS_LAUNCHED, 'Launched'),
    (VM_HAS_FAILED, 'Failed'),
    (VM_IS_TERMINATING, 'Terminating'),
    (VM_IS_TRASHED, 'Trashed'),
)

VM_PORTS = {
    'ssh': 22,
    'vnc': 5900,
    'rdp': 3389,
}

DEFAULT_FLAVOUR = 'tiny'


class VmImage(models.Model):

    name = models.CharField(max_length=60, unique=True)

    image_filename = models.CharField(max_length=120)

    # Used to check if we have enough free space when cloning (in MB).
    disk_size = models.PositiveIntegerField()

    def __repr__(self):
        return 'VM Image: <%s>' % self.name

    def __str__(self):
        return self.name


class Flavour(models.Model):

    name = models.CharField(max_length=60, unique=True)

    # in Megabytes
    memory_size = models.PositiveIntegerField(default=1024)

    # Number of cores
    num_of_cores = models.PositiveSmallIntegerField(default=1)

    def __repr__(self):
        return 'VM Flavour: <%s>' % self.name

    def __str__(self):
        return self.name


class VmInstance(models.Model):

    name = models.CharField(max_length=60, unique=True)

    image = models.ForeignKey(VmImage, related_name='instances')

    flavour = models.ForeignKey(Flavour, related_name='instances')

    current_state = models.CharField(
        max_length=1, choices=VM_STATES, default=VM_IN_CLONING)

    @property
    def memory_size(self):
        return self.flavour.memory_size

    @property
    def num_of_cores(self):
        return self.flavour.num_of_cores

    # has SSH ?
    has_ssh = models.BooleanField(default=False)

    # Set by vm_manager
    ssh_mapping = models.PositiveSmallIntegerField(null=True, blank=True)

    # has VNC ?
    has_vnc = models.BooleanField(default=False)

    # Set by vm_manager
    vnc_mapping = models.PositiveSmallIntegerField(null=True, blank=True)

    # has RDP ? Set True for Windows.
    has_rdp = models.BooleanField(default=False)

    # Set by vm_manager
    rdp_mapping = models.PositiveSmallIntegerField(null=True, blank=True)

    # Vnc port in '-vnc localhost:'
    localhost_vnc_port = models.PositiveSmallIntegerField(null=True,
                                                          blank=True)

    # If left blank, then the value from get_default_disk_filename() is used.
    disk_filename = models.CharField(max_length=120, null=True, blank=True)

    def change_state(self, state):
        self.current_state = state
        self.save(force_update=True)

    @staticmethod
    def get_all_occupied_ports():
        '''Get all ports occupied by running VM instances.'''
        port_mappings = list()
        for machine in VmInstance.objects.filter(current_state=VM_IS_RUNNING):
            ports = [
                machine.ssh_mapping,
                machine.vnc_mapping,
                machine.rdp_mapping,
            ]
            port_mappings.extend([port for port in ports
                                  if port is not None])
        return port_mappings

    def map_port(self, vm_port, host_port):
        if vm_port == 'ssh':
            assert self.has_ssh
            self.ssh_mapping = host_port
        elif vm_port == 'rdp':
            assert self.has_rdp
            self.rdp_mapping = host_port
        elif vm_port == 'vnc':
            assert self.has_vnc
            self.vnc_mapping = host_port
        else:
            raise Exception('Trying to map unknown port: %s' % vm_port)
        self.save(force_update=True)

    def get_default_disk_filename(self):
        return '%s_%s.dsk' % (self.image.image_filename, self.name)

    def get_default_localhost_vnc_port(self):
        allocated_ports = [machine.localhost_vnc_port for machine
                           in VmInstance.objects.all()]
        for port in range(1, VmInstance.objects.count()):
            if not port in allocated_ports:
                return port
        return VmInstance.objects.count() + 1

    def stop(self):
        # Reset/free all port mappings.
        self.ssh_mapping = None
        self.vnc_mapping = None
        self.rdp_mapping = None
        # Update state.
        self.current_state = 'Stopped'
        self.save(force_insert=True)

    @staticmethod
    def prepare_for_cloning(machine_name, vm_image, flavour):
        # Create a new instance.
        machine = VmInstance.objects.create(name=machine_name,
                                            image=vm_image,
                                            current_state='InCloning',
                                            flavour=flavour)
        machine.save()
        return machine

    @staticmethod
    def build_vm(vm_name, image_name, flavour_name=DEFAULT_FLAVOUR):
        vm_image = VmImage.objects.get(name=image_name)
        if not vm_image:
            raise DataModelError('VM image does not exists: %s' % image_name)
        flavour = Flavour.objects.get(name=flavour_name)
        if not flavour:
            raise DataModelError('VM flavour does not exists: %s' %
                                 flavour_name)
        if VmInstance.objects.filter(name=vm_name).exists():
            raise DataModelError('VM instance with this name already exists.')
        machine = VmInstance(
            name=vm_name,
            image=vm_image,
            flavour=flavour,
        )
        machine.save()

    # Some representation and casting implementation.
    def __repr__(self):
        return 'VM instance <%s> (flavour: %s, image: %s) ' % (
            self.name, self.flavour.name, self.image.name)

    def __str__(self):
        return '%s (%s, %s)' % (
            self.name, self.flavour.name, self.image.name)

    def save(self, *args, **kwargs):
        if self.disk_filename is None or self.disk_filename == '':
            self.disk_filename = self.get_default_disk_filename()
        if self.localhost_vnc_port is None or self.localhost_vnc_port == 0:
            self.localhost_vnc_port = self.get_default_localhost_vnc_port()
        super(VmInstance, self).save(*args, **kwargs)
