__author__ = 'weixin'

def rgb2gray(image):
    img = []
    height = len(image)
    width = len(image[0])
    for row in xrange(height):
        img.append([])
        for col in range(width):
            mean = sum(image[row][col])/3
            img[row].append((mean, mean, mean))
    return img



