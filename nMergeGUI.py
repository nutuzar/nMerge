import sys
import os
import json
import re
import winsound
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QLabel, QLineEdit, QListWidget, QAbstractItemView, 
                             QMessageBox, QProgressBar, QTextEdit, QFileDialog, QGroupBox, 
                             QSplitter, QDialog, QTextBrowser)
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
<h3 style='color: #2a82da;'>nMerge: LLM Çeviri Optimizasyonu İçin Akıllı Altyazı (SRT) Ön İşlemci ve Gramer Motoru</h3>
<br>
<b>Projenin Amacı ve Felsefesi</b><br>
nMerge, altyazı (SRT) dosyalarını geleneksel izleme deneyimi için değil, Büyük Dil Modeli (LLM) tabanlı yapay zeka çeviri motorlarına hazırlamak amacıyla geliştirilmiş, NLP (Doğal Dil İşleme) destekli bir ön işlem (pre-processing) otomasyonudur.<br><br>
Modern Speech-to-Text (STT) yazılımları, konuşma metnini yazıya dökerken gramer kurallarını değil, konuşmacının nefes alışlarını ve sahnelerdeki sessizlik sürelerini (zaman damgalarını) referans alır. Bu durum, tek bir cümlenin anlamsız yerlerden bölünerek iki veya üç farklı altyazı satırına dağılmasına neden olur. Bağlamı kopmuş, öznesi bir satırda, yüklemi başka bir satırda kalmış bu yarım cümleler, LLM tabanlı çeviri motorlarına satır satır gönderildiğinde çeviri kalitesi tamamen çöker; motor bağlamı kaybeder ve halüsinasyon üretir.<br><br>
nMerge, bu sorunu çözmek için "Fiziksel zamanlamaya değil, gramatikal bütünlüğe saygı duy" felsefesini benimser. spaCy kütüphanesini kullanarak cümlenin dilbilgisi anatomisini çıkarır, STT'nin uydurduğu sahte noktalama işaretlerini ezer ve çeviri motorunun metni tek parça, eksiksiz bir bağlam içinde görmesini sağlamak için zaman bariyerlerini yıkarak yarım kalan satırları birbirine diker.<br><br>
nMerge, altyazılardaki derin dilbilgisi analizlerini gerçekleştirmek için spaCy kütüphanesinin "en_core_web_sm" (English Core Web Small) isimli önceden eğitilmiş doğal dil işleme (NLP) modelini kalbinde taşır. Bu model, kelimelerin cümle içindeki sentaktik görevlerini (Part-of-Speech tagging) ve bağlaç, edat gibi havada kalan yapıları olağanüstü bir isabetle tespit edebilen, OntoNotes veri setiyle eğitilmiş hızlı ve kompakt bir evrişimli sinir ağıdır (CNN). Devasa dil modellerinin hantallığından ve API gecikmelerinden bilinçli olarak kaçınan nMerge, bu "hafif ama keskin zekalı" model sayesinde binlerce satırlık SRT dosyalarını işlemciyi yormadan, tamamen çevrimdışı (offline) olarak ve milisaniyeler içinde analiz eder.<br><br>
<b>Temel Yetenekler ve Algoritmik Çözümler</b><br>
<b>1. Zaman-Bağımsız Mutlak Gramer Birleştirmesi:</b> Geleneksel senkronizasyon araçlarının aksine nMerge, iki altyazı satırı arasındaki zaman farkını tamamen görmezden gelir. Eğer birinci satırın sonu ve ikinci satırın başlangıcı dilbilgisi açısından birbirinin devamıysa, aradan ne kadar zaman geçmiş olursa olsun bu iki satır tek bir metin bloğu haline getirilir. Çeviri motoruna eksiksiz bir metin sunmak için ekrandaki zamanlama feda edilir.<br><br>
<b>2. Şartsız Punctuation (Noktalama) Diktatörlüğü:</b> Satır sonundaki Virgül (,), Noktalı Virgül (;), İki Nokta (:), Üç Nokta (...) veya Çift/Üçlü Tire (--, ---) işaretleri görüldüğü anda, alt satırın büyük veya küçük harfle başlamasına bakılmaksızın iki satır derhal birleştirilir.<br><br>
<b>3. Derin POS (Part-of-Speech) Analizi ve Sahte Nokta İhlali:</b> STT yazılımları, konuşmacı duraksadığında cümlenin ortasına hatalı bir nokta (.) veya ünlem (!) koyabilir. nMerge, bu sahte noktalara aldanmaz. Satırın sonundaki noktalama işaretini geçici olarak görmezden gelir ve sondan geriye doğru ilk anlamlı kelimeyi bulur. Bu kelimenin NLP türü (POS Etiketi) bir Edat (ADP), Bağlaç (CCONJ, SCONJ), Yardımcı Fiil (AUX) veya Ek (PART) ise, sistem cümlenin henüz tamamlanmadığına karar verir. STT'nin koyduğu hatalı noktayı ezip geçerek alt satırla birleştirme işlemini zorlar.<br><br>
<b>4. Gelişmiş Regex ile Cerrahi Temizlik ve Korumalar:</b> Birleştirme işlemi sırasında oluşan yapısal bozukluklar düzenli ifadeler (Regex) ile temizlenir:<br>
- <i>Diyalog Koruması:</i> Alt satır tek bir tire (-) ile başlıyorsa, bu durum başka bir karakterin konuşmaya başladığının evrensel işaretidir. nMerge bunu anında algılar ve ne olursa olsun birleştirmeyi reddeder.<br>
- <i>Sahte Nokta İmhası:</i> İki satır birleştirilirken, arada kalan ve cümlenin yapısını bozan hatalı tekil noktalar ameliyat edilerek silinir.<br>
- <i>Kalıntı Temizliği:</i> Cümle başlarında veya sonlarında kalan üç noktalar ve yazar izi olan çift tireler temizlenerek metin pürüzsüzleştirilir.<br><br>
<b>5. Akıllı Nida ve Duygu İfadesi (Filler Words) Filtresi:</b> Altyazılarda tek başına bir satırı işgal eden "Mmm.", "Ah!", "Uh-huh" gibi çeviriye hiçbir anlam katmayan gevezelikler tamamen yok edilir. Kalan saf metinde kelime satırda tamamen yalnızsa, duygu ifadeleri sözlüğünde aranır ve eşleşme durumunda tüm satır silinir. Cümle içinde geçen "Oh, I see" gibi ifadelere dokunulmaz.<br><br>
<b>6. Hafızalı İmla ve Büyük/Küçük Harf Düzeltici:</b> STT yazılımlarının cümlenin ortasında anlamsızca büyük harfle başlattığı kelimeler spaCy üzerinden denetlenir. Eğer önceki satır noktayla bitmemişse, yeni satırın ilk kelimesinin büyük harfini ezer ve küçük harfe zorlar (özel isimler ve I zamiri hariç).
<br><hr><br>
<p style='text-align: center; color: #888;'><b>Developed by nutuzar | nMerge Otomasyon v1.0</b></p>
"""

EN_ABOUT_HTML = """
<h3 style='color: #2a82da;'>nMerge: Smart Subtitle (SRT) Preprocessor and Grammar Engine for LLM Translation Optimization</h3>
<br>
<b>Project Purpose and Philosophy</b><br>
nMerge is an NLP-supported preprocessing automation developed to prepare subtitle (SRT) files not for traditional viewing experiences, but for Large Language Model (LLM) based AI translation engines.<br><br>
Modern Speech-to-Text (STT) software references speakers' breathing patterns and scene silence durations (timestamps) rather than grammar rules when transcribing speech. This causes single sentences to be split at meaningless points and distributed across multiple subtitle lines. When these half-sentences, with their contexts broken and subjects disconnected from verbs, are sent line by line to LLM translation engines, translation quality completely collapses; the engine loses context and produces hallucinations.<br><br>
To solve this, nMerge adopts the philosophy: "Respect grammatical integrity, not physical timing." Using the spaCy library, it extracts the grammatical anatomy of the sentence, overwrites fake punctuation marks fabricated by the STT, and tears down time barriers to stitch fragmented lines together, ensuring the translation engine sees the text as a single, complete context.<br><br>
At its core, nMerge carries spaCy's pre-trained NLP model named "en_core_web_sm" (English Core Web Small) for deep grammatical analysis. This model is a fast and compact Convolutional Neural Network (CNN) trained on the OntoNotes dataset, capable of identifying syntactic roles of words (Part-of-Speech tagging) and dangling structures like conjunctions and adpositions with extraordinary accuracy. By consciously avoiding the clumsiness and API latencies of giant language models, nMerge analyzes thousands of lines of SRT files in milliseconds, completely offline, without straining the CPU.<br><br>
<b>Core Capabilities and Algorithmic Solutions</b><br>
<b>1. Time-Independent Absolute Grammar Merging:</b> Unlike traditional synchronization tools, nMerge completely ignores the time gap between two subtitle lines. If the end of the first line and the beginning of the second line are grammatical continuations, the lines are merged into a single text block regardless of the elapsed time. On-screen timing is sacrificed to provide a complete text to the translation engine.<br><br>
<b>2. Unconditional Punctuation Dictatorship:</b> Binding punctuation marks left intentionally by the STT or original translator are accepted as absolute merging commands. Comma (,), Semicolon (;), Colon (:), Ellipsis (...), or Double/Triple Dashes (--, ---) at the end of a line trigger immediate merging, regardless of capitalization.<br><br>
<b>3. Deep POS Analysis and Fake Period Override:</b> STT software may place erroneous periods (.) or exclamation marks (!) in the middle of a sentence during a speaker's pause. nMerge temporarily ignores trailing punctuation and finds the last meaningful word. If its NLP type (POS Tag) is an Adposition (ADP), Conjunction (CCONJ, SCONJ), Auxiliary (AUX), or Particle (PART), the system concludes the sentence is incomplete, overrides the fake period, and forces a merge with the next line.<br><br>
<b>4. Advanced Regex Surgical Cleaning and Protections:</b> Structural distortions caused by merging are cleaned using Regular Expressions:<br>
- <i>Dialogue Protection:</i> Refuses merging if the bottom line starts with a single dash (-), indicating a new speaker.<br>
- <i>Fake Period Annihilation:</i> Surgically removes isolated incorrect periods trapped between merged lines.<br>
- <i>Residue Cleaning:</i> Smooths text by cleaning leading/trailing ellipses and double dashes.<br><br>
<b>5. Smart Interjection and Filler Words Filter:</b> Isolated fillers like "Mmm.", "Ah!", "Uh-huh" that add no meaning to translation and confuse LLMs are completely eradicated if they match the emotion dictionary, preserving them only when embedded in valid sentences.<br><br>
<b>6. Stateful Orthography and Case Corrector:</b> Words meaninglessly capitalized mid-sentence by STT are inspected via spaCy. If the previous line didn't truly end with a period, the first word of the new line is forced to lowercase (unless it's a Proper Noun or "I"). Thus, 100% grammatically compliant blocks are sent to the LLM.
<br><hr><br>
<p style='text-align: center; color: #888;'><b>Developed by nutuzar | nMerge Otomasyon v1.0</b></p>
"""

LANG_DICT = {
    'tr': {
        'title': "nMerge - Alt Yazı İçi Cümle Birleştirici (v1.0)",
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
        'log_deleted_emo': "  -> Sadece duygu ifadesi içeren {} adet satır silindi.",
        'log_done': "\n--- İŞLEM TAMAMLANDI ---",
        'log_total_files': "Toplam {} dosya işlendi.",
        'log_total_del': "Toplam {} adet gereksiz duygu satırı silindi.",
        'err_pysubs2': "Kritik Hata: 'pysubs2' kütüphanesi bulunamadı!\nTerminalde çalıştırın: pip install pysubs2",
        'err_spacy': "Kritik Hata: 'spacy' kütüphanesi bulunamadı!\nTerminalde çalıştırın: pip install spacy",
        'err_spacy_model': "Kritik Hata: spaCy 'en_core_web_sm' modeli bulunamadı!\nTerminalde çalıştırın: python -m spacy download en_core_web_sm",
        'err_read_file': "Dosya okunamadı: {}\n{}",
        'err_save_file': "Kaydedilemedi: {}\n{}",
        'about_title': "Hakkında - nMerge",
        'about_html': TR_ABOUT_HTML
    },
    'en': {
        'title': "nMerge - Subtitle Intra-Sentence Merger (v1.0)",
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
        'log_deleted_emo': "  -> {} lines containing only emotion expressions were deleted.",
        'log_done': "\n--- PROCESS COMPLETED ---",
        'log_total_files': "Total {} files processed.",
        'log_total_del': "Total {} unnecessary emotion lines deleted.",
        'err_pysubs2': "Critical Error: 'pysubs2' library not found!\nRun in terminal: pip install pysubs2",
        'err_spacy': "Critical Error: 'spacy' library not found!\nRun in terminal: pip install spacy",
        'err_spacy_model': "Critical Error: spaCy 'en_core_web_sm' model not found!\nRun in terminal: python -m spacy download en_core_web_sm",
        'err_read_file': "Could not read file: {}\n{}",
        'err_save_file': "Could not save: {}\n{}",
        'about_title': "About - nMerge",
        'about_html': EN_ABOUT_HTML
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

def sadece_duygu_mu(metin, emotions_set):
    temiz = re.sub(r'<[^>]+>', '', metin)
    saf_metin = re.sub(r'[^\w\s-]', '', temiz).strip()
    if ' ' in saf_metin:
        return False
    if saf_metin.lower() in emotions_set:
        return True
    return False

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

def spacy_ile_birlestirmeli_mi(su_anki_metin, sonraki_metin, nlp):
    temiz_su = re.sub(r'<[^>]+>|\{[^}]+\}', '', su_anki_metin).strip()
    temiz_son = re.sub(r'<[^>]+>|\{[^}]+\}', '', sonraki_metin).strip()

    if not temiz_su or not temiz_son:
        return False

    if re.match(r'^-[^-]', temiz_son):
        return False

    if re.search(r'(\.{2,}|…|-{2,})$', temiz_su):
        return True

    if temiz_su.endswith((',', ';', ':')):
        return True

    doc1 = nlp(temiz_su)
    doc2 = nlp(temiz_son)

    if len(doc1) == 0 or len(doc2) == 0:
        return False

    first_token_doc2 = doc2[0]

    son_gercek_kelime = None
    for token in reversed(doc1):
        if not token.is_punct:
            son_gercek_kelime = token
            break
    
    if son_gercek_kelime is not None:
        tehlikeli_bitisler = ['ADP', 'CCONJ', 'SCONJ', 'DET', 'PART', 'AUX']
        if son_gercek_kelime.pos_ in tehlikeli_bitisler:
            return True

    if first_token_doc2.is_lower:
        return True

    return False

# --- THREAD ---

class WorkerThread(QThread):
    log_signal = pyqtSignal(str)
    progress_signal = pyqtSignal(int)
    finished_signal = pyqtSignal(int, int)
    error_signal = pyqtSignal(str)

    def __init__(self, files, output_name, emotions_set, lang_dict):
        super().__init__()
        self.files = files
        self.output_name = output_name
        self.emotions_set = set(e.lower() for e in emotions_set)
        self.lang = lang_dict

    def run(self):
        try:
            import pysubs2
        except ImportError:
            self.error_signal.emit(self.lang['err_pysubs2'])
            return

        try:
            import spacy
        except ImportError:
            self.error_signal.emit(self.lang['err_spacy'])
            return

        self.log_signal.emit(self.lang['log_model_loading'])
        try:
            nlp = spacy.load("en_core_web_sm")
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
                
                while i + 1 < len(subs):
                    sonraki_satir = subs[i+1]
                    
                    su_anki_metin = su_anki_satir.text.strip()
                    sonraki_metin = sonraki_satir.text.strip()

                    if spacy_ile_birlestirmeli_mi(su_anki_metin, sonraki_metin, nlp):
                        su_anki_satir.end = sonraki_satir.end
                        su_anki_satir.text = baglanti_hatalarini_temizle_ve_birlestir(su_anki_metin, sonraki_metin)
                        su_anki_metin = su_anki_satir.text
                        i += 1
                    else:
                        break
                
                su_anki_satir.text = temizle_metin(su_anki_satir.text)
                su_anki_satir.text, yeni_cumle_mi = spacy_ile_imla_duzelt(su_anki_satir.text, yeni_cumle_mi, nlp)
                
                if sadece_duygu_mu(su_anki_satir.text, self.emotions_set):
                    silinen_satir_sayisi += 1
                    total_deleted += 1
                    i += 1
                    continue
                
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
        self.resize(800, 600)
        layout = QVBoxLayout(self)
        
        browser = QTextBrowser()
        browser.setOpenExternalLinks(True)
        browser.setHtml(html_content)
        
        # Adding a bit of padding and font configuration for better readability
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
        self.resize(900, 700)
        
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout(main_widget)
        
        # TOP LAYOUT FOR LANGUAGE SWITCH
        top_layout = QHBoxLayout()
        top_layout.addStretch()
        
        self.btn_tr = QPushButton("TR")
        self.btn_tr.clicked.connect(lambda: self.switch_language("tr"))
        self.btn_en = QPushButton("EN")
        self.btn_en.clicked.connect(lambda: self.switch_language("en"))
        
        top_layout.addWidget(self.btn_tr)
        top_layout.addWidget(self.btn_en)
        main_layout.addLayout(top_layout)
        
        # SPLITTER FOR LEFT & RIGHT PANELS
        splitter = QSplitter(Qt.Horizontal)
        
        # SOL PANEL: Ayarlar ve Duygu İfadeleri
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
        self.emo_add_btn.setStyleSheet("background-color: #1e90ff; color: white; font-weight: bold;")
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
        
        # SAĞ PANEL: Dosyalar ve İşlem
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(0, 0, 0, 0)
        
        self.file_group = QGroupBox()
        file_layout = QVBoxLayout()
        self.file_list = DragDropListWidget()
        file_layout.addWidget(self.file_list)
        
        file_btns_layout = QHBoxLayout()
        self.add_file_btn = QPushButton()
        self.add_file_btn.setStyleSheet("background-color: #1e90ff; color: white; font-weight: bold;")
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
        
        # ALT PANEL: Telemetri ve Kontroller
        bottom_layout = QVBoxLayout()
        self.telemetry_label = QLabel()
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMaximumHeight(200)
        bottom_layout.addWidget(self.telemetry_label)
        bottom_layout.addWidget(self.log_text)
        
        sys_btns_layout = QHBoxLayout()
        self.about_btn = QPushButton()
        self.about_btn.setStyleSheet("background-color: #1e90ff; color: white; font-weight: bold;")
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
        
        self.start_btn.setText(self.lang['btn_start'])
        self.open_folder_btn.setText(self.lang['btn_open_folder'])
        self.telemetry_label.setText(self.lang['telemetry'])
        
        self.about_btn.setText(self.lang['btn_about'])
        self.close_btn.setText(self.lang['btn_close'])
        self.prepared_by_label.setText(self.lang['prepared_by'])
        
        # Highlight active language button
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
                self.emotion_list.addItem(word)
                self.log_text.append(self.lang['log_emo_added'].format(word))
        self.emo_input.clear()

    def del_emotion(self):
        selected_items = self.emotion_list.selectedItems()
        if not selected_items:
            return
        
        for item in selected_items:
            word = item.text()
            self.emotion_list.takeItem(self.emotion_list.row(item))
            if word in self.config["emotions"]:
                self.config["emotions"].remove(word)
        save_config(self.config)
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

        self.worker = WorkerThread(files, out_name, emotions, self.lang)
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
    except ImportError as e:
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Critical)
        msg.setText(f"Gerekli kütüphaneler eksik (Missing libraries): {e.name}")
        msg.setInformativeText(f"Lütfen terminali açıp şu komutu çalıştırın (Run in terminal):\n\npip install pysubs2 spacy PyQt5")
        msg.setWindowTitle("Eksik Kütüphane / Missing Library")
        msg.exec_()
        sys.exit(1)
        
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
