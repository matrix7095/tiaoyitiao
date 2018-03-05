import cv2
import math
import os
import time
import numpy as np


class Tiaoyitiao():

    def _find_position(self, image, kernel):
        """
        find the location of the starting point by using the correlation operation

        :param image:the screen shot image
        :param kernel:the shape of the pawn
        :return:the position of pawn
        """

        kernel = cv2.Canny(kernel, 100, 200)
        image = cv2.Canny(image, 100, 200)

        dis = cv2.filter2D(image.astype(int), -1, kernel.astype(int)).astype(int)

        m, n = np.where(dis[300:-600, 100:-100] == np.max(dis[300:-600, 100:-100]))

        return n[0] + 100, m[0] + 300 + 60

    def _find_destination(self, image, position_x):
        """
        find the destination

        :param image: the screen shot image
        :param position_x: the x position of pawn
        :return:position of destination
        """

        edge = cv2.Canny(image, 10, 50)

        c, k = edge.shape

        edge[:, position_x - 45:position_x + 45] = 0

        isFlip = False

        if position_x < 540:
            position_x = k - position_x
            edge = cv2.flip(edge, 1)
            isFlip = True

        y_max = np.max(edge, 1)

        y_corner = np.where(y_max[300:1000] == 255)[0][0] + 300

        x = np.mean(np.where(edge[y_corner, :] == 255)[0][0]).astype(int)

        if isFlip:
            x = k - x
            position_x = k - position_x

        pre_edge = x
        for i in range(y_corner, y_corner + 500):
            i += 1

            try:
                current_edge = np.where(edge[i, :] == 255)[0][0]
                next_edge = np.where(edge[i + 1, :] == 255)[0][0]
            except:
                continue
            if current_edge < pre_edge:
                pre_edge = current_edge
            elif current_edge == pre_edge:
                if current_edge == next_edge:
                    break
            else:

                break

        return x, i

    def _draw(self, image, position_x, position_y, destination_x, destination_y):
        """
        draw pawn and destination position on the image

        :param image: background image
        :param position_x: the x position of the pawn
        :param position_y: the y position of the pawn
        :param destination_x: the x position of the destination
        :param destination_y: the y position of the destination
        :return:new image with the position
        """

        image = cv2.circle(image, (position_x, position_y), 20, thickness=3, color=(255, 255, 255))
        image = cv2.circle(image, (destination_x, destination_y), 60, thickness=5, color=(0, 0, 0))
        return image

    def test(self, read_dir="./jump/", save_dir="./test/", kernel_dir="kernel.png"):
        """
        testing with image and kernel
        
        :param read_dir: the path of the image 
        :param save_dir: the path of saving tested image
        :param kernel_dir: the path of the kernel
        :return: 
        """

        imgs = sorted(os.listdir(read_dir))
        count = 0
        for img in imgs:
            if img[-4:] == ".png":
                count += 1
                print("testing %05d.png" % count)
                image = cv2.imread(read_dir + img)
                kernel = cv2.imread(kernel_dir)

                position_x, position_y = self._find_position(image, kernel)
                destination_x, destination_y = self._find_destination(image, position_x)

                image = self._draw(image, position_x, position_y, destination_x, destination_y)

                cv2.imwrite(save_dir + '%05d.png' % count, image)

    def start(self, standard=True, kernel_dir="kernel.png"):
        """
        jumping

        :param standard: 1920X1080 ?
        :param kernel_dir: the path of the kernel
        :return:
        """

        count = 0
        kernel = cv2.imread(kernel_dir)
        while True:
            count += 1
            image_name = "%05d.png" % count

            os.system("adb shell screencap -p /sdcard/%s " % image_name)
            os.system("adb pull /sdcard//%s ./jump/%s" % (image_name, image_name))

            image = cv2.imread("./jump/%s" % image_name)
            if not standard:
                image = cv2.resize(image, (1080, 1920))

            position_x, position_y = self._find_position(image, kernel)
            destination_x, destination_y = self._find_destination(image, position_x)

            distance = math.sqrt((position_x - destination_x) ** 2 + (position_y - destination_y) ** 2)
            swipe_time = max(math.pow(distance, 0.85) * 3.60, 300)

            os.system("adb shell input swipe 600 1600 600 1600 %d " % swipe_time)
            time.sleep(2)


if __name__ == '__main__':
    t = Tiaoyitiao()
    t.start()
    t.test()
