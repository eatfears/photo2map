#!/usr/bin/python
import math
from PIL import Image
import time
import argparse
import multiprocessing

earth_r = 6371.0
earth_geos_h = 35786.0
electrol_lon = 76.0
electrol_fov = 17.89

parser = argparse.ArgumentParser()
parser.add_argument("-R", "--radius", help="Planet radius in kilometers (default " + str(earth_r) + ")",
                    type=float, default=earth_r)
parser.add_argument("-H", "--height", help="Satellite height above surface (default " + str(earth_geos_h) + ")",
                    type=float, default=earth_geos_h)
parser.add_argument("-slon", "--sat-longitude", help="Satellite longitude degrees (default " + str(electrol_lon) + ")",
                    type=float, default=electrol_lon)

parser.add_argument("-i", "--input", help="Input image filename (default input.jpg)",
                    type=str, default="input.jpg")
parser.add_argument("-o", "--output", help="Output image filename (default output.png)",
                    type=str, default="output.png")

parser.add_argument("-w", "--width", help="Output image width (default 1000)",
                    type=int, default=1000)
parser.add_argument("-di", help="Do not use bilinear interpolation (default False)",
                    default=False, action="store_true")

parser.add_argument("-m", "--mode", help="Target, Visible or Full (experimental!) mode (default t)",
                    type=str, default="t", choices=["t", "v", "f"])
parser.add_argument("-p", "--projection", help="Projection (default mer)",
                    type=str, default="mer", choices=["eq", "mer", "mil"])
parser.add_argument("-z", "--zoom", help="Image zoom factor (default 1.0)",
                    type=float, default=1.0)
parser.add_argument("-lat", "--latitude", help="Target latitude degrees (default 0.0)",
                    type=float, default=0.0)
parser.add_argument("-lon", "--longitude", help="Target longitude degrees (default satellite)",
                    type=float, default=electrol_lon)

parser.add_argument("-f", "--fov", help="FOV of input image (default " + str(electrol_fov) + ")",
                    type=float, default=electrol_fov)
parser.add_argument("-j", "--threads", help="Multithreading (default 1)",
                    type=int, default=1)

args = parser.parse_args()

r = args.radius
h = args.height
satellite_lon = math.radians(args.sat_longitude)

input_filename = args.input
output_filename = args.output
output_width = args.width
interpolate = not args.di

pr_str = args.projection

if args.mode == "t":
    zoom = args.zoom
    target_lat = math.radians(args.latitude)
    target_lon = math.radians(args.longitude)
elif args.mode == "v":
    zoom = 1.0
    target_lat = 0.0
    target_lon = satellite_lon
elif args.mode == "f":
    zoom = 1.0
    target_lat = 0.0
    target_lon = 0.0

fov = math.radians(args.fov)
threads_num = args.threads
# ----------------------------------------------------
# input_filename = "11.jpg"
# interpolate = False

# Copenhagen
# zoom = 10.0
# target_lat = math.radians(55.6814)
# target_lon = math.radians(12.6107)

# Saint Petersburg
# zoom = 40.0
# target_lat = math.radians(59.9401)
# target_lon = math.radians(30.3715)

# output_width = 1000
# zoom = 5.0
# target_lat = math.radians(55.6)
# target_lon = math.radians(22.5)

# zoom = 230.0
# target_lat = math.radians(22.2)
# target_lon = math.radians(satellite_lon - 7.0)
# ----------------------------------------------------
h_to_r = h / r
h_to_r_1 = h_to_r + 1.0
# d = (h * (2.0 * r + h)) ** 0.5

max_lon = math.atan((2.0 * h_to_r + h_to_r ** 2) ** 0.5)
visible_angle = math.atan(1.0 / ((2.0 * h_to_r + h_to_r ** 2) ** 0.5))

cos_max_lon = math.cos(max_lon)

input_image = Image.open(input_filename, 'r')
input_size = input_image.size[0]
input_center = input_size / 2.0
fov_scaled = input_size / fov


def bilinear_interpolation(pixels, x_px, y_px):
    x0 = math.floor(x_px)
    x1 = x0 + 1
    y0 = math.floor(y_px)
    y1 = y0 + 1

    Ia = pixels[x0, y0]
    Ib = pixels[x1, y0]
    Ic = pixels[x0, y1]
    Id = pixels[x1, y1]

    wa = (x1 - x_px) * (y1 - y_px)
    wb = (x_px - x0) * (y1 - y_px)
    wc = (x1 - x_px) * (y_px - y0)
    wd = (x_px - x0) * (y_px - y0)

    def weight(c):
        return int(wa * Ia[c] + wb * Ib[c] + wc * Ic[c] + wd * Id[c])

    return weight(0), weight(1), weight(2)


def angle_to_pixel(angle):
    return input_center + angle * fov_scaled


def equirectangular_projection_rev(yy):
    return yy


def mercator_projection_rev(yy):
    return 2.0 * math.atan(math.e ** yy) - math.pi * 0.5


def mercator_projection(lat):
    return math.log(math.tan(0.5 * lat + math.pi / 4.0))


def miller_projection_rev(yy):
    return 2.5 * math.atan(math.e ** (yy * 0.8)) - math.pi * 0.625


def miller_projection(lat):
    return 1.25 * math.log(math.tan(0.4 * lat + math.pi / 4.0))


projection_rev = equirectangular_projection_rev
max_y_angle = max_lon

if pr_str == "eq":
    projection_rev = equirectangular_projection_rev
    max_y_angle = max_lon
    target_y = target_lat
elif pr_str == "mer":
    projection_rev = mercator_projection_rev
    max_y_angle = mercator_projection(max_lon)
    target_y = mercator_projection(target_lat)
elif pr_str == "mil":
    projection_rev = miller_projection_rev
    max_y_angle = miller_projection(max_lon)
    target_y = miller_projection(target_lat)

max_x_angle = max_lon

if args.mode == "t":
    max_y_angle = max_lon
elif args.mode == "f":
    max_y_angle = math.pi / 4.0
    zoom = 0.5
    pass

output_height = int(round(output_width * max_y_angle / max_lon))


def worker(i, output_image_mutex):
    t0 = time.clock()

    x_mul = 2.0 * max_x_angle / output_width / zoom
    y_mul = 2.0 * max_y_angle / output_height / zoom

    x_d = max_x_angle / zoom
    y_d = max_y_angle / zoom

    chunk_size = int(math.ceil(float(output_height) / threads_num))
    chunk_offset = i * chunk_size
    next_chunk_offset = (i + 1) * chunk_size

    output_image_part = Image.new('RGB', (output_width, chunk_size))
    output_pixels_part = output_image_part.load()

    input_image = Image.open(input_filename, 'r')
    input_pixels = input_image.load()

    for y in range(chunk_offset, next_chunk_offset):

        if i == 0:
            t1 = time.clock()
            if t1 - t0 > 1:
                t0 = t1
                print(str(round(float(y * threads_num) / output_height * 100.0, 1)) + "%")

        lat = projection_rev(y_mul * float(y) - y_d - target_y)

        dec_z = math.sin(lat)
        cos_lat = math.cos(lat)

        for x in range(0, output_width):
            lon = x_mul * float(x) - x_d + target_lon - satellite_lon

            if math.fabs(lon) > max_lon:
                continue

            dec_x = cos_lat * math.cos(lon)

            if dec_x < cos_max_lon:
                continue

            dec_y = cos_lat * math.sin(lon)
            dec_x_v = h_to_r_1 - dec_x

            fi = angle_to_pixel(math.atan2(dec_y, dec_x_v))
            psi = angle_to_pixel(math.atan2(dec_z, dec_x_v))

            try:
                if interpolate:
                    output_pixels_part[x, y - chunk_offset] = bilinear_interpolation(input_pixels, fi, psi)
                else:
                    output_pixels_part[x, y - chunk_offset] = input_pixels[round(fi), round(psi)]
            except IndexError:
                pass

    output_image_mutex.acquire()
    output_image_thread = Image.open(output_filename)
    output_image_thread.paste(output_image_part, (0, chunk_offset))
    output_image_thread.save(output_filename)
    output_image_mutex.release()


def main():
    threads = []

    output_image = Image.new('RGB', (output_width, output_height))
    output_image.save(output_filename)

    output_image_mutex = multiprocessing.Lock()

    for i in range(threads_num):
        t = multiprocessing.Process(target=worker, args=(i, output_image_mutex,))
        threads.append(t)
        t.start()

    for thread in threads:
        thread.join()

    print("Image saved")


if __name__ == '__main__':
    main()
