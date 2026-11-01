class ObstacleFlyweight:
    def __init__(self, obstacle_type, color, base_health, base_points):
        self._obstacle_type = obstacle_type
        self._color = color
        self._base_health = base_health
        self._base_points = base_points

    def get_type(self):
        return self._obstacle_type

    def get_color(self):
        return self._color

    def get_base_health(self):
        return self._base_health

    def get_base_points(self):
        return self._base_points

    def render_base(self, renderer, x, y, width, height, health_ratio):
        damage_color = (
            int(self._color[0] * health_ratio),
            int(self._color[1] * health_ratio),
            int(self._color[2] * health_ratio)
        )
        renderer.draw_rect(x, y, width, height, damage_color)
        renderer.draw_rect(x, y, width, height, (0, 0, 0), outline=True, outline_width=2)


class ObstacleFlyweightFactory:
    _flyweights = {}

    _type_configs = {
        'brick': ((139, 69, 19), 3, 10),
        'metal': ((128, 128, 128), 5, 20),
        'wood': ((139, 90, 43), 2, 5),
        'concrete': ((100, 100, 100), 8, 30),
    }

    @classmethod
    def get_flyweight(cls, obstacle_type):
        if obstacle_type not in cls._flyweights:
            if obstacle_type in cls._type_configs:
                color, base_health, base_points = cls._type_configs[obstacle_type]
            else:
                color, base_health, base_points = (139, 0, 0), 3, 10
            cls._flyweights[obstacle_type] = ObstacleFlyweight(
                obstacle_type, color, base_health, base_points
            )
        return cls._flyweights[obstacle_type]

    @classmethod
    def get_all_types(cls):
        return list(cls._type_configs.keys())

    @classmethod
    def get_count(cls):
        return len(cls._flyweights)

    @classmethod
    def reset(cls):
        cls._flyweights.clear()