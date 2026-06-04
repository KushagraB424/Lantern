import subprocess
import tempfile
import os

def execute_python(code: str, dataset_path: str, timeout: int = 15) -> dict:
    """
    Executes Python code in a restricted subprocess sandbox.
    """
    wrapper_code = f"""
import sys
import builtins
import io
import json

# Restrict imports by hijacking __import__
original_import = builtins.__import__
ALLOWED_MODULES = {{'pandas', 'numpy', 'plotly', 'plotly.express', 'plotly.graph_objects', 'json', 'math', 'datetime'}}

def safe_import(name, globals=None, locals=None, fromlist=(), level=0):
    base_name = name.split('.')[0]
    if globals and globals.get('__name__') == '__main__':
        if base_name not in ALLOWED_MODULES and name not in ALLOWED_MODULES:
            raise ImportError(f"Importing '{{name}}' is not allowed in this sandbox.")
    return original_import(name, globals, locals, fromlist, level)

builtins.__import__ = safe_import



# Set up environment variables/paths safely
DATASET_PATH = r"{dataset_path}"

# The user code
{code}
"""
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8') as f:
        f.write(wrapper_code)
        temp_file_path = f.name
        
    try:
        # Run subprocess
        result = subprocess.run(
            ["python", temp_file_path],
            capture_output=True,
            text=True,
            timeout=timeout,
            encoding='utf-8'
        )
        
        status = "success" if result.returncode == 0 else "error"
        
        return {
            "status": status,
            "stdout": result.stdout,
            "stderr": result.stderr
        }
    except subprocess.TimeoutExpired as e:
        return {
            "status": "error",
            "stdout": e.stdout.decode('utf-8', errors='ignore') if e.stdout else "",
            "stderr": f"Execution timed out after {timeout} seconds."
        }
    except Exception as e:
        return {
            "status": "error",
            "stdout": "",
            "stderr": str(e)
        }
    finally:
        if os.path.exists(temp_file_path):
            try:
                os.remove(temp_file_path)
            except:
                pass
