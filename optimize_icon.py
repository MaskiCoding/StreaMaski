"""
Optimize the existing icon for better quality display
"""

from PIL import Image
import os

def optimize_icon():
    """Optimize the existing icon for better quality"""
    
    try:
        # Open the existing icon
        img = Image.open('ghost_play_icon.ico')
        
        # Create a new optimized icon with high-quality sizes
        # These are the standard Windows icon sizes for best quality
        sizes = [
            (16, 16),   # Small icons, taskbar (small)
            (20, 20),   # Small icons (125% DPI)
            (24, 24),   # Small icons (150% DPI)
            (32, 32),   # Medium icons, taskbar (normal)
            (40, 40),   # Medium icons (125% DPI)
            (48, 48),   # Large icons
            (64, 64),   # Extra large icons
            (96, 96),   # Large icons (150% DPI)
            (128, 128), # Extra large icons (125% DPI)
            (256, 256)  # Jumbo icons
        ]
        
        # Start with the largest available size from the original
        base_img = img
        if hasattr(img, 'size'):
            # Try to get the largest size if it's a multi-resolution icon
            try:
                img.seek(0)  # Go to first frame
                largest_size = 0
                best_frame = 0
                
                for i in range(10):  # Check up to 10 frames
                    try:
                        img.seek(i)
                        current_size = img.size[0] * img.size[1]
                        if current_size > largest_size:
                            largest_size = current_size
                            best_frame = i
                    except EOFError:
                        break
                
                img.seek(best_frame)
                base_img = img.copy()
                print(f"Using base image size: {base_img.size}")
            except:
                base_img = img
        
        # Create high-quality resized versions
        images = []
        for size in sizes:
            # Use LANCZOS for high-quality downsampling
            resized = base_img.resize(size, Image.Resampling.LANCZOS)
            
            # Convert to RGBA if not already
            if resized.mode != 'RGBA':
                resized = resized.convert('RGBA')
            
            images.append(resized)
        
        # Save the optimized icon
        backup_name = 'ghost_play_icon_backup.ico'
        if not os.path.exists(backup_name):
            # Create backup of original
            with open('ghost_play_icon.ico', 'rb') as src, open(backup_name, 'wb') as dst:
                dst.write(src.read())
            print(f"Original icon backed up to {backup_name}")
        
        # Save the new optimized icon
        images[0].save(
            'ghost_play_icon_optimized.ico',
            format='ICO',
            sizes=[(img.size[0], img.size[1]) for img in images]
        )
        
        print("Optimized icon created: ghost_play_icon_optimized.ico")
        print("Sizes included:", [f"{img.size[0]}x{img.size[1]}" for img in images])
        
        return True
        
    except Exception as e:
        print(f"Error optimizing icon: {e}")
        return False

if __name__ == "__main__":
    optimize_icon()
