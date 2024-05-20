from math import comb
from numpy.linalg import norm
from numpy import array

class Bezier:
    """
    Klasa reprezentująca krzywą Beziera

    Attributes:
        control_points (list[list[float]]): lista punktów kontrolnych krzywej
    """
    def __init__(self, control_points: list[list[float]]):
        """
        Konstruktor klasy Bezier

        Args:
            control_points (list[list[float]]): lista punktów kontrolnych krzywej
        """
        self.control_points = array(control_points)

    def bernstein(self, n: int, i: int, t: float) -> float:
        """
        Zwraca wartość wielomianu Bernsteina

        Args:
            n (int): stopień wielomianu
            i (int): indeks
            t (float): wartość parametru t

        Returns:
            float: wartość wielomianu Bernsteina
        """
        return comb(n, i) * (1 - t)**(n - i) * t**i
    
    def point(self, t: float) -> list[float]:
        """
        Oblicza punkt na krzywej dla parametru t

        Args:
            t (float): wartość parametru t
        
        Returns:
            list[float]: punkt na krzywej dla parametru t
        """
        n = len(self.control_points) - 1
        x = 0
        y = 0
        for i in range(n + 1):
            x += self.bernstein(n, i, t) * self.control_points[i][0]
            y += self.bernstein(n, i, t) * self.control_points[i][1]
        return [x, y]
    
    def derivative(self, t: float) -> list[float]:
        """
        Zwraca pochodną krzywej Beziera dla parametru t

        Args:
            t (float): wartość parametru t

        Returns:
            list[float]: pochodna krzywej Beziera dla parametru t
        """
        n = len(self.control_points) - 1
        x = 0
        y = 0
        for i in range(n):
            x += n * (self.control_points[i + 1][0] - self.control_points[i][0]) * self.bernstein(n - 1, i, t)
            y += n * (self.control_points[i + 1][1] - self.control_points[i][1]) * self.bernstein(n - 1, i, t)
        return [x, y]
    
    def normal(self, t: float, is_flipped: bool=False) -> list[float]:
        """
        Zwraca wektor normalny do krzywej Beziera dla parametru t

        Args:
            t (float): wartość parametru t
            is_flipped (bool): czy wektor ma być odwrócony

        Returns:
            list[float]: wektor normalny do krzywej Beziera dla parametru t
        """
        d = self.derivative(t)
        d = d/norm(d)
        if is_flipped:
            return [d[1], -d[0]]
        else:   
            return [-d[1], d[0]]
        
    def tangent(self, t: float) -> list[float]:
        """
        Zwraca wektor stycznny do krzywej Beziera dla parametru t

        Args:
            t (float): wartość parametru t

        Returns:
            list[float]: wektor stycznny do krzywej Beziera dla parametru t
        """
        d = self.derivative(t)
        d = array(d)
        return d/norm(d)
    
    def quadratic_crit_point(self) -> list[list[float]]:
        """
        Zwraca punkty krytyczne krzywej Beziera drugiego stopnia

        Returns:
            list[list[float]]: lista punktów krytycznych krzywej Beziera drugiego stopnia
        """
        nominator = self.control_points[0] - self.control_points[1]
        denominator = self.control_points[0] - 2 * self.control_points[1] + self.control_points[2]
        t_val = nominator/denominator
        
        crit_points = []
        if t_val[0] >= 0 and t_val[0] <= 1:
            crit_points.append(self.point(t_val[0]))
        if t_val[1] >= 0 and t_val[1] <= 1:
            crit_points.append(self.point(t_val[1]))
        return crit_points
    
    def quadratic_bounding_box(self) -> list[list[float]]:
        """
        Zwraca bounding box krzywej Beziera drugiego stopnia

        Returns:
            list[list[float]]: bounding box krzywej Beziera drugiego stopnia
        """
        crit_points = self.quadratic_crit_point()
        x = [self.control_points[0][0], self.control_points[2][0]]
        y = [self.control_points[0][1], self.control_points[2][1]]
        for p in crit_points:
            x.append(p[0])
            y.append(p[1])

        return [[min(x), min(y)], [max(x), max(y)]]

    def is_in_bounding_box(self, point: list[float]) -> bool:
        """
        Sprawdza czy punkt znajduje się w bounding boxie krzywej

        Args:
            point (list[float]): punkt do sprawdzenia

        Returns:
            bool: czy punkt znajduje się w bounding boxie krzywej
        """
        bb = self.quadratic_bounding_box()
        return point[0] >= bb[0][0] and point[0] <= bb[1][0] and point[1] >= bb[0][1] and point[1] <= bb[1][1]

    def closest_point(self, point: list[float]) -> list[float]:
        """
        Zwraca najbliższy punkt na krzywej do danego punktu

        Args:
            point (list[float]): punkt do porównania

        Returns:
            list[float]: najbliższy punkt na krzywej do danego punktu
        """
        step = 0.01
        t = 0
        min_distance = norm(array(self.point(0)) - array(point))
        min_t = 0
        while t <= 1:
            distance = norm(array(self.point(t)) - array(point))
            if distance < min_distance:
                min_distance = distance
                min_t = t
            t += step
        return self.point(min_t)