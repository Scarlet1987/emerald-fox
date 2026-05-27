#!/usr/bin/env python3
import os
import sys
import json
import socket
import urllib.request
import re
import subprocess

class EmeraldFoxOrchestrator:
    def __init__(self):
        self.ollama_url = "http://localhost:11434/api/chat"
        self.model_name = "gemma3:12b"
        self.bridge_port = 22026

    def cos_g_verification(self, code_str):
        """Strict structural safety filter for geometry code injections."""
        if not code_str:
            return False, "ERROR: Payload is completely empty."
        try: 
            compile(code_str, '<string>', 'exec')
        except SyntaxError as se: 
            return False, f"SYNTAX ERROR: Line {se.lineno}"
        
        if "while True" in code_str: 
            return False, "CRASH RISK: Infinite Loop detected."
        if "addObject" in code_str and "Shape" not in code_str: 
            return False, "ORPHAN RISK: Shape is unlinked."
        return True, "PASSED"

    def execute_system_app(self, app_name):
        """Dispatches applications checking native PATH and Flatpak layers."""
        clean_app = re.sub(r'[^a-zA-Z0-9_\-]', '', app_name).lower()
        
        try:
            subprocess.Popen([clean_app], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return f"🚀 Native OS Dispatched: Opening {clean_app}..."
        except FileNotFoundError:
            pass

        try:
            result = subprocess.run(["flatpak", "list", "--columns=application"], stdout=subprocess.PIPE, text=True)
            if result.returncode == 0:
                for app_id in result.stdout.splitlines():
                    if clean_app in app_id.lower():
                        subprocess.Popen(["flatpak", "run", app_id], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                        return f"📦 Flatpak Container Dispatched: Opening {app_id}..."
        except:
            pass

        return f"❌ System Search Failure: '{clean_app}' not found."

    def execute_terminal_command(self, bash_command):
        """Executes Bash commands on the metal with hard protections against crash risks."""
        # --- HARD CORE SHIELD ---
        # Block dangerous commands that threaten the filesystem or system stability
        forbidden_patterns = [
            r"\brm\s+-[rRfF]*\s+/",      # Absolute Root wipe attempts
            r":\(\)\{\s*:\s*\|&:\s*\};:", # Classical Fork-Bomb crash logic
            r"\bchmod\b.*-R.*\s+/",       # Recursive Root permission corruption
            r"dd\s+if=.*of=/dev/nvme",    # Direct NVMe block layout destruction
            r"dd\s+if=.*of=/dev/sd"       # Direct Storage block layout destruction
        ]
        
        for pattern in forbidden_patterns:
            if re.search(pattern, bash_command):
                return "❌ SHIELD TRIGGERED: Core system crash or filesystem risk blocked. Protection rule absolute."

        try:
            # Run the command through the native shell, capturing output
            result = subprocess.run(
                bash_command, 
                shell=True, 
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE, 
                text=True,
                timeout=30 # Safety threshold: stops hung processes from freezing your loop
            )
            
            output = ""
            if result.stdout:
                output += f"📝 Output:\n{result.stdout.strip()}\n"
            if result.stderr:
                output += f"⚠️ System Alerts/Errors:\n{result.stderr.strip()}\n"
            if not output:
                output = "✅ Command executed successfully with zero terminal output returned."
                
            return output
        except subprocess.TimeoutExpired:
            return "❌ Execution Timeout: Command took longer than 30 seconds to return. Safe drop applied."
        except Exception as e:
            return f"❌ Metal Execution Fault: {e}"

    def inject_to_geometry_bridge(self, python_code):
        """Pipes raw CAD coordinate math across the local network adapter."""
        passed, status = self.cos_g_verification(python_code)
        if not passed: 
            return f"❌ Safety Stop: {status}"
        try:
            data = json.dumps({"command": "execute", "payload": python_code})
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
                client.connect(('127.0.0.1', self.bridge_port))
                client.sendall(data.encode('utf-8'))
            return "📦 Geometry injected via local TCP Bridge!"
        except Exception as e: 
            return f"❌ Port {self.bridge_port} Link Failure: {e}"

    def interact(self, user_prompt):
        json_schema = {
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                    "enum": ["open_app", "inject_geometry", "run_terminal_command"]
                },
                "arguments": {
                    "type": "object",
                    "properties": {
                        "app_name": {"type": "string"},
                        "code": {"type": "string"},
                        "command": {"type": "string"}
                    }
                }
            },
            "required": ["name", "arguments"]
        }
        
        system_instruction = (
            "You are a local system orchestrator core with direct access to the host machine metal. "
            "Analyze the user request and choose the precise tool:\n"
            "1. To open a GUI program (e.g. Spotify, Blender), set name to 'open_app' and fill 'app_name'.\n"
            "2. To construct CAD/3D geometry code, set name to 'inject_geometry' and fill 'code'.\n"
            "3. To execute system checks, manage files, read hardware stats, or run bash utilities, set name to 'run_terminal_command' and fill 'command'."
        )
        
        payload = {
            "model": self.model_name,
            "messages": [
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": user_prompt}
            ],
            "stream": False,
            "format": json_schema
        }
        
        try:
            req = urllib.request.Request(self.ollama_url, data=json.dumps(payload).encode('utf-8'), headers={'Content-Type': 'application/json'})
            with urllib.request.urlopen(req) as response:
                res = json.loads(response.read().decode('utf-8'))
                content = res.get("message", {}).get("content", "").strip()
                
                data = json.loads(content)
                tool_name = data.get("name")
                args = data.get("arguments", {})
                
                if tool_name == "open_app":
                    print(self.execute_system_app(args.get("app_name")))
                elif tool_name == "inject_geometry":
                    print(self.inject_to_geometry_bridge(args.get("code")))
                elif tool_name == "run_terminal_command":
                    cmd_target = args.get("command")
                    if cmd_target:
                        print(f"⚙️ Running on Metal: {cmd_target}")
                        print(self.execute_terminal_command(cmd_target))
                    else:
                        print("🦊: Terminal tool invoked, but command field was left blank.")
                else:
                    print(f"🦊 Tool Mismatch: Unknown tool execution request '{tool_name}'.")
                    
        except Exception as e: 
            print(f"System Fault: {e}")

if __name__ == "__main__":
    o = EmeraldFoxOrchestrator()
    print("--- Emerald Fox TCP-Bridge Initialized ---")
    print(f"Active Compute Node: {o.model_name} | Target Port: {o.bridge_port}")
    
    while True:
        try:
            u = input("fox@lotus:~$ ")
            if u.lower() == "exit": 
                break
            if u.strip(): 
                o.interact(u)
        except (KeyboardInterrupt, SystemExit):
            break
        except Exception as e:
            print(f"\nLoop Exception Caught: {e}")
            continue
