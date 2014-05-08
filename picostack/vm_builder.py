from picostack.process_spawn import invoke
from picostack.textwrap_util import wrap_multiline


class VmBuilder(object):

    def get_build_jeos_call(self):
        return wrap_multiline('''
            sudo vmbuilder kvm ubuntu --suite quantal --flavour virtual
                --arch i386 -o --libvirt qemu:///system
                --bridge %(bridge_interface)s
                --addpkg linux-image-generic
        ''' % {
            'bridge_interface': 'br0',
        })

    def build_jeos(self):
        print 'Building ubuntu JeOS..'
        command = self.get_build_jeos_call()
        print '"%s"' % command
        print invoke(command)
