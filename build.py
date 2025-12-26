import subprocess
import os
import shutil

def build_exe():
    print("=" * 60)
    print("          Сборка VideoConverter v2.0")
    print("=" * 60)
    
    # Проверяем наличие необходимых файлов
    print("\n🔍 Проверяю наличие файлов...")
    
    required_files = ["video_converter.py", "ffmpeg.exe"]
    missing_files = []
    
    for file in required_files:
        if not os.path.exists(file):
            missing_files.append(file)
    
    if missing_files:
        print("❌ ОШИБКА: Отсутствуют файлы:")
        for file in missing_files:
            print(f"   - {file}")
        
        if "ffmpeg.exe" in missing_files:
            print("\n📥 Скачайте ffmpeg.exe с:")
            print("   https://github.com/BtbN/FFmpeg-Builds/releases")
            print("\n   Выберите: ffmpeg-master-latest-win64-gpl.zip")
            print("   Извлеките ffmpeg.exe в текущую папку")
        
        input("\nНажмите Enter для выхода...")
        return
    
    print("✅ Все необходимые файлы найдены")
    
    # Очищаем старые сборки
    print("\n🧹 Очищаю старые сборки...")
    for folder in ['dist', 'build', '__pycache__']:
        if os.path.exists(folder):
            shutil.rmtree(folder)
            print(f"   ✓ Очищена папка: {folder}")
    
    # Команда для сборки БЕЗ иконки
    cmd = [
        'pyinstaller',
        '--onefile',
        '--windowed',
        '--noconsole',
        '--name=VideoConverter',
        '--add-data=ffmpeg.exe;.',
        '--clean',
        'video_converter.py'  # Убрали --icon=icon.ico
    ]
    
    print("\n⚙ Начинаю сборку...")
    print(f"\nКоманда:\n{' '.join(cmd)}\n")
    
    try:
        # Запускаем сборку
        result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8')
        
        if result.returncode == 0:
            print("✅ Сборка завершена успешно!")
            
            # Показываем информацию о созданном файле
            exe_path = os.path.abspath('dist/VideoConverter.exe')
            if os.path.exists(exe_path):
                size = os.path.getsize(exe_path) / 1024 / 1024
                print(f"\n📁 EXE файл: {exe_path}")
                print(f"📦 Размер: {size:.1f} MB")
                print(f"✨ Функции: Темная тема + Реальный прогресс")
            else:
                print("⚠ Файл не создан, проверьте папку build/")
                
        else:
            print("❌ Ошибка при сборке!")
            if result.stderr:
                print(f"\nДетали ошибки:\n{result.stderr}")
            
    except FileNotFoundError:
        print("❌ PyInstaller не найден!")
        print("\nУстановите PyInstaller:")
        print("   pip install pyinstaller")
    except Exception as e:
        print(f"❌ Неожиданная ошибка: {e}")
    
    print("\n" + "=" * 60)
    input("Нажмите Enter для выхода...")

if __name__ == "__main__":
    build_exe()