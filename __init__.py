def __init__():
    from pathlib import Path
    import sys


    p = Path(__file__).parent.parent
    if str(p) not in sys.path:
        sys.path.append(str(p))
    # print(sys.path)

__init__()

