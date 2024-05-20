from line import Line
from numpy import array, cross
from bezier_tools import Bezier
from numpy.linalg import norm

class Glyph:
    """
    Klasa reprezentująca pojedynczy glif (znak)

    Attributes:
        unicode (str): Unicode znaku
        svg_path (str): Ścieżka SVG znaku
        horiz_adv_x (float): Szerokość znaku
        lines (list[Line]): Lista linii tworzących znak
    """
    def __init__(self, unicode: str, svg_path: str, horiz_adv_x: float = None):
        """
        Konstruktor klasy Glyph

        Args:
            unicode (str): Unicode znaku
            svg_path (str): Ścieżka SVG znaku
            horiz_adv_x (float): Szerokość znaku
        """
        self.unicode = unicode
        self.svg_path = svg_path
        self.horiz_adv_x = horiz_adv_x
        self.lines: list[Line] = []
        self.__parse_svg_path()
        self.__process_lines()
        self.scale(1, -1)

    def __parse_svg_path(self):
        """
        Metoda parsująca ścieżkę SVG znaku na linie
        """
        last_num = 0
        floating_point = 0
        is_last_num = False
        is_negative = False
        for c in self.svg_path:
            if c.isalpha():
                if is_last_num:
                    if is_negative:
                        last_num *= -1
                    current_line = self.lines.pop()
                    current_line.points.append(last_num)
                    self.lines.append(current_line)
                    last_num = 0
                    floating_point = 0
                    is_last_num = False
                    is_negative = False
                self.lines.append(Line(c))
            elif c.isnumeric():
                if floating_point == 0:
                    last_num *= 10
                last_num += 0.1**floating_point * int(c)
                if floating_point > 0:
                    floating_point += 1
                is_last_num = True
            elif c == "-":
                is_negative = True
            elif c == ".":
                floating_point += 1
            else:
                if is_last_num:
                    if is_negative:
                        last_num *= -1
                    current_line = self.lines.pop()
                    current_line.points.append(last_num)
                    self.lines.append(current_line)
                    last_num = 0
                    floating_point = 0
                    is_last_num = False
                    is_negative = False


    def __process_lines(self):
        """
        Metoda przetwarzająca linie znaku
        """
        last_x = None
        last_y = None
        last_ctrl_x = None
        last_ctrl_y = None
        last_M_x = None
        last_M_y = None
        for line in self.lines:
            line.set_last_M_point(last_M_x, last_M_y)
            line.set_last_point(last_x, last_y)
            line.set_last_control_point(last_ctrl_x, last_ctrl_y)
            line.process_line(True)
            if line.ltype == 'M':
                last_M_x = line.points[0]
                last_M_y = line.points[1]
            if len(line.points) >= 2:
                last_x = line.points[len(line.points) - 2]
                last_y = line.points[len(line.points) - 1]
                if len(line.points) >= 4:
                    last_ctrl_x = line.points[0]
                    last_ctrl_y = line.points[1]
                else:
                    last_ctrl_x = None
                    last_ctrl_y = None
            else:
                last_x = None
                last_y = None
                
    def svg_code(self) -> str:
        """
        Generuje kod SVG znaku

        Returns:
            str: Kod SVG znaku
        """
        output = ""
        for line in self.lines:
            output += line.svg_line() + ' '
        return output

    def transform(self, x: float, y: float):
        """
        Przesuwa znak o podane wartości

        Args:
            x (float): Wartość przesunięcia w osi X
            y (float): Wartość przesunięcia w osi Y
        """
        for line in self.lines:
            line.transform(x, y)

    def scale(self, x: float, y: float):
        """
        Skaluje znak o podane wartości

        Args:
            x (float): Wartość skalowania w osi X
            y (float): Wartość skalowania w osi Y
        """
        for line in self.lines:
            line.scale(x, y)
    
    def print_glyph(self):
        """
        Wypisuje wszystkie linie tworzące znak
        """
        print("[" + self.unicode + "]")
        for line in self.lines:
            print("\t", end="")
            line.print_line()
        print(self.svg_code())
        print()

    def glyph_bbox(self) -> list[float]:
        """
        Zwraca bounding box znaku

        Returns:
            list[float]: Bounding box znaku [x0, y0, x1, y1]
        """
        x0 = self.lines[0].points[0]
        x1 = self.lines[0].points[0]
        y0 = self.lines[0].points[1]
        y1 = self.lines[0].points[1]
        for line in self.lines:
            for i in range(0, len(line.points), 2):
                x = line.points[i]
                y = line.points[i + 1]
                if x < x0:
                    x0 = x
                if x > x1:
                    x1 = x
                if y < y0:
                    y0 = y
                if y > y1:
                    y1 = y
        return [0, y0, self.horiz_adv_x, y1]


    def print_glyph_point_notation(self, accuracy: float = 0.1):
        """
        Zwraca znak w postaci punktowej

        Args:
            accuracy (float): Dokładność przybliżenia krzywych Beziera
        
        Returns:
            str: Znak w postaci punktowej
        """
        glyph_str = ''
        glyph_str += ">" + self.unicode + '\n'
        for line in self.lines:
            glyph_str += line.print_line_point_notation(accuracy)
        return glyph_str
     
    def closest_line(self, point: list[float]) -> Line:
        """
        Zwraca najbliższą linię do podanego punktu

        Args:
            point (list[float]): Punkt [x, y]
        Returns:
            Line: Najbliższa linia
        """
        closest_line = self.lines[0]
        closest_distance = closest_line.distance_to_line(point)
        for line in self.lines:
            distance = line.distance_to_line(point)
            if distance < closest_distance:
                closest_distance = distance
                closest_line = line
           
        return closest_line
    
    def last_line(self, line: Line) -> Line:
        """
        Zwraca poprzednią linię do podanej linii

        Args:
            line (Line): Linia

        Returns:
            Line: Poprzednia linia
        """
        index = self.lines.index(line)
        if(line.ltype == 'M'):
            for i in range(index, len(self.lines)):
                if(self.lines[i].ltype == 'Z'):
                    return self.lines[i]
        last_l = self.lines[index - 1]
        if last_l.ltype == 'M':
            return self.last_line(last_l)
        return last_l
    
    def sharp_corners(self) -> list[list[float]]:
        """
        Zwraca punkty ostrych narożników

        Returns:
            list[list[float]]: Lista punktów ostrych narożników
        """
        sharp_corners = []
        for i, line in enumerate(self.lines):
            last_line = self.last_line(line)
            if(line.ltype == 'Z'):
                z_line = array([line.last_M_point[0] - line.last_point[0], line.last_M_point[1] - line.last_point[1]])
                if(norm(z_line) == 0):
                    continue
            if(last_line.ltype == 'Z'):
                z_line = array([last_line.last_M_point[0] - last_line.last_point[0], last_line.last_M_point[1] - last_line.last_point[1]])
                if(norm(z_line) == 0):
                    last_line = self.last_line(last_line)
                    
            first_tangent = None
            second_tangent = None

            if line.ltype == 'M':
                continue
            elif line.ltype == 'Z':
                first_tangent = array([line.last_M_point[0] - line.last_point[0], line.last_M_point[1] - line.last_point[1]])
                if(norm(first_tangent) != 0):
                    first_tangent /= norm(first_tangent)
            elif line.ltype == 'L':
                first_tangent = array([line.points[0] - line.last_point[0], line.points[1] - line.last_point[1]])
                if(norm(first_tangent) != 0):
                    first_tangent /= norm(first_tangent)
            else:
                if len(line.points) < 4:
                    print("Error: Quadratic bezier with less than 4 points in first tangent calculation")
                    print(line.ltype)
                bezier = Bezier([line.last_point, line.points[0:2], line.points[2:4]])
                first_tangent = bezier.tangent(0)
            if last_line.ltype == 'L':
                second_tangent = array([last_line.last_point[0] - last_line.points[0] , last_line.last_point[1] - last_line.points[1]])
                if(norm(second_tangent) != 0):
                    second_tangent /= norm(second_tangent)
            elif last_line.ltype == 'Z':
                second_tangent = array([last_line.last_point[0] - last_line.last_M_point[0], last_line.last_point[1] - last_line.last_M_point[1]])
                if(norm(second_tangent) != 0): 
                    second_tangent /= norm(second_tangent)
            else:
                if len(last_line.points) < 4:
                    print("Error: Quadratic last bezier with less than 4 points in second tangent calculation")
                    print(last_line.ltype)
                bezier = Bezier([last_line.last_point, last_line.points[0:2], last_line.points[2:4]])
                second_tangent = bezier.tangent(1)
                second_tangent *= -1

            first_tangent = array([first_tangent[0], first_tangent[1], 0])
            second_tangent = array([second_tangent[0], second_tangent[1], 0])

            cross_p = cross(first_tangent, second_tangent)
            angle = cross_p[2]
            if(angle > 0.1):
                sharp_corners.append(line.last_point)
            
        return sharp_corners
    
    def scale_and_move_to_bbox(self, x0: float, y0: float, x1: float, y1: float, original_glyph) -> float:
        """
        Skaluje i przesuwa znak do podanego bounding box

        Args:
            x0 (float): Współrzędna x0 bounding box
            y0 (float): Współrzędna y0 bounding box
            x1 (float): Współrzędna x1 bounding box
            y1 (float): Współrzędna y1 bounding box
            original_glyph (Glyph): Oryginalny znak
        
        Returns:
            float: Współczynnik skalowania w osi X
        """
        current_bbox = original_glyph.glyph_bbox()
        current_width = original_glyph.horiz_adv_x
        current_height = current_bbox[3] - current_bbox[1]
        width = x1 - x0
        height = y1 - y0
        scale_factor_w = width / current_width
        self.scale(scale_factor_w, scale_factor_w)
        transform_x = x0
        transform_y = y0 # - current_bbox[1]
        self.transform(transform_x, -transform_y)
        return scale_factor_w
