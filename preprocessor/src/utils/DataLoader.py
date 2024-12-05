import os
import numpy as np
import glob


class DataLoader:
    def __init__(self, args):
        if args.input is None:
            self.raw = os.path.join(os.getcwd(), 'raw')
        if args.output is None:
            self.output_dir = os.path.join(os.getcwd(), 'results')

        if args.input is None:
            self.replays = glob.glob(os.path.join(self.raw, '*.rep'))
        else:
            pass

        self.data = {}
        for replay in self.replays:
            filename = os.path.basename(replay)
            if not os.path.exists(os.path.join(self.output_dir, filename)):
                os.makedirs(os.path.join(self.output_dir, filename))
            self.data[filename] = self.load_data(replay)

    def _open_file_with_fallback(self, file_path):
        """
        Tries to open a file without specifying encoding. 
        If it fails, retries with cp949 encoding.
        """
        try:
            with open(file_path, 'r') as f:
                return f.readlines()
        except UnicodeDecodeError:
            with open(file_path, 'r', encoding='cp949') as f:
                return f.readlines()

    def load_meta(self, path):
        meta = self._open_file_with_fallback(os.path.join(path, 'meta'))
        meta = dict(zip(meta[0].split(','), meta[1].split(',')))
        return meta

    def load_terrain(self, path):
        terrain = self._open_file_with_fallback(os.path.join(path, 'terrain'))
        terrain = np.array([line.strip() for line in terrain])
        return terrain

    def load_vision(self, path):
        vision = self._open_file_with_fallback(os.path.join(path, 'vision'))
        vision = np.array([line.strip() for line in vision])
        return vision

    def load_event(self, path):
        event = self._open_file_with_fallback(os.path.join(path, 'event'))
        event = np.array([line.strip() for line in event])
        return event

    def load_raw(self, path):
        raw = self._open_file_with_fallback(os.path.join(path, 'raw'))
        raw = np.array([line.strip() for line in raw])
        return raw

    def load_data(self, file_path):
        data = {}
        data['meta'] = self.load_meta(file_path)
        data['terrain'] = self.load_terrain(file_path)
        data['vision'] = self.load_vision(file_path)
        data['event'] = self.load_event(file_path)
        data['raw'] = self.load_raw(file_path)
        return data

    def load_data_mp(self):
        # Logic for loading data with multiprocessing can be implemented here
        # For now, returning data without multiprocessing
        return self.load_data()
