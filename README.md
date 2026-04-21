# Cloudmesh Multipass Extension


## Multipass Installation

Before installing the cloudmesh extension, you must install Multipass on your system:

### macOS
```bash
brew install --cask multipass
```

### Windows
Download and run the installer from the [official Multipass website](https://multipass.run/install).

### Linux
Multipass is distributed as a snap package:
```bash
sudo snap install multipass
```

## Installation

Install the cloudmesh multipass extension:
```bash
pip install cloudmesh-multipass
cms help multipass
```

## User Guide

You can also use the built-in installation helper to install the Multipass binary on your system:
```bash
cms multipass install
```

The Cloudmesh Multipass extension provides a simplified interface to manage Multipass virtual machines directly from the `cms` command line.

### 1. Getting Started
To create and launch a new virtual machine:
```bash
cms multipass create my-vm
```
**Which OS is used?**
By default, Multipass launches **Ubuntu** virtual machines. The specific version is typically the latest Ubuntu LTS (Long Term Support) release available in the Multipass image repository.

To see all available OS versions and images you can use:
```bash
cms multipass images
```

### 2. System Information and Diagnostics
You can get a complete overview of your Multipass installation, including version, health tests, default VM settings, current VMs, and available images, with a single command:
```bash
cms multipass info
```
This consolidated command runs multiple diagnostics and provides a comprehensive report of your environment.

### 3. Managing VM Lifecycle
You can control the state of your VMs using the following commands:
- **Start**: `cms multipass start my-vm`
- **Stop**: `cms multipass stop my-vm`
- **Reboot**: `cms multipass reboot my-vm`
- **Delete**: `cms multipass delete my-vm` (removes the VM but keeps the data)
- **Destroy**: `cms multipass destroy my-vm` (completely purges the VM and its data)

### 4. Interacting with VMs
- **Shell Access**: Enter the VM's terminal:
  ```bash
  cms multipass shell my-vm
  ```
- **Run Command**: Execute a command inside the VM without entering the shell:
  ```bash
  cms multipass run "ls -la /tmp" my-vm
  ```

### 5. Advanced VM Creation
You can customize the resources allocated to your VM:
```bash
cms multipass create my-custom-vm --cpus 2 --memory 4G --disk 20G --image ubuntu-22.04
```
- `--cpus`: Number of CPU cores.
- `--memory`: Amount of RAM (e.g., 2G, 4G).
- `--disk`: Disk size.
- `--image`: Specify a different Multipass image (use `cms multipass images` to see available ones).

### 6. File and Data Management
- **Mounting**: Share a local directory with the VM:
  ```bash
  cms multipass mount /home/user/data my-vm:/home/ubuntu/data
  ```
- **Unmounting**: `cms multipass umount /home/user/data my-vm:/home/ubuntu/data`
- **Transfer**: Move files between host and VM:
  ```bash
  cms multipass transfer local_file.txt my-vm:/home/ubuntu/remote_file.txt
  ```

### 7. Deployment
The `deploy` command is used to automate the setup of Multipass environments based on predefined configurations.
```bash
cms multipass deploy
```

## Last verified install test

cms multipass deploy
* Ubuntu 22.04, Dec 2023

## Manual Page

<!-- START-MANUAL -->
```
Command multipass
=================

::

  Usage:
        multipass install
        multipass info [NAMES] [--output=OUTPUT] [--dryrun]
        multipass deploy [--dryrun]
        multipass images [--output=OUTPUT] [--refresh] [--purge] [--dryrun]
        multipass list [--output=OUTPUT] [--dryrun]
        multipass create NAMES [--image=IMAGE]
                               [--size=SIZE]
                               [--memory=MEMORY]
                               [--cpus=CPUS]
                               [--disk=DISK]
                               [--dryrun]
                               [--cloudinit=FILE_OR_URL]
                               [--network=NETWORK]
                               [--bridged]
                               [--mount=SOURCE]
                               [--timeout=TIMEOUT]
        multipass delete NAMES [--output=OUTPUT][--dryrun]
        multipass destroy NAMES [--output=OUTPUT][--dryrun]
        multipass shell NAMES [--dryrun]
        multipass run COMMAND NAMES [--output=OUTPUT] [--dryrun]
        multipass suspend NAMES [--output=OUTPUT] [--dryrun]
        multipass resume NAMES [--output=OUTPUT] [--dryrun]
        multipass start NAMES [--output=OUTPUT] [--dryrun]
        multipass stop NAMES [--output=OUTPUT] [--dryrun]
        multipass reboot NAMES [--output=OUTPUT] [--dryrun]
        multipass mount SOURCE DESTINATION [--dryrun]
        multipass umount SOURCE [--dryrun]
        multipass transfer SOURCE DESTINATION [--dryrun]
        multipass set key=VALUE [--dryrun]
        multipass get [key] [--dryrun]
        multipass rename NAMES [--dryrun]
        multipass test
        multipass vm defaults [--output=OUTPUT]
        multipass version

  Interface to multipass

  Options:
       --output=OUTPUT    the output format [default: table]. Other
                          values are yaml, csv and json.

       --image=IMAGE      the image name to be used to create a VM.

       --cpus=CPUS        Number of CPUs to allocate.
                          Minimum: 1, default: 1.

       --size=SIZE        Disk space to allocate. Positive integers,
                          in bytes, or with K, M, G suffix.
                          Minimum: 512M, default: 5G.

       --mem=MEMORY       Amount of memory to allocate. Positive
                          integers, in bytes, or with K, M, G suffix.
                          Minimum: 128M, default: 1G.

       --cloudinit=FILE  Path to a user-data cloudinit configuration

  Arguments:
      NAMES   the names of the virtual machine

  Description:

      The NAMES can be a parameterized hostname such as

        red[0-1,5] = red0,red1,red5

  Commands:

    Install Multipass on the host system:

        cms multipass install

    Get consolidated system information or specific VM info:

        cms multipass info [NAMES]

    First you can see the supported multipass images with

        cms multipass images

    Create and launch a new vm using

        cms multipass create NAMES

        Optionally you can provide image name, size, memory,
        number of cpus to create an instance.

    Start one or multiple multipass vms with

        cms multipass start NAMES

    Stop one or multiple vms with

        cms multipass stop NAMES

    Gets all multipass internal key values with

      cms multipass get

    Gets a specific internal key.

      cms multipass get KEY

      Known keys

          client.gui.autostart
          client.primary-name
          local.driver

    Reboot (stop and then start) vms with

        cms multipass reboot NAMES

    Delete one of multiple vms without purging with

        cms multipass delete NAMES

    Destory multipass vms (delete and purge) with

        cms multipass destroy NAMES

        Caution: Once destroyed everything in vm will be deleted
                 and cannot be recovered.

    WHEN YOU IMPLEMENT A FUNCTION INCLUDE MINIMAL
      DOCUMENTATION HERE
```
<!-- STOP-MANUAL -->