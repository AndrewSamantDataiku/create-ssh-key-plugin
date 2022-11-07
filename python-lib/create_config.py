import dataiku
from subprocess import Popen, PIPE

client = dataiku.api_client()

base_git_config_template = {'allowGit': True,
  'dssControlsSSHCommand': True,
  'gitConfigurationOptions': [{'key': 'core.sshCommand',
    'value': 'ssh -i /home/dataiku/.ssh/{ssh_key} -o StrictHostKeyChecking=yes'}],
  'groupName': '{group_name}',
  'remoteWhitelist': ['^(?:git|ssh|https?|git@[-\\w.]+):(\\/\\/)?(.*?)(\\.git)?(\\/?|\\#[-\\d\\w._]+?)$']}


def generate_key():
    
    # Create new ssh key and save to the rsa-key.pub file
    process = Popen(['ssh-keygen', '-t', 'rsa','-b','2048','-f','rsa-key'], stdout=PIPE, stderr=PIPE)
    # Print the contents of the rsa-key.pub file
    process = Popen(['cat','rsa-key.pub'], stdout=PIPE, stderr=PIPE)
    stdout, stderr = process.communicate()
    # Prase out the trailing \n and recode to utf-8 format.
    ssh_key = stdout.decode("utf-8").replace('\n','')
    
    # Create or update the project variable storing the ssh key
    project = client.get_project(dataiku.default_project_key())
    variables = project.get_variables()
    variables['standard']['GitSSHKey'] = ssh_key
    project.set_variables(variables)
    
    return ssh_key
    
    

def create_config(group,key,git_config_template):
    
    config = git_config_template
    
    config['groupName'] = group
    
    config_options = config['gitConfigurationOptions']
    config_options[0]['value'] = config_options[0]['value'].format(ssh_key = key)
    config['gitConfigurationOptions'] = config_options
    
    return config
    
def update_git_settings(git_group,git_config_template):

    general_settings_handle = client.get_general_settings()
    general_settings_json = general_settings.get_raw()
    git_config_list = general_settings_json['git']['enforcedConfigurationRules']
    existing_group_list = [config.get('groupName','NO_GROUP_ENTERED') for config in git_config_list]

    if git_group=='':
        print("You must enter a git group.")
    elif git_group in existing_group_list:
        print("The {} group already exists. Please contact your admin if you would like to change the ssh key or git settings.".format(git_group))
    else:
        print('Generating SSH Key')
        ssh_key = generate_key()
        print('Generated SSH Key: {}'.format(ssh_key))
        print("Generating New Git Configuration Settings")
        new_config_list = create_config(git_group,ssh_key,git_config_template)
        all_git_config_list = git_config_list + new_config_list
        general_settings_json['git']['enforcedConfigurationRules'] = all_git_config_list
        general_settings.save()
        print("New Configuration Group {} added successfully".format(git_group))