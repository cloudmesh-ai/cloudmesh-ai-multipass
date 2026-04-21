import platform
import shutil
import subprocess
import click
from cloudmesh.common.console import Console
from cloudmesh.common.debug import VERBOSE
from cloudmesh.common.util import banner
from cloudmesh.common.Printer import Printer
from cloudmesh.multipass.Provider import Provider as multipassProvider

@click.group()
@click.option("--dryrun", is_flag=True, help="Dry run mode")
@click.pass_context
def multipass_group(ctx, dryrun):
    """
    Interface to multipass
    """
    ctx.ensure_object(dict)
    ctx.obj['dryrun'] = dryrun

@multipass_group.command()
@click.pass_context
def install(ctx):
    """
    Install Multipass on the host system
    """
    dryrun = ctx.obj.get('dryrun', False)
    if dryrun:
        banner("dryrun install")
        return

    os_type = platform.system()
    install_cmd = ""
    if os_type == "Darwin":
        install_cmd = "brew install --cask multipass"
    elif os_type == "Linux":
        install_cmd = "sudo snap install multipass"
    elif os_type == "Windows":
        Console.info("Multipass for Windows must be installed via the official installer.")
        Console.info("Please visit: https://multipass.run/install")
        return
    else:
        Console.error(f"Unsupported OS: {os_type}")
        return

    if Console.confirm(f"Do you want to install Multipass using '{install_cmd}'?"):
        try:
            subprocess.run(install_cmd, shell=True, check=True)
            Console.ok("Multipass installed successfully.")
        except subprocess.CalledProcessError as e:
            Console.error(f"Installation failed: {e}")

@multipass_group.command(name="info")
@click.argument("name", required=False)
@click.option("--output", default="table", help="Output format (table, yaml, csv, json)")
@click.pass_context
def info(ctx, name, output):
    """
    Get consolidated system information or specific VM info
    """
    dryrun = ctx.obj.get('dryrun', False)
    
    if not name:
        # System-wide consolidated info
        if dryrun:
            banner("dryrun system info")
        else:
            provider = multipassProvider()
            
            banner("multipass version")
            version = provider.version()
            print(Printer.attribute(version, header=["Program", "Version"]))
            
            banner("multipass test")
            provider.test()
            
            banner("multipass vm defaults")
            provider.defaults(output=output)
            
            banner("multipass list")
            vm_list = provider.list()
            print(provider.Print(vm_list, kind="vm", output=output))
            
            banner("multipass images")
            image_list = provider.images()
            print(provider.Print(image_list, kind="image", output=output))
            
            Console.section("Image Selection Guide")
            Console.info("To choose a particular version of Ubuntu, use the --image flag during creation.")
            print("Example: cms multipass create my-vm --image ubuntu-22.04")
            print("Example: cms multipass create my-vm --image ubuntu-24.04")
            
            path = shutil.which("multipass")
            print(f"\nMultipass binary path: {path}")
        return

    if dryrun:
        banner(f"dryrun info {name}")
    else:
        provider = multipassProvider()
        info_data = provider.info(name)
        print(provider.Print(info_data, kind="info", output=output))

def register():
    """
    Register the multipass command group
    """
    return multipass_group