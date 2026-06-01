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
from PyQt5.QtGui import QFont

if getattr(sys, 'frozen', False):
    APP_DIR = os.path.dirname(sys.executable)
else:
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
<h3 style='color: #0a84ff; font-family: -apple-system, sans-serif;'>nMerge v1.3: LLM Çeviri Optimizasyonu İçin Akıllı Altyazı (SRT) Ön İşlemci</h3>
<br>
<b>Projenin Amacı ve Felsefesi</b><br>
nMerge, altyazı (SRT) dosyalarını geleneksel izleme deneyimi için değil, Büyük Dil Modeli (LLM) tabanlı yapay zeka çeviri motorlarına hazırlamak amacıyla geliştirilmiş, NLP destekli bir ön işlem otomasyonudur.<br><br>
Modern Speech-to-Text (STT) yazılımları, konuşma metnini yazıya dökerken gramer kurallarını değil, fiziksel süreleri referans alır. nMerge, bu sorunu çözmek için "Fiziksel zamanlamaya değil, gramatikal bütünlüğe saygı duy" felsefesini benimser.<br><br>
<b>v1.3 Güncellemeleri ve İşlem Boru Hattı:</b><br><br>
<b>1. "Sadeleştirme" Modu (Kullanıcı İradesi vs. spaCy Otonomisi):</b><br>
Yeni eklenen "Sadeleştirme" seçeneği kapalıyken, sistem sadece sizin tanımladığınız <i>Duygu İfadeleri (Sözlük)</i> listesine itaat eder. Ancak bu kutuyu işaretlerseniz, spaCy'nin tasmaları çıkarılır ve metindeki tüm INTJ (Nida) etiketli kelimeler acımasızca temizlenir.<br><br>
<b>2. ALL CAPS Normalizasyonu ve Dokunulmazlık İlkesi:</b><br> 
Karakterlerinin %80'i büyük harf olan satırlar tespit edilip spaCy için geçici olarak küçük harfe indirgenir. Alt satırla birleştirme kararı verilirken her zaman dosyanın <b>Orijinal DNA'sı</b> (ilk harfin durumu) referans alınır.<br><br>
<b>3. Alfanümerik Koruma:</b> Sayılar ve rakamlar "isalnum()" kalkanıyla korunarak nida temizliği sırasında istatistiksel hata kurbanı olmaktan kurtarılır.<br><br>
<b>4. Hafızalı İmla Motoru (Stateful Orthography):</b> Cümlenin ortasında kalan haksız büyük harfler küçük harfe zorlanır. Döngü, cümlenin nasıl bittiğini hafızasına yazar ve sonraki satırın kaderini belirler.<br><br>
<br><hr style='border: 1px solid #3a3a3c;'><br>
<p style='text-align: center; color: #8e8e93;'><b>Developed by nutuzar | nMerge Otomasyon v1.3 (Apple Dark Mode Edition)</b></p>
"""

EN_ABOUT_HTML = """
<h3 style='color: #0a84ff; font-family: -apple-system, sans-serif;'>nMerge v1.3: Smart Subtitle (SRT) Preprocessor for LLM Optimization</h3>
<br>
<b>Project Purpose and Philosophy</b><br>
nMerge is an NLP-supported preprocessing automation developed to prepare subtitle (SRT) files for Large Language Model (LLM) based AI translation engines.<br><br>
Modern Speech-to-Text (STT) software references speakers' breathing patterns rather than grammar rules. nMerge adopts the philosophy: "Respect grammatical integrity, not physical timing."<br><br>
<b>v1.3 Updates & Execution Pipeline:</b><br><br>
<b>1. "Simplification" Mode (User Will vs. spaCy Autonomy):</b><br>
When the new "Simplification" option is disabled, the system obeys solely your custom <i>Emotion Expressions</i> list. If checked, spaCy's leash is removed, and all words tagged as INTJ (Interjection) are aggressively eradicated.<br><br>
<b>2. ALL CAPS Normalization & Immutability Principle:</b><br>
Lines with >80% uppercase characters are temporarily lowered for spaCy. Merging decisions are strictly based on the <b>Original DNA</b> (the actual first letter state) of the file.<br><br>
<b>3. Alphanumeric Shield:</b> Pure numbers are protected via the "isalnum()" shield, preventing accidental deletion during interjection cleaning.<br><br>
<b>4. Stateful Orthography:</b> Unjustified capital letters in the middle of sentences are forced to lowercase. The system remembers sentence endings to format the next line accordingly.<br><br>
<br><hr style='border: 1px solid #3a3a3c;'><br>
<p style='text-align: center; color: #8e8e93;'><b>Developed by nutuzar | nMerge Automation v1.3 (Apple Dark Mode Edition)</b></p>
"""

LANG_DICT = {
    'tr': {
        'title': "nMerge - Alt Yazı İçi Cümle Birleştirici (v1.3)",
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
        'cb_simplify': "Sadeleştirme (spaCy INTJ Agresif Temizlik)",
        'cb_debug_mode': "Gelişmiş Telemetri (Röntgen) Modu",
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
        'about_title': "Hakkında - nMerge v1.3",
        'about_html': TR_ABOUT_HTML,
        'log_debug_rejected': "[RÖNTGEN] REDDEDİLDİ: '{}' + '{}'\n  -> Sebep: {}"
    },
    'en': {
        'title': "nMerge - Subtitle Intra-Sentence Merger (v1.3)",
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
        'cb_simplify': "Simplify (spaCy INTJ Aggressive Clean)",
        'cb_debug_mode': "Advanced Telemetry (X-Ray) Mode",
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
        'about_title': "About - nMerge v1.3",
        'about_html': EN_ABOUT_HTML,
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
    return {"emotions": DEFAULT_EMOTIONS, "default_output_name": "orijinal_film", "lang": "tr", "simplify_mode": False}

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

def nida_temizle_spacy(metin, emotions_set, nlp, use_spacy_intj=False):
    """
    v1.3: Sadeleştirme modu devredeyse spaCy'nin INTJ kuralı da listeye ek olarak çalışır.
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
            
        # Öncelik özel sözlükte, eğer orada yoksa ve Sadeleştirme açıksa spaCy'nin fikrini al
        if kelime_saf in emotions_set:
            silinecek_kelimeler.append(token.text)
        elif use_spacy_intj and token.pos_ == "INTJ":
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

    def __init__(self, files, output_name, emotions_set, lang_dict, debug_mode, use_spacy_intj):
        super().__init__()
        self.files = files
        self.output_name = output_name
        self.emotions_set = set(e.lower() for e in emotions_set)
        self.lang = lang_dict
        self.debug_mode = debug_mode
        self.use_spacy_intj = use_spacy_intj

    def run(self):
        try:
            import pysubs2
        except ImportError:
            self.error_signal.emit(self.lang['err_pysubs2'])
            return

        try:
            import spacy
            import en_core_web_sm
        except ImportError:
            self.error_signal.emit(self.lang['err_spacy'] + "\n(Veya model eksik, lütfen 'python -m spacy download en_core_web_sm' komutunu çalıştırın)")
            return

        self.log_signal.emit(self.lang['log_model_loading'])
        try:
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
                su_anki_satir.text = nida_temizle_spacy(su_anki_satir.text, self.emotions_set, nlp, self.use_spacy_intj)
                
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
        font.setPointSize(12)
        browser.setFont(font)
        
        layout.addWidget(browser)
        
        btn = QPushButton(close_text)
        btn.setObjectName("btnPrimary")
        btn.clicked.connect(self.accept)
        btn.setMinimumHeight(40)
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
        self.resize(1000, 750)
        
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout(main_widget)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        top_layout = QHBoxLayout()
        top_layout.addStretch()
        
        self.btn_tr = QPushButton("TR")
        self.btn_tr.setFixedSize(50, 30)
        self.btn_tr.clicked.connect(lambda: self.switch_language("tr"))
        self.btn_en = QPushButton("EN")
        self.btn_en.setFixedSize(50, 30)
        self.btn_en.clicked.connect(lambda: self.switch_language("en"))
        
        top_layout.addWidget(self.btn_tr)
        top_layout.addWidget(self.btn_en)
        main_layout.addLayout(top_layout)
        
        splitter = QSplitter(Qt.Horizontal)
        splitter.setHandleWidth(10)
        
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(0, 0, 10, 0)
        
        self.output_group = QGroupBox()
        output_layout = QVBoxLayout()
        output_layout.setSpacing(10)
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
        emotion_layout.setSpacing(10)
        self.emotion_list = QListWidget()
        for e in sorted(self.config.get("emotions", [])):
            self.emotion_list.addItem(e)
        emotion_layout.addWidget(self.emotion_list)
        
        emo_add_layout = QHBoxLayout()
        self.emo_input = QLineEdit()
        self.emo_input.returnPressed.connect(self.add_emotion)
        self.emo_add_btn = QPushButton()
        self.emo_add_btn.setObjectName("btnPrimary")
        self.emo_add_btn.clicked.connect(self.add_emotion)
        emo_add_layout.addWidget(self.emo_input)
        emo_add_layout.addWidget(self.emo_add_btn)
        emotion_layout.addLayout(emo_add_layout)
        
        self.emo_del_btn = QPushButton()
        self.emo_del_btn.setObjectName("btnDestructive")
        self.emo_del_btn.clicked.connect(self.del_emotion)
        emotion_layout.addWidget(self.emo_del_btn)
        self.emotion_group.setLayout(emotion_layout)
        left_layout.addWidget(self.emotion_group)
        
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(10, 0, 0, 0)
        right_layout.setSpacing(15)
        
        self.file_group = QGroupBox()
        file_layout = QVBoxLayout()
        file_layout.setSpacing(10)
        self.file_list = DragDropListWidget()
        file_layout.addWidget(self.file_list)
        
        file_btns_layout = QHBoxLayout()
        self.add_file_btn = QPushButton()
        self.add_file_btn.setObjectName("btnPrimary")
        self.add_file_btn.clicked.connect(self.add_files)
        self.rem_file_btn = QPushButton()
        self.rem_file_btn.setObjectName("btnDestructive")
        self.rem_file_btn.clicked.connect(self.remove_files)
        self.clear_file_btn = QPushButton()
        self.clear_file_btn.setObjectName("btnDestructive")
        self.clear_file_btn.clicked.connect(self.file_list.clear)
        file_btns_layout.addWidget(self.add_file_btn)
        file_btns_layout.addWidget(self.rem_file_btn)
        file_btns_layout.addWidget(self.clear_file_btn)
        file_layout.addLayout(file_btns_layout)
        self.file_group.setLayout(file_layout)
        right_layout.addWidget(self.file_group)
        
        options_layout = QVBoxLayout()
        self.simplify_cb = QCheckBox()
        self.simplify_cb.setStyleSheet("color: #ff9f0a; font-weight: bold; font-size: 14px;")
        self.simplify_cb.setChecked(self.config.get("simplify_mode", False))
        self.simplify_cb.stateChanged.connect(self.update_config_simplify)
        
        self.debug_cb = QCheckBox()
        self.debug_cb.setStyleSheet("color: #32d74b; font-weight: bold;")
        
        options_layout.addWidget(self.simplify_cb)
        options_layout.addWidget(self.debug_cb)
        right_layout.addLayout(options_layout)

        action_layout = QHBoxLayout()
        self.start_btn = QPushButton()
        self.start_btn.setObjectName("btnSuccess")
        self.start_btn.setMinimumHeight(45)
        font = self.start_btn.font()
        font.setPointSize(14)
        font.setBold(True)
        self.start_btn.setFont(font)
        self.start_btn.clicked.connect(self.start_processing)
        
        self.open_folder_btn = QPushButton()
        self.open_folder_btn.setObjectName("btnWarning")
        self.open_folder_btn.setMinimumHeight(45)
        self.open_folder_btn.setEnabled(False)
        self.open_folder_btn.clicked.connect(self.open_output_folder)
        
        action_layout.addWidget(self.start_btn)
        action_layout.addWidget(self.open_folder_btn)
        right_layout.addLayout(action_layout)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        right_layout.addWidget(self.progress_bar)
        
        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        splitter.setSizes([350, 850])
        main_layout.addWidget(splitter)
        
        bottom_layout = QVBoxLayout()
        bottom_layout.setSpacing(10)
        self.telemetry_label = QLabel()
        self.telemetry_label.setStyleSheet("color: #8e8e93; font-weight: bold;")
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMaximumHeight(200)
        bottom_layout.addWidget(self.telemetry_label)
        bottom_layout.addWidget(self.log_text)
        
        sys_btns_layout = QHBoxLayout()
        self.about_btn = QPushButton()
        self.about_btn.setObjectName("btnPrimary")
        self.about_btn.clicked.connect(self.show_about)
        
        self.close_btn = QPushButton()
        self.close_btn.setObjectName("btnDestructive")
        self.close_btn.clicked.connect(self.exit_app)
        
        self.prepared_by_label = QLabel()
        self.prepared_by_label.setStyleSheet("color: #8e8e93;")
        
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
        
        self.simplify_cb.setText(self.lang['cb_simplify'])
        self.debug_cb.setText(self.lang['cb_debug_mode'])
        self.start_btn.setText(self.lang['btn_start'])
        self.open_folder_btn.setText(self.lang['btn_open_folder'])
        self.telemetry_label.setText(self.lang['telemetry'])
        
        self.about_btn.setText(self.lang['btn_about'])
        self.close_btn.setText(self.lang['btn_close'])
        self.prepared_by_label.setText(self.lang['prepared_by'])
        
        if self.current_lang == "tr":
            self.btn_tr.setStyleSheet("background-color: #0a84ff; color: white; border-radius: 4px; font-weight: bold;")
            self.btn_en.setStyleSheet("background-color: #3a3a3c; color: #f5f5f7; border-radius: 4px;")
        else:
            self.btn_en.setStyleSheet("background-color: #0a84ff; color: white; border-radius: 4px; font-weight: bold;")
            self.btn_tr.setStyleSheet("background-color: #3a3a3c; color: #f5f5f7; border-radius: 4px;")

    def exit_app(self):
        self.close()

    def update_config_name(self):
        self.config["default_output_name"] = self.output_name_input.text()
        save_config(self.config)

    def update_config_simplify(self):
        self.config["simplify_mode"] = self.simplify_cb.isChecked()
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
        is_simplify = self.simplify_cb.isChecked()

        self.worker = WorkerThread(files, out_name, emotions, self.lang, is_debug, is_simplify)
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
    
    apple_dark_qss = """
    QWidget {
        background-color: #1c1c1e;
        color: #f5f5f7;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
        font-size: 14px;
    }
    QGroupBox {
        border: 1px solid #3a3a3c;
        border-radius: 10px;
        margin-top: 4ex;
        font-weight: bold;
        color: #8e8e93;
    }
    QGroupBox::title {
        subcontrol-origin: margin;
        subcontrol-position: top center;
        padding: 0 10px;
    }
    QLineEdit, QTextEdit, QListWidget, QTextBrowser {
        background-color: #2c2c2e;
        border: 1px solid #3a3a3c;
        border-radius: 8px;
        padding: 8px;
        color: #f5f5f7;
        selection-background-color: #0a84ff;
    }
    QLineEdit:focus, QTextEdit:focus, QListWidget:focus {
        border: 1px solid #0a84ff;
    }
    QPushButton {
        background-color: #3a3a3c;
        border: none;
        border-radius: 8px;
        padding: 8px 16px;
        color: #f5f5f7;
        font-weight: bold;
    }
    QPushButton:hover {
        background-color: #4a4a4c;
    }
    QPushButton:pressed {
        background-color: #2c2c2e;
    }
    QPushButton:disabled {
        background-color: #2c2c2e;
        color: #555555;
    }
    #btnPrimary {
        background-color: #0a84ff;
        color: white;
    }
    #btnPrimary:hover {
        background-color: #0070e0;
    }
    #btnDestructive {
        background-color: #ff453a;
        color: white;
    }
    #btnDestructive:hover {
        background-color: #d70015;
    }
    #btnSuccess {
        background-color: #30d158;
        color: black;
    }
    #btnSuccess:hover {
        background-color: #28b84d;
    }
    #btnSuccess:disabled {
        background-color: #1a5226;
        color: #555555;
    }
    #btnWarning {
        background-color: #ffd60a;
        color: black;
    }
    #btnWarning:hover {
        background-color: #e5c009;
    }
    #btnWarning:disabled {
        background-color: #665604;
        color: #555555;
    }
    QProgressBar {
        border: 1px solid #3a3a3c;
        border-radius: 8px;
        text-align: center;
        background-color: #2c2c2e;
        color: white;
        font-weight: bold;
    }
    QProgressBar::chunk {
        background-color: #0a84ff;
        border-radius: 7px;
    }
    QCheckBox {
        spacing: 10px;
    }
    QCheckBox::indicator {
        width: 18px;
        height: 18px;
        border-radius: 4px;
        border: 1px solid #555;
        background-color: #2c2c2e;
    }
    QCheckBox::indicator:checked {
        background-color: #0a84ff;
        border: 1px solid #0a84ff;
    }
    QSplitter::handle {
        background-color: #1c1c1e;
    }
    """
    app.setStyleSheet(apple_dark_qss)

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