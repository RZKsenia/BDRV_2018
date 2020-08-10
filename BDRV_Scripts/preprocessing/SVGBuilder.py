from lxml import etree
import io
from BDRV_Scripts.preprocessing.MnemoObj import MnemoObj
from BDRV_Scripts.preprocessing.MnemoObjList import MnemoObjList

class SVGBuilder(object):
    """
    Класс для построения файла в формате SVG на основе
    обработанного скришота мнемосхемы
    """
    def __init__(self, width, height, mnemo_obj_list, mnlines_obj_list):
        self.width = width
        self.height = height
        self.mnobj_list = mnemo_obj_list # список объектов мнемосхемы
        self.mnlines_list = mnlines_obj_list # список линий мнемосхемы

        self.root = etree.Element("svg",
                                  version = "1.1",
                                  baseProfile = "full",
                                  width=str(self.width),
                                  height=str(self.height),
                                  viewBox = "0 0 " + str(self.width) + ' '+ str(self.height),
                                  xmlns="http://www.w3.org/2000/svg"
                                  )
        # заголовок файла
        self.title_of_svg = etree.SubElement(self.root, "title")
        self.title_of_svg.text = "This is the first mnemoscheme"

        # детальное описание файла
        self.desc_svg = etree.SubElement(self.root, "desc")
        self.desc_svg.text = "This is a description of the first Mnemoscheme"

        # Эта часть содержит описания (например, градиенты и прочее):
        self.defs = etree.SubElement(self.root, "desc")

    def group(self, root, id):
        """
        Создать групповой тег. Одна группа может входить в другую
        """
        g = etree.SubElement(root, "g", id=id)
        return g

    def rectangle(self, parent=None, x=0, y=0, width=0, height=0, fill_color="", stroke_width="1",
                  stroke_color=()):
        """
        Создать прямоугольник
        """
        style = "fill:"+ fill_color +";stroke-width:"+ str(stroke_width) + ";stroke:" + stroke_color
        rect = etree.SubElement(parent, "rect",
                                x= str(x),
                                y= str(y),
                                width=str(width),
                                height=str(height),
                                style=style)

    def add_indicator(self, parent, mn_obj):
        """
        создать индикатор
        """
        group_id = "g" + str(mn_obj.obj_name)
        indicator = self.group(parent, group_id)

        self.rectangle(parent=indicator,
                       x=mn_obj.x+3,
                       y=mn_obj.y+12,
                       width=43,
                       height=10,
                       fill_color="black",
                       stroke_width='1',
                       stroke_color="black"
                       )
        indicator_text = etree.SubElement(indicator,
                                          "text",
                                          x= str(mn_obj.x+3),
                                          y= str(mn_obj.y+8),
                                          style="fill:black;font-size:xx-small;")

        indicator_text_tag = etree.SubElement(indicator,
                                          "text",
                                          x=str(mn_obj.x + 5),
                                          y=str(mn_obj.y + 20),
                                          style="fill:lime;font-size:xx-small;")
        indicator_text.text = mn_obj.obj_title
        indicator_text_tag.text = "0.0"

    def add_valve(self, parent, mn_obj):
        """
        Арматура запорная
        """
        group_id = "g" + str(mn_obj.obj_name)
        valve = self.group(parent, group_id)

        x = mn_obj.x
        y = mn_obj.y

        ax = x
        ay = y + 10
        bx = x
        by = y + 20
        cx = x + 10
        cy = y + 15
        dx = x + 20
        dy = y + 10
        ex = x + 20
        ey = y + 20

        points = str(ax)+','+str(ay)+' '
        points += str(bx)+','+str(by)+' '
        points += str(cx)+','+str(cy)

        etree.SubElement(valve, "polygon",
                         x=str(x),
                         y=str(y),
                         points= points,
                         style="fill:gold;stroke:black;stroke-width:1")

        points = str(cx) + ',' + str(cy) + ' '
        points += str(dx) + ',' + str(dy) + ' '
        points += str(ex) + ',' + str(ey)

        etree.SubElement(valve, "polygon",
                         x=str(x),
                         y=str(y),
                         points=points,
                         style="fill:gold;stroke:black;stroke-width:1")

        etree.SubElement(valve, "line",
                         x1=str(cx),
                         y1=str(cy),
                         x2=str(cx),
                         y2=str(cy-5),
                         style="stroke:black;stroke-width:1")

        ax = x + 5
        ay = y
        bx = x + 5
        by = y + 10
        cx = x + 15
        cy = y
        dx = x + 15
        dy = y + 10

        path_points = 'M'+str(bx) + ' ' + str(by) + ' '
        path_points += 'C'+str(ax) + ' ' + str(ay) + ' ' + str(cx) + ' ' + str(cy) + ' '
        path_points += str(dx) + ' ' + str(dy) + 'Z'

        etree.SubElement(valve, "path",
                         x=str(x),
                         y=str(y),
                         d= path_points,
                         style="fill:gold;stroke:black;stroke-width:1")

    def add_heat_exchanger(self, parent, mn_obj):
        """
        теплообменник
        """
        group_id = "g" + str(mn_obj.obj_name)
        heat_exhanger = self.group(parent, group_id)

        etree.SubElement(heat_exhanger, "rect",
                         x=str(mn_obj.x),
                         y=str(mn_obj.y),
                         rx = str(15),
                         ry = str(15),
                         width=str(mn_obj.width),
                         height=str(mn_obj.height),
                         style="fill:gainsboro;stroke:black;stoke-width:1")

        he_title = etree.SubElement(heat_exhanger,
                         "text",
                         x=str(mn_obj.x + 3),
                         y=str(mn_obj.y + mn_obj.height/2),
                         style="fill:black;font-size:xx-small;")
        he_title.text = mn_obj.obj_title

    def add_pump(self, parent, mn_obj):
        """
        добавить насос
        """
        group_id = "g" + str(mn_obj.obj_name)
        pump = self.group(parent, group_id)

        ax = mn_obj.x
        ay = mn_obj.y + mn_obj.height
        bx = mn_obj.x + mn_obj.width/2
        by = mn_obj.y + mn_obj.height/2
        cx = mn_obj.x + mn_obj.width
        cy = mn_obj.y + mn_obj.height

        points = str(ax) + ',' + str(ay) + ' '
        points += str(bx) + ',' + str(by) + ' '
        points += str(cx) + ',' + str(cy)

        etree.SubElement(pump, "polygon",
                         x=str(mn_obj.x),
                         y=str(mn_obj.y),
                         points=points,
                         style="fill:chartreuse;stroke:black;stroke-width:1")

        etree.SubElement(pump, "circle",
                         cx=str(mn_obj.x + mn_obj.width/2),
                         cy=str(mn_obj.y + mn_obj.height/2-10),
                         r=str(mn_obj.width/2-2),
                         style="fill:chartreuse;stroke:black;stoke-width:1")

        pump_title = etree.SubElement(pump,
                                    "text",
                                    x=str(mn_obj.x + 10),
                                    y=str(mn_obj.y + mn_obj.height / 2-5),
                                    style="fill:black;font-size:xx-small;")
        pump_title.text = mn_obj.obj_title

    def add_line(self, parent, mn_line_obj):
        """
        добавить линию
        """
        etree.SubElement(parent, "line",
                         x1 = str(mn_line_obj.x1),
                         y1 = str(mn_line_obj.y1),
                         x2 = str(mn_line_obj.x2),
                         y2 = str(mn_line_obj.y2),
                         style="stroke:" + mn_line_obj.line_color + ";stroke-width:2")

    def build_svg(self):
        """
        создание файла SVG на базе обнаруженных объектов мнемосхемы
        """
        # группируем все линии вместе:
        group_id = "g" + str('mnemoscheme-lines')
        lines_group = self.group(self.root, group_id)
        cur_line_obj = self.mnlines_list.head
        # Рисуем соединительные линии мнемосхемы:
        while cur_line_obj is not None:
            self.add_line(lines_group, cur_line_obj.key)
            cur_line_obj = cur_line_obj.next


        cur_obj = self.mnobj_list.head
        # Рисуем объекты мнемосхемы
        while cur_obj is not None:
            type = cur_obj.key.type # получаем тип объекта

            if type == 'indicator':
                self.add_indicator(self.root,
                                   cur_obj.key
                                   )
            if type == 'valve':
                self.add_valve(self.root,
                               cur_obj.key)

            if type == 'heat-exchanger':
                self.add_heat_exchanger(self.root,
                                        cur_obj.key)

            if type == 'pump':
                self.add_pump(self.root,
                              cur_obj.key)
            cur_obj = cur_obj.next

    def write_file(self):
        """
        записать всё дерево тегов в файл SVG
        """
        with io.open(r'C:/Python_projects/test.svg', mode = 'wb') as file:
            file.write(etree.tostring(self.root, pretty_print=True))
            file.close()
