import os
import sys
import subprocess
import tkinter as tk
from tkinter import filedialog, ttk, messagebox
import threading
import json
import time
from pathlib import Path

class VideoConverter:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("Видео конвертер v2.22")
        self.window.geometry("600x650")
        
        # Настройки
        self.settings_file = "converter_settings.json"
        self.load_settings()
        
        # Инициализируем путь к ffmpeg
        self.ffmpeg_path = None
        self.current_process = None
        self.is_converting = False
        self.total_duration = 0
        self.converted_duration = 0
        
        # Загружаем тему
        self.setup_theme()
        self.setup_ui()
        self.find_ffmpeg()
    
    def load_settings(self):
        """Загружаем настройки из файла"""
        self.settings = {
            "theme": "dark",  # По умолчанию темная тема
            "video_bitrate": "2500",
            "audio_bitrate": "128",
            "profile": "main",
            "output_dir": "converted"
        }
        
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    loaded_settings = json.load(f)
                    self.settings.update(loaded_settings)
        except:
            pass
    
    def save_settings(self):
        """Сохраняем настройки в файл"""
        try:
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, indent=2, ensure_ascii=False)
        except:
            pass
    
    def setup_theme(self):
        """Настраиваем тему"""
        if self.settings["theme"] == "dark":
            self.apply_dark_theme()
        else:
            self.apply_light_theme()
    
    def apply_dark_theme(self):
        """Применяем темную тему"""
        self.window.configure(bg='#2b2b2b')
        
        # Стили для темной темы
        self.style = ttk.Style()
        
        # Темная тема для ttk виджетов
        self.style.theme_use('clam')
        
        # Конфигурация стилей
        self.style.configure('TLabel', background='#2b2b2b', foreground='#ffffff')
        self.style.configure('TButton', background='#3c3c3c', foreground='#ffffff')
        self.style.configure('TFrame', background='#2b2b2b')
        self.style.configure('TLabelframe', background='#2b2b2b', foreground='#ffffff')
        self.style.configure('TLabelframe.Label', background='#2b2b2b', foreground='#ffffff')
        self.style.configure('TRadiobutton', background='#2b2b2b', foreground='#ffffff')
        self.style.configure('TEntry', fieldbackground='#3c3c3c', foreground='#ffffff')
        self.style.configure('TProgressbar', background='#4CAF50', troughcolor='#3c3c3c')
        self.style.configure('Listbox', background='#3c3c3c', foreground='#ffffff')
        
        # Стиль для кнопок темы
        self.style.configure('Theme.TButton', background='#4CAF50', foreground='#ffffff')
    
    def apply_light_theme(self):
        """Применяем светлую тему"""
        self.window.configure(bg='#f0f0f0')
        
        # Стили для светлой темы
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Конфигурация стилей
        self.style.configure('TLabel', background='#f0f0f0', foreground='#000000')
        self.style.configure('TButton', background='#e0e0e0', foreground='#000000')
        self.style.configure('TFrame', background='#f0f0f0')
        self.style.configure('TLabelframe', background='#f0f0f0', foreground='#000000')
        self.style.configure('TLabelframe.Label', background='#f0f0f0', foreground='#000000')
        self.style.configure('TRadiobutton', background='#f0f0f0', foreground='#000000')
        self.style.configure('TEntry', fieldbackground='#ffffff', foreground='#000000')
        self.style.configure('TProgressbar', background='#4CAF50', troughcolor='#e0e0e0')
        self.style.configure('Listbox', background='#ffffff', foreground='#000000')
        
        # Стиль для кнопок темы
        self.style.configure('Theme.TButton', background='#4CAF50', foreground='#ffffff')
    
    def toggle_theme(self):
        """Переключает тему"""
        if self.settings["theme"] == "dark":
            self.settings["theme"] = "light"
        else:
            self.settings["theme"] = "dark"
        
        self.save_settings()
        self.setup_theme()
        
        # Перезагружаем UI
        for widget in self.window.winfo_children():
            widget.destroy()
        
        self.setup_ui()
    
    def find_ffmpeg(self):
        """Ищем ffmpeg в доступных местах"""
        try:
            # Список мест где может быть ffmpeg
            possible_locations = []
            
            # 1. Проверяем в папке с программой (для EXE)
            if getattr(sys, 'frozen', False):
                # Режим EXE - ищем в папке с программой
                exe_dir = os.path.dirname(sys.executable)
                possible_locations.append(os.path.join(exe_dir, 'ffmpeg.exe'))
                
                # 2. Проверяем во временной папке PyInstaller
                try:
                    base_path = sys._MEIPASS
                    possible_locations.append(os.path.join(base_path, 'ffmpeg.exe'))
                except:
                    pass
            else:
                # Режим разработки - ищем рядом со скриптом
                script_dir = os.path.dirname(os.path.abspath(__file__))
                possible_locations.append(os.path.join(script_dir, 'ffmpeg.exe'))
            
            # 3. Проверяем в PATH
            possible_locations.append('ffmpeg')
            
            # Пробуем все варианты
            for location in possible_locations:
                if self.try_ffmpeg(location):
                    self.ffmpeg_path = location
                    return True
            
            # Если ничего не нашли
            raise Exception("FFmpeg не найден ни в одной из возможных локаций")
            
        except Exception as e:
            messagebox.showerror(
                "Ошибка", 
                f"Не удалось найти FFmpeg:\n\n{str(e)}\n\n"
                "Убедитесь что ffmpeg.exe находится в той же папке что и программа."
            )
            sys.exit(1)
    
    def try_ffmpeg(self, path):
        """Пробуем запустить ffmpeg"""
        try:
            # Создаем startupinfo чтобы скрыть консоль
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            startupinfo.wShowWindow = subprocess.SW_HIDE
            
            # Пробуем получить версию
            result = subprocess.run(
                [path, '-version'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                stdin=subprocess.DEVNULL,
                creationflags=subprocess.CREATE_NO_WINDOW,
                startupinfo=startupinfo,
                timeout=2
            )
            
            return result.returncode == 0
            
        except:
            return False
    
    def validate_numeric(self, P):
        """Валидация ввода - только цифры"""
        if P == "" or P.isdigit():
            return True
        return False
    
    def get_video_duration(self, input_file):
        """Получаем длительность видео в секундах"""
        try:
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            startupinfo.wShowWindow = subprocess.SW_HIDE
            
            cmd = [
                self.ffmpeg_path,
                '-i', input_file,
                '-f', 'null',
                '-'
            ]
            
            process = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                stdin=subprocess.DEVNULL,
                creationflags=subprocess.CREATE_NO_WINDOW,
                startupinfo=startupinfo,
                encoding='utf-8',
                errors='ignore'
            )
            
            # Ищем длительность в выводе
            for line in process.stderr.split('\n'):
                if 'Duration:' in line:
                    time_str = line.split('Duration:')[1].split(',')[0].strip()
                    hours, minutes, seconds = time_str.split(':')
                    seconds = float(seconds)
                    minutes = int(minutes)
                    hours = int(hours)
                    
                    total_seconds = hours * 3600 + minutes * 60 + seconds
                    return total_seconds
            
            return 0
            
        except:
            return 0
    
    def parse_progress(self, line):
        """Парсим прогресс из строки FFmpeg"""
        if 'time=' in line:
            try:
                time_str = line.split('time=')[1].split(' ')[0]
                hours, minutes, seconds = time_str.split(':')
                seconds = float(seconds)
                minutes = int(minutes)
                hours = int(hours)
                
                current_seconds = hours * 3600 + minutes * 60 + seconds
                return current_seconds
            except:
                pass
        return None
    
    def convert_video_with_progress(self, input_file, output_file, progress_callback):
        """Конвертирует видео с отслеживанием прогресса"""
        # Получаем значения и форматируем для FFmpeg
        video_value = self.video_bitrate.get().strip()
        audio_value = self.audio_bitrate.get().strip()
        
        # Проверяем что значения не пустые
        if not video_value:
            video_value = "2500"
        if not audio_value:
            audio_value = "128"
        
        # Добавляем "k" если его нет
        video_bitrate = video_value if video_value.endswith('k') else f"{video_value}k"
        audio_bitrate = audio_value if audio_value.endswith('k') else f"{audio_value}k"
        
        profile = self.profile_var.get()
        
        # Команда ffmpeg с прогрессом
        cmd = [
            self.ffmpeg_path,
            '-i', input_file,
            '-c:v', 'libx264',
            '-preset', 'medium',
            '-profile:v', profile,
            '-b:v', video_bitrate,
            '-maxrate', video_bitrate,
            '-bufsize', '5000k',
            '-c:a', 'aac',
            '-b:a', audio_bitrate,
            '-movflags', '+faststart',
            '-progress', 'pipe:1',  # Вывод прогресса
            '-loglevel', 'info',    # Подробный лог
            '-y',
            output_file
        ]
        
        try:
            # Скрываем консольное окно
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            startupinfo.wShowWindow = subprocess.SW_HIDE
            
            # Запускаем процесс
            self.current_process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,  # Объединяем stdout и stderr
                stdin=subprocess.DEVNULL,
                creationflags=subprocess.CREATE_NO_WINDOW,
                startupinfo=startupinfo,
                encoding='utf-8',
                errors='ignore',
                bufsize=1,
                universal_newlines=True
            )
            
            # Читаем вывод построчно для отслеживания прогресса
            for line in iter(self.current_process.stdout.readline, ''):
                if progress_callback:
                    current_time = self.parse_progress(line)
                    if current_time is not None:
                        progress_callback(current_time)
            
            # Ждем завершения процесса
            self.current_process.wait()
            
            if self.current_process.returncode == 0:
                return True, output_file
            else:
                return False, "FFmpeg завершился с ошибкой"
                
        except Exception as e:
            return False, f"Исключение: {str(e)}"
        finally:
            self.current_process = None
    
    def setup_ui(self):
        # Заголовок
        title_frame = ttk.Frame(self.window)
        title_frame.pack(pady=10, padx=20, fill='x')
        
        title = ttk.Label(title_frame, 
                         text="🎬 Видео конвертер для работяг", 
                         font=('Arial', 16, 'bold'))
        title.pack(side='left')
        
        # Кнопка переключения темы
        theme_text = "🌙" if self.settings["theme"] == "dark" else "☀️"
        self.theme_btn = ttk.Button(title_frame, text=theme_text, 
                                   command=self.toggle_theme,
                                   width=3, style='Theme.TButton')
        self.theme_btn.pack(side='right')
        
        # Фрейм для выбора файлов
        frame_files = ttk.LabelFrame(self.window, text="Выбор файлов")
        frame_files.pack(pady=10, padx=20, fill='x')
        
        self.btn_select = ttk.Button(frame_files, 
                                    text="📁 Выбрать файлы", 
                                    command=self.select_files)
        self.btn_select.pack(pady=10, padx=10, fill='x')
        
        self.file_list = tk.Listbox(frame_files, height=5)
        self.file_list.pack(pady=5, padx=10, fill='x')
        
        # Фрейм настроек
        frame_settings = ttk.LabelFrame(self.window, text="Настройки кодирования")
        frame_settings.pack(pady=10, padx=20, fill='x')
        
        # Профиль кодирования
        profile_frame = ttk.Frame(frame_settings)
        profile_frame.pack(pady=5, padx=10, fill='x')
        
        ttk.Label(profile_frame, text="Профиль H.264:").pack(side='left')
        
        self.profile_var = tk.StringVar(value=self.settings["profile"])
        profile_radio_frame = ttk.Frame(profile_frame)
        profile_radio_frame.pack(side='left', padx=10)
        
        ttk.Radiobutton(profile_radio_frame, text="Main", 
                       variable=self.profile_var, value="main").pack(side='left', padx=5)
        ttk.Radiobutton(profile_radio_frame, text="Baseline", 
                       variable=self.profile_var, value="baseline").pack(side='left', padx=5)
        
        # Качество видео
        video_frame = ttk.Frame(frame_settings)
        video_frame.pack(pady=5, padx=10, fill='x')
        
        ttk.Label(video_frame, text="Битрейт видео:").pack(side='left')
        
        # Валидация для цифрового ввода
        vcmd = (self.window.register(self.validate_numeric), '%P')
        
        self.video_bitrate = ttk.Entry(video_frame, width=10, validate='key', validatecommand=vcmd)
        self.video_bitrate.insert(0, self.settings["video_bitrate"])
        self.video_bitrate.pack(side='left', padx=5)
        ttk.Label(video_frame, text="kbps").pack(side='left')
        
        # Качество аудио
        audio_frame = ttk.Frame(frame_settings)
        audio_frame.pack(pady=5, padx=10, fill='x')
        
        ttk.Label(audio_frame, text="Битрейт аудио:").pack(side='left')
        self.audio_bitrate = ttk.Entry(audio_frame, width=10, validate='key', validatecommand=vcmd)
        self.audio_bitrate.insert(0, self.settings["audio_bitrate"])
        self.audio_bitrate.pack(side='left', padx=5)
        ttk.Label(audio_frame, text="kbps").pack(side='left')
        
        # Прогресс
        progress_frame = ttk.LabelFrame(self.window, text="Прогресс")
        progress_frame.pack(pady=10, padx=20, fill='x')
        
        # Прогресс бар
        self.progress = ttk.Progressbar(progress_frame, mode='determinate', length=400)
        self.progress.pack(pady=10, padx=10, fill='x')
        
        # Информация о прогрессе
        self.progress_info = ttk.Label(progress_frame, text="Ожидание...")
        self.progress_info.pack(pady=5)
        
        # Время
        self.time_label = ttk.Label(progress_frame, text="")
        self.time_label.pack(pady=5)
        
        # Кнопка конвертации
        self.btn_convert = ttk.Button(self.window, 
                                     text="⚡ Конвертировать", 
                                     command=self.start_conversion)
        self.btn_convert.pack(pady=10)
        
        # Кнопка отмены
        self.btn_cancel = ttk.Button(self.window, 
                                    text="❌ Отмена", 
                                    command=self.cancel_conversion,
                                    state='disabled')
        self.btn_cancel.pack(pady=5)
        
        # Статус
        self.status_label = ttk.Label(self.window, text="Готов к работе", 
                                     font=('Arial', 10, 'italic'))
        self.status_label.pack(pady=5)
        
        # Версия FFmpeg
        self.version_label = ttk.Label(self.window, text="", font=('Arial', 8))
        self.version_label.pack(pady=5)
        
        # Показываем версию ffmpeg
        self.show_ffmpeg_version()
    
    def show_ffmpeg_version(self):
        """Показываем версию FFmpeg"""
        try:
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            startupinfo.wShowWindow = subprocess.SW_HIDE
            
            result = subprocess.run(
                [self.ffmpeg_path, '-version'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                stdin=subprocess.DEVNULL,
                creationflags=subprocess.CREATE_NO_WINDOW,
                startupinfo=startupinfo,
                encoding='utf-8',
                errors='ignore'
            )
            
            if result.returncode == 0:
                # Берем первую строку вывода
                first_line = result.stdout.split('\n')[0]
                self.version_label.config(text=f"FFmpeg: {first_line[:50]}...")
                
        except:
            pass
    
    def select_files(self):
        files = filedialog.askopenfilenames(
            title="Выберите видео файлы",
            filetypes=[
                ("Видео файлы", "*.mp4 *.avi *.mov *.mkv *.wmv *.flv *.webm *.mpg *.mpeg *.3gp"),
                ("Все файлы", "*.*")
            ]
        )
        
        if files:
            self.file_list.delete(0, tk.END)
            for file in files:
                self.file_list.insert(tk.END, os.path.basename(file))
            self.files_to_convert = list(files)
            self.update_status(f"Выбрано файлов: {len(files)}")
    
    def update_progress(self, current_time):
        """Обновляет прогресс бар"""
        if self.total_duration > 0:
            progress_percent = (current_time / self.total_duration) * 100
            self.progress['value'] = progress_percent
            
            # Оставшееся время
            if current_time > 0:
                elapsed_time = time.time() - self.start_time
                speed = current_time / elapsed_time if elapsed_time > 0 else 0
                remaining_time = (self.total_duration - current_time) / speed if speed > 0 else 0
                
                # Форматируем время
                current_str = self.format_time(current_time)
                total_str = self.format_time(self.total_duration)
                remaining_str = self.format_time(remaining_time)
                
                self.progress_info.config(text=f"{progress_percent:.1f}% ({current_str} / {total_str})")
                self.time_label.config(text=f"Осталось: {remaining_str}")
            
            self.window.update_idletasks()
    
    def format_time(self, seconds):
        """Форматирует время в ЧЧ:ММ:СС"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        
        if hours > 0:
            return f"{hours:02d}:{minutes:02d}:{secs:02d}"
        else:
            return f"{minutes:02d}:{secs:02d}"
    
    def start_conversion(self):
        """Запускает конвертацию в отдельном потоке"""
        if not hasattr(self, 'files_to_convert') or not self.files_to_convert:
            messagebox.showwarning("Внимание", "Сначала выберите файлы для конвертации!")
            return
        
        # Сохраняем настройки
        self.settings.update({
            "video_bitrate": self.video_bitrate.get().strip(),
            "audio_bitrate": self.audio_bitrate.get().strip(),
            "profile": self.profile_var.get()
        })
        self.save_settings()
        
        # Проверяем корректность введенных значений
        try:
            video_val = self.video_bitrate.get().strip()
            audio_val = self.audio_bitrate.get().strip()
            
            if not video_val or int(video_val) <= 0:
                messagebox.showerror("Ошибка", "Введите корректный битрейт видео (> 0)")
                return
                
            if not audio_val or int(audio_val) <= 0:
                messagebox.showerror("Ошибка", "Введите корректный битрейт аудио (> 0)")
                return
                
        except ValueError:
            messagebox.showerror("Ошибка", "Битрейт должен быть числом!")
            return
        
        # Блокируем кнопки во время конвертации
        self.btn_select.config(state='disabled')
        self.btn_convert.config(state='disabled')
        self.btn_cancel.config(state='normal')
        self.is_converting = True
        
        self.progress['value'] = 0
        self.progress_info.config(text="Подготовка...")
        self.time_label.config(text="")
        
        # Запускаем в отдельном потоке
        thread = threading.Thread(target=self.convert_all)
        thread.daemon = True
        thread.start()
    
    def cancel_conversion(self):
        """Отменяет конвертацию"""
        if self.current_process and self.is_converting:
            self.current_process.terminate()
            self.is_converting = False
            self.update_status("Конвертация отменена")
    
    def convert_all(self):
        """Конвертирует все выбранные файлы"""
        total_files = len(self.files_to_convert)
        success_count = 0
        errors = []
        
        for file_idx, input_file in enumerate(self.files_to_convert, 1):
            if not self.is_converting:
                break
                
            filename = os.path.basename(input_file)
            self.window.after(0, lambda f=filename, idx=file_idx, tot=total_files: 
                            self.update_status(f"Файл {idx}/{tot}: {f}"))
            
            # Создаем выходную папку
            output_dir = os.path.join(os.path.dirname(input_file), self.settings["output_dir"])
            os.makedirs(output_dir, exist_ok=True)
            
            output_file = os.path.join(output_dir, f"{os.path.splitext(filename)[0]}.mp4")
            
            # Получаем длительность видео
            self.total_duration = self.get_video_duration(input_file)
            self.converted_duration = 0
            self.start_time = time.time()
            
            if self.total_duration > 0:
                self.window.after(0, lambda: self.progress_info.config(text="0%"))
            
            # Функция обратного вызова для обновления прогресса
            def progress_callback(current_time):
                self.window.after(0, lambda: self.update_progress(current_time))
            
            # Конвертируем с отслеживанием прогресса
            success, result = self.convert_video_with_progress(
                input_file, output_file, progress_callback
            )
            
            if success:
                success_count += 1
                self.progress['value'] = 100
                self.progress_info.config(text="100% - Завершено")
                self.time_label.config(text="")
            else:
                errors.append(f"{filename}: {result}")
            
            # Сбрасываем прогресс
            self.window.after(0, lambda: self.progress.configure(value=0))
        
        # Восстанавливаем интерфейс
        self.window.after(0, self.restore_ui)
        
        # Показываем результаты
        self.window.after(0, lambda: 
                         self.update_status(f"Готово! Успешно: {success_count}/{total_files}"))
        
        if errors:
            error_text = "\n\n".join(errors[:3])
            if len(errors) > 3:
                error_text += f"\n\n...и еще {len(errors) - 3} ошибок"
            
            self.window.after(0, lambda: 
                            messagebox.showerror("Ошибки конвертации", 
                                               f"Были ошибки:\n\n{error_text}"))
        elif success_count > 0:
            self.window.after(0, lambda: 
                            messagebox.showinfo("Готово", 
                                              f"Конвертация завершена успешно!\n\n"
                                              f"Успешно: {success_count}/{total_files}\n"
                                              f"Файлы сохранены в папке '{self.settings['output_dir']}'"))
    
    def restore_ui(self):
        """Восстанавливает UI после конвертации"""
        self.btn_select.config(state='normal')
        self.btn_convert.config(state='normal')
        self.btn_cancel.config(state='disabled')
        self.is_converting = False
        self.current_process = None
        
        self.progress_info.config(text="Ожидание...")
        self.time_label.config(text="")
    
    def update_status(self, message):
        """Обновляет статус в UI"""
        self.status_label.config(text=message)
    
    def run(self):
        self.window.mainloop()

if __name__ == "__main__":
    app = VideoConverter()
    app.run()