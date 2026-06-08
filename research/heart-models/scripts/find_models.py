import asyncio
from sdk.tools.utils_tools import web_search
async def main():
    qs=[
      "Sketchfab anatomically accurate human heart 3D model downloadable CC Attribution license free download",
      "Sketchfab heart anatomy model CC0 or CC BY downloadable free realistic",
      "NIH 3D print exchange human heart anatomically accurate model CC0 download glb stl",
      "free anatomically correct human heart 3D model CC BY commercial use download glTF",
      "Z-Anatomy heart model export GLB CC BY-SA download github",
    ]
    for q in qs:
        r=await web_search(q); print("\n"+"="*70); print(q); print(r.search_response[:1800])
asyncio.run(main())
