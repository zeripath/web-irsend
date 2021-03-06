from subprocess import call
import fileinput
import glob
import re


class Lirc:
    """
    Parses the lircd.conf file and can send remote commands through irsend.
    """
    codes = {}

    def __init__(self, conf):
        # Open the config file and directory
        conflist = [conf]
        conflist.extend(glob.glob(conf+".d/*.conf"))
        self.conf = fileinput.input(conflist, mode='r')

        # Parse the config file
        self.parse()
        self.conf.close()

    @property
    def devices(self):
        """
        Return a list of devices.
        """
        return self.codes.keys()

    def parse(self):
        """
        Parse the lircd.conf config file and create a dictionary.
        """
        remote_name = None
        codes_section = False
        raw_codes_section = False

        for line in self.conf:
            # Convert (multiple) tabs to spaces
            line = re.sub(r'[ \t]+', ' ', line)
            # Remove comments
            line = re.sub(r'#.*', '', line)
            # Remove surrounding whitespaces
            line = line.strip()

            # Look for a 'begin remote' line
            if line == 'begin remote':
                # Got the start of a remote definition
                remote_name = None
                codes_section = False
                raw_codes_section = False

            elif not remote_name and line.startswith('name '):
                # Got the name of the remote
                remote_name = line.split(' ')[1]
                if remote_name not in self.codes:
                    self.codes[remote_name] = set()

            elif remote_name and line == 'end remote':
                # Got to the end of a remote definition
                remote_name = None

            elif remote_name and line == 'begin codes':
                codes_section = True

            elif remote_name and line == 'end codes':
                codes_section = False

            elif remote_name and line == 'begin raw_codes':
                raw_codes_section = True

            elif remote_name and line == 'end raw_codes':
                raw_codes_section = False

            elif remote_name and codes_section:
                fields = line.split(' ')
                self.codes[remote_name].add(fields[0])

            elif remote_name and raw_codes_section:
                fields = line.split(' ')
                if len(fields) >= 2 and fields[0] == 'name':
                    self.codes[remote_name].add(fields[1])

    def send_once(self, device_id, message):
        """
        Send single call to IR LED.
        """
        call(['irsend', 'SEND_ONCE', device_id, message])


if __name__ == "__main__":
    lirc = Lirc('/etc/lirc/lircd.conf')
