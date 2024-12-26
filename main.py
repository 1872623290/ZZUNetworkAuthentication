import time
import httpx
from fake_useragent import UserAgent
import base64
import socket
import toml
import psutil

# List of TOML files to load
toml_files = ['config1.toml']  # Add more file names as needed

# Function to load configuration from multiple TOML files
def load_config(toml_files):
    all_config = []
    for toml_file in toml_files:
        try:
            config = toml.load(toml_file)
            all_config.append(config)
        except Exception as e:
            print(f"Error loading {toml_file}: {e}")
    return all_config

# Load configuration files
configs = load_config(toml_files)

# Process each configuration
for config in configs:
    account = config['Account']['account']
    password = config['Account']['password']
    interfaces = config['Settings']['interfaces']

    try:
        baseLoginURL = config['Settings']['baseLoginURL']
    except KeyError:
        baseLoginURL = 'http://10.2.8.8:801/eportal/portal/login'

    def getIPByInterface(interface):
        addresses = psutil.net_if_addrs()
        if interface in addresses:
            for addr in addresses[interface]:
                if addr.family == socket.AF_INET:
                    return addr.address
        return None

    def createClient(interface):
        transport = httpx.HTTPTransport(local_address=getIPByInterface(interface))
        client = httpx.Client(transport=transport)
        return client

    headers = {
        'Accept': '*/*',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'Connection': 'keep-alive',
        'Referer': 'http://10.2.7.8/',
        'User-Agent': UserAgent().random,
    }

    # Process each interface in the config
    for interface in interfaces:
        ipv4_address = getIPByInterface(interface)
        if ipv4_address:
            print(f"{interface} IPv4 Address: {ipv4_address}")
        else:
            print(f"{interface} does not have a valid IPv4 address.")

        params = [
            ('callback', 'dr1003'),
            ('login_method', '1'),
            ('user_account', f',0,{account}'),
            ('user_password', base64.b64encode(password.encode()).decode()),
            ('wlan_user_ip', getIPByInterface(interface)),
            ('wlan_user_ipv6', ''),
            ('wlan_user_mac', '000000000000'),
            ('wlan_ac_ip', ''),
            ('wlan_ac_name', ''),
            ('jsVersion', '4.2.1'),
            ('terminal_type', '1'),
            ('lang', 'zh-cn'),
            ('v', '1262'),
            ('lang', 'zh'),
        ]

        client = createClient(interface)
        response = client.get(baseLoginURL, params=params, headers=headers)
        print(f"{interface}: {response.text}")
        time.sleep(1)
