import shutil
import os
import os, fnmatch
from signal import raise_signal

### ERROR STRINGS #####
ERR_G_VAR_UNDEFINED = "ERR: a required global variable was never assigned a value"

glad_hs_dir = os.path.dirname(os.path.realpath(__file__))

if (os.path.basename(glad_hs_dir) != 'glad_hs'):
    glad_hs_dir = os.path.dirname(glad_hs_dir)
    if (os.path.basename(glad_hs_dir) != 'glad_hs'):
        print("Setup script is not in expected directory")
        exit(1)

DEFAULT_DOMAIN_NAME = 'my_domain.com'
g_domain_name = None
g_oauth_proxy_client_id = None
g_oauth_proxy_client_secret = None
g_oauth_secret_cookie = None

def main():
    setup_fb()
    setup_nginx()
    setup_env()
    setup_oauth()

    print('\nSetup of glad_hs has finished.')
    print('If you skipped steps and need to finish setup manually please view the README for more information: https://github.com/aglad-eng/glad_hs#setup')

def setup_nginx():
    inp = get_user_yes_no('Do you want nginx to be automatically setup for you? (will put your domain name into .conf files): (Y/n)', 'y')
    if is_yes(inp):
        prep_nginx_conf_files()
        print('')

def setup_env():
    inp = get_user_yes_no('Do you want the .env file to be automatically setup for you? (will put environment variables for docker-compose.yml): (Y/n)', 'y')
    if is_yes(inp):
        prep_env_file()
        print('')

def setup_oauth():
    inp = get_user_yes_no('Do you want the oauth2 configuration file to be automatically setup for you? (will replace necessary vairables, and add permitted google accounts): (Y/n)', 'y')
    if is_yes(inp):
        prep_oauth_config_file()
        prep_oauth_emails_file()
        print('')

def setup_fb():
    inp = get_user_yes_no('Do you want filebrowser to be automatically setup for you? (will create empty database file): (Y/n)', 'y')
    if is_yes(inp):
        create_empty_db()
        print('')

def prep_nginx_conf_files():
    global g_domain_name

    ### Get paths
    nginx_conf_relPath = "nginx_config/"
    nginx_conf_absPath = os.path.join(glad_hs_dir, nginx_conf_relPath)
    nginx_ex_relPath = "nginx_config/examples/"
    nginx_ex_absPath = os.path.join(glad_hs_dir, nginx_ex_relPath)

    ### Check if files already exist
    nginx_main_conf_path = os.path.join(nginx_conf_absPath, "nginx.conf")
    print(nginx_main_conf_path)
    if (os.path.isfile(nginx_main_conf_path)):
        print("file existed")
        inp = get_user_yes_no('***Warning*** nginx conf files already exist.  Are you sure you want to overwrite them? (y/N)', 'n')
        if is_no(inp):
            return

    ### check pre requisite global variables
    if (g_domain_name is None):
        g_domain_name = ui_get_domain_name()
        if (g_domain_name is None):
            raise Exception(f"{__name__} - {ERR_G_VAR_UNDEFINED}")

    print("Creating .conf files from examples provided and replacing domain in .conf files...")
    shutil.copytree(nginx_ex_absPath, nginx_conf_absPath, dirs_exist_ok=True)

    findReplace_DIR(os.path.join(nginx_conf_absPath, "conf.d/"), DEFAULT_DOMAIN_NAME, g_domain_name)
    findReplace_DIR(os.path.join(nginx_conf_absPath, "conf_templates/"), DEFAULT_DOMAIN_NAME, g_domain_name)
    findReplace_File(nginx_main_conf_path, DEFAULT_DOMAIN_NAME, g_domain_name)

    # Open 999_remaining_subdomains.conf and replace correct sections
    all_subdomains_conf_path = os.path.join(nginx_conf_absPath, "conf.d/999_remaining_subdomains.conf")
    filedata = None
    with open(all_subdomains_conf_path, 'r') as file:
        filedata =  file.read()

    repl_string = g_domain_name.replace('.', '\.')
    # Replace the target string
    filedata = filedata.replace('my_domain\.com', repl_string)

    # Write the file out again
    with open(all_subdomains_conf_path, 'w') as file:
        file.write(filedata)

def prep_env_file():
    global g_domain_name
    global g_oauth_proxy_client_id
    global g_oauth_proxy_client_secret
    global g_oauth_secret_cookie

    ### Get paths
    fname = ".env"
    envExample_file_path = os.path.join(glad_hs_dir, fname + ".example")
    env_file_path = os.path.join(glad_hs_dir, fname)

    ### Check if file exists
    if (os.path.isfile(env_file_path)):
        inp = get_user_yes_no(f'***Warning*** {fname} files already exists.  Are you sure you want to overwrite it? (y/N)', 'n')
        if is_no(inp):
            return

    if (g_domain_name is None):
        g_domain_name = ui_get_domain_name()

    oauth_admin_email = input('Oath2 admin email: ')
    if g_oauth_secret_cookie is None:
        g_oauth_secret_cookie = ui_get_oauth_secret_cookie()
    if g_oauth_proxy_client_id is None:
        g_oauth_proxy_client_id = ui_get_oauth_proxy_client_id()
    if g_oauth_proxy_client_secret is None:
        g_oauth_proxy_client_secret = ui_get_oauth_proxy_client_secret()

    smtp_username = input('SMTP username: ')
    smtp_password = input('SMTP password: ')
    smtp_email = input('SMTP email: ')
    smtp_domain = input('SMTP domain: ')
    VW_admin_token = input('Vaultwarden (bit warden) admin token: ')
    
    print("Creating and editing .env file...")

    with open(envExample_file_path, 'r') as file:
        filedata =  file.read()

    # Replace the target string
    filedata = filedata.replace('GHS_DIR=/home/username/glad_hs', 'GHS_DIR=' + glad_hs_dir)
    filedata = filedata.replace('GHS_SECRETS_DIR=/home/username/glad_hs/secrets', 'GHS_SECRETS_DIR=' + os.path.join(glad_hs_dir, '/secrets'))
    filedata = filedata.replace('GHS_DOMAIN_NAME_PROXY=mydomain.com', 'GHS_DOMAIN_NAME_PROXY=' + g_domain_name)
    filedata = filedata.replace('GHS_BASE_DOMAIN=mydomain.com', 'GHS_BASE_DOMAIN=' + g_domain_name)

    filedata = filedata.replace('MY_OAUTH_ADMIN_EMAIL=my_email@gmail.com', 'MY_OAUTH_ADMIN_EMAIL=' + oauth_admin_email)
    filedata = filedata.replace('OAUTH2_PROXY_COOKIE_SECRET=SUPER_SECRET_GENERATED_COOKIE', 'OAUTH2_PROXY_COOKIE_SECRET=' + g_oauth_secret_cookie)
    filedata = filedata.replace('OAUTH2_PROXY_COOKIE_DOMAIN=https://<oauth_sub_domain>.mydomain.com', 'OAUTH2_PROXY_COOKIE_DOMAIN=' + f"https://oauth.{g_domain_name}")
    filedata = filedata.replace('OAUTH2_PROXY_CLIENT_ID=client_id_recieved_from_oauth_provider', 'OAUTH2_PROXY_CLIENT_ID=' + g_oauth_proxy_client_id)
    filedata = filedata.replace('OAUTH2_PROXY_CLIENT_SECRET=client_secret', 'OAUTH2_PROXY_CLIENT_SECRET=' + g_oauth_proxy_client_secret)

    filedata = filedata.replace('SMTP_USERNAME=my_email@gmail.com', 'SMTP_USERNAME=' + smtp_username)
    filedata = filedata.replace('SMTP_PASSWORD=smtp_password', 'SMTP_PASSWORD=' + smtp_password)
    filedata = filedata.replace('SMTP_EMAIL=my_email@gmail.com', 'SMTP_EMAIL=' + smtp_email)
    filedata = filedata.replace('SMTP_DOMAIN=smtp.gmail.com', 'SMTP_DOMAIN=' + smtp_domain)
    filedata = filedata.replace('VW_ADMIN_TOKEN=super_secure_admin_token', 'VW_ADMIN_TOKEN=' + VW_admin_token)

    # Write the file out again
    with open(env_file_path, 'w') as file:
        file.write(filedata)

def prep_oauth_config_file():
    global g_domain_name
    global g_oauth_proxy_client_id
    global g_oauth_proxy_client_secret
    global g_oauth_secret_cookie
    
    ### Get Paths
    fname = "oauth2_proxy.cfg"
    oauthConfigExample_file_path = os.path.join(glad_hs_dir, "oauth/", fname + ".example")
    oauthConfig_file_path = os.path.join(glad_hs_dir, "oauth/", fname)
    
    ### Check if file exists
    if (os.path.isfile(oauthConfig_file_path)):
        inp = get_user_yes_no(f'***Warning*** {fname} files already exists.  Are you sure you want to overwrite it? (y/N)', 'n')
        if is_no(inp):
            return

    if (g_domain_name is None):
        g_domain_name = ui_get_domain_name()

    if g_oauth_secret_cookie is None:
        g_oauth_secret_cookie = ui_get_oauth_secret_cookie()
    if g_oauth_proxy_client_id is None:
        g_oauth_proxy_client_id = ui_get_oauth_proxy_client_id()
    if g_oauth_proxy_client_secret is None:
        g_oauth_proxy_client_secret = ui_get_oauth_proxy_client_secret()

    cookie_exp_hours = get_UI("time until cookie expires in hours - (this will determine how long people stay signed in via oauth): ")
    cookie_refresh_hours = get_UI("how often you want to check for expired cookies in hours: ")

    print("Creating and editing oauth2_proxy.cfg file...")

    with open(oauthConfigExample_file_path, 'r') as file:
        filedata =  file.read()

    # Replace the target string
    filedata = filedata.replace('client_id = "123456.apps.googleusercontent.com"', f'client_id = "{g_oauth_proxy_client_id}"')
    filedata = filedata.replace('client_secret = "123456789123456789123456789"', f'client_secret = "{g_oauth_proxy_client_secret}"')
    filedata = filedata.replace('cookie_secret = "123456123456123456123"', f'cookie_secret = "{g_oauth_secret_cookie}"')
    filedata = filedata.replace('cookie_domains = ".my_domain.com"', f'cookie_domains = ".{g_domain_name}"')
    filedata = filedata.replace('cookie_expire = "168h"', f'cookie_expire = "{cookie_exp_hours}h"')
    filedata = filedata.replace('cookie_refresh = "6h"', f'cookie_refresh = "{cookie_refresh_hours}h"')

    # Write the file out again
    with open(oauthConfig_file_path, 'w') as file:
        file.write(filedata)

def prep_oauth_emails_file():
    fname = "permitted_emails.txt"
    oauthEmail_file_path = os.path.join(glad_hs_dir, "oauth/", fname)
    
    if (os.path.isfile(oauthEmail_file_path)):
        inp = get_user_yes_no(f'***Warning*** {fname} files already exists.  Are you sure you want to overwrite it? (y/N)', 'n')
        if is_no(inp):
            return

    with open(oauthEmail_file_path, 'w') as file:
        print("Enter a single email on each prompt that  is associated with a google account you whish to have access to your server.")
        while True:
            inp = input('     Please enter another email or enter "q" to exit: ')
            if (inp.strip().lower() == "q"):
                break
            file.write(inp + "\n")

def create_empty_db():
    db_filename = "fb_database.db"
    db_relPath = "fb_config/"
    db_file_path = os.path.join(glad_hs_dir, db_relPath, db_filename)

    if (os.path.isfile(db_file_path)):
        inp = get_user_yes_no(f'***Warning*** {db_filename} files already exists.  Are you sure you want to overwrite it? (y/N)', 'n')
        if is_no(inp):
            return
        
        print("Creating Filebroswer database...")
        with open(db_file_path, 'w') as fp:
            pass

########## UI functions ##############
def get_UI(prompt):
    return input('Enter ' + prompt)

def ui_get_domain_name():
    return get_UI('base domain name of server: ')

def ui_get_oauth_proxy_client_id():
    return get_UI('Oath2 proxy client id: ')

def ui_get_oauth_secret_cookie():
    return get_UI('Oath2 secret cookie: ')

def ui_get_oauth_proxy_client_secret():
    return get_UI('Oath2 proxy client secret: ')

########## Utility Functions #############
def findReplace_DIR(directory, find, replace, filePattern = '*'):
    for path, dirs, files in os.walk(os.path.abspath(directory)):            
        for filename in fnmatch.filter(files, filePattern):
            filepath = os.path.join(path, filename)
            findReplace_File(filepath, find, replace)

def findReplace_File(filepath, find, replace):
    with open(filepath) as f:
        s = f.read()
    s = s.replace(find, replace)
    with open(filepath, "w") as f:
        f.write(s)

def get_user_yes_no(prompt, default):
    if not isinstance(prompt, str):
        raise TypeError
    
    if not isinstance(default, str) or ((not is_yes(default)) and (not is_no(default))):
        raise TypeError
    
    user_input = input(prompt)
    # check if "y", "n", or white space
    while (not is_yes(user_input)) and (not is_no(user_input)) and (not user_input.isspace()) and (user_input != ''):
        user_input = input('    Incorrect input provided, please provide \'y\' or \'n\'')

    if (user_input.isspace() or user_input == ''):
        user_input = default

    return user_input

def is_yes(string):
    if not isinstance(string, str):
        raise TypeError

    if string.strip().lower() == 'y' or string.strip().lower() == 'yes':
        return True
    return False

def is_no(string):
    if not isinstance(string, str):
        raise TypeError

    if string.strip().lower() == 'n' or string.strip().lower() == 'no':
        return True
    return False

if __name__ == "__main__":
    main()