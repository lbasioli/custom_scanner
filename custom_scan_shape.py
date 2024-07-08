from custom_scanner_algorithm import custom_scanner as scan

flag = True

while flag:
    scan(shape = "elipse",    # supported: rectangle, elipse, triangle, valley, parabola
        center_x = 0,          # offset
        center_y = 0,          # offset
        max_x_volts = 100,    # calibrate to physical size?
        aspect_ratio = 5,      # size of the shape is smaller in y_dimension for aspect_ratio < 1, make sure max_y not too high!!
        spots_distance = 5,  # Volts difference between two neighouring poitns
        time_frame = 1E-6,     # Time to pass between two points, radiation time
        gradient = True,       # True to start with time_frame and end with time_frame_end
        time_frame_end = 1E-17, # End value of linear exposure time gradient
        output = True,         # Print coordinates to console? Can slow down if scan time is fast (not tested)
        draw_real_time = False,# False when looking at the beam, slows down a lot
        draw_end = True,       # False when looking at the beam, pauses at the end of 1 full scan
        send_to_epics = False, # True to do stuff in the lab
        h_pv_name = "ALL:SW2:PLC:uPHDefVoltage:Set",
        v_pv_name = "ALL:SW2:PLC:uPVDefVoltage:Set")

    flag = False # True for endless loop