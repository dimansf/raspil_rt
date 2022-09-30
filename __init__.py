def __init__():
    from pathlib import Path
    import sys


    p = Path(__file__).parent.parent
    sys.path.append(str(p))
    print(f'dirname - {p}')
    print(str(sys.path))


__init__()