import numpy as np
import tensorflow as tf
import cv2
import time

class Modeller(object):
    """
    Класс для работы с моделью нейросети.
    Методы его включают в себя загрузку данных, обучение и переобучение нейросети.
    Также класс включает методы для распознования объектов, поиска и удаления линий
    на изображении.
    """
    def __init__(self):
        self.directory = r'C:/Python_projects/BDRV2/images'
        self.training_directory = r'C:/Python_projects/BDRV2/images/training'
        self.testing_directory = r'C:/Python_projects/BDRV2/images/test'
        self.model_dir = r'C:/Python_projects/BDRV2/model'
        self.result_folder = r'C:/Python_projects/BDRV2/test'

        self.baseColor = () # базовый цвет - то есть цвет фона скриншота мнемосхемы
        self.lines_colors = []  # Цвета линий, связыаающих объекты на мнемосхеме
        self.obj_colors = {} # словарь цветов объектов
        self.contours_list = [] # здесь храним типы контуров с их координатами и размерами
        self.found_contours = [] # здесь храним первоначально найденные контуры

        self.horizontal_lines = []
        self.vertical_lines = []
        self.lines = []

        self.BUFFER_SIZE = 10000
        self.BATCH_SIZE = 64
        self.NUM_EPOCHS = 9

    def upload_datasets(self):
        """
        Функция по загрузке наборов данных из папок на диске
        :return:
        """
        training_datagen = tf.keras.preprocessing.image.ImageDataGenerator(rescale = 1./255)
        training_generator = training_datagen.flow_from_directory(
            self.training_directory,
            target_size=(250, 250),
            class_mode='categorical' # из имён папок берутся названия категорий
        )
        validation_datagen = tf.keras.preprocessing.image.ImageDataGenerator(rescale=1. / 255)
        validation_generator = validation_datagen.flow_from_directory(
            self.testing_directory,
            target_size=(250, 250),
            class_mode='categorical'  # из имён папок берутся названия категорий
        )

        return training_datagen, validation_datagen, training_generator, validation_generator

    def retrain_model(self, model):
        """
            Функция повторного обучения модели
            Входным сигналом служит массив размером 250х250, с окном 3х3.
            :return: ничего не возвращает
            """
        train_dataset, validation_dataset, training_generator, validation_generator = self.upload_datasets()
        print('Массивы данных загружены')
        print('Приступаю к обучению модели...')

        # Обучаем модель с новым коллбеком
        history = model.fit(training_generator,
                            epochs=self.NUM_EPOCHS,
                            validation_data=validation_generator,
                            verbose=1)

        model.save(self.model_dir + r'/trained_model.h5')
        print('Обучение и сохранение модели завершено')

    def create_and_train_model(self):
        """
        Функция создания и обучения модели нейросети. После того, как модель была обучена,
        её можно просто загружать из файла и использовать.
        Входным сигналом служит массив размером 250х250, с окном 3х3.
        :return: ничего не возвращает
        """
        model = tf.keras.models.Sequential([
            tf.keras.layers.Conv2D(64, (3, 3), activation='relu', input_shape=(250, 250, 3)),
            tf.keras.layers.MaxPooling2D(2, 2),
            tf.keras.layers.Conv2D(64, (3, 3), activation='relu'),
            tf.keras.layers.MaxPooling2D(2, 2),
            tf.keras.layers.Conv2D(128, (3, 3), activation='relu'),
            tf.keras.layers.MaxPooling2D(2, 2),
            tf.keras.layers.Conv2D(128, (3, 3), activation='relu'),
            tf.keras.layers.MaxPooling2D(2, 2),
            tf.keras.layers.Flatten(),
            tf.keras.layers.Dropout(0.5),
            tf.keras.layers.Dense(512, activation='relu'),
            tf.keras.layers.Dense(7, activation='softmax')
        ])

        model.compile(loss='binary_crossentropy',
                      optimizer='rmsprop',
                      metrics=['accuracy'])

        train_dataset, validation_dataset, training_generator, validation_generator = self.upload_datasets()
        print('Массивы данных загружены')
        print('Приступаю к обучению модели...')

        model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])

        # Обучаем модель с новым коллбеком
        history = model.fit(training_generator,
                            epochs=self.NUM_EPOCHS,
                            validation_data=validation_generator,
                            verbose=1)

        model.save(self.model_dir + r'/trained_model.h5')
        print ('Обучение и сохранение модели завершено')

    def view_image(self, image):
        """
        Функция для вывода изображения на экран
        :param image:
        :return:
        """
        cv2.namedWindow('Display', cv2.WINDOW_NORMAL)
        cv2.imshow('Display', image)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    def delete_lines_from_colored_image(self, imageWithLines):
        """
        baseColor считываем из файла конфигурации.
        удаляем линии
        :param image: массив, представляющий собой исходную картинку
        :return: массив, представляющий собой исходную картинку с заменёнными пикселами
        """
        for index in range(len(imageWithLines)):
            for jindex in range(len(imageWithLines[index])):
                cur_clr = imageWithLines[index][jindex]
                for clr in self.lines_colors:
                    if (clr[0] == cur_clr[0]) & (clr[1] == cur_clr[1]) & (clr[2] == cur_clr[2]):
                        imageWithLines[index][jindex] = self.baseColor

        return imageWithLines

    def replace_lines(self, imageWithLines, coloredImageSource):
        """
        функция для замены цвета пикселей линий в черно-белом изображении,
        связывающих объекты мнемосхемы
        :param image: массив, представляющий собой исходную картинку
        :return: массив, представляющий собой исходную картинку с заменёнными пикселами
        """
        dt = np.dtype('f8')

        for index in range(len(imageWithLines)):
            for jindex in range(len(imageWithLines[index])):
                if imageWithLines[index][jindex] == 255:
                    coloredImageSource[index][jindex] = (64, 48, 0)

        return coloredImageSource

    def transform_horizontal_and_vertical_lines(self, filename):
        """
        Нахождение горизонтальных и вертикальных линий на скриншоте.
        :param filename: путь к файлу скриншота
        :return: в результате заполняются 2 списка: horizontal_lines и vertical_lines
        """
        image = cv2.imread(filename)
        shape = image.shape  # определяем размер поступившей на вход картинки
        width = shape[1]  # ширина
        height = shape[0]  # высота

        # результирующая картинка - шаблон, заполненный базовым цветом
        result = np.uint8(np.full(shape=(height, width, 3), fill_value= self.baseColor))
        # готовим пустую, залитую цветом фона картинку
        # на неё будем переносить линии
        for row_index in range(height):
            for col_index in range(width):
                cur_clr = image[row_index][col_index]

                for clr in self.lines_colors:
                    if (clr[0] == cur_clr[0]) & (clr[1] == cur_clr[1]) & (clr[2] == cur_clr[2]):
                        # переносим линии на заготовленную картинку
                        result[row_index][col_index][0] = image[row_index][col_index][0]
                        result[row_index][col_index][1] = image[row_index][col_index][1]
                        result[row_index][col_index][2] = image[row_index][col_index][2]

        cv2.imwrite(r'C:/Python_projects/BDRV2/test/' + "lines.png", result)  # записываем файл
        image2 = self.read_image_and_convert_it(result) # преобразуем в чёрно-белое изображение

        bw = cv2.adaptiveThreshold(image2, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 15, -2)
        horizontal = np.copy(bw)
        vertical = np.copy(bw)
        cols  = horizontal.shape[1]
        rows = horizontal.shape[0]

        horizontalsize = int(cols / 30)
        horizontalStructure = cv2.getStructuringElement(cv2.MORPH_RECT, (horizontalsize, 1))
        horizontal = cv2.erode(horizontal, horizontalStructure) # , (-2, -2)
        horizontal = cv2.dilate(horizontal, horizontalStructure) # , (-2, -2)
        cv2.imwrite(r'C:/Python_projects/BDRV2/test/' + "horizontal_lines.png", horizontal)  # записываем файл

        begins_of_lines = []
        ends_of_lines = []
        for row_index in range(height-1):
            for col_index in range(1, width-1):
                # начало линии - это место, где пиксели сменяют свой цвет с чёрного на белый
                if (horizontal[row_index][col_index - 1] == 0) and (horizontal[row_index][col_index] == 255):
                    begins_of_lines.append((col_index, row_index))
                # конец линии - место, где пиксели сменяют свой цвет с белого на чёрный:
                if (horizontal[row_index][col_index] == 255) and (horizontal[row_index][col_index + 1] == 0):
                    ends_of_lines.append((col_index, row_index))

        # соединяем начала и концы линий:
        for index in range(len(begins_of_lines)):
            col_index = begins_of_lines[index][0]
            row_index = begins_of_lines[index][1]
            color_of_line = (image[row_index][col_index][0],
                             image[row_index][col_index][1],
                             image[row_index][col_index][2])

            self.horizontal_lines.append([begins_of_lines[index][0],
                                        begins_of_lines[index][1],
                                        ends_of_lines[index][0],
                                        ends_of_lines[index][1],
                                        color_of_line])

        index = 0
        while index < len(self.horizontal_lines):
            jindex = 0
            x11 = self.horizontal_lines[index][0]
            y11 = self.horizontal_lines[index][1]
            x12 = self.horizontal_lines[index][2]
            while jindex < len(self.horizontal_lines):
                if index != jindex:
                    x21 = self.horizontal_lines[jindex][0]
                    y21 = self.horizontal_lines[jindex][1]
                    x22 = self.horizontal_lines[jindex][2]

                    delta_x1 = x11 - x21
                    delta_x2 = x12 - x22
                    delta_y = y21 - y11

                    if (-3 <= delta_x1 <= 5) and (1 <= delta_y <= 3) and (-3 <= delta_x2 <= 5):
                        self.horizontal_lines.remove(self.horizontal_lines[jindex])
                        jindex -= 1
                jindex += 1
            index += 1

        verticalsize = int(rows / 30)
        verticalStructure = cv2.getStructuringElement(cv2.MORPH_RECT, (1, verticalsize))
        vertical = cv2.erode(vertical, verticalStructure) # , (-2, -2)
        vertical = cv2.dilate(vertical, verticalStructure) # , (-2, -2)

        cv2.imwrite(r'C:/Python_projects/BDRV2/test/' + "vertical_lines.png", vertical)  # записываем файл

        begins_of_lines = []
        ends_of_lines = []
        for col_index in range(width-1):
            for row_index in range(1, height - 1):
                # начало линии - это место, где пиксели сменяют свой цвет с чёрного на белый
                if (vertical[row_index - 1][col_index] == 0) and (vertical[row_index][col_index] == 255):
                    begins_of_lines.append((col_index, row_index))
                # конец линии - место, где пиксели сменяют свой цвет с белого на чёрный:
                if (vertical[row_index][col_index] == 255) and (vertical[row_index + 1][col_index] == 0):
                    ends_of_lines.append((col_index, row_index))

        # соединяем начала и концы линий:
        for index in range(len(begins_of_lines)):
            col_index = begins_of_lines[index][0]
            row_index = begins_of_lines[index][1]
            color_of_line = (image[row_index][col_index][0],
                             image[row_index][col_index][1],
                             image[row_index][col_index][2])

            self.vertical_lines.append([begins_of_lines[index][0],
                                        begins_of_lines[index][1],
                                        ends_of_lines[index][0],
                                        ends_of_lines[index][1],
                                        color_of_line])

        index = 0
        while index < len(self.vertical_lines):
            jindex = 0
            x11 = self.vertical_lines[index][0]
            y11 = self.vertical_lines[index][1]
            y12 = self.vertical_lines[index][3]
            while jindex < len(self.vertical_lines):
                if index != jindex:
                    x21 = self.vertical_lines[jindex][0]
                    y21 = self.vertical_lines[jindex][1]
                    y22 = self.vertical_lines[jindex][3]

                    delta_x = x21 - x11
                    delta_y1 = y11 - y21
                    delta_y2 = y12 - y22

                    if (-5 <= delta_y1 <= 5) and (1 <= delta_x <= 5) and (-5 <= delta_y2 <= 5):
                        self.vertical_lines.remove(self.vertical_lines[jindex])
                        jindex -= 1
                jindex += 1
            index += 1

        image = None
        horizontal = None
        vertical = None

        # Соединение краёв линий для образования прямых углов:
        for index in range(len(self.horizontal_lines)):
            x11 = self.horizontal_lines[index][0]
            y11 = self.horizontal_lines[index][1]
            x12 = self.horizontal_lines[index][2]
            y12 = self.horizontal_lines[index][3]
            for jindex in range(len(self.vertical_lines)):
                x21 = self.vertical_lines[jindex][0]
                y21 = self.vertical_lines[jindex][1]
                x22 = self.vertical_lines[jindex][2]
                y22 = self.vertical_lines[jindex][3]

                if(-10 <= x21 - x11 <= 10) and (1 <= y21 - y11 <= 10):
                    self.horizontal_lines[index][0] = self.vertical_lines[jindex][0]
                    self.vertical_lines[jindex][1] = self.horizontal_lines[index][1]

                if(-10 <= x12 - x22 <= 10) and (-10 <= y22 - y12 <= 10):
                    self.horizontal_lines[index][2] = self.vertical_lines[jindex][2]
                    self.vertical_lines[jindex][3] = self.horizontal_lines[index][3]

    def read_image_and_convert_it(self, image2):
        """
        Преобразование изображения к оттенкам серого для дальнейшего оконтуривания
        :param image2:
        :return:
        """
        hsv_img = cv2.cvtColor(image2, cv2.COLOR_BGR2HSV)
        green_low = np.array([45, 100, 50]) # [45, 100, 50]
        green_high = np.array([75, 255, 255])
        curr_mask = cv2.inRange(hsv_img, green_low, green_high)
        hsv_img[curr_mask > 0] = ([240, 255, 200])
        RGB_again = cv2.cvtColor(hsv_img, cv2.COLOR_HSV2RGB)
        gray = cv2.cvtColor(RGB_again, cv2.COLOR_RGB2GRAY)
        return gray

    def FindContoursInGray(self, gray):
        """
        Функция оконтуривания чернобелого изображения
        :param gray:
        :return:
        """
        ret, treshold = cv2.threshold(gray, 50, 255, 0)
        # view_image(treshold)

        # создайте и примените закрытие
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (7, 7))
        closed = cv2.morphologyEx(treshold, cv2.MORPH_CLOSE, kernel)

        countours, hirerarchy = cv2.findContours(treshold, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        cv2.drawContours(gray, countours, -1, (0, 150, 0), 3)
        return gray, countours

    def merge_contours(self, contours_type=None):
        """
        Функция объединяет близлежащие или вложенные контуры
        :param contours: это массив списков, каждый из которых представляет собой набор из 4х параметров:
        х - координата центра прямоугольника, очерчивающего контур найденного объекта
        у - координата центра прямоугольника, очерчивающего контур найденного объекта
        h - высота контура
        w - ширина контура
        :return:
        """
        if contours_type is None:
            contours_type = []
        index = 0
        circle_end = len(self.found_contours)

        while (index < circle_end):
            jindex = 0
            while (jindex < circle_end):
                if (index != jindex):
                    x1 = self.found_contours[index][0]
                    y1 = self.found_contours[index][1]
                    w1 = self.found_contours[index][2]
                    h1 = self.found_contours[index][3]

                    x2 = self.found_contours[jindex][0]
                    y2 = self.found_contours[jindex][1]
                    w2 = self.found_contours[jindex][2]
                    h2 = self.found_contours[jindex][3]

                    delta_bottom = (y1 + h1) - y2  # расстояние между нижним краем контура А и верхним краем контура В
                    delta_right = x2 - (x1 + w1)  # расстояние между левым краем контура В и правым краем контура А
                    delta_left = x1 - (x2 + w2)  # расстояние между левым краем контура A и правым краем контура B

                    if (x2 > x1) & (y2 > y1):
                        if ((x2+w2) < (x1+w1)) & ((y2+h2) < (y1+h1)):
                            #контур В входит в контур А
                            self.found_contours.remove([x2, y2, w2, h2])
                            circle_end = len(self.found_contours)
                            jindex -= 1
                            continue

                    if (y2 >= y1) & ((y2 + h2) <= (y1 + h1)):
                        if (0 <= delta_right <= 5) or (5 <= delta_left < 10):
                            # контур В находится справа или слева от контура А
                            # определяем новый размер контуров:
                            if 0 <= delta_right <= 5:
                                new_w = w1 + w2 + delta_right
                                self.found_contours[index][0] = x1
                                self.found_contours[index][1] = y1
                                self.found_contours[index][2] = new_w
                                self.found_contours[index][3] = h1
                                self.found_contours.remove([x2, y2, w2, h2])
                            else:
                                new_w = w1 + w2 + delta_left
                                self.found_contours[index][0] = x2
                                self.found_contours[index][1] = y1
                                self.found_contours[index][2] = new_w
                                self.found_contours[index][3] = h1
                                self.found_contours.remove([x2, y2, w2, h2])

                            circle_end = len(self.found_contours)
                            jindex -= 1
                            continue
                    # Контур В находится ниже контура А, и при этом не сильно выдаётся по горизонтали вправо/влево:
                    if (0 <= delta_bottom <= 10) & \
                            ((-5 <= delta_right <= 5) or (5 <= delta_left <= 10)):
                        self.found_contours[index][0] = x1
                        self.found_contours[index][1] = y1
                        self.found_contours[index][2] = w2
                        self.found_contours[index][3] = h1+h2
                        self.found_contours.remove([x2, y2, w2, h2])
                        circle_end = len(self.found_contours)
                        jindex -= 1
                        continue

                jindex += 1
            index += 1
        return self.found_contours

    def gcd(self, a, b):
        """
        Функция определения наибольшего общего детилеля
        :param a: размер стороны
        :param b: размер стороны
        :return: наибольший общий делителя
        """
        if b == 0:
            return a
        return self.gcd(b, a % b)

    def resize_image(self, image):
        """
        Функция для изменения размера массива image в размер 250х250x3,
        так как именно такой размер воспринимает нейросеть и на нём
        она и была обучена ранее.
        :param image: это массив, представляющий собой часть исходной картинки
        :return: массив, размером 250х250
        """
        # результирующая картинка - шаблон, заполненный базовым цветом
        result = np.uint8(np.tile(0, (250, 250, 3)))

        for index in range(250):
            for jindex in range(250):
                result[index][jindex][0] = self.baseColor[0]
                result[index][jindex][1] = self.baseColor[1]
                result[index][jindex][2] = self.baseColor[2]

        shape = image.shape # определяем размер поступившей на вход картинки
        width = shape[0] # ширина
        height = shape[1] # высота
        gcd_val = self.gcd(width, height)    # определяем наибольший общий детилель
        aspect_ratio_width = int(width/gcd_val) # соотношение сторон по ширине
        aspect_ratio_heigth = int(height/gcd_val) # соотношение сторон по высоте

        # если картинка шире, чем 250 пикселей, то нужно будет поменять её размер
        if width > 250:
            width = 250
            height = int((250 * aspect_ratio_heigth) / aspect_ratio_width)

        # если картинка выше, чем 250 пикселей, то нужно поменять её размер
        if height > 250:
            height = 250
            width = int((250 * aspect_ratio_width) / aspect_ratio_heigth)

        # Так как у нас уже есть подготовленный базовый рисунок размером 250х250,
        # то далее необходимо полученный на входе рисунок разместить по центру
        # этого базового рисунка и вернуть результат
        if (width != 0) & (height != 0):
            cindex = 0
            for index in range (125-int(width/2), 125+int(width/2)):
                dindex = 0
                for jindex in range (125-int(height/2), 125+int(height/2)):
                    result[index][jindex][0] = image[cindex][dindex][0]
                    result[index][jindex][1] = image[cindex][dindex][1]
                    result[index][jindex][2] = image[cindex][dindex][2]
                    dindex += 1
                cindex += 1

        return result

    def get_type_of_object(self, predictions, coloredImageRender, x, y, w, h):
        """
        Функция определения типа объекта
        :param prediction: предсказание в виде кортежа
        :param coloredImageRender: картинка, на которой нарисуем контур объекта
        :param x, y, h, w: координаты контура, высота и ширина его
        :return: тип объекта, строка
        """

        if predictions[0][0] != 0:
            img = cv2.rectangle(coloredImageRender,
                                (x, y),
                                (x + w, y + h),
                                self.obj_colors['collon'],
                                2)  # жёлтый - колонны
            return "collon"
        if predictions[0][1] != 0:
            img = cv2.rectangle(coloredImageRender,
                                (x, y),
                                (x + w, y + h),
                                self.obj_colors['heat-exchanger'],
                                2)  # красный - теплообменники
            return "heat-exchanger"
        if predictions[0][2] != 0:
            img = cv2.rectangle(coloredImageRender,
                                (x, y),
                                (x + w, y + h),
                                self.obj_colors['indicator'],
                                2)  # голубой - индикаторы
            return "indicator"
        if predictions[0][3] != 0:
            img = cv2.rectangle(coloredImageRender,
                                (x, y),
                                (x + w, y + h),
                                self.obj_colors['pump'],
                                2)  # зелёный - насосы
            return "pump"
        if predictions[0][4] != 0:
            img = cv2.rectangle(coloredImageRender,
                                (x, y),
                                (x + w, y + h),
                                self.obj_colors['tank'],
                                2)  # оранжевый - резервуары
            return "tank"
        if predictions[0][5] != 0:
            img = cv2.rectangle(coloredImageRender,
                                (x, y),
                                (x + w, y + h),
                                self.obj_colors['text'],
                                2)  # пурпурный - текст
            return"text"
        if predictions[0][6] != 0:
            img = cv2.rectangle(coloredImageRender,
                                (x, y),
                                (x + w, y + h),
                                self.obj_colors['valve'],
                                2)  # серый - арматура
            return "valve"
        return "unknown"

    def analize_screenshot(self, filename2):
        """
        Функция анализа скриншота. Результатом будет картинка, на которой будут
        выделены контуры найденных объектов.
        """
        folder_contours = r"C:/Python_projects/BDRV2/test/images_by_contours/"

        coloredImage = cv2.imread(filename2)
        coloredImageRender = cv2.imread(filename2)
        image3 = self.delete_lines_from_colored_image(coloredImage) # удаляем линии
        # cv2.imwrite(self.result_folder + r'/without_lines.png', image3)  # записываем файл для контроля
        self.transform_horizontal_and_vertical_lines(filename2) # обнаружение горизонт. и верт. линий на скриншоте

        # Размываем изображение, конвертируем его в чёрно-белое и находим контуры объектов:
        image5, contours = self.FindContoursInGray(self.read_image_and_convert_it(cv2.blur(image3, (5, 5))))

        index = 0
        while (index < len(contours)):
            cnt = contours[index]  # получаем очередной контур
            # определяем координаты контура
            x, y, w, h = cv2.boundingRect(cnt)

            # аппроксимируем (сглаживаем) контур
            peri = cv2.arcLength(cnt, True)
            approx = cv2.approxPolyDP(cnt, 0.02 * peri, True)

            if len(approx) >= 4:
                self.found_contours.append([x, y, w, h])
            index += 1

        # Объединяем контуры, которые находятся близко друг к другу:
        contours_to_draw = self.merge_contours()

        # Восстановим в точности ту же модель, включая веса и оптимизатор
        new_model = tf.keras.models.load_model(self.model_dir + r'/trained_model.h5')

        # Рассматриваем каждый найденный объект и проверяем - к какому классу
        # объектов он принадлежит:
        index = 0

        while index < len(contours_to_draw):
            x = contours_to_draw[index][0]
            y = contours_to_draw[index][1]
            w = contours_to_draw[index][2]
            h = contours_to_draw[index][3]

            if ((w * h) > 50) and ((w * h) < 100000):
                # определяем размерность картинки
                dArr = np.uint8(np.tile(0, (h, w, 3)))

                # заполняем массив данными из первоначальной цветной картинки:
                cindex = x
                for xindex in range(w):
                    dindex = y
                    for jindex in range(h):
                        dArr[jindex][xindex][0] = coloredImage[dindex][cindex][0]
                        dArr[jindex][xindex][1] = coloredImage[dindex][cindex][1]
                        dArr[jindex][xindex][2] = coloredImage[dindex][cindex][2]
                        dindex += 1
                    cindex += 1

                new_img = np.uint8(Modeller.resize_image(self, dArr))

                # Добавим изображение в пакет, где он является единственным членом
                img2 = (np.expand_dims(new_img, 0))
                predictions = new_model.predict(img2, batch_size=6)
                # определяем тип объекта, обведённого текущим контуром:
                pd = self.get_type_of_object(predictions, coloredImageRender, x, y, w, h)
                obj_title = 'object-'+str(time.clock())
                # записываем тип контура, его коорд. и размеры:
                self.contours_list.append([obj_title, pd, x, y, w, h, ""])
                cv2.imwrite(folder_contours + str(pd) + "_" + str(index) + ".png", new_img) # записываем файл
            index += 1
        return

