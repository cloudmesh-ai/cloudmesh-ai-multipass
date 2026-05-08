import platform
import shutil
import subprocess
import sys
import click
from cloudmesh.ai.common.io import console
from cloudmesh.ai.common.util import yn_choice
from cloudmesh.ai.common.debug import VERBOSE
from cloudmesh.ai.common.io import banner
from cloudmesh.ai.common.Printer import Printer
from cloudmesh.ai.multipass.MultipassProvider import MultipassProvider


@click.group(help="Manage Multipass virtual machines and system configuration.")
@click.option("--dryrun", is_flag=True, help="Dry run mode")
@click.pass_context
def multipass_group(ctx, dryrun):
    """
    Manage Multipass virtual machines and system configuration.

    This command group provides an interface to install Multipass,
    retrieve system information, and manage Ubuntu VMs on your host.
    """
    ctx.ensure_object(dict)
    ctx.obj["dryrun"] = dryrun


@multipass_group.command(help="Uninstall Multipass from the host system.")
@click.pass_context
def uninstall(ctx):
    """
    Uninstall Multipass from the host system.
    """
    dryrun = ctx.obj.get("dryrun", False)
    os_type = platform.system()

    if os_type == "Darwin":
        console.print("Uninstalling Multipass on macOS...")
        # Try Homebrew first
        if shutil.which("brew"):
            if yn_choice("Try uninstalling via Homebrew?"):
                cmd = "brew uninstall multipass"
                if dryrun:
                    banner(f"dryrun: {cmd}")
                else:
                    subprocess.run(cmd, shell=True)

        if yn_choice("Also remove .pkg installation (stop daemon and remove app)?"):
            cmds = [
                "sudo launchctl unload /Library/LaunchDaemons/com.canonical.multipassd.plist",
                "sudo rm -rf /Applications/Multipass.app",
            ]
            for cmd in cmds:
                if dryrun:
                    banner(f"dryrun: {cmd}")
                else:
                    # Use stderr=subprocess.DEVNULL to ignore errors if the service/file is already gone
                    subprocess.run(cmd, shell=True, stderr=subprocess.DEVNULL)

    elif os_type == "Linux":
        console.print("Uninstalling Multipass on Linux...")
        cmd = "sudo snap remove multipass"
        if dryrun:
            banner(f"dryrun: {cmd}")
        else:
            subprocess.run(cmd, shell=True)

        if yn_choice(
            "Remove snap data directory (/var/snap/multipass) for a clean removal?"
        ):
            cmd = "sudo rm -rf /var/snap/multipass"
            if dryrun:
                banner(f"dryrun: {cmd}")
            else:
                subprocess.run(cmd, shell=True)
    else:
        console.error(f"Uninstall not implemented for OS: {os_type}")
        return

    console.msg("Uninstall process completed.")


@multipass_group.command(help="Install Multipass on the host system.")
@click.pass_context
def install(ctx):
    """
    Install Multipass on the host system.

    Automatically detects the operating system and uses the appropriate
    package manager (Homebrew for macOS, Snap for Linux) to install Multipass.
    """
    dryrun = ctx.obj.get("dryrun", False)
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
        console.print(
            "Multipass for Windows must be installed via the official installer."
        )
        console.print("Please visit: https://multipass.run/install")
        return
    else:
        console.error(f"Unsupported OS: {os_type}")
        return

    if yn_choice(f"Do you want to install Multipass using '{install_cmd}'?"):
        try:
            subprocess.run(install_cmd, shell=True, check=True)
            console.msg("Multipass installed successfully.")

            console.print("\nVerifying installation...")
            subprocess.run("multipass version", shell=True)
        except subprocess.CalledProcessError as e:
            console.error(f"Installation failed: {e}")


@multipass_group.command(name="enable", help="Enable the Multipass daemon on macOS.")
@click.pass_context
def enable(ctx):
    """
    Enable the Multipass daemon on macOS.
    """
    dryrun = ctx.obj.get("dryrun", False)
    cmd = "sudo launchctl kickstart -k system/com.canonical.multipassd"
    if dryrun:
        banner(f"dryrun enable: {cmd}")
    else:
        try:
            subprocess.run(cmd, shell=True, check=True)
            console.msg("Multipass daemon enabled successfully.")
        except subprocess.CalledProcessError as e:
            console.error(f"Failed to enable Multipass daemon: {e}")


@multipass_group.command(name="disable", help="Disable the Multipass daemon on macOS.")
@click.pass_context
def disable(ctx):
    """
    Disable the Multipass daemon on macOS.
    """
    dryrun = ctx.obj.get("dryrun", False)
    cmd = "sudo launchctl unload /Library/LaunchDaemons/com.canonical.multipassd.plist"
    if dryrun:
        banner(f"dryrun disable: {cmd}")
    else:
        try:
            subprocess.run(cmd, shell=True, check=True)
            console.msg("Multipass daemon disabled successfully.")
        except subprocess.CalledProcessError as e:
            console.error(f"Failed to disable Multipass daemon: {e}")


@multipass_group.command(
    name="run", help="Ensure a VM is running (launch if missing, start if stopped)."
)
@click.argument("name")
@click.option("--cpus", default="1", help="Number of CPUs to allocate.")
@click.option("--memory", default="1G", help="Amount of memory to allocate (e.g. 2G).")
@click.option("--disk", default="5G", help="Disk size to allocate (e.g. 20G).")
@click.pass_context
def run(ctx, name, cpus, memory, disk):
    """
    Ensure a VM is running. If the VM does not exist, it will be launched.
    If it exists but is stopped, it will be started.
    """
    dryrun = ctx.obj.get("dryrun", False)
    provider = MultipassProvider()

    console.print(f"Checking if VM '{name}' exists...")
    vms = provider.list()
    exists = any(vm.get("name") == name for vm in vms)

    if exists:
        console.print(f"VM '{name}' already exists. Attempting to start it...")
        if dryrun:
            banner(f"dryrun: multipass start {name}")
        else:
            result = provider.start(name)
            if not result.get("success"):
                console.error(f"Error: {result.get('error')}")
    else:
        console.print(f"Launching a new VM: {name}...")
        if dryrun:
            banner(f"dryrun: multipass launch --name {name} --cpus {cpus} --memory {memory} --disk {disk}")
        else:
            result = provider.launch(name, cpus, memory, disk)
            if not result.get("success"):
                console.error(f"Error: {result.get('error')}")

    # Verify status
    vms = provider.list()
    vm = next((v for v in vms if v.get("name") == name), None)
    if vm and vm.get("state") == "Running":
        console.print("------------------------------------------------")
        console.print(f"SUCCESS: VM '{name}' is now running.")
        console.print(f"To enter the VM, run: multipass shell {name}")
        console.print("------------------------------------------------")
    else:
        console.error(
            f"ERROR: Failed to start the VM '{name}'. Please check 'multipass list' for details."
        )


@multipass_group.command(name="version", help="Show Multipass version information.")
@click.pass_context
def version(ctx):
    """
    Show Multipass version information.
    """
    dryrun = ctx.obj.get("dryrun", False)
    os_type = platform.system()

    console.print("\n[bold]Package Manager Info:[/bold]")
    if os_type == "Linux":
        console.print("Linux (Snap):")
        subprocess.run("snap info multipass", shell=True)
    elif os_type == "Darwin":
        console.print("macOS (Homebrew):")
        if shutil.which("brew"):
            subprocess.run("brew info multipass", shell=True)
        else:
            console.print("Homebrew not found.")

    console.print("\n[bold]Multipass Version:[/bold]")
    if dryrun:
        banner("dryrun multipass version")
    else:
        provider = MultipassProvider()
        console.print(provider.version())


@multipass_group.command(name="gui", help="Launch the Multipass GUI application.")
def gui():
    """
    Launch the Multipass GUI application.
    """
    os_type = platform.system()
    if os_type == "Darwin":
        console.print("Launching Multipass.app...")
        subprocess.run("open -a Multipass", shell=True)
    elif os_type == "Windows":
        console.print("Launching Multipass GUI...")
        # On Windows, we can try to start the process if we know the path,
        # but usually, it's a system tray app.
        subprocess.run("start multipass", shell=True)
    else:
        console.error(f"Native GUI not available for OS: {os_type}")
        console.print("Please use the Cloudmesh AI Panel for a graphical interface.")


@multipass_group.command(
    name="status",
    help="Retrieve Multipass system information or details for a specific VM.",
)
@click.argument("name", required=False)
@click.option(
    "--output", default="table", help="Output format (table, yaml, csv, json)"
)
@click.pass_context
def status(ctx, name, output):
    """
    Retrieve Multipass system information or details for a specific VM.

    If no VM name is provided, it displays a consolidated report including:
    - Multipass version and connectivity test
    - Default VM configuration
    - List of all existing VMs
    - Available Ubuntu images
    - Available network interfaces

    If a VM name is provided, it displays detailed information for that specific instance.
    """
    dryrun = ctx.obj.get("dryrun", False)

    if not name:
        # System-wide consolidated info
        if dryrun:
            banner("dryrun system info")
        else:
            provider = MultipassProvider()

            banner("multipass version")
            version = provider.version()
            print(Printer.attribute(version, header=["Program", "Version"]))

            banner("multipass test")
            subprocess.run("multipass test", shell=True)

            banner("multipass images")
            image_list = provider.images()
            for item in image_list:
                print(item.get("output"))

            banner("multipass networks")
            network_list = provider.networks()
            for item in network_list:
                print(item.get("output"))

            console.print("\n[bold]Image Selection Guide[/bold]\n")
            console.print(
                "To choose a particular version of Ubuntu, use the --image flag during creation."
            )
            print("Example: cms multipass create my-vm --image ubuntu-22.04")
            print("Example: cms multipass create my-vm --image ubuntu-24.04")

            path = shutil.which("multipass")
            print(f"\nMultipass binary path: {path}")
        return

    if dryrun:
        banner(f"dryrun info {name}")
    else:
        provider = MultipassProvider()
        result = provider.info(name)
        if result.get("success"):
            print(result.get("data"))
        else:
            console.error(f"Error: {result.get('error')}")


entry_point = multipass_group


def register(cli=None):
    """
    Register the multipass command group
    """
    if cli:
        cli.add_command(multipass_group, name="multipass")

    def main(args=None, standalone_mode=False):
        # If args is None, we must manually slice sys.argv to remove 'cmc' and 'multipass'
        if args is None:
            try:
                idx = sys.argv.index("multipass")
                args = sys.argv[idx + 1 :]
            except (ValueError, IndexError):
                args = []
        elif len(args) > 0 and args[0] == "multipass":
            args = args[1:]

        try:
            multipass_group.main(args=args, standalone_mode=standalone_mode)
        except SystemExit:
            # Prevent click from exiting the entire cmc process
            pass

    return main


# Remove the make_context hack to see if it's causing the "Usage: cmc" issue
