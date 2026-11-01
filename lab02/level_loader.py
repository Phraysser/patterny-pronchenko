import os

class LevelLoader:
    def load_level(self, file_path):
        level_data = {
            'tank_start': (50, 500),
            'obstacles': []
        }
        
        if not os.path.exists(file_path):
            self.create_default_level(file_path)
        
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                
                parts = line.split()
                
                if parts[0] == 'TANK':
                    level_data['tank_start'] = (int(parts[1]), int(parts[2]))
                elif parts[0] == 'OBSTACLE':
                    level_data['obstacles'].append({
                        'x': int(parts[1]),
                        'y': int(parts[2]),
                        'width': int(parts[3]),
                        'height': int(parts[4]),
                        'health': int(parts[5]),
                        'points': int(parts[6]),
                        'type': parts[7]
                    })
        
        return level_data
    
    def create_default_level(self, file_path):
        directory = os.path.dirname(file_path)
        if directory and not os.path.exists(directory):
            os.makedirs(directory)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write("# Уровень 1\n")
            f.write("TANK 50 500\n\n")
            f.write("# Кирпичные стены\n")
            f.write("OBSTACLE 200 100 60 60 3 10 brick\n")
            f.write("OBSTACLE 300 100 60 60 3 10 brick\n")
            f.write("OBSTACLE 400 100 60 60 3 10 brick\n\n")
            f.write("# Металлические блоки\n")
            f.write("OBSTACLE 200 250 60 60 5 20 metal\n")
            f.write("OBSTACLE 400 250 60 60 5 20 metal\n\n")
            f.write("# Деревянные ящики\n")
            f.write("OBSTACLE 150 400 40 40 2 5 wood\n")
            f.write("OBSTACLE 250 400 40 40 2 5 wood\n")
            f.write("OBSTACLE 350 400 40 40 2 5 wood\n")
            f.write("OBSTACLE 450 400 40 40 2 5 wood\n")