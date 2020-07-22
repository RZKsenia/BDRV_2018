

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

    def search_by_obj_name(self, obj_name):
        """
        Поиск элемента списка по ключу
        """
        mn_obj_lst = self.head
        while mn_obj_lst != None:
            if mn_obj_lst.key.obj_name == obj_name:
                return mn_obj_lst.key
            else:
                mn_obj_lst = mn_obj_lst.next
        return None

    def search_by_object(self, mn_obj):
        """
        Поиск по объекту мнемосхемы.
        mn_obj - объект типа MnemoObject
        """
        list_el = self.head
        while list_el != None and list_el.key != mn_obj:
            list_el = list_el.next
        return list_el

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