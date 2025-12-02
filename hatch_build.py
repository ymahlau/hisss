import os
import subprocess
import sys
from hatchling.builders.hooks.plugin.interface import BuildHookInterface

class CustomBuildHook(BuildHookInterface):
    def initialize(self, version, build_data):
        print(">>> Hatch Build Hook: Starting C++ Compilation...")
        
        # --- PATH SETUP ---
        root = os.getcwd()
        
        # New location: src/hisss/cpp
        package_dir = os.path.join(root, "src", "hisss")
        cpp_root = os.path.join(package_dir, "cpp")
        
        alglib_dir = os.path.join(cpp_root, "alglib")
        source_dir = os.path.join(cpp_root, "source")
        compiled_dir = os.path.join(cpp_root, "compiled")
        
        # The output library sits directly in src/hisss
        lib_output = os.path.join(compiled_dir, "liblink.so")

        # Ensure directories exist
        os.makedirs(compiled_dir, exist_ok=True)

        # --- STEP 1: COMPILE ALGLIB ---
        # Flags: -w (suppress warnings), -O3, -fPIC
        print(f"   [1/3] Compiling Alglib files...")
        
        alglib_files = [
            "ap", "alglibinternal", "alglibmisc", 
            "linalg", "solvers", "optimization"
        ]
        
        alglib_flags = ["g++", "-w", "-std=c++11", "-c", "-fPIC", "-O3"]

        for name in alglib_files:
            src = os.path.join(alglib_dir, f"{name}.cpp")
            obj = os.path.join(compiled_dir, f"{name}.o")
            self._compile(alglib_flags, src, obj)

        # --- STEP 2: COMPILE PROJECT SOURCE ---
        # Flags: -Wall (show warnings), -O3, -fPIC
        print(f"   [2/3] Compiling Source files...")

        source_files = [
            "battlesnake", "battlesnake_helper", 
            "utils", "nash", "link"
        ]

        source_flags = ["g++", "-Wall", "-std=c++11", "-c", "-fPIC", "-O3"]

        for name in source_files:
            src = os.path.join(source_dir, f"{name}.cpp")
            obj = os.path.join(compiled_dir, f"{name}.o")
            self._compile(source_flags, src, obj)

        # --- STEP 3: LINKING ---
        print(f"   [3/3] Linking shared library...")
        
        # Combine all object files
        all_objects = [os.path.join(compiled_dir, f"{f}.o") for f in alglib_files + source_files]
        
        link_cmd = [
            "g++", "-Wall", "-std=c++11", "-O3", "-shared",
            "-Wl,-soname,liblink.so",
            "-o", lib_output
        ] + all_objects

        self._run_command(link_cmd)
        print(f">>> Success: {lib_output}")

    def _compile(self, flags, src, obj):
        # Basic caching: only compile if source is newer than object
        if not os.path.exists(obj) or os.path.getmtime(src) > os.path.getmtime(obj):
            print(f"       Compiling {os.path.basename(src)}")
            cmd = flags + [src, "-o", obj]
            self._run_command(cmd)

    def _run_command(self, cmd):
        try:
            subprocess.check_call(cmd)
        except subprocess.CalledProcessError:
            print(f"!!! Error executing: {' '.join(cmd)}")
            sys.exit(1)