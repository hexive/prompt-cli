import subprocess
import time
import shutil

from pathlib import Path
from util import *

def start_qdrant():
    console.print("--starting qdrant ... (it can take several seconds to load BIG DATA)")
    cmd = [
        "docker", "run", "-d",
        "-p", "6333:6333", "-p", "6334:6334",
        "-v", "qdrant_storage:/qdrant/storage:z",
        "-e", "QDRANT__TELEMETRY_DISABLED=true",
        "qdrant/qdrant"
    ]
    subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def start_stable_diffusion():
    console.print("--starting stable diffusion ...")
    script_path = config('image','stable_diffusion_path')
    activate_venv =  f". {script_path.split("webui.sh")[0].rstrip("/")}/venv/bin/activate"
    cmd = f"{activate_venv} && bash {script_path} "
    subprocess.Popen(cmd,stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,shell=True)

def wait_for_qdrant(url):
    timeout = 30  # 30 second timeout
    end_time = time.time() + timeout
    while time.time() < end_time:
        if check_service(url):
            print("--qdrant is up!")
            return True
        print("...")
        time.sleep(5)
    console.print("There was a problem with the qdrant startup -- maybe try to start it manually?", style=f"bold {error_color}")
    return False

def wait_for_image_diffusion(url):
    timeout = 30  # 30 second timeout
    end_time = time.time() + timeout
    while time.time() < end_time:
        if check_service(url):
            print("--stable diffusion is up!")
            return True
        print("...")
        time.sleep(5)
    return False

def preflight():  
    console.print("Checking External Programs:")

    # Check and start Qdrant if needed
    url = config('search','qdrant_url') + "/dashboard"
    if check_service(url):
        console.print("--qdrant is up!")
    else:
        if config('search','qdrant_start',bool):
            start_qdrant()
            time.sleep(3)
            if not wait_for_qdrant(url):
                exit(1)
        else:  
            console.print("--qdrant not found.", style=f"bold {error_color}")
            console.print("  start it manually and try again.\n", style=f"bold {error_color}")
            exit(1)      

    # Check and start Image Diffusion if needed
    url = config('image','image-gen_url') + "/docs"
    if check_service(url):
        console.print("--stable diffusion is up!")
    else:
        if config('image','stable_diffusion_start',bool):
            start_stable_diffusion()
            time.sleep(3)
            if not wait_for_image_diffusion(url):
                console.print("--there was a problem auto-starting stable diffusion", style=f"bold {error_color}")
                console.print("  start it manually before generating images.", style=f"bold {error_color}")
        else:
            console.print("--stable diffusion not found.", style=f"bold {error_color}")
            console.print("  start it manually before generating images.", style=f"bold {error_color}")

    # Check kitty icat dependency and 
    # Check terminal image compatibility
    try:
        result = subprocess.run(['kitty', 'icat', '--detect-support'], capture_output=True, text=True, check=False)
        if result.returncode == 0:
            console.print("--your terminal supports image display!")
        else:
            console.print("--your terminal cannot display images.", style=f"bold {error_color}")
            console.print("  try a terminal that supports the kitty graphics protocol", style=f"bold {error_color}")
            console.print("  eg. kitty, WezTerm, Konsole", style=f"bold {error_color}")

    except:
        console.print("--icat not found.", style=f"bold {error_color}")
        console.print("  we use this to stream images to your terminal", style=f"bold {error_color}")
        console.print("  icat is part of kitty. we need 'kitty' on your os", style=f"bold {error_color}")
        console.print("  even if you use another terminal. (eg. apt install kitty)", style=f"bold {error_color}")

    # Check imagemagic dependency
    if shutil.which("convert") is not None:
        pass
    else:
        console.print("--imagemagick not found.", style=f"bold {error_color}")
        console.print("  we use this to resize large images for terminal view", style=f"bold {error_color}")
        console.print("  your generated images will not be displayed", style=f"bold {error_color}")
        console.print("  (apt install imagemagick, for example)", style=f"bold {error_color}")

    # Check llm & encoding models exist where they should:
    llm_model_path = install_path() + "/models/Mistral-7B-Instruct-v0.3-Q6_K.gguf"
    if os.path.exists(llm_model_path):
        pass
    else:
        console.print("--llm model not found at expected location", style=f"bold {error_color}")
        console.print(f"  {llm_model_path}", style=f"bold {error_color}")
        console.print(f"  you may run prompt-cli/scripts/model_download.py to get it", style=f"bold {error_color}")
        console.print(f"  search will still work but not '/chat'\n", style=f"bold {error_color}")

    encode_model_path = install_path() + "/models/BAII/model.safetensors"
    if os.path.exists(encode_model_path):
        pass
    else:
        console.print("--vector encoding model not found at expected location", style=f"bold {error_color}")
        console.print(f"  {encode_model_path}", style=f"bold {error_color}")
        console.print(f"  you may run prompt-cli/scripts/model_download.py to get it\n", style=f"bold {error_color}")
        exit(1)