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
Verify the installation:
```bash
multipass version
```

## Installation

Install the cloudmesh multipass extension:
```bash
pip install cloudmesh-multipass
cmc help multipass
```

## User Guide

You can use the built-in helpers to install or uninstall the Multipass binary on your system:

**Install:**
```bash
cmc multipass install
```

**Uninstall:**
```bash
cmc multipass uninstall
```

The Cloudmesh Multipass extension provides a simplified interface to manage Multipass virtual machines directly from the `cmc` command line.

### 1. VM Lifecycle Management
You can easily ensure a VM is running with the `run` command. It will launch a new VM if it doesn't exist, or start it if it's stopped:
```bash
cmc multipass run my-vm --cpus 2 --memory 4G --disk 20G
```

### 2. Daemon Management (macOS)
You can enable or disable the Multipass daemon on macOS:
- **Enable**: `cmc multipass enable`
- **Disable**: `cmc multipass disable`

### 2. Version Information
You can check the Multipass version and package manager info:
```bash
cmc multipass version
```

### 3. System Information and Diagnostics
You can get a complete overview of your Multipass installation, including version, health tests, available images, and network interfaces, or get details for a specific VM:

**System-wide info:**
```bash
cmc multipass status
```

**Specific VM info:**
```bash
cmc multipass status my-vm
```
This command provides a comprehensive report of your environment or the specific instance.

### Troubleshooting
If you encounter the error `cannot connect to the multipass socket`, it usually means the Multipass daemon is not running.

**On macOS:**
Restart the Multipass daemon using:
```bash
sudo launchctl kickstart -k system/com.canonical.multipassd
```

**On Linux:**
Ensure the snap service is running:
```bash
sudo snap restart multipass
```

**On Windows:**
Restart the "Multipass" service via the Services manager (`services.msc`).


## Manual Page

<!-- START-MANUAL -->
```
Command multipass
=================

::

  Usage:
        multipass uninstall
        multipass install
        multipass enable
        multipass disable
        multipass run NAME [--cpus=CPUS] [--memory=MEMORY] [--disk=DISK]
        multipass version
        multipass status [NAME] [--output=OUTPUT]

  Interface to multipass

  Options:
       --output=OUTPUT    the output format [default: table]. Other
                           values are yaml, csv and json.

  Arguments:
      NAME    the name of the virtual machine

  Description:

  Commands:

    Uninstall Multipass from the host system:

        cmc multipass uninstall

    Install Multipass on the host system:

        cmc multipass install

    Enable the Multipass daemon (macOS):

        cmc multipass enable

    Disable the Multipass daemon (macOS):

        cmc multipass disable

    Ensure a VM is running (launch or start):

        cmc multipass run NAME [--cpus=CPUS] [--memory=MEMORY] [--disk=DISK]

    Show Multipass version information:

        cmc multipass version

    Retrieve Multipass system information or details for a specific VM:

        cmc multipass status [NAME]
```
<!-- STOP-MANUAL -->
## Core Dependencies
This project depends on the following core components of the Cloudmesh AI ecosystem:
- [cloudmesh-ai-common](https://github.com/cloudmesh-ai/cloudmesh-ai-common)
- [cloudmesh-ai-cmc](https://github.com/cloudmesh-ai/cloudmesh-ai-cmc)
