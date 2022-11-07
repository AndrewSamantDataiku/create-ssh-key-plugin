# This file is the actual code for the Python runnable create-ssh-key-and-add-git-config
import dataiku
from dataiku.runnables import Runnable
from create_config import generate_key, create_config





class MyRunnable(Runnable):
    """The base interface for a Python runnable"""

    def __init__(self, project_key, config, plugin_config):
        """
        :param project_key: the project in which the runnable executes
        :param config: the dict of the configuration of the object
        :param plugin_config: contains the plugin settings
        """
        self.project_key = project_key
        self.config = config
        self.plugin_config = plugin_config
        self.client = dataiku.api_client()
        self.git_config_template = base_git_config_template = {
                              'allowGit': True,
                              'dssControlsSSHCommand': True,
                              'gitConfigurationOptions': [{'key': 'core.sshCommand',
                                'value': 'ssh -i /home/dataiku/.ssh/{ssh_key} -o StrictHostKeyChecking=yes'}],
                              'groupName': '{group_name}',
                              'remoteWhitelist': ['^(?:git|ssh|https?|git@[-\\w.]+):(\\/\\/)?(.*?)(\\.git)?(\\/?|\\#[-\\d\\w._]+?)$']}

    def get_progress_target(self):
        """
        If the runnable will return some progress info, have this function return a tuple of 
        (target, unit) where unit is one of: SIZE, FILES, RECORDS, NONE
        """
        return None

    def run(self, progress_callback):
        """
        Do stuff here. Can return a string or raise an exception.
        The progress_callback is a function expecting 1 value: current progress
        """
        general_settings_handle = self.client.get_general_settings()
        general_settings_json = general_settings_handle.get_raw()
        git_config_list = general_settings_json['git']['enforcedConfigurationRules']
        existing_group_list = [config.get('groupName','NO_GROUP_ENTERED') for config in git_config_list]
        
        git_group = self.config.get('group_name','')
        
        if git_group=='':
            raise("You must enter a git group.")
        elif git_group in existing_group_list:
            raise("The {} group already exists. Please contact your admin if you would like to change the ssh key or git settings.".format(git_group))
        else:
            print('Generating SSH Key')
            try:
                ssh_key = generate_key(self.project_key)
                print('Generated SSH Key: {}'.format(ssh_key))
            except:
                raise('Failed to generate ssh key.')
            
            # Create or update the project variable storing the ssh key
            project = self.client.get_project(self.project_key)
            variables = project.get_variables()
            variables['standard']['GitSSHKey'] = ssh_key
            project.set_variables(variables)


            print("Generating New Git Configuration Settings")
            try:
                new_config = create_config(git_group,ssh_key,self.git_config_template)
                all_git_config_list = git_config_list + [new_config]
                general_settings_json['git']['enforcedConfigurationRules'] = all_git_config_list
                general_settings_handle.save()
            except:
                raise('')
            print("New Configuration Group {} added successfully".format(git_group))
            return ssh_key      
        