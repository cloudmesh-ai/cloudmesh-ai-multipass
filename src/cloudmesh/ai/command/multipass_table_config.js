window.MultipassTableConfig = {
    columns: [
        { 
            title: "Actions", 
            formatter: function(cell) {
                const row = cell.getData();
                const container = document.createElement('div');
                container.className = 'flex gap-1 justify-start';
                
                window.MultipassTableConfig.rowActions.forEach(action => {
                    const btn = document.createElement('button');
                    btn.className = 'p-1 px-2 text-xs rounded bg-gray-200 dark:bg-gray-700 hover:bg-gray-300 dark:hover:bg-gray-600 transition-colors flex items-center gap-1';
                    btn.title = action.label;
                    btn.innerHTML = `<i class="${action.icon} text-[10px]"></i>`;
                    btn.onclick = () => action.callback(row);
                    container.appendChild(btn);
                });
                
                return container;
            }, 
            width: 150, 
            headerSort: false 
        },
        { title: "VM Name", field: "name", sortable: true },
        { title: "State", field: "state", sortable: true },
        { title: "IPv4", field: "ipv4", sortable: true },
        { title: "IPv6", field: "ipv6", sortable: true },
        { title: "CPUs", field: "cpus", sortable: true },
        { title: "Memory", field: "memory", sortable: true },
        { title: "Disk", field: "disk", sortable: true },
        { title: "Image", field: "image", sortable: true },
    ],
    actions: [
        {
            label: "+ Add VM",
            icon: "fa-solid fa-plus",
            callback: async () => {
                const name = prompt("Enter VM Name:");
                if (!name) return;
                
                const cpus = prompt("CPUs (default 1):", "1") || "1";
                const memory = prompt("Memory (default 1G):", "1G") || "1G";
                const disk = prompt("Disk (default 5G):", "5G") || "5G";

                try {
                    const response = await fetch(`/api/plugin/multipass/add_vm?name=${encodeURIComponent(name)}&cpus=${encodeURIComponent(cpus)}&memory=${encodeURIComponent(memory)}&disk=${encodeURIComponent(disk)}`);
                    const result = await response.json();
                    if (result.success) {
                        alert("VM launched successfully!");
                        window.location.reload();
                    } else {
                        alert("Error: " + result.error);
                    }
                } catch (e) {
                    alert("Request failed: " + e);
                }
            }
        },
        {
            label: "Launch GUI",
            icon: "fa-solid fa-desktop",
            callback: async () => {
                try {
                    const response = await fetch(`/api/plugin/multipass/launch_gui`);
                    const result = await response.json();
                    if (!result.success) alert("Error: " + result.error);
                } catch (e) {
                    alert("Request failed: " + e);
                }
            }
        }
    ],
    rowActions: [
        {
            label: "Terminal",
            icon: "fa-solid fa-terminal",
            callback: async (row) => {
                const response = await fetch(`/api/plugin/multipass/open_terminal?name=${encodeURIComponent(row.name)}`);
                const result = await response.json();
                if (!result.success) alert(result.error);
            }
        },
        {
            label: "Stop",
            icon: "fa-solid fa-stop",
            callback: async (row) => {
                const response = await fetch(`/api/plugin/multipass/pause_vm?name=${encodeURIComponent(row.name)}`);
                const result = await response.json();
                if (result.success) {
                    alert(result.message);
                    window.location.reload();
                } else alert(result.error);
            }
        },
        {
            label: "Pause",
            icon: "fa-solid fa-pause",
            callback: async (row) => {
                const response = await fetch(`/api/plugin/multipass/pause_vm?name=${encodeURIComponent(row.name)}`);
                const result = await response.json();
                if (result.success) {
                    alert(result.message);
                    window.location.reload();
                } else alert(result.error);
            }
        },
        {
            label: "Resume",
            icon: "fa-solid fa-play",
            callback: async (row) => {
                const response = await fetch(`/api/plugin/multipass/resume_vm?name=${encodeURIComponent(row.name)}`);
                const result = await response.json();
                if (result.success) {
                    alert(result.message);
                    window.location.reload();
                } else alert(result.error);
            }
        },
        {
            label: "Delete",
            icon: "fa-solid fa-trash",
            callback: async (row) => {
                if (!confirm(`Are you sure you want to delete VM ${row.name}?`)) return;
                const response = await fetch(`/api/plugin/multipass/delete_vm?name=${encodeURIComponent(row.name)}`);
                const result = await response.json();
                if (result.success) {
                    alert(result.message);
                    window.location.reload();
                } else alert(result.error);
            }
        }
    ],
    log: function(message, level = 'info') {
        const logsContainer = document.getElementById('multipass-error-logs');
        const timestamp = new Date().toLocaleTimeString();
        const colorClass = level === 'error' ? 'text-red-500 dark:text-red-400' : 'text-gray-600 dark:text-gray-300';
        const levelLabel = level === 'error' ? '[ERROR]' : '[INFO]';
        
        if (logsContainer) {
            const logEntry = document.createElement('div');
            logEntry.className = `mb-1 ${colorClass}`;
            logEntry.innerHTML = `<span class="text-gray-400 mr-2">${timestamp}</span><span class="font-bold mr-2">${levelLabel}</span>${message}`;
            logsContainer.appendChild(logEntry);
            while (logsContainer.children.length > 100) {
                logsContainer.removeChild(logsContainer.firstChild);
            }
            const panel = document.getElementById('multipass-error-panel');
            if (panel) panel.scrollTop = panel.scrollHeight;
        }
    },

    pollLogs: async function() {
        try {
            const res = await fetch('/api/plugin/multipass/get_logs');
            if (!res.ok) return;
            const data = await res.json();
            if (!data.logs) return;
            
            const logsContainer = document.getElementById('multipass-error-logs');
            if (!logsContainer) return;

            // For simplicity in this implementation, we just append new logs
            // In a real app, we'd track the last log index
            data.logs.forEach(log => this.log(log));
        } catch (e) {
            // Silently fail polling
        }
    },

    toggleErrorPanel: function() {
        const panel = document.getElementById('multipass-error-panel');
        const logs = document.getElementById('multipass-error-logs');
        const icon = document.getElementById('multipass-error-toggle-icon');
        if (!panel || !logs || !icon) return;

        const isMinimized = logs.classList.toggle('hidden');
        if (isMinimized) {
            panel.className = 'h-auto overflow-hidden bg-gray-50 dark:bg-gray-900 text-gray-900 dark:text-gray-100 font-mono text-xs p-2 border-t border-gray-200 dark:border-gray-700';
            icon.className = 'fa-solid fa-chevron-down text-gray-400 dark:text-gray-500 transition-transform';
        } else {
            panel.className = 'h-40 overflow-y-auto bg-gray-50 dark:bg-gray-900 text-gray-900 dark:text-gray-100 font-mono text-xs p-2 border-t border-gray-200 dark:border-gray-700';
            icon.className = 'fa-solid fa-chevron-up text-gray-400 dark:text-gray-500 transition-transform';
        }
    },

    render: function(elementId, data) {
        try {
            if (typeof Tabulator === 'undefined') {
                throw new Error("Tabulator library is not loaded");
            }

            const container = document.querySelector(elementId);
            if (!container) throw new Error(`Element ${elementId} not found`);

            container.innerHTML = ''; 
            
            const mainWrapper = document.createElement('div');
            mainWrapper.className = 'flex flex-col h-full w-full';
            container.appendChild(mainWrapper);

            const contentWrapper = document.createElement('div');
            contentWrapper.className = 'flex-1 overflow-hidden';
            
            const tableEl = document.createElement('div');
            tableEl.className = 'w-full h-full';
            contentWrapper.appendChild(tableEl);
            mainWrapper.appendChild(contentWrapper);

            const errorPanel = document.createElement('div');
            errorPanel.id = 'multipass-error-panel';
            errorPanel.className = 'h-40 overflow-y-auto bg-gray-50 dark:bg-gray-900 text-gray-900 dark:text-gray-100 font-mono text-xs p-2 border-t border-gray-200 dark:border-gray-700';
            
            const header = document.createElement('div');
            header.className = 'flex items-center justify-between cursor-pointer mb-1 p-1 rounded hover:bg-gray-200 dark:hover:bg-gray-700 transition-colors';
            header.onclick = () => this.toggleErrorPanel();
            header.innerHTML = `
                <span class="text-gray-500 dark:text-gray-400 font-semibold uppercase text-[10px] tracking-wider">System logs</span>
                <i id="multipass-error-toggle-icon" class="fa-solid fa-chevron-up text-gray-400 dark:text-gray-500 transition-transform"></i>
            `;
            
            const logsContainer = document.createElement('div');
            logsContainer.id = 'multipass-error-logs';
            
            errorPanel.appendChild(header);
            errorPanel.appendChild(logsContainer);
            mainWrapper.appendChild(errorPanel);

            const table = new Tabulator(tableEl, {
                data: data,
                layout: "fitColumns",
                height: "100%",
                columns: this.columns,
            });

            setInterval(() => this.pollLogs(), 5000);

            return table;
        } catch (e) {
            console.error("[MultipassTableConfig] Render error:", e);
            throw e;
        }
    }
};
