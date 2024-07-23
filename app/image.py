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

def get_aspect_ratios():
    aspect_ratios = {
    "512x768": "Portrait",
    "768x512": "Landscape",
    "768x768": "Square",
    "768x1024": "Portrait",
    "1024x768": "Landscape",
    "1024x1024": "Square",
    }
    return aspect_ratios

def list_aspect():
    aspect_ratios = get_aspect_ratios()
    width=config('image','gen_img_width',int)
    height=config('image','gen_img_height',int)
    current_ratio = f"{width}x{height}"

    console.print(f"\nCurrently using '{width}x{height}'",style=f"{app_color} bold")
    console.print("\nSD1 Training Resolutions",style=f"{app_color} bold")

    for index, (ratio, description) in enumerate(aspect_ratios.items(), 1):
        label = f"{index}. '{description} {ratio}'" if current_ratio == ratio else f"{index}. {description} {ratio}"
        console.print(label, style=f"{app_color}")

        if index == 3:  # After the third item
            console.print("\nSDXL / SD3 Training Resolutions",style=f"{app_color} bold")

    console.print(f"\nTo change enter '/aspect 6', for example.\n",style=f"{app_color}")

def change_aspect(number):
    aspect_ratios = get_aspect_ratios()
    choice = number - 1
    ratios = list(aspect_ratios.keys())
    
    if 0 <= choice < len(aspect_ratios):
        selected_ratio = ratios[choice]
        width, height = map(int, selected_ratio.split('x'))
        
        set_config('image', 'gen_img_width', width)
        set_config('image', 'gen_img_height', height)
        
        console.print("\nSuccess! we set new aspect for image generation.\n",style=f"")

    else:
        console.print("\nINVALID! I really question your choices sometimes.\n", style=f"{error_color}")

def list_models():

    # Define the URL and the payload to send.
    img_url = config('image','image-gen_url')

    response = requests.get(url=f'{img_url}/sdapi/v1/sd-models')
    models = response.json()

    # Get the currently loaded model
    response = requests.get(url=f'{img_url}/sdapi/v1/options')
    options = response.json()

    current_model = options['sd_model_checkpoint']

    console.print(f"\nCurrently loaded model: ",style=f"bold {app_color}")
    console.print(f"'{current_model}'",style=f"{app_color}")

    console.print("\nAvailable models:",style=f"bold {app_color}")

    for i, model in enumerate(models):
        if model['title'] == current_model:
            console.print(f"{i+1}. '{model['title']}'",style=f"{app_color}")
        else:
            console.print(f"{i+1}. {model['title']}",style=f"{app_color}")

    console.print(f"\nTo change enter '/load 3', for example.\n",style=f"{app_color}")

def change_model(number):
    img_url = config('image','image-gen_url')

    #get models again
    response = requests.get(url=f'{img_url}/sdapi/v1/sd-models')
    models = response.json()

    choice = number - 1
    if 0 <= choice < len(models):
        new_model = models[choice]['title']

        option_payload = {
        "sd_model_checkpoint": new_model
        }

        with console.status("\nLoading new image model ..."):
            response = requests.post(url=f'{img_url}/sdapi/v1/options', json=option_payload)
            
        
        if response.status_code == 200:
            console.print("\nSuccess! the new image model is loaded.\n",style=f"")
        else:
            console.print(f"\nSomething went wrong with the model change. Try again?\n", style=f"{error_color}")
    else:
        console.print("\nINVALID! I really question your choices sometimes.\n", style=f"{error_color}")

def prepare_image(documents, number=None, llm_prompt=None):
    # verify automatic1111 is up  
    url = config('image','image-gen_url') + "/docs"
    if check_service(url):
        # verify there are some search results
        try:
            len(documents['result'])
            return generate_image(documents, number, llm_prompt)
        except Exception as e:
            console.print(f"\nSomething went wrong:", style=f"{error_color}")
            console.print("--maybe try a /search first?", style=f"{error_color}")
            print_error(e)
    else:
        console.print("\noops, did you forget to start stable diffusion?\n--fire that up before you try again\n", style=f"bold {error_color}")

def generate_image(documents, number, llm_prompt):

    # ugly work-around for llm prompt
    if llm_prompt is not None:
        prompt = llm_prompt
    else:
        # randomize prompt for /r RANDOM
        if number==9999:
            top_range = len(documents['result'])
            number = random.randrange(1, top_range)

        prompt = documents['result']
        prompt_number = number-1
        prompt = prompt[prompt_number]


    # from config define the URL and the payload to send.
    img_url = config('image','image-gen_url')

    payload = {
        "prompt": f"{prompt}",
        "negative_prompt":"",
        "seed":-1,
        "cfg_scale":5,
        "steps": 30,
        "sampler_name":config('image','sampler_name'),
        "scheduler": "Automatic",
        "steps":30,
        "width":config('image','gen_img_width',int),
        "height":config('image','gen_img_height',int),
        "save_images": config('image','save_images_api',bool)
    }
   
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

        subprocess.run(["convert", file_path, "-quiet", "-resize", f"{thumb_img_max_width}x{thum_img_max_height}>", thumb_path])

        # Write image to console
        subprocess.run(["kitty", "icat", thumb_path])
        

        if llm_prompt is not None:
            console.print(f"From Llama: {prompt}\n", style=f"{llm_color}")
        else:
            console.print(f"{number}. {prompt}\n", style=f"{search_color}")

        # Remove thumb
        if os.path.isfile(thumb_path):
            os.remove(thumb_path) 