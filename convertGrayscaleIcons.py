from PIL import Image
import numpy as np
import os
import random

# not sure what the actual colors are so vary them a bit
def bitwise_and(image_path, hex_color, vary_range):
    image = Image.open(image_path)

    assert image.mode == 'RGBA', "Image is not RGBA"

    rgb_image = image.convert('RGB')
    alpha_channel = image.split()[3]

    hex_color = hex_color.lstrip('#')
    perturbation = random.randint(-vary_range, vary_range)
    mask_rgb = np.array([int(hex_color[i:i+2], 16) for i in (0, 2, 4)], dtype=np.uint8)
    mask_rgb = np.array([max(0, min(255, base + perturbation))
                              for base in mask_rgb], dtype=np.uint8)

    result_image_np = np.array(rgb_image) & mask_rgb
    result_image = Image.fromarray(result_image_np, 'RGB')
    result_image.putalpha(alpha_channel)
    return result_image

def to_red(image_path):
    return bitwise_and(image_path, '#E02020', 20)

def to_blue(image_path):
    img =  bitwise_and(image_path, '#3090E0', 20)
    return img
