import argparse
import cv2
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def read_image(fp):
    orig_image = cv2.imread(fp, cv2.IMREAD_UNCHANGED)
    gray_img = cv2.imread(fp, cv2.COLOR_BGR2GRAY)
    a_ratio = orig_image.shape[:2]

    return gray_img, orig_image, a_ratio


def key_points(aratio, gray):
    fast = cv2.FastFeatureDetector_create()
    key_points_ = fast.detect(gray, None)

    pts_array = ([key_points_[x].pt for x in range(0, len(key_points_))])
    logger.info(f'Length of KeyPoints Array: {len(pts_array)}')
    a_ratio = aratio[0]
    b_ratio = aratio[1]

    buffer_pts_array = []
    if a_ratio > b_ratio:
        for tup in pts_array:
            if (.05*a_ratio) <= tup[0] <= (.3*a_ratio) \
                    and (.4*a_ratio) <= tup[1] <= (.66*b_ratio):
                buffer_pts_array.append(tup)
            else:
                pass
        mean_tp = [sum(y) / len(y) for y in zip(*buffer_pts_array)]
        logger.info(f'Adjusted Method Used: {mean_tp}')

    else:
        for tup in pts_array:
            if (.25*a_ratio) <= tup[0] <= (.75*a_ratio) \
                    and (.25*a_ratio) <= tup[1] <= (.75*b_ratio):
                buffer_pts_array.append(tup)
            else:
                pass
        mean_tp = [sum(y) / len(y) for y in zip(*buffer_pts_array)]
        logger.info(f'Unadjusted Method Used: {mean_tp}')

    # result = cv2.drawKeypoints(gray, key_points_, None)

    # plt.imshow(result)
    # plt.axis('off')
    # plt.show()

    return mean_tp


def crop_images(m_tp, fp, aratio):
    a_ratio = aratio[0]
    b_ratio = aratio[1]

    if a_ratio > b_ratio:
        i = int(m_tp[0])
        ver = int(b_ratio / 1.25)
    else:
        i = int((m_tp[1] / 255))
        ver = int(b_ratio / 1.25)

    img = cv2.imread(fp)
    output_image = img[i:i+ver, :]
    # insert_name = fp.split('/')[-1].replace('.jpg','')
    # cv2.imwrite(f'data/{insert_name}_cropped.jpg', output_image)

    return output_image


def run(args_dict):
    fp = args_dict['photopath']

    gray, input_image, aratio = read_image(fp)
    m_tp = key_points(aratio, gray)
    logger.info(f'Average Tuple Point: {m_tp}')
    try:
        output_image = crop_images(m_tp, fp, aratio)
        y_val, x_val = output_image.shape[:2]

        logger.info(f'Aspect Ratio: {x_val}x{y_val}')
        logger.info(f'Aspect Ratio Factor: {(x_val/y_val)}')
        abs_error = abs(1.5 - (x_val / y_val))
        logger.info(f'Error from 1.5: {abs_error}')

        # plt.imshow(output_image)
        # plt.show()

        return output_image

    except IndexError:
        logger.info('Failure to find feature')

        return input_image


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Utility to crop images for features'
    )
    parser.add_argument(
        '-p', '--photopath',
        required=True,
        help='Filepath to photo you are looking to crop',
    )

    args_dict = vars(parser.parse_args())

    run(args_dict)