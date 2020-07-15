


class MnemoObj(object):
    """
    Класс объекта мнемосхемы
    """
    def __init__(self, lst):
        """
        Экземпляр класса создаётся на базе списка.
        Элементы списка:
        0 - тип объекта. Строка
        1 - координата Х
        2 - координата Y
        3 - ширина объекта
        4 - высота объекта
        """
        self.obj_name = lst[0]
        self.type = lst[1]
        self.x = int(lst[2])
        self.y = int(lst[3])
        self.width = int(lst[4])
        self.height = int(lst[5])

