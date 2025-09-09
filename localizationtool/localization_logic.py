# # localizationtool/localization_logic.py
# import polib
# import csv
# import zipfile
# import os
# import shutil
# from datetime import datetime
# from deep_translator import GoogleTranslator, exceptions
# import re
# from charset_normalizer import from_path
# import time

# class ColabLocalizationTool:
#     def __init__(self):
#         self.pot_file_path = None
#         self.zip_file_path = None
#         self.csv_file_path = None
#         self.target_languages = []
#         self.temp_dir = "/tmp/po_extract"
#         self.simple_placeholder_regex = re.compile(r'%\d+\$\w|%[a-zA-Z_]\w*|%%|%[sSdD]')
#         self.complex_placeholder_regex = re.compile(r'(&ldquo;%[^&]+?&rdquo;)')
#         self.translation_rules = {
#             "%s min read": {
#                 "ja": "%s分で読めます",
#                 "it": "%s min di lettura",
#                 "nl": "%s min gelezen",
#                 "pl": "%s min czytania",
#                 "pt": "%s min de leitura",
#                 "de": "%s Min. Lesezeit",
#                 "ar": "قراءة في %s دقيقة",
#                 "fr": "%s min de lecture",
#                 "ru": "%s мин. чтения"
#             }
#         }

#     def _display_status(self, message):
#         print(f"\n--- STATUS: {message} ---")
    
#     def _display_error(self, message):
#         print(f"\n--- ERROR: {message} ---")

#     def _parse_glossary_csv(self, csv_file_path):
#         glossary_lookup = {}
#         try:
#             detected = from_path(csv_file_path).best()
#             encoding = detected.encoding if detected else 'utf-8'
#             with open(csv_file_path, 'r', encoding=encoding) as f:
#                 reader = csv.DictReader(f)
#                 for row in reader:
#                     key = (row["Original String"].strip(), row.get("Context", "").strip())
#                     cleaned_translation = self._normalize_placeholders(row["Translated String"].strip())
#                     glossary_lookup[key] = cleaned_translation
#         except Exception as e:
#             self._display_error(f"Glossary parse error: {e}")
#         return glossary_lookup

#     def _normalize_placeholders(self, msgstr):
#         msgstr = re.sub(r'%\s*(\d+)\s*\$\s*[sSdD]', r'%\1$s', msgstr)
#         return msgstr

#     def _extract_and_parse_existing_pos(self, zip_file_path):
#         existing_po_lookup = {}
#         if os.path.exists(self.temp_dir):
#             shutil.rmtree(self.temp_dir)
#         os.makedirs(self.temp_dir)
#         try:
#             with zipfile.ZipFile(zip_file_path, 'r') as zf:
#                 for member in zf.namelist():
#                     if member.endswith('.po'):
#                         zf.extract(member, self.temp_dir)
#                         path = os.path.join(self.temp_dir, member)
#                         try:
#                             po = polib.pofile(path)
#                             for entry in po:
#                                 key = (entry.msgid, entry.msgctxt or '')
#                                 cleaned_msgstr = entry.msgstr
#                                 if cleaned_msgstr:
#                                     cleaned_msgstr = self._normalize_placeholders(cleaned_msgstr)
#                                     if self._placeholders_are_valid(entry.msgid, cleaned_msgstr):
#                                         cleaned_msgstr = self._clean_translated_text(cleaned_msgstr)
#                                         existing_po_lookup[key] = cleaned_msgstr
#                         except Exception as e:
#                             self._display_error(f"Error parsing PO: {e}")
#         except Exception as e:
#             self._display_error(f"Error extracting ZIP: {e}")
#         finally:
#             shutil.rmtree(self.temp_dir, ignore_errors=True)
#         return existing_po_lookup

#     def _placeholders_are_valid(self, original, translated):
#         try:
#             orig_ph = self._get_placeholders(original)
#             trans_ph = self._get_placeholders(translated)
#             return set(orig_ph) == set(trans_ph) and len(orig_ph) == len(trans_ph)
#         except Exception as e:
#             self._display_error(f"Placeholder validation failed: {e}")
#             return False

#     def _get_placeholders(self, text):
#         simple_placeholders = self.simple_placeholder_regex.findall(text)
#         complex_placeholders = self.complex_placeholder_regex.findall(text)
#         all_placeholders = list(set(simple_placeholders + complex_placeholders))
#         return all_placeholders

#     def _protect_placeholders(self, text):
#         placeholders = self._get_placeholders(text)
#         placeholder_map = {}
#         protected_text = text
#         placeholders.sort(key=len, reverse=True)
#         for i, ph in enumerate(placeholders):
#             token = f"PH_{i}_TOKEN"
#             placeholder_map[token] = ph
#             protected_text = protected_text.replace(ph, token)
#         return protected_text, placeholder_map

#     def _restore_placeholders(self, text, placeholder_map):
#         for token in placeholder_map:
#             pattern = r'\s*'.join(list(token))
#             regex = re.compile(pattern, flags=re.IGNORECASE)
#             text = regex.sub(token, text)
#         for token, ph in placeholder_map.items():
#             text = text.replace(token, ph)
#         return text

#     def _clean_translated_text(self, text):
#         text = re.sub(r'&\s*(#?\w+)\s*;', r'&\1;', text)
#         text = re.sub(r'\s+([.,!?;:])', r'\1', text)
#         text = re.sub(r'([.,!?;:])\s+', r'\1 ', text)
#         text = re.sub(r'(\s+)(”|\))', r'\2', text)
#         text = re.sub(r'(“|\()\s+', r'\1', text)
#         return text

#     def _is_likely_untranslated(self, original_text, translated_text):
#         protected_orig, _ = self._protect_placeholders(original_text)
#         protected_trans, _ = self._protect_placeholders(translated_text)
#         raw_orig = re.sub(r'PH_\d+_TOKEN', '', protected_orig)
#         raw_trans = re.sub(r'PH_\d+_TOKEN', '', protected_trans)
#         return raw_orig.strip().lower() == raw_trans.strip().lower()

#     def _apply_custom_rules(self, msgid, target_lang):
#         """Checks and applies custom translation rules."""
#         if msgid in self.translation_rules and target_lang in self.translation_rules[msgid]:
#             return self.translation_rules[msgid][target_lang]
#         return None

#     def _is_valid_translation(self, text):
#         error_signs = [
#             "Error 500",
#             "That’s an error",
#             "There was an error",
#             "<html", "</html>", "<body>", "</body>",
#             "Please try again later",
#         ]
#         lowered = text.lower()
#         for sign in error_signs:
#             if sign.lower() in lowered:
#                 return False
#         return True

#     def _fallback_translate(self, text, target_lang, retries=3, delay=1):
#         protected_text, placeholder_map = self._protect_placeholders(text)
#         for i in range(retries):
#             try:
#                 translator = GoogleTranslator(source='auto', target=target_lang)
#                 translated_protected = translator.translate(protected_text)
#                 translated_protected = re.sub(r"&\s+([a-zA-Z]+)\s*;", r"&\1;", translated_protected)
#                 translated = self._restore_placeholders(translated_protected, placeholder_map)
#                 translated = self._clean_translated_text(translated)
#                 if not self._is_valid_translation(translated):
#                     self._display_error(f"Invalid translation detected for '{text}' in '{target_lang}'. Using original text as fallback.")
#                     return text
#                 return translated
#             except exceptions.NotValidPayload as e:
#                 self._display_error(f"Invalid payload for '{text}'. Error: {e}")
#                 break
#             except Exception as e:
#                 self._display_error(f"Translation attempt {i + 1}/{retries} failed for '{text}' to '{target_lang}': {e}")
#                 if i < retries - 1:
#                     time.sleep(delay)
#                 else:
#                     return text
#         return text

#     def _process_translation(self, pot_entry, glossary_lookup, existing_po_lookup, target_lang):
#         msgid = pot_entry.msgid
#         msgctxt = pot_entry.msgctxt or ''
#         key = (msgid, msgctxt)
#         custom_translation = self._apply_custom_rules(msgid, target_lang)
#         if custom_translation:
#             return custom_translation, "Custom Rule"
#         if key in glossary_lookup:
#             glossary_trans = glossary_lookup[key]
#             if not self._placeholders_are_valid(msgid, glossary_trans) or self._is_likely_untranslated(msgid, glossary_trans):
#                 return self._fallback_translate(msgid, target_lang), "Glossary (Fuzzy)"
#             return glossary_trans, "Glossary"
#         if key in existing_po_lookup:
#             existing_translation = existing_po_lookup[key]
#             if not self._placeholders_are_valid(msgid, existing_translation) or self._is_likely_untranslated(msgid, existing_translation):
#                 return self._fallback_translate(msgid, target_lang), "Existing PO (Fuzzy)"
#             return existing_translation, "Existing PO"
#         return self._fallback_translate(msgid, target_lang), "Machine Translation"

#     def run(self, pot_path, zip_path, csv_path, target_langs, output_dir):
#         self._display_status("Starting WP Localization Tool")
        
#         self.pot_file_path = pot_path
#         self.zip_file_path = zip_path
#         self.csv_file_path = csv_path
#         self.target_languages = target_langs
        
#         try:
#             if not self.pot_file_path or not os.path.exists(self.pot_file_path):
#                 self._display_error("POT file not found.")
#                 return None
            
#             pot_file = polib.pofile(self.pot_file_path)
#             glossary = self._parse_glossary_csv(self.csv_file_path) if self.csv_file_path and os.path.exists(self.csv_file_path) else {}
#             existing = self._extract_and_parse_existing_pos(self.zip_file_path) if self.zip_file_path and os.path.exists(self.zip_file_path) else {}
            
#             for target_language in self.target_languages:
#                 self._display_status(f"Translating into {target_language}...")
#                 po = polib.POFile()
#                 now = datetime.now().strftime("%Y-%m-%d %H:%M:%S+0000")
                
#                 po.metadata = {
#                     'Project-Id-Version': 'Colab Free',
#                     'POT-Creation-Date': now,
#                     'PO-Revision-Date': now,
#                     'Language': target_language,
#                     'MIME-Version': '1.0',
#                     'Content-Type': 'text/plain; charset=UTF-8',
#                     'Content-Transfer-Encoding': '8bit',
#                     'X-Generator': 'Colab Tool'
#                 }
                
#                 for entry in pot_file:
#                     if not entry.msgid:
#                         continue
#                     try:
#                         translated_msgstr, source = self._process_translation(entry, glossary, existing, target_language)
#                         new_entry = polib.POEntry(
#                             msgid=entry.msgid,
#                             msgstr=translated_msgstr,
#                             msgctxt=entry.msgctxt,
#                             occurrences=entry.occurrences,
#                             comment=entry.comment,
#                             tcomment=entry.tcomment
#                         )
#                         if "Fuzzy" in source or "Fallback" in source:
#                             new_entry.flags.append("fuzzy")
#                         po.append(new_entry)
#                     except Exception as e:
#                         self._display_error(f"Failed to translate string '{entry.msgid[:50]}...'. Error: {e}")
#                         new_entry = polib.POEntry(
#                             msgid=entry.msgid,
#                             msgstr='',
#                             msgctxt=entry.msgctxt,
#                             occurrences=entry.occurrences,
#                             comment=entry.comment,
#                             tcomment=entry.tcomment
#                         )
#                         new_entry.flags.append("fuzzy")
#                         po.append(new_entry)
                
#                 # Logic to handle versioning
#                 counter = 0
#                 while True:
#                     suffix = f"-{counter}" if counter > 0 else ""
#                     out_po = os.path.join(output_dir, f"{target_language}{suffix}.po")
#                     out_mo = os.path.join(output_dir, f"{target_language}{suffix}.mo")
#                     if not os.path.exists(out_po) and not os.path.exists(out_mo):
#                         po.save(out_po)
#                         po.save_as_mofile(out_mo)
#                         break
#                     counter += 1

#             self._display_status("Translation complete.")
#             return True
        
#         except Exception as e:
#             self._display_error(f"Unexpected error during setup or file processing: {e}")
#             return False



# # localizationtool/localization_logic.py
# import polib
# import csv
# import zipfile
# import os
# import shutil
# from datetime import datetime
# from deep_translator import GoogleTranslator, exceptions
# import re
# from charset_normalizer import from_path
# import time
# import json

# class ColabLocalizationTool:
#     def __init__(self, memory_file="translation_memory.json"):
#         self.pot_file_path = None
#         self.zip_file_path = None
#         self.csv_file_path = None
#         self.target_languages = []
#         self.temp_dir = "/tmp/po_extract"
#         self.memory_file = memory_file
#         self.memory = self._load_memory()
#         self.simple_placeholder_regex = re.compile(r'%\d+\$\w|%[a-zA-Z_]\w*|%%|%[sSdD]')
#         self.complex_placeholder_regex = re.compile(r'(&ldquo;%[^&]+?&rdquo;)')
#         self.translation_rules = {
#             "%s min read": {
#                 "ja": "%s分で読めます",
#                 "it": "%s min di lettura",
#                 "nl": "%s min gelezen",
#                 "pl": "%s min czytania",
#                 "pt": "%s min de leitura",
#                 "de": "%s Min. Lesezeit",
#                 "ar": "قراءة في %s دقيقة",
#                 "fr": "%s min de lecture",
#                 "ru": "%s мин. чтения"
#             }
#         }

#     # --- Memory Handling ---
#     def _load_memory(self):
#         if os.path.exists(self.memory_file):
#             try:
#                 with open(self.memory_file, 'r', encoding='utf-8') as f:
#                     return json.load(f)
#             except Exception:
#                 return {}
#         return {}

#     def _save_memory(self):
#         try:
#             with open(self.memory_file, 'w', encoding='utf-8') as f:
#                 json.dump(self.memory, f, ensure_ascii=False, indent=2)
#         except Exception as e:
#             self._display_error(f"Failed to save memory file: {e}")

#     def _get_memory_translation(self, msgid, target_lang):
#         if msgid in self.memory and target_lang in self.memory[msgid]:
#             return self.memory[msgid][target_lang]
#         return None

#     def _update_memory(self, msgid, target_lang, translation):
#         if msgid not in self.memory:
#             self.memory[msgid] = {}
#         self.memory[msgid][target_lang] = translation
#         self._save_memory()

#     # --- Status & Error ---
#     def _display_status(self, message):
#         print(f"\n--- STATUS: {message} ---")
    
#     def _display_error(self, message):
#         print(f"\n--- ERROR: {message} ---")

#     # --- Glossary ---
#     def _parse_glossary_csv(self, csv_file_path):
#         glossary_lookup = {}
#         try:
#             detected = from_path(csv_file_path).best()
#             encoding = detected.encoding if detected else 'utf-8'
#             with open(csv_file_path, 'r', encoding=encoding) as f:
#                 reader = csv.DictReader(f)
#                 for row in reader:
#                     key = (row["Original String"].strip(), row.get("Context", "").strip())
#                     cleaned_translation = self._normalize_placeholders(row["Translated String"].strip())
#                     glossary_lookup[key] = cleaned_translation
#         except Exception as e:
#             self._display_error(f"Glossary parse error: {e}")
#         return glossary_lookup

#     def _normalize_placeholders(self, msgstr):
#         msgstr = re.sub(r'%\s*(\d+)\s*\$\s*[sSdD]', r'%\1$s', msgstr)
#         return msgstr

#     # --- Existing PO files ---
#     def _extract_and_parse_existing_pos(self, zip_file_path):
#         existing_po_lookup = {}
#         if os.path.exists(self.temp_dir):
#             shutil.rmtree(self.temp_dir)
#         os.makedirs(self.temp_dir)
#         try:
#             with zipfile.ZipFile(zip_file_path, 'r') as zf:
#                 for member in zf.namelist():
#                     if member.endswith('.po'):
#                         zf.extract(member, self.temp_dir)
#                         path = os.path.join(self.temp_dir, member)
#                         try:
#                             po = polib.pofile(path)
#                             for entry in po:
#                                 key = (entry.msgid, entry.msgctxt or '')
#                                 cleaned_msgstr = entry.msgstr
#                                 if cleaned_msgstr:
#                                     cleaned_msgstr = self._normalize_placeholders(cleaned_msgstr)
#                                     if self._placeholders_are_valid(entry.msgid, cleaned_msgstr):
#                                         cleaned_msgstr = self._clean_translated_text(cleaned_msgstr)
#                                         existing_po_lookup[key] = cleaned_msgstr
#                         except Exception as e:
#                             self._display_error(f"Error parsing PO: {e}")
#         except Exception as e:
#             self._display_error(f"Error extracting ZIP: {e}")
#         finally:
#             shutil.rmtree(self.temp_dir, ignore_errors=True)
#         return existing_po_lookup

#     # --- Placeholders ---
#     def _placeholders_are_valid(self, original, translated):
#         try:
#             orig_ph = self._get_placeholders(original)
#             trans_ph = self._get_placeholders(translated)
#             return set(orig_ph) == set(trans_ph) and len(orig_ph) == len(trans_ph)
#         except Exception as e:
#             self._display_error(f"Placeholder validation failed: {e}")
#             return False

#     def _get_placeholders(self, text):
#         simple_placeholders = self.simple_placeholder_regex.findall(text)
#         complex_placeholders = self.complex_placeholder_regex.findall(text)
#         all_placeholders = list(set(simple_placeholders + complex_placeholders))
#         return all_placeholders

#     def _protect_placeholders(self, text):
#         placeholders = self._get_placeholders(text)
#         placeholder_map = {}
#         protected_text = text
#         placeholders.sort(key=len, reverse=True)
#         for i, ph in enumerate(placeholders):
#             token = f"PH_{i}_TOKEN"
#             placeholder_map[token] = ph
#             protected_text = protected_text.replace(ph, token)
#         return protected_text, placeholder_map

#     def _restore_placeholders(self, text, placeholder_map):
#         for token in placeholder_map:
#             pattern = r'\s*'.join(list(token))
#             regex = re.compile(pattern, flags=re.IGNORECASE)
#             text = regex.sub(token, text)
#         for token, ph in placeholder_map.items():
#             text = text.replace(token, ph)
#         return text

#     def _clean_translated_text(self, text):
#         text = re.sub(r'&\s*(#?\w+)\s*;', r'&\1;', text)
#         text = re.sub(r'\s+([.,!?;:])', r'\1', text)
#         text = re.sub(r'([.,!?;:])\s+', r'\1 ', text)
#         text = re.sub(r'(\s+)(”|\))', r'\2', text)
#         text = re.sub(r'(“|\()\s+', r'\1', text)
#         return text

#     def _is_likely_untranslated(self, original_text, translated_text):
#         protected_orig, _ = self._protect_placeholders(original_text)
#         protected_trans, _ = self._protect_placeholders(translated_text)
#         raw_orig = re.sub(r'PH_\d+_TOKEN', '', protected_orig)
#         raw_trans = re.sub(r'PH_\d+_TOKEN', '', protected_trans)
#         return raw_orig.strip().lower() == raw_trans.strip().lower()

#     def _apply_custom_rules(self, msgid, target_lang):
#         if msgid in self.translation_rules and target_lang in self.translation_rules[msgid]:
#             return self.translation_rules[msgid][target_lang]
#         return None

#     def _is_valid_translation(self, text):
#         error_signs = [
#             "Error 500",
#             "That’s an error",
#             "There was an error",
#             "<html", "</html>", "<body>", "</body>",
#             "Please try again later",
#         ]
#         lowered = text.lower()
#         for sign in error_signs:
#             if sign.lower() in lowered:
#                 return False
#         return True

#     def _fallback_translate(self, text, target_lang, retries=3, delay=1):
#         # Check memory first
#         memory_translation = self._get_memory_translation(text, target_lang)
#         if memory_translation:
#             return memory_translation

#         protected_text, placeholder_map = self._protect_placeholders(text)
#         for i in range(retries):
#             try:
#                 translator = GoogleTranslator(source='auto', target=target_lang)
#                 translated_protected = translator.translate(protected_text)
#                 translated_protected = re.sub(r"&\s+([a-zA-Z]+)\s*;", r"&\1;", translated_protected)
#                 translated = self._restore_placeholders(translated_protected, placeholder_map)
#                 translated = self._clean_translated_text(translated)
#                 if not self._is_valid_translation(translated):
#                     self._display_error(f"Invalid translation detected for '{text}' in '{target_lang}'. Using original text as fallback.")
#                     return text
#                 # Save to memory
#                 self._update_memory(text, target_lang, translated)
#                 return translated
#             except exceptions.NotValidPayload as e:
#                 self._display_error(f"Invalid payload for '{text}'. Error: {e}")
#                 break
#             except Exception as e:
#                 self._display_error(f"Translation attempt {i + 1}/{retries} failed for '{text}' to '{target_lang}': {e}")
#                 if i < retries - 1:
#                     time.sleep(delay)
#                 else:
#                     return text
#         return text

#     def _process_translation(self, pot_entry, glossary_lookup, existing_po_lookup, target_lang):
#         msgid = pot_entry.msgid
#         msgctxt = pot_entry.msgctxt or ''
#         key = (msgid, msgctxt)
#         custom_translation = self._apply_custom_rules(msgid, target_lang)
#         if custom_translation:
#             self._update_memory(msgid, target_lang, custom_translation)
#             return custom_translation, "Custom Rule"
#         if key in glossary_lookup:
#             glossary_trans = glossary_lookup[key]
#             if not self._placeholders_are_valid(msgid, glossary_trans) or self._is_likely_untranslated(msgid, glossary_trans):
#                 fallback = self._fallback_translate(msgid, target_lang)
#                 return fallback, "Glossary (Fuzzy)"
#             self._update_memory(msgid, target_lang, glossary_trans)
#             return glossary_trans, "Glossary"
#         if key in existing_po_lookup:
#             existing_translation = existing_po_lookup[key]
#             if not self._placeholders_are_valid(msgid, existing_translation) or self._is_likely_untranslated(msgid, existing_translation):
#                 fallback = self._fallback_translate(msgid, target_lang)
#                 return fallback, "Existing PO (Fuzzy)"
#             self._update_memory(msgid, target_lang, existing_translation)
#             return existing_translation, "Existing PO"
#         fallback = self._fallback_translate(msgid, target_lang)
#         return fallback, "Machine Translation"

#     # --- Main run function ---
#     def run(self, pot_path, zip_path, csv_path, target_langs, output_dir):
#         self._display_status("Starting WP Localization Tool")
        
#         self.pot_file_path = pot_path
#         self.zip_file_path = zip_path
#         self.csv_file_path = csv_path
#         self.target_languages = target_langs
        
#         try:
#             if not self.pot_file_path or not os.path.exists(self.pot_file_path):
#                 self._display_error("POT file not found.")
#                 return None
            
#             pot_file = polib.pofile(self.pot_file_path)
#             glossary = self._parse_glossary_csv(self.csv_file_path) if self.csv_file_path and os.path.exists(self.csv_file_path) else {}
#             existing = self._extract_and_parse_existing_pos(self.zip_file_path) if self.zip_file_path and os.path.exists(self.zip_file_path) else {}
            
#             for target_language in self.target_languages:
#                 self._display_status(f"Translating into {target_language}...")
#                 po = polib.POFile()
#                 now = datetime.now().strftime("%Y-%m-%d %H:%M:%S+0000")
                
#                 po.metadata = {
#                     'Project-Id-Version': 'Colab Free',
#                     'POT-Creation-Date': now,
#                     'PO-Revision-Date': now,
#                     'Language': target_language,
#                     'MIME-Version': '1.0',
#                     'Content-Type': 'text/plain; charset=UTF-8',
#                     'Content-Transfer-Encoding': '8bit',
#                     'X-Generator': 'Colab Tool'
#                 }
                
#                 for entry in pot_file:
#                     if not entry.msgid:
#                         continue
#                     try:
#                         translated_msgstr, source = self._process_translation(entry, glossary, existing, target_language)
#                         new_entry = polib.POEntry(
#                             msgid=entry.msgid,
#                             msgstr=translated_msgstr,
#                             msgctxt=entry.msgctxt,
#                             occurrences=entry.occurrences,
#                             comment=entry.comment,
#                             tcomment=entry.tcomment
#                         )
#                         if "Fuzzy" in source or "Fallback" in source:
#                             new_entry.flags.append("fuzzy")
#                         po.append(new_entry)
#                     except Exception as e:
#                         self._display_error(f"Failed to translate string '{entry.msgid[:50]}...'. Error: {e}")
#                         new_entry = polib.POEntry(
#                             msgid=entry.msgid,
#                             msgstr='',
#                             msgctxt=entry.msgctxt,
#                             occurrences=entry.occurrences,
#                             comment=entry.comment,
#                             tcomment=entry.tcomment
#                         )
#                         new_entry.flags.append("fuzzy")
#                         po.append(new_entry)
                
#                 # Logic to handle versioning
#                 counter = 0
#                 while True:
#                     suffix = f"-{counter}" if counter > 0 else ""
#                     out_po = os.path.join(output_dir, f"{target_language}{suffix}.po")
#                     out_mo = os.path.join(output_dir, f"{target_language}{suffix}.mo")
#                     if not os.path.exists(out_po) and not os.path.exists(out_mo):
#                         po.save(out_po)
#                         po.save_as_mofile(out_mo)
#                         break
#                     counter += 1

#             self._display_status("Translation complete.")
#             return True
        
#         except Exception as e:
#             self._display_error(f"Unexpected error during setup or file processing: {e}")
#             return False




# # localizationtool/localization_logic.py
# import polib
# import csv
# import zipfile
# import os
# import shutil
# from datetime import datetime
# from deep_translator import GoogleTranslator, exceptions
# import re
# from charset_normalizer import from_path
# import time
# import json

# class ColabLocalizationTool:
#     def __init__(self, memory_base_dir="translation_memory"):
#         self.pot_file_path = None
#         self.zip_file_path = None
#         self.csv_file_path = None
#         self.target_languages = []
#         self.temp_dir = "/tmp/po_extract"
#         self.memory_base_dir = memory_base_dir
#         os.makedirs(self.memory_base_dir, exist_ok=True)
#         self.simple_placeholder_regex = re.compile(r'%\d+\$\w|%[a-zA-Z_]\w*|%%|%[sSdD]')
#         self.complex_placeholder_regex = re.compile(r'(&ldquo;%[^&]+?&rdquo;)')
#         self.translation_rules = {
#             "%s min read": {
#                 "ja": "%s分で読めます",
#                 "it": "%s min di lettura",
#                 "nl": "%s min gelezen",
#                 "pl": "%s min czytania",
#                 "pt": "%s min de leitura",
#                 "de": "%s Min. Lesezeit",
#                 "ar": "قراءة في %s دقيقة",
#                 "fr": "%s min de lecture",
#                 "ru": "%s мин. чтения"
#             }
#         }
#         self.memory_storage_limit_mb = 100

#     # --- Memory Handling ---
#     def _get_memory_file_path(self, project_name, lang):
#         project_dir = os.path.join(self.memory_base_dir, project_name)
#         os.makedirs(project_dir, exist_ok=True)
#         return os.path.join(project_dir, f"{lang}.json")

#     def _load_memory(self, project_name, lang):
#         path = self._get_memory_file_path(project_name, lang)
#         if os.path.exists(path):
#             try:
#                 with open(path, 'r', encoding='utf-8') as f:
#                     return json.load(f)
#             except Exception:
#                 return {}
#         return {}

#     def _save_memory(self, memory, project_name, lang):
#         path = self._get_memory_file_path(project_name, lang)
#         try:
#             with open(path, 'w', encoding='utf-8') as f:
#                 json.dump(memory, f, ensure_ascii=False, indent=2)
#         except Exception as e:
#             self._display_error(f"Failed to save memory file: {e}")

#     def _get_memory_translation(self, memory, msgid, target_lang):
#         if msgid in memory:
#             return memory[msgid]
#         return None

#     def _update_memory(self, memory, msgid, translation):
#         memory[msgid] = translation

#     # --- Status & Error ---
#     def _display_status(self, message):
#         print(f"\n--- STATUS: {message} ---")
    
#     def _display_error(self, message):
#         print(f"\n--- ERROR: {message} ---")
    
#     # --- Glossary ---
#     def _parse_glossary_csv(self, csv_file_path):
#         glossary_lookup = {}
#         try:
#             detected = from_path(csv_file_path).best()
#             encoding = detected.encoding if detected else 'utf-8'
#             with open(csv_file_path, 'r', encoding=encoding) as f:
#                 reader = csv.DictReader(f)
#                 for row in reader:
#                     key = (row["Original String"].strip(), row.get("Context", "").strip())
#                     cleaned_translation = self._normalize_placeholders(row["Translated String"].strip())
#                     glossary_lookup[key] = cleaned_translation
#         except Exception as e:
#             self._display_error(f"Glossary parse error: {e}")
#         return glossary_lookup

#     def _normalize_placeholders(self, msgstr):
#         msgstr = re.sub(r'%\s*(\d+)\s*\$\s*[sSdD]', r'%\1$s', msgstr)
#         return msgstr

#     # --- Existing PO files ---
#     def _extract_and_parse_existing_pos(self, zip_file_path):
#         existing_po_lookup = {}
#         if os.path.exists(self.temp_dir):
#             shutil.rmtree(self.temp_dir)
#         os.makedirs(self.temp_dir)
#         try:
#             with zipfile.ZipFile(zip_file_path, 'r') as zf:
#                 for member in zf.namelist():
#                     if member.endswith('.po'):
#                         zf.extract(member, self.temp_dir)
#                         path = os.path.join(self.temp_dir, member)
#                         try:
#                             po = polib.pofile(path)
#                             for entry in po:
#                                 key = (entry.msgid, entry.msgctxt or '')
#                                 cleaned_msgstr = entry.msgstr
#                                 if cleaned_msgstr:
#                                     cleaned_msgstr = self._normalize_placeholders(cleaned_msgstr)
#                                     if self._placeholders_are_valid(entry.msgid, cleaned_msgstr):
#                                         cleaned_msgstr = self._clean_translated_text(cleaned_msgstr)
#                                         existing_po_lookup[key] = cleaned_msgstr
#                         except Exception as e:
#                             self._display_error(f"Error parsing PO: {e}")
#         except Exception as e:
#             self._display_error(f"Error extracting ZIP: {e}")
#         finally:
#             shutil.rmtree(self.temp_dir, ignore_errors=True)
#         return existing_po_lookup

#     # --- Placeholders ---
#     def _placeholders_are_valid(self, original, translated):
#         try:
#             orig_ph = self._get_placeholders(original)
#             trans_ph = self._get_placeholders(translated)
#             return set(orig_ph) == set(trans_ph) and len(orig_ph) == len(trans_ph)
#         except Exception as e:
#             self._display_error(f"Placeholder validation failed: {e}")
#             return False

#     def _get_placeholders(self, text):
#         simple_placeholders = self.simple_placeholder_regex.findall(text)
#         complex_placeholders = self.complex_placeholder_regex.findall(text)
#         return list(set(simple_placeholders + complex_placeholders))

#     def _protect_placeholders(self, text):
#         placeholders = self._get_placeholders(text)
#         placeholder_map = {}
#         protected_text = text
#         placeholders.sort(key=len, reverse=True)
#         for i, ph in enumerate(placeholders):
#             token = f"PH_{i}_TOKEN"
#             placeholder_map[token] = ph
#             protected_text = protected_text.replace(ph, token)
#         return protected_text, placeholder_map

#     def _restore_placeholders(self, text, placeholder_map):
#         for token in placeholder_map:
#             escaped_token = re.escape(token)
#             pattern = re.compile(r'\s*'.join(list(escaped_token)), flags=re.IGNORECASE)
#             text = pattern.sub(token, text)
#         for token, ph in placeholder_map.items():
#             text = text.replace(token, ph)
#         return text

#     def _clean_translated_text(self, text):
#         text = re.sub(r'&\s*(#?\w+)\s*;', r'&\1;', text)
#         text = re.sub(r'\s+([.,!?;:])', r'\1', text)
#         text = re.sub(r'([.,!?;:])\s+', r'\1 ', text)
#         text = re.sub(r'(\s+)(”|\))', r'\2', text)
#         text = re.sub(r'(“|\()\s+', r'\1', text)
#         return text

#     def _is_likely_untranslated(self, original_text, translated_text):
#         protected_orig, _ = self._protect_placeholders(original_text)
#         protected_trans, _ = self._protect_placeholders(translated_text)
#         raw_orig = re.sub(r'PH_\d+_TOKEN', '', protected_orig)
#         raw_trans = re.sub(r'PH_\d+_TOKEN', '', protected_trans)
#         return raw_orig.strip().lower() == raw_trans.strip().lower()

#     def _apply_custom_rules(self, msgid, target_lang):
#         if msgid in self.translation_rules and target_lang in self.translation_rules[msgid]:
#             return self.translation_rules[msgid][target_lang]
#         return None

#     def _is_valid_translation(self, text):
#         error_signs = [
#             "Error 500",
#             "That’s an error",
#             "There was an error",
#             "<html", "</html>", "<body>", "</body>",
#             "Please try again later",
#         ]
#         lowered = text.lower()
#         for sign in error_signs:
#             if sign.lower() in lowered:
#                 return False
#         return True

#     def _fallback_translate(self, memory, text, target_lang, retries=3, delay=1):
#         memory_translation = self._get_memory_translation(memory, text, target_lang)
#         if memory_translation:
#             return memory_translation

#         protected_text, placeholder_map = self._protect_placeholders(text)
#         for i in range(retries):
#             try:
#                 translator = GoogleTranslator(source='auto', target=target_lang)
#                 translated_protected = translator.translate(protected_text)
#                 translated_protected = re.sub(r"&\s+([a-zA-Z]+)\s*;", r"&\1;", translated_protected)
#                 translated = self._restore_placeholders(translated_protected, placeholder_map)
#                 translated = self._clean_translated_text(translated)
#                 if not self._is_valid_translation(translated):
#                     self._display_error(f"Invalid translation detected for '{text}' in '{target_lang}'. Using original text as fallback.")
#                     return text
#                 self._update_memory(memory, text, translated)
#                 return translated
#             except exceptions.NotValidPayload as e:
#                 self._display_error(f"Invalid payload for '{text}'. Error: {e}")
#                 break
#             except Exception as e:
#                 self._display_error(f"Translation attempt {i + 1}/{retries} failed for '{text}' to '{target_lang}': {e}")
#                 if i < retries - 1:
#                     time.sleep(delay)
#                 else:
#                     return text
#         return text

#     def _process_translation(self, memory, pot_entry, glossary_lookup, existing_po_lookup, target_lang):
#         msgid = pot_entry.msgid
#         msgctxt = pot_entry.msgctxt or ''
#         key = (msgid, msgctxt)
#         custom_translation = self._apply_custom_rules(msgid, target_lang)
#         if custom_translation:
#             self._update_memory(memory, msgid, custom_translation)
#             return custom_translation, "Custom Rule"
#         if key in glossary_lookup:
#             glossary_trans = glossary_lookup[key]
#             if not self._placeholders_are_valid(msgid, glossary_trans) or self._is_likely_untranslated(msgid, glossary_trans):
#                 fallback = self._fallback_translate(memory, msgid, target_lang)
#                 return fallback, "Glossary (Fuzzy)"
#             self._update_memory(memory, msgid, glossary_trans)
#             return glossary_trans, "Glossary"
#         if key in existing_po_lookup:
#             existing_translation = existing_po_lookup[key]
#             if not self._placeholders_are_valid(msgid, existing_translation) or self._is_likely_untranslated(msgid, existing_translation):
#                 fallback = self._fallback_translate(memory, msgid, target_lang)
#                 return fallback, "Existing PO (Fuzzy)"
#             self._update_memory(memory, msgid, existing_translation)
#             return existing_translation, "Existing PO"
#         fallback = self._fallback_translate(memory, msgid, target_lang)
#         return fallback, "Machine Translation"

#     # --- Main run function ---
#     def run(self, pot_path, zip_path, csv_path, target_langs, output_dir):
#         self._display_status("Starting WP Localization Tool")
        
#         self.pot_file_path = pot_path
#         self.zip_file_path = zip_path
#         self.csv_file_path = csv_path
#         self.target_languages = target_langs

#         project_name = os.path.splitext(os.path.basename(pot_path))[0]
#         project_dir = os.path.join(output_dir, project_name)
#         os.makedirs(project_dir, exist_ok=True)
        
#         try:
#             if not self.pot_file_path or not os.path.exists(self.pot_file_path):
#                 self._display_error("POT file not found.")
#                 return None

#             pot_file = polib.pofile(self.pot_file_path)
#             glossary = self._parse_glossary_csv(self.csv_file_path) if self.csv_file_path and os.path.exists(self.csv_file_path) else {}
#             existing = self._extract_and_parse_existing_pos(self.zip_file_path) if self.zip_file_path and os.path.exists(self.zip_file_path) else {}

#             for target_language in self.target_languages:
#                 memory = self._load_memory(project_name, target_language)
#                 self._display_status(f"Translating into {target_language}...")
#                 po = polib.POFile()
#                 now = datetime.now().strftime("%Y-%m-%d %H:%M:%S+0000")
                
#                 po.metadata = {
#                     'Project-Id-Version': 'Colab Free',
#                     'POT-Creation-Date': now,
#                     'PO-Revision-Date': now,
#                     'Language': target_language,
#                     'MIME-Version': '1.0',
#                     'Content-Type': 'text/plain; charset=UTF-8',
#                     'Content-Transfer-Encoding': '8bit',
#                     'X-Generator': 'Colab Tool'
#                 }
                
#                 for entry in pot_file:
#                     if not entry.msgid:
#                         continue
#                     try:
#                         translated_msgstr, source = self._process_translation(memory, entry, glossary, existing, target_language)
#                         new_entry = polib.POEntry(
#                             msgid=entry.msgid,
#                             msgstr=translated_msgstr,
#                             msgctxt=entry.msgctxt,
#                             occurrences=entry.occurrences,
#                             comment=entry.comment,
#                             tcomment=entry.tcomment
#                         )
#                         if "Fuzzy" in source or "Fallback" in source:
#                             new_entry.flags.append("fuzzy")
#                         po.append(new_entry)
#                     except Exception as e:
#                         self._display_error(f"Failed to translate string '{entry.msgid[:50]}...'. Error: {e}")
#                         new_entry = polib.POEntry(
#                             msgid=entry.msgid,
#                             msgstr='',
#                             msgctxt=entry.msgctxt,
#                             occurrences=entry.occurrences,
#                             comment=entry.comment,
#                             tcomment=entry.tcomment
#                         )
#                         new_entry.flags.append("fuzzy")
#                         po.append(new_entry)
                
#                 # Save PO & MO files
#                 out_po = os.path.join(project_dir, f"{target_language}.po")
#                 out_mo = os.path.join(project_dir, f"{target_language}.mo")
#                 po.save(out_po)
#                 po.save_as_mofile(out_mo)

#                 # Save memory JSON
#                 self._save_memory(memory, project_name, target_language)

#             self._display_status("Translation complete.")
#             return True
        
#         except Exception as e:
#             self._display_error(f"Unexpected error during setup or file processing: {e}")
#             return False






# # localizationtool/localization_logic.py
# import polib
# import csv
# import zipfile
# import os
# import shutil
# from datetime import datetime
# from deep_translator import GoogleTranslator, exceptions
# import re
# from charset_normalizer import from_path
# import time
# import json

# class ColabLocalizationTool:
#     def __init__(self, memory_base_dir="translation_memory"):
#         self.pot_file_path = None
#         self.zip_file_path = None
#         self.csv_file_path = None
#         self.target_languages = []
#         self.temp_dir = "/tmp/po_extract"
#         self.memory_base_dir = memory_base_dir
#         os.makedirs(self.memory_base_dir, exist_ok=True)
#         self.simple_placeholder_regex = re.compile(r'%\d+\$\w|%[a-zA-Z_]\w*|%%|%[sSdD]')
#         self.complex_placeholder_regex = re.compile(r'(&ldquo;%[^&]+?&rdquo;)')
#         self.translation_rules = {
#             "%s min read": {
#                 "ja": "%s分で読めます",
#                 "it": "%s min di lettura",
#                 "nl": "%s min gelezen",
#                 "pl": "%s min czytania",
#                 "pt": "%s min de leitura",
#                 "de": "%s Min. Lesezeit",
#                 "ar": "قراءة في %s دقيقة",
#                 "fr": "%s min de lecture",
#                 "ru": "%s мин. чтения"
#             }
#         }
#         self.memory_storage_limit_mb = 100

#     # --- Memory Handling ---
#     def _get_memory_file_path(self, project_name, lang):
#         project_dir = os.path.join(self.memory_base_dir, project_name)
#         os.makedirs(project_dir, exist_ok=True)
#         return os.path.join(project_dir, f"{lang}.json")

#     def _load_memory(self, project_name, lang):
#         path = self._get_memory_file_path(project_name, lang)
#         if os.path.exists(path):
#             try:
#                 with open(path, 'r', encoding='utf-8') as f:
#                     return json.load(f)
#             except Exception:
#                 return {}
#         return {}

#     def _save_memory(self, memory, project_name, lang):
#         path = self._get_memory_file_path(project_name, lang)
#         try:
#             with open(path, 'w', encoding='utf-8') as f:
#                 json.dump(memory, f, ensure_ascii=False, indent=2)
#         except Exception as e:
#             self._display_error(f"Failed to save memory file: {e}")

#     def _get_memory_translation(self, memory, msgid, target_lang):
#         if msgid in memory:
#             return memory[msgid]
#         return None

#     def _update_memory(self, memory, msgid, translation):
#         memory[msgid] = translation

#     # --- Status & Error ---
#     def _display_status(self, message):
#         print(f"\n--- STATUS: {message} ---")
    
#     def _display_error(self, message):
#         print(f"\n--- ERROR: {message} ---")
    
#     # --- Glossary ---
#     def _parse_glossary_csv(self, csv_file_path):
#         glossary_lookup = {}
#         try:
#             detected = from_path(csv_file_path).best()
#             encoding = detected.encoding if detected else 'utf-8'
#             with open(csv_file_path, 'r', encoding=encoding) as f:
#                 reader = csv.DictReader(f)
#                 for row in reader:
#                     key = (row["Original String"].strip(), row.get("Context", "").strip())
#                     cleaned_translation = self._normalize_placeholders(row["Translated String"].strip())
#                     glossary_lookup[key] = cleaned_translation
#         except Exception as e:
#             self._display_error(f"Glossary parse error: {e}")
#         return glossary_lookup

#     def _normalize_placeholders(self, msgstr):
#         msgstr = re.sub(r'%\s*(\d+)\s*\$\s*[sSdD]', r'%\1$s', msgstr)
#         return msgstr

#     # --- Existing PO files ---
#     def _extract_and_parse_existing_pos(self, zip_file_path):
#         existing_po_lookup = {}
#         if os.path.exists(self.temp_dir):
#             shutil.rmtree(self.temp_dir)
#         os.makedirs(self.temp_dir)
#         try:
#             with zipfile.ZipFile(zip_file_path, 'r') as zf:
#                 for member in zf.namelist():
#                     if member.endswith('.po'):
#                         zf.extract(member, self.temp_dir)
#                         path = os.path.join(self.temp_dir, member)
#                         try:
#                             po = polib.pofile(path)
#                             for entry in po:
#                                 key = (entry.msgid, entry.msgctxt or '')
#                                 cleaned_msgstr = entry.msgstr
#                                 if cleaned_msgstr:
#                                     cleaned_msgstr = self._normalize_placeholders(cleaned_msgstr)
#                                     if self._placeholders_are_valid(entry.msgid, cleaned_msgstr):
#                                         cleaned_msgstr = self._clean_translated_text(cleaned_msgstr)
#                                         existing_po_lookup[key] = cleaned_msgstr
#                         except Exception as e:
#                             self._display_error(f"Error parsing PO: {e}")
#         except Exception as e:
#             self._display_error(f"Error extracting ZIP: {e}")
#         finally:
#             shutil.rmtree(self.temp_dir, ignore_errors=True)
#         return existing_po_lookup

#     # --- Placeholders ---
#     def _placeholders_are_valid(self, original, translated):
#         try:
#             orig_ph = self._get_placeholders(original)
#             trans_ph = self._get_placeholders(translated)
#             return set(orig_ph) == set(trans_ph) and len(orig_ph) == len(trans_ph)
#         except Exception as e:
#             self._display_error(f"Placeholder validation failed: {e}")
#             return False

#     def _get_placeholders(self, text):
#         simple_placeholders = self.simple_placeholder_regex.findall(text)
#         complex_placeholders = self.complex_placeholder_regex.findall(text)
#         return list(set(simple_placeholders + complex_placeholders))

#     def _protect_placeholders(self, text):
#         placeholders = self._get_placeholders(text)
#         placeholder_map = {}
#         protected_text = text
#         placeholders.sort(key=len, reverse=True)
#         for i, ph in enumerate(placeholders):
#             token = f"PH_{i}_TOKEN"
#             placeholder_map[token] = ph
#             protected_text = protected_text.replace(ph, token)
#         return protected_text, placeholder_map

#     def _restore_placeholders(self, text, placeholder_map):
#         for token in placeholder_map:
#             escaped_token = re.escape(token)
#             pattern = re.compile(r'\s*'.join(list(escaped_token)), flags=re.IGNORECASE)
#             text = pattern.sub(token, text)
#         for token, ph in placeholder_map.items():
#             text = text.replace(token, ph)
#         return text

#     def _clean_translated_text(self, text):
#         text = re.sub(r'&\s*(#?\w+)\s*;', r'&\1;', text)
#         text = re.sub(r'\s+([.,!?;:])', r'\1', text)
#         text = re.sub(r'([.,!?;:])\s+', r'\1 ', text)
#         text = re.sub(r'(\s+)(”|\))', r'\2', text)
#         text = re.sub(r'(“|\()\s+', r'\1', text)
#         return text

#     def _is_likely_untranslated(self, original_text, translated_text):
#         protected_orig, _ = self._protect_placeholders(original_text)
#         protected_trans, _ = self._protect_placeholders(translated_text)
#         raw_orig = re.sub(r'PH_\d+_TOKEN', '', protected_orig)
#         raw_trans = re.sub(r'PH_\d+_TOKEN', '', protected_trans)
#         return raw_orig.strip().lower() == raw_trans.strip().lower()

#     def _apply_custom_rules(self, msgid, target_lang):
#         if msgid in self.translation_rules and target_lang in self.translation_rules[msgid]:
#             return self.translation_rules[msgid][target_lang]
#         return None

#     def _is_valid_translation(self, text):
#         error_signs = [
#             "Error 500",
#             "That’s an error",
#             "There was an error",
#             "<html", "</html>", "<body>", "</body>",
#             "Please try again later",
#         ]
#         lowered = text.lower()
#         for sign in error_signs:
#             if sign.lower() in lowered:
#                 return False
#         return True

#     def _fallback_translate(self, memory, text, target_lang, retries=3, delay=1):
#         memory_translation = self._get_memory_translation(memory, text, target_lang)
#         if memory_translation:
#             return memory_translation

#         protected_text, placeholder_map = self._protect_placeholders(text)
#         for i in range(retries):
#             try:
#                 translator = GoogleTranslator(source='auto', target=target_lang)
#                 translated_protected = translator.translate(protected_text)
#                 translated_protected = re.sub(r"&\s+([a-zA-Z]+)\s*;", r"&\1;", translated_protected)
#                 translated = self._restore_placeholders(translated_protected, placeholder_map)
#                 translated = self._clean_translated_text(translated)
#                 if not self._is_valid_translation(translated):
#                     self._display_error(f"Invalid translation detected for '{text}' in '{target_lang}'. Using original text as fallback.")
#                     return text
#                 self._update_memory(memory, text, translated)
#                 return translated
#             except exceptions.NotValidPayload as e:
#                 self._display_error(f"Invalid payload for '{text}'. Error: {e}")
#                 break
#             except Exception as e:
#                 self._display_error(f"Translation attempt {i + 1}/{retries} failed for '{text}' to '{target_lang}': {e}")
#                 if i < retries - 1:
#                     time.sleep(delay)
#                 else:
#                     return text
#         return text

#     def _process_translation(self, memory, pot_entry, glossary_lookup, existing_po_lookup, target_lang):
#         msgid = pot_entry.msgid
#         msgctxt = pot_entry.msgctxt or ''
#         key = (msgid, msgctxt)
#         custom_translation = self._apply_custom_rules(msgid, target_lang)
#         if custom_translation:
#             self._update_memory(memory, msgid, custom_translation)
#             return custom_translation, "Custom Rule"
#         if key in glossary_lookup:
#             glossary_trans = glossary_lookup[key]
#             if not self._placeholders_are_valid(msgid, glossary_trans) or self._is_likely_untranslated(msgid, glossary_trans):
#                 fallback = self._fallback_translate(memory, msgid, target_lang)
#                 return fallback, "Glossary (Fuzzy)"
#             self._update_memory(memory, msgid, glossary_trans)
#             return glossary_trans, "Glossary"
#         if key in existing_po_lookup:
#             existing_translation = existing_po_lookup[key]
#             if not self._placeholders_are_valid(msgid, existing_translation) or self._is_likely_untranslated(msgid, existing_translation):
#                 fallback = self._fallback_translate(memory, msgid, target_lang)
#                 return fallback, "Existing PO (Fuzzy)"
#             self._update_memory(memory, msgid, existing_translation)
#             return existing_translation, "Existing PO"
#         fallback = self._fallback_translate(memory, msgid, target_lang)
#         return fallback, "Machine Translation"

#     # --- Main run function ---
#     def run(self, pot_path, zip_path, csv_path, target_langs, output_dir):
#         self._display_status("Starting WP Localization Tool")
        
#         self.pot_file_path = pot_path
#         self.zip_file_path = zip_path
#         self.csv_file_path = csv_path
#         self.target_languages = target_langs

#         project_name = os.path.splitext(os.path.basename(pot_path))[0]
#         project_dir = os.path.join(output_dir, project_name)
#         os.makedirs(project_dir, exist_ok=True)
        
#         try:
#             if not self.pot_file_path or not os.path.exists(self.pot_file_path):
#                 self._display_error("POT file not found.")
#                 return None

#             pot_file = polib.pofile(self.pot_file_path)
#             glossary = self._parse_glossary_csv(self.csv_file_path) if self.csv_file_path and os.path.exists(self.csv_file_path) else {}
#             existing = self._extract_and_parse_existing_pos(self.zip_file_path) if self.zip_file_path and os.path.exists(self.zip_file_path) else {}

#             for target_language in self.target_languages:
#                 memory = self._load_memory(project_name, target_language)
#                 self._display_status(f"Translating into {target_language}...")
#                 po = polib.POFile()
#                 now = datetime.now().strftime("%Y-%m-%d %H:%M:%S+0000")
                
#                 po.metadata = {
#                     'Project-Id-Version': 'Colab Free',
#                     'POT-Creation-Date': now,
#                     'PO-Revision-Date': now,
#                     'Language': target_language,
#                     'MIME-Version': '1.0',
#                     'Content-Type': 'text/plain; charset=UTF-8',
#                     'Content-Transfer-Encoding': '8bit',
#                     'X-Generator': 'Colab Tool'
#                 }
                
#                 for entry in pot_file:
#                     if not entry.msgid:
#                         continue
#                     try:
#                         translated_msgstr, source = self._process_translation(memory, entry, glossary, existing, target_language)
#                         new_entry = polib.POEntry(
#                             msgid=entry.msgid,
#                             msgstr=translated_msgstr,
#                             msgctxt=entry.msgctxt,
#                             occurrences=entry.occurrences,
#                             comment=entry.comment,
#                             tcomment=entry.tcomment
#                         )
#                         if "Fuzzy" in source or "Fallback" in source:
#                             new_entry.flags.append("fuzzy")
#                         po.append(new_entry)
#                     except Exception as e:
#                         self._display_error(f"Failed to translate string '{entry.msgid[:50]}...'. Error: {e}")
#                         new_entry = polib.POEntry(
#                             msgid=entry.msgid,
#                             msgstr='',
#                             msgctxt=entry.msgctxt,
#                             occurrences=entry.occurrences,
#                             comment=entry.comment,
#                             tcomment=entry.tcomment
#                         )
#                         new_entry.flags.append("fuzzy")
#                         po.append(new_entry)
                
#                 # --- Save PO & MO files with versioning ---
#                 counter = 1
#                 while True:
#                     out_po = os.path.join(project_dir, f"{target_language}-v{counter}.po")
#                     out_mo = os.path.join(project_dir, f"{target_language}-v{counter}.mo")
#                     if not os.path.exists(out_po) and not os.path.exists(out_mo):
#                         po.save(out_po)
#                         po.save_as_mofile(out_mo)
#                         break
#                     counter += 1

#                 # Save memory JSON
#                 self._save_memory(memory, project_name, target_language)

#             self._display_status("Translation complete.")
#             return True
        
#         except Exception as e:
#             self._display_error(f"Unexpected error during setup or file processing: {e}")
#             return False




# localizationtool/localization_logic.py (enhanced)
# -*- coding: utf-8 -*-
"""
Major upgrades:
- CLDR-style pluralization support (singular/other baseline; n-plurals via header map).
- msgid_plural handling using Babel categories (one/other) with safe fallback for extra forms.
- ICU/JS placeholders (e.g., {0}, {name}) and HTML tag protection/validation.
- Incremental POT diffing with snapshot JSON (new/modified/unchanged); modified → fuzzy.
- Glossary/context enhancements (exact, partial, and regex context matching; multi-word).
- Translation QA report per language (JSON + CSV): counts & issues (placeholders, HTML, empty, etc.).
- Performance: in-memory cache, basic batch-friendly join/split (opt-in), retries with backoff.
- Multi-engine pluggable _Translator with Google as default; hooks for DeepL/Microsoft.

Notes:
- For full CLDR plural accuracy, include proper Plural-Forms headers per target language. A
  curated map is provided for common locales; others default to 2 plural forms (n != 1).
- When nplurals > 2 (e.g., Russian, Arabic), we populate ALL indices using the best available
  translation for category "one" vs "other". If you have language-specific templates, extend
  `self.translation_rules_plural_templates` to override.
"""

import polib
import csv
import zipfile
import os
import shutil
from datetime import datetime
from deep_translator import GoogleTranslator as _GoogleTranslator, exceptions
import re
from charset_normalizer import from_path
import time
import json
from typing import Dict, Tuple, List, Optional

try:
    from babel.core import Locale
    from babel.plural import PluralRule
except Exception:  # Babel optional; code works with fallback headers
    Locale = None
    PluralRule = None


class _Translator:
    """Pluggable translator interface."""
    def translate(self, texts: List[str], target_lang: str) -> List[str]:
        raise NotImplementedError


class GoogleTranslatorEngine(_Translator):
    """Batch-friendly wrapper around deep_translator.GoogleTranslator.
    We implement naive batching by joining with a delimiter that is unlikely to appear.
    """

    _SEP = "\u2063"  # Invisible Separator – rare in UI text

    def translate(self, texts: List[str], target_lang: str) -> List[str]:
        if not texts:
            return []
        joined = self._SEP.join(texts)
        translator = _GoogleTranslator(source='auto', target=target_lang)
        out = translator.translate(joined)
        # Some engines may return list already; normalize to string first
        if isinstance(out, list):
            # deep_translator usually returns str; handle list defensively
            return [str(x) for x in out]
        parts = str(out).split(self._SEP)
        if len(parts) != len(texts):
            # delimiter collision fallback – translate one by one
            parts = []
            for t in texts:
                parts.append(str(_GoogleTranslator(source='auto', target=target_lang).translate(t)))
        return parts


class ColabLocalizationTool:
    def __init__(self, memory_base_dir: str = "translation_memory"):
        self.pot_file_path = None
        self.zip_file_path = None
        self.csv_file_path = None
        self.target_languages: List[str] = []
        self.temp_dir = "/tmp/po_extract"
        self.memory_base_dir = memory_base_dir
        os.makedirs(self.memory_base_dir, exist_ok=True)

        # Placeholder regexes (extended)
        # printf: %s, %1$s, %d, %04d, %name, %%
        self.printf_placeholder_regex = re.compile(r"%\d+\$[sdif]|%[sdif]|%[a-zA-Z_]\w*|%%")
        # ICU/JS: {0}, {name}, {count, plural, one {...} other {...}}
        self.icu_placeholder_regex = re.compile(r"\{\s*([\w\d]+)(?:\s*,[^}]*)?\}")
        # HTML tags: <b>, </b>, <strong attr="..">, <br/>
        self.html_tag_regex = re.compile(r"</?[a-zA-Z][^>]*>")
        # Legacy complex placeholder (from quotes)
        self.quoted_printf_regex = re.compile(r'(&ldquo;%[^&]+?&rdquo;)')

        # Custom rule templates for specific strings (by msgid)
        self.translation_rules = {
            "%s min read": {
                "ja": "%s分で読めます",
                "it": "%s min di lettura",
                "nl": "%s min gelezen",
                "pl": "%s min czytania",
                "pt": "%s min de leitura",
                "de": "%s Min. Lesezeit",
                "ar": "قراءة في %s دقيقة",
                "fr": "%s min de lecture",
                "ru": "%s мин. чтения",
                "en": "%s mins read"  # default plural template – we still map one/other
            }
        }

        # Plural templates for languages that need category-specific texts
        # For msgid "%s min read" -> different singular/plural.
        self.translation_rules_plural_templates = {
            "%s min read": {
                # category -> template
                "en": {"one": "%s min read", "other": "%s mins read"},
                "fr": {"one": "%s min de lecture", "other": "%s min de lecture"},
                "ru": {"one": "%s мин. чтения", "few": "%s мин. чтения", "many": "%s мин. чтения", "other": "%s мин. чтения"},
                "ar": {"one": "قراءة في دقيقة %s", "other": "قراءة في %s دقيقة"},
            }
        }

        # Limit for all memories (not enforced strictly here; kept from original)
        self.memory_storage_limit_mb = 100

        # QA & diff tracking (per run)
        self._qa_rows: List[Dict] = []
        self._counts = {
            "new": 0,
            "modified": 0,
            "unchanged": 0,
            "reused": 0,
            "fuzzy": 0,
            "failed": 0,
            "translated": 0,
        }

        # In-memory translation cache for this run
        self._cache: Dict[Tuple[str, str], str] = {}

        # Default translator engine (pluggable)
        self.translator_engine: _Translator = GoogleTranslatorEngine()

        # Plural-Forms header map (gettext) for common locales
        # Add more as needed.
        self.plural_forms_header = {
            "en": "nplurals=2; plural=(n != 1);",
            "fr": "nplurals=2; plural=(n > 1);",
            "de": "nplurals=2; plural=(n != 1);",
            "it": "nplurals=2; plural=(n != 1);",
            "nl": "nplurals=2; plural=(n != 1);",
            "pl": "nplurals=3; plural=(n==1 ? 0 : n%10>=2 and n%10<=4 and (n%100<10 or n%100>=20) ? 1 : 2);",
            "ru": "nplurals=3; plural=(n%10==1 and n%100!=11 ? 0 : n%10>=2 and n%10<=4 and (n%100<10 or n%100>=20) ? 1 : 2);",
            "uk": "nplurals=3; plural=(n%10==1 and n%100!=11 ? 0 : n%10>=2 and n%10<=4 and (n%100<10 or n%100>=20) ? 1 : 2);",
            "ar": "nplurals=6; plural=(n==0?0 : n==1?1 : n==2?2 : n%100>=3 and n%100<=10?3 : n%100>=11 and n%100<=99?4 : 5);",
            "ja": "nplurals=1; plural=0;",
            "zh": "nplurals=1; plural=0;",
            "pt": "nplurals=2; plural=(n != 1);",
            "pt_BR": "nplurals=2; plural=(n > 1);",
            "es": "nplurals=2; plural=(n != 1);",
        }

    # -----------------------
    # Memory Handling
    # -----------------------
    def _get_memory_file_path(self, project_name, lang):
        project_dir = os.path.join(self.memory_base_dir, project_name)
        os.makedirs(project_dir, exist_ok=True)
        return os.path.join(project_dir, f"{lang}.json")

    def _get_snapshot_file_path(self, project_name):
        project_dir = os.path.join(self.memory_base_dir, project_name)
        os.makedirs(project_dir, exist_ok=True)
        return os.path.join(project_dir, "_last_snapshot.json")

    def _load_memory(self, project_name, lang):
        path = self._get_memory_file_path(project_name, lang)
        if os.path.exists(path):
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                return {}
        return {}

    def _save_memory(self, memory, project_name, lang):
        path = self._get_memory_file_path(project_name, lang)
        try:
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(memory, f, ensure_ascii=False, indent=2)
        except Exception as e:
            self._display_error(f"Failed to save memory file: {e}")

    def _get_memory_translation(self, memory, msgid, target_lang):
        return memory.get(msgid)

    def _update_memory(self, memory, msgid, translation):
        memory[msgid] = translation

    # -----------------------
    # Status & Error
    # -----------------------
    def _display_status(self, message):
        print(f"\n--- STATUS: {message} ---")

    def _display_error(self, message):
        print(f"\n--- ERROR: {message} ---")

    # -----------------------
    # Glossary
    # -----------------------
    def _parse_glossary_csv(self, csv_file_path):
        """CSV columns: Original String, Translated String, Context (optional, regex allowed)."""
        glossary_lookup: Dict[Tuple[str, str], str] = {}
        try:
            detected = from_path(csv_file_path).best()
            encoding = detected.encoding if detected else 'utf-8'
            with open(csv_file_path, 'r', encoding=encoding) as f:
                reader = csv.DictReader(f)
                for row in reader:
                    orig = (row.get("Original String", "") or "").strip()
                    ctx = (row.get("Context", "") or "").strip()
                    trans = (row.get("Translated String", "") or "").strip()
                    trans = self._normalize_placeholders(trans)
                    glossary_lookup[(orig, ctx)] = trans
        except Exception as e:
            self._display_error(f"Glossary parse error: {e}")
        return glossary_lookup

    def _match_glossary(self, glossary_lookup, msgid: str, msgctxt: str) -> Optional[str]:
        # 1) Exact context match
        key = (msgid, msgctxt or '')
        if key in glossary_lookup:
            return glossary_lookup[key]
        # 2) Partial context match (substring)
        for (orig, ctx), trans in glossary_lookup.items():
            if orig == msgid and ctx and (msgctxt or '').find(ctx) >= 0:
                return trans
        # 3) Regex context match
        for (orig, ctx), trans in glossary_lookup.items():
            if orig == msgid and ctx:
                try:
                    if re.search(ctx, msgctxt or ''):
                        return trans
                except re.error:
                    continue
        return None

    def _normalize_placeholders(self, msgstr):
        return re.sub(r'%\s*(\d+)\s*\$\s*[sSdD]', r'%\1$s', msgstr)

    # -----------------------
    # Existing PO files
    # -----------------------
    def _extract_and_parse_existing_pos(self, zip_file_path):
        existing_po_lookup = {}
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
        os.makedirs(self.temp_dir)
        try:
            with zipfile.ZipFile(zip_file_path, 'r') as zf:
                for member in zf.namelist():
                    if member.endswith('.po'):
                        zf.extract(member, self.temp_dir)
                        path = os.path.join(self.temp_dir, member)
                        try:
                            po = polib.pofile(path)
                            for entry in po:
                                key = (entry.msgid, entry.msgctxt or '')
                                cleaned_msgstr = entry.msgstr
                                if cleaned_msgstr:
                                    cleaned_msgstr = self._normalize_placeholders(cleaned_msgstr)
                                    if self._placeholders_are_valid(entry.msgid, cleaned_msgstr):
                                        cleaned_msgstr = self._clean_translated_text(cleaned_msgstr)
                                        existing_po_lookup[key] = cleaned_msgstr
                        except Exception as e:
                            self._display_error(f"Error parsing PO: {e}")
        except Exception as e:
            self._display_error(f"Error extracting ZIP: {e}")
        finally:
            shutil.rmtree(self.temp_dir, ignore_errors=True)
        return existing_po_lookup

    # -----------------------
    # Placeholders
    # -----------------------
    def _collect_placeholders(self, text: str) -> List[str]:
        ph = []
        ph += self.printf_placeholder_regex.findall(text)
        ph += self.icu_placeholder_regex.findall(text)
        quoted = self.quoted_printf_regex.findall(text)
        ph += quoted
        # Normalize ICU capture (regex returns only the name) into canonical tokens
        normalized = []
        for x in ph:
            if isinstance(x, tuple):  # ICU group returns tuple due to capturing name
                normalized.append('{' + x[0] + '}')
            else:
                normalized.append(x)
        # Unique, keep order by dict
        return list(dict.fromkeys(normalized))

    def _placeholders_are_valid(self, original: str, translated: str) -> bool:
        try:
            orig_ph = self._collect_placeholders(original)
            trans_ph = self._collect_placeholders(translated)
            return set(orig_ph) == set(trans_ph) and len(orig_ph) == len(trans_ph)
        except Exception as e:
            self._display_error(f"Placeholder validation failed: {e}")
            return False

    def _protect_markers(self, text: str) -> Tuple[str, Dict[str, str]]:
        placeholders = self._collect_placeholders(text)
        tags = self.html_tag_regex.findall(text)
        to_protect = placeholders + tags
        placeholder_map = {}
        protected_text = text
        # Sort long → short to avoid partial overlaps
        to_protect.sort(key=len, reverse=True)
        for i, ph in enumerate(to_protect):
            token = f"PH_{i}_TOKEN"
            placeholder_map[token] = ph
            protected_text = protected_text.replace(ph, token)
        return protected_text, placeholder_map

    def _restore_markers(self, text: str, placeholder_map: Dict[str, str]) -> str:
        # Avoid token mangling by MT adding spaces – normalize tokens first
        for token in list(placeholder_map.keys()):
            escaped = re.escape(token)
            pattern = re.compile(r'\s*'.join(list(escaped)))
            text = pattern.sub(token, text)
        for token, ph in placeholder_map.items():
            text = text.replace(token, ph)
        return text

    def _clean_translated_text(self, text):
        text = re.sub(r'&\s*(#?\w+)\s*;', r'&\1;', text)
        text = re.sub(r'\s+([.,!?;:])', r'\1', text)
        text = re.sub(r'([.,!?;:])\s+', r'\1 ', text)
        text = re.sub(r'(\s+)(”|\))', r'\2', text)
        text = re.sub(r'(“|\()\s+', r'\1', text)
        return text

    def _is_likely_untranslated(self, original_text, translated_text):
        protected_orig, _ = self._protect_markers(original_text)
        protected_trans, _ = self._protect_markers(translated_text)
        raw_orig = re.sub(r'PH_\d+_TOKEN', '', protected_orig)
        raw_trans = re.sub(r'PH_\d+_TOKEN', '', protected_trans)
        return raw_orig.strip().lower() == raw_trans.strip().lower()

    def _apply_custom_rules(self, msgid, target_lang, plural_category: Optional[str] = None):
        # Plural-aware specific templates if present
        if msgid in self.translation_rules_plural_templates:
            lang_map = self.translation_rules_plural_templates[msgid]
            lang_map = lang_map.get(target_lang) or lang_map.get(target_lang.split("_", 1)[0])
            if lang_map and plural_category and plural_category in lang_map:
                return lang_map[plural_category]
        # Non-plural override
        if msgid in self.translation_rules:
            lang_map = self.translation_rules[msgid]
            return lang_map.get(target_lang) or lang_map.get(target_lang.split("_", 1)[0])
        return None

    def _is_valid_translation(self, text):
        error_signs = [
            "Error 500",
            "That’s an error",
            "There was an error",
            "<html", "</html>", "<body>", "</body>",
            "Please try again later",
        ]
        lowered = text.lower()
        return not any(s.lower() in lowered for s in error_signs)

    # -----------------------
    # Translation Core
    # -----------------------
    def _retry(self, func, max_retries=3):
        delay = 1.0
        for i in range(max_retries):
            try:
                return func()
            except Exception as e:
                self._display_error(f"Attempt {i+1}/{max_retries} failed: {e}")
                if i == max_retries - 1:
                    raise
                time.sleep(delay)
                delay *= 2

    def _translate_batch(self, memory, texts: List[str], target_lang: str) -> List[str]:
        # Use cache + translator_engine
        outputs: List[str] = [None] * len(texts)  # type: ignore
        to_query_idx = []
        to_query = []
        for i, t in enumerate(texts):
            # Memory first
            mem = self._get_memory_translation(memory, t, target_lang)
            if mem:
                outputs[i] = mem
                continue
            # Run-cache
            key = (t, target_lang)
            if key in self._cache:
                outputs[i] = self._cache[key]
            else:
                to_query_idx.append(i)
                to_query.append(t)
        if to_query:
            def call():
                return self.translator_engine.translate(to_query, target_lang)
            translated_list = self._retry(call, max_retries=3)
            for j, out in enumerate(translated_list):
                idx = to_query_idx[j]
                outputs[idx] = out
                self._cache[(texts[idx], target_lang)] = out
                self._update_memory(memory, texts[idx], out)
        return [x or "" for x in outputs]

    def _fallback_translate(self, memory, text, target_lang):
        # Returns a single string; use batch variant for speed when possible
        mem = self._get_memory_translation(memory, text, target_lang)
        if mem:
            return mem
        key = (text, target_lang)
        if key in self._cache:
            return self._cache[key]

        protected_text, placeholder_map = self._protect_markers(text)
        try:
            translated_protected = self._translate_batch(memory, [protected_text], target_lang)[0]
            translated_protected = re.sub(r"&\s+([a-zA-Z]+)\s*;", r"&\1;", translated_protected)
            translated = self._restore_markers(translated_protected, placeholder_map)
            translated = self._clean_translated_text(translated)
            if not self._is_valid_translation(translated):
                self._display_error(f"Invalid translation detected for '{text}' in '{target_lang}'. Using original text as fallback.")
                return text
            self._cache[key] = translated
            self._update_memory(memory, text, translated)
            return translated
        except exceptions.NotValidPayload as e:
            self._display_error(f"Invalid payload for '{text}'. Error: {e}")
            return text
        except Exception as e:
            self._display_error(f"Translation failed for '{text}' → '{target_lang}': {e}")
            return text

    def _process_translation(self, memory, pot_entry, glossary_lookup, existing_po_lookup, target_lang):
        msgid = pot_entry.msgid
        msgctxt = pot_entry.msgctxt or ''
        key_ctxt = (msgid, msgctxt)

        # Custom rules (non-plural)
        custom = self._apply_custom_rules(msgid, target_lang)
        if custom:
            self._update_memory(memory, msgid, custom)
            self._counts["translated"] += 1
            return custom, "Custom Rule"

        # Glossary (context-aware)
        gloss = self._match_glossary(glossary_lookup, msgid, msgctxt)
        if gloss:
            if not self._placeholders_are_valid(msgid, gloss) or self._is_likely_untranslated(msgid, gloss):
                fb = self._fallback_translate(memory, msgid, target_lang)
                self._counts["translated"] += 1
                return fb, "Glossary (Fuzzy)"
            self._update_memory(memory, msgid, gloss)
            self._counts["reused"] += 1
            return gloss, "Glossary"

        # Existing PO reuse
        if key_ctxt in existing_po_lookup:
            existing = existing_po_lookup[key_ctxt]
            if not self._placeholders_are_valid(msgid, existing) or self._is_likely_untranslated(msgid, existing):
                fb = self._fallback_translate(memory, msgid, target_lang)
                self._counts["translated"] += 1
                return fb, "Existing PO (Fuzzy)"
            self._update_memory(memory, msgid, existing)
            self._counts["reused"] += 1
            return existing, "Existing PO"

        # MT fallback
        fb = self._fallback_translate(memory, msgid, target_lang)
        self._counts["translated"] += 1
        return fb, "Machine Translation"

    # -----------------------
    # Pluralization helpers
    # -----------------------
    def _plural_header_for_lang(self, lang: str) -> str:
        return self.plural_forms_header.get(lang) or self.plural_forms_header.get(lang.split('_', 1)[0]) or "nplurals=2; plural=(n != 1);"

    def _nplurals_from_header(self, header: str) -> int:
        m = re.search(r"nplurals\s*=\s*(\d+)", header)
        return int(m.group(1)) if m else 2

    def _plural_categories_for_lang(self, lang: str) -> List[str]:
        # Requires Babel; otherwise default to [one, other]
        base = lang.split('_', 1)[0]
        if PluralRule and Locale:
            try:
                loc = Locale.parse(lang)
            except Exception:
                try:
                    loc = Locale.parse(base)
                except Exception:
                    loc = None
            if loc is not None:
                # Common set – order is heuristic (one, two, few, many, other)
                return [c for c in ["one", "two", "few", "many", "other"] if c in loc.plural_form.rules]
        return ["one", "other"]

    def _pluralize_entry(self, memory, entry: polib.POEntry, target_lang: str) -> Dict[int, str]:
        header = self._plural_header_for_lang(target_lang)
        npl = self._nplurals_from_header(header)
        categories = self._plural_categories_for_lang(target_lang)
        # Ensure at least one/other
        if "one" not in categories:
            categories = ["one"] + [c for c in categories if c != "one"]
        if "other" not in categories:
            categories = categories + ["other"]

        # Build base templates: try custom plural templates, else translate msgid and msgid_plural
        templates_by_cat: Dict[str, str] = {}
        for cat in categories:
            custom = self._apply_custom_rules(entry.msgid, target_lang, plural_category=cat)
            if custom:
                templates_by_cat[cat] = custom

        if not templates_by_cat:
            # Fallback: translate singular and plural once each
            one_tmpl = self._fallback_translate(memory, entry.msgid, target_lang)
            other_tmpl = self._fallback_translate(memory, entry.msgid_plural or entry.msgid, target_lang)
            templates_by_cat["one"] = one_tmpl
            templates_by_cat["other"] = other_tmpl

        # Map indices 0..npl-1 to categories heuristically: 0->one, last->other
        idx_map: List[str] = []
        if npl == 1:
            idx_map = ["other"]
        elif npl == 2:
            idx_map = ["one", "other"]
        elif npl == 3:
            # Slavic-like: one, few, other
            pref = ["one", "few", "other"]
            idx_map = [c if c in categories else "other" for c in pref]
        elif npl == 4:
            pref = ["one", "two", "few", "other"]
            idx_map = [c if c in categories else "other" for c in pref]
        else:  # 5 or 6 (Arabic)
            pref = ["zero", "one", "two", "few", "many", "other"]
            idx_map = [c if c in categories else "other" for c in pref[:npl]]

        msgstr_plural: Dict[int, str] = {}
        for i, cat in enumerate(idx_map):
            tmpl = templates_by_cat.get(cat) or templates_by_cat.get("other") or templates_by_cat.get("one") or (entry.msgid_plural or entry.msgid)
            msgstr_plural[i] = tmpl
        return msgstr_plural

    # -----------------------
    # POT diffing
    # -----------------------
    def _snapshot_from_pot(self, pot: polib.POFile) -> Dict[str, Dict]:
        snap = {}
        for e in pot:
            key = (e.msgctxt or '') + "\u241E" + (e.msgid or '') + "\u241E" + (e.msgid_plural or '')
            snap[key] = {
                "msgctxt": e.msgctxt or '',
                "msgid": e.msgid or '',
                "msgid_plural": e.msgid_plural or ''
            }
        return snap

    def _diff_snapshots(self, old: Dict[str, Dict], new: Dict[str, Dict]) -> Dict[str, str]:
        # returns key -> status: new|modified|unchanged
        diff = {}
        for k, nv in new.items():
            if k not in old:
                diff[k] = "new"
            else:
                ov = old[k]
                if nv["msgid"] != ov["msgid"] or nv["msgid_plural"] != ov["msgid_plural"]:
                    diff[k] = "modified"
                else:
                    diff[k] = "unchanged"
        return diff

    # -----------------------
    # QA helpers
    # -----------------------
    def _qa_check(self, entry: polib.POEntry, translated: str, status: str, target_lang: str):
        issues = []
        if not translated:
            issues.append("empty")
        if not self._placeholders_are_valid(entry.msgid if not entry.msgid_plural else entry.msgid_plural, translated):
            issues.append("placeholders")
        # HTML balance (very naive): count opening/closing tags
        tags = self.html_tag_regex.findall(translated)
        opens = sum(1 for t in tags if not t.startswith("</") and not t.endswith("/>") )
        closes = sum(1 for t in tags if t.startswith("</"))
        if opens != closes:
            issues.append("html_unbalanced")
        if self._is_likely_untranslated(entry.msgid, translated):
            issues.append("unchanged_like")
        row = {
            "msgctxt": entry.msgctxt or '',
            "msgid": entry.msgid,
            "msgid_plural": entry.msgid_plural or '',
            "target_lang": target_lang,
            "status": status,
            "issues": ",".join(issues)
        }
        self._qa_rows.append(row)
        if "placeholders" in issues or "empty" in issues:
            self._counts["failed"] += 1

    # -----------------------
    # Main run
    # -----------------------
    def run(self, pot_path, zip_path, csv_path, target_langs, output_dir):
        self._display_status("Starting WP Localization Tool")

        self.pot_file_path = pot_path
        self.zip_file_path = zip_path
        self.csv_file_path = csv_path
        self.target_languages = target_langs

        project_name = os.path.splitext(os.path.basename(pot_path))[0]
        project_dir = os.path.join(output_dir, project_name)
        os.makedirs(project_dir, exist_ok=True)

        try:
            if not self.pot_file_path or not os.path.exists(self.pot_file_path):
                self._display_error("POT file not found.")
                return None

            pot_file = polib.pofile(self.pot_file_path)

            # POT diffing against last snapshot
            snapshot_path = self._get_snapshot_file_path(project_name)
            prev_snap = {}
            if os.path.exists(snapshot_path):
                try:
                    with open(snapshot_path, 'r', encoding='utf-8') as f:
                        prev_snap = json.load(f)
                except Exception:
                    prev_snap = {}
            new_snap = self._snapshot_from_pot(pot_file)
            diff_map = self._diff_snapshots(prev_snap, new_snap)

            # Persist new snapshot for next run
            with open(snapshot_path, 'w', encoding='utf-8') as f:
                json.dump(new_snap, f, ensure_ascii=False, indent=2)

            glossary = self._parse_glossary_csv(self.csv_file_path) if self.csv_file_path and os.path.exists(self.csv_file_path) else {}
            existing = self._extract_and_parse_existing_pos(self.zip_file_path) if self.zip_file_path and os.path.exists(self.zip_file_path) else {}

            # Prepare list of entries with their diff status
            entry_status: Dict[polib.POEntry, str] = {}
            for e in pot_file:
                key = (e.msgctxt or '') + "\u241E" + (e.msgid or '') + "\u241E" + (e.msgid_plural or '')
                status = diff_map.get(key, "new")
                entry_status[e] = status
                self._counts[status] += 1

            timestamp = datetime.utcnow().strftime("%Y-%m-%dT%H-%M-%SZ")

            for target_language in self.target_languages:
                self._qa_rows = []
                # Reset per-language counters that matter (keep global diffs)
                self._counts.update({"reused": 0, "fuzzy": 0, "failed": 0, "translated": 0})

                memory = self._load_memory(project_name, target_language)
                self._display_status(f"Translating into {target_language}…")
                po = polib.POFile()
                now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S+0000")

                po.metadata = {
                    'Project-Id-Version': 'Colab Free',
                    'POT-Creation-Date': now,
                    'PO-Revision-Date': now,
                    'Language': target_language,
                    'MIME-Version': '1.0',
                    'Content-Type': 'text/plain; charset=UTF-8',
                    'Content-Transfer-Encoding': '8bit',
                    'X-Generator': 'Colab Tool',
                    'Plural-Forms': self._plural_header_for_lang(target_language)
                }

                for entry in pot_file:
                    if not entry.msgid:
                        continue
                    status = entry_status.get(entry, "new")
                    try:
                        if entry.msgid_plural:
                            # Plural path: build msgstr_plural
                            msgstr_plural = self._pluralize_entry(memory, entry, target_language)
                            new_entry = polib.POEntry(
                                msgid=entry.msgid,
                                msgid_plural=entry.msgid_plural,
                                msgstr_plural=msgstr_plural,
                                msgctxt=entry.msgctxt,
                                occurrences=entry.occurrences,
                                comment=entry.comment,
                                tcomment=entry.tcomment
                            )
                            if status == "modified":
                                new_entry.flags.append("fuzzy")
                                self._counts["fuzzy"] += 1
                            po.append(new_entry)
                            # QA for each plural form (combine issues)
                            for i, s in msgstr_plural.items():
                                self._qa_check(entry, s, status, target_language)
                            continue

                        # Non-plural path
                        translated_msgstr, source = self._process_translation(memory, entry, glossary, existing, target_language)

                        new_entry = polib.POEntry(
                            msgid=entry.msgid,
                            msgstr=translated_msgstr,
                            msgctxt=entry.msgctxt,
                            occurrences=entry.occurrences,
                            comment=entry.comment,
                            tcomment=entry.tcomment
                        )
                        if status == "modified" or "Fuzzy" in source or "Fallback" in source:
                            new_entry.flags.append("fuzzy")
                            self._counts["fuzzy"] += 1
                        if status == "unchanged" and source in ("Glossary", "Existing PO"):
                            self._counts["reused"] += 1

                        po.append(new_entry)
                        self._qa_check(entry, translated_msgstr, status, target_language)
                    except Exception as e:
                        self._display_error(f"Failed to translate string '{entry.msgid[:50]}…'. Error: {e}")
                        new_entry = polib.POEntry(
                            msgid=entry.msgid,
                            msgstr='',
                            msgctxt=entry.msgctxt,
                            occurrences=entry.occurrences,
                            comment=entry.comment,
                            tcomment=entry.tcomment
                        )
                        new_entry.flags.append("fuzzy")
                        self._counts["failed"] += 1
                        po.append(new_entry)

                # --- Save PO & MO files with versioning ---
                counter = 1
                while True:
                    out_po = os.path.join(project_dir, f"{target_language}-v{counter}.po")
                    out_mo = os.path.join(project_dir, f"{target_language}-v{counter}.mo")
                    if not os.path.exists(out_po) and not os.path.exists(out_mo):
                        po.save(out_po)
                        po.save_as_mofile(out_mo)
                        break
                    counter += 1

                # Save memory JSON
                self._save_memory(memory, project_name, target_language)

                # --- Reports ---
                report_json = os.path.join(project_dir, f"report-{target_language}-{timestamp}.json")
                report_csv = os.path.join(project_dir, f"report-{target_language}-{timestamp}.csv")
                report = {
                    "language": target_language,
                    "generated_at": timestamp,
                    "counts": dict(self._counts),
                    "rows": self._qa_rows,
                }
                try:
                    with open(report_json, 'w', encoding='utf-8') as f:
                        json.dump(report, f, ensure_ascii=False, indent=2)
                except Exception as e:
                    self._display_error(f"Failed to write JSON report: {e}")
                try:
                    # CSV
                    if self._qa_rows:
                        headers = ["msgctxt", "msgid", "msgid_plural", "target_lang", "status", "issues"]
                        with open(report_csv, 'w', encoding='utf-8', newline='') as f:
                            w = csv.DictWriter(f, fieldnames=headers)
                            w.writeheader()
                            for r in self._qa_rows:
                                w.writerow({k: r.get(k, "") for k in headers})
                except Exception as e:
                    self._display_error(f"Failed to write CSV report: {e}")

            self._display_status("Translation complete.")
            return True

        except Exception as e:
            self._display_error(f"Unexpected error during setup or file processing: {e}")
            return False


