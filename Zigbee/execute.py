import subprocess

path = "."
scripts = ['zigbee.py', 'run.py']

script_processes = [
    subprocess.Popen(f'python {path}/{script}', shell=True)
    for script in scripts
]

for script in script_processes:
    script.wait()
