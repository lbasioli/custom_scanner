import time
import math
import epics
import matplotlib.pyplot as plt

def valley_borders(aspect_ratio, max_x_volts, x_diff):
    height = aspect_ratio * max_x_volts
    return -height, x_diff ** 2 / max_x_volts - height

def parabola_borders(aspect_ratio, max_x_volts, x_diff):
    height = aspect_ratio * max_x_volts
    return -height, height - x_diff ** 2 / max_x_volts

def rectangle_borders(aspect_ratio, max_x_volts, x_diff):
    height = aspect_ratio * max_x_volts
    return -height, height

def elipse_borders(aspect_ratio, max_x_volts, x_diff):
    border = aspect_ratio * math.sqrt(max_x_volts ** 2 - x_diff ** 2)
    return -border, border

def triangle_borders(aspect_ratio, max_x_volts, x_diff):
    max_y = aspect_ratio * max_x_volts
    return -max_y, max_y - 2 * aspect_ratio * abs(x_diff)

def custom_scanner(shape = "circle",
                   center_x = 0,
                   center_y = 0,
                   max_x_volts = 20,
                   aspect_ratio = 1,
                   spots_distance = 1,
                   time_frame = 0.1,
                   gradient = False,
                   time_frame_end = 0,
                   output = False,
                   draw_real_time = False,
                   draw_end = False,
                   send_to_epics = False,
                   h_pv_name = '',
                   v_pv_name = ''):
    """
    Generates coordinates in a square grid pattern that fills a given shape.
    One spot is always exactly at the center.
    All pixels that have their center's distance from the shape center
    strictly smaller than the radius are included.
    spots_distance must not be greater than radius.
    time_frame is set to assure reliabilty of power source output.
    
    Args:
    center_x (int): The x-coordinate of the shape's center.
    center_y (int): The y-coordinate of the shape's center.
    radius (float): The longest size of the shape in x direction. Spots exactly on the border are dissmised (in Volts!!, calibrate!!)
    spots_distance (float): The lattice constant of "spots lattice". (in Volts!!, calibrate!!)
    time_frame (float): The time in seconds between generating each point.
    
    Yields:
    tuple: A pair (x, y) of integer coordinates.
    """
    def borders(shape, aspect_ratio, max_x_volts, x_diff):
        try:
            return eval(shape + "_borders")(aspect_ratio, max_x_volts, x_diff)
        except:
            raise ValueError("Shape unknown")

    draw = draw_real_time | draw_end
    if draw:
        x_values = []
        y_values = []
        plt.figure(figsize=(10, 6))
        plt.title('Visual Representation of Coordinates')
        plt.xlabel('X coordinate')
        plt.ylabel('Y coordinate')
        plt.grid(True)
        plt.axis('equal')

    # How many squares from the center to the edge
    resolution = max_x_volts / spots_distance

    # The borders of the shape in x direction.
    min_x = center_x - (math.ceil(resolution) - 1) * spots_distance
    max_x = 2 * center_x - min_x

    # for every neighbouring column we will change direction to minimize voltage jumps
    y_direction = +1

    # time control is set to make sure this algorithm is not too fast for network, epics, plc, amplifier or magnets (??)  (but also for light effects)
    start_time = time.time()

    # Iterate for each row
    for x in range(min_x, max_x + 1, spots_distance):

        # Calculate acceptable y coordinates for current x
        y_down, y_up = borders(shape, aspect_ratio, max_x_volts, x - center_x)

        # Ensure all spot centres are strictly within the shape
        y_down = -math.floor(y_down + 1) // spots_distance * spots_distance * -1
        y_up = math.ceil(y_up - 1) // spots_distance * spots_distance

        # Ensure the beam doesn't jump in y when passing to new x
        if y_direction == -1: y_up, y_down = y_down, y_up

        # Iterate vertically in the current column
        for y in range(center_y + y_down, center_y + y_up + y_direction, spots_distance * y_direction):  

            if send_to_epics:
                epics.caput(h_pv_name, x)
                epics.caput(v_pv_name, y)

            #if output:
              #  print(f"Pixel coordinate: ({x}, {y})")

            if draw:
                x_values.append(x)
                y_values.append(y)
                if draw_real_time:
                    plt.scatter(x_values, y_values, c='black', marker='o')
                    plt.draw()
                    plt.pause(time_frame)

            # Time control
            elapsed_time = time.time() - start_time
            adjusted_sleep = max(0, time_frame - elapsed_time)
            time.sleep(adjusted_sleep)
            start_time = time.time()  # Reset the start time

        y_direction *= -1

        if gradient & (max_x != x):
            time_frame += (time_frame_end - time_frame) * spots_distance / (max_x - x)

        if output: print("time_frame = " + str(time_frame))

    if send_to_epics:
        epics.caput(h_pv_name, 0)
        epics.caput(h_pv_name, 0)

    if draw_end:
        plt.scatter(x_values, y_values, c='black', marker='o')
        plt.show()