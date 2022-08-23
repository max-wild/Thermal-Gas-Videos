import bpy
from random import seed, randint, uniform  # , getrandbits
from math import sin, cos, copysign
# from numpy import log as ln
import os
from time import sleep
from datetime import datetime
import argparse
import sys


seed()

domain = bpy.context.scene.objects["Smoke Domain"]
emitter = bpy.context.scene.objects["Emitter"]
init_velocity = emitter.modifiers["Fluid"].flow_settings.velocity_coord
light = bpy.context.scene.objects["Light"]
cam = bpy.context.scene.objects["Camera"]
turbulence = bpy.context.scene.objects["Turbulence"]
wind = bpy.context.scene.objects["Wind"]

sign = lambda x: copysign(1, x)
start_time = datetime.now()


class ArgumentParserForBlender(argparse.ArgumentParser):
    """
    This class is taken online from stack exhange. Use double dashes to express arguments
    given after the script in the console
    >> blender --python my_script.py -- -a 1 -b 2
    """

    def _get_argv_after_doubledash(self):
        try:
            idx = sys.argv.index("--")
            return sys.argv[idx+1:]  # the list after '--'
        except ValueError as e:  # '--' not in the list:
            return []

    # overrides superclass
    def parse_args(self, args=None, namespace=None):
        return super().parse_args(args=self._get_argv_after_doubledash())


def rand_color_val() -> float:
    """
    Returns a number between 0 and 0.6 generated with weight, to represent RGB colors

    :return:
    """

    # Generate num between 0 and 1
    c = randint(0, 100) / 100

    # Put it through a weighted function
    return max(c/5, 54*c/70 - 6/35)


def rand_smoke_offset() -> float:
    """
    Makes an x-offset, away from the camera, for the emitter's transform to emulate
    smaller smoke 
    
    Pushes the smoke back further into the frame
    """
    
    if randint(0, 1) == 0: 
        return 0
    
    else:
        return randint(-850, -300) / 100  # -8.5 to -3, pushes the smoke back


def setup_new_scene():
    """
    Sets up a new random configuration for a scene

    :return:
    """

    # Domain Shader (Color and Density)
    col = rand_color_val()  # RGB between 0 and .6
    domain.active_material.node_tree.nodes['Principled Volume'].inputs[0].default_value = (col, col, col, 1)

    min_den = 1 / (2 * col + 0.5)
    max_den = -0.7 * col + 0.5
    density = uniform(min_den, max_den)  # Random density within a range depending on col
    domain.active_material.node_tree.nodes['Principled Volume'].inputs[2].default_value = density

    # Domain Settings
    domain.modifiers['Fluid'].domain_settings.vorticity = randint(30, 60) / 100  # 0.3 to 0.6

    # Emitter Initial Velocity
    init_vel_degree = randint(0, 6283) / 1000
    init_vel_degree2 = randint(0, 3141) / 1000  # A higher value means it will be directed downward
    init_vel_mag = randint(2, 60) / 10  # 0.2 to 6

    init_velocity.x = init_vel_mag * sin(init_vel_degree2) * cos(init_vel_degree)
    init_velocity.y = init_vel_mag * sin(init_vel_degree2) * sin(init_vel_degree)
    init_velocity.z = init_vel_mag * cos(init_vel_degree2)

    # Turbulence Transform -- Needs to be near the emitter
    turbulence.location.x = domain.location.x + randint(-32, 32) / 10
    turbulence.location.y = domain.location.y + randint(-32, 32) / 10
    turbulence.location.z = domain.location.z + randint(-16, 16) / 10

    # Turbulence Field
    turbulence.field.strength = randint(300, 700) / 100  # 3 to 7
    turbulence.field.flow = randint(0, 100) / 100  # 0 to 1
    turbulence.field.size = randint(80, 600) / 100  # .8 to 6

    # Wind Field
    wind.field.flow = randint(80, 280) / 100  # 0.8 to 2.8
    wind.field.noise = randint(0, 250) / 100  # 0 to 2.5    

    # Light Transform
    light_degree = randint(524, 2618) / 1000  # Goes from 30 degrees to 150
    light.location.x = 8 * cos(light_degree)
    light.location.y = 8 * sin(light_degree)
    light.location.z = randint(500, 700) / 100

    # Light Strength
    light.data.energy = randint(800, 1200) / 100  # 8 to 12

    # ------------ Position Affecting Parameters ------------ #

    # Buoyancy and Heat -- affects Z
    domain.modifiers['Fluid'].domain_settings.alpha = randint(8, 35) / 10  # 0.8 to 3.5
    domain.modifiers['Fluid'].domain_settings.beta = randint(-35, 35) / 10  # -3.5 to 3.5
    emitter.modifiers["Fluid"].flow_settings.temperature = randint(-80, 80) / 10  # -8 to 8

    heat_sign = sign(domain.modifiers['Fluid'].domain_settings.beta) * \
                sign(emitter.modifiers["Fluid"].flow_settings.temperature)

    # Generate random numbers
    emitter_distance = randint(0, 1000) / 100  # 0 to 10
    rand_place_degree = randint(0, 6283) / 1000
    rand_adjustment = randint(-1047, 1047) / 1000  # Spans 60 degrees to the left or the right

    # Emitter Transform
    emitter.location.x = emitter_distance * cos(rand_place_degree)
    emitter.location.y = emitter_distance * sin(rand_place_degree) + rand_smoke_offset()

    if heat_sign == 1:
        # Smoke will likely rise
        emitter.location.z = randint(-320, 500) / 100  # -3.2 to 5
    else:
        # Smoke will likely fall
        emitter.location.z = randint(250, 1220) / 100  # 2.5 to 12.2

    # Domain Transform
    domain.location.x = emitter.location.x
    domain.location.y = emitter.location.y
    domain.location.z = emitter.location.z  # + 4.6  # The Z should be tied to emitter

    # Wind Rotation
    if emitter_distance < 4:  
        # If the emitter is within frame, then the wind can blow in any dir
        wind.rotation_euler.z = randint(0, 6283) / 1000
    
    else:
        # Otherwise, wind must blow into frame
        wind.rotation_euler.z = rand_place_degree + 3.14 + rand_adjustment
    
    wind.rotation_euler.x = rand_adjustment / 2
    wind.rotation_euler.y = 90 + -rand_adjustment / 2

    if emitter_distance > 4.2:
        # The emitter is so far that the wind should certainly blow strong enough
        wind.field.strength = randint(400, 600) / 100  # 4 to 6
    else:
        wind.field.strength = randint(0, 180) / 100  # 0 to 1.8


def delete_bake():
    bpy.context.view_layer.objects.active = domain
    bpy_freeing = bpy.ops.fluid.free_all()

    assert ('FINISHED' in bpy_freeing)


def bake():
    bpy.context.view_layer.objects.active = domain
    bpy_baking = bpy.ops.fluid.bake_all()

    assert ('FINISHED' in bpy_baking)


def render_anim(r_num: int, make_images: bool, output_dir: str, digits: int) -> int:
    """
    Renders four frames of the animation, subdivided into 16-20 frames per image

    :param r_num: The number of the file attached to the rendered image
    :param make_images: If the video is rendered as an image slideshow or a single video
    :param output_dir: What the output of the file should be
    :param digits: How many digits are in the amount of image renders. Used solely for naming
        rendered images
    :return: Returns the new number of the file attached to the rendered image
    """

    # Set frame
    bpy.context.scene.frame_set(20)

    if make_images:
        # Save images into a folder
        output_end = 'slideshow{}/'.format(r_num)
        output = os.path.join(output_dir, output_end)

        bpy.context.scene.render.filepath = output
        bpy.ops.render.render(animation=True)
        r_num += 1

    else:
        # Save video
        bpy.context.scene.render.filepath = os.path.join(output_dir, 'video{}.mp4'.format(r_num))
        bpy.ops.render.render(animation=True)
        r_num += 1

    return r_num


def init_values():
    parser = ArgumentParserForBlender()

    parser.add_argument('-f', '--fps', type=int, default=30,
                        help='How many frames per second the video should be')
    parser.add_argument('-s', '--seconds', type=int, default=20,
                        help='How many seconds of video should be rendered')
    parser.add_argument('-v', '--video_count', type=int, default=1,
                        help='How many different scenarios/videos should be rendered')
    parser.add_argument('-r', '--render_image_slideshow', type=bool, default=False,
                        help='Determine if the video be rendered as a slideshow of images or as a single video')

    parser.add_argument('-o', '--output', type=str, required=True,
                        help='File location of the renders folder')

    args = vars(parser.parse_args())

    return args['fps'], args['seconds'], args['video_count'], args['render_image_slideshow'], args['output']


def init_gpu():
    """
    Ensures that blender is using Google Colab's provided GPU

    Code taken from "donmahallem" in their GitHub project colab_blender!
    """

    import re
    scene = bpy.context.scene
    scene.cycles.device = 'GPU'
    prefs = bpy.context.preferences
    prefs.addons['cycles'].preferences.get_devices()
    cprefs = prefs.addons['cycles'].preferences
    print(cprefs)

    # Attempt to set GPU device types if available
    for compute_device_type in ('CUDA', 'OPENCL', 'NONE'):
        try:
            cprefs.compute_device_type = compute_device_type
            print('Device found', compute_device_type)
            break
        except TypeError:
            pass

    # Enable all CPU and GPU devices
    for device in cprefs.devices:
        if not re.match('intel', device.name, re.I):
            print('Activating', device)
            device.use = True
        else:
            device.use = False

    # bpy.ops.render.render(True)


def start_render():
    """
    Frees the smoke data, sets up new random reconfiguration, then preps to rebake / re-export

    :return:
    """

    fps, vid_secs, vids_count, render_images, output = init_values()

    # Set up video requirements
    delete_bake()
    sleep(0.4)

    frames = (fps * vid_secs) + 20  # Total frames of animation
    bpy.context.scene.frame_start = 20
    bpy.context.scene.frame_end = frames
    domain.modifiers["Fluid"].domain_settings.cache_frame_end = frames  # Smoke domain frame end
    bpy.context.scene.render.fps = fps

    print(f'TEST: {render_images=}')

    if render_images:
        bpy.context.scene.render.image_settings.file_format = 'PNG'
    else:
        bpy.context.scene.render.image_settings.file_format = 'FFMPEG'
        bpy.context.scene.render.ffmpeg.format = 'MPEG4'

    file_num = 1

    init_gpu()
    
    print(f'\nStarting to render {vids_count} gas videos...')

    for i in range(vids_count):

        # DELETE OLD BAKE
        delete_bake()        

        # REMAKE SCENE
        setup_new_scene()

        # WAIT TO CONFIRM END OF BAKE DELETE
        sleep(0.4)

        if i != 0:
            print(f'\nCompleted render {i}, seconds: {(datetime.now() - start_time).total_seconds()}')

        # BAKE
        bake()

        print(f'\nStarting render for video {i + 1}, seconds: {(datetime.now() - start_time).total_seconds()}')

        # RENDER
        file_num = render_anim(file_num, render_images, output, digits=len(str(frames - 20)))

    print(f'Finished producing {vids_count} {"render" if vids_count == 1 else "renders"}, '
          f'time {(datetime.now() - start_time).total_seconds()}\n')


if __name__ == '__main__':
    start_render()
