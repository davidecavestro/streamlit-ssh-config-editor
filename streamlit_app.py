import altair as alt
import numpy as np
import pandas as pd
import streamlit as st

import os
import shutil
from streamlit.file_util import get_streamlit_file_path

PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))

credential_path = get_streamlit_file_path("credentials.toml")
if not os.path.exists(credential_path):
    os.makedirs(os.path.dirname(credential_path), exist_ok=True)
    shutil.copyfile(os.path.join(PROJECT_ROOT, ".streamlit\\credentials.toml"), credential_path)

# Path to SSH config file
SSH_CONFIG_PATH = os.path.expanduser("~/.ssh/config")

# Function to read SSH config
def read_ssh_config():
    if not os.path.exists(SSH_CONFIG_PATH):
        return []
    with open(SSH_CONFIG_PATH, 'r') as file:
        config_lines = file.readlines()
    return config_lines

# Function to parse SSH config into blocks
def parse_ssh_config(config_lines):
    config_blocks = []
    current_block = {}

    for line in config_lines:
        line = line.strip()
        if line.startswith("Host "):
            if current_block:
                config_blocks.append(current_block)
                current_block = {}
            current_block["Host"] = line.split()[1]
        elif line.startswith("#"):
            # ignore it
            continue
        elif line:
            key, value = line.split(None, 1)
            current_block[key] = value

    if current_block:
        config_blocks.append(current_block)
    
    return config_blocks

# Function to write SSH config blocks to file
def write_ssh_config(config_blocks):
    with open(SSH_CONFIG_PATH, "w") as file:
        for block in config_blocks:
            file.write(f"Host {block['Host']}\n")
            for key, value in block.items():
                if key != "Host" and value:
                    file.write(f"    {key} {value}\n")
            file.write("\n")

# Read and parse the SSH config
config_lines = read_ssh_config()
config_blocks = parse_ssh_config(config_lines)

# Streamlit App
st.title("SSH Config Manager")

# Display Existing Configurations
st.subheader("Existing Configurations")
# for block in config_blocks:
#     with st.expander(f"Host: {block['Host']}"):
#         for key, value in block.items():
#             st.write(f"{key}: {value}")

df = pd.DataFrame(config_blocks)

st.dataframe(df, use_container_width=True)

# Add New SSH Configuration
with st.form("add_config"):
    st.subheader("Add New Configuration")
    host = st.text_input("Host")
    hostname = st.text_input("HostName")
    user = st.text_input("User")
    port = st.text_input("Port", value="22")
    identity_file = st.text_input("IdentityFile")

    add_button = st.form_submit_button("Add Configuration")

    if add_button and host:
        new_block = {
            "Host": host,
            "HostName": hostname,
            "User": user,
            "Port": port,
            "IdentityFile": identity_file
        }
        config_blocks.append(new_block)
        write_ssh_config(config_blocks)
        st.success(f"Configuration for {host} added.")
        st.rerun()

# Edit Existing SSH Configuration
selected_host = st.selectbox("Select Host to Edit", [block['Host'] for block in config_blocks])

if selected_host:
    block_to_edit = next(block for block in config_blocks if block["Host"] == selected_host)
    with st.form("edit_config"):
        hostname = st.text_input("HostName", value=block_to_edit.get("HostName", ""))
        user = st.text_input("User", value=block_to_edit.get("User", ""))
        port = st.text_input("Port", value=block_to_edit.get("Port", "22"))
        identity_file = st.text_input("IdentityFile", value=block_to_edit.get("IdentityFile", ""))

        edit_button = st.form_submit_button("Update Configuration")

        if edit_button:
            block_to_edit.update({
                "HostName": hostname,
                "User": user,
                "Port": port,
                "IdentityFile": identity_file
            })
            write_ssh_config(config_blocks)
            st.success(f"Configuration for {selected_host} updated.")
            st.rerun()

# Delete SSH Configuration
selected_host_to_delete = st.selectbox("Select Host to Delete", [block['Host'] for block in config_blocks])

if st.button("Delete Configuration"):
    config_blocks = [block for block in config_blocks if block["Host"] != selected_host_to_delete]
    write_ssh_config(config_blocks)
    st.success(f"Configuration for {selected_host_to_delete} deleted.")
    st.rerun()

# Run the app using the following command in terminal:
# streamlit run streamlit_app.py
