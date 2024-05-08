import yaml
def get_config():
    with open('./ChatBot_Extract_Intent/config_app/config.yml', encoding='utf-8') as cfgFile:
        config_app = yaml.safe_load(cfgFile)
        cfgFile.close()
    return config_app

