from PIL import Image, ImageDraw, ImageFont
import os

def create_icon():
    """Создает простую иконку 256x256"""
    try:
        # Создаем изображение
        size = 256
        img = Image.new('RGB', (size, size), color='#4CAF50')
        draw = ImageDraw.Draw(img)
        
        # Рисуем круг
        draw.ellipse([10, 10, size-10, size-10], fill='#2E7D32', outline='#1B5E20', width=5)
        
        # Рисуем треугольник (символ play)
        triangle_size = 120
        x1, y1 = size//2 - triangle_size//3, size//2 - triangle_size//2
        x2, y2 = size//2 - triangle_size//3, size//2 + triangle_size//2
        x3, y3 = size//2 + triangle_size//2, size//2
        
        draw.polygon([(x1, y1), (x2, y2), (x3, y3)], fill='#FFFFFF')
        
        # Сохраняем в разных размерах для иконки
        icon_sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
        icon_images = []
        
        for sz in icon_sizes:
            resized = img.resize(sz, Image.Resampling.LANCZOS)
            icon_images.append(resized)
        
        # Сохраняем как ICO
        icon_images[0].save('icon.ico', format='ICO', sizes=icon_sizes)
        print("✅ Иконка создана: icon.ico")
        
        # Также сохраняем как PNG для просмотра
        img.save('icon.png')
        print("✅ PNG иконка создана: icon.png")
        
    except ImportError:
        print("❌ Pillow не установлен!")
        print("Установите: pip install pillow")
        
        # Создаем пустую иконку
        with open('icon.ico', 'wb') as f:
            f.write(b'')  # Пустой файл
        print("⚠ Создан пустой файл icon.ico")
    
    except Exception as e:
        print(f"❌ Ошибка при создании иконки: {e}")
        
        # Создаем пустую иконку
        with open('icon.ico', 'wb') as f:
            f.write(b'')
        print("⚠ Создан пустой файл icon.ico")

if __name__ == "__main__":
    create_icon()