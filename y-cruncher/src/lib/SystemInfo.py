import json
import platform
import urllib.request


class SystemInfo:
    def __init__(self):
        self.on_wsl = "microsoft" in platform.uname()[3].lower()

        try:
            with urllib.request.urlopen('http://169.254.169.254/latest/meta-data/instance-type') as response:
                self.platform = "Amazon Web Services"
                self.instance_type = response.read().decode('utf-8')
        except:
            try:
                request = urllib.request.Request('http://metadata.google.internal/computeMetadata/v1/instance/machine-type', headers={'Metadata-Flavor':'Google'})
                with urllib.request.urlopen(request) as response:
                    self.platform = "Google Cloud Platform"
                    self.instance_type = response.read().decode('utf-8').split('/')[-1]
            except:
                request = urllib.request.Request('http://169.254.169.254/metadata/instance?api-version=2019-06-01', headers={'Metadata':'true'})
                with urllib.request.urlopen(request) as response:
                    self.platform = "Microsoft Azure"
                    self.instance_type = json.loads(response.read())['compute']['vmSize']

        print('Running on {} platform, instance type {}'.format(self.platform, self.instance_type))

    def write_username_txt(self, username_template_filename):
        with open(username_template_filename, 'r', newline='\r\n') as file:
            username_template = file.read()

        with open('Username.txt', 'w') as file:
            file.write(username_template.format(platform=self.platform, instance_type=self.instance_type))
