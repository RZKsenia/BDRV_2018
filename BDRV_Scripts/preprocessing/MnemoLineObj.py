class MnemoLineObj:
    """
    Класс линии в мнемосхеме
    x1 - координата х начала линии
    у1 - координата у начала линии
    х2 - координата х конца линии
    у2 - координити у конца линии
    color_title - название цвета CSS3
    """
    def __init__(self, line_info, color_title):
        self.x1 = int(line_info[0])
        self.y1 = int(line_info[1])
        self.x2 = int(line_info[2])
        self.y2 = int(line_info[3])

        self.line_color = color_title
