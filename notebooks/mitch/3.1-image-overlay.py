import cv2

background = cv2.imread('overlay/D2xVPFpU4AI32iy.jpg')
overlay = cv2.imread('overlay/1f44d.png')

added_image = cv2.addWeighted(background, 0.4, overlay, 0.1, 0, 0)

cv2.imwrite('combined.png', added_image)

