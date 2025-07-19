import polib
import json
import os
from pathlib import Path
from typing import List, Dict, Any, Optional
import requests
from dataclasses import dataclass
import time
from concurrent.futures import ThreadPoolExecutor
import re
import argparse
from enum import Enum
from collections import defaultdict
import logging
import sys
import glob
from concurrent.futures import as_completed
import subprocess
import shutil

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class TranslationRules:
    """Translation rules for a specific language"""
    language_name: str
    language_code: str
    plural_forms: str
    context: str

@dataclass  
class TranslationConfig:
    """Configuration for translation service"""
    api_key: str
    base_url: str
    model: str

# Base teaching context that applies to all languages
BASE_TEACHING_CONTEXT = """You are a friendly and patient high school Python teacher translating from English to {language_name}.
Your goal is to make Python programming accessible and engaging for young students.

Follow these translation rules:
1. Use clear, simple language that high school students can understand
2. Keep explanations friendly and encouraging
3. Maintain a teaching tone that guides students through concepts
4. Keep all code, variables, and technical terms in English
5. Preserve all markdown formatting, code blocks, and special markers
6. Maintain all HTML tags and their attributes
7. Keep all placeholders (e.g., {{variable}}, %s, etc.) unchanged
8. Preserve all newlines and spacing
9. Keep all numbers and units unchanged
10. Maintain all punctuation style
11. Keep all URLs and email addresses unchanged
12. Preserve all special characters and emojis
13. IMPORTANT: Never translate or modify special strings that start with double underscores (e.g., __copyable__, __code0__, __program__)
14. Keep all special strings exactly as they appear in the original text

Remember to:
- Use age-appropriate analogies and examples
- Break down complex concepts into simpler terms
- Maintain an encouraging and supportive tone
- Keep technical explanations clear but not oversimplified"""

class Language(Enum):
    """Supported languages and their translation rules"""
    ZH = TranslationRules(
        language_name="Chinese",
        language_code="zh",
        plural_forms="nplurals=1; plural=0;",
        context=BASE_TEACHING_CONTEXT.format(language_name="Chinese (Simplified)")
    )
    FR = TranslationRules(
        language_name="French",
        language_code="fr",
        plural_forms="nplurals=2; plural=(n > 1);",
        context=BASE_TEACHING_CONTEXT.format(language_name="French")
    )
    # Example of how to add a new language:
    # ES = TranslationRules(
    #     language_name="Spanish",
    #     language_code="es",
    #     plural_forms="nplurals=2; plural=(n != 1);",
    #     context=BASE_TEACHING_CONTEXT.format(language_name="Spanish")
    # )

    @classmethod
    def get_rules(cls, language_code: str) -> TranslationRules:
        """Get translation rules for a language code."""
        try:
            return cls[language_code.upper()].value
        except KeyError:
            raise ValueError(f"Unsupported language code: {language_code}")

    @classmethod
    def add_language(cls, language_code: str, language_name: str, plural_forms: str) -> None:
        """Add a new language to the supported languages.
        
        Args:
            language_code: Two-letter language code (e.g., 'es' for Spanish)
            language_name: Full name of the language
            plural_forms: Plural forms expression for the language
        """
        # Create new TranslationRules instance
        rules = TranslationRules(
            language_name=language_name,
            language_code=language_code,
            plural_forms=plural_forms,
            context=BASE_TEACHING_CONTEXT.format(language_name=language_name)
        )
        
        # Add to enum
        cls._member_map_[language_code.upper()] = rules
        cls._member_names_.append(language_code.upper())
        cls._value2member_map_[rules] = rules

class POFileSplitter:
    def __init__(self, input_file: str, base_output_dir: str, chunk_size: int):
        """Initialize the PO file splitter.
        
        Args:
            input_file: Path to the input PO file
            base_output_dir: Base directory for chunks (will create chunks/en/ subdirectory)
            chunk_size: Maximum number of entries per chunk (for large chapters)
        """
        self.input_file = input_file
        self.base_output_dir = Path(base_output_dir)
        self.en_chunks_dir = self.base_output_dir / "chunks" / "en"
        self.chunk_size = chunk_size
        self.logger = logging.getLogger(__name__)
        self.logger.info(f"Initializing POFileSplitter with input: {input_file}, output: {self.en_chunks_dir}, max chunk size: {chunk_size}")

    def extract_chapter_name(self, msgid: str) -> str:
        """Extract chapter name from msgid."""
        # Handle different msgid patterns
        if msgid.startswith('pages.'):
            # Extract chapter from patterns like: pages.IntroducingNestedLoops.steps.crack_password_exercise.hints.0.text
            parts = msgid.split('.')
            if len(parts) >= 2:
                return parts[1]  # IntroducingNestedLoops
        elif msgid.startswith('frontend.'):
            # Frontend UI elements
            return 'frontend_ui'
        elif 'hint' in msgid.lower():
            # Hint-related entries
            return 'hints'
        elif 'code_bits.' in msgid:
            # Code bits
            return 'code_bits'
        elif any(marker in msgid for marker in ['__program__', '__code', '__copyable__']):
            # Special markers
            return 'special_markers'
        else:
            # General/uncategorized entries
            return 'general'

    def split_entries(self) -> None:
        """Split the PO file into chunks organized by chapters and save to chunks/en/."""
        try:
            # Load the PO file
            self.logger.info(f"Loading PO file: {self.input_file}")
            po_file = polib.pofile(self.input_file)
            total_entries = len(po_file)
            self.logger.info(f"Found {total_entries} entries to split")

            # Group entries by chapter
            chapters = defaultdict(list)
            for entry in po_file:
                chapter_name = self.extract_chapter_name(entry.msgid)
                chapters[chapter_name].append(entry)

            self.logger.info(f"Organized entries into {len(chapters)} chapters:")
            for chapter, entries in chapters.items():
                self.logger.info(f"  - {chapter}: {len(entries)} entries")

            # Create English chunks directory
            self.en_chunks_dir.mkdir(parents=True, exist_ok=True)
            self.logger.info(f"Created English chunks directory: {self.en_chunks_dir}")

            # Save each chapter as one or more chunks to en/ directory
            chunk_count = 0
            for chapter_name, entries in chapters.items():
                # If chapter has too many entries, split into multiple chunks
                if len(entries) <= self.chunk_size:
                    # Single chunk for this chapter
                    chunk_count += 1
                    chunk_file = self.en_chunks_dir / f"{chapter_name}.po"
                    self.save_chunk(entries, chunk_file, po_file.metadata)
                    self.logger.info(f"Saved chapter '{chapter_name}' to {chunk_file}")
                else:
                    # Split large chapter into multiple chunks
                    num_chunks = (len(entries) + self.chunk_size - 1) // self.chunk_size
                    for i in range(num_chunks):
                        start_idx = i * self.chunk_size
                        end_idx = min((i + 1) * self.chunk_size, len(entries))
                        chunk_entries = entries[start_idx:end_idx]
                        
                        chunk_count += 1
                        chunk_file = self.en_chunks_dir / f"{chapter_name}_part{i+1:02d}.po"
                        self.save_chunk(chunk_entries, chunk_file, po_file.metadata)
                        self.logger.info(f"Saved chapter '{chapter_name}' part {i+1}/{num_chunks} to {chunk_file}")

            self.logger.info(f"Successfully split PO file into {chunk_count} chapter-based chunks in {self.en_chunks_dir}")

        except Exception as e:
            self.logger.error(f"Error splitting PO file: {str(e)}")
            raise

    def save_chunk(self, entries: List[polib.POEntry], chunk_file: Path, metadata: dict):
        """Save a chunk of entries to a PO file."""
        chunk_po = polib.POFile()
        chunk_po.metadata = metadata.copy()
        chunk_po.extend(entries)
        chunk_po.save(str(chunk_file))

class Translator:
    def __init__(self, config: TranslationConfig, language_code: str):
        """Initialize the translator.
        
        Args:
            config: Translation configuration
            language_code: Language code to translate to
        """
        self.config = config
        self.language_code = language_code
        self.rules = Language.get_rules(language_code)
        self.logger = logging.getLogger(__name__)
        self.logger.info(f"Initialized translator for {self.rules.language_name}")
        
        # Initialize HTTP session
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {config.api_key}",
            "Content-Type": "application/json"
        })

    def is_chunk_translated(self, chunk_file: str) -> bool:
        """Check if a chunk file is already translated."""
        try:
            chunk = polib.pofile(chunk_file)
            total_entries = len(chunk)
            translated_entries = 0
            
            for entry in chunk:
                if entry.msgstr and entry.msgstr.strip():
                    translated_entries += 1
                elif entry.msgstr_plural:
                    # Check if any plural form is translated
                    if any(msgstr.strip() for msgstr in entry.msgstr_plural.values()):
                        translated_entries += 1
            
            # Consider chunk translated if at least 80% of entries are translated
            translation_percentage = (translated_entries / total_entries) * 100 if total_entries > 0 else 0
            is_translated = translation_percentage >= 80
            
            self.logger.debug(f"Chunk {os.path.basename(chunk_file)}: {translated_entries}/{total_entries} entries translated ({translation_percentage:.1f}%)")
            
            return is_translated
            
        except Exception as e:
            self.logger.error(f"Error checking translation status of {chunk_file}: {str(e)}")
            return False

    def prepare_translation_request(self, chunk: polib.POFile) -> Dict:
        """Prepare the translation request payload."""
        # Convert PO entries to text format
        entries_text = []
        for entry in chunk:
            # Add special markers to help preserve special strings and formatting
            entry_text = f"msgid: {entry.msgid}\n"
            if entry.msgstr:
                # Mark special strings with a unique marker
                msgstr = entry.msgstr
                
                # Special handling for misc terms
                if entry.msgid.startswith("misc_terms."):
                    # For misc terms, preserve all newlines and formatting exactly
                    msgstr = msgstr.replace('\n', '<NEWLINE>')
                    # Also preserve markdown formatting
                    msgstr = msgstr.replace('*', '<ITALIC>')
                    msgstr = msgstr.replace('**', '<BOLD>')
                    msgstr = msgstr.replace('`', '<CODE>')
                    msgstr = msgstr.replace('[', '<LINK_START>')
                    msgstr = msgstr.replace(']', '<LINK_END>')
                    msgstr = msgstr.replace('(', '<URL_START>')
                    msgstr = msgstr.replace(')', '<URL_END>')
                else:
                    # For regular entries, just preserve newlines
                    msgstr = msgstr.replace('\n', '<NEWLINE>')
                
                # Mark special strings
                msgstr = re.sub(r'(__\w+__)', r'<SPECIAL>\1</SPECIAL>', msgstr)
                entry_text += f"msgstr: {msgstr}\n"
            if entry.msgid_plural:
                entry_text += f"msgid_plural: {entry.msgid_plural}\n"
                for i, msgstr in enumerate(entry.msgstr_plural.values()):
                    # Mark newlines and special strings in plural forms too
                    msgstr = msgstr.replace('\n', '<NEWLINE>')
                    msgstr = re.sub(r'(__\w+__)', r'<SPECIAL>\1</SPECIAL>', msgstr)
                    entry_text += f"msgstr[{i}]: {msgstr}\n"
            entries_text.append(entry_text)

        # Combine all entries
        text_to_translate = "\n\n".join(entries_text)
        self.logger.debug(f"Prepared text to translate (first 100 chars): {text_to_translate[:100]}")

        # Prepare the system message with rules
        system_message = f"""You are a professional translator. Your task is to translate the following PO file entries from English to {self.rules.language_name}.

{self.rules.context}

The input will be in PO file format with msgid (English) and msgstr (translation) pairs.
Only translate the text in the msgstr fields, keeping all other formatting, markers, and structure exactly as is.

Special formatting rules:
1. Special strings marked with <SPECIAL> tags must be preserved exactly as they are
2. Newlines marked with <NEWLINE> must be preserved exactly as they are, including their position and count
3. For misc_terms entries (starting with "misc_terms."):
   - Preserve all newlines exactly as they appear in the original
   - Preserve all markdown formatting:
     * <ITALIC> for italics (*)
     * <BOLD> for bold (**)
     * <CODE> for code blocks (`)
     * <LINK_START> and <LINK_END> for links ([ and ])
     * <URL_START> and <URL_END> for URLs (( and ))
   - Keep all URLs and links unchanged
   - Maintain the exact same number of newlines as the original

Return the translated text in the same PO file format."""

        return {
            "model": self.config.model,
            "messages": [
                {"role": "system", "content": system_message},
                {"role": "user", "content": text_to_translate}
            ],
            "temperature": 0.3
        }

    def translate_chunk(self, en_chunk_file: str, target_chunk_file: str) -> Optional[polib.POFile]:
        """Translate a chunk from English to target language."""
        try:
            # Check if target chunk already exists and is translated
            if os.path.exists(target_chunk_file) and self.is_chunk_translated(target_chunk_file):
                self.logger.info(f"Skipping already translated chunk: {os.path.basename(target_chunk_file)}")
                return polib.pofile(target_chunk_file)
            
            self.logger.info(f"Translating {os.path.basename(en_chunk_file)} → {os.path.basename(target_chunk_file)}")
            
            # Load the English chunk
            self.logger.debug(f"Loading English chunk: {en_chunk_file}")
            chunk = polib.pofile(en_chunk_file)
            self.logger.debug(f"Loaded chunk with {len(chunk)} entries")

            # Prepare translation request
            payload = self.prepare_translation_request(chunk)
            self.logger.debug("Prepared translation request")

            # Make API call
            self.logger.debug(f"Making API call to {self.config.base_url}")
            response = self.session.post(self.config.base_url, json=payload)
            
            if response.status_code == 200:
                result = response.json()
                translated_text = result['choices'][0]['message']['content']
                self.logger.debug(f"Received translation (first 100 chars): {translated_text[:100]}")
                
                # Parse the translated text and update the chunk
                updated_chunk = self.parse_translated_text(translated_text, chunk)
                
                if updated_chunk:
                    # Ensure target directory exists
                    os.makedirs(os.path.dirname(target_chunk_file), exist_ok=True)
                    # Save to target language directory
                    updated_chunk.save(target_chunk_file)
                    self.logger.info(f"Successfully translated and saved: {os.path.basename(target_chunk_file)}")
                    return updated_chunk
                else:
                    self.logger.error(f"Failed to parse translated text for {en_chunk_file}")
                    return None
            else:
                self.logger.error(f"API error {response.status_code}: {response.text}")
                return None
                
        except Exception as e:
            self.logger.error(f"Error translating chunk {en_chunk_file}: {str(e)}")
            return None

    def parse_translated_text(self, translated_text: str, original_chunk: polib.POFile) -> Optional[polib.POFile]:
        """Parse the translated text and update the original chunk with translations."""
        try:
            self.logger.debug("Parsing translated text")
            translated_lines = translated_text.split('\n')
            current_entry = None
            current_key = None

            for line in translated_lines:
                line = line.strip()
                if not line:
                    continue
                    
                if line.startswith('msgid: '):
                    current_key = 'msgid'
                    msgid = line[7:].strip()
                    # Find the entry in the original chunk
                    current_entry = original_chunk.find(msgid)
                    if current_entry:
                        self.logger.debug(f"Found entry for msgid: {msgid[:50]}...")
                    else:
                        self.logger.warning(f"Could not find entry for msgid: {msgid[:50]}...")
                        
                elif line.startswith('msgid_plural: '):
                    current_key = 'msgid_plural'
                    msgid_plural = line[14:].strip()
                    if current_entry and current_entry.msgid_plural == msgid_plural:
                        self.logger.debug(f"Found entry for msgid_plural: {msgid_plural[:50]}...")
                        
                elif line.startswith('msgstr: '):
                    if current_entry and current_key == 'msgid':
                        translation = line[8:].strip()
                        
                        # Special handling for misc terms
                        if current_entry.msgid.startswith("misc_terms."):
                            # Restore markdown formatting
                            translation = translation.replace('<ITALIC>', '*')
                            translation = translation.replace('<BOLD>', '**')
                            translation = translation.replace('<CODE>', '`')
                            translation = translation.replace('<LINK_START>', '[')
                            translation = translation.replace('<LINK_END>', ']')
                            translation = translation.replace('<URL_START>', '(')
                            translation = translation.replace('<URL_END>', ')')
                        
                        # Restore newlines and special strings
                        translation = translation.replace('<NEWLINE>', '\n')
                        translation = re.sub(r'<SPECIAL>(__\w+__)</SPECIAL>', r'\1', translation)
                        
                        if translation and translation != current_entry.msgid:  # Only update if actually translated
                            current_entry.msgstr = translation
                            self.logger.debug(f"Updated msgstr for entry: {current_entry.msgid[:50]}...")
                            
                elif line.startswith('msgstr[0]: '):
                    if current_entry and current_key == 'msgid_plural':
                        translation = line[11:].strip()
                        # Restore newlines and special strings
                        translation = translation.replace('<NEWLINE>', '\n')
                        translation = re.sub(r'<SPECIAL>(__\w+__)</SPECIAL>', r'\1', translation)
                        if translation:
                            current_entry.msgstr_plural[0] = translation
                            self.logger.debug(f"Updated msgstr[0] for plural entry")
                            
                elif line.startswith('msgstr[1]: '):
                    if current_entry and current_key == 'msgid_plural':
                        translation = line[11:].strip()
                        # Restore newlines and special strings
                        translation = translation.replace('<NEWLINE>', '\n')
                        translation = re.sub(r'<SPECIAL>(__\w+__)</SPECIAL>', r'\1', translation)
                        if translation:
                            current_entry.msgstr_plural[1] = translation
                            self.logger.debug(f"Updated msgstr[1] for plural entry")

            self.logger.debug(f"Successfully parsed translated text")
            return original_chunk

        except Exception as e:
            self.logger.error(f"Error parsing translated text: {str(e)}")
            return None

class TranslationMerger:
    def __init__(self, chunks_dir: str, output_file: str, language_code: str):
        self.chunks_dir = chunks_dir
        self.output_file = output_file
        self.language_code = language_code
        self.logger = logging.getLogger(__name__)
        # Define the locales directory path
        self.locales_dir = Path(os.path.dirname(output_file)) / "locales" / language_code / "LC_MESSAGES"
        self.locales_dir.mkdir(parents=True, exist_ok=True)
        # Load English PO file for reference
        self.english_po = polib.pofile(os.path.join(os.path.dirname(output_file), "english.po"))

    def validate_special_strings(self, entry: polib.POEntry, original_entry: polib.POEntry) -> bool:
        """Validate that all special strings from the original entry are preserved in the translation."""
        try:
            # Extract special strings from original entry with their positions
            original_special_strings = []
            for match in re.finditer(r'(__\w+__)', original_entry.msgstr):
                original_special_strings.append((match.group(1), match.start()))
            
            # Extract special strings from translated entry with their positions
            translated_special_strings = []
            for match in re.finditer(r'(__\w+__)', entry.msgstr):
                translated_special_strings.append((match.group(1), match.start()))
            
            # Check if we have the same number of special strings
            if len(original_special_strings) != len(translated_special_strings):
                self.logger.warning(f"Mismatched special strings count for {entry.msgid[:50]}...")
                self.logger.warning(f"Original has {len(original_special_strings)} special strings: {[s[0] for s in original_special_strings]}")
                self.logger.warning(f"Translation has {len(translated_special_strings)} special strings: {[s[0] for s in translated_special_strings]}")
                return False
            
            # Check if each special string matches and is in a similar relative position
            for (orig_str, orig_pos), (trans_str, trans_pos) in zip(original_special_strings, translated_special_strings):
                if orig_str != trans_str:
                    self.logger.warning(f"Mismatched special string in {entry.msgid[:50]}...")
                    self.logger.warning(f"Original: {orig_str} at position {orig_pos}")
                    self.logger.warning(f"Translation: {trans_str} at position {trans_pos}")
                    return False
                
                # Calculate relative positions (as percentage of total length)
                orig_rel_pos = orig_pos / len(original_entry.msgstr)
                trans_rel_pos = trans_pos / len(entry.msgstr)
                
                # Allow some flexibility in position (within 20% of the text length)
                if abs(orig_rel_pos - trans_rel_pos) > 0.2:
                    self.logger.warning(f"Special string {orig_str} is too far from expected position in {entry.msgid[:50]}...")
                    self.logger.warning(f"Original relative position: {orig_rel_pos:.2f}")
                    self.logger.warning(f"Translation relative position: {trans_rel_pos:.2f}")
                    return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error validating special strings: {str(e)}")
            return False

    def fix_special_strings(self, entry: polib.POEntry, original_entry: polib.POEntry) -> polib.POEntry:
        """Fix missing or misplaced special strings in the translation by copying them from the original entry."""
        try:
            # Extract special strings from original entry with their context
            original_special_strings = []
            original_text = original_entry.msgstr
            translated_text = entry.msgstr
            
            # Find all special strings and their surrounding context
            for match in re.finditer(r'(__\w+__)', original_text):
                special_str = match.group(1)
                start = max(0, match.start() - 20)  # Get 20 chars before
                end = min(len(original_text), match.end() + 20)  # Get 20 chars after
                context = original_text[start:end]
                original_special_strings.append((special_str, context, match.start()))
            
            # For each special string in the original, ensure it exists in the translation
            fixed_text = translated_text
            for special_str, context, orig_pos in original_special_strings:
                # Check if the special string exists in the translation
                if special_str not in fixed_text:
                    # Find a good position to insert the special string
                    # Try to find similar context in the translation
                    context_words = set(re.findall(r'\w+', context))
                    best_pos = 0
                    best_match = 0
                    
                    # Look for similar context in the translation
                    for i in range(len(fixed_text) - len(context) + 1):
                        trans_context = fixed_text[i:i + len(context)]
                        trans_words = set(re.findall(r'\w+', trans_context))
                        common_words = len(context_words & trans_words)
                        if common_words > best_match:
                            best_match = common_words
                            best_pos = i
                    
                    # Insert the special string at the best position
                    if best_match > 0:
                        fixed_text = fixed_text[:best_pos] + special_str + fixed_text[best_pos:]
                    else:
                        # If no good context found, append at the end
                        fixed_text += f"\n{special_str}\n"
                    
                    self.logger.info(f"Added missing special string {special_str} to translation")
            
            # Create a new entry with the fixed translation
            fixed_entry = polib.POEntry(
                msgid=entry.msgid,
                msgstr=fixed_text,
                msgid_plural=entry.msgid_plural,
                msgstr_plural=entry.msgstr_plural,
                comment=entry.comment,
                tcomment=entry.tcomment,
                occurrences=entry.occurrences,
                flags=entry.flags,
                previous_msgid=entry.previous_msgid,
                previous_msgid_plural=entry.previous_msgid_plural,
                encoding=entry.encoding
            )
            
            # Validate the fix
            if not self.validate_special_strings(fixed_entry, original_entry):
                self.logger.warning(f"Failed to fix special strings for {entry.msgid[:50]}...")
                # If validation fails, return the original entry's msgstr
                fixed_entry.msgstr = original_entry.msgstr
                self.logger.info(f"Using original English text for {entry.msgid[:50]}...")
            
            return fixed_entry

        except Exception as e:
            self.logger.error(f"Error fixing special strings: {str(e)}")
            return entry

    def normalize_po_file(self, po_file: str) -> bool:
        """Normalize line endings and validate PO file format."""
        try:
            # Read the PO file
            with open(po_file, 'r', encoding='utf-8') as f:
                content = f.read()

            # Normalize line endings to \n
            content = content.replace('\r\n', '\n').replace('\r', '\n')

            # Parse the PO file using polib first to get proper structure
            po = polib.pofile(po_file)
            
            # Create a new PO file with normalized entries
            normalized_po = polib.POFile()
            normalized_po.metadata = po.metadata.copy()
            
            for entry in po:
                # Create a new entry
                new_entry = polib.POEntry(
                    msgid=entry.msgid.strip(),
                    msgstr=entry.msgstr.strip(),
                    msgid_plural=entry.msgid_plural.strip() if entry.msgid_plural else None,
                    msgstr_plural=entry.msgstr_plural if entry.msgstr_plural else None,
                    comment=entry.comment,
                    tcomment=entry.tcomment,
                    occurrences=entry.occurrences,
                    flags=entry.flags,
                    previous_msgid=entry.previous_msgid,
                    previous_msgid_plural=entry.previous_msgid_plural,
                    encoding=entry.encoding
                )
                normalized_po.append(new_entry)

            # Write back the normalized content
            normalized_po.save(po_file)
            
            # Validate the normalized file
            try:
                polib.pofile(po_file)
                self.logger.info(f"Successfully normalized and validated {po_file}")
                return True
            except Exception as e:
                self.logger.error(f"PO file validation failed: {str(e)}")
                return False

        except Exception as e:
            self.logger.error(f"Error normalizing PO file: {str(e)}")
            return False

    def compile_mo_file(self, po_file: str) -> bool:
        """Compile PO file to MO file using msgfmt."""
        try:
            # First normalize the PO file
            if not self.normalize_po_file(po_file):
                self.logger.error(f"Failed to normalize {po_file}")
                return False

            # Always use futurecoder.mo as the output filename
            mo_file = self.locales_dir / "futurecoder.mo"
            
            # Use msgfmt to compile the PO file to MO
            result = subprocess.run(
                ["msgfmt", "-o", str(mo_file), po_file],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                self.logger.info(f"Successfully compiled {po_file} to {mo_file}")
                return True
            else:
                self.logger.error(f"Failed to compile {po_file}: {result.stderr}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error compiling MO file: {str(e)}")
            return False

    def merge_translations(self) -> None:
        """Merge translated chunks into a single PO file and compile to MO."""
        self.logger.info(f"Starting merge process for {self.language_code}")
        self.logger.info(f"Looking for chunks in: {self.chunks_dir}")
        
        # Create output directory if it doesn't exist
        os.makedirs(os.path.dirname(os.path.abspath(self.output_file)), exist_ok=True)
        
        # Get all chunk files
        chunk_files = sorted(glob.glob(os.path.join(self.chunks_dir, "*.po")))
        if not chunk_files:
            self.logger.error(f"No chunk files found in {self.chunks_dir}")
            all_files = glob.glob(os.path.join(self.chunks_dir, "*"))
            self.logger.info(f"All files found: {all_files}")
            raise FileNotFoundError(f"No chunk files found in {self.chunks_dir}")
        
        self.logger.info(f"Found {len(chunk_files)} chapter-based chunk files to merge")
        for f in chunk_files:
            self.logger.info(f"  - {os.path.basename(f)}")

        # Create new PO file with metadata from english.po
        try:
            merged_po = polib.POFile()
            merged_po.metadata = self.english_po.metadata.copy()
            merged_po.metadata['Language'] = self.language_code
            
            # Get language rules for plural forms
            language_rules = Language.get_rules(self.language_code)
            merged_po.metadata['Plural-Forms'] = language_rules.plural_forms
        except Exception as e:
            self.logger.error(f"Failed to read english.po: {str(e)}")
            raise

        # Track statistics
        total_entries = 0
        translated_entries = 0
        skipped_entries = 0
        code_bits_kept = 0
        program_entries_kept = 0
        prediction_choices_kept = 0
        
        # Process each translated chunk
        for chunk_file in chunk_files:
            self.logger.info(f"Processing translated chunk: {chunk_file}")
            try:
                chunk_po = polib.pofile(chunk_file)
                total_entries += len(chunk_po)
                
                for entry in chunk_po:
                    if entry.msgstr and entry.msgstr.strip():  # Only include translated entries
                        # Find the corresponding English entry
                        original_entry = self.english_po.find(entry.msgid)
                        if original_entry:
                            # For Chinese and Tamil, keep certain entries in English
                            if self.language_code in ["zh", "ta"] and (
                                entry.msgid.startswith("code_bits.") or
                                entry.msgid.endswith(".program") or
                                "output_prediction_choices" in entry.msgid
                            ):
                                entry.msgstr = original_entry.msgstr  # Use English version
                                if entry.msgid.startswith("code_bits."):
                                    code_bits_kept += 1
                                    self.logger.info(f"Keeping English code bit: {entry.msgid[:50]}...")
                                elif entry.msgid.endswith(".program"):
                                    program_entries_kept += 1
                                    self.logger.info(f"Keeping English program entry: {entry.msgid[:50]}...")
                                else:
                                    prediction_choices_kept += 1
                                    self.logger.info(f"Keeping English prediction choice: {entry.msgid[:50]}...")

                        # Create a new entry with stripped content
                        new_entry = polib.POEntry(
                            msgid=entry.msgid.strip(),
                            msgstr=entry.msgstr.strip(),
                            msgid_plural=entry.msgid_plural.strip() if entry.msgid_plural else None,
                            msgstr_plural=entry.msgstr_plural if entry.msgstr_plural else None,
                            comment=entry.comment,
                            tcomment=entry.tcomment,
                            occurrences=entry.occurrences,
                            flags=entry.flags,
                            previous_msgid=entry.previous_msgid,
                            previous_msgid_plural=entry.previous_msgid_plural,
                            encoding=entry.encoding
                        )
                        merged_po.append(new_entry)
                        translated_entries += 1
                    else:
                        self.logger.warning(f"Skipping untranslated entry in {chunk_file}: {entry.msgid[:50]}...")
                        skipped_entries += 1
                        
            except Exception as e:
                self.logger.error(f"Error processing chunk {chunk_file}: {str(e)}")
                raise
        
        # Save the merged PO file
        try:
            # Save with proper formatting
            merged_po.save(self.output_file)
            self.logger.info(f"Successfully merged translations to {self.output_file}")
            
            # Normalize and compile the merged PO file to MO
            if self.compile_mo_file(self.output_file):
                self.logger.info(f"Successfully compiled MO file to {self.locales_dir}")
            else:
                self.logger.error("Failed to compile MO file")
            
            self.logger.info(f"Statistics:")
            self.logger.info(f"  Total entries: {total_entries}")
            self.logger.info(f"  Translated entries: {translated_entries}")
            if self.language_code in ["zh", "ta"]:
                self.logger.info(f"  Code bits kept in English: {code_bits_kept}")
                self.logger.info(f"  Program entries kept in English: {program_entries_kept}")
                self.logger.info(f"  Prediction choices kept in English: {prediction_choices_kept}")
            self.logger.info(f"  Skipped entries: {skipped_entries}")
            if total_entries > 0:
                self.logger.info(f"  Translation coverage: {(translated_entries/total_entries)*100:.1f}%")
        except Exception as e:
            self.logger.error(f"Failed to save merged file: {str(e)}")
            raise

def validate_language_code(language_code: str) -> bool:
    """Validate if the language code is supported"""
    try:
        Language(language_code)
        return True
    except ValueError:
        return False

def translate_all_chunks(translator: Translator, base_chunks_dir: str, language_code: str, max_workers: int = 3):
    """Translate all chunks from chunks/en/ to chunks/{lang}/, skipping already translated ones."""
    logger = logging.getLogger(__name__)
    
    en_chunks_dir = os.path.join(base_chunks_dir, "chunks", "en")
    target_chunks_dir = os.path.join(base_chunks_dir, "chunks", language_code)
    
    # Get all English chunk files
    en_chunk_files = sorted(glob.glob(os.path.join(en_chunks_dir, "*.po")))
    if not en_chunk_files:
        logger.error(f"No English chunk files found in {en_chunks_dir}")
        return
    
    logger.info(f"Found {len(en_chunk_files)} English chunk files in {en_chunks_dir}")
    logger.info(f"Will translate to {target_chunks_dir}")
    
    # Create target directory
    os.makedirs(target_chunks_dir, exist_ok=True)
    
    # Check which chunks need translation
    chunks_to_translate = []
    already_translated = []
    
    for en_chunk_file in en_chunk_files:
        chunk_name = os.path.basename(en_chunk_file)
        target_chunk_file = os.path.join(target_chunks_dir, chunk_name)
        
        if os.path.exists(target_chunk_file) and translator.is_chunk_translated(target_chunk_file):
            already_translated.append((en_chunk_file, target_chunk_file))
        else:
            chunks_to_translate.append((en_chunk_file, target_chunk_file))
    
    logger.info(f"Translation status:")
    logger.info(f"  - Already translated: {len(already_translated)} chunks")
    logger.info(f"  - Need translation: {len(chunks_to_translate)} chunks")
    
    if already_translated:
        logger.info("Already translated chunks:")
        for en_file, target_file in already_translated:
            logger.info(f"  ✓ {os.path.basename(target_file)}")
    
    if not chunks_to_translate:
        logger.info("All chunks are already translated! Skipping translation phase.")
        return
    
    logger.info("Chunks to translate:")
    for en_file, target_file in chunks_to_translate:
        logger.info(f"  → {os.path.basename(en_file)} → {os.path.basename(target_file)}")
    
    # Translate only the chunks that need translation
    logger.info(f"Starting translation of {len(chunks_to_translate)} chunks using {max_workers} workers...")
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit translation tasks
        future_to_chunk = {
            executor.submit(translator.translate_chunk, en_file, target_file): (en_file, target_file)
            for en_file, target_file in chunks_to_translate
        }
        
        completed = 0
        failed = 0
        
        # Process completed tasks
        for future in as_completed(future_to_chunk):
            en_file, target_file = future_to_chunk[future]
            try:
                result = future.result()
                if result is not None:
                    completed += 1
                    logger.info(f"Progress: {completed + failed}/{len(chunks_to_translate)} - Completed: {os.path.basename(target_file)}")
                else:
                    failed += 1
                    logger.error(f"Progress: {completed + failed}/{len(chunks_to_translate)} - Failed: {os.path.basename(target_file)}")
            except Exception as e:
                failed += 1
                logger.error(f"Progress: {completed + failed}/{len(chunks_to_translate)} - Error: {str(e)}")
        
        logger.info(f"Translation completed: {completed} successful, {failed} failed")

def main():
    parser = argparse.ArgumentParser(description="Translate Futurecoder PO files")
    parser.add_argument("-l", "--language", required=True, help="Language code (e.g., zh, fr, es)")
    parser.add_argument("-k", "--api-key", required=True, help="API key for translation service")
    parser.add_argument("--base-url", default="https://api.openai.com/v1/chat/completions",
                      help="Base URL for the translation API")
    parser.add_argument("-m", "--model", default="gpt-3.5-turbo",
                      help="Model to use for translation")
    parser.add_argument("-i", "--input", default="./english.po",
                      help="Input PO file to translate")
    parser.add_argument("-o", "--output-dir", default="./",
                      help="Output directory for translated files")
    parser.add_argument("--max-workers", type=int, default=5,
                      help="Maximum number of parallel workers")
    parser.add_argument("--chunk-size", type=int, default=50,
                      help="Number of entries per chunk")
    parser.add_argument("--skip-mo", action="store_true",
                      help="Skip MO file compilation")
    args = parser.parse_args()

    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(f"translation_{args.language}.log"),
            logging.StreamHandler(sys.stdout)
        ]
    )
    logger = logging.getLogger(__name__)

    try:
        # Validate language code
        try:
            rules = Language.get_rules(args.language)
            logger.info(f"Using translation rules for {rules.language_name}")
        except ValueError as e:
            logger.error(str(e))
            logger.info("Supported languages: " + ", ".join(lang.value.language_name for lang in Language))
            sys.exit(1)

        # Create base chunks directory structure
        base_chunks_dir = args.output_dir
        en_chunks_dir = os.path.join(base_chunks_dir, "chunks", "en")
        target_chunks_dir = os.path.join(base_chunks_dir, "chunks", args.language)
        
        logger.info(f"Directory structure:")
        logger.info(f"  - English chunks: {en_chunks_dir}")
        logger.info(f"  - Target chunks: {target_chunks_dir}")

        # Initialize components
        config = TranslationConfig(
            api_key=args.api_key,
            base_url=args.base_url,
            model=args.model
        )
        
        # Initialize splitter with base output directory
        splitter = POFileSplitter(
            input_file=args.input,
            base_output_dir=base_chunks_dir,
            chunk_size=args.chunk_size
        )
        translator = Translator(config, args.language)
        merger = TranslationMerger(
            chunks_dir=target_chunks_dir,
            output_file=os.path.join(args.output_dir, f"{args.language}.po"),
            language_code=args.language
        )

        # Split the file into English chunks
        logger.info(f"Splitting PO file from: {args.input}")
        splitter.split_entries()
        
        # Translate chunks from en/ to {lang}/
        logger.info("Starting translation of chunks...")
        translate_all_chunks(translator, base_chunks_dir, args.language, args.max_workers)
        
        # Merge translations and compile MO file
        logger.info(f"Merging translated chunks to: {merger.output_file}")
        merger.merge_translations()
        
        logger.info("Translation process completed successfully!")
        logger.info(f"Final output files:")
        logger.info(f"  - PO file: {os.path.abspath(merger.output_file)}")
        logger.info(f"  - MO file: {os.path.abspath(merger.locales_dir / 'futurecoder.mo')}")
        
    except Exception as e:
        logger.error(f"Translation process failed: {str(e)}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()