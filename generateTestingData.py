import random
import numpy as np
from PIL import Image, ImageDraw, ImageEnhance, ImageFont
import cv2
import os
import multiprocessing
from multiprocessing import Process

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

def do_work(int_counter, champ_map):

    max_champ = len(champ_map)
    all_champ_names = []
    for i in range(max_champ):
        matching_champ_obj = champ_map[str(i)]
        for j in range(matching_champ_obj['champ_images']):
            all_champ_names.append(champ_map[str(i)]['champ_name'])

    random_10_numbers = []
    for i in range(10):
        champ_name = random.choice(all_champ_names)
        annotation_from_champ_name = [key for key, value in champ_map.items() if value['champ_name'] == champ_name][0]
        random_10_numbers.append(annotation_from_champ_name)

    champ_annotations = []

    map_path = 'assets/lolmap.png'
    if(random.randint(0, 5) == 0):
        map_path = 'assets/lolmap_bounties.png'
        if(random.randint(0, 1) == 0):
            map_path = 'assets/lolmap_hextech.png'

    map = Image.open(map_path).convert("RGBA")

    enhancer = ImageEnhance.Brightness(map)

    factor = random.randint(7, 15) / 10
    map = enhancer.enhance(factor)

    #resize map to be 469x469
    map = map.resize((469, 469))

    x_center_point_int = random.randint(0, 1000)
    champ_x_center_point_as_pct = x_center_point_int / 1000
    y_center_point_int = random.randint(0, 1000)
    champ_y_center_point_as_pct = y_center_point_int / 1000

    previous_champ_recalling = False

    champ_center_points = []

    for i in range(10):

        champ_annotation_id = random_10_numbers[i]
        champ_name = champ_map[str(champ_annotation_id)]['champ_name']
        champ_image_choice = random.randint(0, champ_map[str(champ_annotation_id)]['champ_images'] - 1) + 1

        if champ_name == "Yuumi" and random.randint(0, 1) == 0 and previous_champ_recalling == False and i != 0:

            yuumi_image = "assets/yuumiblue_minimap.png"
            if(random.randint(0, 1) == 0):
                yuumi_image = "assets/yuumired_minimap.png"

            circle_image=Image.open(yuumi_image).convert("RGBA")
            rgba = np.array(circle_image)

            circle_size = random.randint(45, 60)
            adjusted_size = circle_size
            circle_image = circle_image.resize((circle_size, circle_size))

            yuumi_x_center_point = int(map_size[0] * champ_x_center_point_as_pct) + random.randint(-1, 3)
            yuumi_y_center_point = int(map_size[1] * champ_y_center_point_as_pct) + random.randint(-1, 3)

            map.paste(circle_image, (yuumi_x_center_point - int(circle_size/2), yuumi_y_center_point - int(circle_size/2)), circle_image)

            yolo_training_data = generate_yolo_training_data(champ_annotation_id, champ_x_center_point_as_pct, champ_y_center_point_as_pct, adjusted_size/map_size[0], adjusted_size/map_size[1])

            champ_annotations.append(yolo_training_data)

            previous_champ_recalling = True
            continue


        img=Image.open("champions/" + champ_name + "/" + champ_image_choice.__str__() + ".png").convert("RGBA")
        h,w=img.size
        # crop_amount = random.randint(0, 2)
        # img = img.crop((crop_amount, crop_amount, h-crop_amount, w-crop_amount))
        # npImage=np.array(img)

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

        image_size = random.randint(35, 44)

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

        map_size = map.size

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
            
            recall_image_size = image_size + random.randint(18, 30)
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

    for i in range(random.randint(0, 20)):
        random_ping = random.choice(ping_images)
        ping_image = Image.open('assets/pings/' + random_ping).convert("RGBA")
        ping_image_size = random.randint(15, 35)
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
                    circle_image = Image.open('assets/pings/circles/' + circle_image_name).convert("RGBA")
                    # convert tintable image white to red
                    circle_image = circle_image.convert("RGBA")
                    rgba = np.array(circle_image)
                    b, g, r, a = cv2.split(rgba)
                    res = cv2.merge((b, g, r, a))

                    #find where the pixels are white and make those red, but the less white ones should be less red
                    whiteish_pixels = (res[:, :, 0] > 10) & (res[:, :, 1] > 10) & (res[:, :, 2] > 10)

                    values_to_change = np.zeros_like(res)

                    colours = ['red', 'blue', 'yellow']
                    colour = random.choice(colours)

                    # loop through red_values
                    for j in range(len(values_to_change)):
                        for jj in range(len(values_to_change[j])):
                            if(colour == 'red'):
                                values_to_change[j][jj][0] = random.randint(200, 255) - res[j][jj][0]
                                values_to_change[j][jj][1] = 0
                                values_to_change[j][jj][2] = 0
                                values_to_change[j][jj][3] = circle_opacity
                            elif(colour == 'blue'):
                                values_to_change[j][jj][0] = 0
                                values_to_change[j][jj][1] = 0
                                values_to_change[j][jj][2] = random.randint(200, 255) - res[j][jj][0]
                                values_to_change[j][jj][3] = circle_opacity
                            elif(colour == 'yellow'):
                                values_to_change[j][jj][0] = random.randint(200, 255) - res[j][jj][0]
                                values_to_change[j][jj][1] = random.randint(200, 255) - res[j][jj][0]
                                values_to_change[j][jj][2] = 0
                                values_to_change[j][jj][3] = circle_opacity

                    res[whiteish_pixels] = values_to_change[whiteish_pixels]
                    circle_image = Image.fromarray(res)
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


    # add random minimap icons
    minimap_icons = os.listdir('assets/minimap_icons')
    for i in range(random.randint(0, 10)):
        random_icon = random.choice(minimap_icons)
        icon_image = Image.open('assets/minimap_icons/' + random_icon).convert("RGBA")
        icon_image_size = int(icon_image.size[0] * (random.randint(7, 13) / 10))
        icon_image = icon_image.resize((icon_image_size, icon_image_size))

        icon_x_center_point_as_pct = random.randint(0, 1000) / 1000
        icon_y_center_point_as_pct = random.randint(0, 1000) / 1000
        icon_x_center_point = int(map_size[0] * icon_x_center_point_as_pct)
        icon_y_center_point = int(map_size[1] * icon_y_center_point_as_pct)

        map.paste(icon_image, (icon_x_center_point - int(icon_image_size/2), icon_y_center_point - int(icon_image_size/2)), icon_image)

    for i in range(random.randint(2, 4)):
        red_circle_size = random.randint(7, 9)
        red_circle = Image.new('RGBA', (red_circle_size, red_circle_size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(red_circle)
        draw.ellipse([(0, 0), (red_circle_size, red_circle_size)], fill=(255, 0, random.randint(0, 70), 255), outline=(0, 0, 0, 255), width=random.randint(1, 2))

        number_in_group = random.randint(1, 8)
        x_center_point_as_pct = random.randint(0, 1000) / 1000
        y_center_point_as_pct = random.randint(0, 1000) / 1000
        for j in range(number_in_group):
            map_size = map.size

            x_center_point = int(map_size[0] * x_center_point_as_pct)
            y_center_point = int(map_size[1] * y_center_point_as_pct)

            x_start = x_center_point - int(5/2)
            y_start = y_center_point - int(5/2)

            map.paste(red_circle, (x_start, y_start), red_circle)

            x_center_point_as_pct = x_center_point_as_pct + (random.randint(-20, 20) / 1000)
            y_center_point_as_pct = y_center_point_as_pct + (random.randint(-20, 20) / 1000)

    for i in range(random.randint(3, 5)):
        blue_circle_size = random.randint(7, 9)
        blue_circle = Image.new('RGBA', (blue_circle_size, blue_circle_size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(red_circle)
        draw.ellipse([(0, 0), (blue_circle_size, blue_circle_size)], fill=(0, random.randint(0, 70), 255, 255), outline=(0, 0, 0, 255), width=random.randint(1, 2))

        number_in_group = random.randint(1, 8)
        x_center_point_as_pct = random.randint(0, 1000) / 1000
        y_center_point_as_pct = random.randint(0, 1000) / 1000
        for j in range(number_in_group):
            map_size = map.size

            x_center_point = int(map_size[0] * x_center_point_as_pct)
            y_center_point = int(map_size[1] * y_center_point_as_pct)

            x_start = x_center_point - int(5/2)
            y_start = y_center_point - int(5/2)

            map.paste(red_circle, (x_start, y_start), red_circle)

            x_center_point_as_pct = x_center_point_as_pct + (random.randint(-20, 20) / 1000)
            y_center_point_as_pct = y_center_point_as_pct + (random.randint(-20, 20) / 1000)

    if random.randint(0, 3) == 1:
        cursor_images = ['assets/new_cursor.png', 'assets/old_cursor.png']
        new_cursor = Image.open(random.choice(cursor_images))
        cursor_size = int(50 * (random.randint(80, 100) / 100))
        new_cursor = new_cursor.resize((cursor_size, cursor_size))
        if(random.randint(0, 1) == 1):
            random_champ = random.choice(champ_center_points)
            map.paste(new_cursor, (int((random_champ[0] * map.size[0]) + random.randint(-10, 10) - int(cursor_size / 2)), int((random_champ[1] * map.size[1]) + random.randint(-10, 10) - int(cursor_size / 2))), new_cursor)
        else:
            map.paste(new_cursor, (random.randint(0, map.size[0] - cursor_size), random.randint(0, map.size[1] - cursor_size)), new_cursor)


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

    if(random.randint(3, 3) == 3):

        random_number_to_generate = random.randint(1, 15)

        for i in range(random_number_to_generate):

            fonts = ['assets/arial.ttf', 'assets/arial-bold.ttf']
            font_path = random.choice(fonts)

            time_amount = '{}{}:{}{}'.format(random.randint(0, 2), random.randint(0, 9), random.randint(0, 5), random.randint(0, 9))

            time_font = ImageFont.truetype(font_path, random.randint(16, 24))
        
            text_image = Image.new('RGBA', (100, 100))
            draw = ImageDraw.Draw(text_image)
            draw.text((0, 0), time_amount, font=time_font, fill=(255, 255, 255, 255))

            text_x_center_point_int = random.randint(0, 1000)
            text_x_center_point_as_pct = text_x_center_point_int / 1000
            text_x_center_point = int(map_size[0] * text_x_center_point_as_pct)
            text_y_center_point_int = random.randint(0, 1000)
            text_y_center_point_as_pct = text_y_center_point_int / 1000
            text_y_center_point = int(map_size[1] * text_y_center_point_as_pct)

            map.paste(text_image, (text_x_center_point, text_y_center_point), text_image)

    os.makedirs('raw_training_data', exist_ok=True)
    os.makedirs('raw_training_data/annotations', exist_ok=True)
    os.makedirs('raw_training_data/images', exist_ok=True)

    if(random.randint(0, 10) == 0): # 1 in 10 remains original quality
        map = map.convert('RGB')
        map.save('raw_training_data/images/' + int_counter.__str__() + '.jpg', format='JPEG')
    else:
        resize_amount = (random.randint(10, 20) / 10) ** 2

        map = map.resize((int(map.size[0] / resize_amount), int(map.size[1] / resize_amount)))
        map = map.resize((int(map.size[0] * resize_amount), int(map.size[1] * resize_amount)))

        if random.randint(0, 1) == 1:
            resize_amount = random.randint(10, 20) / 10
            map = map.resize((int(map.size[0] / resize_amount), int(map.size[1] / resize_amount)))

        map = map.convert('RGB')
        random_quality = (random.randint(2, 9) ** 2) + 20
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
    total_amount = 300000
    amount_per_pool = int(total_amount / number_of_processes)

    for w in range(number_of_processes):
        int_counter_start = w * amount_per_pool
        int_counter_end = int_counter_start + amount_per_pool

        p = Process(target=do_job, args=(int_counter_start, int_counter_end))
        processes.append(p)
        p.start()

    for p in processes:
        p.join()

    
