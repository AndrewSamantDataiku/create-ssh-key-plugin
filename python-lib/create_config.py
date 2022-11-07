import dataiku
from subprocess import Popen, PIPE


def generate_key(project_key):
    
    # Create new ssh key and save to the rsa-key.pub file
    process = Popen(['ssh-keygen', '-t', 'rsa','-b','2048','-f','rsa-key','-N',"''"], stdout=PIPE, stderr=PIPE)
    gen_stdout, gen_stderr = process.communicate()#b'', b'' #process.stdout.readline(), process.stderr.readline()
    # Print the contents of the rsa-key.pub file
    process = Popen(['cat','rsa-key.pub'], stdout=PIPE, stderr=PIPE)
    read_stdout, read_stderr = process.communicate()
    # Prase out the trailing \n and recode to utf-8 format.
    ssh_key = gen_stdout.decode("utf-8").replace('\n','')
    
    return ssh_key, gen_stderr, read_stderr
    
    

def create_config(group, key, git_config_template):
    
    config = git_config_template
    
    config['groupName'] = group
    
    config_options = config['gitConfigurationOptions']
    config_options[0]['value'] = config_options[0]['value'].format(ssh_key = key)
    config['gitConfigurationOptions'] = config_options
    
    return config
    