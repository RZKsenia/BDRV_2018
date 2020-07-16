

class MnemoObjList(object):
    """
    Класс дважды связанного списка объектов мнемосхемы
    """
    def __init__(self):
        self.head = None
        self.key = None
        self.next = None
        self.prev = None

    def insert(self, new_value):
        """
        Вставка элемента в список
        """
        new_value.next = self.head
        if self.head != None:
            self.head.prev = new_value
        self.head = new_value
        self.key = new_value.key # ключом служит уникальное имя объекта
        new_value.prev = None

    def delete(self, deleted_value):
        """
        Удаление элемента из списка
        """
        if deleted_value.prev != None:
            deleted_value.prev.next = deleted_value.next
        else:
            self.head = deleted_value.next
        if deleted_value.next != None:
            deleted_value.next.prev = deleted_value.prev

    def search(self, key):
        """
        Поиск элемента списка по ключу
        """
        x = self.head
        while x != None and x.key != key:
            x = x.next
        return x

    def count_by_type(self, type):
        """
        Подсчёт кол-ва объектов определённого типа
        """
        cntr = 0
        x = self.head
        while x != None:
            if x.key.type == type:
                cntr += 1
            x = x.next
        return cntr

    def search_coord(self, x, y):
        """
        поиск объекта мнемосхемы по координатам
        """
        el = self.head
        while el != None:
            if  el.key.x <= x <= (el.key.x + el.key.width):
                if el.key.y <= y <= (el.key.y + el.key.height):
                    return el.key # возвращаем найденный объект
            el = el.next
        return None