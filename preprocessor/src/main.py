from argparse import ArgumentParser

from preprocessor import Meta, Raw, Terrain, Vision, Event

from utils import Common, DataLoader


def main():
    parser = ArgumentParser()
    parser.add_argument('--input', type=str)
    parser.add_argument('--output', type=str)
    args = parser.parse_args()

    loader = DataLoader(args)
    
    meta = Meta(loader)
    # raw = Raw(loader)
    terrain = Terrain(loader)
    vision = Vision(loader)
    event = Event(loader)


if __name__ == '__main__':
    main()
