import dataiku
from subprocess import Popen, PIPE


def generate_key(project_key):
    
    # Create new ssh key and save to the rsa-key.pub file
    process = Popen(['ssh-keygen', '-t', 'rsa','-b','2048','-f','rsa-key'], stdout=PIPE, stderr=PIPE)
    # Print the contents of the rsa-key.pub file
    process = Popen(['cat','rsa-key.pub'], stdout=PIPE, stderr=PIPE)
    stdout, stderr = process.communicate()
    # Prase out the trailing \n and recode to utf-8 format.
    ssh_key = stdout.decode("utf-8").replace('\n','')
    
    # Create or update the project variable storing the ssh key
    project = client.get_project(project_key)
    variables = project.get_variables()
    variables['standard']['GitSSHKey'] = ssh_key
    project.set_variables(variables)
    
    return ssh_key
    
    

def create_config(group, key, git_config_template):
    
    config = git_config_template
    
    config['groupName'] = group
    
    config_options = config['gitConfigurationOptions']
    config_options[0]['value'] = config_options[0]['value'].format(ssh_key = key)
    config['gitConfigurationOptions'] = config_options
    
    return config
    