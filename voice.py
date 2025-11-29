import speech_recognition as sr
import webbrowser
import time
import pygame
from gtts import gTTS
import tempfile
import pyautogui
import threading
import os
import random
import datetime
import requests
import json
import subprocess
import sys
import psutil

class Jarvis:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.is_listening = False
        self.waiting_for_spell = False
        self.waiting_for_platform = False
        self.waiting_for_song = False
        self.waiting_for_video = False
        self.waiting_for_youtuber = False
        self.waiting_for_search = False
        self.current_platform = ""
        self.sleep_mode = False
        self.security_mode = False
        self.last_motivation_time = 0
        self.daily_questions_asked = False
        self.music_playing = False
        self.sleep_conversation_active = False
        self.assistant_mode = True
        self.background_mode = True
        
        # Gelişmiş ses tanıma ayarları
        self.recognizer.energy_threshold = 400
        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.pause_threshold = 1.0
        
        # Kullanıcının sevdiği youtuber'lar
        self.favorite_youtubers = [
            "Enes Batur",
            "Ruhi Çenet", 
            "Barış Özcan",
            "Lütfi Şahin",
            "Bebar Bilim",
            "Evrim Ağacı",
            "Teknofil",
            "Vogue Türkiye",
            "Mithrain",
            "Jahrein"
        ]
        
        # Motivasyon sözleri
        self.motivational_quotes = [
            "Harika iş çıkarıyorsun, seninle gurur duyuyorum!",
            "İnanılmaz bir enerjin var, bu seni başarıya götürecek!",
            "Yapabileceğine inanıyorsun, değil mi? Çünkü ben inanıyorum!",
            "Bugün harika bir gün olacak, buna eminim!",
            "Çalışmaların gerçekten takdire şayan, böyle devam et!",
            "Senin gibi birine sahip olduğum için çok şanslıyım!",
            "Enerjin ve azmin herkesi etkiliyor, muhteşemsin!",
            "Başarın tesadüf değil, emeğinin karşılığı!",
            "Her gün daha iyiye gidiyorsun, bu çok etkileyici!",
            "Seninle çalışmak gerçekten keyifli, enerjin bulaşıcı!"
        ]
        
        # Günlük sorular
        self.daily_questions = [
            "Bugün kendin için ne iyi bir şey yaptın?",
            "Bugün en çok neye minnettar hissediyorsun?",
            "Bugün öğrendiğin en ilginç şey neydi?",
            "Yarın için en büyük hedefin nedir?",
            "Bugün kendinle gurur duydun mu?",
            "Bugün nasıl bir iyilik yaptın?",
            "Bu hafta en çok neyi başarmak istiyorsun?",
            "Kendine bugün için bir hedef belirledin mi?",
            "Bugün seni en çok ne mutlu etti?",
            "Yarın bugünden daha iyi olmak için ne yapacaksın?"
        ]
        
        # Uyku modu sohbet soruları
        self.sleep_conversation_questions = [
            "Nasılsın? Bugün neler yaptın?",
            "Seninle konuşmak güzel, bana biraz kendinden bahseder misin?",
            "Bugün en sevdiğin an neydi?",
            "Hayatında en çok neye değer veriyorsun?",
            "Yakın zamanda öğrendiğin ilginç bir şey var mı?",
            "Kendini en mutlu hissettiğin anı hatırlıyor musun?",
            "Hayatta en büyük hayalin nedir?",
            "Son zamanlarda seni en çok ne güldürdü?",
            "Kendinle gurur duyduğun bir şey var mı?",
            "Gelecekte neler yapmak istiyorsun?"
        ]

        # Akıllı cevaplar
        self.smart_responses = {
            "nasılsın": "Teşekkür ederim, ben iyiyim. Siz nasılsınız?",
            "sen kimsin": "Ben JARVIS, size yardımcı olmak için buradayım!",
            "ne yapıyorsun": "Sizi dinliyorum ve komutlarınızı bekliyorum!",
            "teşekkür ederim": "Rica ederim, her zaman yanınızdayım!",
            "sağ ol": "Ne demek, ben buradayım!",
            "günaydın": "Günaydın! Harika bir gün geçirmenizi diliyorum!",
            "iyi geceler": "İyi geceler! Tatlı rüyalar!",
            "ne haber": "Her şey yolunda, sizden haber bekliyorum!",
            "harika": "Bu harika bir haber! Sizinle gurur duyuyorum!",
            "yorgunum": "Biraz dinlenmeyi düşünmelisiniz, size yardımcı olabilirim!"
        }
        
        pygame.mixer.init()
        
    def speak(self, text):
        """Özel asistan sesiyle konuş"""
        try:
            tts = gTTS(text=text, lang='tr', slow=False)
            with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as tmpfile:
                temp_filename = tmpfile.name
            
            tts.save(temp_filename)
            pygame.mixer.music.load(temp_filename)
            pygame.mixer.music.play()
            
            while pygame.mixer.music.get_busy():
                pygame.time.Clock().tick(10)
            
            pygame.mixer.music.stop()
            os.unlink(temp_filename)
            
        except Exception as e:
            print(f"JARVIS: {text}")

    def listen(self):
        """Gelişmiş ses tanıma - arka plan için optimize"""
        try:
            with sr.Microphone() as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                
                try:
                    audio = self.recognizer.listen(
                        source, 
                        timeout=10,
                        phrase_time_limit=8
                    )
                    command = self.recognizer.recognize_google(audio, language='tr-TR')
                    print(f"Siz: {command}")
                    return command.lower()
                except sr.WaitTimeoutError:
                    return ""
                except sr.UnknownValueError:
                    return ""
                except sr.RequestError as e:
                    return ""
        except Exception as e:
            return ""

    def is_chrome_running(self):
        """Chrome çalışıyor mu kontrol et"""
        try:
            for process in psutil.process_iter(['name']):
                if 'chrome' in process.info['name'].lower():
                    return True
            return False
        except:
            return False

    def security_mode_on(self):
        """Güvenlik modunu aç"""
        self.security_mode = True
        self.speak("Güvenlik modu aktif.")
        
    def security_mode_off(self):
        """Güvenlik modunu kapat"""
        self.security_mode = False
        self.speak("Güvenlik modu kapatıldı.")

    def open_netflix(self):
        """Netflix'i aç"""
        webbrowser.open("https://www.netflix.com")
        self.speak("Netflix açılıyor")

    def open_maps(self):
        """Google Haritalar'ı aç"""
        webbrowser.open("https://www.google.com/maps")
        self.speak("Google Haritalar açılıyor")

    def open_news(self):
        """Haberleri aç"""
        webbrowser.open("https://news.google.com")
        self.speak("Google Haberler açılıyor")

    def google_search(self, query):
        """Google'da arama yap"""
        search_query = query.replace(' ', '+')
        url = f"https://www.google.com/search?q={search_query}"
        webbrowser.open(url)
        self.speak(f"Google'da {query} aranıyor")

    def ask_search(self):
        """Google arama için ne aramak istediğini sor"""
        self.speak("Google'da ne aramamı istersiniz? efendim")
        self.waiting_for_search = True

    def close_and_switch_tab(self):
        """Sekmeyi kapat ve diğerine geç - GÜNCELLENDİ"""
        try:
            pyautogui.hotkey('ctrl', 'w')  # Mevcut sekmeyi kapat
            time.sleep(0.3)
            pyautogui.hotkey('ctrl', 'tab')  # Diğer sekmeye geç
            self.speak("Sekme kapatıldı ve diğer sekmeye geçildi")
        except Exception as e:
            self.speak("Sekme değiştirilemedi")

    def ask_youtuber(self):
        """Hangi youtuber istediğini sor"""
        youtuber_list = ", ".join(self.favorite_youtubers[:5])
        self.speak(f"Hangi youtuber'ın videosunu izlemek istersiniz? Örneğin: {youtuber_list}")
        self.waiting_for_youtuber = True

    def play_youtuber_video(self, youtuber_name):
        """Youtuber videosu aç"""
        youtuber_clean = youtuber_name.replace(' ', '+')
        url = f"https://www.youtube.com/results?search_query={youtuber_clean}"
        webbrowser.open(url)
        self.speak(f"{youtuber_name} videoları açılıyor")

    def play_youtube_song(self, song_name):
        """YouTube'dan direkt şarkı aç"""
        song_clean = song_name.replace(' ', '+')
        url = f"https://www.youtube.com/results?search_query={song_clean}"
        webbrowser.open(url)
        self.speak(f"YouTube'da {song_name} aranıyor")

    def spell_text(self, text):
        """Metni hecele ve oku"""
        spelled_text = " ".join(text.upper())
        self.speak(f"Heceleme: {spelled_text}")
        self.speak(f"Okunuş: {text}")

    def get_time(self):
        """Saati söyle"""
        now = datetime.datetime.now()
        hour = now.hour
        minute = now.minute
        
 
        if minute < 10:
            minute_str = f"sıfır {minute}"
        else:
            minute_str = str(minute)
            
        time_text = f"Saat {hour} {minute_str}"
        self.speak(time_text)
        return time_text

    def get_weather(self, city="iskenderun"):
        """Hava durumu bilgisini al"""
        try:
            conditions = ["açık", "parçalı bulutlu", "bulutlu", "hafif yağmurlu", "güneşli", "yağmurlu"]
            temps = [15, 18, 20, 22, 25, 28]
            condition = random.choice(conditions)
            temp = random.choice(temps)
            weather_text = f"{city} için hava durumu: {condition}, sıcaklık {temp} derece"
                
            self.speak(weather_text)
            return weather_text
            
        except Exception as e:
            error_text = "Hava durumu bilgisi alınamadı"
            self.speak(error_text)
            return error_text

    def pause_music(self):
        """Müziği duraklat - SADECE müziği durdur, JARVIS'i kapatma"""
        try:
            pyautogui.press('space')
            self.music_playing = False
            self.speak("Müzik duraklatıldı")
        except Exception as e:
            self.speak("Müzik duraklatılamadı")

    def resume_music(self):
        """Müziği devam ettir"""
        try:
            pyautogui.press('space')
            self.music_playing = True
            self.speak("Müzik devam ediyor")
        except Exception as e:
            self.speak("Müzik devam ettirilemedi")

    def next_track(self):
        """Sonraki şarkı - Spotify ve YouTube uyumlu"""
        try:
            if self.current_platform == "youtube":
                pyautogui.hotkey('shift', 'n')
            elif self.current_platform == "spotify":
                pyautogui.hotkey('ctrl', 'right')
            else:
                pyautogui.press('nexttrack')
                
            self.speak("Sonraki şarkıya geçiliyor")
        except Exception as e:
            self.speak("Şarkı değiştirilemedi")

    def previous_track(self):
        """Önceki şarkı - Spotify ve YouTube uyumlu"""
        try:
            if self.current_platform == "youtube":
                pyautogui.hotkey('shift', 'p')
            elif self.current_platform == "spotify":
                pyautogui.hotkey('ctrl', 'left')
            else:
                pyautogui.press('prevtrack')
                
            self.speak("Önceki şarkıya geçiliyor")
        except Exception as e:
            self.speak("Şarkı değiştirilemedi")

    def change_track(self):
        """Şarkı değiştir (sonraki şarkı)"""
        self.next_track()
        self.speak("Şarkı değiştiriliyor")

    def change_tab(self):
        """Sekme değiştir - GÜNCELLENDİ: Kapat ve geç"""
        self.close_and_switch_tab()

    def change_video(self):
        """Video değiştir"""
        pyautogui.hotkey('shift', 'n')
        self.speak("Video değiştiriliyor")

    def youtube_fullscreen(self):
        """YouTube'da tam ekran yap"""
        pyautogui.press('f')
        self.speak("YouTube tam ekran yapıldı")

    def ask_video(self):
        """Video sorma"""
        self.speak("Hangi videoyu açmamı istersiniz?")
        self.waiting_for_video = True

    def play_video(self, video_name):
        """Video aç"""
        video_clean = video_name.replace(' ', '+')
        url = f"https://www.youtube.com/results?search_query={video_clean}"
        webbrowser.open(url)
        self.speak(f"{video_name} videosu aranıyor")

    def smart_response(self, command):
        """Akıllı cevap ver"""
        for key, response in self.smart_responses.items():
            if key in command:
                self.speak(response)
                return True
        return False

    def start_sleep_conversation(self):
        """Uyku modu sohbetini başlat"""
        self.sleep_conversation_active = True
        self.speak("Uyku moduna geçtim. beni çağırmak için uyan demeniz yeterli efendim")
        
        def conversation_loop():
            time.sleep(3)
            while self.sleep_mode and self.sleep_conversation_active:
                question = random.choice(self.sleep_conversation_questions)
                self.speak(question)
                
                time.sleep(2)
                response = self.listen()
                if response:
                    if any(word in response for word in ["hayır", "yeter", "dur", "sus", "kapat"]):
                        self.speak("Tamam, sessizce dinliyorum. Beni istediğin zaman çağırabilirsin.")
                        self.sleep_conversation_active = False
                    else:
                        if not self.smart_response(response):
                            friendly_responses = [
                                "Bu çok ilginç, devam edebilir misin?",
                                "Seni dinlemek gerçekten güzel",
                                "Bunu duyduğuma sevindim",
                                "Senin hakkında daha fazla şey öğrenmek istiyorum",
                                "Harika, başka neler paylaşmak istersin?"
                            ]
                            response_text = random.choice(friendly_responses)
                            self.speak(response_text)
                
                time.sleep(random.randint(20, 40))
        
        conversation_thread = threading.Thread(target=conversation_loop)
        conversation_thread.daemon = True
        conversation_thread.start()

    def motivate_user(self):
        """Kullanıcıyı motive et"""
        quote = random.choice(self.motivational_quotes)
        self.speak(quote)
        self.last_motivation_time = time.time()

    def ask_daily_question(self):
        """Günlük soru sor"""
        if not self.daily_questions_asked:
            question = random.choice(self.daily_questions)
            self.speak(question)
            self.daily_questions_asked = True

    def auto_motivation_check(self):
        """Otomatik motivasyon kontrolü"""
        current_time = time.time()
        if current_time - self.last_motivation_time > 1700:  # 30 dakika
            if random.random() < 0.3:
                self.motivate_user()

    def ask_platform(self):
        """Platform sorma"""
        self.speak("Hangi platformda açayım? YouTube veya Spotify? efendim")
        self.waiting_for_platform = True

    def ask_song(self):
        """Şarkı sorma"""
        self.speak("Hangi şarkıyı çalmamı istersiniz? efendim")
        self.waiting_for_song = True

    def ask_youtube_song(self):
        """YouTube için şarkı sorma"""
        self.speak("YouTube'da hangi şarkıyı açmamı istersiniz? efendim")
        self.waiting_for_song = True

    def ask_spell(self):
        """Heceleme için metin sor"""
        self.speak("Hangi metni hecelememi istersiniz? efendim")
        self.waiting_for_spell = True

    def play_music(self, platform, song_name=""):
        """Müzik çal"""
        self.music_playing = True
        self.current_platform = platform
        
        if platform == "youtube":
            if song_name:
                song_clean = song_name.replace(' ', '+')
                url = f"https://www.youtube.com/results?search_query={song_clean}"
                self.speak(f"YouTube'da {song_name} çalınıyor")
            else:
                url = "https://www.youtube.com"
                self.speak("YouTube açılıyor")
        elif platform == "spotify":
            if song_name:
                song_clean = song_name.replace(' ', '+')
                url = f"https://open.spotify.com/search/{song_clean}"
                self.speak(f"Spotify'da {song_name} aranıyor")
            else:
                url = "https://open.spotify.com"
                self.speak("Spotify açılıyor")
        else:
            url = "https://www.youtube.com"
            
        webbrowser.open(url)

    def execute_command(self, command):
        """Komutu çalıştır"""
        
        # Güvenlik modu kontrolü
        if self.security_mode:
            if any(word in command for word in ["güvenlik kapat", "güvenlik modu kapat", "güvenlik kapat"]):
                self.security_mode_off()
                return True
            else:
                self.speak("Güvenlik modu aktif. Sadece güvenlik komutları çalışıyor. efendim")
                return True
        
        # Akıllı cevap kontrolü
        if self.smart_response(command):
            return True
        
        # Uyku modu kontrolü - ÖNEMLİ: Bu diğer komutlardan önce gelmeli
        if self.sleep_mode:
            if any(word in command for word in ["uyan", "merhaba", "jarvis", "hey jarvis", "uyuyan jarvis"]):
                self.sleep_mode = False
                self.sleep_conversation_active = False
                self.speak("Uyandım! Seni özlemiştim. Nasılsın? efendim")
                return True
            else:
                # Uyku modundayken diğer komutları görmezden gel
                return True
        
        # Google arama bekleniyorsa
        if self.waiting_for_search:
            self.waiting_for_search = False
            self.google_search(command)
            return True
            
        # Google arama komutları
        if any(word in command for word in ["google'da ara", "google ara", "arama yap", "internette ara", "webde ara"]):
            # Komuttan arama terimini çıkarmaya çalış
            search_terms = [
                "google'da ara",
                "google ara", 
                "arama yap",
                "internette ara",
                "webde ara"
            ]
            
            search_query = command
            for term in search_terms:
                search_query = search_query.replace(term, "").strip()
            
            if search_query and len(search_query) > 2:
                self.google_search(search_query)
            else:
                self.ask_search()
            return True
        
        # Müzik duraklatma komutu - "dur" komutundan önce gelmeli
        if any(word in command for word in ["duraklat", "müziği durdur", "şarkıyı durdur", "durdur"]):
            self.pause_music()
            return True
            
        # Gelişmiş sekme değiştirme komutu
        if any(word in command for word in ["sekme değiştir", "sekmeyi kapat ve geç", "kapat ve geç"]):
            self.close_and_switch_tab()
            return True
            
        # Netflix komutu
        if any(word in command for word in ["film aç", "netflix aç", "sinema aç"]):
            self.open_netflix()
            return True
            
        # Gelişmiş haritalar komutları
        if any(word in command for word in ["haritaları aç", "harita aç", "maps aç", "haritalar"]):
            self.open_maps()
            return True
            
        # Gelişmiş haberler komutları
        if any(word in command for word in ["haberleri aç", "haber aç", "haberler", "gündem"]):
            self.open_news()
            return True
        
        # YouTube direkt şarkı açma
        if any(word in command for word in ["şarkıyı youtube dan aç", "youtube dan şarkı aç", "youtube şarkı aç"]):
            self.ask_youtube_song()
            return True
        
        # Değiştirme komutları
        if any(word in command for word in ["şarkı değiştir", "müzik değiştir"]):
            self.change_track()
            return True
            
        # SEKME DEĞİŞTİR KOMUTU GÜNCELLENDİ - Artık kapatıp geçecek
        if any(word in command for word in ["sekme değiştir", "sekme geç"]):
            self.change_tab()  # Bu artık close_and_switch_tab fonksiyonunu çağırıyor
            return True
            
        if any(word in command for word in ["video değiştir", "sonraki video"]):
            self.change_video()
            return True
        
        # Youtuber bekleniyorsa
        if self.waiting_for_youtuber:
            self.waiting_for_youtuber = False
            self.play_youtuber_video(command)
            return True
            
        # Video açma kontrolü
        if self.waiting_for_video:
            self.waiting_for_video = False
            self.play_video(command)
            return True
            
        # YouTube şarkı açma kontrolü
        if self.waiting_for_song and "youtube" in command:
            self.waiting_for_song = False
            self.play_youtube_song(command)
            return True
            
        # YouTube youtuber komutu
        if any(word in command for word in ["video aç", "youtuber videosu aç"]):
            self.ask_youtuber()
            return True
        
        # YouTube tam ekran
        if any(word in command for word in ["tam ekran", "fullscreen", "ekranı büyüt"]):
            self.youtube_fullscreen()
            return True
            
        # Heceleme modu kontrolü
        if self.waiting_for_spell:
            self.waiting_for_spell = False
            self.spell_text(command)
            return True
            
        # Heceleme komutu
        if any(word in command for word in ["hecele", "heceleyerek oku", "harf harf oku"]):
            self.ask_spell()
            return True
        
        # Şarkı kontrol komutları
        if any(word in command for word in ["şarkı devam et", "müzik devam et", "devam et"]):
            self.resume_music()
            return True
            
        if any(word in command for word in ["sonraki şarkı", "bir sonraki", "next"]):
            self.next_track()
            return True
            
        if any(word in command for word in ["önceki şarkı", "bir önceki", "previous"]):
            self.previous_track()
            return True
        
        # Saat komutu
        if any(word in command for word in ["saat kaç", "saati söyle", "saat"]):
            self.get_time()
            return True
            
        # Hava durumu komutu
        if any(word in command for word in ["hava durumu", "hava nasıl", "havayı söyle", "hava"]):
            self.get_weather()
            return True
        
        # Motivasyon komutları
        if any(word in command for word in ["beni öv", "motivasyon", "moral", "güzel söz"]):
            self.motivate_user()
            return True
            
        # Günlük soru komutları
        if any(word in command for word in ["soru sor", "günlük soru", "düşündürücü soru"]):
            self.ask_daily_question()
            return True

        # Uyku moduna geç - ÖNEMLİ: Bu "dur" komutundan önce gelmeli
        if any(word in command for word in ["uyku modu", "uyu", "sleep", "dinlenme modu"]):
            self.sleep_mode = True
            self.start_sleep_conversation()
            return True

        # Güncellenmiş güvenlik modu komutları
        if any(word in command for word in ["güvenlik modu", "güvenlik aç", "koruma modu"]):
            self.security_mode_on()
            return True

        # Platform bekleniyorsa
        if self.waiting_for_platform:
            self.waiting_for_platform = False
            if "youtube" in command:
                self.current_platform = "youtube"
                self.ask_song()
            elif "spotify" in command:
                self.current_platform = "spotify"
                self.ask_song()
            else:
                self.speak("Anlayamadım, YouTube veya Spotify seçin")
                self.ask_platform()
            return True

        # Şarkı bekleniyorsa
        if self.waiting_for_song:
            self.waiting_for_song = False
            self.play_music(self.current_platform, command)
            return True

        # Normal komutlar
        if "müzik aç" in command or "şarkı aç" in command:
            self.ask_platform()
            
        elif "müzikal aç" in command:
            self.speak("Müzikal açılıyor")
            webbrowser.open("https://www.youtube.com/results?search_query=müzikal")
            
        elif "sesi aç" in command:
            self.speak("Ses açılıyor")
            for i in range(8):
                pyautogui.press('volumeup')
                
        elif "sesi kıs" in command:
            self.speak("Ses kısılıyor")
            for i in range(8):
                pyautogui.press('volumedown')
                
        elif "sekme aç" in command:
            self.speak("Yeni sekme açılıyor")
            pyautogui.hotkey('ctrl', 't')
            
        elif "sekme kapat" in command:
            self.speak("Sekme kapatılıyor")
            pyautogui.hotkey('ctrl', 'w')
            
        elif "chrome aç" in command:
            self.speak("Chrome açılıyor")
            webbrowser.open("https://www.google.com")
            
        # "DUR" komutu - EN SONA EKLENDİ
        elif any(word in command for word in ["kapan", "çık", "dur jarvis"]):
            self.speak("JARVIS kapanıyor. Harika bir gün geçirmeni dilerim!")
            return False
            
        else:
            # Anlaşılmayan komutlar için nazikçe yardım teklif et
            if len(command) > 3:  # Rastgele sesleri görmezden gel
                self.speak("Bu komutu anlamadım. Müzik, video, haberler, Google arama veya haritalar gibi şeyler için yardım edebilirim.")
            
        return True

    def background_listener(self):
        """Arka plan dinleyici - Chrome dışında da çalışır"""
        print("🔄 Arka plan dinleyici başlatıldı...")
        
        while self.is_listening:
            try:
                chrome_running = self.is_chrome_running()
                
                if not chrome_running:
                    print("🔍 Chrome kapalı, ama JARVIS dinlemeye devam ediyor...")
                
                # ARKA PLAN MESAJ KONTROLÜ KALDIRILDI
                
                command = self.listen()
                if command:
                    if not self.execute_command(command):
                        self.is_listening = False
                else:
                    time.sleep(2)
                    self.auto_motivation_check()
                    
            except Exception as e:
                # Hata olsa bile dinlemeye devam et
                print(f"🔧 Dinleyici hatası: {e}")
                time.sleep(2)
                continue

    def start(self):
        """JARVIS'i başlat"""
        self.speak("Merhaba! Ben JARVIS, arka planda çalışmaya başlıyorum.")
        self.speak("Chrome açık olmasa bile sizi dinliyorum. Her zaman yanınızdayım!")
        self.is_listening = True
        
        time.sleep(1)
        self.motivate_user()
        
        # Arka plan dinleyiciyi başlat
        background_thread = threading.Thread(target=self.background_listener)
        background_thread.daemon = True
        background_thread.start()

def minimize_console():
    """Konsolu minimize et (Windows için)"""
    try:
        import win32gui
        import win32con
        window = win32gui.GetForegroundWindow()
        win32gui.ShowWindow(window, win32con.SW_MINIMIZE)
    except:
        pass

if __name__ == "__main__":
    print("🚀 JARVIS Güncellenmiş Sürüm Başlatılıyor...")
    print("🎵 ÖZELLİK: 'sekme değiştir' artık sekmeyi kapatıp diğerine geçer")
    print("🔊 ÖZELLİK: Özel asistan sesi")
    print("🔍 YENİ ÖZELLİK: Google arama desteği")
    print("❌ ARKA PLAN MESAJLARI: KALDIRILDI")
    print("")
    print("🔄 Gelişmiş Sekme Kontrolü:")
    print("   • 'sekme değiştir' - Mevcut sekmeyi kapatır ve diğerine geçer")
    print("🔍 Google Arama Komutları:")
    print("   • 'google'da ara [aranacak kelime]'")
    print("   • 'arama yap [aranacak kelime]'")
    print("   • 'google ara' - sonra ne aramak istediğinizi sorar")
    print("🗺️  Harita Komutları: 'haritalar'")
    print("📰 Haber Komutları: 'haberler'")
    print("🔒 Güvenlik: 'güvenlik modu'")
    print("🎵 YouTube: 'şarkıyı youtube dan aç'")
    print("🎬 Netflix: 'film aç'")
    print("⏸️  ÖNEMLİ: 'duraklat' = müziği durdur, 'kapan' = JARVIS'i kapat")
    print("")
    print("⚡ JARVIS 3 saniye içinde arka planda başlayacak...")
    
    # Konsolu minimize et
    minimize_console()
    
    time.sleep(3)
    
    try:
        jarvis = Jarvis()
        jarvis.start()
        
        # Ana döngü - programın kapanmaması için
        while jarvis.is_listening:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n❌ Program kullanıcı tarafından durduruldu")
    except Exception as e:
        print(f"❌ Hata: {e}")
    finally:
        print("👋 JARVIS kapatılıyor...")