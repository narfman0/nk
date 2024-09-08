import time
import numpy as np

from nk_shared.settings import PROJECT_ROOT


def generate_tiled_csv(tilemap: np.ndarray) -> str:
    width, height = tilemap.shape
    lines = []
    for x in range(width):
        lines.append(",".join([str(int(tilemap[x, y])) for y in range(height)]))
    return ",\n".join(lines)


def generate_tiled_tmx(tilemap: np.ndarray):
    width, height = tilemap.shape
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<map version="1.10" tiledversion="1.10.2" orientation="isometric" renderorder="right-down" width="{width}" height="{height}" tilewidth="32" tileheight="16" infinite="0" nextlayerid="10" nextobjectid="1">
 <properties>
  <property name="GroundLayerNames" value="ground"/>
  <property name="StartXY" value="{width//2},{height//2}"/>
 </properties>
 <tileset firstgid="0" source="../tsx/jumpstart.tsx"/>
 <layer id="1" name="ground" width="{width}" height="{height}" offsetx="0" offsety="8">
  <data encoding="csv">
{generate_tiled_csv(tilemap)}
</data>
 </layer>
</map>"""


def write_tmx_file(tilemap: np.array):
    start = time.time()
    with open(f"{PROJECT_ROOT}/data/tiled/tmx/mapgen.tmx", "w", encoding="utf-8") as f:
        f.write(generate_tiled_tmx(tilemap))
    end = time.time()
    print(f"Write TMX: {end - start:.2f}s")
