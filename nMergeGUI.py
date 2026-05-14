import sys
import os
import json
import re
import winsound
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QLabel, QLineEdit, QListWidget, QAbstractItemView, 
                             QMessageBox, QProgressBar, QTextEdit, QFileDialog, QGroupBox, 
                             QSplitter, QDialog, QTextBrowser, QCheckBox)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QPalette, QColor, QFont

if getattr(sys, 'frozen', False):
    # PyInstaller ile derlenmişse (.exe)
    APP_DIR = os.path.dirname(sys.executable)
else:
    # Normal Python scripti olarak çalışıyorsa
    APP_DIR = os.path.dirname(os.path.abspath(__file__))

CONFIG_FILE = os.path.join(APP_DIR, "config.json")
DEFAULT_EMOTIONS = [
    "ah", "oh", "uh", "um", "mm", "mmm", "ha", "haha", "uhuh", "uh-huh", "hmm", "himm",
    "shh", "shhh", "wow", "aw", "aww", "ugh", "eh", "pff", "pfft", 
    "psst", "ouch", "whew", "phew", "huh", "hm", "ooh", "whoa", "aha",
    "mhm", "humm", "tsk", "brr", "yikes", "ow", "oww", "yay", "yippee", 
    "boo", "argh", "grr", "ahem", "er", "erm", "meh", "nah", "duh", 
    "gee", "jeez", "ew", "eww"
]

TR_ABOUT_HTML = """
<h3 style='color: #2a82da;'>nMerge v1.2: LLM Çeviri Optimizasyonu İçin Akıllı Altyazı (SRT) Ön İşlemci ve Gramer Motoru</h3>
<br>
<b>Projenin Amacı ve Felsefesi</b><br>
nMerge, altyazı (SRT) dosyalarını geleneksel izleme deneyimi için değil, Büyük Dil Modeli (LLM) tabanlı yapay zeka çeviri motorlarına hazırlamak amacıyla geliştirilmiş, NLP (Doğal Dil İşleme) destekli bir ön işlem (pre-processing) otomasyonudur.<br><br>
Modern Speech-to-Text (STT) yazılımları, konuşma metnini yazıya dökerken gramer kurallarını değil, konuşmacının nefes alışlarını ve sahnelerdeki sessizlik sürelerini referans alır. Bu durum, tek bir cümlenin anlamsız yerlerden bölünerek iki veya üç farklı altyazı satırına dağılmasına neden olur. nMerge, bu sorunu çözmek için "Fiziksel zamanlamaya değil, gramatikal bütünlüğe saygı duy" felsefesini benimser.<br><br>
nMerge, altyazılardaki derin dilbilgisi analizlerini gerçekleştirmek için spaCy kütüphanesinin "en_core_web_sm" (English Core Web Small) isimli önceden eğitilmiş NLP modelini kalbinde taşır.<br><br>
<b>v1.2 ile Kusursuzlaşan İşlem Boru Hattı ve Diktatörlük Modu:</b><br><br>
<b>1. Aşama: Ön Yıkama ve "Evrensel Hafızalı" ALL CAPS Normalizasyonu:</b> Bazı eski altyazılar tamamen büyük harfle (ALL CAPS) yazılmış olabilir. Bu durum spaCy modelinin tüm kelimeleri Özel İsim (PROPN) sanmasına neden olur. nMerge, her satırı analiz eder. Eğer karakterlerin %80'inden fazlası büyük harfse, o satıra "ALL CAPS" mührü vurur ve spaCy'nin anlayabilmesi için geçici olarak küçük harfe indirger.<br><br>
<b>2. Aşama: Zaman-Bağımsız Gramatikal Birleştirme (Dokunulmazlık İlkesi ve Bypass):</b> spaCy kullanılarak cümlenin dilbilgisi anatomisi çıkarılır. Bu aşamada iki ölümcül kural devrededir:<br>
<i>- Orijinal DNA Referansı:</i> Sistem, alt satırın küçük harfle başlayıp başlamadığını sahte (küçültülmüş) metinden değil, orijinal dosyadan teyit eder. Orijinali küçükse tereddütsüz birleştirir. Alt satırın orijinal objesi (State) asla zehirlenmez, dokunulmazlığı korunur.<br>
<i>- ALL CAPS Bypass:</i> Eğer satır tamamen büyük harflerden oluşuyorsa (ALL CAPS mührü varsa) ve sonunda açıkça nokta, ünlem veya soru işareti yoksa, sistem diğer tüm kuralları ezerek satırı alt satırla birleştirir.<br><br>
<b>3. Aşama: Mutlak İrade ile Nida Temizliği (Mikro-Cerrahi ve Alfanümerik Koruma):</b> spaCy'nin neyin "nida" (INTJ) olduğuna karar verme yetkisi tamamen elinden alınmıştır! Sistem, cümle içindeki çöpleri ararken sadece ve sadece sizin arayüzden belirlediğiniz <b>Duygu İfadeleri (Sözlük)</b> listesine itaat eder. Ayrıca sayılar ve rakamlar "isalnum()" kalkanıyla korunarak istatistiksel hata kurbanı olmaktan %100 kurtarılmıştır.<br><br>
<b>4. Aşama: Hafızalı İmla ve spaCy Cilası (Stateful Orthography):</b> Metin son kez NLP motorundan geçer. Cümlenin ortasında kalan haksız büyük harfler küçük harfe zorlanır. Döngü, cümlenin nasıl bittiğini hafızasına yazar ve sonraki satırın kaderini belirler.<br><br>
<b>* Gelişmiş Telemetri (Röntgen) Modu:</b> Kodun birleştirmeyi reddettiği satırlarda, kararın arkasındaki nedeni (hangi kurala takıldığını, orijinal ilk harfin ne olduğunu vb.) log ekranına basarak karanlıkta kalan hataları teşhis etmenizi sağlar.<br><br>
<br><hr><br>
<p style='text-align: center; color: #888;'><b>Developed by nutuzar | nMerge Otomasyon v1.2</b></p>
"""

EN_ABOUT_HTML = """
<h3 style='color: #2a82da;'>nMerge v1.2: Smart Subtitle (SRT) Preprocessor and Grammar Engine for LLM Optimization</h3>
<br>
<b>Project Purpose and Philosophy</b><br>
nMerge is an NLP-supported preprocessing automation developed to prepare subtitle (SRT) files not for traditional viewing experiences, but for Large Language Model (LLM) based AI translation engines.<br><br>
Modern Speech-to-Text (STT) software references speakers' breathing patterns and scene silence durations rather than grammar rules. This causes single sentences to be split at meaningless points. nMerge adopts the philosophy: "Respect grammatical integrity, not physical timing."<br><br>
At its core, nMerge carries spaCy's pre-trained NLP model named "en_core_web_sm" for deep grammatical analysis.<br><br>
<b>The Perfected Execution Pipeline & Dictatorship Mode in v1.2:</b><br><br>
<b>Stage 1: Pre-wash and "Stateful" ALL CAPS Normalization:</b> Some older subtitles might be completely capitalized (ALL CAPS). This causes the spaCy model to mistake all words for Proper Nouns (PROPN). nMerge analyzes each line. If more than 80% of characters are uppercase, it stamps the line with an "ALL CAPS" seal and temporarily reduces it to lowercase for spaCy.<br><br>
<b>Stage 2: Time-Independent Absolute Grammar Merging (Immutability Principle & Bypass):</b> Using spaCy, the grammatical anatomy of the sentence is extracted. Two lethal rules are active here:<br>
<i>- Original DNA Reference:</i> The system checks if the bottom line starts with a lowercase letter by looking at the original file, not the fake (lowered) text. If the original is lowercase, it merges unconditionally. The state of the bottom line object is strictly protected.<br>
<i>- ALL CAPS Bypass:</i> If the line consists entirely of uppercase letters (ALL CAPS seal is present) and clearly lacks a terminal period, exclamation, or question mark, the system overrides all other rules and merges it with the bottom line.<br><br>
<b>Stage 3: Absolute Will Interjection Cleaning (Micro-Surgery & Alphanumeric Shield):</b> spaCy's authority to decide what constitutes an "interjection" (INTJ) has been completely revoked! When searching for garbage within a sentence, the system obeys solely your custom <b>Emotion Expressions (Dictionary)</b> defined in the GUI. Furthermore, pure numbers are protected via the "isalnum()" shield, 100% immune to statistical errors.<br><br>
<b>Stage 4: Stateful Orthography and spaCy Polish:</b> The text passes through the NLP engine one last time. Unjustified capital letters in the middle of the sentence are forced to lowercase.<br><br>
<b>* Advanced Telemetry (X-Ray) Mode:</b> For lines where the code refuses to merge, it prints the exact reason behind the decision (which rule it failed, what the original first letter was, etc.) to the log screen, allowing you to diagnose hidden errors.<br><br>
<br><hr><br>
<p style='text-align: center; color: #888;'><b>Developed by nutuzar | nMerge Automation v1.2</b></p>
"""

LANG_DICT = {
    'tr': {
        'title': "nMerge - Alt Yazı İçi Cümle Birleştirici (v1.2)",
        'out_settings': "Çıktı Ayarları",
        'out_filename': "Çıktı Dosya Adı:",
        'emo_dict': "Duygu İfadeleri (Sözlük)",
        'new_emo_placeholder': "Yeni ifade...",
        'btn_add': "Ekle",
        'btn_del_sel': "Seçileni Sil",
        'srt_files': "Altyazı Dosyaları (Sürükle - Bırak)",
        'btn_add_file': "Dosya Ekle",
        'btn_rem_file': "Seçileni Çıkar",
        'btn_clear_all': "Tümünü Temizle",
        'btn_start': "BAŞLAT",
        'btn_open_folder': "Çıktı Klasörünü Aç",
        'telemetry': "Telemetri / Rapor Ekranı:",
        'btn_about': "Hakkında",
        'btn_close': "Kapat",
        'prepared_by': "Hazırlayan: nutuzar",
        'log_emo_added': "Duygu ifadesi eklendi: {}",
        'log_emo_deleted': "Seçili duygu ifadeleri silindi.",
        'msg_close_warn_title': "Bilgi",
        'msg_close_warn': "Lütfen çıkmak için sağ alttaki '{}' butonunu kullanın.",
        'msg_no_file': "Henüz bir işlem yapılmadı!",
        'msg_err_folder': "Klasör bulunamadı veya henüz işlem yapılmadı.",
        'msg_err': "Hata",
        'msg_warn': "Uyarı",
        'msg_pls_add_srt': "Lütfen işlenecek en az bir .srt dosyası ekleyin!",
        'log_starting': "İşlem başlatılıyor...",
        'log_model_loading': "İngilizce dil modeli yükleniyor, lütfen bekleyin...",
        'log_model_loaded': "Dil modeli başarıyla yüklendi!\n",
        'log_processing': "[{}/{}] İşleniyor: {}",
        'log_saved': "Başarıyla kaydedildi: {}",
        'log_deleted_emo': "  -> İçinden tamamen çöp (nida) temizlenen/silinen satır sayısı: {}",
        'log_done': "\n--- İŞLEM TAMAMLANDI ---",
        'log_total_files': "Toplam {} dosya işlendi.",
        'log_total_del': "Toplam {} adet gereksiz duygu satırı buharlaştırıldı.",
        'err_pysubs2': "Kritik Hata: 'pysubs2' kütüphanesi bulunamadı!\nTerminalde çalıştırın: pip install pysubs2",
        'err_spacy': "Kritik Hata: 'spacy' kütüphanesi bulunamadı!\nTerminalde çalıştırın: pip install spacy",
        'err_spacy_model': "Kritik Hata: spaCy 'en_core_web_sm' modeli bulunamadı!\nTerminalde çalıştırın: python -m spacy download en_core_web_sm",
        'err_read_file': "Dosya okunamadı: {}\n{}",
        'err_save_file': "Kaydedilemedi: {}\n{}",
        'about_title': "Hakkında - nMerge v1.2",
        'about_html': TR_ABOUT_HTML,
        'cb_debug_mode': "Gelişmiş Telemetri (Röntgen) Modu",
        'log_debug_rejected': "[RÖNTGEN] REDDEDİLDİ: '{}' + '{}'\n  -> Sebep: {}"
    },
    'en': {
        'title': "nMerge - Subtitle Intra-Sentence Merger (v1.2)",
        'out_settings': "Output Settings",
        'out_filename': "Output Filename:",
        'emo_dict': "Emotion Expressions (Dictionary)",
        'new_emo_placeholder': "New expression...",
        'btn_add': "Add",
        'btn_del_sel': "Delete Selected",
        'srt_files': "Subtitle Files (Drag & Drop)",
        'btn_add_file': "Add File",
        'btn_rem_file': "Remove Selected",
        'btn_clear_all': "Clear All",
        'btn_start': "START",
        'btn_open_folder': "Open Output Folder",
        'telemetry': "Telemetry / Report Screen:",
        'btn_about': "About",
        'btn_close': "Close",
        'prepared_by': "Developed by: nutuzar",
        'log_emo_added': "Emotion expression added: {}",
        'log_emo_deleted': "Selected emotion expressions deleted.",
        'msg_close_warn_title': "Information",
        'msg_close_warn': "Please use the '{}' button at the bottom right to exit.",
        'msg_no_file': "No operations performed yet!",
        'msg_err_folder': "Folder not found or no operations performed yet.",
        'msg_err': "Error",
        'msg_warn': "Warning",
        'msg_pls_add_srt': "Please add at least one .srt file to process!",
        'log_starting': "Process starting...",
        'log_model_loading': "Loading English language model, please wait...",
        'log_model_loaded': "Language model successfully loaded!\n",
        'log_processing': "[{}/{}] Processing: {}",
        'log_saved': "Successfully saved: {}",
        'log_deleted_emo': "  -> {} lines completely evaporated due to pure garbage/filler content.",
        'log_done': "\n--- PROCESS COMPLETED ---",
        'log_total_files': "Total {} files processed.",
        'log_total_del': "Total {} unnecessary emotion lines evaporated.",
        'err_pysubs2': "Critical Error: 'pysubs2' library not found!\nRun in terminal: pip install pysubs2",
        'err_spacy': "Critical Error: 'spacy' library not found!\nRun in terminal: pip install spacy",
        'err_spacy_model': "Critical Error: spaCy 'en_core_web_sm' model not found!\nRun in terminal: python -m spacy download en_core_web_sm",
        'err_read_file': "Could not read file: {}\n{}",
        'err_save_file': "Could not save: {}\n{}",
        'about_title': "About - nMerge v1.2",
        'about_html': EN_ABOUT_HTML,
        'cb_debug_mode': "Advanced Telemetry (X-Ray) Mode",
        'log_debug_rejected': "[X-RAY] REJECTED: '{}' + '{}'\n  -> Reason: {}"
    }
}

def load_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            pass
    return {"emotions": DEFAULT_EMOTIONS, "default_output_name": "orijinal_film", "lang": "tr"}

def save_config(config):
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=4, ensure_ascii=False)

# --- İŞLEME FONKSİYONLARI ---

def temizle_metin(text):
    text = text.replace("\\N", " ").strip()
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'\bi\b', 'I', text)
    return text

def baglanti_hatalarini_temizle_ve_birlestir(su_anki_metin, sonraki_metin):
    m1 = re.sub(r'(\.{2,}|…|-{2,})(\s*(?:<[^>]+>)?\s*)$', r'\2', su_anki_metin.strip())
    m1 = re.sub(r'(?<!\.)\.(?!\.)(\s*(?:<[^>]+>)?\s*)$', r'\1', m1.strip())
    m2 = re.sub(r'^(\s*(?:<[^>]+>)?\s*)(\.{2,}|…|-{2,})', r'\1', sonraki_metin.strip())
    return m1.strip() + " " + m2.strip()

def nida_temizle_spacy(metin, emotions_set, nlp):
    """
    v1.2: spaCy'nin INTJ (Nida) dictatörlüğü YIKILDI.
    Algoritma sadece ve sadece kullanıcının emotions_set (Duygu Listesi) kurallarına itaat eder.
    Sayılar ve rakamlar isalnum() kalkanıyla korunmaktadır.
    """
    if not metin.strip():
        return metin
        
    doc = nlp(metin)
    silinecek_kelimeler = []
    
    for token in doc:
        kelime = token.text.lower()
        if kelime in ['<', '>', 'i', '/i', 'b', '/b', 'u', '/u']:
            continue
        if token.is_punct or token.is_space:
            continue
            
        kelime_saf = re.sub(r'[^\w\s-]', '', kelime).strip()
        if not kelime_saf: 
            continue
            
        if kelime_saf in emotions_set:
            silinecek_kelimeler.append(token.text)
            
    yeni_metin = metin
    for s_kelime in set(silinecek_kelimeler):
        pattern = r'\b' + re.escape(s_kelime) + r'\b\s*[,]?\s*'
        yeni_metin = re.sub(pattern, '', yeni_metin, flags=re.IGNORECASE)
        
    temiz = re.sub(r'<[^>]+>', '', yeni_metin)
    
    if not any(c.isalnum() for c in temiz):
        return ""
        
    yeni_metin = re.sub(r'^\s*[,]\s*', '', yeni_metin)
    
    return yeni_metin.strip()

def spacy_ile_imla_duzelt(metin, onceki_satir_noktayla_mi_bitti, nlp):
    if not metin.strip():
        return metin, onceki_satir_noktayla_mi_bitti
        
    doc = nlp(metin)
    duzeltilmis_kelimeler = []
    
    for i, token in enumerate(doc):
        kelime = token.text
        if '<' in kelime or '>' in kelime or '{' in kelime:
            duzeltilmis_kelimeler.append(kelime + token.whitespace_)
            continue

        is_sentence_start = token.is_sent_start
        if i == 0:
            is_sentence_start = onceki_satir_noktayla_mi_bitti
            
        if token.pos_ == "PROPN" or kelime == "I":
            pass
        elif is_sentence_start:
            kelime = kelime.capitalize()
        elif kelime.isalpha():
            kelime = kelime.lower()
            
        duzeltilmis_kelimeler.append(kelime + token.whitespace_)
        
    temiz_sonuc = "".join(duzeltilmis_kelimeler).strip()
    
    sonraki_satir_yeni_cumle_mi = False
    if temiz_sonuc:
        son_karakter = temiz_sonuc[-1]
        if son_karakter in ['.', '!', '?'] and not temiz_sonuc.endswith('...'):
            sonraki_satir_yeni_cumle_mi = True
            
    return temiz_sonuc, sonraki_satir_yeni_cumle_mi

def spacy_ile_birlestirmeli_mi(su_anki_metin, sonraki_metin, sonraki_orijinal, su_anki_all_caps_mi, nlp):
    temiz_su = re.sub(r'<[^>]+>|\{[^}]+\}', '', su_anki_metin).strip()
    temiz_son = re.sub(r'<[^>]+>|\{[^}]+\}', '', sonraki_metin).strip()
    temiz_son_orijinal = re.sub(r'<[^>]+>|\{[^}]+\}', '', sonraki_orijinal).strip()

    if not temiz_su or not temiz_son_orijinal:
        return False, "Satırlardan biri veya HTML tagleri temizlendikten sonraki hali tamamen boş."

    if re.match(r'^-[^-]', temiz_son_orijinal):
        return False, "Sonraki satır diyalog tirelesi (-) ile başlıyor."

    if re.search(r'(\.{2,}|…|-{2,})$', temiz_su):
        return True, ""
    if temiz_su.endswith((',', ';', ':')):
        return True, ""

    if su_anki_all_caps_mi:
        son_karakter = temiz_su[-1]
        if son_karakter not in ['.', '!', '?']:
            return True, ""
        else:
            return False, "Üst satır ALL CAPS damgalı ama cümlenin sonu açıkça bir noktalama işareti (.!?) ile bitmiş."

    doc1 = nlp(temiz_su)
    doc2 = nlp(temiz_son)

    if len(doc1) > 0:
        son_gercek_kelime = None
        for token in reversed(doc1):
            if not token.is_punct:
                son_gercek_kelime = token
                break
        
        if son_gercek_kelime is not None:
            tehlikeli_bitisler = ['ADP', 'CCONJ', 'SCONJ', 'DET', 'PART', 'AUX']
            if son_gercek_kelime.pos_ in tehlikeli_bitisler:
                return True, ""

    ilk_harf = ""
    for c in temiz_son_orijinal:
        if c.isalpha():
            ilk_harf = c
            break
    
    if ilk_harf and ilk_harf.islower():
        return True, ""

    return False, f"Hiçbir bağ kuralına uymadı. (Orijinal DNA'da tespit edilen ilk harf: '{ilk_harf}' - islower: {ilk_harf.islower() if ilk_harf else 'Yok'})"

# --- THREAD ---

class WorkerThread(QThread):
    log_signal = pyqtSignal(str)
    progress_signal = pyqtSignal(int)
    finished_signal = pyqtSignal(int, int)
    error_signal = pyqtSignal(str)

    def __init__(self, files, output_name, emotions_set, lang_dict, debug_mode):
        super().__init__()
        self.files = files
        self.output_name = output_name
        self.emotions_set = set(e.lower() for e in emotions_set)
        self.lang = lang_dict
        self.debug_mode = debug_mode

    def run(self):
        try:
            import pysubs2
        except ImportError:
            self.error_signal.emit(self.lang['err_pysubs2'])
            return

        # PyInstaller'ın statik analizörünü atlatmak için doğrudan modül importu yapıyoruz
        try:
            import spacy
            import en_core_web_sm
        except ImportError:
            self.error_signal.emit(self.lang['err_spacy'] + "\n(Veya model eksik, lütfen 'python -m spacy download en_core_web_sm' komutunu çalıştırın)")
            return

        self.log_signal.emit(self.lang['log_model_loading'])
        try:
            # Artık spacy.load("en_core_web_sm") kullanmıyoruz. Doğrudan modülden load yapıyoruz.
            nlp = en_core_web_sm.load()
            self.log_signal.emit(self.lang['log_model_loaded'])
        except Exception:
            self.error_signal.emit(self.lang['err_spacy_model'])
            return

        total_files = len(self.files)
        total_deleted = 0

        for idx, dosya in enumerate(self.files):
            self.log_signal.emit(self.lang['log_processing'].format(idx+1, total_files, os.path.basename(dosya)))
            
            try:
                subs = pysubs2.load(dosya, encoding="utf-8")
            except UnicodeDecodeError:
                try:
                    subs = pysubs2.load(dosya, encoding="latin-1")
                except Exception as e:
                    self.error_signal.emit(self.lang['err_read_file'].format(os.path.basename(dosya), str(e)))
                    continue
            except Exception as e:
                self.error_signal.emit(self.lang['err_read_file'].format(os.path.basename(dosya), str(e)))
                continue

            yeni_satirlar = []
            i = 0
            silinen_satir_sayisi = 0
            yeni_cumle_mi = True 

            while i < len(subs):
                su_anki_satir = subs[i]
                su_anki_orijinal = su_anki_satir.text.strip()
                su_anki_metin = su_anki_orijinal
                su_anki_all_caps_mi = False
                
                harfler = [c for c in su_anki_orijinal if c.isalpha()]
                if harfler:
                    buyuk_harf_orani = sum(1 for c in harfler if c.isupper()) / len(harfler)
                    if buyuk_harf_orani > 0.8:
                        su_anki_all_caps_mi = True
                        su_anki_metin = su_anki_orijinal.lower()
                        if yeni_cumle_mi:
                            for i_char, char in enumerate(su_anki_metin):
                                if char.isalpha():
                                    su_anki_metin = su_anki_metin[:i_char] + char.upper() + su_anki_metin[i_char+1:]
                                    break
                su_anki_satir.text = su_anki_metin
                
                while i + 1 < len(subs):
                    sonraki_satir = subs[i+1]
                    sonraki_orijinal = sonraki_satir.text.strip()
                    sonraki_metin = sonraki_orijinal
                    
                    s_harfler = [c for c in sonraki_orijinal if c.isalpha()]
                    if s_harfler:
                        s_buyuk_orani = sum(1 for c in s_harfler if c.isupper()) / len(s_harfler)
                        if s_buyuk_orani > 0.8:
                            sonraki_metin = sonraki_orijinal.lower()

                    birlestir_mi, sebep = spacy_ile_birlestirmeli_mi(su_anki_satir.text, sonraki_metin, sonraki_orijinal, su_anki_all_caps_mi, nlp)
                    
                    if birlestir_mi:
                        su_anki_satir.end = sonraki_satir.end
                        
                        su_anki_satir.text = baglanti_hatalarini_temizle_ve_birlestir(su_anki_satir.text, sonraki_orijinal)
                        
                        su_anki_orijinal = baglanti_hatalarini_temizle_ve_birlestir(su_anki_orijinal, sonraki_orijinal)
                        yeni_harfler = [c for c in su_anki_orijinal if c.isalpha()]
                        if yeni_harfler:
                            su_anki_all_caps_mi = (sum(1 for c in yeni_harfler if c.isupper()) / len(yeni_harfler)) > 0.8
                        else:
                            su_anki_all_caps_mi = False
                            
                        i += 1
                    else:
                        if self.debug_mode:
                            t1 = su_anki_satir.text.replace('\n', ' ')
                            t2 = sonraki_orijinal.replace('\n', ' ')
                            self.log_signal.emit(self.lang['log_debug_rejected'].format(t1, t2, sebep))
                        break
                
                su_anki_satir.text = temizle_metin(su_anki_satir.text)
                su_anki_satir.text = nida_temizle_spacy(su_anki_satir.text, self.emotions_set, nlp)
                
                if not su_anki_satir.text.strip():
                    silinen_satir_sayisi += 1
                    total_deleted += 1
                    i += 1
                    continue
                
                su_anki_satir.text, yeni_cumle_mi = spacy_ile_imla_duzelt(su_anki_satir.text, yeni_cumle_mi, nlp)
                
                yeni_satirlar.append(su_anki_satir)
                i += 1

            subs.events = yeni_satirlar
            
            hedef_dizin = os.path.dirname(os.path.abspath(dosya))
            
            out_base = self.output_name if self.output_name else "orijinal_film"
            if not out_base.lower().endswith('.srt'):
                out_base += '.srt'
                
            if total_files > 1:
                name, ext = os.path.splitext(out_base)
                out_base = f"{name}_{idx+1}{ext}"

            cikti_adi = os.path.join(hedef_dizin, out_base)
            
            try:
                subs.save(cikti_adi)
                self.log_signal.emit(self.lang['log_saved'].format(os.path.basename(cikti_adi)))
                if silinen_satir_sayisi > 0:
                    self.log_signal.emit(self.lang['log_deleted_emo'].format(silinen_satir_sayisi))
            except Exception as e:
                self.error_signal.emit(self.lang['err_save_file'].format(cikti_adi, str(e)))
            
            progress = int(((idx + 1) / total_files) * 100)
            self.progress_signal.emit(progress)

        self.finished_signal.emit(total_files, total_deleted)

# --- GUI BİLEŞENLERİ ---

class DragDropListWidget(QListWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.setSelectionMode(QAbstractItemView.ExtendedSelection)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        if event.mimeData().hasUrls():
            event.setDropAction(Qt.CopyAction)
            event.accept()
            for url in event.mimeData().urls():
                if url.isLocalFile():
                    file_path = url.toLocalFile()
                    if file_path.lower().endswith('.srt'):
                        items = [self.item(x).text() for x in range(self.count())]
                        if file_path not in items:
                            self.addItem(file_path)
        else:
            event.ignore()

class AboutDialog(QDialog):
    def __init__(self, parent, html_content, title_text, close_text):
        super().__init__(parent)
        self.setWindowTitle(title_text)
        self.resize(850, 650)
        layout = QVBoxLayout(self)
        
        browser = QTextBrowser()
        browser.setOpenExternalLinks(True)
        browser.setHtml(html_content)
        
        font = browser.font()
        font.setPointSize(11)
        browser.setFont(font)
        
        layout.addWidget(browser)
        
        btn = QPushButton(close_text)
        btn.clicked.connect(self.accept)
        btn.setMinimumHeight(35)
        layout.addWidget(btn, alignment=Qt.AlignCenter)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.config = load_config()
        self.current_lang = self.config.get("lang", "tr")
        if self.current_lang not in LANG_DICT:
            self.current_lang = "tr"
        
        self.lang = LANG_DICT[self.current_lang]
        self.last_output_dir = None
        self.worker = None
        
        self.initUI()
        self.apply_language()

    def initUI(self):
        self.resize(950, 750)
        
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout(main_widget)
        
        top_layout = QHBoxLayout()
        top_layout.addStretch()
        
        self.btn_tr = QPushButton("TR")
        self.btn_tr.clicked.connect(lambda: self.switch_language("tr"))
        self.btn_en = QPushButton("EN")
        self.btn_en.clicked.connect(lambda: self.switch_language("en"))
        
        top_layout.addWidget(self.btn_tr)
        top_layout.addWidget(self.btn_en)
        main_layout.addLayout(top_layout)
        
        splitter = QSplitter(Qt.Horizontal)
        
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(0, 0, 0, 0)
        
        self.output_group = QGroupBox()
        output_layout = QVBoxLayout()
        self.output_label = QLabel()
        self.output_name_input = QLineEdit()
        self.output_name_input.setText(self.config.get("default_output_name", "orijinal_film"))
        self.output_name_input.textChanged.connect(self.update_config_name)
        output_layout.addWidget(self.output_label)
        output_layout.addWidget(self.output_name_input)
        self.output_group.setLayout(output_layout)
        left_layout.addWidget(self.output_group)
        
        self.emotion_group = QGroupBox()
        emotion_layout = QVBoxLayout()
        self.emotion_list = QListWidget()
        for e in sorted(self.config.get("emotions", [])):
            self.emotion_list.addItem(e)
        emotion_layout.addWidget(self.emotion_list)
        
        emo_add_layout = QHBoxLayout()
        self.emo_input = QLineEdit()
        self.emo_input.returnPressed.connect(self.add_emotion)
        self.emo_add_btn = QPushButton()
        self.emo_add_btn.setStyleSheet("background-color: #004080; color: white; font-weight: bold;")
        self.emo_add_btn.clicked.connect(self.add_emotion)
        emo_add_layout.addWidget(self.emo_input)
        emo_add_layout.addWidget(self.emo_add_btn)
        emotion_layout.addLayout(emo_add_layout)
        
        self.emo_del_btn = QPushButton()
        self.emo_del_btn.setStyleSheet("background-color: #b22222; color: white; font-weight: bold;")
        self.emo_del_btn.clicked.connect(self.del_emotion)
        emotion_layout.addWidget(self.emo_del_btn)
        self.emotion_group.setLayout(emotion_layout)
        left_layout.addWidget(self.emotion_group)
        
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(0, 0, 0, 0)
        
        self.file_group = QGroupBox()
        file_layout = QVBoxLayout()
        self.file_list = DragDropListWidget()
        file_layout.addWidget(self.file_list)
        
        file_btns_layout = QHBoxLayout()
        self.add_file_btn = QPushButton()
        self.add_file_btn.setStyleSheet("background-color: #004080; color: white; font-weight: bold;")
        self.add_file_btn.clicked.connect(self.add_files)
        self.rem_file_btn = QPushButton()
        self.rem_file_btn.setStyleSheet("background-color: #b22222; color: white; font-weight: bold;")
        self.rem_file_btn.clicked.connect(self.remove_files)
        self.clear_file_btn = QPushButton()
        self.clear_file_btn.setStyleSheet("background-color: #b22222; color: white; font-weight: bold;")
        self.clear_file_btn.clicked.connect(self.file_list.clear)
        file_btns_layout.addWidget(self.add_file_btn)
        file_btns_layout.addWidget(self.rem_file_btn)
        file_btns_layout.addWidget(self.clear_file_btn)
        file_layout.addLayout(file_btns_layout)
        self.file_group.setLayout(file_layout)
        right_layout.addWidget(self.file_group)
        
        self.debug_cb = QCheckBox()
        self.debug_cb.setStyleSheet("color: #ff9900; font-weight: bold;")
        right_layout.addWidget(self.debug_cb)

        action_layout = QHBoxLayout()
        self.start_btn = QPushButton()
        self.start_btn.setMinimumHeight(40)
        self.start_btn.setStyleSheet("background-color: #2e8b57; color: white; font-weight: bold; font-size: 14px;")
        font = self.start_btn.font()
        font.setBold(True)
        self.start_btn.setFont(font)
        self.start_btn.clicked.connect(self.start_processing)
        
        self.open_folder_btn = QPushButton()
        self.open_folder_btn.setMinimumHeight(40)
        self.open_folder_btn.setStyleSheet("background-color: #d4af37; color: black; font-weight: bold;")
        self.open_folder_btn.setEnabled(False)
        self.open_folder_btn.clicked.connect(self.open_output_folder)
        
        action_layout.addWidget(self.start_btn)
        action_layout.addWidget(self.open_folder_btn)
        right_layout.addLayout(action_layout)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        right_layout.addWidget(self.progress_bar)
        
        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        splitter.setSizes([300, 800])
        main_layout.addWidget(splitter)
        
        bottom_layout = QVBoxLayout()
        self.telemetry_label = QLabel()
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMaximumHeight(250)
        bottom_layout.addWidget(self.telemetry_label)
        bottom_layout.addWidget(self.log_text)
        
        sys_btns_layout = QHBoxLayout()
        self.about_btn = QPushButton()
        self.about_btn.setStyleSheet("background-color: #004080; color: white; font-weight: bold;")
        self.about_btn.clicked.connect(self.show_about)
        
        self.close_btn = QPushButton()
        self.close_btn.setStyleSheet("background-color: #b22222; color: white; font-weight: bold;")
        self.close_btn.clicked.connect(self.exit_app)
        
        self.prepared_by_label = QLabel()
        
        sys_btns_layout.addWidget(self.about_btn)
        sys_btns_layout.addStretch()
        sys_btns_layout.addWidget(self.prepared_by_label)
        sys_btns_layout.addStretch()
        sys_btns_layout.addWidget(self.close_btn)
        bottom_layout.addLayout(sys_btns_layout)
        
        main_layout.addLayout(bottom_layout)

    def switch_language(self, lang_code):
        self.current_lang = lang_code
        self.config["lang"] = lang_code
        save_config(self.config)
        self.lang = LANG_DICT[lang_code]
        self.apply_language()

    def apply_language(self):
        self.setWindowTitle(self.lang['title'])
        self.output_group.setTitle(self.lang['out_settings'])
        self.output_label.setText(self.lang['out_filename'])
        self.emotion_group.setTitle(self.lang['emo_dict'])
        self.emo_input.setPlaceholderText(self.lang['new_emo_placeholder'])
        self.emo_add_btn.setText(self.lang['btn_add'])
        self.emo_del_btn.setText(self.lang['btn_del_sel'])
        
        self.file_group.setTitle(self.lang['srt_files'])
        self.add_file_btn.setText(self.lang['btn_add_file'])
        self.rem_file_btn.setText(self.lang['btn_rem_file'])
        self.clear_file_btn.setText(self.lang['btn_clear_all'])
        
        self.debug_cb.setText(self.lang['cb_debug_mode'])
        self.start_btn.setText(self.lang['btn_start'])
        self.open_folder_btn.setText(self.lang['btn_open_folder'])
        self.telemetry_label.setText(self.lang['telemetry'])
        
        self.about_btn.setText(self.lang['btn_about'])
        self.close_btn.setText(self.lang['btn_close'])
        self.prepared_by_label.setText(self.lang['prepared_by'])
        
        if self.current_lang == "tr":
            self.btn_tr.setStyleSheet("background-color: #2a82da; font-weight: bold;")
            self.btn_en.setStyleSheet("")
        else:
            self.btn_en.setStyleSheet("background-color: #2a82da; font-weight: bold;")
            self.btn_tr.setStyleSheet("")

    def exit_app(self):
        self.close()

    def update_config_name(self):
        self.config["default_output_name"] = self.output_name_input.text()
        save_config(self.config)

    def add_emotion(self):
        word = self.emo_input.text().strip().lower()
        if word:
            current_emotions = self.config.get("emotions", [])
            if word not in current_emotions:
                current_emotions.append(word)
                self.config["emotions"] = current_emotions
                save_config(self.config)
                
                self.emotion_list.clear()
                for e in sorted(self.config.get("emotions", [])):
                    self.emotion_list.addItem(e)
                    
                self.log_text.append(self.lang['log_emo_added'].format(word))
        self.emo_input.clear()

    def del_emotion(self):
        selected_items = self.emotion_list.selectedItems()
        if not selected_items:
            return
        
        for item in selected_items:
            word = item.text()
            if word in self.config["emotions"]:
                self.config["emotions"].remove(word)
        save_config(self.config)
        
        self.emotion_list.clear()
        for e in sorted(self.config.get("emotions", [])):
            self.emotion_list.addItem(e)
            
        self.log_text.append(self.lang['log_emo_deleted'])

    def add_files(self):
        files, _ = QFileDialog.getOpenFileNames(self, self.lang['btn_add_file'], "", "Subtitle Files (*.srt)")
        if files:
            existing = [self.file_list.item(i).text() for i in range(self.file_list.count())]
            for f in files:
                if f not in existing:
                    self.file_list.addItem(f)

    def remove_files(self):
        for item in self.file_list.selectedItems():
            self.file_list.takeItem(self.file_list.row(item))

    def show_about(self):
        dialog = AboutDialog(self, self.lang['about_html'], self.lang['about_title'], self.lang['btn_close'])
        dialog.exec_()

    def open_output_folder(self):
        if self.last_output_dir and os.path.exists(self.last_output_dir):
            if os.name == 'nt':
                os.startfile(self.last_output_dir)
            else:
                import subprocess
                subprocess.Popen(['xdg-open', self.last_output_dir])
        else:
            QMessageBox.warning(self, self.lang['msg_err'], self.lang['msg_err_folder'])

    def log_message(self, msg):
        self.log_text.append(msg)
        self.log_text.verticalScrollBar().setValue(self.log_text.verticalScrollBar().maximum())

    def start_processing(self):
        count = self.file_list.count()
        if count == 0:
            QMessageBox.warning(self, self.lang['msg_warn'], self.lang['msg_pls_add_srt'])
            return

        files = [self.file_list.item(i).text() for i in range(count)]
        
        self.last_output_dir = os.path.dirname(os.path.abspath(files[0]))
        self.open_folder_btn.setEnabled(False)
        self.start_btn.setEnabled(False)
        self.progress_bar.setValue(0)
        self.log_text.clear()
        self.log_message(self.lang['log_starting'])

        emotions = self.config.get("emotions", DEFAULT_EMOTIONS)
        out_name = self.output_name_input.text()
        is_debug = self.debug_cb.isChecked()

        self.worker = WorkerThread(files, out_name, emotions, self.lang, is_debug)
        self.worker.log_signal.connect(self.log_message)
        self.worker.progress_signal.connect(self.progress_bar.setValue)
        self.worker.error_signal.connect(self.on_error)
        self.worker.finished_signal.connect(self.on_finished)
        self.worker.start()

    def on_error(self, err_msg):
        QMessageBox.critical(self, self.lang['msg_err'], err_msg)
        self.log_message(f"{self.lang['msg_err'].upper()}: {err_msg}")
        self.start_btn.setEnabled(True)

    def on_finished(self, total_files, total_deleted):
        self.start_btn.setEnabled(True)
        self.open_folder_btn.setEnabled(True)
        self.log_message(self.lang['log_done'])
        self.log_message(self.lang['log_total_files'].format(total_files))
        self.log_message(self.lang['log_total_del'].format(total_deleted))
        
        try:
            winsound.Beep(1000, 500)
        except:
            pass

def set_dark_theme(app):
    app.setStyle('Fusion')
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(45, 45, 45))
    palette.setColor(QPalette.WindowText, Qt.white)
    palette.setColor(QPalette.Base, QColor(25, 25, 25))
    palette.setColor(QPalette.AlternateBase, QColor(45, 45, 45))
    palette.setColor(QPalette.ToolTipBase, Qt.white)
    palette.setColor(QPalette.ToolTipText, Qt.white)
    palette.setColor(QPalette.Text, Qt.white)
    palette.setColor(QPalette.Button, QColor(53, 53, 53))
    palette.setColor(QPalette.ButtonText, Qt.white)
    palette.setColor(QPalette.BrightText, Qt.red)
    palette.setColor(QPalette.Link, QColor(42, 130, 218))
    palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
    palette.setColor(QPalette.HighlightedText, Qt.black)
    app.setPalette(palette)

if __name__ == "__main__":
    if hasattr(Qt, 'AA_EnableHighDpiScaling'):
        QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    if hasattr(Qt, 'AA_UseHighDpiPixmaps'):
        QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
        
    app = QApplication(sys.argv)
    set_dark_theme(app)
    
    try:
        import pysubs2
        import spacy
        import en_core_web_sm
    except ImportError as e:
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Critical)
        msg.setText(f"Gerekli kütüphaneler eksik (Missing libraries): {e.name}")
        msg.setInformativeText(f"Lütfen terminali açıp şu komutu çalıştırın (Run in terminal):\n\npip install pysubs2 spacy PyQt5\npython -m spacy download en_core_web_sm")
        msg.setWindowTitle("Eksik Kütüphane / Missing Library")
        msg.exec_()
        sys.exit(1)
        
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())