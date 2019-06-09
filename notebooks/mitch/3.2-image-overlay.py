import cv2
import numpy as np


def resize_img(image):
    height, width = image.shape[:2]
    max_height = 100000
    max_width = 175

    # only shrink if img is bigger than required
    if max_height < height or max_width < width:
        # get scaling factor
        scaling_factor = max_height / float(height)
        if max_width/float(width) < scaling_factor:
            scaling_factor = max_width / float(width)
        # resize image
        image = cv2.resize(image, None, fx=scaling_factor, fy=scaling_factor, interpolation=cv2.INTER_AREA)

    return image

def overlay_transparent(background, overlay, x, y):
    background_width, background_height = background.shape[:2]

    if x >= background_width or y >= background_height:
        return background

    h, w = overlay.shape[:2]

    if x + w > background_width:
        w = background_width - x
        overlay = overlay[:, :w]

    if y + h > background_height:
        h = background_height - y
        overlay = overlay[:h]

    if overlay.shape[2] < 4:
        overlay = np.concatenate(
            [
                overlay,
                np.ones((overlay.shape[0], overlay.shape[1], 1), dtype = overlay.dtype) * 255
            ],
            axis = 2,
        )

    overlay_image = overlay[..., :3]
    mask = overlay[..., 3:] / 255.0

    background[y:y+h, x:x+w] = (1.0 - mask) * background[y:y+h, x:x+w] + mask * overlay_image

    return background


def get_coordinates(background, overlay):
    half, extra_half = background.shape[1]/2, overlay.shape[1]/2
    return int(half - extra_half), 110


def crop_image(y, x, image):
    h, w = image.shape[:2]
    return image[y:y + h, x:x + w]


background = cv2.imread('overlay/background.jpg') # 480 by 492
overlay = cv2.imread('overlay/test2.jpg')
overlay = resize_img(overlay)
import pdb; pdb.set_trace()
if overlay.shape[0] > 100:
    overlay = crop_image(overlay.shape[0]-100, 0, overlay)


x, y = get_coordinates(background, overlay)

img = overlay_transparent(background, overlay, x, y)

cv2.imwrite('overlay/combined_test_17.jpg', img)

