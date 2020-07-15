from tkinter import *
from tkinter import filedialog
from tkinter import messagebox
from tkinter import ttk
import io

from PIL import Image, ImageTk

from BDRV_Scripts.preprocessing.MainScript import Modeller
from BDRV_Scripts.preprocessing.MnemoObj import MnemoObj
from BDRV_Scripts.preprocessing.MnemoObjList import MnemoObjList

class GUI(object):
    def __init__(self):
        self.config_file_path = r'C:/Python_projects/BDRV2/config/bdrv_config.txt'
        self.uploadedScreenshot = '' # здесь будем хранить путь к скриншоту мнемосхемы
        self.obj_colors = {}  # словарь для хранения цветов объектов
        self.image_with_objects = None  # путь к изображению с обнаруженными объектами
        self.canvas_with_objects = None  # канва, на которой работаем с найденными объектами
        self.display_image = None  # отображаемая картинка в Canvas
        self.ph = None  # отображаемый прямоугольник поверх объекта
        self.rect = None  # прямоугольник для обводки объекта мнемосхемы под курсором

        self.mnemo_obj_list = MnemoObjList()
        self.Md = Modeller()  # класс для работы с нейросетью

        self.window = Tk() # главное окно интерфейса
        self.frame_right_menu = ttk.Frame(self.window, width=200)
        self.tab_control = ttk.Notebook(self.window)  # вкладки на главном окне
        self.lbl_tree = ttk.Label(self.frame_right_menu, text='Объекты мнемосхемы:')
        self.obj_tree = ttk.Treeview(self.frame_right_menu)
        self.frame_right_menu_sub = ttk.Frame(self.frame_right_menu)
        self.window.title("Автомнемо")
        self.window.geometry('1000x650')

        self.frame_right_menu.pack(side=RIGHT, fill=Y)

        self.tab1 = ttk.Frame(self.tab_control)
        self.tab2 = ttk.Frame(self.tab_control)
        self.tab3 = ttk.Frame(self.tab_control)

        self.lbl_tree.pack(side=TOP)

        self.obj_tree.master = self.frame_right_menu
        self.obj_tree["columns"] = ("one", "two", "three")
        self.obj_tree.column("#0", width=100, minwidth=20)
        self.obj_tree.column("one", width=70, minwidth=10)
        self.obj_tree.column("two", width=70, minwidth=20)

        self.obj_tree.heading("#0", text="Имя")
        self.obj_tree.heading("one", text="Х")
        self.obj_tree.heading("two", text="Y")

        # Level 1
        self.folder1 = self.obj_tree.insert("", 0, "collon", text="Колонны", values=("collon", "", ""))
        self.folder2 = self.obj_tree.insert("", 1, "heat-exchanger", text="Теплообменники",
                                            values=("heat-exchanger", "", ""))
        self.folder3 = self.obj_tree.insert("", 2, "indicator", text="Индикаторы", values=("indicator", "", ""))
        self.folder4 = self.obj_tree.insert("", 3, "pump", text="Насосы", values=("pump", "", ""))
        self.folder5 = self.obj_tree.insert("", 4, "tank", text="Резервуары", values=("tank", "", ""))
        self.folder6 = self.obj_tree.insert("", 5, "valve", text="Арматура", values=("valve", "", ""))
        self.folder7 = self.obj_tree.insert("", 6, "text", text="Текст", values=("text", "", ""))
        self.obj_tree.pack(side=TOP)

        self.frame_right_menu_sub.pack(side=TOP)
        self.lbl_mn_obj = ttk.Label(self.frame_right_menu_sub, text='Свойства объекта:')
        self.lbl_mn_obj.pack(side=TOP)

        self.frame_right_menu_sub0 = ttk.Frame(self.frame_right_menu)
        self.frame_right_menu_sub0.pack(side=TOP)
        self.frame_right_menu_sub00 = ttk.Frame(self.frame_right_menu)
        self.frame_right_menu_sub00.pack(side=TOP)
        self.lbl_objName = ttk.Label(self.frame_right_menu_sub00, text='Имя объекта:')
        self.lbl_objName.pack(side=LEFT)
        self.txtObjName = ttk.Entry(self.frame_right_menu_sub00)
        self.txtObjName.pack(side=LEFT)
        self.frame_right_menu_sub1 = ttk.Frame(self.frame_right_menu_sub00)
        self.frame_right_menu_sub1.pack(side=LEFT)
        self.lblObjType = ttk.Label(self.frame_right_menu_sub1, text='Тип объекта:')
        self.lblObjType.pack(side=LEFT)
        self.cmbxObjType = ttk.Combobox(self.frame_right_menu_sub1)
        self.cmbxObjType['values'] = ('collon',
                                      'heat-exchanger',
                                      'indicator',
                                      'pump',
                                      'tank',
                                      'valve',
                                      'text')
        self.cmbxObjType.pack(side=LEFT)

        self.frame_right_menu_sub2 = ttk.Frame(self.frame_right_menu)
        self.frame_right_menu_sub2.pack(side=TOP)
        self.lblcoord = ttk.Label(self.frame_right_menu_sub2, text='Координаты объекта:')
        self.lblcoord.pack(side=LEFT)
        self.lblX = ttk.Label(self.frame_right_menu_sub2, text='x:')
        self.lblX.pack(side=LEFT)
        self.lblXval = ttk.Label(self.frame_right_menu_sub2, text='')
        self.lblXval.pack(side=LEFT)
        self.lblY = ttk.Label(self.frame_right_menu_sub2, text='y:')
        self.lblY.pack(side=LEFT)
        self.lblYval = ttk.Label(self.frame_right_menu_sub2, text='')
        self.lblYval.pack(side=LEFT)

        self.frame_right_menu_sub3 = ttk.Frame(self.frame_right_menu)
        self.frame_right_menu_sub3.pack(side=TOP)
        self.btnSaveObj = ttk.Button(self.frame_right_menu_sub3, text='Сохранить изменения')
        self.btnSaveObj.pack(side=LEFT)
        self.btnDelObj = ttk.Button(self.frame_right_menu_sub3, text='Удалить объект')
        self.btnDelObj.pack(side=LEFT)

        # Вкладки:
        self.tab_control.add(self.tab1, text='Скриншот мнемосземы')
        self.tab_control.add(self.tab2, text='Обнаруженные объекты')
        self.tab_control.add(self.tab3, text='Обнаруженные линии')
        self.tab_control.pack(expand=1, fill='both')

        # читаем файл конфигурации:
        with io.open(self.config_file_path) as config:
            row = config.readline()
            row = config.readline()
            row = row.split(' ')
            # базовый цвет - цвет фона мнемосхемы
            self.Md.baseColor = (int(row[0]), int(row[1]), int(row[2].rstrip('\n')))
            row = config.readline()
            row = config.readline()
            # цыета линий:
            while row != '===objects-colors:===\n':
                row = row.split(' ')
                self.Md.lines_colors.append((int(row[0]), int(row[1]), int(row[2].rstrip('\n'))))
                row = config.readline()
            # цвета объектов:
            row = config.readline()
            while row != '=== end of objects-colors ===\n':
                row = row.split(' ')
                if row[0] != '===':
                    self.Md.obj_colors[row[0]] = (int(row[1]), int(row[2]), int(row[3]))
                    self.obj_colors[row[0]] = row[4].rstrip('\n')
                else:
                    break
                row = config.readline()
            config.close()

    def buildWindow(self):
        """
            Функция построения окна программы
        """
        # Главное меню:
        menu = Menu(self.window)
        new_item = Menu(menu)
        new_item.add_command(label = 'Загрузить скриншот мнемосхемы', command = lambda: self.uploadScreenshot(self))
        new_item.add_command(label = 'Запустить обнаружение объектов', command = lambda: self.detectObjects(self))
        new_item.add_command(label = 'Сохранить найденные контуры в файл', command=lambda: self.saveFoundContours(self))
        new_item.add_command(label = 'Открыть файл с контурами', command=lambda: self.openFoundContours(self))

        menu.add_cascade(label = 'Файл', menu=new_item)
        self.window.config(menu = menu)

        self.window.mainloop()

    def uploadScreenshot(self, file=None):
        """
        Функция команды меню - Загрузить файл мнемосхемы.
        Загружается файл и выводится на первую вкладку в окне программы
        """
        # получаем имя файла:
        if file == None:
            filename = filedialog.askopenfilename(filetypes = (("png files","*.png"),("all files","*.*")))
            tab = self.tab1
        else:
            # открываем файл с обнаруженными ранее объектами мнемосхемы
            filename = file
            tab = self.tab2
        screenshot = Image.open(filename)
        self.uploadedScreenshot = filename # сохраняем путь к скриншоту для дальнейшего использования

        self.uploadImage(self, screenshot, tab)

    def detectObjects(self):
        """
        Функция обнаружения объектов на скриншоте
        """
        if self.uploadedScreenshot == "":
            messagebox.showinfo('Ошибка поиска объектов', 'Загрузите файл мнемосхемы')
            return
        else:
            messagebox.showinfo('Обнаружение объектов', 'Поиск объектов может занять некоторое время. Подождите.')
            # проводим анализ загруженного скриншота:
            self.image_with_objects = self.Md.analizeScreenshot(self.uploadedScreenshot)
            screenshot = Image.open(self.image_with_objects)
            # messagebox.showinfo('Обнаружение объектов', 'Обработка скриншота завершена')
            self.uploadImage(self, screenshot, self.tab2) # выводим результат анализа скриншота

    def uploadImage(self, screenshot, tab_obj):
        """
        Функция вывода изображения (screenshot) на вкладку (tab)
        """
        frame = Frame(tab_obj)
        frame.pack(expand=True, fill=BOTH)

        vbar = Scrollbar(frame, orient=VERTICAL)
        vbar.pack(side=RIGHT, fill=Y)
        hbar = Scrollbar(frame, orient=HORIZONTAL)
        hbar.pack(side=BOTTOM, fill=X)
        self.canvas_with_objects = Canvas(frame,
                                          yscrollcommand=vbar.set,
                                          xscrollcommand=hbar.set)
        self.canvas_with_objects.pack(side=LEFT, expand=True, fill=BOTH)

        # Сохраняем картинку в переменную класса, чтобы сборщик мусора её не уничтожил раньше времени:
        self.display_image = ImageTk.PhotoImage(screenshot)

        self.canvas_with_objects.config(width=screenshot.width, height=screenshot.height)
        self.canvas_with_objects.config(scrollregion=(0, 0, 400, 1000))
        self.canvas_with_objects.create_image(screenshot.width / 2, screenshot.height / 2,
                                                              image=self.display_image)

        # отслеживаем координаты курсора:
        self.canvas_with_objects.bind("<Motion>", lambda event: self.onOverTheObjectMove(self))
        # полосы прокрутки:
        vbar.config(command=self.canvas_with_objects.yview)
        hbar.config(command=self.canvas_with_objects.xview)

        for index in range(len(self.Md.contours_list)):
            # проходим по списку обнаруженных контуров
            obj_title = 'object-' + str(index)
            mn_obj = MnemoObj(self.Md.contours_list[index])  # создаём объект мнемосхемы
            mn_list_el = MnemoObjList() # новый элемент списка
            mn_list_el.key = mn_obj
            self.mnemo_obj_list.insert(mn_list_el)  # вставляем объект в список
            self.insertObjIntoTree(self, mn_obj=mn_obj) # вставляем объект в дерево объектов

    def insertObjIntoTree(self, mn_obj):
        """
        Вставить объект в дерево объектов.
        mn_obj: объект типа MnemoObj
        """
        if mn_obj.type == "collon":
            self.obj_tree.insert(self.folder1, "end", mn_obj.obj_name, text=mn_obj.obj_name, values=(mn_obj.x, mn_obj.y))
        else:
            if mn_obj.type == "heat-exchanger":
                self.obj_tree.insert(self.folder2, "end", mn_obj.obj_name, text=mn_obj.obj_name, values=(mn_obj.x, mn_obj.y))
            else:
                if mn_obj.type == "indicator":
                    self.obj_tree.insert(self.folder3, "end", mn_obj.obj_name, text=mn_obj.obj_name, values=(mn_obj.x, mn_obj.y))
                else:
                    if mn_obj.type == "pump":
                        self.obj_tree.insert(self.folder4, "end", mn_obj.obj_name, text=mn_obj.obj_name,
                                             values=(mn_obj.x, mn_obj.y))
                    else:
                        if mn_obj.type == "tank":
                            self.obj_tree.insert(self.folder5, "end", mn_obj.obj_name, text=mn_obj.obj_name,
                                                 values=(mn_obj.x, mn_obj.y))
                        else:
                            if mn_obj.type == "valve":
                                self.obj_tree.insert(self.folder6, "end", mn_obj.obj_name, text=mn_obj.obj_name,
                                                     values=(mn_obj.x, mn_obj.y))
                            else:
                                self.obj_tree.insert(self.folder7, "end", mn_obj.obj_name, text=mn_obj.obj_name,
                                                     values=(mn_obj.x, mn_obj.y))

    def onOverTheObjectMove(self):
        """
        При наведении курсора мыши на объект мнемосхемы - он выделяется
        в дереве объектов, а также выделяется цветом на самой мнемосхеме
        """
        # удаляем нарисованные ранее прямоугольники:
        self.canvas_with_objects.delete(self.canvas_with_objects.find_withtag('rect'))
        if self.mnemo_obj_list != None:
            # Считываем координаты курсора мыши:
            x = self.window.winfo_pointerx() - self.window.winfo_rootx()
            y = self.window.winfo_pointery() - self.window.winfo_rooty()
            # находим - есть ли объект мнемосхемы по этим координатам:
            mn_obj = self.mnemo_obj_list.search_coord(x,y)
            # Если объект мнемосхемы найден:
            if mn_obj != None:
                # курсор попал на объект - обводим его прямоугольником
                self.rect = self.canvas_with_objects.create_rectangle(mn_obj.x, mn_obj.y,
                                                                 mn_obj.x + mn_obj.width,
                                                                 mn_obj.y + mn_obj.height,
                                                                 outline = 'white',
                                                                 width = 5,
                                                                 tag = 'rect')

    def saveFoundContours(self):
        """
        Сохранить найденные контуры и путь к сохранённой картинке/
        Первой строкой в файле будет путь к картинке с нарисованными контурами.
        Все последующие строки - это информация о контурах:
        obj_title; pd; x; y; w; h\n
        """
        # получаем имя файла:
        filename = filedialog.asksaveasfilename(filetypes=(("txt files", "*.txt"), ("all files", "*.*")))

        if len(self.Md.contours_list) != 0:
            with open(filename, mode = 'w') as file:
                file.write(self.uploadedScreenshot + '\n')
                for index in range (len(self.Md.contours_list)):
                    str_to_write = self.Md.contours_list[index][0] + '; ' +\
                                   self.Md.contours_list[index][1] + '; ' +\
                                   str(self.Md.contours_list[index][2]) + '; ' + \
                                   str(self.Md.contours_list[index][3]) + '; ' + \
                                   str(self.Md.contours_list[index][4]) + '; ' + \
                                   str(self.Md.contours_list[index][5]) + '\n'
                    file.write(str_to_write)
                file.close()

    def openFoundContours(self):
        """
        Загрузить картинку с сохранёнными ранее контурами,
        а также перечень контуров
        """
        filename = filedialog.askopenfilename(filetypes=(("txt files", "*.txt"), ("all files", "*.*")))

        if filename != '':
            self.mnemo_obj_list = MnemoObjList()

            with open(filename, mode='r') as file:
                file_rows = file.readlines()

                self.uploadedScreenshot = file_rows[0].rstrip('\n') # считываем путь к картинке с контурами
                self.uploadScreenshot(self, file = self.uploadedScreenshot) # выводим на экран картинку с найденными контурами
                self.window.title('Автомнемо - ' + self.uploadedScreenshot)

                for index in range (1, len(file_rows)):
                    obj_str = file_rows[index].rstrip('\n').split('; ')
                    mn_obj = MnemoObj(obj_str) # создаём новый объект
                    mn_list_el = MnemoObjList()  # новый элемент списка
                    mn_list_el.key = mn_obj
                    self.mnemo_obj_list.insert(mn_list_el)  # вставляем объект в список
                    self.insertObjIntoTree(self, mn_obj = mn_obj)
                file.close()

            # прорисовываем рамки обнаруженных объектов
            cur_val = self.mnemo_obj_list.head
            while cur_val != None:
                color = self.obj_colors[cur_val.key.type] # получаем цвет рамки в зависимости от типа объекта
                # обводим объекты рамками:
                self.canvas_with_objects.create_rectangle(cur_val.key.x,
                                                          cur_val.key.y,
                                                          cur_val.key.x + cur_val.key.width,
                                                          cur_val.key.y + cur_val.key.height,
                                                          outline = color,
                                                          width = 3,
                                                          tag = 'rect_obj')
                cur_val = cur_val.next


gui = GUI
gui.__init__(GUI)
gui.buildWindow(GUI)
gui.window.mainloop()