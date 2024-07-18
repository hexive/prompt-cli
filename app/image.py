import os
import sys
import time
import random
import requests
import subprocess
import base64
from util import *


#######################################################
#####################  IMAGES  ########################
#######################################################

def prepare_image(documents, number):
    # verify automatic1111 is up  
    url = config('image','image-gen_url') + "/docs"
    if check_service(url):
        # verify there are some search results
        try:
            len(documents['result'])
            return generate_image(documents, number)
        except Exception as e:
            console.print(f"\nSomething went wrong. The error shown is:\n--{e}", style=f"{error_color}")
            #console.print("--try a /search first?\n", style=f"{error_color}")
            # on for debug?
            #import traceback
            #console.print(f"--Traceback says: ", style=f"bold {error_color}")
            #traceback.print_exc()
            #console.print("\n\n")
    else:
        console.print("\noops, did you forget to start stable diffusion?\n--fire that up before you try again\n", style=f"bold {error_color}")

def generate_image(documents, number):
    # randomize prompt for /r RANDOM
    if number==9999:
        top_range = len(documents['result'])
        number = random.randrange(1, top_range)

    prompt = documents['result']
    prompt_number = number-1
    prompt = prompt[prompt_number]

    #get some config settings
    gen_img_width=config('image','gen_img_width',int)
    gen_img_height=config('image','gen_img_height',int)


    # Define the URL and the payload to send.
    img_url = config('image','image-gen_url')

    payload = {
        "prompt": f"{prompt}",
        "negative_prompt":"",
        "seed":-1,
        "cfg_scale":5,
        "steps": 30,
        "sampler_name":"DPM++ 2M",
        "scheduler": "Automatic",
        "steps":30,
        "width":gen_img_width,
        "height":gen_img_height,
        "save_images": config('image','save_images_api',bool)
    }

#   #SETTING CHECKPOINT only do once?
#    option_payload = {
#        "sd_model_checkpoint": "Anything-V3.0-pruned",
#        "CLIP_stop_at_last_layers": 2
#        }
#    response = requests.post(url=f'{url}/sdapi/v1/options', json=option_payload)
   
    # Send payload to URL through the API.
    with console.status("\nGenerating diffusion image ..."):
        response = requests.post(url=f'{img_url}/sdapi/v1/txt2img', json=payload)
        r = response.json()

    if r.get('error') and r['error'].strip():
        console.print(f"\nSomething went wrong. The error shown is:\n--{r['error']}\n", style=f"{error_color}")
    else:
        # check config to set save to output folder
        if config('image','save_images_app',bool):
            filename = time.strftime("%Y%m%d-%H%M%S")
        else:
            filename = "thumb"

        file_path = install_path() + (f"/output/{filename}.png")
        thumb_path = install_path() + (f"/output/thumb.png")
    

        # Decode and save the image.
        with open(file_path, 'wb') as f:
            f.write(base64.b64decode(r['images'][0]))

        #resize XL images to fit in screen better
        thumb_img_max_width=config('image','thumb_img_max_width',int)
        thum_img_max_height=config('image','thum_img_max_height',int)

        subprocess.run(["convert", file_path, "-resize", f"{thumb_img_max_width}x{thum_img_max_height}>", thumb_path])

        # Write image to console
        subprocess.run(["kitty", "icat", thumb_path])
        console.print(f"{number}. {prompt}", style=f"{search_color}")
