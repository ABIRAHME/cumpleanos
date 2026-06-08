import os, collections
from PIL import Image, ImageFilter

def remove_background(img_path, out_path, tolerance=38):
    print(f"  {os.path.basename(img_path)} -> {os.path.basename(out_path)} ... ", end="")
    try:
        img = Image.open(img_path).convert('RGBA')
    except Exception as e:
        print(f"ERROR: {e}"); return

    w, h = img.size
    px = img.load()
    corners = [(0,0),(w-1,0),(0,h-1),(w-1,h-1)]
    corner_colors = [px[p] for p in corners]

    visited = set()
    mask = Image.new('L', (w, h), 255)
    mp = mask.load()

    def close(c1, c2):
        return ((c1[0]-c2[0])**2 + (c1[1]-c2[1])**2 + (c1[2]-c2[2])**2) ** 0.5 < tolerance

    q = collections.deque()
    for p in corners:
        if p not in visited:
            visited.add(p); q.append(p)

    while q:
        x, y = q.popleft()
        mp[x, y] = 0
        for dx, dy in ((-1,0),(1,0),(0,-1),(0,1)):
            nx, ny = x+dx, y+dy
            if 0 <= nx < w and 0 <= ny < h and (nx,ny) not in visited:
                nc = px[nx, ny]
                is_bg = any(close(nc, cc) for cc in corner_colors)
                # Also catch very light pixels near white
                if not is_bg:
                    is_light_corner = any(c[0]>215 and c[1]>215 and c[2]>215 for c in corner_colors)
                    if is_light_corner and nc[0]>225 and nc[1]>225 and nc[2]>225:
                        is_bg = True
                if is_bg:
                    visited.add((nx,ny)); q.append((nx,ny))

    mask = mask.filter(ImageFilter.GaussianBlur(1.3))
    img.putalpha(mask)
    img.save(out_path, 'PNG')
    print("OK")

def main():
    d = 'assests'
    # Skip the profile photo and any existing PNGs
    skip = {'mahmuda_nazmin_image.jpeg', '.DS_Store'}

    # Collect all jpegs that need processing
    jpegs = sorted([f for f in os.listdir(d)
                     if (f.endswith('.jpeg') or f.endswith('.jpg')) and f not in skip])

    print(f"Found {len(jpegs)} images to process:\n")

    for idx, fname in enumerate(jpegs, 1):
        src = os.path.join(d, fname)
        out = os.path.join(d, f'flower_{idx}.png')
        # Special tolerance for gray-background image
        tol = 38
        if '(33)' in fname:
            tol = 25  # gray bg needs tighter tolerance
        remove_background(src, out, tolerance=tol)

    print(f"\nDone! Processed {len(jpegs)} images -> flower_1.png to flower_{len(jpegs)}.png")

if __name__ == '__main__':
    main()
