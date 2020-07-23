

class MnemoObjList(object):
    """
    Класс дважды связанного списка объектов мнемосхемы
    """
    def __init__(self):
        self.clear()

    def insert(self, new_value):
        """
        Вставка элемента в список
        """
        new_value.next = self.head
        if self.head != None:
            self.head.prev = new_value
        self.head = new_value
        self.key = new_value.key # ключом служит объект мнемосхемы
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

    def clear(self):
        """
        удалчение всех элементов списка
        """
        self.head = None
        self.key = None
        self.next = None
        self.prev = None

    def __len__(self):
        """
        Количество элементов в списке
        """
        cntr = 0
        cur_el = self.head
        while cur_el != None:
            cntr +=1
            cur_el = cur_el.next
        return cntr

    def search(self, mn_obj=None, obj_name='', obj_title='', x=-1, y=-1):
        """
        Поиск элемента списка по одному из параметров:
        mn_obj - объект мнемосхемы
        obj_name - имя объекта
        obj_title - обозначение объекта
        х, у - координаты объекта
        """
        if mn_obj is not None:
            list_el = self.head
            while list_el != None and list_el.key != mn_obj:
                list_el = list_el.next
            return list_el

        if obj_name != '':
            mn_obj_lst = self.head
            while mn_obj_lst != None:
                if obj_name != '':
                    if mn_obj_lst.key.obj_name == obj_name:
                        return mn_obj_lst.key
                mn_obj_lst = mn_obj_lst.next

        if obj_title != '':
            mn_obj_lst = self.head
            while mn_obj_lst != None:
                if obj_title != '':
                    if mn_obj_lst.key.obj_title == obj_title:
                        return mn_obj_lst.key
                mn_obj_lst = mn_obj_lst.next

        if (x != -1) and (y != -1):
            el = self.head
            while el != None:
                if el.key.x <= x <= (el.key.x + el.key.width):
                    if el.key.y <= y <= (el.key.y + el.key.height):
                        return el.key  # возвращаем найденный объект
                el = el.next

        return None

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