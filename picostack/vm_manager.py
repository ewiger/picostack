

class VmManager(object):

    def build_machines(self):
        pass

    def start_machines(self):
        pass

    def stop_machines(self):
        pass

    def destory_machines(self):
        pass

    def run_machine(self, machine):
        raise NotImplementedError()

    def stop_machine(self, machine):
        raise NotImplementedError()

    def clone_image(self, vm_image):
        raise NotImplementedError()

    def remove_image(self, vm_image):
        raise NotImplementedError()


class Kvm(VmManager):

    def run_machine(self, machine):
        raise NotImplementedError()

    def stop_machine(self, machine):
        raise NotImplementedError()

    def clone_image(self, vm_image):
        raise NotImplementedError()

    def remove_image(self, vm_image):
        raise NotImplementedError()
