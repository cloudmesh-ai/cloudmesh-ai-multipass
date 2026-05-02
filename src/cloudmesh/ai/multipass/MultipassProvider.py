import subprocess
import json
import platform
from typing import Any, List, Dict, Optional
from cloudmesh.ai.common.io import console

class MultipassProvider:
    """Python API to interface with the Multipass command line.

    This provider encapsulates the subprocess calls to the multipass binary,
    providing a clean Pythonic interface for managing Multipass VMs.
    """

    def __init__(self):
        """Initializes the MultipassProvider."""
        self.bin = "multipass"

    def _run(self, args: List[str], check: bool = True) -> subprocess.CompletedProcess:
        """Internal helper to run multipass commands.

        Args:
            args (List[str]): List of arguments to pass to the multipass binary.
            check (bool): Whether to raise a CalledProcessError on failure.

        Returns:
            subprocess.CompletedProcess: The result of the command execution.
        """
        cmd = [self.bin] + args
        return subprocess.run(cmd, capture_output=True, text=True, check=check)

    def version(self) -> str:
        """Returns the Multipass version.

        Returns:
            str: The version string returned by 'multipass version'.
        """
        try:
            res = self._run(["version"])
            return res.stdout.strip()
        except Exception as e:
            return f"Error getting version: {str(e)}"

    def list(self) -> List[Dict[str, Any]]:
        """Returns a list of all VMs with enriched metadata.

        Returns:
            List[Dict[str, Any]]: A list of dictionaries containing VM metadata.
        """
        try:
            res = self._run(["list", "--format", "json"])
            data = json.loads(res.stdout)
            vms = data.get("list", []) if isinstance(data, dict) else data
            
            if not isinstance(vms, list):
                return []

            enriched_vms = []
            for vm in vms:
                name = vm.get("name")
                # Convert IP arrays to comma-separated strings for the table
                ipv4 = vm.get("ipv4", [])
                ipv6 = vm.get("ipv6", [])
                ipv4_str = ", ".join(ipv4) if isinstance(ipv4, list) else str(ipv4)
                ipv6_str = ", ".join(ipv6) if isinstance(ipv6, list) else str(ipv6)
                
                vm_data = {
                    **vm,
                    "ipv4": ipv4_str,
                    "ipv6": ipv6_str,
                }

                # Enrich with detailed info using JSON format
                if name:
                    info_res = self.info(name)
                    if info_res.get("success"):
                        info_data = info_res["data"]
                        vm_info = info_data.get("info", {}).get(name, {})
                        
                        # Extract CPU
                        cpus = vm_info.get("cpu_count")
                        
                        # Extract Memory (handle dict or empty)
                        mem_data = vm_info.get("memory", {})
                        memory = mem_data.get("total", "N/A") if isinstance(mem_data, dict) else "N/A"
                        
                        # Extract Disk (handle dict or empty)
                        disk_data = vm_info.get("disks", {})
                        disk = "N/A"
                        if isinstance(disk_data, dict) and disk_data:
                            # Sum up disk sizes if multiple disks exist
                            total_disk = 0
                            for d in disk_data.values():
                                total_disk += d.get("size", 0)
                            disk = f"{total_disk}B" if total_disk > 0 else "N/A"

                        vm_data.update({
                            "cpus": cpus if cpus else "N/A",
                            "memory": memory,
                            "disk": disk,
                            "image": vm_info.get("image_hash", "N/A"),
                        })
                
                enriched_vms.append(vm_data)
                
            return enriched_vms
        except Exception as e:
            console.error(f"Error listing VMs: {str(e)}")
            return []

    def launch(self, name: str, cpus: str = "1", memory: str = "1G", disk: str = "5G", image: Optional[str] = None) -> Dict[str, Any]:
        """Launches a new Multipass VM.

        Args:
            name (str): The name of the VM to create.
            cpus (str): Number of CPUs to allocate. Defaults to "1".
            memory (str): Amount of memory to allocate. Defaults to "1G".
            disk (str): Disk size to allocate. Defaults to "5G".
            image (Optional[str]): The image to use for the VM. Defaults to None.

        Returns:
            Dict[str, Any]: A dictionary containing 'success' (bool) and 'message' or 'error'.
        """
        try:
            args = ["launch", "--name", name, "--cpus", cpus, "--memory", memory, "--disk", disk]
            if image:
                args.extend(["--image", image])
            
            self._run(args)
            return {"success": True, "message": f"VM {name} launched successfully"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def start(self, name: str) -> Dict[str, Any]:
        """Starts a stopped VM.

        Args:
            name (str): The name of the VM to start.

        Returns:
            Dict[str, Any]: A dictionary containing 'success' (bool) and 'message' or 'error'.
        """
        try:
            self._run(["start", name])
            return {"success": True, "message": f"VM {name} started"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def stop(self, name: str) -> Dict[str, Any]:
        """Stops a running VM.

        Args:
            name (str): The name of the VM to stop.

        Returns:
            Dict[str, Any]: A dictionary containing 'success' (bool) and 'message' or 'error'.
        """
        try:
            self._run(["stop", name])
            return {"success": True, "message": f"VM {name} stopped"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def pause(self, name: str) -> Dict[str, Any]:
        """Pauses a running VM.

        Args:
            name (str): The name of the VM to pause.

        Returns:
            Dict[str, Any]: A dictionary containing 'success' (bool) and 'message' or 'error'.
        """
        try:
            self._run(["pause", name])
            return {"success": True, "message": f"VM {name} paused"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def delete(self, name: str, purge: bool = True) -> Dict[str, Any]:
        """Deletes a VM.

        Args:
            name (str): The name of the VM to delete.
            purge (bool): Whether to purge the VM immediately. Defaults to True.

        Returns:
            Dict[str, Any]: A dictionary containing 'success' (bool) and 'message' or 'error'.
        """
        try:
            args = ["delete", name]
            if purge:
                args.append("--purge")
            self._run(args)
            return {"success": True, "message": f"VM {name} deleted"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def info(self, name: str) -> Dict[str, Any]:
        """Returns detailed information for a specific VM in JSON format.

        Args:
            name (str): The name of the VM.

        Returns:
            Dict[str, Any]: The parsed JSON output of 'multipass info <name> --format json'.
        """
        try:
            res = self._run(["info", name, "--format", "json"])
            return {"success": True, "data": json.loads(res.stdout)}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def images(self) -> List[Dict[str, Any]]:
        """Lists available Ubuntu images.

        Returns:
            List[Dict[str, Any]]: A list of available images.
        """
        try:
            res = self._run(["images"])
            return [{"output": res.stdout}]
        except Exception as e:
            console.error(f"Error listing images: {str(e)}")
            return []

    def networks(self) -> List[Dict[str, Any]]:
        """Lists available network interfaces.

        Returns:
            List[Dict[str, Any]]: A list of available networks.
        """
        try:
            res = self._run(["networks"])
            return [{"output": res.stdout}]
        except Exception as e:
            console.error(f"Error listing networks: {str(e)}")
            return []

    def launch_gui(self) -> Dict[str, Any]:
        """Launches the Multipass GUI application.

        Returns:
            Dict[str, Any]: A dictionary containing 'success' (bool) and 'message' or 'error'.
        """
        try:
            if platform.system() == "Darwin":
                subprocess.run(["open", "-a", "Multipass"], check=True)
                return {"success": True, "message": "Multipass GUI launched"}
            else:
                return {"success": False, "error": "Multipass GUI launch only supported on macOS"}
        except Exception as e:
            return {"success": False, "error": str(e)}
