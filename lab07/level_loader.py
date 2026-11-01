import os


class LevelLoader:
    def load_level(self, file_path):
        level_data = {
            'tank_start': (50, 500),
            'obstacles': [],
            'groups': []
        }

        if not os.path.exists(file_path):
            self.create_default_level(file_path)

        with open(file_path, 'r', encoding='utf-8') as f:
            current_group = None
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue

                parts = line.split()

                if parts[0] == 'TANK':
                    level_data['tank_start'] = (int(parts[1]), int(parts[2]))
                    current_group = None
                elif parts[0] == 'GROUP':
                    group_name = parts[1] if len(parts) > 1 else "Group"
                    current_group = {
                        'name': group_name,
                        'obstacles': []
                    }
                    level_data['groups'].append(current_group)
                elif parts[0] == 'OBSTACLE':
                    obstacle = {
                        'x': int(parts[1]),
                        'y': int(parts[2]),
                        'width': int(parts[3]),
                        'height': int(parts[4]),
                        'health': int(parts[5]),
                        'points': int(parts[6]),
                        'type': parts[7]
                    }
                    level_data['obstacles'].append(obstacle)
                    if current_group is not None:
                        current_group['obstacles'].append(obstacle)

        return level_data

    def create_default_level(self, file_path):
        directory = os.path.dirname(file_path)
        if directory and not os.path.exists(directory):
            os.makedirs(directory)

        with open(file_path, 'w', encoding='utf-8') as f:
            f.write("# Уровень 1\n")
            f.write("TANK 50 500\n\n")
            f.write("# Группа: Кирпичная стена\n")
            f.write("GROUP BrickWall\n")
            f.write("OBSTACLE 200 100 60 60 3 10 brick\n")
            f.write("OBSTACLE 260 100 60 60 3 10 brick\n")
            f.write("OBSTACLE 320 100 60 60 3 10 brick\n\n")
            f.write("# Группа: Металлические блоки\n")
            f.write("GROUP MetalBlocks\n")
            f.write("OBSTACLE 200 250 60 60 5 20 metal\n")
            f.write("OBSTACLE 400 250 60 60 5 20 metal\n\n")
            f.write("# Группа: Деревянные ящики\n")
            f.write("GROUP WoodenBoxes\n")
            f.write("OBSTACLE 150 400 40 40 2 5 wood\n")
            f.write("OBSTACLE 190 400 40 40 2 5 wood\n")
            f.write("OBSTACLE 230 400 40 40 2 5 wood\n")
            f.write("OBSTACLE 270 400 40 40 2 5 wood\n")