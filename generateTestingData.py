import random
import numpy as np
from PIL import Image, ImageDraw, ImageEnhance
import cv2
import os
import multiprocessing
from multiprocessing import Process

from convertGrayscaleIcons import to_red, to_blue

def generate_yolo_training_data(annotation_id, x_center_point_pct, y_center_point_pct, x_size_as_pct, y_size_as_pct):

    bounding_box = [
        [x_center_point_pct - (x_size_as_pct / 2), y_center_point_pct - (y_size_as_pct / 2)],
        [x_center_point_pct + (x_size_as_pct / 2), y_center_point_pct - (y_size_as_pct / 2)],
        [x_center_point_pct + (x_size_as_pct / 2), y_center_point_pct + (y_size_as_pct / 2)],
        [x_center_point_pct - (x_size_as_pct / 2), y_center_point_pct + (y_size_as_pct / 2)]
    ]
    
    # update bounding box so that no number can be outside of 0-1
    for i in range(len(bounding_box)):
        if bounding_box[i][0] < 0:
            bounding_box[i][0] = 0
        if bounding_box[i][1] < 0:
            bounding_box[i][1] = 0
        if bounding_box[i][0] > 1:
            bounding_box[i][0] = 1
        if bounding_box[i][1] > 1:
            bounding_box[i][1] = 1

    x_center_point = (bounding_box[0][0] + bounding_box[2][0]) / 2
    y_center_point = (bounding_box[0][1] + bounding_box[2][1]) / 2
    x_size = bounding_box[2][0] - bounding_box[0][0]
    y_size = bounding_box[2][1] - bounding_box[0][1]

    return '{0} {1} {2} {3} {4}'.format(annotation_id, x_center_point, y_center_point, x_size, y_size)

def random_color_augmentation(image):
    # Randomly adjust brightness (0.8 to 1.2)
    enhancer = ImageEnhance.Brightness(image)
    image = enhancer.enhance(random.uniform(0.8, 1.2))

    # Randomly adjust contrast (0.8 to 1.2)
    enhancer = ImageEnhance.Contrast(image)
    image = enhancer.enhance(random.uniform(0.8, 1.2))

    # Randomly adjust saturation (0.8 to 1.2)
    enhancer = ImageEnhance.Color(image)
    image = enhancer.enhance(random.uniform(0.8, 1.2))

    # Randomly adjust hue (-10 to 10 degrees)
    # Convert to HSV, adjust hue, convert back to RGB
    image = np.array(image.convert('HSV'))
    image[..., 0] = (image[..., 0] + random.randint(-10, 10)) % 256
    image = Image.fromarray(image, 'HSV').convert('RGB')

    return image

def do_work(int_counter, champ_map):

    max_champ = len(champ_map)
    all_champ_names = []
    for i in range(max_champ):
        matching_champ_obj = champ_map[str(i)]
        for j in range(matching_champ_obj['champ_images']):
            all_champ_names.append(champ_map[str(i)]['champ_name'])

    random_10_numbers = []
    for i in range(50):
        champ_name = random.choice(all_champ_names)
        annotation_from_champ_name = [key for key, value in champ_map.items() if value['champ_name'] == champ_name][0]
        random_10_numbers.append(annotation_from_champ_name)

    champ_annotations = []

    rn = random.randint(0, 9)
    if(rn < 4):
        map_path = 'assets/maps/lolmap.png'
    elif(rn < 8):
        map_path = 'assets/maps/lolmap_bounties.png'
    else:
        map_paths = os.listdir('assets/maps/other')
        map_path = 'assets/maps/other/' + random.choice(map_paths)

    map = Image.open(map_path).convert("RGBA")

    #resize map to be 320x320
    map = map.resize((320, 320))
    map_size = map.size

    # add minion clusters
    for i in range(random.randint(5, 10)):
        if random.randint(0, 1) == 0:
            minion_image = to_blue('assets/minimap_icons/minionmapcircle_gray.png')
        else:
            minion_image = to_red('assets/minimap_icons/minionmapcircle_gray.png')
        minion_image_size = random.randint(3, 6)
        minion_image = minion_image.resize((minion_image_size, minion_image_size))

        minion_x_center_point_as_pct = random.randint(0, 1000) / 1000
        minion_y_center_point_as_pct = random.randint(0, 1000) / 1000
        for _ in range(random.randint(6, 8)):
            minion_x_center_point = int(map_size[0] * minion_x_center_point_as_pct)
            minion_y_center_point = int(map_size[1] * minion_y_center_point_as_pct)
            map.paste(minion_image, (minion_x_center_point - int(minion_image_size/2), minion_y_center_point - int(minion_image_size/2)), minion_image)
            minion_x_center_point_as_pct = minion_x_center_point_as_pct + (random.randint(-30, 30) / 1000)
            minion_y_center_point_as_pct = minion_y_center_point_as_pct + (random.randint(-30, 30) / 1000)

    # add random minimap icons
    minimap_icons = os.listdir('assets/minimap_icons')
    for i in range(random.randint(0, 100)):
        random_icon = random.choice(minimap_icons)
        if random_icon.endswith('_gray.png'):
            if random.randint(0, 1) == 0:
                icon_image = to_blue('assets/minimap_icons/' + random_icon)
            else:
                icon_image = to_red('assets/minimap_icons/' + random_icon)
        else:
            icon_image = Image.open('assets/minimap_icons/' + random_icon).convert("RGBA")

        if random_icon in ['tunnelicon.png', 'tunnelicon2.png', 'yorickmaiden.png', 'yorickmaiden_enemy.png', 'sr_infernalrift_meep.png']:
            icon_image_size = int(icon_image.size[0] * (random.randint(1, 3) / 10))
        else:
            icon_image_size = int(icon_image.size[0] * (random.randint(4, 8) / 10))
        icon_image = icon_image.resize((icon_image_size, icon_image_size))

        icon_x_center_point_as_pct = random.randint(0, 1000) / 1000
        icon_y_center_point_as_pct = random.randint(0, 1000) / 1000
        icon_x_center_point = int(map_size[0] * icon_x_center_point_as_pct)
        icon_y_center_point = int(map_size[1] * icon_y_center_point_as_pct)

        map.paste(icon_image, (icon_x_center_point - int(icon_image_size/2), icon_y_center_point - int(icon_image_size/2)), icon_image)

    x_center_point_int = random.randint(0, 1000)
    champ_x_center_point_as_pct = x_center_point_int / 1000
    y_center_point_int = random.randint(0, 1000)
    champ_y_center_point_as_pct = y_center_point_int / 1000

    previous_champ_recalling = False

    champ_center_points = []

    for i in range(50):

        champ_annotation_id = random_10_numbers[i]
        champ_name = champ_map[str(champ_annotation_id)]['champ_name']
        champ_image_choice = random.randint(0, champ_map[str(champ_annotation_id)]['champ_images'] - 1) + 1

        if champ_name == "Yuumi" and random.randint(0, 1) == 0 and previous_champ_recalling == False and i != 0:

            if(random.randint(0, 1) == 0):
                circle_image = to_blue('assets/yuumi_minimap_gray.png')
            else:
                circle_image = to_red('assets/yuumi_minimap_gray.png')

            circle_size = random.randint(45, 60)
            circle_image = circle_image.resize((circle_size, circle_size))

            yuumi_x_center_point = int(map_size[0] * champ_x_center_point_as_pct) + random.randint(-1, 3)
            yuumi_y_center_point = int(map_size[1] * champ_y_center_point_as_pct) + random.randint(-1, 3)

            map.paste(circle_image, (yuumi_x_center_point - int(circle_size/2), yuumi_y_center_point - int(circle_size/2)), circle_image)

            yolo_training_data = generate_yolo_training_data(champ_annotation_id, champ_x_center_point_as_pct, champ_y_center_point_as_pct, circle_size/map_size[0], circle_size/map_size[1])

            champ_annotations.append(yolo_training_data)

            previous_champ_recalling = True
            continue


        img=Image.open("champions/" + champ_name + "/" + champ_image_choice.__str__() + ".png").convert("RGBA")
        newH,newW=img.size

        X, Y = newH/2, newH/2
        r = newH/2

        # Create a new image with a transparent background
        circle = Image.new('RGBA', (newH, newW), (0, 0, 0, 0))

        # Draw a circle with a black border on the new image
        draw = ImageDraw.Draw(circle)

        outline_colour = (0, random.randint(0, 70), 255, 255)
        if(random.randint(0, 1) == 0):
            outline_colour = (255, 0, random.randint(0, 70), 255)

        draw.ellipse([(X-r, Y-r), (X+r, Y+r)], fill=(255, 255, 255, 0), outline=outline_colour, width=random.randint(2, 4))

        img.paste(circle, (0, 0), circle)

        image_size = random.randint(25, 35)

        resized_img = img.resize((image_size, image_size))

        if(random.randint(0, 3) == 0 ):
            random_x_offset = random.randint(10, 60)
            random_y_offset = random.randint(10, 60)
            if(random.randint(0, 1) == 0):
                x_center_point_int = x_center_point_int + random_x_offset
                y_center_point_int = y_center_point_int + random_y_offset
            else:
                x_center_point_int = x_center_point_int - random_x_offset
                y_center_point_int = y_center_point_int - random_y_offset
        else:
            x_center_point_int = random.randint(0, 1000)
            y_center_point_int = random.randint(0, 1000)

        champ_x_center_point_as_pct = x_center_point_int / 1000
        champ_y_center_point_as_pct = y_center_point_int / 1000

        champ_center_points.append((champ_x_center_point_as_pct, champ_y_center_point_as_pct))

        x_center_point = int(map_size[0] * champ_x_center_point_as_pct)
        y_center_point = int(map_size[1] * champ_y_center_point_as_pct)
        
        x_start = x_center_point - int(image_size/2)
        y_start = y_center_point - int(image_size/2)

        enhancer = ImageEnhance.Brightness(resized_img)

        factor = random.randint(7, 14) / 10
        resized_img = enhancer.enhance(factor)

        map.paste(resized_img, (x_start, y_start), resized_img)

        if(random.randint(0, 10) == 0):
            recall_images = ['assets/recall.png', 'assets/recall_enemy.png', 'assets/tp_enemy.png', 'assets/tp_friendly.png', 'assets/tp_tf.png', 'assets/tp_shen.png']
            recall_image = Image.open(random.choice(recall_images)).convert("RGBA")
            
            recall_rotation = random.randint(0, 360)
            recall_image = recall_image.rotate(recall_rotation, expand=True)
            
            recall_image_size = image_size + random.randint(18, 25)
            recall_image = recall_image.resize((recall_image_size, recall_image_size))
            map.paste(recall_image, (x_start - int(recall_image_size/2) + int(image_size/2), y_start - int(recall_image_size/2) + int(image_size/2)), recall_image)
            previous_champ_recalling = True

        else:
            previous_champ_recalling = False

        yolo_training_data = generate_yolo_training_data(champ_annotation_id, champ_x_center_point_as_pct, champ_y_center_point_as_pct, image_size/map_size[0], image_size/map_size[1])

        champ_annotations.append(yolo_training_data)

    # add pings to map
    ping_images = [ping_image for ping_image in os.listdir('assets/pings') if ping_image.endswith('.png')]
    circle_images = os.listdir('assets/pings/circles')
    
    ping_x_center_point_as_pct = random.randint(0, 1000) / 1000
    ping_y_center_point_as_pct = random.randint(0, 1000) / 1000
    ping_x_center_point = int(map_size[0] * ping_x_center_point_as_pct)
    ping_y_center_point = int(map_size[1] * ping_y_center_point_as_pct)

    for i in range(random.randint(0, 50)):
        random_ping = random.choice(ping_images)
        ping_image = Image.open('assets/pings/' + random_ping).convert("RGBA")
        if random.randint(0, 1) == 1:
            ping_image = to_red('assets/pings/' + random_ping)
        else:
            ping_image = to_blue('assets/pings/' + random_ping)
        ping_image_size = random.randint(10, 20)
        ping_image = ping_image.resize((ping_image_size, ping_image_size))

        # randomly put 33% over champs
        if(random.randint(0, 2) == 0):
            champ_center_point = random.choice(champ_center_points)
            ping_x_center_point_as_pct = champ_center_point[0]
            ping_y_center_point_as_pct = champ_center_point[1]
            ping_x_center_point = int(map_size[0] * ping_x_center_point_as_pct) + random.randint(-15, 15)
            ping_y_center_point = int(map_size[1] * ping_y_center_point_as_pct) + random.randint(-15, 15)
        elif random.randint(0, 1) == 0:
            # print(int_counter)
            champ_center_point = random.choice(champ_center_points)
            ping_x_center_point_as_pct = champ_center_point[0]
            ping_y_center_point_as_pct = champ_center_point[1]
            random_one_or_negative_one_x = 1
            if(random.randint(0, 1) == 0):
                random_one_or_negative_one_x = -1
            random_one_or_negative_one_y = 1
            if(random.randint(0, 1) == 0):
                random_one_or_negative_one_y = -1
            ping_x_center_point = int(map_size[0] * ping_x_center_point_as_pct) + (random.randint(20, 70) * random_one_or_negative_one_x)
            ping_y_center_point = int(map_size[1] * ping_y_center_point_as_pct) + (random.randint(20, 70) * random_one_or_negative_one_y)

        else:

            # randomly put 50% over previous ping
            if(random.randint(0, 1) == 0):
                ping_x_center_point = ping_x_center_point + random.randint(10, 60)
                ping_y_center_point = ping_y_center_point + random.randint(10, 60)
            else:
                ping_x_center_point_as_pct = random.randint(0, 1000) / 1000
                ping_y_center_point_as_pct = random.randint(0, 1000) / 1000
                ping_x_center_point = int(map_size[0] * ping_x_center_point_as_pct)
                ping_y_center_point = int(map_size[1] * ping_y_center_point_as_pct)

        map.paste(ping_image, (ping_x_center_point - int(ping_image_size/2), ping_y_center_point - int(ping_image_size/2)), ping_image)

        if(random.randint(0, 3) != 0):
            # add circles to ping
            number_of_circles_in_ping = random.randint(1, 3)
            for ii in range(number_of_circles_in_ping):

                circle_opacity = random.randint(0, 255)
                # randomly use the tintable circle for 50% of circles
                if(random.randint(0, 1) == 0):
                    tintable_images = ['ring_tintable.png', 'ring2_tintable.png']
                    circle_image_name = random.choice(tintable_images)
                    circle_image_path = 'assets/pings/circles/' + circle_image_name
                    if random.randint(0, 1) == 1:
                        circle_image = to_red(circle_image_path)
                    else:
                        circle_image = to_blue(circle_image_path)
                    circle_size = random.randint(10, 80)
                    circle_image = circle_image.resize((circle_size, circle_size))
                    circle_image.save('circle.png')
                    map.paste(circle_image, (ping_x_center_point - int(circle_size/2), ping_y_center_point - int(circle_size/2)), circle_image)

                else:
                    
                    circle_image_name = random.choice(circle_images)
                    circle_image = Image.open('assets/pings/circles/' + random.choice(circle_images)).convert("RGBA")
                    circle_size = random.randint(10, 80)
                    circle_image = circle_image.resize((circle_size, circle_size))
                    if(random.randint(0, 1) == 0):
                        circle_image.putalpha(random.randint(0, 40))
                    map.paste(circle_image, (ping_x_center_point - int(circle_size/2), ping_y_center_point - int(circle_size/2)), circle_image)

    recangle_height = random.randint(70, 120)
    recangle_width = random.randint(100, 170)

    white_rectangle = Image.new('RGBA', (recangle_width, recangle_height))
    draw = ImageDraw.Draw(white_rectangle)
    draw.rectangle([(0, 0), (recangle_width, recangle_height)], fill=(0, 0, 0, 0), outline=(255, 255, 255, 255), width=3)

    if(random.randint(0, 1) == 1):
        map.paste(white_rectangle, (random.randint(0, map.size[0]), random.randint(0, map.size[1])), white_rectangle)
    else:
        random_champ = random.choice(champ_center_points)
        map.paste(white_rectangle, (int((random_champ[0] * map.size[0]) + random.randint(-10, 10)), int((random_champ[1] * map.size[1]) + random.randint(-10, 10))), white_rectangle)

    map = random_color_augmentation(map)

    os.makedirs('raw_training_data', exist_ok=True)
    os.makedirs('raw_training_data/annotations', exist_ok=True)
    os.makedirs('raw_training_data/images', exist_ok=True)

    if(random.randint(0, 10) < 8): # 8 in 10 remains high quality
        random_quality = 95
    else:
        random_quality = random.randint(50, 90)

    map = map.convert("RGB")
    map.save('raw_training_data/images/' + int_counter.__str__() + '.jpg', format='JPEG', quality=random_quality)

    with open('raw_training_data/annotations/' + int_counter.__str__() + '.txt', 'w') as f:
        f.write('\n'.join(champ_annotations))

    int_counter += 1

def do_job(int_counter_start, int_counter_end):
    
    champ_map = {}
    with open("champMap.json", "r") as f:
        champ_map = eval(f.read())

    int_counter = int_counter_start
    while(int_counter < int_counter_end):
        pct_complete = ((int_counter - int_counter_start) / (int_counter_end - int_counter_start)) * 100
        print(pct_complete)
        do_work(int_counter, champ_map)
        int_counter += 1

if __name__ == "__main__":
    int_counter = 0
    processes = []

    number_of_processes = multiprocessing.cpu_count()
    total_amount = 1000
    amount_per_pool = int(total_amount / number_of_processes)

    for w in range(number_of_processes):
        int_counter_start = w * amount_per_pool
        int_counter_end = int_counter_start + amount_per_pool

        p = Process(target=do_job, args=(int_counter_start, int_counter_end))
        processes.append(p)
        p.start()

    for p in processes:
        p.join()

