import subprocess
from pathlib import Path
from typing import Any
from cloudmesh.ai.command.plugin import PanelPlugin
from cloudmesh.ai.multipass.MultipassProvider import MultipassProvider
from cloudmesh.ai.common.io import console

class MultipassPlugin(PanelPlugin):
    @property
    def plugin_id(self) -> str:
        return "multipass"

    @property
    def plugin_name(self) -> str:
        return "Multipass VM Manager"

    @property
    def plugin_icon(self) -> str:
        return "fa-solid fa-server"

    @property
    def plugin_description(self) -> str:
        return "Manage Multipass virtual machines and system status."

    def _log(self, message: str):
        """Writes events to the shared AI Panel log file."""
        log_file = Path.home() / ".config" / "cloudmesh" / "ai" / "panel.log"
        log_file.parent.mkdir(parents=True, exist_ok=True)
        with open(log_file, "a") as f:
            f.write(f"[Multipass] {message}\n")

    def __init__(self):
        """Initializes the MultipassPlugin with a provider."""
        self.provider = MultipassProvider()

    def get_data(self) -> Any:
        """Returns the list of Multipass VMs for the table."""
        try:
            data = self.provider.list()
            if not isinstance(data, list):
                self._log(f"Unexpected data format from provider: {type(data)}")
                return []
            return data
        except Exception as e:
            self._log(f"Error fetching VM data: {str(e)}")
            return []

    def get_logs(self) -> Dict[str, Any]:
        """Returns the system logs for Multipass."""
        # For now, we return a mock set of logs.
        return {"logs": ["Multipass plugin initialized", "Fetching VM list..."]}

    def launch_gui(self):
        """Launches the Multipass GUI application."""
        self._log("Request to launch Multipass GUI")
        return self.provider.launch_gui()

    def add_vm(self, name: str, cpus: str = "1", memory: str = "1G", disk: str = "5G"):
        """Launches a new Multipass VM."""
        self._log(f"Request to add VM: {name} (CPU: {cpus}, Mem: {memory}, Disk: {disk})")
        result = self.provider.launch(name, cpus, memory, disk)
        if result.get("success"):
            self._log(f"Successfully launched VM: {name}")
        else:
            self._log(f"Failed to launch VM {name}: {result.get('error')}")
        return result

    def run_vm(self, name: str):
        """Starts a stopped VM."""
        self._log(f"Request to start VM: {name}")
        result = self.provider.start(name)
        if result.get("success"):
            self._log(f"Successfully started VM: {name}")
        return result

    def pause_vm(self, name: str):
        """Pauses a running VM."""
        self._log(f"Request to pause VM: {name}")
        result = self.provider.pause(name)
        if result.get("success"):
            self._log(f"Successfully paused VM: {name}")
        return result

    def resume_vm(self, name: str):
        """Resumes a paused VM."""
        self._log(f"Request to resume VM: {name}")
        result = self.provider.start(name)
        if result.get("success"):
            self._log(f"Successfully resumed VM: {name}")
        return result

    def delete_vm(self, name: str):
        """Deletes a VM."""
        self._log(f"Request to delete VM: {name}")
        result = self.provider.delete(name)
        if result.get("success"):
            self._log(f"Successfully deleted VM: {name}")
        return result

    def open_terminal(self, name: str):
        """Opens a terminal for the VM."""
        try:
            self._log(f"Request to open terminal for VM: {name}")
            cmd = f"multipass shell {name}"
            # Since this is a server-side call, we can't 'open' a terminal on the user's machine
            # unless we use osascript like in the monitor plugin.
            import platform
            if platform.system() == "Darwin":
                iterm_script = f'tell application "iTerm" to create window with default profile, then tell current session of current window to write text "{cmd}"'
                subprocess.run(["osascript", "-e", iterm_script], check=True)
                subprocess.run(["osascript", "-e", 'tell application "iTerm" to activate'], check=True)
                return {"success": True, "message": f"iTerm2 opened for {name}"}
            else:
                return {"success": False, "error": "Terminal automation only supported on macOS"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def get_assets(self):
        """Returns the paths to the JS and CSS configuration files."""
        return {
            "multipass_table_config.js": "cloudmesh-ai-multipass/src/cloudmesh/ai/command/multipass_table_config.js",
            "multipass_table_styles.css": "cloudmesh-ai-multipass/src/cloudmesh/ai/command/multipass_table_styles.css",
        }