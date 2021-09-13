from PIL import Image, ImageDraw, ImageOps
import numpy as np
# import matplotlib.pyplot as plt
from CalculationWeightLine import createLineIterator  # createLineIterator(np.array([x1, y2]), np.array([x2, y2]), image)
# import cv2
# import pdb
import os

if not os.path.isdir("Made"):
    os.mkdir("Made")  # Создаем пустой каталог если его нет


BOARD_WIDTH = 60  # диаметр картины СМ
PIXEL_WIDTH = float(0.05)  # Размер пикселя при толщине нити 0.14мм
# thickness = 1 # толщина линии, Данная переменная пока не задействована
NUM_NAILS = 257  # кол-во гвоздей(писать на 1 больше чем требуется)
MAX_ITERATIONS = 5000  # кол-во линий
NAILS_SKIP = 10  # пропуск ближайших гвоздей


pixels = int(BOARD_WIDTH / PIXEL_WIDTH)
size = (pixels + 1, pixels + 1)


def cropToCircle(path):
    img = Image.open(path).convert("L")  # открываем и переводим изображение в ч/б
    img = img.resize(size)  # подгоняем изображение под необходимое разрешение
    mask = Image.new('L', size, 0)  # создаем пустое изображение
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0) + size, fill=255)
    mask = mask.resize(img.size, Image.ANTIALIAS)
    img.putalpha(mask)

    output = ImageOps.fit(img, mask.size, centering=(0.5, 0.5))
    output.putalpha(mask)
    return output


# Обрезка изображения до круга
ref = cropToCircle("image.jpg")  # изображение содержит 2 слоя(0-слой с картинкой, 1-слой это заполненный круг)

# plt.imshow(ref, cmap='gray')
# plt.show()

base = Image.new('L', size, color=255)

# Расчет координат гвоздей
angles = np.linspace(0, 2 * np.pi, NUM_NAILS)  # углы к точкам
cx, cy = (BOARD_WIDTH / 2 / PIXEL_WIDTH, BOARD_WIDTH / 2 / PIXEL_WIDTH)  # центр круга
xs = cx + BOARD_WIDTH * 0.5 * np.cos(angles) / PIXEL_WIDTH
ys = cy + BOARD_WIDTH * 0.5 * np.sin(angles) / PIXEL_WIDTH
nails = list(zip(np.around(xs).astype(int), np.around(ys).astype(int)))  # получаем [(x1, y1), (x2, y2),...(xn, yn)] это координаты гвоздей (первый гвоздь nails[0][x=0,y=1])
nails.pop()  # удаляем последний гвоздь т.к. он повтаряет первый(ну тот который нулевой)
# nails = list(map(lambda x,y: (int(x),int(y)), xs,ys))  # альтернативный способ создания координат гвоздец
# print(nails)

img_arr = np.array(ref)[:, :, 0]  # выбираем изображение и переводим в массив
img_arr = 255 - img_arr  # инвертируем изображение

'''
pixels_sum = int(img_arr.sum() * (np.pi/4)) #Сумма всех пикселей на изображении
arr_size = img_arr.shape
print(f"Сумма всех пикселей на изображении: {pixels_sum}")
print(f"Кол-во строк и колонок: {arr_size}")
'''

results = open("results.txt", "w")
res = ""

# cur_nail =a_point, n = b_point  # Предложение о замение начального и конечного гвоздя(для лучшей читаемости кода)
cur_nail = 0  # Задаем начальный гвоздь
new_nail = None


for iter in range(MAX_ITERATIONS):  # Цикл для проведения MAX_ITERATIONS линий на картине

    best_darkness = 0

    for n in range(cur_nail + 1 + NAILS_SKIP, cur_nail + len(nails) - NAILS_SKIP):  # Цикл для проведения линий от текущего гвоздя до каждого другого и поиска лучшей линии
        n = n % (NUM_NAILS - 1)
        darkness = 0

        my_line = createLineIterator(np.array([nails[cur_nail][0], nails[cur_nail][1]]), np.array([nails[n][0], nails[n][1]]), img_arr)

        darkness = np.mean(my_line, axis=0)[2]

        if darkness > best_darkness:  # ветвление для поиска лучшей линии
            best_darkness = darkness
            new_nail = n

    # print(f'Лучшая линия №{iter} {best_darkness}. Она идет от гвоздя {cur_nail} x,y={nails[cur_nail]} до гвоздя {new_nail} x,y={nails[new_nail]}')

    addLine = ImageDraw.Draw(base)  # добавляем лучшую линию на изображение
    addLine.line((nails[cur_nail][0], nails[cur_nail][1], nails[new_nail][0], nails[new_nail][1]), fill=50)

    coordinates_best_line = createLineIterator(np.array([nails[cur_nail][0], nails[cur_nail][1]]), np.array([nails[new_nail][0], nails[new_nail][1]]), img_arr)
    # print(f"Линия №{iter}")
    print(f"Лучшая линия №{iter}. Она идет от гвоздя {cur_nail} x,y={nails[cur_nail]} до гвоздя {new_nail} x,y={nails[new_nail]}")
    # print(f"Она имеет средний вес пикселя: {np.mean(coordinates_best_line, axis=0)[2]}")
    # print(f"Всего пикселей в линии: {coordinates_best_line.shape[0]}")
    # print(f"Полный вес линии: {np.sum(coordinates_best_line[:,2])}")
    # print('')

    res += 'Линия №' + str(iter) + str(' ') + str(cur_nail) + str(' ') + str(new_nail) + ('\n')

    """Цикл ниже в будущем нужно заменить на класс"""
    for k in range(coordinates_best_line.shape[0]):  # Уменьшаем интенсивность под созданной линией
        x_in_arr = coordinates_best_line[k, 0]
        y_in_arr = coordinates_best_line[k, 1]
        # if img_arr[y_in_arr, x_in_arr] >= 30:
        #     img_arr[y_in_arr, x_in_arr] -= 30
        # else:
        #     img_arr[y_in_arr, x_in_arr] = 0

        if x_in_arr >= 400 and x_in_arr <= 800 and y_in_arr >= 400 and y_in_arr <= 800:
            img_arr[y_in_arr, x_in_arr] -= int(img_arr[y_in_arr, x_in_arr] / 6)
        else:
            img_arr[y_in_arr, x_in_arr] -= int(img_arr[y_in_arr, x_in_arr] / 4)

    cur_nail = new_nail

# plt.imshow(base, cmap='gray')
# plt.show()
base.save('FINAL_FILE.png')  # Сохраняем конечный файл
ref.save('ORIGINAL.png')  # Сохраняем входное изображение в виде круга

results.write(res)  # Записываем последовательность точек в файл
results.close()

os.replace("FINAL_FILE.png", "Made/FINAL_FILE.png")
os.replace("ORIGINAL.png", "Made/ORIGINAL.png")
os.replace("results.txt", "Made/results.txt")
"""
Что еще нужно сделать:
1) Откорректировать вывод данных
2) Связать вывод данных с файлом string_post.py
3) Файл string_post.py отредактировать
4) В цикле 'n' попытаться сделать проверку линий соседствующих с линией my_line
5) Заменить цикл отнимания веса линии(цикл 'k') на класс(но это не точно)
"""

'''
Поиск линий с соседними линиями. Используй его, когда все будет готово


left_line = createLineIterator(np.array([nails[0][0]-1, nails[0][1]-1]), np.array([nails[1][0]-1, nails[1][1]-1]), img_arr)

my_line = createLineIterator(np.array([nails[0][0], nails[0][1]]), np.array([nails[1][0], nails[1][1]]), img_arr)

right_line = createLineIterator(np.array([nails[0][0]+1, nails[0][1]+1]), np.array([nails[1][0]+1, nails[1][1]+1]), img_arr)

darkness = (int(np.sum(left_line[:,2])) + int(np.sum(my_line[:,2])) + int(np.sum(right_line[:,2]))) / (3 * (left_line.shape[0] + my_line.shape[0] + right_line.shape[0]))

'''
