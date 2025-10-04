import os
import shutil
import subprocess


def check_vnc_exists():
    try:
        out = shutil.which('vnc-viewer')
    except Exception as e:
        raise Exception(
            'An error occurred while trying to find path to vnc-viewer')
    if (out is None):
        raise Exception(('vnc-viewer not found!' % ()))


# def launch_vnc_viewer(host, port):
#     os.spawnl(os.P_NOWAIT, shutil.which('vnc-viewer'), 'vnc-viewer', ('%s:%s' % (host, port)))


def launch_vnc_viewer(host, port):
    # echo $PATH
    
    # Locate the VNC viewer executable
    vnc_path = shutil.which('vnc-viewer.exe')  # Ensure 'vncviewer.exe' is in PATH
    if not vnc_path:
        raise FileNotFoundError("VNC Viewer executable not found in PATH.")
    
    # Construct the command
    command = [vnc_path, f'{host}:{port}']
    
    # Launch the VNC Viewer
    try:
        subprocess.Popen(command, shell=True)
        print(f"VNC Viewer launched for {host}:{port}.")
    except Exception as e:
        print(f"Failed to launch VNC Viewer: {e}")

