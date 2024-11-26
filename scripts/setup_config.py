
import os
import shutil

def setup_config():
    env = os.getenv('ENV', 'development')
    source = f'.streamlit/config.{env}.toml'
    target = '.streamlit/config.toml'
    
    if os.path.exists(source):
        shutil.copy(source, target)
        print(f"Applied {env} configuration")
    else:
        print(f"Config file not found: {source}")