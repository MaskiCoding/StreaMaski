from PIL import Image
import os

# Check if icon exists
if os.path.exists('ghost_play_icon.ico'):
    print("✓ Icon file exists")
    
    # Open and check the icon
    with Image.open('ghost_play_icon.ico') as img:
        print(f"✓ Icon format: {img.format}")
        print(f"✓ Current size: {img.size}")
        
        # Check all available sizes in the ICO file
        img.load()
        sizes = []
        try:
            while True:
                sizes.append(img.size)
                img.seek(img.tell() + 1)
        except EOFError:
            pass
        
        print(f"✓ Total sizes in ICO: {len(sizes)}")
        print(f"✓ Available sizes: {sizes}")
else:
    print("✗ Icon file not found")
