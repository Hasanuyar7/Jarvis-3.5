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
import psutil
import sys
import json
from typing import Dict, List, Tuple, Any, Optional
from dataclasses import dataclass
from enum import Enum

# ==================== DUYGU ANALİZİ SEVİYE 5 SİSTEMİ ====================

class Emotion(Enum):
    """Duygu türleri"""
    JOY = "neşe"
    SADNESS = "üzüntü"
    ANGER = "öfke"
    FEAR = "korku"
    SURPRISE = "şaşkınlık"
    DISGUST = "tiksinme"
    NEUTRAL = "nötr"
    LOVE = "sevgi"
    GRATITUDE = "minnettarlık"
    PRIDE = "gurur"
    SHAME = "utanç"
    ENVY = "kıskançlık"
    HOPE = "umut"
    RELIEF = "rahatlama"
    DISAPPOINTMENT = "hayal kırıklığı"

@dataclass
class EmotionalState:
    """Duygu durumu analizi sonucu"""
    primary_emotion: Emotion
    secondary_emotions: List[Emotion]
    intensity: float  # 0.0 - 1.0
    confidence: float  # 0.0 - 1.0
    triggers: List[str]  # Duyguyu tetikleyen kelimeler
    context_score: Dict[str, float]  # Bağlamsal puanlar
    timestamp: float

class Level5EmotionAnalyzer:
    """Seviye 5 Duygu Analizi Sistemi"""
    
    def __init__(self):
        self.emotion_history = []
        self.user_profile = {}
        self.emotion_patterns = {}
        self.conversation_memory = []  # YENİ: Konuşma belleği
        self.curiosity_level = 0.7  # YENİ: Merak seviyesi
        self.question_count = 0  # YENİ: Soru sayacı
        self.initialize_advanced_models()
        
    def initialize_advanced_models(self):
        """Gelişmiş duygu analizi modellerini başlat"""
        self.emotion_hierarchy = {
            "basic": [Emotion.JOY, Emotion.SADNESS, Emotion.ANGER, Emotion.FEAR],
            "complex": [Emotion.LOVE, Emotion.GRATITUDE, Emotion.PRIDE, Emotion.HOPE],
            "social": [Emotion.SHAME, Emotion.ENVY, Emotion.RELIEF, Emotion.DISAPPOINTMENT]
        }
        
        self.turkish_emotion_lexicon = self.load_turkish_emotion_lexicon()
        self.self_awareness = self.define_ethical_bounds()
        
        # YENİ: Soru şablonları
        self.question_templates = self.initialize_question_templates()
    
    def initialize_question_templates(self):
        """Soru şablonlarını başlat"""
        return {
            "deep_thinking": [
                "Bu konu hakkında ne düşünüyorsunuz?",
                "Bana bu konuda daha fazla anlatır mısınız?",
                "Bu size nasıl hissettiriyor?",
                "Bu konuda merak ettiğiniz başka bir şey var mı?",
                "Bu fikrinizi neyin etkilediğini düşünüyorsunuz?"
            ],
            "emotional": [
                "Bu konuda nasıl hissediyorsunuz?",
                "Bu duygu size ne düşündürüyor?",
                "Bu hissin arkasında ne yatıyor?",
                "Bu duyguyla nasıl başa çıkıyorsunuz?",
                "Bu konuda konuşmak size iyi gelir mi?"
            ],
            "curiosity": [
                "Bunu nasıl keşfettiniz?",
                "Bu konuda daha fazla bilgi edinmek ister misiniz?",
                "Size bunun hakkında ne ilginç geliyor?",
                "Bu konuda başka neler merak ediyorsunuz?",
                "Bana bu konuda bir şey öğretir misiniz?"
            ],
            "reflective": [
                "Daha önce buna benzer bir durum yaşadınız mı?",
                "Bu deneyim size ne öğretti?",
                "Bu konu hakkındaki görüşleriniz zamanla değişti mi?",
                "Bu size neyin önemli olduğunu hatırlattı?",
                "Bundan ne sonuç çıkarıyorsunuz?"
            ]
        }
    
    def load_turkish_emotion_lexicon(self) -> Dict[str, Dict[str, float]]:
        """Türkçe duygu sözlüğü yükle"""
        lexicon = {
            # Neşe
            "mutlu": {"joy": 0.9, "love": 0.3},
            "sevinç": {"joy": 0.95, "surprise": 0.2},
            "neşe": {"joy": 0.85},
            "harika": {"joy": 0.8, "pride": 0.4},
            "mükemmel": {"joy": 0.7, "gratitude": 0.3},
            "iyi": {"joy": 0.6},
            "güzel": {"joy": 0.5},
            "süper": {"joy": 0.7},
            "gül": {"joy": 0.8},
            
            # Üzüntü
            "üzgün": {"sadness": 0.9, "disappointment": 0.4},
            "keder": {"sadness": 0.95, "fear": 0.2},
            "hüzün": {"sadness": 0.85},
            "kırgın": {"sadness": 0.7, "anger": 0.3},
            "yalnız": {"sadness": 0.8, "fear": 0.3},
            "kötü": {"sadness": 0.6, "disappointment": 0.3},
            "berbat": {"sadness": 0.7, "anger": 0.4},
            "ağla": {"sadness": 0.9},
            
            # Öfke
            "kızgın": {"anger": 0.9, "disgust": 0.3},
            "sinir": {"anger": 0.85},
            "öfke": {"anger": 0.95},
            "hırs": {"anger": 0.6, "pride": 0.4},
            "küfür": {"anger": 0.8},
            "sinirlen": {"anger": 0.7},
            
            # Korku
            "korku": {"fear": 0.95},
            "endişe": {"fear": 0.8, "sadness": 0.3},
            "panik": {"fear": 0.9, "surprise": 0.4},
            "tedirgin": {"fear": 0.7},
            "kork": {"fear": 0.8},
            
            # Sevgi
            "sevgi": {"love": 0.95, "joy": 0.5},
            "aşk": {"love": 0.98, "joy": 0.6},
            "değer": {"love": 0.7, "gratitude": 0.4},
            "seviyorum": {"love": 0.9},
            "aşığım": {"love": 0.95},
            
            # Minnettarlık
            "teşekkür": {"gratitude": 0.9, "joy": 0.4},
            "minnettar": {"gratitude": 0.85},
            "sağ ol": {"gratitude": 0.7},
            "eyvallah": {"gratitude": 0.6},
            
            # Gurur
            "gurur": {"pride": 0.9, "joy": 0.4},
            "başarı": {"pride": 0.85, "joy": 0.5},
            "başardım": {"pride": 0.8},
            "kazandım": {"pride": 0.7},
            
            # Umut
            "umut": {"hope": 0.9, "joy": 0.3},
            "gelecek": {"hope": 0.7, "fear": 0.2},
            "inşallah": {"hope": 0.6},
            "beklenti": {"hope": 0.5},
            
            # Şaşkınlık
            "şaşkın": {"surprise": 0.8},
            "vay": {"surprise": 0.7},
            "oha": {"surprise": 0.9},
            "inanılmaz": {"surprise": 0.6, "joy": 0.4},
            
            # Tiksinme
            "tiksin": {"disgust": 0.8},
            "iğrenç": {"disgust": 0.9},
            "pis": {"disgust": 0.7},
            
            # Hayal kırıklığı
            "hayal kırıklığı": {"disappointment": 0.9},
            "hayalkırıklığı": {"disappointment": 0.9},
            "keşke": {"disappointment": 0.7, "sadness": 0.4},
        }
        return lexicon
    
    def define_ethical_bounds(self) -> Dict[str, Any]:
        """Etik sınırları tanımla"""
        return {
            "privacy_respect": True,
            "emotional_manipulation": False,
            "transparency": True,
            "user_consent": True,
            "emotional_safety": True
        }
    
    def analyze_with_context(self, text: str, context: Dict = None) -> EmotionalState:
        """Metni bağlamla birlikte analiz et"""
        if context is None:
            context = {}
        
        # 1. Dilbilimsel Analiz
        linguistic_features = self.extract_linguistic_features(text)
        
        # 2. Semantik Anlama
        semantic_scores = self.analyze_semantics(text)
        
        # 3. Duygu Sözlüğü Eşleştirme
        emotion_scores = self.emotion_lexicon_matching(text)
        
        # 4. Bağlamsal Değerlendirme
        context_scores = self.evaluate_context(text, context)
        
        # 5. Çok Katmanlı Duygu Sınıflandırma
        final_analysis = self.multi_layer_classification(
            linguistic_features,
            semantic_scores,
            emotion_scores,
            context_scores
        )
        
        # 6. Tarihsel Bağlam Entegrasyonu
        final_analysis = self.integrate_historical_context(final_analysis)
        
        # 7. Kendini Düzelten Analiz
        final_analysis = self.self_correcting_analysis(final_analysis)
        
        # 8. Duygu durumunu kaydet
        self.emotion_history.append(final_analysis)
        
        # 9. Kullanıcı profilini güncelle
        self.update_user_profile(final_analysis)
        
        # 10. Konuşmayı belleğe kaydet
        self.store_conversation_memory(text, final_analysis)
        
        return final_analysis
    
    def store_conversation_memory(self, text: str, analysis: EmotionalState):
        """Konuşmayı belleğe kaydet"""
        memory_entry = {
            "text": text[:200],  # İlk 200 karakter
            "emotion": analysis.primary_emotion.value,
            "intensity": analysis.intensity,
            "timestamp": time.time(),
            "topics": self.extract_topics(text)
        }
        self.conversation_memory.append(memory_entry)
        
        # Bellek sınırı
        if len(self.conversation_memory) > 50:
            self.conversation_memory = self.conversation_memory[-50:]
    
    def extract_topics(self, text: str) -> List[str]:
        """Metinden konuları çıkar"""
        topics = []
        text_lower = text.lower()
        
        topic_keywords = {
            "teknoloji": ["bilgisayar", "telefon", "yazılım", "internet", "wifi", "teknoloji"],
            "müzik": ["şarkı", "müzik", "albüm", "sanatçı", "çal", "dinle"],
            "film": ["film", "dizi", "netflix", "youtube", "izle", "video"],
            "spor": ["spor", "futbol", "maç", "takım", "oyun"],
            "eğitim": ["öğren", "okul", "ders", "çalış", "kitap"],
            "kişisel": ["aile", "arkadaş", "sevgi", "duygu", "mutlu", "üzgün"],
            "günlük": ["yemek", "uyku", "alışveriş", "plan", "program"]
        }
        
        for topic, keywords in topic_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                topics.append(topic)
        
        return topics[:3]
    
    def extract_linguistic_features(self, text: str) -> Dict[str, Any]:
        """Dilbilimsel özellikleri çıkar"""
        features = {
            "word_count": len(text.split()),
            "sentence_complexity": self.calculate_sentence_complexity(text),
            "emotional_words": self.find_emotional_words(text),
            "negations": self.count_negations(text),
            "intensifiers": self.find_intensifiers(text),
            "punctuation_pattern": self.analyze_punctuation(text),
            "capitalization_pattern": self.analyze_capitalization(text),
            "word_order_emotionality": self.analyze_word_order(text)
        }
        return features
    
    def find_emotional_words(self, text: str) -> List[Tuple[str, str]]:
        """Metindeki duygusal kelimeleri bul"""
        words = text.lower().split()
        emotional_words = []
        
        for word in words:
            for emotion_word, emotions in self.turkish_emotion_lexicon.items():
                if emotion_word in word:
                    for emotion in emotions.keys():
                        emotional_words.append((word, emotion))
        
        return emotional_words
    
    def count_negations(self, text: str) -> int:
        """Olumsuzluk ifadelerini say"""
        negations = ["değil", "yok", "hayır", "olmaz", "olmamış", "olmamalı", "değil mi"]
        count = 0
        for negation in negations:
            count += text.lower().count(negation)
        return count
    
    def find_intensifiers(self, text: str) -> List[str]:
        """Yoğunlaştırıcı kelimeleri bul"""
        intensifiers = ["çok", "aşırı", "fazla", "çokça", "son derece", "feci", "müthiş", "inanılmaz", "harika"]
        found = []
        for intensifier in intensifiers:
            if intensifier in text.lower():
                found.append(intensifier)
        return found
    
    def analyze_punctuation(self, text: str) -> Dict[str, int]:
        """Noktalama işaretlerini analiz et"""
        return {
            "exclamation": text.count("!"),
            "question": text.count("?"),
            "ellipsis": text.count("..."),
            "period": text.count(".")
        }
    
    def analyze_capitalization(self, text: str) -> Dict[str, Any]:
        """Büyük harf kullanımını analiz et"""
        if not text.strip():
            return {"capital_ratio": 0, "has_all_caps": False}
        
        words = text.split()
        if not words:
            return {"capital_ratio": 0, "has_all_caps": False}
        
        capital_count = sum(1 for word in words if word.isupper())
        return {
            "capital_ratio": capital_count / len(words),
            "has_all_caps": any(word.isupper() for word in words)
        }
    
    def analyze_word_order(self, text: str) -> float:
        """Kelime sırasının duygusal etkisini analiz et"""
        emotional_first_words = ["keşke", "keşki", "ah", "vah", "off", "eyvah", "aman", "lütfen"]
        words = text.lower().split()
        if words and words[0] in emotional_first_words:
            return 0.8
        return 0.3
    
    def calculate_sentence_complexity(self, text: str) -> float:
        """Cümle karmaşıklığını hesapla"""
        sentences = [s.strip() for s in text.split('.') if s.strip()]
        if not sentences:
            return 0.0
        
        avg_words = sum(len(s.split()) for s in sentences) / len(sentences)
        return min(avg_words / 20, 1.0)  # 0-1 arası normalize
    
    def emotion_lexicon_matching(self, text: str) -> Dict[str, float]:
        """Duygu sözlüğü eşleştirmesi"""
        text_lower = text.lower()
        emotion_scores = {emotion.value: 0.0 for emotion in Emotion}
        
        for word, emotions in self.turkish_emotion_lexicon.items():
            if word in text_lower:
                for emotion, score in emotions.items():
                    try:
                        # Emotion enum değerine çevir
                        emotion_enum = next(e for e in Emotion if e.value == emotion)
                        emotion_scores[emotion_enum.value] += score
                    except (ValueError, StopIteration):
                        # Eğer eşleşme yoksa devam et
                        pass
        
        # Normalize scores
        total = sum(emotion_scores.values())
        if total > 0:
            emotion_scores = {k: v/total for k, v in emotion_scores.items()}
        
        return emotion_scores
    
    def analyze_semantics(self, text: str) -> Dict[str, float]:
        """Semantik analiz yap"""
        semantic_scores = {}
        
        # İroni tespiti
        irony_indicators = ["müthiş", "harika", "süper", "çok güzel"]
        has_irony = any(indicator in text.lower() for indicator in irony_indicators) and \
                   any(neg in text.lower() for neg in ["değil", "yok", "ama", "fakat"])
        
        semantic_scores["irony"] = 0.8 if has_irony else 0.0
        
        # Sarcasm detection
        sarcasm_patterns = ["tabi canım", "elbette", "ne sandın", "tabii ki"]
        has_sarcasm = any(pattern in text.lower() for pattern in sarcasm_patterns)
        semantic_scores["sarcasm"] = 0.9 if has_sarcasm else 0.0
        
        # Metaphor detection
        metaphor_indicators = ["kalbim", "ruhum", "içim", "derin", "yürek"]
        metaphor_count = sum(1 for indicator in metaphor_indicators if indicator in text.lower())
        semantic_scores["metaphor"] = min(metaphor_count * 0.2, 1.0)
        
        return semantic_scores
    
    def evaluate_context(self, text: str, context: Dict) -> Dict[str, float]:
        """Bağlamsal değerlendirme yap"""
        context_scores = {}
        
        # Zaman bağlamı
        hour = datetime.datetime.now().hour
        if 22 <= hour <= 6:  # Gece saatleri
            context_scores["night_time"] = 0.7
            context_scores["emotional_vulnerability"] = 0.6
        else:
            context_scores["day_time"] = 0.7
        
        # Sosyal bağlam
        if any(word in text.lower() for word in ["video", "müzik", "şarkı", "film"]):
            context_scores["entertainment_context"] = 0.8
        
        if any(word in text.lower() for word in ["yardım", "problem", "sorun", "hata"]):
            context_scores["problem_solving_context"] = 0.9
        
        # Geçmiş etkileşimler
        if self.emotion_history:
            last_emotion = self.emotion_history[-1].primary_emotion
            if last_emotion == Emotion.SADNESS:
                context_scores["recent_sadness"] = 0.6
        
        return context_scores
    
    def multi_layer_classification(self, linguistic_features, semantic_scores, 
                                  emotion_scores, context_scores) -> EmotionalState:
        """Çok katmanlı duygu sınıflandırma"""
        
        # 1. Temel duygu skorlarını hesapla
        weighted_scores = {}
        
        for emotion_value, score in emotion_scores.items():
            if score == 0:
                continue
                
            # Dilbilimsel özelliklerle ağırlıklandır
            linguistic_weight = 1.0
            if linguistic_features["word_count"] > 10:
                linguistic_weight *= 1.2
            if linguistic_features["negations"] > 0:
                # Olumsuzluk varsa üzüntü/öfke ağırlığını artır
                if emotion_value in [Emotion.SADNESS.value, Emotion.ANGER.value, Emotion.FEAR.value]:
                    linguistic_weight *= 1.3
            
            # Bağlamsal ağırlıklandırma
            context_weight = 1.0
            if "night_time" in context_scores and context_scores["night_time"] > 0.5:
                if emotion_value in [Emotion.SADNESS.value, Emotion.FEAR.value]:
                    context_weight *= 1.4
            
            weighted_scores[emotion_value] = score * linguistic_weight * context_weight
        
        # Eğer hiç skor yoksa, nötr döndür
        if not weighted_scores:
            return EmotionalState(
                primary_emotion=Emotion.NEUTRAL,
                secondary_emotions=[],
                intensity=0.1,
                confidence=0.5,
                triggers=[],
                context_score=context_scores,
                timestamp=time.time()
            )
        
        # 2. Birincil duyguyu belirle
        primary_emotion_value = max(weighted_scores, key=weighted_scores.get)
        try:
            primary_emotion = Emotion(primary_emotion_value)
        except ValueError:
            primary_emotion = Emotion.NEUTRAL
        
        # 3. İkincil duyguları belirle
        sorted_emotions = sorted(weighted_scores.items(), key=lambda x: x[1], reverse=True)
        secondary_emotions = []
        
        for emotion_value, score in sorted_emotions[1:4]:  # İlk 3 ikincil duygu
            if score > 0.1:  # Eşik değeri
                try:
                    emotion = Emotion(emotion_value)
                    if emotion != primary_emotion:
                        secondary_emotions.append(emotion)
                except ValueError:
                    continue
        
        # 4. Yoğunluk hesapla
        intensity = min(weighted_scores[primary_emotion_value] * 1.5, 1.0)
        
        # 5. Güven skoru hesapla
        confidence = self.calculate_confidence(
            linguistic_features, 
            semantic_scores, 
            max(weighted_scores.values())
        )
        
        # 6. Tetikleyicileri belirle
        triggers = linguistic_features["emotional_words"]
        trigger_words = [word for word, _ in triggers[:3]] if triggers else []  # İlk 3 tetikleyici
        
        return EmotionalState(
            primary_emotion=primary_emotion,
            secondary_emotions=secondary_emotions,
            intensity=intensity,
            confidence=confidence,
            triggers=trigger_words,
            context_score=context_scores,
            timestamp=time.time()
        )
    
    def calculate_confidence(self, linguistic_features, semantic_scores, max_emotion_score) -> float:
        """Analiz güven skorunu hesapla"""
        confidence = max_emotion_score
        
        # Dilbilimsel güven faktörleri
        if linguistic_features["word_count"] >= 5:
            confidence *= 1.1
        else:
            confidence *= 0.7  # Çok kısa metinlerde güven az
        
        # Semantik güven faktörleri
        if semantic_scores.get("irony", 0) > 0.5:
            confidence *= 0.6  # İroni varsa güven azalır
        
        return min(confidence, 1.0)
    
    def integrate_historical_context(self, current_analysis: EmotionalState) -> EmotionalState:
        """Tarihsel bağlamı entegre et"""
        if not self.emotion_history:
            return current_analysis
        
        # Son 5 analizi al
        recent_history = self.emotion_history[-5:]
        
        # Duygu trendini analiz et
        emotion_counts = {}
        for analysis in recent_history:
            emotion = analysis.primary_emotion
            emotion_counts[emotion] = emotion_counts.get(emotion, 0) + 1
        
        # Eğer belirgin bir trend varsa, bunu dikkate al
        if len(recent_history) >= 3:
            most_common_emotion = max(emotion_counts, key=emotion_counts.get)
            if emotion_counts[most_common_emotion] >= len(recent_history) * 0.6:
                # Trendi güçlendir
                if current_analysis.primary_emotion == most_common_emotion:
                    current_analysis.intensity = min(current_analysis.intensity * 1.2, 1.0)
        
        return current_analysis
    
    def self_correcting_analysis(self, analysis: EmotionalState) -> EmotionalState:
        """Kendini düzelten analiz"""
        # Eğer çok düşük güven varsa, nötr duyguya yaklaştır
        if analysis.confidence < 0.3:
            analysis.primary_emotion = Emotion.NEUTRAL
            analysis.intensity *= 0.5
            analysis.confidence = 0.5
        
        # Çelişkili duyguları kontrol et
        if (analysis.primary_emotion == Emotion.JOY and 
            Emotion.SADNESS in analysis.secondary_emotions and
            analysis.intensity > 0.7):
            # Acı tatlı durum - yoğunluğu ayarla
            analysis.intensity = min(analysis.intensity * 0.8, 0.9)
        
        return analysis
    
    def update_user_profile(self, analysis: EmotionalState):
        """Kullanıcı profilini güncelle"""
        emotion_name = analysis.primary_emotion.value
        
        if "emotion_patterns" not in self.user_profile:
            self.user_profile["emotion_patterns"] = {}
        
        if emotion_name not in self.user_profile["emotion_patterns"]:
            self.user_profile["emotion_patterns"][emotion_name] = 0
        
        self.user_profile["emotion_patterns"][emotion_name] += 1
        
        # Duygu yoğunluk ortalamasını güncelle
        if "intensity_history" not in self.user_profile:
            self.user_profile["intensity_history"] = []
        
        self.user_profile["intensity_history"].append(analysis.intensity)
        
        # Son 10 ortalamayı hesapla
        recent_intensities = self.user_profile["intensity_history"][-10:]
        if recent_intensities:
            self.user_profile["avg_intensity"] = sum(recent_intensities) / len(recent_intensities)
        else:
            self.user_profile["avg_intensity"] = 0
    
    def generate_emotional_response(self, analysis: EmotionalState, original_command: str) -> str:
        """Duygu analizine göre akıllı yanıt oluştur"""
        
        response_templates = {
            Emotion.JOY: [
                "Neşeni hissediyorum, bu çok güzel!",
                "Mutluluğun bulaşıcı, seninle aynı enerjiyi paylaşmak harika!",
                "Bu neşe dolu anı paylaştığın için teşekkürler!"
            ],
            Emotion.SADNESS: [
                "Üzgün olduğunu hissediyorum. Yanındayım, istersen konuşabiliriz.",
                "Bu duyguyu anlıyorum. Bazen her şey zor gelebilir.",
                "Senin için buradayım. Bu duygu geçecek, birlikte atlatacağiz."
            ],
            Emotion.ANGER: [
                "Öfkeni anlıyorum. Sakin nefes al, yanındayım.",
                "Bu durumda öfkelenmek normal. Duygularını ifade etmek önemli.",
                "Öfkeni dinliyorum. Birlikte çözüm bulabiliriz."
            ],
            Emotion.FEAR: [
                "Korkunu hissediyorum. Güvendesin, yanındayım.",
                "Endişelenme, bu duygu geçecek. Seninleyim.",
                "Korkuların normal, birlikte üstesinden geleceğiz."
            ],
            Emotion.LOVE: [
                "Sevgi dolu olduğunu hissediyorum, bu çok değerli!",
                "Sevginin enerjisi harika! Bunu paylaştığın için teşekkürler.",
                "Sevgi dolu anlar hayatın en güzel yanı."
            ],
            Emotion.GRATITUDE: [
                "Minnettarlığın çok değerli. Sen de çok değerlisin.",
                "Minnettarlık duygusu harika! Ben de sana minnettarım.",
                "Bu minnettarlık hissi çok güzel, teşekkür ederim."
            ],
            Emotion.NEUTRAL: [
                "Anlıyorum.",
                "Tamam.",
                "Peki."
            ]
        }
        
        # Yoğunluğa göre tepkiyi ayarla
        intensity_modifier = ""
        if analysis.intensity > 0.8:
            intensity_modifier = " Bu duygu çok güçlü görünüyor."
        elif analysis.intensity < 0.3:
            intensity_modifier = " Bu duygu hafif görünüyor."
        
        # Birincil duygu için şablon seç
        if analysis.primary_emotion in response_templates:
            templates = response_templates[analysis.primary_emotion]
            response = random.choice(templates)
        else:
            response = "Anlıyorum."
        
        # Yoğunluk modifikatörünü ekle
        response += intensity_modifier
        
        # Eğer karmaşık duygu varsa, buna da değin
        if len(analysis.secondary_emotions) > 0 and analysis.intensity > 0.5:
            secondary_str = ", ".join([e.value for e in analysis.secondary_emotions[:2]])
            response += f" Ayrıca {secondary_str} hissettiğini de fark ettim."
        
        return response
    
    # YENİ METOTLAR: AKILLI SORU SORMA VE DÜŞÜNME
    
    def generate_intelligent_question(self, user_input: str) -> Optional[str]:
        """Akıllı soru üret"""
        
        # Duygu analizi yap
        emotion_analysis = self.analyze_with_context(user_input)
        
        # Konu analizi
        topics = self.extract_topics(user_input)
        
        # Eğer konuşma belleği boşsa veya ilk konuşmalardaysa
        if len(self.conversation_memory) < 3:
            return self.generate_opening_question()
        
        # Merak seviyesine göre soru sorma kararı
        if random.random() > self.curiosity_level:
            return None
        
        # Duyguya göre soru tipi seç
        question_type = self.select_question_type(emotion_analysis, topics)
        
        # Soru oluştur
        question = self.create_question(user_input, question_type, topics)
        
        if question:
            self.question_count += 1
        
        return question
    
    def generate_opening_question(self) -> str:
        """Açılış sorusu üret"""
        opening_questions = [
            "Size nasıl yardımcı olabilirim?",
            "Bugün nasılsınız?",
            "Merak ettiğiniz bir konu var mı?",
            "Sohbet etmek istediğiniz bir şey var mı?",
            "Size ne hakkında soru sormamı istersiniz?"
        ]
        return random.choice(opening_questions)
    
    def select_question_type(self, analysis: EmotionalState, topics: List[str]) -> str:
        """Soru tipi seç"""
        
        if analysis.primary_emotion in [Emotion.SADNESS, Emotion.ANGER, Emotion.FEAR]:
            return "emotional"
        elif "?" in analysis.triggers or any(t in ["merak", "öğrenmek"] for t in topics):
            return "curiosity"
        elif len(topics) > 0:
            return "deep_thinking"
        else:
            return "reflective"
    
    def create_question(self, user_input: str, question_type: str, topics: List[str]) -> str:
        """Soru oluştur"""
        
        if question_type not in self.question_templates:
            question_type = "deep_thinking"
        
        template = random.choice(self.question_templates[question_type])
        
        # Konuya göre kişiselleştir
        if topics:
            topic = random.choice(topics)
            template = template.replace("[konu]", topic)
        
        # Önceki konuşmalardan referans
        if self.conversation_memory and random.random() < 0.3:
            prev_memory = random.choice(self.conversation_memory[-3:])
            if "konu" in prev_memory["topics"]:
                template += f" Daha önce {prev_memory['topics'][0]} hakkında konuşmuştuk."
        
        return template
    
    def generate_reflective_response(self, user_input: str) -> str:
        """Yansıtıcı yanıt oluştur"""
        
        # Önceki konuşmaları analiz et
        if len(self.conversation_memory) > 5:
            # Ortak konuları bul
            all_topics = []
            for memory in self.conversation_memory[-5:]:
                all_topics.extend(memory.get("topics", []))
            
            if all_topics:
                from collections import Counter
                topic_counts = Counter(all_topics)
                common_topic = topic_counts.most_common(1)[0][0] if topic_counts else None
                
                if common_topic:
                    reflections = [
                        f"Son zamanlarda {common_topic} hakkında çok konuşuyoruz.",
                        f"{common_topic} konusu size önemli görünüyor.",
                        f"{common_topic} hakkında konuşmak bana ilginç geliyor."
                    ]
                    return random.choice(reflections)
        
        return ""
    
    def get_conversation_summary(self) -> Dict[str, Any]:
        """Konuşma özetini al"""
        if not self.conversation_memory:
            return {"status": "no_data"}
        
        # Son 10 konuşmayı analiz et
        recent_memories = self.conversation_memory[-10:] if len(self.conversation_memory) > 10 else self.conversation_memory
        
        # Konu analizi
        all_topics = []
        for memory in recent_memories:
            all_topics.extend(memory.get("topics", []))
        
        # Duygu analizi
        emotions = [memory.get("emotion", "nötr") for memory in recent_memories]
        
        from collections import Counter
        topic_counts = Counter(all_topics)
        emotion_counts = Counter(emotions)
        
        return {
            "total_conversations": len(self.conversation_memory),
            "recent_topics": topic_counts.most_common(3),
            "recent_emotions": emotion_counts.most_common(3),
            "questions_asked": self.question_count,
            "conversation_depth": len(self.conversation_memory) // 10  # Her 10 konuşmada 1 derinlik
        }
    
    def get_emotion_summary(self) -> Dict[str, Any]:
        """Duygu analizi özetini döndür"""
        if not self.emotion_history:
            return {"status": "no_data", "message": "Henüz analiz yapılmadı."}
        
        recent_analyses = self.emotion_history[-10:]  # Son 10 analiz
        
        summary = {
            "total_analyses": len(self.emotion_history),
            "recent_emotions": [
                {
                    "emotion": analysis.primary_emotion.value,
                    "intensity": analysis.intensity,
                    "time": datetime.datetime.fromtimestamp(analysis.timestamp).strftime('%H:%M:%S')
                }
                for analysis in recent_analyses
            ],
            "most_common_emotion": self._get_most_common_emotion(),
            "emotional_patterns": self.user_profile.get("emotion_patterns", {}),
            "avg_emotional_intensity": self.user_profile.get("avg_intensity", 0),
            "emotional_stability_score": self._calculate_emotional_stability()
        }
        
        return summary
    
    def _get_most_common_emotion(self) -> str:
        """En sık görülen duyguyu bul"""
        if not self.emotion_history:
            return "bilinmiyor"
        
        emotion_counts = {}
        for analysis in self.emotion_history:
            emotion = analysis.primary_emotion.value
            emotion_counts[emotion] = emotion_counts.get(emotion, 0) + 1
        
        if emotion_counts:
            return max(emotion_counts, key=emotion_counts.get)
        return "bilinmiyor"
    
    def _calculate_emotional_stability(self) -> float:
        """Duygusal stabilite skorunu hesapla"""
        if len(self.emotion_history) < 3:
            return 0.5
        
        recent_emotions = [analysis.primary_emotion for analysis in self.emotion_history[-5:]]
        
        # Aynı duygu ne kadar süre devam etti?
        changes = 0
        for i in range(1, len(recent_emotions)):
            if recent_emotions[i] != recent_emotions[i-1]:
                changes += 1
        
        stability = 1.0 - (changes / (len(recent_emotions) - 1))
        return stability

# ==================== GÜNCELLENMİŞ JARVIS SINIFI ====================

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
        
        # YENİ: Akıllı özellikler
        self.keyboard_mode = False
        self.deep_think_mode = True  # YENİ: Derin düşünme modu
        self.auto_question_mode = True  # YENİ: Otomatik soru sorma modu
        self.conversation_depth = 0  # YENİ: Konuşma derinliği
        self.last_question_time = 0  # YENİ: Son soru zamanı
        
        # SEVİYE 5 DUYGU ANALİZİ SİSTEMİ EKLENDİ (GÜNCELLENMİŞ)
        self.emotion_analyzer = Level5EmotionAnalyzer()
        self.last_emotion_response_time = 0
        self.emotion_aware_mode = True  # Duygu farkındalık modu
        
        # Ses tanıma ayarları - daha toleranslı
        self.recognizer.energy_threshold = 300
        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.pause_threshold = 0.8
        
        # Veri listeleri
        self.favorite_youtubers = [
            "Enes Batur", "Ruhi Çenet", "Barış Özcan", "Lütfi Şahin",
            "Bebar Bilim", "Evrim Ağacı", "Teknofil", "Vogue Türkiye"
        ]
        
        self.motivational_quotes = [
            "Harika iş çıkarıyorsun, seninle gurur duyuyorum!",
            "İnanılmaz bir enerjin var, bu seni başarıya götürecek!",
            "Yapabileceğine inanıyorsun, değil mi? Çünkü ben inanıyorum!",
            "Bugün harika bir gün olacak, buna eminim!",
            "Çalışmaların gerçekten takdire şayan, böyle devam et!"
        ]
        
        self.daily_questions = [
            "Bugün kendin için ne iyi bir şey yaptın?",
            "Bugün en çok neye minnettar hissediyorsun?",
            "Bugün öğrendiğin en ilginç şey neydi?",
            "Yarın için en büyük hedefin nedir?",
            "Bugün kendinle gurur duydun mu?"
        ]
        
        self.sleep_conversation_questions = [
            "Nasılsın? Bugün neler yaptın?",
            "Seninle konuşmak güzel, bana biraz kendinden bahseder misin?",
            "Bugün en sevdiğin an neydi?",
            "Hayatında en çok neye değer veriyorsun?",
            "Yakın zamanda öğrendiğin ilginç bir şey var mı?"
        ]

        self.smart_responses = {
            "selam": "Aleyküm selam", 
            "nasılsın": "Teşekkür ederim, ben iyiyim. Siz nasılsınız?",
            "sen kimsin": "Ben JARVIS, size yardımcı olmak için buradayım!",
            "ne yapıyorsun": "Sizi dinliyorum ve komutlarınızı bekliyorum!",
            "teşekkür ederim": "Rica ederim, her zaman yanınızdayım!",
            "sağ ol": "Ne demek, ben buradayım!",
            "günaydın": "Günaydın! Harika bir gün geçirmenizi diliyorum!",
            "iyi geceler": "İyi geceler! Tatlı rüyalar!",
            "ne haber": "Her şey yolunda, sizden haber bekliyorum!"
        }
        
        # YENİ: Akıllı sorular
        self.intelligent_questions = [
            "Bu konu hakkında ne düşünüyorsunuz?",
            "Bana bu konuda daha fazla anlatır mısınız?",
            "Bu size nasıl hissettiriyor?",
            "Bu fikrinizi neyin etkilediğini düşünüyorsunuz?",
            "Bu konuda merak ettiğiniz başka bir şey var mı?",
            "Bu deneyim size ne öğretti?",
            "Bu konu hakkındaki görüşleriniz zamanla değişti mi?",
            "Bana bu konuda bir şey öğretir misiniz?",
            "Bunu nasıl keşfettiniz?",
            "Size bunun hakkında ne ilginç geliyor?"
        ]
        
        pygame.mixer.init()
    
    # YENİ METOT: Akıllı soru sorma
    def ask_intelligent_question(self, user_input: str = "") -> Optional[str]:
        """Akıllı soru sor"""
        
        # Otomatik soru modu kapalıysa
        if not self.auto_question_mode:
            return None
        
        # Çok sık soru sorma (en az 30 saniye ara)
        current_time = time.time()
        if current_time - self.last_question_time < 30:
            return None
        
        # Rastgele soru sorma şansı (%40)
        if random.random() > 0.4:
            return None
        
        # Eğer kullanıcı girdisi varsa, ona göre soru üret
        if user_input and len(user_input) > 5:
            question = self.emotion_analyzer.generate_intelligent_question(user_input)
            if question:
                self.last_question_time = current_time
                return question
        
        # Genel sorular
        questions = [
            "Size nasıl yardımcı olabilirim?",
            "Merak ettiğiniz bir konu var mı?",
            "Bugün nasılsınız?",
            "Size ne hakkında soru sormamı istersiniz?",
            "Benimle paylaşmak istediğiniz bir şey var mı?"
        ]
        
        self.last_question_time = current_time
        return random.choice(questions)
    
    # YENİ METOT: Derin düşünme yanıtı
    def generate_deep_response(self, user_input: str) -> str:
        """Derin düşünme yanıtı oluştur"""
        
        # Derin düşünme modu kapalıysa
        if not self.deep_think_mode:
            return ""
        
        # Yansıtıcı yanıt oluştur
        reflective_response = self.emotion_analyzer.generate_reflective_response(user_input)
        if reflective_response:
            return reflective_response
        
        # Konuşma özeti
        summary = self.emotion_analyzer.get_conversation_summary()
        if summary.get("status") != "no_data" and summary.get("conversation_depth", 0) > 1:
            if summary.get("recent_topics"):
                topic = summary["recent_topics"][0][0] if summary["recent_topics"] else "konuşmalarımız"
                responses = [
                    f"Son zamanlarda {topic} hakkında çok konuşuyoruz.",
                    f"{topic} konusundaki sohbetimiz ilginç.",
                    f"{topic} hakkında konuşmak bana ilginç geliyor."
                ]
                return random.choice(responses)
        
        return ""
    
    # YENİ METOT: Konuşma analizi
    def analyze_conversation(self):
        """Konuşma analizi yap"""
        summary = self.emotion_analyzer.get_conversation_summary()
        
        if summary.get("status") == "no_data":
            return "Henüz yeterli konuşma verisi yok."
        
        response = f"Toplam {summary['total_conversations']} konuşma yaptık. "
        
        if summary.get('recent_topics'):
            topics_str = ", ".join([f"{topic}" for topic, count in summary['recent_topics'][:2]])
            response += f"Son zamanlarda {topics_str} hakkında konuşuyoruz. "
        
        if summary.get('questions_asked', 0) > 0:
            response += f"Size {summary['questions_asked']} soru sordum. "
        
        return response
    
    def check_microphone(self):
        """Mikrofon kontrolü yap"""
        try:
            print("🔍 Mikrofon kontrol ediliyor...")
            with sr.Microphone() as source:
                print("✅ Mikrofon bulundu")
                return True
        except Exception as e:
            print(f"❌ Mikrofon hatası: {e}")
            print("💡 Klavye giriş modu aktifleştiriliyor...")
            self.keyboard_mode = True
            return False
    
    def get_keyboard_input(self):
        """Klavyeden komut al"""
        try:
            print("\n⌨️  Komut girin (çıkmak için 'q' yazın): ", end="", flush=True)
            command = input().strip().lower()
            if command == 'q':
                return ""
            return command
        except Exception as e:
            print(f"Klavye giriş hatası: {e}")
            return ""
    
    def speak(self, text):
        """Metni sesli söyle"""
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
            print(f"🤖 JARVIS: {text}")

    def listen(self):
        """Mikrofonla ses dinle"""
        try:
            with sr.Microphone() as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                
                try:
                    print("🎤 Dinliyorum... (konuşun)")
                    audio = self.recognizer.listen(
                        source, 
                        timeout=5,
                        phrase_time_limit=7
                    )
                    command = self.recognizer.recognize_google(audio, language='tr-TR')
                    print(f"👤 Siz: {command}")
                    return command.lower()
                except sr.WaitTimeoutError:
                    return ""
                except sr.UnknownValueError:
                    print("❌ Sesi anlayamadım")
                    return ""
                except sr.RequestError as e:
                    print(f"🌐 İnternet bağlantı hatası: {e}")
                    return ""
        except Exception as e:
            print(f"🎤 Mikrofon hatası: {e}")
            self.keyboard_mode = True
            return ""

    # ==================== MEVCUT METOTLAR ====================
    
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
        self.speak("Google'da ne aramamı istersiniz?")
        self.waiting_for_search = True

    def close_and_switch_tab(self):
        """Sekmeyi kapat ve diğerine geç"""
        try:
            pyautogui.hotkey('ctrl', 'w')
            time.sleep(0.2)
            pyautogui.hotkey('ctrl', 'tab')
            self.speak("Sekme kapatıldı ve diğer sekmeye geçildi")
        except Exception:
            self.speak("Sekme değiştirilemedi")

    def ask_youtuber(self):
        """Hangi youtuber istediğini sor"""
        youtuber_list = ", ".join(self.favorite_youtubers[:3])
        self.speak(f"Hangi youtuber'ın videosunu izlemek istersiniz? Örneğin: {youtuber_list}")
        self.waiting_for_youtuber = True

    def play_youtuber_video(self, youtuber_name):
        """Youtuber videosu aç"""
        youtuber_clean = youtuber_name.replace(' ', '+')
        url = f"https://www.youtube.com/results?search_query={youtuber_clean}"
        webbrowser.open(url)
        self.speak(f"{youtuber_name} videoları açılıyor")

    def play_youtube_song(self, song_name):
        """YouTube'dan şarkı aç"""
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
        
        if hour < 10:
            hour_str = f"sıfır {hour}"
        else:
            hour_str = str(hour)
        
        if minute < 10:
            minute_str = f"sıfır {minute}"
        else:
            minute_str = str(minute)
            
        time_text = f"Saat {hour_str} {minute_str}"
        self.speak(time_text)
        return time_text

    def get_weather(self, city="İskenderun"):
        """Hava durumu bilgisini al"""
        try:
            conditions = ["açık", "parçalı bulutlu", "bulutlu", "güneşli"]
            temps = [18, 20, 22, 25]
            condition = random.choice(conditions)
            temp = random.choice(temps)
            weather_text = f"{city} için hava durumu: {condition}, sıcaklık {temp} derece"
                
            self.speak(weather_text)
            return weather_text
            
        except Exception:
            error_text = "Hava durumu bilgisi alınamadı"
            self.speak(error_text)
            return error_text

    def pause_music(self):
        """Müziği duraklat"""
        try:
            pyautogui.press('space')
            self.music_playing = False
            self.speak("Müzik duraklatıldı")
        except Exception:
            self.speak("Müzik duraklatılamadı")

    def resume_music(self):
        """Müziği devam ettir"""
        try:
            pyautogui.press('space')
            self.music_playing = True
            self.speak("Müzik devam ediyor")
        except Exception:
            self.speak("Müzik devam ettirilemedi")

    def next_track(self):
        """Sonraki şarkı"""
        try:
            if self.current_platform == "youtube":
                pyautogui.hotkey('shift', 'n')
            elif self.current_platform == "spotify":
                pyautogui.hotkey('ctrl', 'right')
            else:
                pyautogui.press('nexttrack')
                
            self.speak("Sonraki şarkıya geçiliyor")
        except Exception:
            self.speak("Şarkı değiştirilemedi")

    def previous_track(self):
        """Önceki şarkı"""
        try:
            if self.current_platform == "youtube":
                pyautogui.hotkey('shift', 'p')
            elif self.current_platform == "spotify":
                pyautogui.hotkey('ctrl', 'left')
            else:
                pyautogui.press('prevtrack')
                
            self.speak("Önceki şarkıya geçiliyor")
        except Exception:
            self.speak("Şarkı değiştirilemedi")

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
        self.speak("Uyku moduna geçtim. Beni çağırmak için uyan demeniz yeterli.")
        
        def conversation_loop():
            time.sleep(2)
            while self.sleep_mode and self.sleep_conversation_active:
                question = random.choice(self.sleep_conversation_questions)
                self.speak(question)
                
                time.sleep(2)
                response = self.listen() if not self.keyboard_mode else self.get_keyboard_input()
                if response:
                    if any(word in response for word in ["hayır", "yeter", "dur", "sus", "kapat"]):
                        self.speak("Tamam, sessizce dinliyorum. Beni istediğin zaman çağırabilirsin.")
                        self.sleep_conversation_active = False
                    else:
                        if not self.smart_response(response):
                            friendly_responses = [
                                "Bu çok ilginç, devam edebilir misin?",
                                "Seni dinlemek gerçekten güzel",
                                "Bunu duyduğuma sevindim"
                            ]
                            response_text = random.choice(friendly_responses)
                            self.speak(response_text)
                
                time.sleep(random.randint(15, 30))
        
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
        if current_time - self.last_motivation_time > 1800:  # 30 dakika
            if random.random() < 0.3:
                self.motivate_user()

    def ask_platform(self):
        """Platform sorma"""
        self.speak("Hangi platformda açayım? YouTube veya Spotify?")
        self.waiting_for_platform = True

    def ask_song(self):
        """Şarkı sorma"""
        self.speak("Hangi şarkıyı çalmamı istersiniz?")
        self.waiting_for_song = True

    def ask_youtube_song(self):
        """YouTube için şarkı sorma"""
        self.speak("YouTube'da hangi şarkıyı açmamı istersiniz?")
        self.waiting_for_song = True

    def ask_spell(self):
        """Heceleme için metin sor"""
        self.speak("Hangi metni hecelememi istersiniz?")
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
    
    def get_welcome_message(self):
        """Günün saatine göre hoşgeldin mesajı"""
        hour = datetime.datetime.now().hour
        
        if 5 <= hour < 12:
            return "Günaydın efendim! Yeni bir güne başlamak için harika bir zaman!"
        elif 12 <= hour < 17:
            return "Tünaydın efendim! Gününüz nasıl geçiyor?"
        elif 17 <= hour < 22:
            return "İyi akşamlar efendim! Günün yorgunluğunu atmaya hazır mısınız?"
        else:
            return "İyi geceler efendim! Hala burada olmanız harika!"
    
    # YENİ METOT: Spotify direkt açma
    def open_spotify_direct(self):
        """Spotify'ı direkt aç"""
        self.speak("Spotify açılıyor")
        webbrowser.open("https://open.spotify.com")
    
    # YENİ METOT: YouTube direkt açma
    def open_youtube_direct(self):
        """YouTube'u direkt aç"""
        self.speak("YouTube açılıyor")
        webbrowser.open("https://www.youtube.com")
    
    # ==================== GÜNCELLENMİŞ EXECUTE_COMMAND ====================
    
    def execute_command(self, command):
        """Komutu çalıştır - AKILLI SORU SORMA ENTEGRE EDİLDİ"""
        
        # Boş komut kontrolü
        if not command or len(command.strip()) < 2:
            return True
        
        # YENİ: Spotify aç komutu - EN BAŞTA
        if any(word in command for word in ["spotify aç", "spotify'ı aç", "spotify'ı başlat"]):
            self.open_spotify_direct()
            return True
            
        # YENİ: YouTube aç komutu - EN BAŞTA
        if any(word in command for word in ["youtube aç", "youtube'u aç", "youtube'u başlat"]):
            self.open_youtube_direct()
            return True
        
        # YENİ: Haberler aç komutu - EN BAŞTA
        if any(word in command for word in ["haberleri aç", "haber oku", "haberler"]):
            self.open_news()
            return True
        
        # DUYGU ANALİZİ ENTEGRASYONU (SEVİYE 5)
        if self.emotion_aware_mode:
            emotional_response, emotion_analysis = self.analyze_emotion_in_text(command)
            
            # Eğer güçlü bir duygu tespit edildiyse ve son 2 dakikada yanıt vermediysek
            current_time = time.time()
            if (emotion_analysis and 
                emotion_analysis.intensity > 0.5 and 
                emotion_analysis.confidence > 0.6 and
                (current_time - self.last_emotion_response_time) > 120):
                
                # Duyguya özel yanıt ver
                if emotional_response:
                    self.speak(emotional_response)
                    self.last_emotion_response_time = current_time
                    
                    # Özellikle olumsuz duygular için ek destek
                    if emotion_analysis.primary_emotion in [Emotion.SADNESS, Emotion.ANGER, Emotion.FEAR]:
                        support_responses = [
                            "Bu duyguyu hissetmek normal, yanındayım.",
                            "Duyguların değerli, onları dinlemek önemli.",
                            "Her duygu geçici, bu da geçecek."
                        ]
                        self.speak(random.choice(support_responses))
        
        # Güvenlik modu kontrolü
        if self.security_mode:
            if any(word in command for word in ["güvenlik kapat", "güvenlik modu kapat"]):
                self.security_mode_off()
                return True
            else:
                self.speak("Güvenlik modu aktif. Sadece güvenlik komutları çalışıyor.")
                return True
        
        # Akıllı cevap kontrolü
        if self.smart_response(command):
            # YENİ: Akıllı soru sor
            question = self.ask_intelligent_question(command)
            if question:
                time.sleep(1)
                self.speak(question)
            return True
        
        # Uyku modu kontrolü
        if self.sleep_mode:
            if any(word in command for word in ["uyan", "merhaba", "jarvis"]):
                self.sleep_mode = False
                self.sleep_conversation_active = False
                self.speak("Uyandım! Seni özlemiştim. Nasılsın?")
                return True
            else:
                return True
        
        # Google arama bekleniyorsa
        if self.waiting_for_search:
            self.waiting_for_search = False
            self.google_search(command)
            
            # YENİ: Arama sonrası soru
            if self.auto_question_mode and random.random() < 0.3:
                time.sleep(2)
                follow_up_questions = [
                    "Bu konu hakkında başka ne öğrenmek istersiniz?",
                    "Aradığınızı bulabildiniz mi?",
                    "Bu konuda size başka nasıl yardımcı olabilirim?"
                ]
                self.speak(random.choice(follow_up_questions))
                
            return True
            
        # YENİ KOMUT: Derin düşünme modu
        if any(word in command for word in ["derin düşünme", "akıllı mod", "düşünme modu"]):
            if "aç" in command:
                self.deep_think_mode = True
                self.speak("Derin düşünme modu açık. Size daha akıllı sorular soracağım.")
            elif "kapat" in command:
                self.deep_think_mode = False
                self.speak("Derin düşünme modu kapalı.")
            else:
                self.deep_think_mode = not self.deep_think_mode
                status = "açık" if self.deep_think_mode else "kapalı"
                self.speak(f"Derin düşünme modu {status}.")
            return True
        
        # YENİ KOMUT: Soru modu
        if any(word in command for word in ["soru modu", "soru sorma"]):
            if "aç" in command:
                self.auto_question_mode = True
                self.speak("Otomatik soru sorma modu açık. Size daha çok soru soracağım.")
            elif "kapat" in command:
                self.auto_question_mode = False
                self.speak("Otomatik soru sorma modu kapalı.")
            else:
                self.auto_question_mode = not self.auto_question_mode
                status = "açık" if self.auto_question_mode else "kapalı"
                self.speak(f"Otomatik soru sorma modu {status}.")
            return True
        
        # YENİ KOMUT: Bana soru sor
        if any(word in command for word in ["bana soru sor", "soru sor", "merak ettiğin"]):
            question = self.ask_intelligent_question(command)
            if question:
                self.speak(question)
            else:
                self.speak(random.choice(self.intelligent_questions))
            return True
        
        # YENİ KOMUT: Konuşma analizi
        if any(word in command for word in ["konuşma analizi", "ne konuştuk", "sohbet analizi"]):
            analysis = self.analyze_conversation()
            self.speak(analysis)
            
            # YENİ: Analiz sonrası soru
            if self.auto_question_mode:
                time.sleep(1)
                follow_up = random.choice([
                    "Bu analiz hakkında ne düşünüyorsunuz?",
                    "Size hangi konularda daha fazla yardımcı olabilirim?",
                    "Hangi konular hakkında daha çok konuşmak istersiniz?"
                ])
                self.speak(follow_up)
                
            return True
        
        # YENİ: Derin yanıt
        if self.deep_think_mode and len(command) > 10:
            deep_response = self.generate_deep_response(command)
            if deep_response and random.random() < 0.3:  # %30 şans
                self.speak(deep_response)
        
        # Duygu analizi özeti
        if any(word in command for word in ["duygu özet", "duygu analizi", "nasıl hissediyorum"]):
            summary = self.get_emotional_summary()
            
            if summary.get("status") == "no_data":
                self.speak("Henüz yeterli veri yok. Benimle biraz daha konuşun.")
            else:
                most_common = summary.get("most_common_emotion", "bilinmiyor")
                stability = summary.get("emotional_stability_score", 0.5)
                
                response = f"Son analizlerinize göre en sık {most_common} hissediyorsunuz. "
                if stability > 0.7:
                    response += "Duygusal dengeniz oldukça stabil."
                elif stability > 0.4:
                    response += "Duygusal dengeniz orta seviyede."
                else:
                    response += "Duygusal dalgalanmalar yaşıyorsunuz."
                
                self.speak(response)
                
                # YENİ: Duygu analizi sonrası soru
                if self.auto_question_mode:
                    time.sleep(1)
                    emotion_questions = [
                        "Bu duygusal durum hakkında ne düşünüyorsunuz?",
                        "Duygularınızı daha iyi anlamak için size nasıl yardımcı olabilirim?",
                        "Bu analiz size ne hissettirdi?"
                    ]
                    self.speak(random.choice(emotion_questions))
                    
            return True
        
        # Duygu modunu aç/kapat
        if any(word in command for word in ["duygu modu", "duygu farkındalık"]):
            if "aç" in command or "aktif" in command:
                response = self.toggle_emotion_aware_mode(True)
            elif "kapat" in command or "pasif" in command:
                response = self.toggle_emotion_aware_mode(False)
            else:
                response = self.toggle_emotion_aware_mode()
            
            self.speak(response)
            return True
        
        # Google arama komutları
        if any(word in command for word in ["google'da ara", "google ara", "arama yap"]):
            search_terms = ["google'da ara", "google ara", "arama yap"]
            
            search_query = command
            for term in search_terms:
                search_query = search_query.replace(term, "").strip()
            
            if search_query and len(search_query) > 2:
                self.google_search(search_query)
            else:
                self.ask_search()
            return True
        
        # Müzik duraklatma
        if any(word in command for word in ["duraklat", "müziği durdur", "şarkıyı durdur"]):
            self.pause_music()
            return True
            
        # Sekme değiştirme
        if any(word in command for word in ["sekme değiştir", "sekmeyi kapat ve geç"]):
            self.close_and_switch_tab()
            return True
            
        # Netflix
        if any(word in command for word in ["film aç", "netflix aç"]):
            self.open_netflix()
            return True
            
        # Haritalar
        if any(word in command for word in ["haritaları aç", "harita aç"]):
            self.open_maps()
            return True
        
        # YouTube şarkı
        if any(word in command for word in ["şarkıyı youtube dan aç", "youtube dan şarkı aç"]):
            self.ask_youtube_song()
            return True
        
        # Şarkı değiştir
        if any(word in command for word in ["şarkı değiştir", "müzik değiştir"]):
            self.next_track()
            return True
            
        # Video değiştir
        if any(word in command for word in ["video değiştir", "sonraki video"]):
            pyautogui.hotkey('shift', 'n')
            self.speak("Video değiştiriliyor")
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
        if self.waiting_for_song:
            self.waiting_for_song = False
            self.play_youtube_song(command)
            return True
            
        # YouTube youtuber komutu
        if any(word in command for word in ["video aç", "youtuber videosu aç"]):
            self.ask_youtuber()
            return True
        
        # YouTube tam ekran
        if any(word in command for word in ["tam ekran", "fullscreen"]):
            self.youtube_fullscreen()
            return True
            
        # Heceleme modu kontrolü
        if self.waiting_for_spell:
            self.waiting_for_spell = False
            self.spell_text(command)
            return True
            
        # Heceleme komutu
        if any(word in command for word in ["hecele", "heceleyerek oku"]):
            self.ask_spell()
            return True
        
        # Şarkı devam et
        if any(word in command for word in ["şarkı devam et", "müzik devam et"]):
            self.resume_music()
            return True
            
        # Sonraki şarkı
        if any(word in command for word in ["sonraki şarkı", "bir sonraki"]):
            self.next_track()
            return True
            
        # Önceki şarkı
        if any(word in command for word in ["önceki şarkı", "bir önceki"]):
            self.previous_track()
            return True
        
        # Saat
        if any(word in command for word in ["saat kaç", "saati söyle"]):
            self.get_time()
            return True
            
        # Hava durumu
        if any(word in command for word in ["hava durumu", "hava nasıl"]):
            self.get_weather()
            return True
        
        # Motivasyon
        if any(word in command for word in ["beni öv", "motivasyon"]):
            self.motivate_user()
            return True
            
        # Günlük soru
        if any(word in command for word in ["soru sor", "günlük soru"]):
            self.ask_daily_question()
            return True

        # Uyku modu
        if any(word in command for word in ["uyku modu", "uyu"]):
            self.sleep_mode = True
            self.start_sleep_conversation()
            return True

        # Güvenlik modu
        if any(word in command for word in ["güvenlik modu", "güvenlik aç"]):
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
            for i in range(5):
                pyautogui.press('volumeup')
                
        elif "sesi kıs" in command:
            self.speak("Ses kısılıyor")
            for i in range(5):
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
            
        # YENİ KOMUT: mod değiştir
        elif "mod değiştir" in command:
            self.keyboard_mode = not self.keyboard_mode
            mode = "klavye" if self.keyboard_mode else "ses"
            self.speak(f"{mode} moduna geçildi")
            
        # YENİ KOMUT: yardım
        elif "yardım" in command or "komutlar" in command:
            self.show_help()
            
        # Kapatma komutu
        elif any(word in command for word in ["kapan", "çık", "dur jarvis", "güle güle"]):
            # Kapanmadan önce duygu özeti ver
            if self.emotion_aware_mode and len(self.emotion_analyzer.emotion_history) > 0:
                summary = self.get_emotional_summary()
                if summary.get("status") != "no_data":
                    most_common = summary.get("most_common_emotion", "bilinmiyor")
                    self.speak(f"Bugün en çok {most_common} hissettiniz. ")
            
            self.speak("JARVIS kapanıyor. Harika bir gün geçirmeni dilerim!")
            return False
            
        else:
            if len(command) > 3:
                # YENİ: Derin düşünme yanıtı
                if self.deep_think_mode and random.random() < 0.2:
                    deep_response = self.generate_deep_response(command)
                    if deep_response:
                        self.speak(deep_response)
                
                # YENİ: Akıllı soru
                question = self.ask_intelligent_question(command)
                if question:
                    self.speak(question)
                else:
                    # Duygu farkındalık modu açıksa, daha empatik bir yanıt
                    if self.emotion_aware_mode:
                        self.speak("Bu komutu anlamadım, ama duygularınızı dinlemeye devam ediyorum.")
                    else:
                        self.speak("Bu komutu anlamadım.")
            
        return True

    # ==================== YENİ VE MEVCUT METOTLAR ====================
    
    def analyze_emotion_in_text(self, text: str) -> Tuple[str, EmotionalState]:
        """Metindeki duyguyu analiz et ve uygun yanıtı döndür"""
        if not text or len(text.strip()) < 3:
            return "", None
        
        try:
            # Duygu analizi yap
            context = {
                "time_of_day": datetime.datetime.now().hour,
                "interaction_type": "voice_command",
                "user_state": "active"
            }
            
            emotion_analysis = self.emotion_analyzer.analyze_with_context(text, context)
            
            # Duyguya özel yanıt oluştur
            emotional_response = self.emotion_analyzer.generate_emotional_response(
                emotion_analysis, 
                ""
            )
            
            return emotional_response, emotion_analysis
            
        except Exception as e:
            print(f"Duygu analizi hatası: {e}")
            return "", None
    
    def get_emotional_summary(self):
        """Duygu analizi özetini al"""
        return self.emotion_analyzer.get_emotion_summary()
    
    def toggle_emotion_aware_mode(self, state: bool = None):
        """Duygu farkındalık modunu aç/kapat"""
        if state is not None:
            self.emotion_aware_mode = state
        else:
            self.emotion_aware_mode = not self.emotion_aware_mode
        
        status = "açık" if self.emotion_aware_mode else "kapalı"
        return f"Duygu farkındalık modu {status}."
    
    def show_help(self):
        """Yardım mesajını göster"""
        help_text = """
╔══════════════════════════════════════════════════════╗
║          🤖 JARVIS 3.5 - GELİŞMİŞ KOMUT LİSTESİ      ║
╠══════════════════════════════════════════════════════╣
║  🎵 MÜZİK VE MEDYA:                                 ║
║  • 'Spotify aç' - Spotify'ı direkt açar             ║
║  • 'YouTube aç' - YouTube'u direkt açar             ║
║  • 'Müzik aç' - Platform seçerek müzik açar         ║
║  • 'Şarkı aç' - Platform seçerek şarkı açar         ║
║                                                      ║
║  🧠 AKILLI ÖZELLİKLER:                              ║
║  • 'bana soru sor' - Size akıllı sorular sorar      ║
║  • 'derin düşünme aç/kapat' - Akıllı mod            ║
║  • 'soru modu aç/kapat' - Otomatik soru sorma       ║
║  • 'konuşma analizi' - Sohbet özetinizi gösterir    ║
║                                                      ║
║  💭 DUYGU KOMUTLARI:                                ║
║  • 'duygu özet' - Duygu analizi özeti               ║
║  • 'duygu modu aç/kapat' - Duygu farkındalık        ║
║                                                      ║
║  📍 TEMEL KOMUTLAR:                                 ║
║  • 'saat kaç' - Saati söyler                        ║
║  • 'hava durumu' - Hava durumunu söyler             ║
║  • 'mod değiştir' - Giriş modunu değiştir           ║
║  • 'yardım' - Bu mesajı gösterir                    ║
║                                                      ║
║  🌐 İNTERNET KOMUTLARI:                             ║
║  • 'google'da ara [kelime]' - Google'da arar        ║
║  • 'netflix aç' - Netflix'i açar                    ║
║  • 'harita aç' - Google Haritalar'ı açar            ║
║  • 'haberleri aç' - Haberleri açar                  ║
║                                                      ║
║  ⚙️  SİSTEM KOMUTLARI:                              ║
║  • 'uyku modu' - Uyku moduna geçer                  ║
║  • 'güvenlik modu' - Güvenlik modu                  ║
║  • 'kapan' - Programı kapatır                       ║
╚══════════════════════════════════════════════════════╝
        """
        print(help_text)
        self.speak("Size yardımcı olabileceğim komutları gösterdim.")
        
        # YENİ: Yardım sonrası soru
        if self.auto_question_mode:
            time.sleep(1)
            self.speak("Size hangi konuda yardımcı olmamı istersiniz?")

    def background_listener(self):
        """Arka plan dinleyici"""
        print("\n🔄 JARVIS arka planda çalışıyor...")
        print("🔊 Mikrofon modu: " + ("AKTİF" if not self.keyboard_mode else "PASİF"))
        print("🧠 Derin düşünme: " + ("AÇIK" if self.deep_think_mode else "KAPALI"))
        print("❓ Soru modu: " + ("AÇIK" if self.auto_question_mode else "KAPALI"))
        print("💡 Yardım için 'yardım' yazın veya söyleyin\n")
        
        while self.is_listening:
            try:
                if self.keyboard_mode:
                    command = self.get_keyboard_input()
                else:
                    command = self.listen()
                    
                if command:
                    if not self.execute_command(command):
                        self.is_listening = False
                else:
                    time.sleep(1)
                    self.auto_motivation_check()
                    
            except Exception as e:
                print(f"Hata: {e}")
                time.sleep(2)
                continue

    def start(self):
        """JARVIS'i başlat"""
        # Tematik hoşgeldin mesajı
        welcome_msg = self.get_welcome_message()
        self.speak(welcome_msg)
        time.sleep(1)
        
        # Mikrofon kontrolü
        if not self.check_microphone():
            self.speak("Mikrofon bulunamadı. Klavye moduna geçiliyor.")
            print("⚠️  Klavye modu aktif. Komutları yazılı olarak girebilirsiniz.")
            print("   Çıkmak için 'kapan' yazın")
        
        # Sistem bilgisi
        self.speak("Seviye 5 duygu analizi sistemi aktif.")
        self.speak("Spotify ve YouTube direkt açma özelliği aktif.")
        self.speak("Akıllı soru sorma modu aktif.")
        
        # YENİ: İlk soru
        if self.auto_question_mode:
            time.sleep(1)
            first_questions = [
                "Size nasıl yardımcı olabilirim?",
                "Bugün nasılsınız?",
                "Merak ettiğiniz bir konu var mı?",
                "Sohbet etmek istediğiniz bir şey var mı?"
            ]
            self.speak(random.choice(first_questions))
        
        self.is_listening = True
        
        background_thread = threading.Thread(target=self.background_listener)
        background_thread.daemon = True
        background_thread.start()

# ==================== ANA PROGRAM ====================

def install_requirements():
    """Gerekli kütüphaneleri kontrol et ve yükle"""
    required_packages = [
        'speechrecognition',
        'pyttsx3',
        'pygame',
        'gtts',
        'pyautogui',
        'psutil'
    ]
    
    print("🔍 Gerekli kütüphaneler kontrol ediliyor...")
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} eksik")
            try:
                import subprocess
                subprocess.check_call([sys.executable, "-m", "pip", "install", package])
                print(f"📦 {package} yüklendi")
            except:
                print(f"⚠️  {package} yüklenemedi")

def main():
    """Ana program"""
    # Konsol temizle
    os.system('cls' if os.name == 'nt' else 'clear')
    
    print("=" * 60)
    print("🤖 JARVIS 3.5 - Yapay Zeka Asistanı")
    print("🎵 Spotify/YouTube Direkt Açma Özelliği")
    print("=" * 60)
    
    # Gerekli kütüphaneleri kontrol et
    install_requirements()
    
    time.sleep(2)
    
    try:
        jarvis = Jarvis()
        jarvis.start()
        
        # Ana döngü
        while jarvis.is_listening:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n\n👋 JARVIS kapatılıyor...")
        jarvis.speak("Görüşürüz efendim!")
    except Exception as e:
        print(f"\n❌ Hata: {e}")
        print("🔄 Program yeniden başlatılabilir...")
    finally:
        print("✅ Program sonlandırıldı.")

if __name__ == "__main__":
    main()