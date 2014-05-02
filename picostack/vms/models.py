from django.db import models

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
    'ssh': '22',
    'vnc': '5900',
    'rdp': '3389',
}


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
    ssh_mapping = models.PositiveSmallIntegerField(null=True)

    # has VNC ?
    has_vnc = models.BooleanField(default=False)

    # Set by vm_manager
    vnc_mapping = models.PositiveSmallIntegerField(null=True)

    # has RDP ? Set True for Windows.
    has_rdp = models.BooleanField(default=False)

    # Set by vm_manager
    rdp_mapping = models.PositiveSmallIntegerField(null=True)

    def change_state(self, state):
        self.current_state = state
        self.save(force_update=True)

    @staticmethod
    def get_all_occupied_ports():
        '''Get all ports occupied by running VM instances.'''
        port_mappings = list()
        for machine in VmInstance.objects.filter(current_state='Running'):
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

    @property
    def disk_filename(self):
        return '%s_%s.dsk' % (self.image.image_filename, self.name)

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

    def __repr__(self):
        return 'VM instance <%s> (flavour: %s, image: %s) ' % (
            self.name, self.flavour.name, self.image.name)

    def __str__(self):
        return '%s (%s, %s)' % (
            self.name, self.flavour.name, self.image.name)
