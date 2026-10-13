#!/usr/bin/env python3
"""ed_voice - speech for the Edit Studio engine: recognition with word timestamps, subtitle/karaoke layers for
ed_text, SRT/ASS, script/lyrics alignment, translation plans, jump-cut data and the Higgsfield dubbing workflow.

ASR STACK (chosen 2026-10-08 by testing what the sandbox can reach; licences: MIT / Apache-2.0 only)
  1. Silero VAD v4 (MIT, 0.6 MB ONNX): speech regions -> <= 28 s chunks (silence/music gaps are never decoded),
     language ID on speech only, word edges trimmed to speech, pause data for jump cuts. No model -> energy VAD.
  2. Whisper large-v3-turbo (OpenAI, MIT), int8 ONNX export by k2-fsa/sherpa-onnx (Apache-2.0), run with the
     preinstalled onnxruntime + numpy (no torch, no pip): text with punctuation/casing, 99 languages, greedy decoding
     with temperature fallback (compression / logprob / no-speech rules of openai-whisper). The decoder graph is
     patched once in the cache (raw protobuf edit) so its cross-attention softmax becomes an output -> word times
     exactly like openai-whisper word_timestamps (alignment heads, median filter, DTW) = the fallback timing.
  3. Word timing = CTC forced alignment of Whisper's words with Meta Omnilingual ASR CTC 300M (Apache-2.0, 1600+
     languages, character vocabulary, 20 ms frames, int8 ONNX via sherpa-onnx), Viterbi in numpy with an optional
     word separator and a wildcard for digits/symbols, then energy-based edges (ends extended to the decay, onsets
     after pauses moved to the energy rise). Per-chunk gate: CTC is used when the aligner hears >= 35 % of the
     letters itself or agrees with DTW (median <= 120 ms); else DTW stays (voice buried under loud music).
     When it hears speech that contradicts low-confidence Whisper text, words get "suspect": true and a warning
     names the CTC reading (Whisper hallucinating on sobs/whispers, or a language Whisper does not know ->
     model='omni' recognises with the CTC model alone: lowercase, no punctuation).
  4. Fallback chain: model='auto' -> turbo -> small -> base -> tiny (download / RAM / disk failures fall through)
     -> user transcript text= (forced-aligned when any model works, else spread over the VAD speech) or srt=
     (cue timing; words interpolated inside cues). timing='dtw' skips the aligner (faster, +-3 frames).
  Memory: ORT arenas off (-35 % RSS); whisper and the aligner are never resident together when the memory cgroup
  is short (peak ~2.2 GB with turbo). Rejected: faster-whisper/ctranslate2, vosk, sherpa-onnx wheels (PyPI blocked,
  403); HuggingFace, alphacephei.com, openaipublic, pytorch.org (egress policy); parakeet, canary, MMS, SenseVoice
  (licences). Reachable: GitHub release assets (github.com/<org>/<repo>/releases/download/...).

MEASURED (this sandbox, 2 CPU cores; test audio = own Russian/English texts synthesised with CC0-data voices and
ffmpeg flite, word-by-word with exact boundaries; plus a real reference edit vs its text-event frames)
  WER turbo: Russian 8.5 % (10.2 % at 12 dB SNR; mostly digits for spelled numbers), English 0 %.
  Word onsets (CTC): Russian MAE 14 ms, 96 % within 1 frame @30 fps; English MAE 26 ms, 77 % / 85 % within 1 / 2
  frames; word ends MAE 19-40 ms. Whisper DTW alone: ~155 ms MAE (onsets ~140 ms early).
  Reference edit (two spoken sentences under music): transcript word-exact; first sentence onsets MAE 1.8 frames
  vs the edit's text events; in the second sentence the edit's text leads the voice by ~5 frames on purpose.
  Speed (uncontended): turbo encoder 5.8 s per 30 s window + 58 ms/token; aligner 0.2-0.3 x audio; VAD 1 h in
  ~15 s -> roughly 0.5-0.7 x real time for dense speech with turbo+CTC, 0.4 x with timing='dtw', tiny ~0.08 x.
  One core (claude.ai sandbox): about twice that. Results are cached by file hash, so each file is paid once.

INSTALL (automatic on first use; nothing is vendored into the project tree)
  Cache dir: $ED_VOICE_CACHE or ~/.cache/edit-studio/asr  (models, VAD, aligner, transcript cache).
  Source:    https://github.com/k2-fsa/sherpa-onnx/releases/download/asr-models/<archive>
  model   archive (download)  on disk (int8 only)  RAM peak  encoder per 30 s window / decoder per token (2 cores)
  tiny    116 MB              100 MB               ~0.4 GB   0.17 s / 16 ms     drafts only (weak on Russian)
  base    208 MB              154 MB               ~0.5 GB   -                  fallback
  small   639 MB              359 MB               ~1.0 GB   1.0 s / ~110 ms    fallback
  turbo   564 MB              990 MB               ~1.7 GB   5.8 s / ~58 ms     DEFAULT
  ctc     293 MB              366 MB               ~1.0 GB   ~9 s per 30 s      sherpa-onnx-omnilingual-asr-1600-
                                                                                 languages-300M-ctc-int8-2025-11-12
  vad     0.6 MB (silero_vad.onnx)
  python3 -I ed_voice.py models --get turbo ctc vad      (bz2 extraction of turbo takes ~70 s on one core)
  Manual (e.g. the claude.ai sandbox: allow github.com + release-assets.githubusercontent.com, or upload archives):
    curl -L -o t.tar.bz2 <source>/sherpa-onnx-whisper-turbo.tar.bz2
    tar -xjf t.tar.bz2 -C ~/.cache/edit-studio/asr --wildcards '*int8.onnx' '*tokens.txt'   (same for the ctc archive
    with '*model.int8.onnx' '*tokens.txt'); curl -L -o ~/.cache/edit-studio/asr/silero_vad.onnx <source>/silero_vad.onnx

API (times in seconds; ed_text wants OUTPUT time -> remap_words after cuts)
  transcribe(path, lang=None, model='auto'|'turbo'|'small'|'base'|'tiny'|'omni', prompt=None, text=None, srt=None,
             timing='auto'|'ctc'|'dtw') ->
      {"lang", "lang_prob", "model", "source": "asr|text|srt", "timing", "duration",
       "words": [{"w", "t0", "t1", "p", ("pa", "suspect")}], "segments": [{"t0", "t1", "text", "w0", "w1"}],
       "speech": [[t0, t1], ...] (VAD), "chunks": [...], "warnings": [...], "stats": {...}}
      cached by sha256(file) + options in <cache>/transcripts. p = Whisper word probability, pa = acoustic score.
  speech_segments(words|transcript, min_pause=.35, keep_pause=.12, fillers='sure'|'all'|'none', fps=None)
      -> pauses, fillers, maybe_fillers, repeats, voiced_gaps, cuts, keep, stats, (segments: EDL with fps)
  keep_to_segments(keep, fps, src) / remap_words(words, segments, fps) -> (output-time words, cuts inside words)
  subtitle_chunks(words, max_chars, max_lines, min_dur, max_cps, lead, tail, kind=None|'subtitle'|'karaoke', fps=30,
                  style=None, canvas=None, breaks=None, fillers='merge')
      -> ed_text layers, one per chunk, with words + lead/tail frames that make ed_text reproduce the chunk
         exactly (karaoke keeps per-word highlight timing); defaults from the clips/ugc cards (SUB_DEFAULTS) or,
         with style = an ed_text caption preset, from ed_text.caption_hints (karaoke-only presets -> karaoke).
         Phrase-aware breaks (punctuation, pauses; a modifier stays with its noun, a function word with the word it
         introduces, no lone last word of a sentence - English lists, punctuation / pauses for any language).
         Readable by construction (ed_qa: <= 20 chars/s, >= 0.7 s on screen): no line / chunk ends on a function
         word, filler-only chunks join a neighbour or stay unshown ("hidden"), short chunks take time from pauses
         and neighbours, then merge; "$10" ",000" ASR splits are joined; breaks = jump-cut times never crossed;
         a chunk the preset cannot show at full size is split in time by ed_text.fit_caption_layers (explicit).
  chunks_layer(chunks) -> one subtitle layer on ed_text's explicit-chunks path (translations: no word timing)
  break_lines(tokens, max_chars, max_lines) / to_srt(...) / to_ass(...) / from_srt(path_or_text) / cue_words(cues)
  align_text(words, known_text, path=None) -> known script/lyrics with times (text DP; acoustic when path given)
  translate_plan(words|transcript, target_lang) -> sentences + per-language budgets (LANG_RULES) for Claude to fill;
  apply_translation(plan, texts=None) -> {"layer", "chunks", "issues"} (re-segmented, timing per source sentence)
  speech_qa(words_out, layers, cuts, fps) -> first_word, pauses, word_cuts, reading_speed (genre-card checks)
  dub_master(edl) / import_dub(audio, dubbed_media, at, mode) / tts_lines(plan) / place_lines(audio, items)
  find_phrase(words, text, after=None, before=None, min_score=0.7) -> {"t0", "t1", "i0", "i1", "score", "text"}|None
      spoken-phrase search for in/out points by words: case, punctuation and number-format insensitive ("4 million"
      = "4,000,000" = "four million" = "4M"; "$10,000" = "10 000 dollars"; English + Russian number words), tolerant
      to ASR splits/merges ("life style" = "lifestyle", "$10" ",000"); fuzzy (edit distance on canon_text, then
      snapped to whole words - a neighbour that only partly matches is never pulled in); a different number than
      the query's is a different phrase. after/before (s) bound the search; ties -> earliest.
      find_phrase_all(...) -> every occurrence, best first; canon_text(text) -> the compared form.
  reaction_end(media, t, words=None, max_s=4.0) -> s: end of the non-verbal or one-word reaction after t (sigh,
      laugh, breath, "wow"; is_reaction(words) = one word or interjections only) at a quiet point before the next
      sentence: the decay of the last speech-band sound event, always before the next onset - the earliest of the
      next sentence's ASR start, its speech onset and any new sound right before it (sound_onsets on the full-band
      level: breath, hum, desk / mic thump) - minus 30 ms; detail=True -> (s, info with events / onsets)
  setup_starts(words, end_t, min_s=6, max_s=25, env=None) -> [{"t", "text", "score", "why"}] where a talk clip that
      ends at end_t should start: sentence starts after a pause, questions, topic openers first; leading "and/but",
      pronouns pointing back, mid-sentence starts and env "avoid" spans (popups) penalised
  clip_candidates(words, media=None, min_s=15, max_s=60, n=10) -> ranked 15-60 s windows for talk clips: start at
      a self-contained sentence, end at a sentence end + pause/reaction; score = hook x payoff x speech density
  CLI: python3 -I ed_voice.py transcribe|subs|jumpcuts|align|plan|models|phrase|reaction|clips ...  (-h for options)
       phrase WORDS.json "over 4 million" [--after S --before S --all];  reaction MEDIA T [--words WORDS.json]

DUBBING WORKFLOW (Higgsfield MCP `dubbing`; 18 languages: eng cmn fra hin ita jpn kor por rus tur spa deu ara pol
ind fil swe fin - see HF_DUB_LANG; translation + synthesis + lip-sync; NO cost preview -> run only after the user's
explicit "yes" for this exact clip and language)
  1. What to upload: a "dub master" rendered from the EDL - picture of the speech section(s) plus the ORIGINAL VOICE
     ONLY (music and SFX muted: render with audio.music/sfx removed), H.264/AAC, the shortest span that covers the
     speech (cost and lip-sync quality scale with length). Faces must be visible and unmirrored where lip-sync matters.
     Upload: media_upload(filename=...) -> curl PUT to upload_url -> media_confirm(type='video') -> media_id.
     A user's own local file goes through media_upload_widget instead (the user picks it).
  2. dubbing(params={video_id: media_id, target_language: 'eng'|'rus'|...}) -> job; wait with jobs_wait; download.
  3. Bring it back: import_dub(edl['audio'], dubbed.mp4, at=<output time where the master starts>) extracts the
     dubbed voice to WAV and returns an audio block with audio.voice = [{"path": dub.wav, "at", "in", "dur",
     "gain_db"}]; the original voice entries are removed (mode='replace') or kept 15-18 dB down under the dub
     (mode='voiceover', interview style). Music/SFX stay as they were; keep or add
     audio.duck = [{"under": "voice", "depth_db": 8-24 (genre card), "attack_ms": 15-80, "release_ms": 250-400}].
     Where lip-sync matters, also swap the picture of those segments to the dubbed video (segment src = dub).
  4. Subtitles for the dubbed version: transcribe(dub_wav, lang=<target>) -> subtitle_chunks(...) so the text
     follows the new voice (translated chunk timing from translate_plan follows the old voice).
  5. Languages outside the 18: translate_plan -> Claude translates -> synthesize lines with generate_audio
     (seed_audio, preset voice or a clone from create_voice; get_cost:true first) -> place each line at its chunk
     t0 in audio.voice (time-stretch <=1.15x or re-cut the picture if it is longer than its slot), no lip-sync.
     Voice clone: create_voice (widget) or create_voice_from_confirmed_audio (10 s-3 min of clean speech; costs
     credits; usable only when list_voices shows status completed). voice_change keeps timing and swaps the timbre.
"""
import os
import re
import sys
import json
import math
import time
import zlib
import base64
import string
import hashlib
import shutil
import tarfile
import argparse
import difflib
import subprocess
import unicodedata
from pathlib import Path

import numpy as np

VERSION = 1                      # bump when the transcript format/algorithm changes (invalidates the cache)
SR = 16000
HOP = 160                        # whisper mel hop (10 ms); attention frames are 20 ms
CHUNK = 30.0                     # whisper window
CACHE = Path(os.environ.get('ED_VOICE_CACHE') or Path(os.environ.get('ED_ROOT', 'C:/Claude Code/cinema-studio/edit')) / 'cache' / 'asr')
RELEASE = 'https://github.com/k2-fsa/sherpa-onnx/releases/download/asr-models/'

# alignment heads (layer, head) = openai-whisper _ALIGNMENT_HEADS (MIT), decoded from its base85 masks
MODELS = {
    'tiny':  dict(archive='sherpa-onnx-whisper-tiny.tar.bz2', dl_mb=116, disk_mb=100, ram_gb=0.4,
                  heads=[(2, 2), (3, 0), (3, 2), (3, 3), (3, 4), (3, 5)]),
    'base':  dict(archive='sherpa-onnx-whisper-base.tar.bz2', dl_mb=208, disk_mb=160, ram_gb=0.5,
                  heads=[(3, 1), (4, 2), (4, 3), (4, 7), (5, 1), (5, 2), (5, 4), (5, 6)]),
    'small': dict(archive='sherpa-onnx-whisper-small.tar.bz2', dl_mb=639, disk_mb=360, ram_gb=1.0,
                  heads=[(5, 3), (5, 9), (8, 0), (8, 4), (8, 7), (8, 8), (9, 0), (9, 7), (9, 9), (10, 5)]),
    'turbo': dict(archive='sherpa-onnx-whisper-turbo.tar.bz2', dl_mb=564, disk_mb=990, ram_gb=2.0,
                  heads=[(2, 4), (2, 11), (3, 3), (3, 6), (3, 11), (3, 14)]),
}
AUTO_CHAIN = ('turbo', 'small', 'base', 'tiny')
VAD_FILE = 'silero_vad.onnx'
# CTC forced aligner for word timing: Meta Omnilingual ASR CTC 300M (Apache-2.0), 1600+ languages, character
# vocabulary, 20 ms frames; exported to ONNX int8 by sherpa-onnx.
CTC = dict(dir='sherpa-onnx-omnilingual-asr-1600-languages-300M-ctc-int8-2025-11-12', dl_mb=293, disk_mb=366,
           ram_gb=1.0, files=('model.int8.onnx', 'tokens.txt'))
CTC['archive'] = CTC['dir'] + '.tar.bz2'

# Higgsfield `dubbing` target codes (ISO 639-3 style) <- whisper / ISO 639-1 codes
HF_DUB_LANG = {'en': 'eng', 'zh': 'cmn', 'fr': 'fra', 'hi': 'hin', 'it': 'ita', 'ja': 'jpn', 'ko': 'kor',
               'pt': 'por', 'ru': 'rus', 'tr': 'tur', 'es': 'spa', 'de': 'deu', 'ar': 'ara', 'pl': 'pol',
               'id': 'ind', 'tl': 'fil', 'fil': 'fil', 'sv': 'swe', 'fi': 'fin'}

# Reading speed (characters incl. spaces per second), max line length for 16:9 / 9:16, CJK flag, typical length of
# a translation relative to the English source (chars). Conservative values in the spirit of common broadcast and
# streaming subtitle guidelines; genre cards may override (clips: <= 20 cps, explainer: <= 17 cps).
LANG_RULES = {
    'en': dict(cps=17, line=42, line_v=20, expand=1.00), 'ru': dict(cps=15, line=42, line_v=20, expand=1.15),
    'uk': dict(cps=15, line=42, line_v=20, expand=1.15), 'de': dict(cps=15, line=42, line_v=20, expand=1.30),
    'fr': dict(cps=15, line=42, line_v=20, expand=1.20), 'es': dict(cps=17, line=42, line_v=20, expand=1.20),
    'it': dict(cps=17, line=42, line_v=20, expand=1.15), 'pt': dict(cps=17, line=42, line_v=20, expand=1.20),
    'pl': dict(cps=15, line=42, line_v=20, expand=1.20), 'tr': dict(cps=15, line=42, line_v=20, expand=1.10),
    'sv': dict(cps=15, line=42, line_v=20, expand=1.05), 'fi': dict(cps=14, line=42, line_v=20, expand=1.30),
    'id': dict(cps=17, line=42, line_v=20, expand=1.15), 'tl': dict(cps=15, line=42, line_v=20, expand=1.25),
    'ar': dict(cps=15, line=42, line_v=20, expand=1.10), 'hi': dict(cps=15, line=42, line_v=20, expand=1.10),
    'zh': dict(cps=9, line=16, line_v=12, expand=0.35, cjk=True),
    'ja': dict(cps=7, line=16, line_v=12, expand=0.45, cjk=True),
    'ko': dict(cps=12, line=16, line_v=12, expand=0.55, cjk=True),
}
NO_SPACE_LANGS = {'zh', 'ja', 'th', 'lo', 'my', 'yue'}

# fillers: 'sure' are cut by default, 'maybe' are reported for a decision (they are often meaningful)
# language data: Russian and English filler words
FILLERS = {
    'ru': dict(sure={'э', 'ээ', 'эээ', 'эм', 'эмм', 'мм', 'ммм', 'хм', 'хмм', 'а-а', 'э-э', 'м-м', 'угу', 'ага'},
               maybe={'ну', 'вот', 'типа', 'короче', 'значит', 'как бы', 'так сказать', 'это самое', 'в общем',
                      'собственно', 'блин', 'слушай', 'смотри', 'понимаешь', 'то есть', 'в принципе'}),
    'en': dict(sure={'uh', 'um', 'uhm', 'umm', 'erm', 'er', 'ah', 'eh', 'hmm', 'hm', 'mm', 'mhm', 'uh-huh'},
               maybe={'like', 'you know', 'i mean', 'sort of', 'kind of', 'basically', 'actually', 'literally',
                      'so', 'well', 'right', 'okay', 'ok'}),
}
# words that should not end a subtitle line or chunk (hanging prepositions / conjunctions / articles)
# language data: Russian and English function words
WEAK_END = {
    'ru': {'в', 'во', 'к', 'ко', 'с', 'со', 'у', 'о', 'об', 'обо', 'от', 'до', 'по', 'за', 'на', 'из', 'не', 'ни',
           'и', 'а', 'но', 'да', 'что', 'как', 'для', 'без', 'под', 'над', 'при', 'про', 'через', 'это', 'то', 'же',
           'ли'},
    'en': {'a', 'an', 'the', 'to', 'of', 'in', 'on', 'at', 'for', 'and', 'but', 'or', 'with', 'from', 'by', 'as',
           'that', 'my', 'your', 'his', 'her', 'our', 'their', 'its', 'is', 'are', 'was', 'were', 'be', 'not', "don't",
           'i', 'per', 'than', 'into', 'onto', 'via', 'about', 'over', 'under', 'this', 'these', 'those', 'some',
           'any', 'every', 'each', 'no', 'very', 'so', 'if', 'because', 'will', 'would', 'can', 'could', 'should',
           "it's", "i'm", "we're", "you're", "they're"},
}
# discourse fillers that may be hidden in captions when a chunk is too dense or holds nothing else (clean verbatim)
# language data: English and Russian multi-word fillers
FILLER_PHRASES = {'en': {"it's like", 'it is like', 'you know', 'i mean', 'kind of', 'sort of', 'like', 'you see'},
                  'ru': {'как бы', 'типа', 'ну', 'вот', 'короче', 'в общем', 'это самое', 'так сказать', 'значит'}}
SENT_END = '.!?…。！？'
# phrase structure for caption chunk and line breaks (language data: English). INTRO_WORDS introduce the word after
# them (articles, determiners, prepositions, conjunctions, relatives): nothing should end on one, and a break right
# before one is a natural phrase boundary. MODIFIERS (and words with MODIFIER_SUFFIXES) usually stand before a noun
# and stay with it ("various models"); NOT_NOUNS are words that never take that role. Other languages fall back to
# punctuation, pauses and WEAK_END.
INTRO_WORDS = {'en': {
    'a', 'an', 'the', 'this', 'that', 'these', 'those', 'my', 'your', 'his', 'her', 'its', 'our', 'their', 'some',
    'any', 'every', 'each', 'no', 'all', 'both', 'either', 'neither', 'another', 'such', 'what', 'which', 'whose',
    'who', 'whom', 'to', 'of', 'in', 'on', 'at', 'for', 'with', 'from', 'by', 'as', 'into', 'onto', 'via', 'about',
    'over', 'under', 'after', 'before', 'between', 'through', 'during', 'without', 'within', 'across', 'against',
    'among', 'around', 'behind', 'below', 'beneath', 'beside', 'besides', 'beyond', 'near', 'since', 'toward',
    'towards', 'until', 'upon', 'per', 'than', 'along', 'alongside', 'inside', 'outside', 'throughout', 'unlike',
    'except', 'versus', 'and', 'but', 'or', 'nor', 'yet', 'so', 'because', 'if', 'when', 'while', 'although',
    'though', 'unless', 'whether', 'where', 'once', 'whereas'}}
MODIFIERS = {'en': {
    'various', 'several', 'many', 'much', 'few', 'more', 'most', 'less', 'least', 'other', 'same', 'different',
    'certain', 'whole', 'entire', 'next', 'last', 'first', 'second', 'third', 'final', 'new', 'old', 'big', 'small',
    'large', 'little', 'great', 'good', 'bad', 'best', 'better', 'worse', 'worst', 'high', 'low', 'long', 'short',
    'huge', 'tiny', 'major', 'minor', 'main', 'real', 'true', 'full', 'top', 'key', 'young', 'early', 'late', 'free',
    'hard', 'easy', 'simple', 'important', 'average', 'total', 'own', 'only', 'extra', 'single', 'double', 'daily',
    'weekly', 'monthly', 'yearly', 'annual', 'special', 'specific', 'general', 'common', 'popular', 'current',
    'recent', 'previous', 'latest', 'massive', 'very', 'really', 'too', 'quite', 'pretty', 'super', 'extremely',
    'highly', 'fully', 'totally', 'completely'}}
MODIFIER_SUFFIXES = {'en': ('ous', 'ful', 'ive', 'ical', 'ic', 'able', 'ible', 'less', 'ish', 'ary', 'al')}


def _degrees(base):
    """big -> bigger, biggest; easy -> easier, easiest; large -> larger, largest; long -> longer, longest"""
    out = set()
    for b in base:
        if b.endswith('y'):
            stem = b[:-1] + 'i'
        elif b.endswith('e'):
            stem = b[:-1]
        elif len(b) <= 4 and b[-1] not in 'aeiouwy' and b[-2] in 'aeiou' and b[-3] not in 'aeiou':
            stem = b + b[-1]
        else:
            stem = b
        out |= {stem + 'er', stem + 'est'}
    return out


_ADJ_BASE = ('big small large long short high low new old young fast slow cheap strong hard easy great wide deep '
             'early late tall quick rich poor nice safe close clear bright dark hot cold warm cool heavy light fresh '
             'clean busy happy smart simple quiet narrow empty thin thick soft loud calm').split()
MODIFIERS['en'] |= set(_ADJ_BASE) | _degrees(_ADJ_BASE) | {
    'blue', 'red', 'green', 'black', 'white', 'yellow', 'grey', 'gray', 'brown', 'pink', 'purple', 'golden', 'open',
    'favorite', 'favourite', 'perfect', 'beautiful', 'tough', 'strange', 'weird', 'crazy', 'amazing', 'awesome'}
NOT_NOUNS = {'en': {
    'i', 'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him', 'us', 'them', 'is', 'are', 'was', 'were', 'be', 'been',
    'being', 'am', 'do', 'does', 'did', 'have', 'has', 'had', 'will', 'would', 'can', 'could', 'should', 'may',
    'might', 'must', 'shall', 'not', 'there', 'here', 'then', 'now', 'just', 'also', 'too', 'very', 'really',
    'yes', 'no', 'okay', 'ok', 'well', 'like', 'right'}}
SUBJECT_PRONOUNS = {'en': {'i', 'you', 'he', 'she', 'it', 'we', 'they'}}
# an amount: a scale word before its unit stays together ("4 million | dollars" costs like ed_text's split +1)
# language data: English and Russian scale words and units
SCALE_WORDS = set('thousand thousands million millions billion billions trillion trillions k m mln bn '
                  'тыс тысяч тысячи тысяча млн миллион миллиона миллионов млрд миллиард миллиарда миллиардов'.split())
SCALE_UNITS = set('dollars dollar bucks euros euro pounds rubles roubles yen percent % users people views '
                  'subscribers followers downloads customers employees years months days hours minutes km miles '
                  'рублей рубля рубль долларов доллара доллар евро процентов процента процент человек '
                  'пользователей просмотров подписчиков лет'.split())
# Conservative glyph widths in units of an average caption character (the ed_text.caption_hints average of its
# sample text), the widest of the caption preset fonts (Montserrat, Inter, Fira Sans Condensed) per glyph: the
# fallback line fit when ed_text.text_fits is missing. Mixed case / caps presets (measured on the upper-case sample).
_GLYPH_W = {
    'mixed': {0.5: ' ', 0.55: "!',.:;", 0.6: 'ij', 0.65: 'Il', 0.7: '()', 0.8: 'f', 0.85: 'rt', 0.9: '-', 0.95: 'г',
              1.0: '1', 1.05: '/зт', 1.1: '"*sxzь–', 1.15: '7?JLacvyГавсухэя', 1.2: 'Fehnuбеклпч',
              1.25: '235689Ebdgkopq£ЕЗийнор', 1.3: '#PTZБРТЬдъ', 1.35: '$+04=BRSВУЯц', 1.4: 'KYКЧ',
              1.45: 'ADUVXАХ€₽', 1.5: 'CGHNИЙЛНПСЭ', 1.55: 'OQОЦ', 1.6: '&м', 1.65: 'ДЪы…', 1.7: 'wжю', 1.75: 'шщ',
              1.8: 'Фф', 1.85: 'MmМЫ', 1.95: '%Ш', 2.0: 'Щ', 2.05: 'Ж—', 2.1: '@WЮ'},
    'caps': {0.45: ' ', 0.5: "!',.:;", 0.55: 'I', 0.65: '()', 0.8: '-', 0.9: '1', 0.95: '*/7JГ', 1.0: '"?FL–',
             1.05: '235E£ЕЗ', 1.1: '#+89=TZТ', 1.15: '$46BPRSБВРУЧЬЯ', 1.2: '0UVXYХ', 1.25: 'ACDGHKNИЙКЛНПСЭ€₽',
             1.3: 'OQАОЦ', 1.4: 'ДЪ', 1.45: '&', 1.5: '…', 1.55: 'MМ', 1.6: 'Ф', 1.65: 'ШЫ', 1.7: '%—',
             1.8: 'WЖЮ', 1.9: '@'}}
_GLYPH_TABLE = {k: {ch: w for w, chs in v.items() for ch in chs} for k, v in _GLYPH_W.items()}


def glyph_width(text, caps=False):
    """Conservative width of a caption line in average characters (_GLYPH_W; unknown glyphs 1.3)."""
    t = _GLYPH_TABLE['caps' if caps else 'mixed']
    return sum(t.get(ch, 1.3) for ch in (text.upper() if caps else text))


_GLYPH_CACHE = {}


def _preset_measure(pre):
    """(measure, capacity factor) of a caption preset: line width in the average characters of
    ed_text.caption_hints - per-glyph advances of the preset's font (ed_text.text_length, cached; against
    max_chars / 0.97, the capacity before caption_hints' 3 % margin), else the conservative built-in table
    (glyph_width, max_chars x 1.03)."""
    caps = bool(pre.get('caps'))
    font, tracking = pre.get('font'), float(pre.get('tracking') or 0.0)
    tl = sample = None
    try:
        import ed_text as Tx
        tl, sample = getattr(Tx, 'text_length', None), getattr(Tx, '_HINT_SAMPLE', None)
    except Exception:
        pass
    if callable(tl) and font and sample:
        try:
            cache = _GLYPH_CACHE.setdefault((font, caps, tracking), {})
            if None not in cache:
                smp = sample.upper() if caps else sample
                cache[None] = max(1e-6, float(tl(smp, font, 100.0, tracking)) / len(smp))

            def measure(text):
                w = 0.0
                for ch in (text.upper() if caps else text):
                    if ch not in cache:
                        cache[ch] = float(tl(ch, font, 100.0, tracking)) / cache[None]
                    w += cache[ch]
                return w
            measure('a')
            return measure, 1.0 / 0.97
        except Exception:
            pass
    return (lambda x: glyph_width(x, caps)), 1.03


def _scale_unit(a, b):
    """'million' + 'dollars': a scale word before its unit (one amount)."""
    return norm_word(a) in SCALE_WORDS and norm_word(b) in SCALE_UNITS and not _CLAUSE_RE.search(a) and \
        not _SENT_RE.search(a)
_SENT_RE = re.compile(r'[.!?…。！？]["»”)\']*$')
_CLAUSE_RE = re.compile(r'[,;:—–，、；：]["»”)\']*$')
PREPEND_PUNCT = "\"'“¿([{-«„‹"
APPEND_PUNCT = "\"'.。,，!！?？:：”)]}、»›…;"


# ----------------------------------------------------------------------------------------------- small utils
def _threads():
    try:
        return max(1, len(os.sched_getaffinity(0)))
    except AttributeError:
        return max(1, os.cpu_count() or 1)


def _mem_available_gb():
    """min(MemAvailable, memory-cgroup headroom) - sandboxes enforce the cgroup limit, not the host RAM."""
    avail = 8.0
    try:
        with open('/proc/meminfo') as f:
            for line in f:
                if line.startswith('MemAvailable:'):
                    avail = int(line.split()[1]) / 1048576.0
    except OSError:
        pass
    try:
        rel = ''
        with open('/proc/self/cgroup') as f:
            for line in f:
                parts = line.strip().split(':', 2)
                if parts[1] == 'memory' or (parts[0] == '0' and not rel):
                    rel = parts[2]
        for lim_f, use_f in (('memory.limit_in_bytes', 'memory.usage_in_bytes'), ('memory.max', 'memory.current')):
            for base in ('/sys/fs/cgroup/memory', '/sys/fs/cgroup'):
                lim_p, use_p = Path(base + rel) / lim_f, Path(base + rel) / use_f
                if lim_p.exists() and use_p.exists():
                    lim = lim_p.read_text().strip()
                    if lim.isdigit() and int(lim) < 1 << 60:
                        avail = min(avail, (int(lim) - int(use_p.read_text().strip())) / 1073741824.0)
                    return avail
    except (OSError, IndexError, ValueError):
        pass
    return avail


def _r(x, n=3):
    return None if x is None else round(float(x), n)


def _log(verbose, *a):
    if verbose:
        print('[ed_voice]', *a, file=sys.stderr, flush=True)


def norm_word(w):
    """lowercase, NFKC, Russian "yo" folded into "ye", strip punctuation at the edges (keeps inner
    hyphens/apostrophes)."""
    # language data: Russian (yo folded into ye)
    w = unicodedata.normalize('NFKC', w).lower().replace('ё', 'е').replace('’', "'")
    return w.strip(string.punctuation + '«»“”„‚‹›…—–‑ \t\n')


def _words_of(x):
    """accept a transcript dict, a list of word dicts or a list of chunk/layer dicts with 'words'."""
    if isinstance(x, dict):
        x = x.get('words', [])
    if x and isinstance(x[0], dict) and 'words' in x[0] and 'w' not in x[0]:
        return [w for c in x for w in c['words']]
    return list(x)


# ----------------------------------------------------------------------------------------------- downloads
def _download(url, dst):
    dst = Path(dst)
    dst.parent.mkdir(parents=True, exist_ok=True)
    tmp = dst.with_name(dst.name + '.part')
    if shutil.which('curl'):
        r = subprocess.run(['curl', '-sS', '-L', '--fail', '--retry', '5', '--retry-delay', '3', '-C', '-',
                            '-o', str(tmp), url], capture_output=True, text=True)
        if r.returncode != 0:
            raise RuntimeError(f'download failed ({r.returncode}): {url}: {r.stderr.strip()[:300]}')
    else:
        import urllib.request
        with urllib.request.urlopen(url, timeout=60) as resp, open(tmp, 'wb') as f:
            shutil.copyfileobj(resp, f, 1 << 20)
    os.replace(tmp, dst)
    return dst


def _safe_extract(tf, member, dest):
    if hasattr(tarfile, 'data_filter'):
        tf.extract(member, dest, filter='data')
        return
    target = (Path(dest) / member.name).resolve()
    if not str(target).startswith(str(Path(dest).resolve()) + os.sep) or not member.isfile():
        raise RuntimeError(f'unsafe archive member {member.name}')
    tf.extract(member, dest)


def model_dir(name):
    return CACHE / f'sherpa-onnx-whisper-{name}'


def ensure_model(name, download=True, verbose=False):
    """Download + extract the int8 Whisper ONNX model `name` into the cache; returns its directory."""
    if name not in MODELS:
        raise ValueError(f'unknown model {name!r}; one of {list(MODELS)}')
    d = model_dir(name)
    files = [d / f'{name}-encoder.int8.onnx', d / f'{name}-decoder.int8.onnx', d / f'{name}-tokens.txt']
    if all(f.exists() for f in files):
        return d
    if not download:
        raise FileNotFoundError(f'model {name} is not installed in {CACHE}')
    spec = MODELS[name]
    CACHE.mkdir(parents=True, exist_ok=True)
    free_mb = shutil.disk_usage(CACHE).free / 1e6
    if free_mb < spec['dl_mb'] + spec['disk_mb'] + 200:
        need = spec['dl_mb'] + spec['disk_mb']
        raise RuntimeError(f'not enough disk for {name}: need ~{need} MB, free {free_mb:.0f}')
    arc = CACHE / 'dl' / spec['archive']
    t = time.time()
    if not arc.exists():
        _log(verbose, f'downloading {spec["archive"]} ({spec["dl_mb"]} MB)')
        _download(RELEASE + spec['archive'], arc)
    _log(verbose, f'extracting int8 files ({time.time() - t:.0f}s so far)')
    with tarfile.open(arc, 'r|bz2') as tf:                    # stream: one pass over the bz2
        for m in tf:
            if m.isfile() and (m.name.endswith('.int8.onnx') or m.name.endswith('-tokens.txt')):
                _safe_extract(tf, m, CACHE)
    if not all(f.exists() for f in files):
        raise RuntimeError(f'archive {arc} did not contain the expected files')
    arc.unlink()
    _log(verbose, f'model {name} ready in {time.time() - t:.0f}s')
    return d


def ensure_ctc(download=True, verbose=False):
    d = CACHE / CTC['dir']
    if all((d / f).exists() for f in CTC['files']):
        return d
    if not download:
        raise FileNotFoundError(f'CTC aligner is not installed in {CACHE}')
    CACHE.mkdir(parents=True, exist_ok=True)
    if shutil.disk_usage(CACHE).free / 1e6 < CTC['dl_mb'] + CTC['disk_mb'] + 200:
        raise RuntimeError('not enough disk for the CTC aligner')
    arc = CACHE / 'dl' / CTC['archive']
    if not arc.exists():
        _log(verbose, f'downloading {CTC["archive"]} ({CTC["dl_mb"]} MB)')
        _download(RELEASE + CTC['archive'], arc)
    with tarfile.open(arc, 'r|bz2') as tf:
        for m in tf:
            if m.isfile() and m.name.rsplit('/', 1)[-1] in CTC['files'] + ('LICENSE',):
                _safe_extract(tf, m, CACHE)
    arc.unlink()
    return d


def ensure_vad(download=True):
    p = CACHE / VAD_FILE
    if not p.exists():
        if not download:
            raise FileNotFoundError(p)
        _download(RELEASE + VAD_FILE, p)
    return p


def installed_models():
    return [m for m in MODELS if all((model_dir(m) / f).exists() for f in
                                     (f'{m}-encoder.int8.onnx', f'{m}-decoder.int8.onnx', f'{m}-tokens.txt'))]


# ----------------------------------------------------------------------------------------------- audio
def load_audio(path, sr=SR, t0=None, dur=None):
    """mono float32 at `sr` via ffmpeg (any audio/video container)."""
    cmd = ['ffmpeg', '-v', 'error', '-nostdin']
    if t0:
        cmd += ['-ss', f'{t0:.3f}']
    cmd += ['-i', str(path)]
    if dur:
        cmd += ['-t', f'{dur:.3f}']
    cmd += ['-vn', '-ac', '1', '-ar', str(sr), '-f', 'f32le', '-']
    raw = subprocess.run(cmd, capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32).copy()


def file_hash(path, block=1 << 22):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(block), b''):
            h.update(chunk)
    return h.hexdigest()[:24]


# ----------------------------------------------------------------------------------------------- VAD
class SileroVAD:
    """Silero VAD v4 (16 kHz branch), 512-sample windows (32 ms)."""
    WIN = 512

    def __init__(self, path=None):
        import onnxruntime as ort
        so = ort.SessionOptions()
        so.intra_op_num_threads = 1
        so.inter_op_num_threads = 1
        so.log_severity_level = 3
        so.enable_cpu_mem_arena = False          # -35 % resident memory, same speed (measured)
        self.sess = ort.InferenceSession(str(path or ensure_vad()), so, providers=['CPUExecutionProvider'])

    def probs(self, audio):
        n = len(audio) // self.WIN
        x = np.ascontiguousarray(audio[:n * self.WIN].reshape(n, 1, self.WIN), np.float32)
        h = np.zeros((2, 1, 64), np.float32)
        c = np.zeros((2, 1, 64), np.float32)
        out = np.empty(n, np.float32)
        run = self.sess.run
        for i in range(n):
            p, h, c = run(None, {'x': x[i], 'h': h, 'c': c})
            out[i] = p[0, 0]
        return out


def energy_probs(audio, win=512):
    """VAD fallback: pseudo-probabilities from short-time energy relative to the noise floor."""
    n = len(audio) // win
    if n == 0:
        return np.zeros(0, np.float32)
    e = 10 * np.log10(np.mean(audio[:n * win].reshape(n, win) ** 2, axis=1) + 1e-10)
    floor = np.percentile(e, 10)
    peak = np.percentile(e, 99)
    thr = max(floor + 10.0, peak - 40.0)
    return (1.0 / (1.0 + np.exp(-(e - thr) / 2.0))).astype(np.float32)


def speech_regions(probs, hop=0.032, thr=0.5, neg=None, min_speech=0.2, min_silence=0.1, pad=0.0, dur=None):
    """silero-style hysteresis: [[t0, t1], ...] of speech."""
    neg = thr - 0.15 if neg is None else neg
    dur = len(probs) * hop if dur is None else dur
    regs, start, low = [], None, None
    for i, v in enumerate(probs):
        t = i * hop
        if v >= thr:
            low = None
            if start is None:
                start = t
        elif start is not None and v < neg:
            if low is None:
                low = t
            if t + hop - low >= min_silence:
                regs.append([start, low])
                start, low = None, None
    if start is not None:
        regs.append([start, len(probs) * hop])
    out = []
    for a, b in regs:
        if b - a < min_speech:
            continue
        a, b = max(0.0, a - pad), min(dur, b + pad)
        if out and a <= out[-1][1]:
            out[-1][1] = max(out[-1][1], b)
        else:
            out.append([a, b])
    return [[round(a, 3), round(b, 3)] for a, b in out]


def make_chunks(regions, probs, hop=0.032, max_len=28.0, pad=0.25, dur=None):
    """Group speech regions into Whisper windows <= max_len s (cut long speech at the quietest point)."""
    dur = dur if dur is not None else len(probs) * hop
    spans = []
    for a, b in regions:                                     # split over-long regions first
        a, b = max(0.0, a - pad), min(dur, b + pad)
        while b - a > max_len:
            lo, hi = int((a + 0.5 * max_len) / hop), int((a + max_len - 0.3) / hop)
            seg = probs[lo:hi]
            if len(seg) == 0:
                break
            sm = np.convolve(seg, np.ones(5) / 5, mode='same')
            cut = (lo + int(np.argmin(sm))) * hop
            spans.append([a, cut])
            a = cut
        spans.append([a, b])
    chunks = []
    for a, b in spans:
        if chunks and b - chunks[-1][0] <= max_len:
            chunks[-1][1] = max(chunks[-1][1], b)
        else:
            chunks.append([a, b])
    return [[round(a, 3), round(b, 3)] for a, b in chunks]


# ----------------------------------------------------------------------------------------------- onnx patch
def _varint(b, i):
    r = s = 0
    while True:
        x = b[i]
        i += 1
        r |= (x & 0x7F) << s
        if x < 0x80:
            return r, i
        s += 7


def _enc_varint(n):
    out = bytearray()
    while True:
        x, n = n & 0x7F, n >> 7
        out.append(x | 0x80 if n else x)
        if not n:
            return bytes(out)


def _pb_fields(b, i, end):
    while i < end:
        key, i = _varint(b, i)
        fn, wt = key >> 3, key & 7
        if wt == 0:
            v, j = _varint(b, i)
            yield fn, wt, i, j, key
            i = j
        elif wt == 1:
            yield fn, wt, i, i + 8, key
            i += 8
        elif wt == 2:
            ln, j = _varint(b, i)
            yield fn, wt, j, j + ln, key
            i = j + ln
        elif wt == 5:
            yield fn, wt, i, i + 4, key
            i += 4
        else:
            raise ValueError(f'protobuf wire type {wt}')


def expose_softmax(src, dst=None):
    """Add every Softmax output of an ONNX model as an extra graph output (raw protobuf edit: ModelProto.graph(7)
    gets GraphProto.output(12) entries appended). Weights and the rest of the file are copied byte for byte."""
    b = memoryview(Path(src).read_bytes())
    gspan = None
    for fn, wt, a, z, _key in _pb_fields(b, 0, len(b)):
        if fn == 7 and wt == 2:
            gspan = (a, z)
    if gspan is None:
        raise ValueError('no graph in model')
    names, have = [], set()
    for fn, wt, a, z, _ in _pb_fields(b, *gspan):
        if fn == 1 and wt == 2:                              # NodeProto: output(2), op_type(4)
            op, outs = None, []
            for f2, _w2, a2, z2, _ in _pb_fields(b, a, z):
                if f2 == 4:
                    op = bytes(b[a2:z2]).decode()
                elif f2 == 2:
                    outs.append(bytes(b[a2:z2]).decode())
            if op == 'Softmax' and outs:
                names.append(outs[0])
        elif fn == 12 and wt == 2:                           # existing outputs (ValueInfoProto.name = 1)
            for f2, _w2, a2, z2, _ in _pb_fields(b, a, z):
                if f2 == 1:
                    have.add(bytes(b[a2:z2]).decode())
    extra = bytearray()
    for n in names:
        if n in have:
            continue
        nb = n.encode()
        tensor = b'\x08\x01'                                 # TypeProto.Tensor.elem_type = FLOAT
        typ = b'\x0a' + _enc_varint(len(tensor)) + tensor
        vi = b'\x0a' + _enc_varint(len(nb)) + nb + b'\x12' + _enc_varint(len(typ)) + typ
        extra += b'\x62' + _enc_varint(len(vi)) + vi
    a, z = gspan
    i = 0                                                    # locate the graph field's key to rewrite its length
    while i < len(b):
        k0 = i
        key, i = _varint(b, i)
        fn, wt = key >> 3, key & 7
        if wt == 2:
            ln, j = _varint(b, i)
            if fn == 7:
                body = bytes(b[j:j + ln]) + bytes(extra)
                out = bytes(b[:k0]) + _enc_varint(key) + _enc_varint(len(body)) + body + bytes(b[j + ln:])
                break
            i = j + ln
        elif wt == 0:
            _, i = _varint(b, i)
        else:
            i += 8 if wt == 1 else 4
    del b
    if dst:
        tmp = Path(str(dst) + '.tmp')
        tmp.write_bytes(out)
        os.replace(tmp, dst)
    return names


# ----------------------------------------------------------------------------------------------- whisper
def _mel_filters(n_mels, sr=SR, n_fft=400):
    """librosa.filters.mel(sr, n_fft, n_mels) (slaney scale + norm) - what whisper's mel_filters.npz holds."""
    def hz2mel(f):
        f = np.asarray(f, np.float64)
        lin = f / (200.0 / 3)
        return np.where(f >= 1000.0, 15.0 + np.log(np.maximum(f, 1e-10) / 1000.0) / (np.log(6.4) / 27.0), lin)

    def mel2hz(m):
        m = np.asarray(m, np.float64)
        return np.where(m >= 15.0, 1000.0 * np.exp((np.log(6.4) / 27.0) * (m - 15.0)), m * (200.0 / 3))
    fft_f = np.linspace(0, sr / 2, 1 + n_fft // 2)
    mel_f = mel2hz(np.linspace(hz2mel(0.0), hz2mel(sr / 2), n_mels + 2))
    fdiff = np.diff(mel_f)
    ramps = mel_f[:, None] - fft_f[None, :]
    w = np.maximum(0, np.minimum(-ramps[:-2] / fdiff[:-1, None], ramps[2:] / fdiff[1:, None]))
    w *= (2.0 / (mel_f[2:n_mels + 2] - mel_f[:n_mels]))[:, None]
    return w.astype(np.float32)


_MEL_CACHE = {}


def log_mel(audio, n_mels, n_samples=int(CHUNK * SR)):
    """whisper.log_mel_spectrogram of `audio` zero-padded/trimmed to 30 s -> (1, n_mels, 3000) float32."""
    a = np.zeros(n_samples, np.float32)
    a[:min(len(audio), n_samples)] = audio[:n_samples]
    if n_mels not in _MEL_CACHE:
        hann = (0.5 - 0.5 * np.cos(2 * np.pi * np.arange(400) / 400)).astype(np.float32)   # torch periodic hann
        _MEL_CACHE[n_mels] = (_mel_filters(n_mels), hann)
    filt, win = _MEL_CACHE[n_mels]
    x = np.pad(a, (200, 200), mode='reflect')
    frames = np.lib.stride_tricks.sliding_window_view(x, 400)[::HOP][:-1]       # center=True, drop last frame
    spec = np.abs(np.fft.rfft(frames * win, axis=1)) ** 2
    mel = spec.astype(np.float32) @ filt.T
    lg = np.log10(np.maximum(mel, 1e-10))
    lg = np.maximum(lg, lg.max() - 8.0)
    return ((lg + 4.0) / 4.0).T[None].astype(np.float32)


def _median_filter(x, w):
    p = w // 2
    if x.shape[-1] <= p:
        return x
    xp = np.pad(x, [(0, 0)] * (x.ndim - 1) + [(p, p)], mode='reflect')
    return np.median(np.lib.stride_tricks.sliding_window_view(xp, w, axis=-1), axis=-1)


def dtw(x):
    """openai-whisper dtw_cpu (same tie-breaking), vectorised over anti-diagonals. -> (text_idx, time_idx)."""
    N, M = x.shape
    cost = np.full((N + 1, M + 1), np.inf)
    cost[0, 0] = 0.0
    trace = np.full((N + 1, M + 1), -1, np.int8)
    for d in range(2, N + M + 1):
        i = np.arange(max(1, d - M), min(N, d - 1) + 1)
        if len(i) == 0:
            continue
        j = d - i
        c0, c1, c2 = cost[i - 1, j - 1], cost[i - 1, j], cost[i, j - 1]
        t = np.where((c0 < c1) & (c0 < c2), 0, np.where((c1 < c0) & (c1 < c2), 1, 2))
        cost[i, j] = x[i - 1, j - 1] + np.choose(t, [c0, c1, c2])
        trace[i, j] = t
    trace[0, :] = 2
    trace[:, 0] = 1
    i, j, path = N, M, []
    while i > 0 or j > 0:
        path.append((i - 1, j - 1))
        t = trace[i, j]
        if t == 0:
            i, j = i - 1, j - 1
        elif t == 1:
            i -= 1
        else:
            j -= 1
    p = np.array(path[::-1]).T
    return p[0], p[1]


def _softmax(x, axis=-1):
    x = x - np.max(x, axis=axis, keepdims=True)
    e = np.exp(x)
    return e / np.sum(e, axis=axis, keepdims=True)


def _log_softmax(x):
    m = np.max(x)
    return x - m - np.log(np.sum(np.exp(x - m)))


def compression_ratio(text):
    b = text.encode('utf-8')
    return len(b) / max(1, len(zlib.compress(b)))


class Whisper:
    """Whisper int8 ONNX (sherpa-onnx export) with greedy decoding + temperature fallback and DTW word timing."""

    def __init__(self, name='turbo', threads=None, verbose=False):
        import onnxruntime as ort
        self.ort, self.name = ort, name
        d = ensure_model(name, verbose=verbose)
        so = ort.SessionOptions()
        so.intra_op_num_threads = threads or _threads()
        so.inter_op_num_threads = 1
        so.log_severity_level = 3
        so.enable_cpu_mem_arena = False          # -35 % resident memory, same speed (measured)
        self.enc = ort.InferenceSession(str(d / f'{name}-encoder.int8.onnx'), so, providers=['CPUExecutionProvider'])
        dec_path = d / f'{name}-decoder.int8.onnx'
        side = d / f'{name}-decoder.attn.json'
        if not side.exists():                     # one-time in-place patch: expose attention softmax outputs
            _log(verbose, 'patching decoder to expose cross-attention')
            expose_softmax(dec_path, dec_path)
        self.dec = ort.InferenceSession(str(dec_path), so, providers=['CPUExecutionProvider'])
        meta = self.enc.get_modelmeta().custom_metadata_map
        g = lambda k: int(meta[k])  # noqa: E731
        self.n_mels, self.n_layer, self.n_ctx = g('n_mels'), g('n_text_layer'), g('n_text_ctx')
        self.n_state, self.n_vocab = g('n_text_state'), g('n_vocab')
        self.sot, self.eot, self.no_speech, self.no_ts = g('sot'), g('eot'), g('no_speech'), g('no_timestamps')
        self.tok_transcribe, self.tok_translate, self.sot_prev = g('transcribe'), g('translate'), g('sot_prev')
        self.blank = g('blank_id')
        codes = meta['all_language_codes'].split(',')
        self.lang_tok = dict(zip(codes, map(int, meta['all_language_tokens'].split(','))))
        self.tok_lang = {v: k for k, v in self.lang_tok.items()}
        self.multilingual = g('is_multilingual') == 1
        self.vocab = []
        with open(d / f'{name}-tokens.txt', encoding='utf-8') as f:
            for line in f:
                t, i = line.split()
                assert int(i) == len(self.vocab)
                self.vocab.append(base64.b64decode(t))
        self.ranks = {b: i for i, b in enumerate(self.vocab)}
        sup = np.zeros(self.n_vocab, bool)
        sup[[int(x) for x in meta['non_speech_tokens'].split(',')]] = True
        sup[self.eot + 1:] = True                 # all specials except <|endoftext|>: no timestamps, no tags
        self.suppress = sup
        if side.exists():
            self.cross = json.loads(side.read_text())['cross']
        else:
            self.cross = self._probe_cross()
            side.write_text(json.dumps({'cross': self.cross}))
        self.heads = MODELS[name]['heads']

    # -- graph plumbing
    def _probe_cross(self):
        names = [o.name for o in self.dec.get_outputs()[3:]]
        T = 8
        k = np.zeros((self.n_layer, 1, T, self.n_state), np.float32)
        res = self.dec.run(names, self._feeds(np.array([[self.sot]], np.int64), 0, k, k, *self._zeros()))
        cross = [n for n, r in zip(names, res) if r.shape[-1] == T]
        if len(cross) != self.n_layer:
            raise RuntimeError(f'cross-attention probe found {len(cross)} tensors for {self.n_layer} layers')
        return cross

    def _zeros(self):
        z = np.zeros((self.n_layer, 1, self.n_ctx, self.n_state), np.float32)
        return z, z.copy()

    @staticmethod
    def _feeds(tokens, offset, k, v, kc, vc):
        return {'tokens': tokens, 'in_n_layer_self_k_cache': kc, 'in_n_layer_self_v_cache': vc,
                'n_layer_cross_k': k, 'n_layer_cross_v': v, 'offset': np.array([offset], np.int64)}

    def encode(self, mel):
        return self.enc.run(None, {'mel': mel})

    # -- text
    def decode_bytes(self, tokens):
        out = bytearray()
        for t in tokens:
            if t < len(self.vocab):
                out += self.vocab[t]
            elif t == self.eot:
                out += b'<|endoftext|>'
        return bytes(out)

    def text(self, tokens):
        return self.decode_bytes([t for t in tokens if t < self.eot]).decode('utf-8', errors='replace')

    _PRE = re.compile(r"""'s|'t|'re|'ve|'m|'ll|'d| ?[^\W\d_]+| ?\d+| ?(?:[^\s\w]|_)+|\s+(?!\S)|\s+""")

    def encode_text(self, text):
        """byte-level BPE (tiktoken-compatible merge order by rank) for prompts and forced alignment."""
        ids = []
        for piece in self._PRE.findall(text):
            parts = [bytes([c]) for c in piece.encode('utf-8')]
            while len(parts) > 1:
                best, bi = None, -1
                for i in range(len(parts) - 1):
                    r = self.ranks.get(parts[i] + parts[i + 1])
                    if r is not None and (best is None or r < best):
                        best, bi = r, i
                if best is None:
                    break
                parts[bi:bi + 2] = [parts[bi] + parts[bi + 1]]
            ids.extend(self.ranks[p] for p in parts)
        return ids

    def split_words(self, tokens, lang):
        """openai-whisper split_tokens_on_unicode / split_tokens_on_spaces."""
        full = self.decode_bytes(tokens).decode('utf-8', errors='replace')
        subs, subt, cur, uoff = [], [], [], 0
        for t in tokens:
            cur.append(t)
            dec = self.decode_bytes(cur).decode('utf-8', errors='replace')
            if '�' not in dec or full[uoff + dec.index('�')] == '�':
                subs.append(dec)
                subt.append(cur)
                cur = []
                uoff += len(dec)
        if lang in NO_SPACE_LANGS:
            return subs, subt
        words, wt = [], []
        for sw, st in zip(subs, subt):
            if st[0] >= self.eot or sw.startswith(' ') or sw.strip() in string.punctuation or not words:
                words.append(sw)
                wt.append(list(st))
            else:
                words[-1] += sw
                wt[-1].extend(st)
        return words, wt

    # -- decoding
    def detect_language(self, k, v):
        kc, vc = self._zeros()
        logits = self.dec.run(['logits'], self._feeds(np.array([[self.sot]], np.int64), 0, k, v, kc, vc))[0][0, -1]
        ids = np.array(list(self.lang_tok.values()))
        p = _softmax(logits[ids])
        return {self.tok_lang[int(i)]: float(x) for i, x in zip(ids, p)}

    def decode(self, k, v, lang, task='transcribe', prompt=(), temperature=0.0, max_len=None, rng=None):
        max_len = max_len or self.n_ctx // 2
        init = []
        if prompt:
            init = [self.sot_prev] + list(prompt)[-(self.n_ctx // 2 - 1):]
        sot_i = len(init)
        init += [self.sot, self.lang_tok.get(lang, self.lang_tok.get('en')),
                 self.tok_translate if task == 'translate' else self.tok_transcribe, self.no_ts]
        ort = self.ort
        kv, vv = ort.OrtValue.ortvalue_from_numpy(k), ort.OrtValue.ortvalue_from_numpy(v)
        bufs = [[ort.OrtValue.ortvalue_from_numpy(z) for z in self._zeros()] for _ in range(2)]
        io = self.dec.io_binding()
        io.bind_ortvalue_input('n_layer_cross_k', kv)
        io.bind_ortvalue_input('n_layer_cross_v', vv)
        cur = [0]

        def step(toks, offset):
            io.clear_binding_outputs()
            io.bind_cpu_input('tokens', np.array([toks], np.int64))
            io.bind_cpu_input('offset', np.array([offset], np.int64))
            io.bind_ortvalue_input('in_n_layer_self_k_cache', bufs[cur[0]][0])
            io.bind_ortvalue_input('in_n_layer_self_v_cache', bufs[cur[0]][1])
            io.bind_output('logits')                     # output 0 (outputs come back in binding order)
            io.bind_ortvalue_output('out_n_layer_self_k_cache', bufs[1 - cur[0]][0])
            io.bind_ortvalue_output('out_n_layer_self_v_cache', bufs[1 - cur[0]][1])
            self.dec.run_with_iobinding(io)
            cur[0] = 1 - cur[0]
            return io.get_outputs()[0].numpy()[0]

        logits = step(init, 0)
        no_speech_prob = float(_softmax(logits[sot_i])[self.no_speech])
        last, offset = logits[-1], len(init)
        tokens, sum_lp, loop = [], 0.0, False
        for i in range(max_len):
            lg = last.astype(np.float64)
            lg[self.suppress] = -np.inf
            if i == 0:
                lg[self.eot] = -np.inf
                lg[self.blank] = -np.inf
            if temperature > 0:
                p = _softmax(lg / temperature)
                tok = int((rng or np.random.default_rng(0)).choice(len(p), p=p))
            else:
                tok = int(np.argmax(lg))
            sum_lp += float(_log_softmax(lg)[tok])
            if tok == self.eot:
                break
            tokens.append(tok)
            if offset + 1 >= self.n_ctx:
                break
            if len(tokens) >= 48 and len(tokens) % 16 == 0 and compression_ratio(self.text(tokens)) > 3.0:
                loop = True                              # repetition loop: stop early, the caller falls back
                break
            last = step([tok], offset)[-1]
            offset += 1
        text = self.text(tokens)
        return dict(tokens=tokens, text=text, avg_logprob=sum_lp / (len(tokens) + 1), no_speech_prob=no_speech_prob,
                    compression_ratio=99.0 if loop else compression_ratio(text), temperature=temperature)

    def align(self, k, v, lang, text_tokens, n_frames, task='transcribe', medfilt=7):
        """openai-whisper find_alignment: -> [(word, tokens, t0, t1, prob)] relative to the window start."""
        if not text_tokens:
            return []
        task_tok = self.tok_translate if task == 'translate' else self.tok_transcribe
        sot_seq = [self.sot, self.lang_tok.get(lang, self.lang_tok.get('en')), task_tok]
        toks = sot_seq + [self.no_ts] + list(text_tokens) + [self.eot]
        if len(toks) > self.n_ctx:
            raise ValueError('too many tokens for one window')
        layers = sorted({l for l, _ in self.heads})
        names = ['logits'] + [self.cross[l] for l in layers]
        kc, vc = self._zeros()
        res = self.dec.run(names, self._feeds(np.array([toks], np.int64), 0, k, v, kc, vc))
        logits = res[0][0]
        att = dict(zip(layers, res[1:]))
        probs = _softmax(logits[len(sot_seq):len(sot_seq) + len(text_tokens), :self.eot].astype(np.float64))
        tok_p = probs[np.arange(len(text_tokens)), text_tokens]
        W = np.stack([att[l][0, h] for l, h in self.heads]).astype(np.float64)    # heads x tokens x 1500
        W = W[:, :, :max(1, n_frames // 2)]
        W = W / np.maximum(W.sum(-1, keepdims=True), 1e-12)
        W = (W - W.mean(-2, keepdims=True)) / np.maximum(W.std(-2, keepdims=True), 1e-9)
        W = _median_filter(W, medfilt)
        M = W.mean(0)[len(sot_seq):-1]
        ti, tj = dtw(-M)
        words, wtoks = self.split_words(list(text_tokens) + [self.eot], lang)
        if len(wtoks) <= 1:
            return []
        bounds = np.pad(np.cumsum([len(t) for t in wtoks[:-1]]), (1, 0))
        jumps = np.pad(np.diff(ti), (1, 0), constant_values=1).astype(bool)
        jt = tj[jumps] / 50.0
        out = []
        for w, t, a, b in zip(words[:-1], wtoks[:-1], bounds[:-1], bounds[1:]):
            out.append([w, t, float(jt[a]), float(jt[b]), float(np.mean(tok_p[a:b]))])
        return out


_LOADED = {}


def _unload_whisper(verbose=False):
    if _LOADED:
        import gc
        _log(verbose, 'unloading whisper to make room for the aligner')
        _LOADED.clear()
        gc.collect()


def get_model(name='auto', threads=None, verbose=False):
    """load (and cache in-process) a Whisper model; 'auto' walks AUTO_CHAIN and returns the first that loads."""
    chain = AUTO_CHAIN if name == 'auto' else (name,)
    if name == 'auto' and os.environ.get('ED_VOICE_MODEL') in MODELS:
        chain = (os.environ['ED_VOICE_MODEL'],) + AUTO_CHAIN
    errors = []
    for m in chain:
        if m in _LOADED:
            return _LOADED[m]
        if _CTC and _mem_available_gb() < MODELS[m]['ram_gb'] + 0.3:
            import gc
            _CTC.clear()                                 # free the aligner before (re)loading whisper
            gc.collect()
        if name == 'auto' and _mem_available_gb() < MODELS[m]['ram_gb'] and m != chain[-1]:
            errors.append(f'{m}: not enough RAM ({_mem_available_gb():.1f} GB available)')
            continue
        try:
            _LOADED[m] = Whisper(m, threads=threads, verbose=verbose)
            return _LOADED[m]
        except Exception as e:                       # download blocked, disk full, corrupt file ... -> next
            errors.append(f'{m}: {type(e).__name__}: {e}')
            _log(verbose, errors[-1])
    raise RuntimeError('no ASR model could be loaded: ' + ' | '.join(errors))


class CTCAligner:
    """Forced alignment of known words with the omnilingual CTC character model (20 ms frames).
    Words without alignable letters (digits, symbols) become a penalised wildcard state; the word separator is
    optional, so missing pauses between words cost nothing."""
    FRAME = 0.02
    WILD = -1
    WILD_PENALTY = 0.7                                   # nats per frame, keeps the wildcard from eating neighbours

    def __init__(self, threads=None, verbose=False):
        import onnxruntime as ort
        d = ensure_ctc(verbose=verbose)
        so = ort.SessionOptions()
        so.intra_op_num_threads = threads or _threads()
        so.inter_op_num_threads = 1
        so.log_severity_level = 3
        so.enable_cpu_mem_arena = False          # -35 % resident memory, same speed (measured)
        self.sess = ort.InferenceSession(str(d / 'model.int8.onnx'), so, providers=['CPUExecutionProvider'])
        self.char = {}
        with open(d / 'tokens.txt', encoding='utf-8') as f:
            for line in f:
                line = line.rstrip('\n')
                if line:
                    tok, i = line.rsplit(' ', 1)
                    if len(tok) == 1:
                        self.char[tok] = int(i)
        self.blank, self.space = 0, self.char.get(' ')

    def logprobs(self, audio):
        x = audio.astype(np.float32)
        x = (x - x.mean()) / np.sqrt(x.var() + 1e-5)
        lg = self.sess.run(None, {'x': x[None]})[0][0].astype(np.float32)
        m = lg.max(1, keepdims=True)
        return lg - m - np.log(np.exp(lg - m).sum(1, keepdims=True))

    def ids(self, word):
        s = unicodedata.normalize('NFKC', word).lower().replace('’', "'").replace('ʼ', "'")
        if any(c.isdigit() for c in s):
            return None
        keep = [c for c in s if unicodedata.category(c)[0] in 'LM' or c in "'-"]
        while keep and keep[0] in "'-":
            keep.pop(0)
        while keep and keep[-1] in "'-":
            keep.pop()
        out = [self.char[c] for c in keep if c in self.char]
        return out or None

    def _viterbi(self, lp, labels):
        T, L = lp.shape[0], len(labels)
        S = 2 * L + 1
        NEG = np.float32(-1e30)
        lab = np.array(labels)
        em = np.empty((T, S), np.float32)
        em[:, 0::2] = lp[:, [self.blank]]
        em[:, 1::2] = lp[:, np.where(lab >= 0, lab, 0)]
        if (lab < 0).any():
            wild = lp[:, 1:].max(1) - self.WILD_PENALTY
            wild = np.maximum(wild, lp[:, self.blank] - self.WILD_PENALTY)
            em[:, 1::2][:, lab < 0] = wild[:, None]
        allow = np.zeros((5, S), bool)
        allow[0] = allow[1] = True
        for k in range(1, L):
            s = 2 * k + 1
            allow[2, s] = labels[k] != labels[k - 1] or labels[k] == self.WILD
            if k >= 2 and labels[k - 1] == self.space and labels[k] != self.space:   # optional separator
                allow[3, s] = True
                allow[4, s] = labels[k] != labels[k - 2]
        dp = np.full(S, NEG, np.float32)
        dp[0] = em[0, 0]
        if S > 1:
            dp[1] = em[0, 1]
        bp = np.zeros((T, S), np.int8)
        cand = np.full((5, S), NEG, np.float32)
        cols = np.arange(S)
        for t in range(1, T):
            cand[0] = dp
            for k in range(1, 5):
                cand[k, :k] = NEG
                cand[k, k:] = dp[:-k]
                cand[k, ~allow[k]] = NEG
            arg = cand.argmax(0)
            dp = cand[arg, cols] + em[t]
            bp[t] = arg
        s = S - 1 if S == 1 or dp[S - 1] >= dp[S - 2] else S - 2
        score = float(dp[s]) / T
        path = np.empty(T, np.int32)
        for t in range(T - 1, -1, -1):
            path[t] = s
            s -= int(bp[t, s])
        return path, score, em

    def greedy(self, lp):
        """best-path decoding -> [(text, first_frame, last_frame, mean_prob)] words split at the separator."""
        ids = lp.argmax(1)
        words, cur, prev = [], [], -1
        inv = getattr(self, '_inv', None) or {v: k for k, v in self.char.items()}
        self._inv = inv
        for t, i in enumerate(ids):
            if i != prev and i != self.blank:
                if i == self.space:
                    if cur:
                        words.append(cur)
                    cur = []
                else:
                    cur.append((inv.get(int(i), ''), t))
            prev = i
        if cur:
            words.append(cur)
        out = []
        for w in words:
            f0, f1 = w[0][1], w[-1][1]
            out.append((''.join(c for c, _ in w), f0, f1, float(np.exp(lp[f0:f1 + 1].max(1)).mean())))
        return out

    def align(self, audio, words, lp=None):
        """words: list of strings -> (list of (t0, t1, p) relative to the audio start, info) where info has the
        path score, how many letters the model hears on its own (greedy) and how many the text has."""
        labels, spans = [], []
        for w in words:
            if labels and self.space is not None:
                labels.append(self.space)
            ids = self.ids(w)
            a = len(labels)
            labels.extend(ids if ids else [self.WILD])
            spans.append((a, len(labels) - 1))
        lp = self.logprobs(audio) if lp is None else lp
        if not labels or lp.shape[0] < len(labels):
            return None, None
        heard = self.greedy(lp)
        info = dict(heard=sum(len(h[0]) for h in heard),
                    expected=sum(1 for x in labels if x not in (self.space, self.WILD)),
                    greedy=' '.join(h[0] for h in heard))
        path, score, em = self._viterbi(lp, labels)
        info['score'] = round(score, 3)
        lab_of = np.where(path % 2 == 1, (path - 1) // 2, -1)
        out = []
        for a, b in spans:
            fr = np.where((lab_of >= a) & (lab_of <= b))[0]
            if len(fr) == 0:
                out.append(None)
                continue
            p = float(np.exp(np.mean(em[fr, path[fr]])))
            out.append((float(fr[0]) * self.FRAME, float(fr[-1] + 1) * self.FRAME, p))
        return out, info


_CTC = []


def get_ctc(threads=None, verbose=False):
    if not _CTC:
        _CTC.append(CTCAligner(threads=threads, verbose=verbose))
    return _CTC[0]


# ----------------------------------------------------------------------------------------------- transcription
def _merge_punct(al):
    """openai-whisper merge_punctuations + our rule: symbol-only 'words' are glued to a neighbour."""
    i, j = len(al) - 2, len(al) - 1
    while i >= 0:
        prev, nxt = al[i], al[j]
        if prev[0].startswith(' ') and prev[0].strip() in PREPEND_PUNCT and prev[0].strip():
            nxt[0], nxt[1], prev[0], prev[1] = prev[0] + nxt[0], prev[1] + nxt[1], '', []
        else:
            j = i
        i -= 1
    i, j = 0, 1
    while j < len(al):
        prev, nxt = al[i], al[j]
        if not prev[0].endswith(' ') and nxt[0] in APPEND_PUNCT and nxt[0]:
            prev[0], prev[1], nxt[0], nxt[1] = prev[0] + nxt[0], prev[1] + nxt[1], '', []
        else:
            i = j
        j += 1
    out = []
    for a in al:
        if not a[0].strip():
            continue
        if not any(ch.isalnum() for ch in a[0]):             # dashes, quotes, ellipses on their own
            if out:
                out[-1][0] = out[-1][0].rstrip() + ' ' + a[0].strip()
                continue
        out.append(a)
    return out


def _fix_durations(al):
    """openai-whisper hack: words at sentence boundaries are not longer than 2x the median word duration."""
    d = np.array([a[3] - a[2] for a in al])
    d = d[d > 0]
    med = min(0.7, float(np.median(d))) if len(d) else 0.0
    mx = med * 2
    if len(d):
        for i in range(1, len(al)):
            if al[i][3] - al[i][2] > mx:
                if al[i][0].strip() in SENT_END:
                    al[i][3] = al[i][2] + mx
                elif al[i - 1][0].strip() and al[i - 1][0].strip()[-1] in SENT_END:
                    al[i][2] = al[i][3] - mx
    return med


def _trim_to_speech(words, fine, tol=0.04):
    """move word edges that sit in VAD silence onto the nearest speech edge (keeps order, min 40 ms)."""
    if not fine:
        return words
    starts = np.array([a for a, _ in fine])
    ends = np.array([b for _, b in fine])

    def region(t):
        i = int(np.searchsorted(starts, t, side='right')) - 1
        return i
    for w in words:
        i = region(w['t0'])
        if i < 0 or w['t0'] > ends[i] + tol:             # start lies in silence -> next speech onset
            nxt = i + 1
            if nxt < len(starts) and starts[nxt] < w['t1']:
                w['t0'] = float(starts[nxt])
        i = region(w['t1'])
        if i >= 0 and w['t1'] > ends[i] + tol and ends[i] > w['t0']:   # end lies in silence -> speech offset
            w['t1'] = float(ends[i])
        if w['t1'] - w['t0'] < 0.04:
            w['t1'] = w['t0'] + 0.04
    for a, b in zip(words, words[1:]):
        if b['t0'] < a['t1']:
            mid = max(a['t0'] + 0.02, min(b['t0'], a['t1']))
            a['t1'] = mid
            b['t0'] = max(b['t0'], mid)
            if b['t1'] < b['t0'] + 0.02:
                b['t1'] = b['t0'] + 0.02
    return words


def make_segments(words, max_dur=12.0, pause=0.9):
    segs, cur = [], []
    for i, w in enumerate(words):
        if cur and (w['t0'] - words[i - 1]['t1'] > pause or w['t1'] - words[cur[0]]['t0'] > max_dur):
            segs.append(cur)
            cur = []
        cur.append(i)
        if w['w'] and w['w'].rstrip('"\'»”)')[-1:] in SENT_END:
            segs.append(cur)
            cur = []
    if cur:
        segs.append(cur)
    out = []
    for s in segs:
        out.append(dict(t0=words[s[0]]['t0'], t1=words[s[-1]]['t1'], w0=s[0], w1=s[-1] + 1,
                        text=join_words([words[i]['w'] for i in s])))
    return out


def join_words(ws, lang=None):
    if lang in NO_SPACE_LANGS:
        return ''.join(w.strip() for w in ws)
    return ' '.join(w.strip() for w in ws if w.strip())


def _vad(audio, verbose=False):
    try:
        probs, kind = SileroVAD().probs(audio), 'silero'
    except Exception as e:                                   # no model / no onnxruntime -> energy detector
        _log(verbose, f'silero VAD unavailable ({e}); using energy VAD')
        probs, kind = energy_probs(audio), 'energy'
    return probs, kind


def transcribe(path, lang=None, model='auto', *, prompt=None, text=None, srt=None, task='transcribe',
               timing='auto', cache=True, threads=None, max_chunk=28.0, verbose=False):
    """Speech -> words with timestamps. See module docstring for the result format.
    lang: 'ru', 'en', ... or None (detected on speech). model: 'auto'|'turbo'|'small'|'base'|'tiny'.
    prompt: vocabulary hint (names, brands, spelling style). text: known script/lyrics -> forced alignment.
    srt: path or SRT text -> cue timing (refined by the audio when a model is available).
    timing: 'auto' (CTC aligner when available, else whisper DTW) | 'ctc' | 'dtw'."""
    path = str(path)
    t_start = time.time()
    if srt is not None and text is None:
        cues = from_srt(srt)
        text = '\n'.join(c['text'] for c in cues)
    else:
        cues = None
    h = file_hash(path)
    opt = json.dumps([VERSION, model, lang, prompt, text, task, max_chunk, timing], ensure_ascii=False)
    key = f'{h}-{hashlib.sha256(opt.encode()).hexdigest()[:12]}'
    cfile = CACHE / 'transcripts' / f'{key}.json'
    if cache and cfile.exists():
        res = json.loads(cfile.read_text())
        res['stats']['cached'] = True
        return res
    audio = load_audio(path)
    dur = len(audio) / SR
    probs, vad_kind = _vad(audio, verbose)
    fine = speech_regions(probs, min_speech=0.08, min_silence=0.06, dur=dur)
    regions = speech_regions(probs, min_speech=0.2, min_silence=0.3, pad=0.0, dur=dur)
    chunks = make_chunks(regions, probs, max_len=max_chunk, dur=dur)
    _log(verbose, f'{dur:.1f}s audio, {sum(b - a for a, b in regions):.1f}s speech, {len(chunks)} chunks '
                  f'({vad_kind} VAD)')
    res = dict(version=VERSION, src=os.path.abspath(path), hash=h, duration=round(dur, 3), lang=lang, lang_prob=None,
               model=None, source='asr', timing=None, words=[], segments=[], speech=fine, vad=vad_kind, stats={})
    try:
        wm = None if model == 'omni' else get_model(model, threads=threads, verbose=verbose)
    except RuntimeError as e:
        if text is None:
            raise RuntimeError(f'{e}. Fallback: pass text= (script) or srt= (subtitles) to transcribe().') from None
        wm = None
        _log(verbose, f'no ASR model ({e}); spreading the provided text over the speech regions')
    if model == 'omni' and text is None:
        words, meta = _recognize_omni(get_ctc(threads=threads, verbose=verbose), audio, chunks, fine, verbose)
        res.update(words=words, model='omnilingual-ctc-300m-int8', chunks=meta, timing='ctc')
    elif wm is None:
        words = cue_words(cues) if cues else spread_text(text, regions or [[0.0, dur]])
        res.update(source='srt' if cues else 'text', words=words, model=None)
    else:
        res['model'] = f'whisper-{wm.name}-int8'
        if text is not None:
            words, lang, lp = _forced(wm, audio, chunks, text, lang, cues, fine, verbose, timing, threads)
            res.update(source='srt' if cues else 'text', words=words, lang=lang, lang_prob=lp)
        else:
            words, lang, lp, seg_meta = _recognize(wm, audio, chunks, lang, prompt, task, fine, verbose,
                                                   timing, threads)
            res.update(words=words, lang=lang, lang_prob=lp)
            res['chunks'] = seg_meta
        res['timing'] = 'ctc' if any(w.get('pa') is not None for w in res['words']) else 'dtw'
    res['segments'] = make_segments(res['words'])
    res['warnings'] = _warnings(res)
    took = time.time() - t_start
    sp = sum(b - a for a, b in regions)
    res['stats'] = dict(seconds=round(took, 1), rtf=round(took / max(dur, 1e-6), 3), speech_s=round(sp, 1),
                        words=len(res['words']), wps=round(len(res['words']) / max(sp, 1e-6), 2), cached=False)
    if cache:
        cfile.parent.mkdir(parents=True, exist_ok=True)
        cfile.write_text(json.dumps(res, ensure_ascii=False))
    return res


def _detect(wm, audio, chunks, encoded, verbose):
    """language from up to the first 3 chunks (>= 6 s of speech when available); encodings are reused."""
    agg, sp = {}, 0.0
    for ci, (a, b) in enumerate(chunks[:3]):
        if ci not in encoded:
            encoded[ci] = wm.encode(log_mel(audio[int(a * SR):int(b * SR)], wm.n_mels))
        p = wm.detect_language(*encoded[ci])
        for k_, v_ in p.items():
            agg[k_] = agg.get(k_, 0.0) + v_ * (b - a)
        sp += b - a
        if sp >= 6.0:
            break
    tot = sum(agg.values()) or 1.0
    lang = max(agg, key=agg.get) if agg else 'en'
    _log(verbose, f'language {lang} ({agg.get(lang, 0) / tot:.2f})')
    return lang, round(agg.get(lang, 0) / tot, 3)


CTC_ONSET_SHIFT = 0.02          # CTC spikes trail the acoustic onset by ~1 frame (measured +16..+38 ms)


def _letters(s):
    # language data: Russian (yo folded into ye)
    return ''.join(c for c in unicodedata.normalize('NFKC', s).lower().replace('ё', 'е')
                   if unicodedata.category(c)[0] in 'LM')


def _ctc_refine(ctc, audio, a, b, cw, m):
    """Replace DTW word times of one chunk by CTC forced-alignment times (in place) when the aligner actually
    hears the speech: it must decode >= 35 % of the letters on its own (voice under loud music -> it hears ~0,
    keep DTW). If it hears speech but its letters disagree with low-confidence Whisper text (unsupported language,
    hallucination on sobs/whispers), the chunk's words are flagged suspect and the CTC reading is kept in m."""
    if not cw:
        return False
    seg = audio[int(a * SR):int(b * SR)]
    res, info = ctc.align(seg, [w['w'] for w in cw])
    if res is None:
        return False
    sim = difflib.SequenceMatcher(None, _letters(info['greedy']), _letters(' '.join(w['w'] for w in cw)),
                                  autojunk=False).ratio()
    heard = info['heard'] / max(1, info['expected'])
    m['ctc'] = dict(heard=round(heard, 2), agree=round(sim, 2))
    if heard >= 0.35 and sim < 0.35 and (m.get('avg_logprob') or 0) < -0.4:
        m['suspect'] = True
        m['ctc_text'] = info['greedy']
        for w in cw:
            w['suspect'] = True
    d = np.array([abs(a + r[0] - CTC_ONSET_SHIFT - w['t0']) for w, r in zip(cw, res) if r is not None])
    agree = len(d) > 0 and np.median(d) <= 0.12 and np.percentile(d, 90) <= 0.25
    m['ctc']['dtw_diff'] = round(float(np.median(d)), 3) if len(d) else None
    if heard < 0.35 and not agree:                       # the aligner cannot hear it and disagrees: keep DTW
        return False
    for w, r in zip(cw, res):
        if r is not None:
            w['t0'], w['t1'], w['pa'] = max(a, a + r[0] - CTC_ONSET_SHIFT), a + r[1], round(r[2], 3)
    _refine_edges(cw, seg, a)
    return True


def _refine_edges(cw, seg, a, step=0.005, max_ext=0.3, max_back=0.12):
    """CTC spans end at the last character spike, before the sound decays: extend each word end while the
    short-time energy stays above the word's level - 30 dB (bounded by the next word); words after a pause get
    their onset moved back to the energy rise (<= 120 ms)."""
    hop = int(step * SR)
    n = len(seg) // hop
    if n < 4:
        return
    e = 10 * np.log10(np.mean(seg[:n * hop].reshape(n, hop) ** 2, axis=1) + 1e-10)
    e = np.convolve(e, np.ones(3) / 3, mode='same')
    floor = np.percentile(e, 10)
    idx = lambda t: int(min(n - 1, max(0, round((t - a) / step))))  # noqa: E731
    for i, w in enumerate(cw):
        i0, i1 = idx(w['t0']), idx(w['t1'])
        peak = e[i0:max(i1, i0 + 1)].max()
        thr = max(floor + 6.0, peak - 30.0)
        nxt = cw[i + 1]['t0'] if i + 1 < len(cw) else a + n * step
        j, lim = i1, min(idx(nxt) - 1, i1 + int(max_ext / step))
        while j < lim and e[j] > thr:
            j += 1
        if j > i1:
            w['t1'] = a + j * step
        prev = cw[i - 1]['t1'] if i else a
        if w['t0'] - prev > 0.1:                             # word after a pause: onset = energy rise
            j, lim = i0, max(idx(prev) + 1, i0 - int(max_back / step))
            while j > lim and e[j - 1] > thr:
                j -= 1
            w['t0'] = a + j * step


def _recognize(wm, audio, chunks, lang, prompt, task, fine, verbose, timing='auto', threads=None):
    encoded = {}
    lp = None
    if lang is None:
        lang, lp = _detect(wm, audio, chunks, encoded, verbose) if wm.multilingual else ('en', 1.0)
    prev = wm.encode_text(' ' + prompt.strip()) if prompt else []
    rng = np.random.default_rng(0)
    words, meta, per_chunk = [], [], []
    for ci, (a, b) in enumerate(chunks):
        seg = audio[int(a * SR):int(b * SR)]
        k, v = encoded.pop(ci) if ci in encoded else wm.encode(log_mel(seg, wm.n_mels))
        best = None
        for temp in (0.0, 0.2, 0.4, 0.6, 0.8, 1.0):
            r = wm.decode(k, v, lang, task=task, prompt=prev, temperature=temp, rng=rng)
            if best is None or r['avg_logprob'] > best['avg_logprob']:
                best = r
            silent = r['no_speech_prob'] > 0.6 and r['avg_logprob'] < -1.0
            if silent or (r['compression_ratio'] <= 2.4 and r['avg_logprob'] >= -1.0):
                best = r
                break
        r = best
        m = dict(t0=a, t1=b, temperature=r['temperature'], avg_logprob=_r(r['avg_logprob']),
                 no_speech_prob=_r(r['no_speech_prob']), compression_ratio=_r(r['compression_ratio'], 2),
                 text=r['text'])
        meta.append(m)
        _log(verbose, f'chunk {ci + 1}/{len(chunks)} {a:.1f}-{b:.1f}s T={r["temperature"]} '
                      f'lp={r["avg_logprob"]:.2f}: {r["text"][:70]}')
        if (r['no_speech_prob'] > 0.6 and r['avg_logprob'] < -1.0) or not r['tokens']:
            m['skipped'] = True
            continue
        al = wm.align(k, v, lang, r['tokens'], n_frames=len(seg) // HOP, task=task)
        _fix_durations(al)
        al = _merge_punct(al)
        cw = [dict(w=x[0].strip(), t0=a + x[2], t1=a + x[3], p=round(x[4], 3)) for x in al]
        per_chunk.append((a, b, cw, m))
        prev = r['tokens'] if r['temperature'] <= 0.5 else []
    ctc = None
    if timing in ('auto', 'ctc') and per_chunk:
        if not _CTC and _mem_available_gb() < CTC['ram_gb'] + 0.5:
            _unload_whisper(verbose)                     # 4 GB sandboxes: never hold both models
        try:
            ctc = get_ctc(threads=threads, verbose=verbose)
        except Exception as e:                           # aligner unavailable -> keep whisper DTW timing
            if timing == 'ctc':
                raise
            _log(verbose, f'CTC aligner unavailable ({type(e).__name__}: {e}); using DTW word timing')
    for a, b, cw, m in per_chunk:
        m['timing'] = 'ctc' if ctc is not None and _ctc_refine(ctc, audio, a, b, cw, m) else 'dtw'
        words.extend(cw)
    words = _trim_to_speech(words, fine)
    for w in words:
        w['t0'], w['t1'] = round(w['t0'], 3), round(w['t1'], 3)
    return words, lang, lp, meta


def _recognize_omni(ctc, audio, chunks, fine, verbose):
    """CTC-only recognition (Omnilingual 300M): lowercase words without punctuation, for languages Whisper does
    not support; word times from the best path + energy edges."""
    words, meta = [], []
    for ci, (a, b) in enumerate(chunks):
        seg = audio[int(a * SR):int(b * SR)]
        g = ctc.greedy(ctc.logprobs(seg))
        cw = [dict(w=t, t0=max(a, a + f0 * ctc.FRAME - CTC_ONSET_SHIFT), t1=a + (f1 + 1) * ctc.FRAME, p=round(pr, 3),
                   pa=round(pr, 3)) for t, f0, f1, pr in g if t.strip()]
        _refine_edges(cw, seg, a)
        words.extend(cw)
        meta.append(dict(t0=a, t1=b, timing='ctc', text=' '.join(w['w'] for w in cw)))
        _log(verbose, f'chunk {ci + 1}/{len(chunks)} {a:.1f}-{b:.1f}s: {meta[-1]["text"][:70]}')
    words = _trim_to_speech(words, fine)
    for w in words:
        w['t0'], w['t1'] = round(w['t0'], 3), round(w['t1'], 3)
    return words, meta


def _warnings(res):
    out = []
    ch = res.get('chunks') or []
    sus = [c for c in ch if c.get('suspect')]
    if sus:
        out.append(f'{len(sus)}/{len(ch)} chunks: the Whisper text is not confirmed by the acoustic model '
                   f'(hallucination '
                   f'on non-speech, or a language Whisper does not support). The aligner hears: '
                   f'"{sus[0].get("ctc_text", "")[:80]}". Options: lang=..., model="omni" (1600+ languages, no '
                   f'punctuation), or text= with the real transcript. Suspect words carry "suspect": true.')
    if res.get('lang_prob') is not None and res['lang_prob'] < 0.6:
        out.append(f'language detection unsure ({res["lang"]} p={res["lang_prob"]}); pass lang= if you know it')
    dtw = [c for c in ch if c.get('timing') == 'dtw' and c.get('ctc') and not c.get('skipped')]
    if dtw:
        out.append(f'{len(dtw)}/{len(ch)} chunks keep Whisper DTW word timing (±3 frames): the aligner could not hear '
                   f'the voice there (loud music/noise)')
    return out


def _forced(wm, audio, chunks, text, lang, cues, fine, verbose, timing='auto', threads=None):
    """Known text -> times: recognise for coarse positions, map the text onto the chunks (align_text), then
    force-align the known words chunk by chunk: CTC aligner, or whisper DTW (find_alignment accepts any tokens)."""
    rough, lang2, lp, _ = _recognize(wm, audio, chunks, lang, None, 'transcribe', fine, verbose, timing, threads)
    lang = lang or lang2
    coarse = align_text(rough, text)
    ctc = None
    if timing in ('auto', 'ctc'):
        try:
            ctc = get_ctc(threads=threads, verbose=verbose)
        except Exception as e:
            if timing == 'ctc':
                raise
            _log(verbose, f'CTC aligner unavailable ({e}); DTW alignment of the text')
    done = set()
    for a, b in chunks:
        idx = [i for i, w in enumerate(coarse) if i not in done and a - 0.05 <= (w['t0'] + w['t1']) / 2 < b + 0.05]
        if not idx:
            continue
        idx = [i for i in range(idx[0], idx[-1] + 1) if i not in done]
        seg = audio[int(a * SR):int(b * SR)]
        if ctc is not None:
            res, _ = ctc.align(seg, [coarse[i]['w'] for i in idx])
            if res is not None:
                for i, r in zip(idx, res):
                    if r is not None:
                        coarse[i].update(t0=a + r[0], t1=a + r[1], pa=round(r[2], 3), src='aligned')
                done.update(idx)
                continue
        k, v = wm.encode(log_mel(seg, wm.n_mels))
        toks = wm.encode_text(' ' + join_words([coarse[i]['w'] for i in idx], lang))
        if len(toks) > wm.n_ctx - 8:
            continue
        al = _merge_punct(wm.align(k, v, lang, toks, n_frames=len(seg) // HOP))
        if len(al) == len(idx):                          # else tokenisation regrouped words -> coarse timing
            for i, x in zip(idx, al):
                coarse[i].update(t0=a + x[2], t1=a + x[3], p=round(x[4], 3), src='aligned')
            done.update(idx)
    coarse.sort(key=lambda w: w['t0'])
    out = _trim_to_speech(coarse, fine)
    for w in out:
        w['t0'], w['t1'] = round(w['t0'], 3), round(w['t1'], 3)
    return out, lang, lp


# ----------------------------------------------------------------------------------------------- fallbacks
def spread_text(text, regions):
    """known text without any model: words spread over the speech regions proportionally to their length."""
    toks = text.split()
    if not toks:
        return []
    total = sum(b - a for a, b in regions) or 1.0
    weights = np.array([len(norm_word(t)) + 1.5 for t in toks], float)
    pos = np.concatenate([[0], np.cumsum(weights)]) / weights.sum() * total

    def at(x):
        acc = 0.0
        for a, b in regions:
            if x <= acc + (b - a) + 1e-9:
                return a + (x - acc)
            acc += b - a
        return regions[-1][1]
    return [dict(w=t, t0=round(float(at(pos[i])), 3), t1=round(float(at(pos[i + 1])), 3), p=None, src='spread')
            for i, t in enumerate(toks)]


_TC = re.compile(r'(\d+):(\d{2}):(\d{2})[,.](\d{1,3})')


def _tc(s):
    m = _TC.match(s.strip())
    h, mi, se, ms = m.groups()
    return int(h) * 3600 + int(mi) * 60 + int(se) + int(ms.ljust(3, '0')) / 1000.0


def from_srt(src):
    """SRT file path or SRT text -> [{"t0", "t1", "text"}] (tags stripped, line breaks -> spaces)."""
    s = src
    if '\n' not in str(src) and os.path.exists(str(src)):
        s = Path(src).read_text(encoding='utf-8-sig', errors='replace')
    cues = []
    for block in re.split(r'\n\s*\n', s.replace('\r\n', '\n').strip()):
        lines = [l for l in block.split('\n') if l.strip()]
        for i, l in enumerate(lines):
            if '-->' in l:
                a, b = l.split('-->')[:2]
                txt = ' '.join(lines[i + 1:])
                txt = re.sub(r'<[^>]+>|\{[^}]*\}', '', txt).strip()
                if txt:
                    cues.append(dict(t0=_tc(a), t1=_tc(b.split()[0]), text=txt))
                break
    return cues


def cue_words(cues):
    """cue-level timing -> word timing spread inside each cue by character count."""
    words = []
    for c in cues:
        words.extend(spread_text(c['text'], [[c['t0'], c['t1']]]))
    for w in words:
        w['src'] = 'srt'
    return words


# ----------------------------------------------------------------------------------------------- text alignment
def _sim(a, b):
    if a == b:
        return 1.0
    if not a or not b:
        return 0.0
    return difflib.SequenceMatcher(None, a, b, autojunk=False).ratio()


def align_text(words, known_text, path=None, lang=None, model='auto'):
    """Put a known script/lyrics onto recognised words. Text-only DP (exact anchors + fuzzy matching inside the
    gaps; unmatched words get the span of the unmatched recognised words or an interpolation by length).
    With `path`, the audio is used instead: transcribe(path, text=known_text) (acoustic forced alignment)."""
    if path is not None:
        return transcribe(path, lang=lang, model=model, text=known_text)['words']
    rec = _words_of(words)
    kn = known_text.split() if isinstance(known_text, str) else list(known_text)
    if not kn:
        return []
    if not rec:
        return spread_text(' '.join(kn), [[0.0, 1.0]])
    A, B = [norm_word(w) for w in kn], [norm_word(w['w']) for w in rec]
    match = [None] * len(kn)
    sm = difflib.SequenceMatcher(None, A, B, autojunk=False)
    blocks = sm.get_matching_blocks()
    pa = pb = 0
    for blk in blocks:
        _fuzzy(A, B, pa, blk.a, pb, blk.b, match)
        for t in range(blk.size):
            match[blk.a + t] = (blk.b + t, 1.0)
        pa, pb = blk.a + blk.size, blk.b + blk.size
    out = []
    for i, w in enumerate(kn):
        if match[i] is not None:
            j, s = match[i]
            r = rec[j]
            out.append(dict(w=w, t0=r['t0'], t1=r['t1'], p=_r((r.get('p') or 1.0) * s), src='asr', rec=j))
        else:
            out.append(dict(w=w, t0=None, t1=None, p=None, src='interp'))
    i = 0
    while i < len(out):                                     # fill runs of unmatched words
        if out[i]['t0'] is not None:
            i += 1
            continue
        j = i
        while j < len(out) and out[j]['t0'] is None:
            j += 1
        prev_rec = out[i - 1]['rec'] if i > 0 else -1
        next_rec = out[j]['rec'] if j < len(out) else len(rec)
        span = rec[prev_rec + 1:next_rec]
        if span:
            a, b = span[0]['t0'], span[-1]['t1']
        else:
            a = out[i - 1]['t1'] if i > 0 else max(0.0, (out[j]['t0'] if j < len(out) else 0.0) - 0.3 * (j - i))
            b = out[j]['t0'] if j < len(out) else a + 0.3 * (j - i)
        wts = np.array([len(norm_word(out[t]['w'])) + 1.5 for t in range(i, j)], float)
        edges = a + (b - a) * np.concatenate([[0], np.cumsum(wts)]) / wts.sum()
        for n, t in enumerate(range(i, j)):
            out[t]['t0'], out[t]['t1'] = round(float(edges[n]), 3), round(float(edges[n + 1]), 3)
        i = j
    for w in out:
        w.pop('rec', None)
    return out


def _fuzzy(A, B, a0, a1, b0, b1, match):
    """monotone fuzzy matching of A[a0:a1] to B[b0:b1] (small gaps between exact anchors)."""
    n, m = a1 - a0, b1 - b0
    if n == 0 or m == 0:
        return
    if n * m > 40000:                                       # very long gap: proportional pairing only
        for i in range(n):
            j = b0 + min(m - 1, int(i * m / n))
            s = _sim(A[a0 + i], B[j])
            if s >= 0.6:
                match[a0 + i] = (j, s)
        return
    S = np.zeros((n + 1, m + 1))
    bt = np.zeros((n + 1, m + 1), np.int8)
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            s = _sim(A[a0 + i - 1], B[b0 + j - 1])
            best, t = S[i - 1, j], 1
            if S[i, j - 1] > best:
                best, t = S[i, j - 1], 2
            if s >= 0.5 and S[i - 1, j - 1] + s > best:
                best, t = S[i - 1, j - 1] + s, 0
            S[i, j], bt[i, j] = best, t
    i, j = n, m
    while i > 0 and j > 0:
        t = bt[i, j]
        if t == 0:
            match[a0 + i - 1] = (b0 + j - 1, _sim(A[a0 + i - 1], B[b0 + j - 1]))
            i, j = i - 1, j - 1
        elif t == 1:
            i -= 1
        else:
            j -= 1


# ----------------------------------------------------------------------------------------------- jump cuts
def _lang_of(words, lang):
    if lang:
        return lang[:2]
    text = ' '.join(w['w'] for w in words[:50])
    cyr = sum(1 for c in text if 'Ѐ' <= c <= 'ӿ')         # language data: the Cyrillic block U+0400–U+04FF
    return 'ru' if cyr > len(text) * 0.3 else 'en'


def _phrase_hits(words, phrases):
    """indices of words forming any phrase (1-3 words) from `phrases` (normalised)."""
    norm = [norm_word(w['w']) for w in words]
    hits = []
    for i in range(len(words)):
        for n in (3, 2, 1):
            if i + n <= len(words) and ' '.join(norm[i:i + n]) in phrases:
                hits.append((i, i + n - 1, ' '.join(norm[i:i + n])))
                break
    return hits


def speech_segments(words, *, speech=None, min_pause=0.35, keep_pause=0.12, lead=0.06, tail=0.10, fillers='sure',
                    repeats=True, voiced_gaps=True, lang=None, fps=None, src='main', min_keep=0.2):
    """Jump-cut data for speech genres (cut by words): pauses, fillers, repeats, voiced gaps (sound in a pause that
    no word explains: a filler such as 'umm' that Whisper dropped, breaths, laughs), the cut list and the keep ranges
    (source s). fillers: 'sure' (hesitation sounds: uh/um ...), 'all' (+ discourse fillers: like/you know ...),
    'none'; the per-language word lists are FILLERS.
    Each removed stretch leaves keep_pause of silence (split around the cut) and never cuts closer than
    lead/tail to a kept word. With fps, cut points are snapped to frames and EDL segments are returned."""
    if isinstance(words, dict):
        speech = speech if speech is not None else words.get('speech')
        lang = lang or words.get('lang')
        words = words['words']
    words = [w for w in words if w.get('t0') is not None]
    if not words:
        return dict(pauses=[], fillers=[], maybe_fillers=[], repeats=[], voiced_gaps=[], cuts=[], keep=[], stats={})
    lg = _lang_of(words, lang)
    fl = FILLERS.get(lg, FILLERS['en'])
    drop = set()
    hits_sure = _phrase_hits(words, fl['sure'])
    hits_maybe = _phrase_hits(words, fl['maybe'])
    if fillers in ('sure', 'all'):
        for a, b, _ in hits_sure:
            drop.update(range(a, b + 1))
    if fillers == 'all':
        for a, b, _ in hits_maybe:
            drop.update(range(a, b + 1))
    rep = []
    if repeats:
        norm = [norm_word(w['w']) for w in words]
        i = 0
        while i < len(words) - 1:
            hit = False
            for n in (3, 2, 1):                              # "I wanted I wanted to say" / "the the"
                if i + 2 * n <= len(words) and norm[i:i + n] == norm[i + n:i + 2 * n] and all(norm[i:i + n]) \
                        and words[i + n]['t0'] - words[i + n - 1]['t1'] < 1.0:
                    rep.append((i, i + n - 1, ' '.join(norm[i:i + n])))
                    drop.update(range(i, i + n))
                    i += n
                    hit = True
                    break
            if not hit:
                i += 1
    kept = [i for i in range(len(words)) if i not in drop]
    pauses, vg, cuts = [], [], []
    regions = speech or []

    def voiced(a, b):
        return sum(max(0.0, min(b, r1) - max(a, r0)) for r0, r1 in regions)
    for k in range(len(kept) - 1):
        i, j = kept[k], kept[k + 1]
        a, b = words[i]['t1'], words[j]['t0']
        removed = [x for x in range(i + 1, j)]
        gap = b - a
        kind = 'filler' if removed else 'pause'
        if removed and any(x in {r for r0, r1, _ in rep for r in range(r0, r1 + 1)} for x in removed):
            kind = 'repeat'
        # sound inside a pause that no word explains; margins skip the VAD's ~0.1 s release after the word
        v = voiced(a + 0.12, b - 0.08) if regions and not removed and gap >= 0.4 else 0.0
        if v >= 0.15 and voiced_gaps:
            vg.append(dict(t0=_r(a), t1=_r(b), voiced=_r(v)))
            kind = 'voiced_gap'
        if kind == 'pause' and gap >= min_pause:
            pauses.append(dict(t0=_r(a), t1=_r(b), dur=_r(gap)))
        if gap >= min_pause or removed:
            c0 = a + max(tail, keep_pause / 2)
            c1 = b - max(lead, keep_pause / 2)
            if c1 - c0 >= 0.05:
                cuts.append(dict(t0=c0, t1=c1, kind=kind, text=join_words([words[x]['w'] for x in removed]) or None))
    t_start = max(0.0, words[kept[0]]['t0'] - lead) if kept else words[0]['t0']
    t_end = words[kept[-1]]['t1'] + tail if kept else words[-1]['t1']
    if fps:
        for c in cuts:                                       # never into a word: start up, end down to frames
            c['t0'] = math.ceil(c['t0'] * fps - 1e-6) / fps
            c['t1'] = math.floor(c['t1'] * fps + 1e-6) / fps
        cuts = [c for c in cuts if c['t1'] - c['t0'] >= 1.0 / fps]
        t_start = math.floor(t_start * fps + 1e-6) / fps
        t_end = math.ceil(t_end * fps - 1e-6) / fps
    keep, cur = [], t_start
    for c in cuts:
        if c['t0'] > cur:
            keep.append([cur, c['t0']])
        cur = max(cur, c['t1'])
    if t_end > cur:
        keep.append([cur, t_end])
    merged = []                                              # keep pieces shorter than min_keep join a neighbour
    for k in keep:
        short = merged and (k[1] - k[0] < min_keep or merged[-1][1] - merged[-1][0] < min_keep)
        if short and k[0] - merged[-1][1] < 0.6:
            merged[-1][1] = k[1]
        else:
            merged.append(list(k))
    keep = [[_r(a), _r(b)] for a, b in merged]
    before = t_end - t_start
    after = sum(b - a for a, b in keep)
    nw = len(kept)
    res = dict(lang=lg,
               pauses=pauses, voiced_gaps=vg,
               fillers=[dict(w=t, t0=words[a]['t0'], t1=words[b]['t1']) for a, b, t in hits_sure],
               maybe_fillers=[dict(w=t, t0=words[a]['t0'], t1=words[b]['t1'], i=a) for a, b, t in hits_maybe],
               repeats=[dict(w=t, t0=words[a]['t0'], t1=words[b]['t1']) for a, b, t in rep],
               cuts=[dict(t0=_r(c['t0']), t1=_r(c['t1']), kind=c['kind'], text=c['text']) for c in cuts],
               keep=keep, dropped_words=sorted(drop),
               stats=dict(before_s=_r(before, 2), after_s=_r(after, 2), removed_s=_r(before - after, 2),
                          wps_before=_r(len(words) / max(before, 1e-6), 2), wps_after=_r(nw / max(after, 1e-6), 2)))
    if fps:
        res['segments'] = keep_to_segments(keep, fps, src)
    return res


def keep_to_segments(keep, fps, src='main', f_start=0, id_prefix='J'):
    """keep ranges (source s) -> consecutive EDL segments {"id","f0","f1","src","t"} (frames inclusive)."""
    segs, f = [], int(f_start)
    for i, (a, b) in enumerate(keep):
        n = int(round((b - a) * fps))
        if n <= 0:
            continue
        segs.append(dict(id=f'{id_prefix}{i + 1:02d}', f0=f, f1=f + n - 1, src=src, t=round(a, 4)))
        f += n
    return segs


def remap_words(words, segments, fps, src=None, edge=0.03):
    """Source-time words -> output-time words through EDL segments (speed respected; speed_curve -> mean rate).
    Returns (words_out, issues): issues list cuts that fall inside a word (QA: cut inside a word)."""
    words = _words_of(words)
    out, issues = [], []
    for s in segments:
        if src is not None and s.get('src') != src:
            continue
        sp = float(s.get('speed', 1.0) or 1.0)
        if s.get('speed_curve'):
            sp = float(np.mean([r for _, r in s['speed_curve']]))
        n = int(s['f1']) - int(s['f0']) + 1
        a = float(s['t'])
        b = a + n / fps * sp
        o = int(s['f0']) / fps
        for w in words:
            if w['t1'] <= a or w['t0'] >= b:
                continue
            inside = (min(b, w['t1']) - max(a, w['t0'])) / max(1e-6, w['t1'] - w['t0'])
            for cut, side in ((a, 'in'), (b, 'out')):
                if w['t0'] + edge < cut < w['t1'] - edge:
                    issues.append(dict(f=int(s['f0']) if side == 'in' else int(s['f1']) + 1, seg=s.get('id'),
                                       word=w['w'], side=side, inside=_r(inside, 2)))
            if inside < 0.5:
                continue
            t0 = o + (max(a, w['t0']) - a) / sp
            t1 = o + (min(b, w['t1']) - a) / sp
            d = dict(w=w['w'], t0=round(t0, 3), t1=round(t1, 3), src_t0=w['t0'])
            if inside < 0.999:
                d['clipped'] = True
            if w.get('p') is not None:
                d['p'] = w['p']
            out.append(d)
    out.sort(key=lambda d: d['t0'])
    return out, issues


# ----------------------------------------------------------------------------------------------- subtitles
def _glue(tokens):
    """g[i] = True: no line / chunk may end after token i (short function word, a number before its unit, a dash
    next); a token that ends with punctuation is a natural break and never glued."""
    weak = WEAK_END['ru'] | WEAK_END['en']
    g = [False] * len(tokens)
    for i in range(len(tokens) - 1):
        tok, nxt = tokens[i], tokens[i + 1]
        if re.search(r'[.,;:!?…)"»”]$', tok):
            continue
        core = norm_word(tok)
        number = re.match(r'^[+\-−]?[$€£₽]?\d[\d.,]*%?$', tok) and re.match(r'^[^\W\d_]', nxt) and \
            norm_word(nxt) not in weak                       # "10 minutes", "4 million" stay together
        if core in weak or nxt in ('—', '–', '-') or number:
            g[i] = True
    return g


def _glue_cost(tokens):
    """line-break cost after each token: a short function word 2500, a number before its unit 3000, else 0 - far
    above any balance difference, below a 1-char overflow (10000): a fitting break without them always wins, and
    a glued break is used only when nothing else fits."""
    g = _glue(tokens)
    out = []
    for i, t in enumerate(tokens):
        if not g[i]:
            out.append(0.0)
        elif re.match(r'^[+\-−]?[$€£₽]?\d', t):
            out.append(3000.0)
        else:
            out.append(2500.0)
    return out


def _modifier(tok):
    """an English word that usually stands before its noun (quantifier, common adjective, -ous/-ful/-ive/... word)"""
    w = norm_word(tok)
    if not w.isalpha() or _SENT_RE.search(tok) or _CLAUSE_RE.search(tok):
        return False
    return w in MODIFIERS['en'] or (len(w) >= 5 and w.endswith(MODIFIER_SUFFIXES['en']))


def _nounish(tok):
    w = norm_word(tok)
    return len(w) >= 3 and w.isalpha() and w not in INTRO_WORDS['en'] and w not in NOT_NOUNS['en'] and \
        w not in WEAK_END['en']


def _name_pair(tokens, k):
    """tokens k, k+1: two capitalised words of one name ("United States"), not a sentence start + "I"."""
    a, b = tokens[k], tokens[k + 1]
    return a[:1].isupper() and b[:1].isupper() and b != 'I' and norm_word(a).isalpha() and \
        norm_word(b).isalpha() and norm_word(a) not in INTRO_WORDS['en'] and norm_word(a) not in NOT_NOUNS['en']


def _phrase_costs(tokens, gaps=None, en=True):
    """Cost of a caption chunk ending after each token (the last one: 0); gaps[k] = pause after token k (s).
    < 0: a natural break - sentence end -400, clause punctuation -200, a pause (up to -360 at 0.6 s), right before
    a phrase-introducing word -100. > 0: splits a phrase - after an article / preposition / conjunction 2500, a
    number before its unit 3000, a copula / auxiliary 900 (_glue_cost), after another phrase-introducing word 1500, a
    modifier from its noun, inside a name, a subject pronoun from its verb 900, a scale word from its unit 1000.
    English word lists when `en`; any language: punctuation, pauses, WEAK_END."""
    n = len(tokens)
    glue = _glue_cost(tokens)
    out = [0.0] * n
    for k in range(n - 1):
        tk, nx = tokens[k], tokens[k + 1]
        c = 0.0
        if gaps is not None and gaps[k] is not None:
            c -= min(max(float(gaps[k]), 0.0), 0.6) * 600.0
        if _SENT_RE.search(tk):
            c -= 400.0
        elif _CLAUSE_RE.search(tk):
            c -= 200.0
        else:
            w = norm_word(tk)
            # a copula / auxiliary / pronoun contraction (WEAK_END, not phrase-introducing) ends a chunk better
            # than an article or a preposition does
            c += glue[k] if (not glue[k] or not en or w in INTRO_WORDS['en'] or glue[k] > 2500.0) else 900.0
            if en and not glue[k]:
                if w in INTRO_WORDS['en']:
                    c += 1500.0
                elif _modifier(tk) and _nounish(nx):
                    c += 900.0
                elif _name_pair(tokens, k):
                    c += 900.0
                elif w in SUBJECT_PRONOUNS['en']:          # "it | was the best": subject and verb together
                    c += 900.0
            if en and norm_word(nx) in INTRO_WORDS['en']:
                c -= 100.0
            if _scale_unit(tk, nx):                          # "4 million | dollars" (ed_text's split: +1)
                c += 1000.0
        out[k] = c
    return out


def _line_costs(tokens):
    """line-break cost after each token: _glue_cost (a copula / auxiliary 1200 instead of 2500), + 1500 after another
    phrase-introducing word, + 400 between a modifier and its noun or inside a name (above any balance difference of
    a caption line, below an overflow)."""
    out = _glue_cost(tokens)
    for k in range(len(tokens) - 1):
        tk = tokens[k]
        w = norm_word(tk)
        if out[k] == 2500.0 and w not in INTRO_WORDS['en']:
            out[k] = 1200.0                                  # a copula / auxiliary: "it was / the best trip"
        if out[k] or _SENT_RE.search(tk) or _CLAUSE_RE.search(tk):
            continue
        if w in INTRO_WORDS['en']:
            out[k] += 1500.0
        elif _scale_unit(tk, tokens[k + 1]):
            out[k] += 1000.0
        elif (_modifier(tk) and _nounish(tokens[k + 1])) or _name_pair(tokens, k):
            out[k] += 400.0
    return out


def _line_ends(tokens, lines):
    """index of the last token of every line but the last (lines = break_lines(tokens, ...))."""
    ends, k = [], 0
    for ln in lines[:-1]:
        acc = -1
        while k < len(tokens) and acc + 1 + len(tokens[k]) <= len(ln):
            acc += 1 + len(tokens[k])
            k += 1
        ends.append(k - 1)
    return ends


def break_lines(tokens, max_chars, max_lines=2, measure=None):
    """Balanced line breaks: minimise overflow, then line-length variance; a line never ends with a short
    function word (the, a, in, and ...) or splits a number from its unit unless nothing else fits, and keeps a
    modifier with its noun and a name together when it can (_line_costs); prefers breaks after punctuation.
    measure(text) = line width in characters (default len; glyph_width for a caption preset)."""
    toks = [t for t in tokens if t]
    n = len(toks)
    if n == 0:
        return []
    ms = measure or len
    if n == 1 or max_lines <= 1 or ms(' '.join(toks)) <= max_chars:
        return [' '.join(toks)]
    glue = _line_costs(toks)
    L = lambda a, b: ms(' '.join(toks[a:b]))  # noqa: E731
    best = None
    for k in range(2, max_lines + 1):
        if k > n:
            break
        target = (L(0, n) - (k - 1)) / k
        INF = float('inf')
        dp = [[INF] * (n + 1) for _ in range(k + 1)]
        bp = [[0] * (n + 1) for _ in range(k + 1)]
        dp[0][0] = 0.0
        for m in range(1, k + 1):
            for j in range(1, n + 1):
                for i in range(m - 1, j):
                    if dp[m - 1][i] == INF:
                        continue
                    ln = L(i, j)
                    over = ln - max_chars                    # any overflow (a fraction of a glyph too) loses
                    c = dp[m - 1][i] + (ln - target) ** 2 + (10000.0 * (1.0 + over) ** 2 if over > 1e-9 else 0.0)
                    if j < n:
                        c += glue[j - 1]
                    if j < n and toks[j - 1][-1:] in ',.;:!?…':
                        c -= 30.0
                    if c < dp[m][j]:
                        dp[m][j], bp[m][j] = c, i
        if dp[k][n] < INF and (best is None or dp[k][n] < best[0] - 1e-9):
            cuts, j = [], n
            for m in range(k, 0, -1):
                cuts.append((bp[m][j], j))
                j = bp[m][j]
            best = (dp[k][n], [' '.join(toks[a:b]) for a, b in reversed(cuts)])
        if best and all(len(x) <= max_chars for x in best[1]):
            break                                            # fewest lines that fit
    return best[1] if best else [' '.join(toks)]


def _fits(tokens, max_chars, max_lines, measure=None):
    ms = measure or len
    if ms(' '.join(tokens)) <= max_chars:
        return True
    if max_lines <= 1:
        return False
    lines = break_lines(tokens, max_chars, max_lines, measure)
    return len(lines) <= max_lines and all(ms(x) <= max_chars for x in lines)


SUB_DEFAULTS = {
    # clips/ugc genre cards: karaoke chunk 2-3 words, <=2 lines of ~20 chars, chunk <= 2.5 s, <= 20 cps,
    # shown 2 frames before the first word, highlight 1 frame before each word, >= 4 frames per word @30
    'karaoke': dict(max_chars=20, max_chars_h=36, max_lines=2, min_dur=0.0, max_cps=20.0, lead=2, tail=6,
                    max_words=3, max_words_h=6, max_dur=2.5, max_dur_h=4.0, split_pause=0.25, bridge=0.6),
    'subtitle': dict(max_chars=26, max_chars_h=42, max_lines=2, min_dur=0.8, max_cps=None, lead=2, tail=6,
                     max_words=None, max_words_h=None, max_dur=6.0, max_dur_h=6.0, split_pause=0.6, bridge=0.3),
}
QA_MAX_CPS, QA_MIN_SHOW = 20.0, 0.7      # ed_qa limits on what is on screen (chars / s, seconds)


def caption_preset(style, canvas=(1080, 1920)):
    """ed_text caption preset named by `style` ("podcast_bold", an alias, or {"preset": name, ...}) ->
    {"name", "kinds", "hints", "caps", "font", "tracking"} with chunking hints for that canvas
    (ed_text.caption_hints), or None."""
    name = style if isinstance(style, str) else (style.get('preset') if isinstance(style, dict) else None)
    if not name:
        return None
    try:
        import ed_text as Tx
    except Exception:                                       # no ed_text: plain defaults
        return None
    canon = getattr(Tx, 'caption_style_name', None)
    n = canon(name) if canon else None
    if not n:
        return None
    P = (getattr(Tx, 'CAPTION_STYLES', {}) or {}).get(n) or {}
    hints = {}
    fn = getattr(Tx, 'caption_hints', None)
    try:
        hints = dict(fn(n, int(canvas[0]), int(canvas[1])) if fn else P.get('voice') or {})
    except Exception:
        hints = dict(P.get('voice') or {})
    st = (P.get('layer') or {}).get('style') or {}
    return dict(name=n, kinds=list(P.get('kinds') or ['subtitle', 'karaoke']), hints=hints, caps=bool(st.get('caps')),
                font=st.get('font'), tracking=st.get('tracking', 0.0))


def _merge_asr_splits(words):
    """"$10" + ",000" -> "$10,000" (one word, joint timing) so captions never show "$10 ,000"."""
    out = []
    for w in words:
        t = str(w['w']).strip()
        if out and re.match(r'^[,.]\d{3}(?!\d)', t) and re.search(r'\d$', str(out[-1]['w']).strip()):
            out[-1] = dict(out[-1], w=str(out[-1]['w']).strip() + t, t1=max(out[-1]['t1'], w['t1']))
            continue
        out.append(dict(w))
    return out


def subtitle_chunks(words, max_chars=None, max_lines=None, min_dur=None, max_cps=None, lead=None, tail=None, *,
                    kind=None, fps=30, max_words=None, max_dur=None, split_pause=None, bridge=None,
                    lang=None, vertical=True, style=None, pos=None, highlight=None, word_lead=1, min_on=4,
                    canvas=None, fillers='merge', min_show=QA_MIN_SHOW, max_early=0.5, max_lag=0.3, breaks=None,
                    soft_breaks=None):
    """Word timestamps (OUTPUT time - use remap_words after cuts) -> ed_text layers, one per chunk:
    {"kind": "subtitle"|"karaoke", "f0", "f1", "t0", "t1", "text", "lines", "words", "lang", "cps", "lead", "tail",
     "chunk": {...}, ["style"], ["warn"], ["hidden"]} - the ed_text chunk params + lead/tail (frames) make ed_text
    reproduce exactly these frames while keeping per-word karaoke timing (switch_lead/min_on in frames).
    lead/tail are frames (int) or seconds (float < 1). Defaults per kind: SUB_DEFAULTS; cps by language: LANG_RULES.
    style = an ed_text caption preset (name or {"preset": ...}): max_chars / max_lines / max_words default to
    ed_text.caption_hints(style, canvas) and a karaoke-only preset makes kind "karaoke" (kind=None picks it).
    Chunk breaks are phrase-aware: between forced breaks (a pause >= split_pause, `breaks`) the chunking is the
    cheapest by _phrase_costs - sentence / clause punctuation and real pauses are good places; splitting a modifier
    from its noun, a name, a subject from its verb, ending on an article / preposition / conjunction, or leaving the
    last word of a sentence alone for the next chunk cost (English word lists: INTRO_WORDS, MODIFIERS; any language:
    punctuation, pauses, WEAK_END) - within hard limits (lines, max_words + 1, max_dur) and the reading time.
    Readability (ed_qa: <= 20 chars/s, >= 0.7 s on screen) stays hard:
      - ASR digit splits are joined ("$10" ",000"); no line and no chunk ends on a short function word when it can
        be helped;
      - a chunk of fillers only ("It's like", "you know") joins its neighbour, or (no room) its words stay unshown
        while its time goes to the next chunk; hesitations (uh, um) are never shown (fillers='keep' shows all);
      - each chunk needs max(min_dur, min_show, chars / max_cps) s: it extends into the pause after it, then up to
        max_early s before its first word, then borrows from a neighbour with time to spare (a chunk may start up
        to max_lag s after its first word); still short or > 20 chars/s -> merged with a neighbour when the text
        fits, else its discourse fillers are dropped from the text; a passage that still fails is chunked again
        for reading time first (then filled greedily); what remains is reported in "warn".
    breaks = output seconds where the picture / audio jumps (jump cuts, part joins): no chunk holds words from both
    sides and no chunk is shown across one. soft_breaks = preferred chunk boundaries that may still be crossed
    (camera cuts over continuous speech): a chunk ends there when the phrase allows, a chunk change happens on one
    when it falls between two chunks, and a chunk's lead / tail does not run over one.
    Line fit: with a caption preset, ed_text.text_fits (the preset's measured text) decides whether a chunk fits its
    lines; without it, per-glyph widths of the preset's font (wide letters count more than an average character),
    else a conservative built-in glyph table (glyph_width)."""
    if isinstance(words, dict):
        lang = lang or words.get('lang')
        words = words['words']
    words = [dict(w) for w in words
             if w.get('t0') is not None and w.get('t1') is not None and str(w.get('w', '')).strip()]
    if not words:
        return []
    words = _merge_asr_splits(sorted(words, key=lambda w: w['t0']))
    lg = _lang_of(words, lang)
    cv = tuple(canvas) if canvas else ((1080, 1920) if vertical else (1920, 1080))
    vertical = cv[1] >= cv[0]
    pre = caption_preset(style, cv)
    hints = (pre or {}).get('hints') or {}
    if pre and pre['kinds'] == ['karaoke']:
        kind = 'karaoke'                                     # the preset only renders word-by-word captions
    kind = kind or 'subtitle'
    d = SUB_DEFAULTS['karaoke' if kind == 'karaoke' else 'subtitle']
    rules = LANG_RULES.get(lg, LANG_RULES['en'])
    max_chars = max_chars or hints.get('max_chars') or (d['max_chars'] if vertical else d['max_chars_h'])
    if rules.get('cjk'):
        max_chars = min(max_chars, rules['line_v' if vertical else 'line'])
    max_lines = max_lines or hints.get('max_lines') or d['max_lines']
    min_dur = d['min_dur'] if min_dur is None else min_dur
    max_cps = max_cps or d['max_cps'] or rules['cps']
    hard_cps = max(float(max_cps), QA_MAX_CPS)
    if max_words is None:
        max_words = hints.get('max_words') or (d['max_words'] if vertical else d['max_words_h'])
    max_dur = max_dur or (d['max_dur'] if vertical else d['max_dur_h'])
    split_pause = d['split_pause'] if split_pause is None else split_pause
    bridge = d['bridge'] if bridge is None else bridge
    fr = lambda v, dflt: (dflt if v is None else (v * fps if isinstance(v, float) and v < 1 else v)) / fps  # noqa: E731
    lead_s, tail_s = fr(lead, d['lead']), fr(tail, d['tail'])
    # ---- fillers: hesitations are never shown, discourse fillers may be hidden when a chunk needs it
    fl = FILLERS.get(lg, FILLERS['en'])
    n = len(words)
    hes = [fillers != 'keep' and norm_word(w['w']) in fl['sure'] for w in words]
    soft = [False] * n
    for i0, i1, _ in _phrase_hits(words, fl['maybe'] | FILLER_PHRASES.get(lg, set())):
        for k in range(i0, i1 + 1):
            soft[k] = True
    vis = [i for i in range(n) if not hes[i]]
    if not vis:
        return []
    toks = [words[i]['w'].strip() for i in vis]
    glue = _glue(toks)
    brk_t = sorted(float(b) for b in (breaks or []))
    soft_t = sorted(float(b) for b in (soft_breaks or []) if not any(abs(float(b) - h) < 1e-3 for h in brk_t))
    # line fit: a caption preset is measured (ed_text.text_fits, else the conservative glyph table); plain captions
    # count characters
    measure, cap_k = _preset_measure(pre) if pre and not rules.get('cjk') else (None, 1.0)
    t_fits = None
    if pre and not rules.get('cjk'):
        try:
            import ed_text as _Tx0
            t_fits = getattr(_Tx0, 'text_fits', None)
        except Exception:
            t_fits = None
    fit_memo = {}

    def text_fit(tk):
        """(fits, lines) of a chunk's tokens at the preset size (max_lines lines)"""
        key = tuple(tk)
        if key not in fit_memo:
            res = None
            if t_fits is not None and tk:
                try:
                    r = t_fits(' '.join(tk), style, cv, max_lines=max_lines) or {}
                    ok, lines = bool(r.get('fits')), r.get('lines')
                    if not (isinstance(lines, list) and lines and all(isinstance(x, str) for x in lines) and
                            ' '.join(' '.join(lines).split()).lower() == ' '.join(tk).lower()):
                        lines = break_lines(tk, max_chars * cap_k, max_lines, measure)    # every line measured too
                        ok = ok and all(bool((t_fits(x, style, cv, max_lines=1) or {}).get('fits')) for x in lines)
                    res = (ok, list(lines))                  # the renderer's own lines: never one it rejects
                except Exception:
                    res = None
            if res is None:                                  # caption_hints keeps 3 % for its average glyph
                lim = max_chars * cap_k
                lines = break_lines(tk, lim, max_lines, measure)
                ms = measure or len
                res = (bool(tk) and len(lines) <= max(1, max_lines) and all(ms(x) <= lim + 1e-9 for x in lines),
                       lines)
            fit_memo[key] = res
        return fit_memo[key]

    def crosses(a_t, b_t):                                   # a break between two words (or at their joint)
        return any(a_t - 1e-6 <= b <= b_t + 1e-6 for b in brk_t)

    # ---- 1. chunks of visible words (index ranges into vis): the cheapest split by a phrase cost between forced
    #      breaks (a pause >= split_pause, `breaks`). Hard: the lines (max_chars x max_lines), max_words + 1 words,
    #      max_dur. Per break: _phrase_costs (punctuation, pauses, function words, a modifier and its noun, names,
    #      numbers and units) + one trailing word of a phrase left for the next chunk, or the first word of a
    #      sentence left at the end of this one. Per chunk: a sentence end inside it, too little time to read it, a
    #      one-word chunk, a bad line break inside it.
    m = len(vis)
    gaps = [words[vis[k + 1]]['t0'] - words[vis[k]]['t1'] for k in range(m - 1)] + [None]
    forced = [k == m - 1 or gaps[k] >= split_pause or crosses(words[vis[k]]['t1'], words[vis[k + 1]]['t0'])
              for k in range(m)]
    sent = [bool(_SENT_RE.search(t)) for t in toks]
    clause = [bool(_CLAUSE_RE.search(t)) for t in toks]
    starts = [k == 0 or forced[k - 1] or sent[k - 1] for k in range(m)]       # a sentence / utterance starts here
    bcost = _phrase_costs(toks, gaps, en=lg == 'en')
    lcost = _line_costs(toks)
    soft_v = [soft[i] for i in vis]
    for k in range(m - 1):
        if forced[k] or sent[k] or clause[k]:
            continue
        if sent[k + 1]:                                      # "... on various | models." : the last word alone
            bcost[k] += 1000.0
        elif clause[k + 1] or forced[k + 1] or (gaps[k + 1] or 0.0) >= 0.3:
            bcost[k] += 600.0
        if starts[k]:                                        # "... in Asia. So | how much"
            bcost[k] += 700.0
    r = 0                                                    # a filler phrase opening a sentence ("It's like | ...")
    while r < m:                                             # is a natural break: step 2 joins or hides it
        if soft_v[r] and starts[r]:
            e = r
            while e + 1 < m and soft_v[e + 1] and not forced[e]:
                e += 1
            if e > r and e < m - 1 and not forced[e]:
                bcost[e] = min(bcost[e], 0.0) - 300.0
            r = e + 1
        else:
            r += 1
    for sb in soft_t:                                        # soft breaks (camera cuts): preferred boundaries
        for k in range(m - 1):
            a_t, b_t = words[vis[k]]['t1'], words[vis[k + 1]]['t0']
            if a_t - 1e-3 <= sb <= b_t + 1e-3:              # outweighs a mild phrase cost, not a modifier
                bcost[k] -= 700.0                            # before its noun (900) or a function word
            elif words[vis[k]]['t0'] < sb < a_t:             # inside word k: right before or after it
                bcost[k] -= 350.0
                if k > 0:
                    bcost[k - 1] -= 350.0
    cum = [0]
    for t in toks:
        cum.append(cum[-1] + len(t))
    cap = max_chars * max(1, max_lines)

    def nchar(a_, b_):
        return cum[b_ + 1] - cum[a_] + (b_ - a_)

    def room(k, after, share):                               # time a chunk may take from the gap before / after
        if after:
            g = gaps[k] if k < m - 1 else 1.0
            return min(max(g, 0.0) * (1.0 if forced[k] else share), 0.6)
        g = gaps[k - 1] if k > 0 else words[vis[0]]['t0']
        return min(max(g, 0.0) * (1.0 if k == 0 or forced[k - 1] else share), max_early)

    def chunk_cost(a_, b_, rw=2500.0, share=0.5):
        nw, ln = b_ - a_ + 1, nchar(a_, b_)
        c = 250.0
        for k in range(a_, b_):
            if sent[k]:
                lone = k - a_ <= 1 and starts[a_] and \
                    words[vis[k]]['t1'] - words[vis[a_]]['t0'] < max(min_dur, 0.8)
                c += 0.0 if (lone and kind != 'karaoke') else (1500.0 if kind == 'karaoke' else 400.0)
            elif clause[k] and ln >= 0.5 * cap:
                c += 150.0
        if max_words and nw > max_words:
            c += 600.0
        if all(soft_v[a_:b_ + 1]) and (nw > 1 or starts[a_]):
            return c                                         # fillers only: joined or hidden in step 2
        if nw == 1 and not (starts[a_] and (sent[b_] or forced[b_])):
            c += 350.0
        d = words[vis[b_]]['t1'] - words[vis[a_]]['t0'] + room(a_, False, share) + room(b_, True, share)
        need = max(min_show, ln / hard_cps)
        if d < need:
            c += rw * (need - d) / need
        c += 150.0 * max(0.0, 0.4 - ln / cap) / 0.4
        if ln > max_chars and max_lines > 1 and not rules.get('cjk'):
            for e in _line_ends(toks[a_:b_ + 1], lines_of(a_, b_)):
                c += 0.2 * max(0.0, lcost[a_ + e])
        return c

    def lines_of(a_, b_):
        return text_fit(toks[a_:b_ + 1])[1]

    def fits_ab(a_, b_):                                     # the chunk's lines fit (measured with a preset)
        return text_fit(toks[a_:b_ + 1])[0]
    segs = []                                                # forced segments (token ranges)
    s0 = 0
    for e0 in range(m):
        if forced[e0]:
            segs.append((s0, e0))
            s0 = e0 + 1

    early_f, lag_f, cut_f = int(max_early * fps + 1e-6), int(max_lag * fps + 1e-6), int(0.12 * fps + 1e-6)

    def seg_frames(s0, e0):
        """frames the chunks of a forced segment may use (a break, the words around it)"""
        t_a, t_b = words[vis[s0]]['t0'], words[vis[e0]]['t1']
        lo = max([b for b in brk_t if b <= t_a + 1e-6] or [0.0])
        hi = min([b for b in brk_t if b >= t_b - 1e-6] or [math.inf])
        if e0 < m - 1:
            hi = min(hi, words[vis[e0 + 1]]['t0'])
        elif hi == math.inf:
            hi = t_b + 3.0
        return int(math.ceil(lo * fps - 1e-3)), int(math.ceil(hi * fps - 1e-3)) - 1

    def dp_groups(s0, e0, rw=800.0, share=0.5):
        """cheapest chunking of a forced segment; first of all the one whose chunks all get their reading time
        when laid out back to back (each from its first word - max_early / the previous chunk, starting no later
        than its first word + max_lag, staying until its last word - 0.12 s): labels (time overflow in frames,
        cost, last frame) per position, Pareto-pruned"""
        ns = e0 - s0 + 1
        lo_f, hi_f = seg_frames(s0, e0)
        labels = [[(0, 0.0, lo_f - 1, -1, -1)]] + [[] for _ in range(ns)]
        for j in range(1, ns + 1):
            b_ = s0 + j - 1
            tail_c = 0.0 if b_ == e0 else bcost[b_]
            w1f = int(round(words[vis[b_]]['t1'] * fps))
            cands = []
            for i in range(j - 1, -1, -1):
                a_ = s0 + i
                if b_ > a_:
                    if nchar(a_, b_) > cap * (1.6 if measure else 1.0) or \
                            (max_words and b_ - a_ + 1 > max_words + 1) or \
                            words[vis[b_]]['t1'] - words[vis[a_]]['t0'] > max_dur:
                        break
                    if not fits_ab(a_, b_):
                        break                                # more words never fit better
                if not labels[i]:
                    continue
                cc = chunk_cost(a_, b_, rw, share) + tail_c
                nf = int(math.ceil(max(min_show, nchar(a_, b_) / hard_cps) * fps - 1e-6))
                w0f = int(round(words[vis[a_]]['t0'] * fps))
                for li, (v, c, e, _, _) in enumerate(labels[i]):
                    st = max(e + 1, w0f - early_f)
                    v2 = v + max(0, st - (w0f + lag_f))
                    e2 = max(st + nf - 1, w1f - cut_f)
                    if j == ns:
                        v2 += max(0, e2 - hi_f)
                    cands.append((v2, c + cc, e2, i, li))
            cands.sort(key=lambda x: (x[0], x[1], x[2]))
            keep = []
            for cd in cands:                                 # Pareto: fewer overflow frames, cost, earlier end
                if not any(k[0] <= cd[0] and k[1] <= cd[1] + 1e-9 and k[2] <= cd[2] for k in keep):
                    keep.append(cd)
            labels[j] = keep[:6] + ([min(keep, key=lambda x: (x[2], x[0], x[1]))] if len(keep) > 6 else [])
        lab = min(range(len(labels[ns])), key=lambda q: (labels[ns][q][0], labels[ns][q][1]))
        cuts, j = [], ns
        while j > 0:
            _, _, _, i, li = labels[j][lab]
            cuts.append([s0 + i, s0 + j - 1])
            j, lab = i, li
        return cuts[::-1]

    def greedy_groups(s0, e0):                               # fill each chunk (the fallback for a dense passage)
        out, start = [], s0
        for i in range(s0 + 1, e0 + 2):
            if i == e0 + 1:
                out.append([start, e0])
                break
            prev, w = words[vis[i - 1]], words[vis[i]]
            hard = not text_fit(toks[start:i + 1])[0] or w['t1'] - words[vis[start]]['t0'] > max_dur
            brk = hard or bool(max_words and i - start >= max_words) or \
                (sent[i - 1] and (kind == 'karaoke' or i - start >= 3 or not starts[start] or
                                  prev['t1'] - words[vis[start]]['t0'] >= max(min_dur, 0.8)))
            if brk:
                j = i - 1                                    # do not end a chunk on a function word / bare number
                while j > start and glue[j]:
                    j -= 1
                if glue[j]:
                    if not hard:
                        continue
                    j = i - 1
                out.append([start, j])
                start = j + 1
        return out
    groups = [g for a_, b_ in segs for g in dp_groups(a_, b_)]
    # chunk records: shown visible indices (into vis), time span (incl. hidden words before), hidden words

    def text_of(c):
        return join_words([toks[k] for k in c['show']], lg)

    def fits(show, extra=1):
        tk = [toks[k] for k in show]
        return bool(tk) and text_fit(tk)[0] and (not max_words or len(tk) <= max_words + extra)

    def span(c):
        ids = [vis[k] for k in c['show']] + c['hid']
        return min(words[i]['t0'] for i in ids), max(words[i]['t1'] for i in ids)

    # ---- 3. timing: spans, gaps, needs (relaxed = the ed_qa limits only, for passages too dense for the targets)
    relax = [False]

    def need(c):
        if relax[0]:
            return max(min_show, len(text_of(c)) / hard_cps)
        return max(min_dur, min_show, len(text_of(c)) / float(max_cps))

    def lay_out(chs):
        relax[0] = False
        S, E = _lay(chs)
        if any(bad(chs, S, E, i) for i in range(len(chs))):
            relax[0] = True
            S2, E2 = _lay(chs)
            if sum(bad(chs, S2, E2, i) for i in range(len(chs))) < sum(bad(chs, S, E, i) for i in range(len(chs))):
                return S2, E2
            relax[0] = False
        return S, E

    def _lay(chs):
        sp = [span(c) for c in chs]
        S = [max(0.0, a - lead_s) for a, _ in sp]
        E = [b + tail_s for _, b in sp]
        lo_b = [max([b for b in brk_t if b <= a] or [0.0]) for a, _ in sp]        # chunk stays between breaks
        hi_b = [min([b for b in brk_t if b >= e] or [1e9]) for _, e in sp]
        S = [max(x, lb) for x, lb in zip(S, lo_b)]
        E = [min(x, hb) for x, hb in zip(E, hi_b)]
        # lead / tail do not run over a soft break (camera cut); the reading time below still may
        S = [max(x, max([b for b in soft_t if b <= a + 1e-6] or [-1e9])) for x, (a, _) in zip(S, sp)]
        E = [min(x, min([b for b in soft_t if b >= e - 1e-6] or [1e9])) for x, (_, e) in zip(E, sp)]
        for i in range(1, len(chs)):                         # no overlap; small gaps bridged (no blinking)
            cut = [b for b in soft_t if sp[i - 1][1] - 1e-6 <= b <= sp[i][0] + 1e-6]
            if cut and E[i - 1] <= cut[0] + 1e-6 and S[i] >= cut[0] - 1e-6 and S[i] - E[i - 1] <= bridge:
                E[i - 1] = S[i] = cut[0]                     # the chunks change on the camera cut
            elif E[i - 1] > S[i]:
                mid = min(max((sp[i - 1][1] + sp[i][0]) / 2, sp[i - 1][1]), sp[i][0])
                E[i - 1] = S[i] = max(S[i - 1] + 1.0 / fps, mid)
            elif S[i] - E[i - 1] <= bridge:
                if hi_b[i - 1] <= S[i]:                      # a break in the gap: the next one starts on it
                    S[i] = max(lo_b[i], E[i - 1])
                else:
                    E[i - 1] = S[i]
        for i, c in enumerate(chs):                          # min duration: pause after, then before the words
            want = need(c)
            nxt = min(S[i + 1] if i + 1 < len(chs) else E[i] + 3.0, hi_b[i])
            if E[i] - S[i] < want:
                E[i] = max(E[i], min(nxt, S[i] + want))
            if E[i] - S[i] < want:
                prv = E[i - 1] if i else 0.0
                S[i] = max(prv, sp[i][0] - max_early, E[i] - want, 0.0, lo_b[i])
        for i, c in enumerate(chs):                          # borrow from a neighbour with time to spare
            want = need(c)
            short = want - (E[i] - S[i])
            if short <= 1e-6:
                continue
            if i + 1 < len(chs) and abs(E[i] - S[i + 1]) < 1e-6:
                # the next chunk may also run on into the pause after it, which frees time at its start
                ext = min(S[i + 2] if i + 2 < len(chs) else E[i + 1] + 3.0, hi_b[i + 1])
                spare = (ext - S[i + 1]) - need(chs[i + 1])
                room = sp[i + 1][0] + max_lag - S[i + 1]
                take = max(0.0, min(short, spare, room, hi_b[i] - E[i]))
                E[i] += take
                S[i + 1] += take
                E[i + 1] = min(ext, max(E[i + 1], S[i + 1] + need(chs[i + 1])))
                short -= take
            if short > 1e-6 and i > 0 and abs(S[i] - E[i - 1]) < 1e-6:
                spare = (E[i - 1] - S[i - 1]) - need(chs[i - 1])
                room = E[i - 1] - (sp[i - 1][1] - 0.12)            # may go 0.12 s before its last word ends
                take = max(0.0, min(short, spare, room, S[i] - lo_b[i]))
                S[i] -= take
                E[i - 1] -= take
        return S, E

    def bad(chs, S, E, i):
        d_ = E[i] - S[i]
        return d_ < min_show - 1e-6 or len(text_of(chs[i])) / max(d_, 1e-6) > hard_cps + 1e-6

    def plan_chunks(groups):
        """steps 2 and 4 on a chunking -> (chunks, S, E)"""
        ch = [dict(show=list(range(a, b + 1)), hid=[]) for a, b in groups]
        lay_out.skip = set()
        # ---- 2. filler-only chunks join a neighbour (or give their time to the next chunk, unshown)
        if fillers != 'keep':
            k = 0
            while k < len(ch):
                c = ch[k]
                if c['show'] and all(soft[vis[x]] for x in c['show']) and len(ch) > 1:
                    a0, a1 = span(c)
                    nxt_ok = k + 1 < len(ch) and span(ch[k + 1])[0] - a1 <= 0.8 and \
                        fits(c['show'] + ch[k + 1]['show']) and not crosses(a1, span(ch[k + 1])[0])
                    prv_ok = k > 0 and a0 - span(ch[k - 1])[1] <= 0.8 and fits(ch[k - 1]['show'] + c['show']) \
                        and not crosses(span(ch[k - 1])[1], a0)
                    if nxt_ok:
                        ch[k + 1]['show'] = c['show'] + ch[k + 1]['show']
                        ch[k + 1]['hid'] += c['hid']
                    elif prv_ok:
                        ch[k - 1]['show'] += c['show']
                        ch[k - 1]['hid'] += c['hid']
                    else:
                        tgt = ch[k + 1] if k + 1 < len(ch) and span(ch[k + 1])[0] - a1 <= 0.8 and \
                            not crosses(a1, span(ch[k + 1])[0]) else \
                            (ch[k - 1] if k > 0 and not crosses(span(ch[k - 1])[1], a0) else None)
                        if tgt is None:
                            k += 1
                            continue
                        tgt['hid'] += [vis[x] for x in c['show']] + c['hid']
                    del ch[k]
                    continue
                k += 1
        # hesitations right before a chunk count for its time span (unshown)
        for c in ch:
            first = vis[c['show'][0]] if c['show'] else None
            j = (first - 1) if first is not None else -1
            while j >= 0 and hes[j] and not crosses(words[j]['t1'], words[first]['t0']):
                c['hid'].append(j)
                j -= 1
        # ---- 4. still too fast / too short: merge with a neighbour whose text fits, else drop discourse fillers
        S, E = lay_out(ch)
        for _ in range(3 * len(ch) + 3):
            idx = [i for i in range(len(ch)) if bad(ch, S, E, i) and i not in getattr(lay_out, 'skip', set())]
            if not idx:
                break
            i = idx[0]
            opts = []
            for j in (i - 1, i + 1):
                if 0 <= j < len(ch):
                    a, b = (j, i) if j < i else (i, j)
                    if fits(ch[a]['show'] + ch[b]['show'], 2) and \
                            span(ch[b])[0] - span(ch[a])[1] < max(split_pause, 0.6) and \
                            not crosses(span(ch[a])[1], span(ch[b])[0]):
                        opts.append((span(ch[b])[0] - span(ch[a])[1], a, b))
            if opts:
                _, a, b = min(opts)
                ch[a] = dict(show=ch[a]['show'] + ch[b]['show'], hid=ch[a]['hid'] + ch[b]['hid'])
                del ch[b]
                S, E = lay_out(ch)
                continue
            # move one word across the boundary with a neighbour when that leaves fewer bad chunks (every word stays
            # shown): "Who do you think | that was?" -> "Who do you | think that was?"
            nbad = sum(bad(ch, S, E, k) for k in range(len(ch)))
            best = None
            for j in (i - 1, i + 1):
                if not 0 <= j < len(ch):
                    continue
                a, b = (j, i) if j < i else (i, j)
                A, B = ch[a]['show'], ch[b]['show']
                wa, wb = vis[A[-1]], vis[B[0]]
                if crosses(words[wa]['t1'], words[wb]['t0']) or \
                        any(wa < x < wb for x in ch[a]['hid'] + ch[b]['hid']):
                    continue
                for A2, B2 in ((A[:-1], [A[-1]] + B), (A + [B[0]], B[1:])):
                    if not A2 or not B2 or glue[A2[-1]] or not fits(A2) or not fits(B2):
                        continue
                    trial = list(ch)
                    trial[a], trial[b] = dict(ch[a], show=A2), dict(ch[b], show=B2)
                    S2, E2 = lay_out(trial)
                    key = (sum(bad(trial, S2, E2, k) for k in range(len(trial))), bcost[A2[-1]])
                    if key[0] < nbad and (best is None or key < best[0]):
                        best = (key, trial, S2, E2)       # the fewest failing chunks, then the best break
            if best is not None:
                ch[:] = best[1]
                S, E = best[2], best[3]
                continue
            fixed = False
            for j in (i, i - 1, i + 1):                          # own discourse fillers first, then a neighbour's
                if fillers == 'keep' or not 0 <= j < len(ch):
                    continue
                c = ch[j]
                drop = [x for x in c['show'] if soft[vis[x]]]
                if drop and len(drop) < len(c['show']):
                    c['hid'] += [vis[x] for x in drop]
                    c['show'] = [x for x in c['show'] if x not in drop]
                    S, E = lay_out(ch)
                    fixed = True
                    break
            if not fixed:
                bad_skip = getattr(lay_out, 'skip', set())
                bad_skip.add(i)
                lay_out.skip = bad_skip
                if all(k in bad_skip for k in range(len(ch)) if bad(ch, S, E, k)):
                    break
        return ch, S, E

    def finalize(ch, S, E):
        """step 5: frames, layers, reading-time repair in frames -> layers"""
        # ---- 5. layers
        layers, lims = [], []
        for c, a_t, b_t in zip(ch, S, E):
            shown = [vis[k] for k in c['show']]
            text = text_of(c)
            w_a, w_b = span(c)
            f0 = int(round(a_t * fps))
            f1 = max(f0, int(round(b_t * fps)) - 1)
            lb = max([b for b in brk_t if b <= w_a] or [None], key=lambda v: -1e18 if v is None else v)
            hb = min([b for b in brk_t if b >= w_b] or [None], key=lambda v: 1e18 if v is None else v)
            if lb is not None:                                   # frames never reach across a break
                f0 = max(f0, int(math.ceil(lb * fps - 1e-3)))
            if hb is not None:
                f1 = max(f0, min(f1, int(math.ceil(hb * fps - 1e-3)) - 1))
            if layers and f0 <= layers[-1]['f1']:
                layers[-1]['f1'] = max(layers[-1]['f0'], f0 - 1)
            lims.append((int(math.ceil(lb * fps - 1e-3)) if lb is not None else 0,
                         int(math.ceil(hb * fps - 1e-3)) - 1 if hb is not None else 10 ** 9))
            cw = [words[i] for i in shown]
            stoks = [toks[k] for k in c['show']]
            L = dict(kind=kind, f0=f0, f1=f1, t0=round(a_t, 3), t1=round(b_t, 3), text=text,
                     lines=text_fit(stoks)[1] if not rules.get('cjk') else [text],
                     words=[dict(w=w['w'], t0=round(w['t0'], 3), t1=round(w['t1'], 3)) for w in cw], lang=lg,
                     lead=f0 - int(round(cw[0]['t0'] * fps)), tail=0,
                     chunk=dict(max_chars=999, max_lines=max_lines, max_dur=1e9, max_words=None, break_on_pause=1e9,
                                min_dur=0, cps_max=0, gap_min=0, join_gap=None, split_on_cut=None, punct_break=False))
            if c['hid']:
                L['hidden'] = [words[i]['w'] for i in sorted(set(c['hid']))]
            if kind == 'karaoke':
                L.update(switch_lead=-int(word_lead), min_on=int(min_on))
            for key, val in (('style', style), ('pos', pos), ('highlight', highlight)):
                if val is not None:
                    L[key] = val
            layers.append(L)
        # rounding to frames (and dense runs) may leave a chunk short of its reading time by a few frames: free them
        # one at a time after it, else before it - from a gap or a neighbour with frames to spare, pushing a run of
        # touching chunks when needed (same limits as the layout: breaks, max_early, max_lag, 0.12 s before a last word)
        early_f, lag_f, cut_f = int(max_early * fps + 1e-6), int(max_lag * fps + 1e-6), int(0.12 * fps + 1e-6)

        def need_f(L):
            return int(math.ceil(max(min_show, len(L['text']) / hard_cps) * fps - 1e-6))

        def word_f(L, last=False):
            return int(round((L['words'][-1]['t1'] if last else L['words'][0]['t0']) * fps))

        def at(plan, j, key):
            return layers[j][key] + plan.get((j, key), 0)

        def free_after(j, plan):                                 # the frame after chunk j becomes free
            f1 = at(plan, j, 'f1')
            if f1 + 1 > lims[j][1]:
                return False
            if j + 1 == len(layers) or at(plan, j + 1, 'f0') > f1 + 1:
                return True
            nf0, nf1 = at(plan, j + 1, 'f0'), at(plan, j + 1, 'f1')
            if nf0 + 1 > word_f(layers[j + 1]) + lag_f:
                return False
            plan[(j + 1, 'f0')] = plan.get((j + 1, 'f0'), 0) + 1
            if nf1 - nf0 >= need_f(layers[j + 1]):
                return True
            if not free_after(j + 1, plan):
                return False
            plan[(j + 1, 'f1')] = plan.get((j + 1, 'f1'), 0) + 1
            return True

        def free_before(j, plan):                                # the frame before chunk j becomes free
            f0 = at(plan, j, 'f0')
            if f0 - 1 < max(lims[j][0], 0, word_f(layers[j]) - early_f):
                return False
            if j == 0 or at(plan, j - 1, 'f1') < f0 - 1:
                return True
            pf0, pf1 = at(plan, j - 1, 'f0'), at(plan, j - 1, 'f1')
            if pf1 - 1 < word_f(layers[j - 1], True) - cut_f:
                return False
            plan[(j - 1, 'f1')] = plan.get((j - 1, 'f1'), 0) - 1
            if pf1 - pf0 >= need_f(layers[j - 1]):
                return True
            if not free_before(j - 1, plan):
                return False
            plan[(j - 1, 'f0')] = plan.get((j - 1, 'f0'), 0) - 1
            return True
        for i, L in enumerate(layers):
            if not L.get('words'):
                continue
            for _ in range(need_f(L) - (L['f1'] - L['f0'] + 1)):
                pl = {}
                if free_after(i, pl):
                    pl[(i, 'f1')] = pl.get((i, 'f1'), 0) + 1
                else:
                    pl = {}
                    if not free_before(i, pl):
                        break
                    pl[(i, 'f0')] = pl.get((i, 'f0'), 0) - 1
                for (j, key), dv in pl.items():
                    layers[j][key] += dv
        for L in layers:
            if (int(round(L['t0'] * fps)), max(int(round(L['t0'] * fps)), int(round(L['t1'] * fps)) - 1)) != \
                    (L['f0'], L['f1']):                          # moved above: times follow the frames
                L['t0'], L['t1'] = round(L['f0'] / fps, 3), round((L['f1'] + 1) / fps, 3)
        return layers

    def frame_bad(layers):
        return [i for i, L in enumerate(layers)
                if (L['f1'] - L['f0'] + 1) / fps < min_show - 1e-6 or
                len(L['text']) / ((L['f1'] - L['f0'] + 1) / fps) > hard_cps + 1e-6]
    ch, S, E = plan_chunks(groups)
    layers = finalize(ch, S, E)
    worst = frame_bad(layers)
    if worst:
        # the reading rules are hard: a forced segment that still holds a failing chunk is chunked again for time
        # (strong reading weight, whole pauses), then filled greedily, then the whole text is filled greedily; a
        # version is kept when fewer chunks fail
        alts = [lambda a_, b_: dp_groups(a_, b_, 10000.0, 1.0), greedy_groups, None]
        for alt in alts:
            bad_tok = {k for i in worst for k in ch[i]['show']}
            redo = segs if alt is None else [sg for sg in segs if any(sg[0] <= k <= sg[1] for k in bad_tok)]
            fill = greedy_groups if alt is None else alt
            g2 = sorted([g for g in groups if not any(sg[0] <= g[0] <= sg[1] for sg in redo)] +
                        [g for sg in redo for g in fill(*sg)])
            ch2, S2, E2 = plan_chunks(g2)
            layers2 = finalize(ch2, S2, E2)
            worst2 = frame_bad(layers2)
            if len(worst2) < len(worst):
                groups, ch, layers, worst = g2, ch2, layers2, worst2
            if not worst:
                break

    try:                                                     # a chunk the preset cannot show at full size is
        import ed_text as _Tx                                # split in time by ed_text: make that explicit here
        _fit = getattr(_Tx, 'fit_caption_layers', None)
    except Exception:
        _fit = None
    if _fit is not None:
        out = []
        for L in layers:                                     # the parts stay inside the chunk's frames (breaks,
            try:                                             # neighbours), else the chunk stays whole
                parts = [dict(P) for P in (_fit([L], cv[0], cv[1], fps) or [L])]
            except Exception:
                parts = [L]
            if len(parts) > 1:
                parts[0]['f0'] = max(int(parts[0]['f0']), L['f0'])
                parts[-1]['f1'] = min(int(parts[-1]['f1']), L['f1'])
                for a_, b_ in zip(parts, parts[1:]):
                    a_['f1'] = min(int(a_['f1']), int(b_['f0']) - 1)
                if any(P['f0'] > P['f1'] or P['f0'] < L['f0'] or P['f1'] > L['f1'] for P in parts):
                    parts = [L]
            out += parts
        layers = out
    for L in layers:                                         # tail / cps / warnings of the final layers
        if L.get('words'):
            L['lead'] = L['f0'] - int(round(L['words'][0]['t0'] * fps))
            L['tail'] = L['f1'] - int(round(L['words'][-1]['t1'] * fps))
        else:                                                # a split part without word times: no stale values
            L.pop('lead', None)
            L.pop('tail', None)
        dur = (L['f1'] - L['f0'] + 1) / fps
        L['cps'] = round(len(L['text']) / dur, 1)
        L.pop('warn', None)
        L.setdefault('lang', lg)
        warn = []
        if L['cps'] > hard_cps + 0.05:
            warn.append(f'reading speed {L["cps"]} cps > {hard_cps:g}')
        if dur < min_show - 1e-6:
            warn.append(f'on screen {dur:.2f} s < {min_show:g}')
        if (not text_fit([t for t in L['text'].split()])[0] if measure else
                any(len(x) > max_chars for x in L['lines'])):
            warn.append(f'line > {max_chars} chars' if not measure else 'lines wider than the preset allows')
        if warn:
            L['warn'] = '; '.join(warn)
    return layers


def chunks_layer(chunks, kind='subtitle', fps=30, **extra):
    """chunk dicts with text + t0/t1 (e.g. a translation) -> ONE ed_text subtitle layer using its explicit
    `chunks` path (no per-word timing, so no karaoke)."""
    out = []
    for c in chunks:
        if not str(c.get('text', '')).strip():
            continue
        f0 = c.get('f0', int(round(c['t0'] * fps)))
        f1 = c.get('f1', max(f0, int(round(c['t1'] * fps)) - 1))
        out.append(dict(text=c['text'], t0=c['t0'], t1=c['t1'], f0=f0, f1=f1))
    if not out:
        return None
    return dict(kind=kind, f0=out[0]['f0'], f1=out[-1]['f1'], chunks=out, lead=0, tail=0, **extra)


def _as_chunks(src, **kw):
    if isinstance(src, dict) and 'chunks' in src and 'words' not in src:
        src = src['chunks']
    if isinstance(src, dict):
        return subtitle_chunks(src, **kw)
    src = list(src)
    if src and 'text' in src[0]:
        return src
    return subtitle_chunks(src, **kw)


def _srt_tc(t):
    ms = int(round(max(0.0, t) * 1000))
    return f'{ms // 3600000:02d}:{ms // 60000 % 60:02d}:{ms // 1000 % 60:02d},{ms % 1000:03d}'


def to_srt(src, path=None, **kw):
    """chunks/layers (or words/transcript -> subtitle_chunks(**kw)) -> SRT text (written to path if given)."""
    cues = []
    for i, c in enumerate(_as_chunks(src, **kw), 1):
        lines = c.get('lines') or [c['text']]
        cues.append(f'{i}\n{_srt_tc(c["t0"])} --> {_srt_tc(c["t1"])}\n' + '\n'.join(lines) + '\n')
    s = '\n'.join(cues)
    if path:
        Path(path).write_text(s, encoding='utf-8')
    return s


def _ass_tc(t):
    cs = int(round(max(0.0, t) * 100))
    return f'{cs // 360000}:{cs // 6000 % 60:02d}:{cs // 100 % 60:02d}.{cs % 100:02d}'


def _ass_col(hexcol, alpha=0):
    h = hexcol.lstrip('#')
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return f'&H{alpha:02X}{b:02X}{g:02X}{r:02X}'


def to_ass(src, path=None, canvas=(1080, 1920), font='Montserrat', size=0.046, color='#FFFFFF', active='#FFE14A',
           outline='#000000', outline_w=0.1, pos=None, karaoke=None, bold=True, word_lead=1 / 30, **kw):
    """ASS export (libass / ffmpeg `subtitles=...:fontsdir=engine/assets/fonts`). Karaoke chunks become one event
    per sounding word with that word in `active` colour. size: fraction of H or px; pos (x, y) fractions."""
    W, H = canvas
    chunks = _as_chunks(src, **kw)
    if karaoke is None:
        karaoke = bool(chunks) and chunks[0].get('kind') == 'karaoke'
    px = size * H if size <= 1 else size
    pos = pos or ((0.47, 0.67) if H > W else (0.5, 0.86))
    x, y = int(pos[0] * W), int(pos[1] * H)
    head = ['[Script Info]', 'ScriptType: v4.00+', f'PlayResX: {W}', f'PlayResY: {H}', 'WrapStyle: 2',
            'ScaledBorderAndShadow: yes', '', '[V4+ Styles]',
            'Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, '
            'Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, '
            'MarginL, MarginR, MarginV, Encoding',
            f'Style: Default,{font},{px:.0f},{_ass_col(color)},{_ass_col(active)},{_ass_col(outline)},'
            f'{_ass_col("#000000", 0x80)},{-1 if bold else 0},0,0,0,100,100,0,0,1,{px * outline_w:.1f},0,5,40,40,0,1',
            '', '[Events]', 'Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text']
    esc = lambda s: s.replace('{', '(').replace('}', ')').replace('\\', '/')  # noqa: E731
    ev = []
    for c in chunks:
        lines = c.get('lines') or [c['text']]
        if not karaoke or not c.get('words'):
            ev.append(f'Dialogue: 0,{_ass_tc(c["t0"])},{_ass_tc(c["t1"])},Default,,0,0,0,,{{\\pos({x},{y})}}'
                      + '\\N'.join(esc(l) for l in lines))
            continue
        toks = [w['w'].strip() for w in c['words']]
        per_line, k = [], 0                                   # map words to lines by token count
        for l in lines:
            n = len(l.split())
            per_line.append(list(range(k, k + n)))
            k += n
        starts = [max(c['t0'], w['t0'] - word_lead) for w in c['words']]
        bounds = [c['t0']] + starts[1:] + [c['t1']]
        if starts[0] > c['t0'] + 0.01:                      # chunk shown before its first word: no highlight yet
            ev.append(f'Dialogue: 0,{_ass_tc(c["t0"])},{_ass_tc(starts[0])},Default,,0,0,0,,{{\\pos({x},{y})}}'
                      + '\\N'.join(esc(l) for l in lines))
            bounds[0] = starts[0]
        for j in range(len(toks)):
            a, b = bounds[j], bounds[j + 1]
            if b <= a:
                continue
            parts = []
            for idx in per_line:
                parts.append(' '.join((f'{{\\c{_ass_col(active)}}}{esc(toks[i])}{{\\c{_ass_col(color)}}}' if i == j
                                       else esc(toks[i])) for i in idx if i < len(toks)))
            ev.append(f'Dialogue: 0,{_ass_tc(a)},{_ass_tc(b)},Default,,0,0,0,,{{\\pos({x},{y})}}' + '\\N'.join(parts))
    s = '\n'.join(head + ev) + '\n'
    if path:
        Path(path).write_text(s, encoding='utf-8')
    return s


# ----------------------------------------------------------------------------------------------- translation
def _lang_code(x):
    """'en' | 'eng' (Higgsfield) | 'fil' | 'English' -> 2-letter code used by LANG_RULES / whisper."""
    x = str(x).strip().lower()
    if x in LANG_RULES:
        return x
    inv = {v: k for k, v in HF_DUB_LANG.items() if k != 'fil'}
    if x in inv:
        return inv[x]
    # language names -> codes (the two Cyrillic names are language data: Russian names of Russian and English)
    names = {'english': 'en', 'russian': 'ru', 'русский': 'ru', 'английский': 'en', 'german': 'de', 'french': 'fr',
             'spanish': 'es', 'italian': 'it', 'portuguese': 'pt', 'chinese': 'zh', 'japanese': 'ja', 'korean': 'ko',
             'turkish': 'tr', 'polish': 'pl', 'arabic': 'ar', 'hindi': 'hi', 'swedish': 'sv', 'finnish': 'fi',
             'indonesian': 'id', 'filipino': 'tl', 'ukrainian': 'uk'}
    return names.get(x, x[:2])


def _sentences(words, max_dur=10.0, pause=0.6):
    """word index groups = sentences/clauses: sentence punctuation, pauses >= `pause`, or max_dur (split at the
    last comma, else at the largest pause)."""
    groups, start = [], 0
    for i in range(1, len(words) + 1):
        end = i == len(words)
        if not end:
            prev, w = words[i - 1], words[i]
            brk = w['t0'] - prev['t1'] >= pause or bool(re.search(r'[.!?…。！？]["»”)]*$', prev['w']))
            if not brk and w['t1'] - words[start]['t0'] > max_dur:
                commas = [j for j in range(start, i) if re.search(r'[,;:—–]$', words[j]['w'])]
                j = commas[-1] if commas else max(range(start, i), key=lambda j: words[j + 1]['t0'] - words[j]['t1'])
                groups.append((start, j))
                start = j + 1
                continue
        if end or brk:
            groups.append((start, i - 1))
            start = i
    return [g for g in groups if g[0] <= g[1]]


def translate_plan(src, target_lang, src_lang=None, fps=30, vertical=True, max_lines=2, max_sentence=10.0):
    """Structure Claude fills in chat. Chunks are whole sentences/clauses of the source (a translation needs the
    complete thought) with timing and a character budget for the target language (reading speed x available
    time). Fill plan["chunks"][i]["target"], then apply_translation(plan): it re-segments every translated
    sentence into subtitle chunks (<= max_lines x line_chars), splitting time at source word boundaries.
    Use output-time words (remap_words) if the subtitles go on a cut edit."""
    tl = _lang_code(target_lang)
    if isinstance(src, dict):
        src_lang = src_lang or src.get('lang')
    words = [w for w in _words_of(src) if w.get('t0') is not None and str(w.get('w', '')).strip()]
    sl = _lang_of(words, src_lang)
    rules = LANG_RULES.get(tl, dict(cps=15, line=42, line_v=20, expand=1.15))
    line = rules['line_v'] if vertical else rules['line']
    exp = rules['expand'] / LANG_RULES.get(sl, {'expand': 1.0})['expand']
    groups = _sentences(words, max_dur=max_sentence)
    out = []
    for i, (a, b) in enumerate(groups):
        t0, t1 = words[a]['t0'], words[b]['t1']
        nxt = words[groups[i + 1][0]]['t0'] if i + 1 < len(groups) else t1 + 1.5
        room = max(t1 - t0, min(nxt, t1 + 1.0) - t0)          # may grow up to 1 s into the following pause
        text = join_words([w['w'] for w in words[a:b + 1]], sl)
        out.append(dict(i=i, t0=round(t0, 3), t1=round(t1, 3), dur=round(t1 - t0, 2), src=text,
                        max_chars=int(rules['cps'] * room), est_chars=int(len(text) * exp), target='',
                        w0=a, w1=b))
    tight = [c['i'] for c in out if c['est_chars'] > c['max_chars']]
    return dict(src_lang=sl, target_lang=tl, dub_code=HF_DUB_LANG.get(tl), fps=fps, vertical=vertical,
                max_lines=max_lines, line_chars=line, rules=rules, chunks=out, tight=tight,
                words=[[round(w['t0'], 3), round(w['t1'], 3), len(w['w'])] for w in words],
                how=('Translate each chunk["src"] (a whole sentence) into chunk["target"] as natural spoken ' + tl +
                     ', meaning first, <= max_chars (reading speed x time). For chunks listed in `tight`, condense '
                     '(drop fillers and repetitions, shorter synonyms, numbers as digits). Keep names and brands. '
                     'Do not merge sentences. Then apply_translation(plan) -> subtitle layer + issues.'))


def _split_text(text, cap, cjk=False):
    """split a translated sentence into pieces <= cap chars, balanced, preferring breaks after punctuation."""
    if len(text) <= cap:
        return [text]
    if cjk:
        k = math.ceil(len(text) / cap)
        n = math.ceil(len(text) / k)
        return [text[i:i + n] for i in range(0, len(text), n)]
    toks = text.split()
    k = math.ceil(len(text) / cap)
    pieces, start = [], 0
    for j in range(1, k):
        target = len(text) * j / k
        best, bc = None, None
        pos = 0
        for t in range(len(toks)):
            pos += len(toks[t]) + 1
            if t < start or t >= len(toks) - 1:
                continue
            cost = abs(pos - target) - (cap * 0.25 if re.search(r'[,.;:!?…—–]$', toks[t]) else 0) \
                + (cap * 0.3 if norm_word(toks[t]) in WEAK_END['ru'] | WEAK_END['en'] else 0)
            if len(' '.join(toks[start:t + 1])) <= cap and (bc is None or cost < bc):
                best, bc = t, cost
        if best is None:
            break
        pieces.append(' '.join(toks[start:best + 1]))
        start = best + 1
    pieces.append(' '.join(toks[start:]))
    return [p for p in pieces if p]


def apply_translation(plan, translations=None, kind='subtitle', extend=True, max_dur=6.0):
    """Filled plan (or translations as a list / {i: text}) -> {"layer": ed_text subtitle layer (explicit chunks),
    "chunks": [{t0, t1, text, lines, cps, i}], "issues": [...]}. Long sentences are re-segmented into subtitle
    chunks; time is split where the same fraction of the source sentence was spoken."""
    fps, rules = plan['fps'], plan['rules']
    line, max_lines = plan['line_chars'], plan['max_lines']
    cap = line * max_lines
    W = plan.get('words') or []
    res, issues = [], []
    for k, c in enumerate(plan['chunks']):
        t = c.get('target', '')
        if translations is not None:
            t = translations[k] if isinstance(translations, list) else translations.get(k, translations.get(str(k), t))
        t = ' '.join(str(t or '').split())
        if not t:
            issues.append(dict(i=k, issue='empty translation'))
            continue
        pieces = _split_text(t, cap, rules.get('cjk'))
        while len(pieces) > 1 and (c['t1'] - c['t0']) / len(pieces) < 0.7:   # too little time per piece
            pieces = _split_text(t, int(cap * 1.25) + 1, rules.get('cjk'))
            cap = int(cap * 1.25) + 1
        cap = line * max_lines
        src_w = W[c['w0']:c['w1'] + 1] if W and 'w0' in c else []
        tot_t = sum(len(p) for p in pieces)
        bounds, acc = [c['t0']], 0
        tot_s = sum(x[2] for x in src_w)
        for p in pieces[:-1]:
            acc += len(p)
            f = acc / tot_t
            if src_w:                                        # same fraction of the source sentence -> word start
                cum, tb = 0, src_w[-1][0]
                for x in src_w:
                    if cum >= f * tot_s:
                        tb = x[0]
                        break
                    cum += x[2]
            else:
                tb = c['t0'] + f * (c['t1'] - c['t0'])
            bounds.append(min(max(tb, bounds[-1] + 0.5), c['t1'] - 0.3))
        bounds.append(c['t1'])
        nxt = plan['chunks'][k + 1]['t0'] if k + 1 < len(plan['chunks']) else c['t1'] + 1.5
        for j, p in enumerate(pieces):
            t0, t1 = bounds[j], bounds[j + 1]
            if j == len(pieces) - 1 and extend and len(p) / max(t1 - t0, 1e-6) > rules['cps']:
                t1 = max(t1, min(nxt - 2.0 / fps, t0 + len(p) / rules['cps'], t0 + max_dur))
            cps = len(p) / max(t1 - t0, 1e-6)
            lines = [p] if rules.get('cjk') else break_lines(p.split(), line, max_lines)
            d = dict(i=k, t0=round(t0, 3), t1=round(t1, 3), text=p, lines=lines, cps=round(cps, 1))
            if cps > rules['cps'] + 0.05:
                fit = int(rules['cps'] * (t1 - t0))
                issues.append(dict(i=k, piece=j, issue=f'{cps:.1f} cps > {rules["cps"]}: shorten to ~{fit} chars'))
            if len(lines) > max_lines or any(len(x) > line for x in lines):
                issues.append(dict(i=k, piece=j, issue=f'does not fit {max_lines} x {line} chars'))
            res.append(d)
    return dict(layer=chunks_layer(res, kind=kind, fps=fps, lang=plan['target_lang']), chunks=res, issues=issues)


# ----------------------------------------------------------------------------------------------- QA, dubbing
def speech_qa(words_out, layers=None, cuts=None, fps=30, max_pause=0.35, allowed_pauses=(), first_word_max=0.3,
              max_cps=20.0, edge=1, remap_issues=None):
    """Speech checks for ed_qa / the genre cards (qa_first_word, qa_pauses, qa_word_cuts, qa_reading_speed):
    words_out are OUTPUT-time words and remap_issues the second value of remap_words (cuts inside source words);
    cuts: output frames where a new shot starts. Returns counts + offending items."""
    w = sorted(_words_of(words_out), key=lambda x: x['t0'])
    res = dict(first_word=_r(w[0]['t0']) if w else None)
    res['first_word_ok'] = bool(w) and w[0]['t0'] <= first_word_max
    pauses = [dict(t0=_r(a['t1']), t1=_r(b['t0']), dur=_r(b['t0'] - a['t1'])) for a, b in zip(w, w[1:])
              if b['t0'] - a['t1'] > max_pause
              and not any(p0 <= a['t1'] and b['t0'] <= p1 for p0, p1 in allowed_pauses)]
    res['pauses'] = pauses
    wc = []
    for f in cuts or []:
        t = f / fps
        for x in w:
            if x['t0'] + edge / fps < t < x['t1'] - edge / fps:
                wc.append(dict(f=f, word=x['w']))
    wc += [dict(f=i['f'], word=i['word'], inside=i.get('inside')) for i in (remap_issues or [])]
    res['word_cuts'] = wc
    slow = [dict(f0=L['f0'], text=L['text'], cps=L.get('cps')) for L in (layers or [])
            if L.get('cps') and L['cps'] > max_cps + 0.05]
    res['reading_speed'] = slow
    res['ok'] = res['first_word_ok'] and not pauses and not wc and not slow
    return res


def dub_master(edl):
    """Copy of an EDL for the dubbing upload: picture + original voice only (music, SFX, ducking removed)."""
    import copy
    e = copy.deepcopy(edl)
    a = e.get('audio') or {}
    if a.get('copy'):
        raise ValueError('audio.copy=true muxes the reference mix - the voice cannot be isolated; '
                         'use a voice stem in audio.voice for the dub master')
    e['audio'] = dict(voice=a.get('voice', []), loudness=a.get('loudness', {'lufs': -16, 'tp': -1}))
    e.setdefault('meta', {})['scenario'] = 'dub_master'
    return e


def _probe_dur(path):
    r = subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', str(path)],
                       capture_output=True, text=True)
    try:
        return float(r.stdout.strip())
    except ValueError:
        return None


def import_dub(audio, dubbed, at=0.0, mode='replace', orig_gain_db=-16.0, gain_db=0.0, out_wav=None,
               duck_db=None):
    """Bring a Higgsfield `dubbing` result (or any dubbed/voice-over file) back into the EDL audio block.
    mode 'replace': the dub becomes audio.voice (original voice entries removed);
    'voiceover': original voice kept orig_gain_db lower under the dub. Music/SFX untouched; a duck rule
    (music under voice) is added when missing (duck_db or 12 dB). Returns (new_audio, info)."""
    import copy
    dubbed = Path(dubbed)
    wav = Path(out_wav) if out_wav else dubbed.with_name(dubbed.stem + '_voice.wav')
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-nostdin', '-i', str(dubbed), '-vn', '-ac', '2', '-ar', '48000',
                    '-c:a', 'pcm_s16le', str(wav)], check=True)
    a = copy.deepcopy(audio or {})
    orig = a.get('voice', [])
    entry = dict(path=str(wav), at=float(at), **{'in': 0.0}, dur=None, gain_db=float(gain_db), role='dub')
    if mode == 'voiceover':
        for v in orig:
            v['gain_db'] = float(v.get('gain_db', 0)) + orig_gain_db
            v['role'] = 'original_under_dub'
        a['voice'] = orig + [entry]
    else:
        a['voice'] = [entry]
    if not any(d.get('under') == 'voice' for d in a.get('duck', [])):
        a.setdefault('duck', []).append(dict(under='voice', depth_db=float(duck_db or 12), attack_ms=30,
                                             release_ms=300))
    return a, dict(wav=str(wav), dur=_probe_dur(wav), mode=mode)


def tts_lines(plan):
    """Translated plan -> lines for generate_audio / generate_audio_batch (languages without `dubbing`):
    [{"i", "at", "slot", "text"}]; slot = seconds until the next line."""
    ch = [c for c in plan['chunks'] if c.get('target')]
    return [dict(i=c['i'], at=c['t0'], slot=round((ch[k + 1]['t0'] if k + 1 < len(ch) else c['t1'] + 1.0) - c['t0'], 2),
                 text=c['target']) for k, c in enumerate(ch)]


def place_lines(audio, items, max_tempo=1.15, out_dir=None):
    """Synthesised lines [{"path", "at", "slot"}] -> audio.voice entries; a line longer than its slot is sped up
    (ffmpeg atempo <= max_tempo); still too long -> reported (re-cut the picture or shorten the text)."""
    import copy
    a = copy.deepcopy(audio or {})
    voice, issues = [], []
    for it in items:
        p = Path(it['path'])
        d = _probe_dur(p) or 0.0
        slot = float(it.get('slot') or d)
        path = p
        if d > slot > 0:
            tempo = min(max_tempo, d / slot)
            path = Path(out_dir or p.parent) / (p.stem + f'_x{tempo:.2f}.wav')
            subprocess.run(['ffmpeg', '-v', 'error', '-y', '-nostdin', '-i', str(p), '-af', f'atempo={tempo:.4f}',
                            '-ar', '48000', str(path)], check=True)
            if d / tempo > slot + 0.05:
                issues.append(dict(path=str(p), over_s=round(d / tempo - slot, 2)))
        voice.append(dict(path=str(path), at=float(it['at']), **{'in': 0.0}, dur=None, gain_db=0.0, role='tts'))
    a['voice'] = voice
    if not any(x.get('under') == 'voice' for x in a.get('duck', [])):
        a.setdefault('duck', []).append(dict(under='voice', depth_db=12.0, attack_ms=30, release_ms=300))
    return a, issues


# ----------------------------------------------------------------------------------------------- phrase search
# language data: English and Russian number words, scale words and currency/unit names. They make the phrase
# search number-format insensitive: "4 million" = "4,000,000" = "four million"; "$10,000" = "10 000 dollars".
def _fold(s):
    """lowercase, NFKC, yo -> ye, diacritics removed (same folding for the transcript and the query)."""
    s = unicodedata.normalize('NFKC', str(s)).lower().replace('ё', 'е').replace('’', "'")
    s = unicodedata.normalize('NFKD', s)
    return unicodedata.normalize('NFC', ''.join(c for c in s if unicodedata.category(c) != 'Mn'))


def _fold_keys(d):
    return {_fold(k): v for k, v in d.items()}


_NUM_UNITS = _fold_keys({
    'zero': 0, 'one': 1, 'two': 2, 'three': 3, 'four': 4, 'five': 5, 'six': 6, 'seven': 7, 'eight': 8, 'nine': 9,
    'ten': 10, 'eleven': 11, 'twelve': 12, 'thirteen': 13, 'fourteen': 14, 'fifteen': 15, 'sixteen': 16,
    'seventeen': 17, 'eighteen': 18, 'nineteen': 19,
    'ноль': 0, 'один': 1, 'одна': 1, 'одно': 1, 'одного': 1, 'одной': 1, 'два': 2, 'две': 2, 'двух': 2, 'три': 3,
    'трех': 3, 'четыре': 4, 'четырех': 4, 'пять': 5, 'пяти': 5, 'шесть': 6, 'шести': 6, 'семь': 7, 'семи': 7,
    'восемь': 8, 'восьми': 8, 'девять': 9, 'девяти': 9, 'десять': 10, 'десяти': 10, 'одиннадцать': 11,
    'двенадцать': 12, 'тринадцать': 13, 'четырнадцать': 14, 'пятнадцать': 15, 'шестнадцать': 16,
    'семнадцать': 17, 'восемнадцать': 18, 'девятнадцать': 19})
_NUM_TENS = _fold_keys({
    'twenty': 20, 'thirty': 30, 'forty': 40, 'fourty': 40, 'fifty': 50, 'sixty': 60, 'seventy': 70, 'eighty': 80,
    'ninety': 90, 'двадцать': 20, 'тридцать': 30, 'сорок': 40, 'пятьдесят': 50, 'шестьдесят': 60,
    'семьдесят': 70, 'восемьдесят': 80, 'девяносто': 90})
_NUM_HUNDREDS = _fold_keys({
    'сто': 100, 'двести': 200, 'триста': 300, 'четыреста': 400, 'пятьсот': 500, 'шестьсот': 600, 'семьсот': 700,
    'восемьсот': 800, 'девятьсот': 900})
_NUM_SCALES = _fold_keys({
    'thousand': 1e3, 'million': 1e6, 'billion': 1e9, 'trillion': 1e12,
    'тысяча': 1e3, 'тысячи': 1e3, 'тысяч': 1e3, 'тысячу': 1e3, 'миллион': 1e6, 'миллиона': 1e6, 'миллионов': 1e6,
    'миллиард': 1e9, 'миллиарда': 1e9, 'миллиардов': 1e9, 'триллион': 1e12, 'триллиона': 1e12,
    'триллионов': 1e12,
    'mln': 1e6, 'bn': 1e9, 'тыс': 1e3, 'млн': 1e6, 'млрд': 1e9, 'трлн': 1e12})
_NUM_SUFFIX = {'k': 1e3, 'm': 1e6, 'mm': 1e6, 'mn': 1e6, 'b': 1e9, 't': 1e12, 'tn': 1e12}   # only glued: "10k"
_UNIT_WORDS = _fold_keys({
    '$': 'dollar', 'usd': 'dollar', 'dollar': 'dollar', 'dollars': 'dollar', 'bucks': 'dollar',
    '€': 'euro', 'eur': 'euro', 'euros': 'euro', '£': 'pound', 'gbp': 'pound', 'pounds': 'pound',
    '%': 'percent', 'pct': 'percent', '¥': 'yen',
    '₽': 'рубль', 'руб': 'рубль', 'рубля': 'рубль', 'рублей': 'рубль', 'доллара': 'доллар', 'долларов': 'доллар',
    'процента': 'процент', 'процентов': 'процент'})
_PREFIX_UNITS = {'$', '€', '£', '₽', '¥'}
_TOKEN = re.compile(r"[$€£₽¥%]|\d+(?:[.,]\d+)*|[^\W\d_]+")


def _num_value(s):
    """'4,000,000' -> 4e6, '4.5' -> 4.5, '1,5' -> 1.5 (a comma before exactly 3 digits groups thousands)."""
    if not s[:1].isdigit():
        return None
    parts, seps = re.split(r'[.,]', s), re.findall(r'[.,]', s)
    if not seps:
        return float(s)
    if all(len(p) == 3 for p in parts[1:]) and (all(c == ',' for c in seps) or len(seps) > 1):
        return float(''.join(parts))
    return float(''.join(parts[:-1]) + '.' + parts[-1])


def _num_str(v):
    if abs(v - round(v)) < 1e-9:
        return str(int(round(v)))
    return ('%.6f' % v).rstrip('0').rstrip('.')


def _tokens(words):
    """sub-word tokens [{s, w (word index), glued (no gap to the previous token), cont (a ',000' ASR split)}]."""
    toks = []
    for wi, w in enumerate(words):
        f = _fold(w)
        cont = bool(re.match(r'^[,.]\d{3}(?!\d)', f.strip()))
        prev_end = None
        for m in _TOKEN.finditer(f):
            toks.append(dict(s=m.group(0), w=wi, glued=prev_end is not None and m.start() == prev_end,
                             cont=cont and prev_end is None))
            prev_end = m.end()
    return toks


def _parse_number(toks, i):
    """longest number phrase starting at toks[i] -> (end index, value) | (i, None)."""
    total, cur, last, j, n = 0.0, None, None, i, len(toks)
    while j < n:
        t = toks[j]
        s = t['s']
        nxt = toks[j + 1]['s'] if j + 1 < n else ''
        v = _num_value(s)
        if v is not None:
            if last is None:
                cur, last = v, 'digit'
            elif last == 'digit' and total == 0 and cur is not None and cur == int(cur) and cur < 1000 and \
                    re.fullmatch(r'\d{3}', s) and (t['cont'] or t['w'] != toks[j - 1]['w']):
                cur = cur * 1000 + v                                   # "10 000", "$10" + ",000"
            else:
                break
        elif s in _NUM_UNITS:
            u = _NUM_UNITS[s]
            if last in (None, 'scale', 'hundred', 'and') or (last == 'tens' and u < 10):
                cur, last = (cur or 0) + u, 'unit'
            else:
                break
        elif s in _NUM_TENS:
            if last in (None, 'scale', 'hundred', 'and'):
                cur, last = (cur or 0) + _NUM_TENS[s], 'tens'
            else:
                break
        elif s in _NUM_HUNDREDS:
            if last in (None, 'scale'):
                cur, last = (cur or 0) + _NUM_HUNDREDS[s], 'hundred'
            else:
                break
        elif s == 'hundred':
            if last in ('unit', 'digit', 'a', None):
                cur, last = (cur if cur is not None else 1) * 100, 'hundred'
            else:
                break
        elif s in _NUM_SCALES or (s in _NUM_SUFFIX and t['glued'] and last == 'digit'):
            if last in ('unit', 'tens', 'digit', 'hundred', 'a') or (last is None and s in _NUM_SCALES
                                                                      and len(s) > 4):
                total += (cur if cur is not None else 1) * (_NUM_SCALES.get(s) or _NUM_SUFFIX[s])
                cur, last = None, 'scale'
            else:
                break
        elif s in ('a', 'an') and last is None and (nxt in _NUM_SCALES or nxt == 'hundred'):
            cur, last = 1, 'a'
        elif s == 'and' and last in ('hundred', 'scale') and (nxt in _NUM_UNITS or nxt in _NUM_TENS):
            last = 'and'
        else:
            break
        j += 1
    if j > i and last in ('a', 'and'):
        j -= 1
    if j == i or (cur is None and total == 0 and last not in ('digit', 'unit')):
        return i, None
    return j, total + (cur or 0)


def _canon(words):
    """canonical units [(text, first word, last word)]: numbers as digits, units as words, no punctuation."""
    toks = _tokens(words)
    out, i = [], 0
    while i < len(toks):
        s = toks[i]['s']
        if s in _PREFIX_UNITS and i + 1 < len(toks):
            j, v = _parse_number(toks, i + 1)
            if v is not None:                                        # "$10,000" -> "10000" "dollar"
                out.append((_num_str(v), toks[i]['w'], toks[j - 1]['w']))
                out.append((_UNIT_WORDS[s], toks[i]['w'], toks[j - 1]['w']))
                i = j
                continue
        j, v = _parse_number(toks, i)
        if v is not None:
            out.append((_num_str(v), toks[i]['w'], toks[j - 1]['w']))
            i = j
            continue
        out.append((_UNIT_WORDS.get(s, s), toks[i]['w'], toks[i]['w']))
        i += 1
    return out


def canon_text(text):
    """the folded, number-normalised form find_phrase compares (spaces and punctuation removed)."""
    return ''.join(u[0] for u in _canon(str(text).split()))


def _myers(p, t, search=True):
    """bit-parallel edit distance (Myers / Hyyro): search=True -> best distance of p to a substring of t ending at
    each position of t; search=False -> distance of p to each prefix of t."""
    m = len(p)
    out = np.zeros(len(t), np.int32)
    if m == 0:
        return out if search else np.arange(1, len(t) + 1, dtype=np.int32)
    peq = {}
    for k, c in enumerate(p):
        peq[c] = peq.get(c, 0) | (1 << k)
    mask, hb = (1 << m) - 1, 1 << (m - 1)
    pv, mv, score = mask, 0, m
    carry = 0 if search else 1
    for j, c in enumerate(t):
        eq = peq.get(c, 0)
        xv = eq | mv
        xh = ((((eq & pv) + pv) & mask) ^ pv) | eq
        ph = mv | (~(xh | pv) & mask)
        mh = pv & xh
        if ph & hb:
            score += 1
        elif mh & hb:
            score -= 1
        ph = ((ph << 1) | carry) & mask
        mh = (mh << 1) & mask
        pv = mh | (~(xv | ph) & mask)
        mv = ph & xv
        out[j] = score
    return out


def _lev(a, b):
    if not a or not b:
        return max(len(a), len(b))
    return int(_myers(a, b, search=False)[-1])


def _phrase_score(q, s):
    return 1.0 - _lev(q, s) / max(len(q), len(s), 1)


def _span_score(q, qnums, span_words):
    """phrase similarity of a word span; a different number than the query's costs 0.35 (10,000 is not 4M)."""
    units = _canon(span_words)
    sc = _phrase_score(q, ''.join(u[0] for u in units))
    if qnums and [u[0] for u in units if u[0][:1].isdigit()] != qnums:
        sc -= 0.35
    return sc


def _snap_span(q, qnums, sub, a, b):
    """word span of a character match: a boundary word stays (or is added) only when it earns at least half of
    its own length in score - a partly matching neighbour ("Wow." for "dollars") is not part of the phrase."""
    def score(x, y):
        return _span_score(q, qnums, sub[x:y + 1])

    def wlen(k):
        return max(1, len(canon_text(sub[k])))
    cur = score(a, b)
    changed, rounds = True, 0
    while changed and rounds < 8:
        changed, rounds = False, rounds + 1
        for side in ('l', 'r'):
            if a >= b:
                break
            x, y, k = (a + 1, b, a) if side == 'l' else (a, b - 1, b)
            s2 = score(x, y)
            if cur - s2 < 0.5 * wlen(k) / max(len(q), 1):
                a, b, cur, changed = x, y, s2, True
        for side in ('l', 'r'):
            x, y, k = (a - 1, b, a - 1) if side == 'l' else (a, b + 1, b + 1)
            if 0 <= x and y < len(sub):
                s2 = score(x, y)
                if s2 - cur >= 0.5 * wlen(k) / max(len(q), 1):
                    a, b, cur, changed = x, y, s2, True
    return a, b, cur


def find_phrase_all(words, text, after=None, before=None, min_score=0.7, limit=20):
    """Every occurrence of `text` in the transcript (see find_phrase), best first:
    [{"t0", "t1", "i0", "i1", "score", "text"}]."""
    ws = _words_of(words)
    idx = sorted((i for i, w in enumerate(ws) if w.get('t0') is not None and w.get('t1') is not None
                  and (after is None or w['t0'] >= after - 0.05) and (before is None or w['t1'] <= before + 0.05)),
                 key=lambda i: ws[i]['t0'])
    qu = _canon(str(text).split())
    q = ''.join(u[0] for u in qu)
    qnums = [u[0] for u in qu if u[0][:1].isdigit()]
    if not q or not idx:
        return []
    sub = [str(ws[i].get('w', '')) for i in idx]
    units = _canon(sub)
    stream = ''.join(u[0] for u in units)
    if not stream:
        return []
    cu = np.concatenate([np.full(len(u[0]), k, np.int32) for k, u in enumerate(units)])
    m = len(q)
    kmax = int(math.floor((1.0 - min_score) * m + 1e-9))
    dist = _myers(q, stream)
    ends = []
    k = 0
    while k < len(dist):                                   # best end inside every run of acceptable distances
        if dist[k] <= kmax:
            r = k
            while r + 1 < len(dist) and dist[r + 1] <= kmax:
                r += 1
            ends.append(k + int(np.argmin(dist[k:r + 1])))
            k = r + 1
        else:
            k += 1
    seen, hits = set(), []
    for e in ends[:200]:
        span = stream[max(0, e - m - kmax):e + 1][::-1]
        d = _myers(q[::-1], span, search=False)
        best = min(range(len(d)), key=lambda L: (d[L], abs(L + 1 - m)))
        s = e - best
        u0, u1 = int(cu[s]), int(cu[e])
        a, b, sc = _snap_span(q, qnums, sub, units[u0][1], units[u1][2])
        if (a, b) in seen:
            continue
        seen.add((a, b))
        if sc >= min_score:
            i0, i1 = idx[a], idx[b]
            hits.append(dict(t0=_r(ws[i0]['t0']), t1=_r(ws[i1]['t1']), i0=i0, i1=i1, score=_r(sc),
                             text=join_words(sub[a:b + 1])))
    hits.sort(key=lambda h: (-h['score'], h['t0']))
    return hits[:limit]


def find_phrase(words, text, after=None, before=None, min_score=0.7):
    """Find a spoken phrase in a transcript: fuzzy, case/punctuation/number-format insensitive ("4 million" =
    "4,000,000" = "four million"; "$10,000" = "10 000 dollars"), tolerant to ASR splits and merges ("life style"
    = "lifestyle", "$10" ",000"). Matching runs on the canonical character stream (canon_text) with a bit-parallel
    edit distance, then snaps to whole words. after/before (seconds) restrict the search to words starting at or
    after `after` and ending by `before`. Returns {"t0", "t1", "i0", "i1", "score", "text"} for the best match
    (score = 1 - edit distance / length; ties -> earliest) or None below min_score."""
    hits = find_phrase_all(words, text, after=after, before=before, min_score=min_score, limit=1)
    return hits[0] if hits else None


# ----------------------------------------------------------------------------------------------- reactions
# language data: English and Russian interjections / one-word reactions
_DRAWN = re.compile(r'(?:(?:ha|ah|he)h?){2,}|w+h?o+a+h*|wo{2,}h*|o+h+|a+h+|h*m{2,}h*|u+h+', re.I)


def _is_interjection(tok):
    """A folded token that is a reaction word: the list below, or a drawn-out / repeated form of one (laughs,
    long "oh", "whoa", "hmm" spelled with extra letters)."""
    return tok in INTERJECTIONS or bool(_DRAWN.fullmatch(tok))


INTERJECTIONS = {_fold(w) for w in (
    'wow', 'whoa', 'oh', 'ooh', 'ah', 'aah', 'aha', 'ha', 'hah', 'haha', 'heh', 'hmm',
    'huh', 'mm', 'mhm', 'damn', 'dang', 'jeez', 'gosh', 'god', 'omg', 'nice', 'cool', 'great', 'amazing', 'awesome',
    'incredible', 'insane', 'crazy', 'really', 'seriously', 'yeah', 'yes', 'yep', 'no', 'nope', 'right', 'okay',
    'ok', 'what', 'way', 'my', 'holy', 'shit', 'fuck', 'man', 'dude', 'yikes', 'oof', 'ouch', 'unbelievable',
    'вау', 'ого', 'ух', 'ты', 'ах', 'ох', 'ой', 'ха', 'хаха', 'ахах', 'ахаха', 'хм', 'ну', 'да', 'нет', 'круто',
    'класс', 'жесть', 'офигеть', 'обалдеть', 'серьезно', 'правда', 'блин', 'ничего', 'себе', 'капец', 'ужас')}


def _voice_env(audio, sr=SR, hop=0.01, lo=150.0, hi=4000.0):
    """voice-band energy envelope in dB, one value per `hop` seconds (32 ms Hann frames)."""
    n = 512
    h = int(round(hop * sr))
    if len(audio) < n:
        audio = np.pad(audio, (0, n - len(audio)))
    frames = 1 + (len(audio) - n) // h
    idx = np.arange(n)[None, :] + h * np.arange(frames)[:, None]
    spec = np.abs(np.fft.rfft(audio[idx] * np.hanning(n)[None, :], axis=1)) ** 2
    f = np.fft.rfftfreq(n, 1.0 / sr)
    band = spec[:, (f >= lo) & (f <= hi)].sum(axis=1)
    env = 10 * np.log10(band + 1e-10)
    k = np.ones(3) / 3
    return np.convolve(env, k, mode='same')          # 30 ms smoothing, centre at frame start + 16 ms


def _events(env, t0, hop, thr, min_gap=0.08, min_len=0.03):
    """[[a, b], ...] seconds where env >= thr (gaps < min_gap merged, blips < min_len dropped)."""
    on = env >= thr
    ev, k = [], 0
    while k < len(on):
        if on[k]:
            r = k
            while r + 1 < len(on) and on[r + 1]:
                r += 1
            ev.append([t0 + k * hop, t0 + (r + 1) * hop])
            k = r + 1
        else:
            k += 1
    merged = []
    for a, b in ev:
        if merged and a - merged[-1][1] < min_gap:
            merged[-1][1] = b
        else:
            merged.append([a, b])
    return [e for e in merged if e[1] - e[0] >= min_len]


def _utterances(words, gap=0.35):
    """consecutive words grouped by pauses >= gap or sentence punctuation."""
    groups = []
    for w in words:
        if groups and w['t0'] - groups[-1][-1]['t1'] < gap and \
                not re.search(r'[.!?…。！？]["»”)]*$', str(groups[-1][-1]['w'])):
            groups[-1].append(w)
        else:
            groups.append([w])
    return groups


def is_reaction(utt):
    """a one-word or interjection-only utterance (sigh words, 'wow', 'oh my god', 'no way', laughs)."""
    toks = [norm_word(_fold(w['w'] if isinstance(w, dict) else w)) for w in utt]
    toks = [t for t in toks if t]
    if not toks:
        return True
    if len(toks) == 1:
        return True
    return len(toks) <= 3 and all(_is_interjection(t) for t in toks)


def _level_db(audio, sr=SR, hop=0.01, win=0.025):
    """full-band level in dB (25 ms RMS every 10 ms, DC removed) - low thumps and breaths count here; frame k is
    centred at k*hop + win/2."""
    n, h = int(round(win * sr)), int(round(hop * sr))
    x = np.asarray(audio, np.float64)
    if len(x) < n:
        x = np.pad(x, (0, n - len(x)))
    x = x - x.mean()
    k = 1 + (len(x) - n) // h
    idx = np.arange(n)[None, :] + h * np.arange(k)[:, None]
    return 10 * np.log10(np.mean(x[idx] ** 2, axis=1) + 1e-10)


def _low_onset(audio, t, sr=SR, dur=0.06):
    """True when the sound starting at t (s into `audio`) is mostly below 150 Hz: a thump, not a voice."""
    a, b = int(max(0.0, t) * sr), int((max(0.0, t) + dur) * sr)
    x = np.asarray(audio[a:b], np.float64)
    if len(x) < 64:
        return False
    x = (x - x.mean()) * np.hanning(len(x))
    p = np.abs(np.fft.rfft(x, n=max(1024, len(x)))) ** 2
    f = np.fft.rfftfreq(max(1024, len(x)), 1.0 / sr)
    lo, hi = p[(f >= 20) & (f < 150)].sum(), p[(f >= 150) & (f < 4000)].sum()
    return bool(lo > 4.0 * hi)


def sound_onsets(level, t0=0.0, hop=0.01, rise_db=12.0, dip_db=6.0, floor=None, merge=0.08):
    """times where a new sound starts: the level jumps >= rise_db within 30 ms, from a quiet point (near the floor
    or >= dip_db below the loudest of the last 300 ms) to above floor + 15 dB (word onsets, breaths, thumps - not
    the ripple inside a sound). level = _level_db(...) frames; t0 = time of frame 0's start."""
    lv = np.asarray(level, float)
    if len(lv) < 5:
        return []
    sm = np.convolve(lv, np.ones(3) / 3, mode='same')
    floor = float(np.percentile(sm, 10)) if floor is None else floor
    out = []
    for i in range(len(lv) - 3):
        if lv[i + 3] - lv[i] < rise_db or lv[i + 3] < floor + 15.0:
            continue
        prev = sm[max(0, i - 30):i]
        if sm[i] <= floor + 12.0 or (len(prev) and sm[i] <= prev.max() - dip_db):
            t = t0 + (i + 1) * hop + 0.0125
            if not out or t - out[-1] > merge:
                out.append(round(t, 3))
    return out


def reaction_end(media, t, words=None, max_s=4.0, margin=0.03, tail=0.02, detail=False):
    """End of the reaction that follows time t (a sigh, laugh, breath or a one-word "wow"), at a quiet point
    before the next sentence. Words (optional, recommended) tell where the next real sentence starts: words after t
    are grouped into utterances and one-word / interjection-only utterances count as the reaction. The audio finds
    where things really happen (ASR word times drift 0.1-0.3 s):
      next onset = the earliest of the next sentence's ASR start, its speech onset (voice-band energy) and any new
      sound starting right before it (sound_onsets on the full-band level: a breath, a hum, a desk/mic thump that
      runs into the next sentence) - the result is always before it (minus `margin`);
      reaction end = decay of the last speech-band sound event before that onset (last moment within 28 dB of its
      peak) + `tail`; when the reaction is still ringing at the onset, the quietest full-band point of the last
      0.2 s before it. Capped at t + max_s; without a reaction the end of the phrase's own decay is returned.
    Without words (audio only) a speech cluster shorter than 0.7 s counts as the reaction. detail=True -> (time,
    info dict with events, onsets and the next onset)."""
    t = float(t)
    ws = sorted((w for w in (_words_of(words) if words is not None else []) if w.get('t0') is not None),
                key=lambda w: w['t0'])
    after = [w for w in ws if w['t0'] >= t - 0.02 and not (w['t0'] < t < w['t1'] - 0.05)]
    reaction_words, nxt = [], None
    for u in _utterances(after):
        if is_reaction(u) and u[0]['t0'] < t + max_s:
            reaction_words += u
            continue
        nxt = u[0]['t0']
        break
    limit = t + float(max_s)
    if nxt is not None:
        limit = min(limit, nxt)
    a0 = max(0.0, t - 1.0)
    a1 = limit + 0.8
    hop = 0.01
    info = dict(t=round(t, 3), next_word=_r(nxt), reaction_words=[w['w'] for w in reaction_words])
    try:
        audio = load_audio(media, t0=a0, dur=a1 - a0)
    except (subprocess.CalledProcessError, OSError):        # no audio stream: words only
        audio = np.zeros(0, np.float32)
    if len(audio) < SR * 0.1:
        end = reaction_words[-1]['t1'] + 0.1 if reaction_words else t + tail
        res = round(max(t, min(limit - margin, end)), 3)
        info.update(end=res, audio=False)
        return (res, info) if detail else res
    env = _voice_env(audio, hop=hop)                        # speech band: what was said / exclaimed
    tt = a0 + np.arange(len(env)) * hop + 0.016
    lev = _level_db(audio, hop=hop)                         # full band: every sound, thumps included
    tl = a0 + np.arange(len(lev)) * hop + 0.0125
    lsm = np.convolve(lev, np.ones(3) / 3, mode='same')
    floor = float(np.percentile(env, 10))
    sel = (tt >= t - 0.3) & (tt <= limit + 0.5)
    peak = float(env[sel].max()) if sel.any() else float(env.max())
    thr = max(floor + 20.0, peak - 35.0)
    ev = _events(env, a0 + 0.016, hop, thr)
    ons = [o for o in sound_onsets(lev, a0, hop) if o > t + 0.05]
    info.update(floor_db=round(floor, 1), thr_db=round(thr, 1), events=[[_r(a), _r(b)] for a, b in ev], onsets=ons)
    hard = limit
    if nxt is None and not ws:
        # audio only: speech clusters (gaps >= 0.15 s); a cluster shorter than 0.7 s is a reaction, the first longer
        # one after t is the next sentence
        clusters = []
        for e in ev:
            if e[1] <= t + 0.05:
                continue
            if clusters and e[0] - clusters[-1][1] < 0.15:
                clusters[-1][1] = e[1]
            else:
                clusters.append([max(e[0], t), e[1]])
        for c in clusters:
            if c[1] - c[0] >= 0.7 and c[0] > t + 0.1:
                hard = min(hard, c[0])
                break
    elif nxt is not None:                                  # speech onset of the next sentence (ASR starts drift)
        nw = next(w for w in after if w['t0'] == nxt)

        def ov(e, a, b):
            return max(0.0, min(e[1], b) - max(e[0], a))
        cand = [e for e in ev if e[0] > t + 0.05 and ov(e, nxt - 0.3, nw['t1'] + 0.3) > 0
                and all(ov(e, nxt, nw['t1']) >= ov(e, r['t0'], r['t1']) for r in reaction_words)]
        if cand:
            hard = min(hard, min(e[0] for e in cand))
    if hard < t + float(max_s) or nxt is not None:
        # a new sound that starts before the next sentence and belongs to it - closer to its onset than to a
        # reaction word, or a low thump (desk, mic stand) - the cut must come before it: a breath, a hum, a bump
        anchors = [w['t0'] + 0.07 for w in reaction_words]
        nx = hard + 0.07
        pk = max((e[0] for e in ev if t < e[0] < hard), default=t)
        pre = [o for o in ons if max(t + 0.05, hard - 0.45) <= o < hard
               and (all(abs(o - nx) < abs(o - r) for r in anchors) or (o > pk + 0.1 and _low_onset(audio, o - a0)))]
        if pre:
            hard = min(hard, pre[0])
        info['next_onset'] = _r(hard)
    cap = hard - margin
    before = [e for e in ev if e[0] < cap and e[1] > t - 0.3]
    if not before:
        res = min(cap, t + tail)
    else:
        last = list(before[-1])
        k0, k1 = int(np.searchsorted(tt, last[0])), int(np.searchsorted(tt, last[1]))
        pk_t = last[0]
        if k1 > k0:
            seg = env[k0:k1]
            pk_t = float(tt[k0 + int(np.argmax(seg))])
            # the event's own decay: last moment within 28 dB of its peak (a loud "wow" rings longer above thr)
            loud = np.nonzero(seg >= max(thr, float(seg.max()) - 28.0))[0]
            if len(loud):
                last[1] = float(tt[k0 + loud[-1]]) + hop / 2
        if last[1] + tail <= cap:
            res = last[1] + tail
        else:                                              # still ringing at the next onset: quietest point
            lo = max(t, pk_t + 0.1, cap - 0.2)
            m = (tl >= lo) & (tl <= cap)
            if m.any():
                v, ts_ = lsm[m], tl[m]
                ok = v <= float(v.min()) + 2.0
                res = float(ts_[ok][-1])
            else:
                res = cap
    res = round(max(t, min(res, cap)), 3)
    info['end'] = res
    return (res, info) if detail else res


# ----------------------------------------------------------------------------------------------- clip candidates
# language data: English and Russian openers that need earlier context, hook and payoff markers
_CONTEXT_OPENERS = {_fold(w) for w in (
    'and', 'but', 'so', 'because', 'also', 'then', 'which', 'or', 'anyway', 'plus', 'he', 'she', 'they', 'it',
    'this', 'that', 'those', 'these', 'him', 'her', 'them', 'there', 'yeah', 'exactly', 'right',
    'и', 'но', 'а', 'потому', 'поэтому', 'так', 'тоже', 'он', 'она', 'они', 'оно', 'это', 'этот', 'эта', 'там',
    'тогда', 'да', 'вот')}
_HOOK_WORDS = {_fold(w) for w in (
    'never', 'always', 'secret', 'mistake', 'biggest', 'best', 'worst', 'crazy', 'insane', 'money', 'million',
    'billion', 'problem', 'truth', 'why', 'how', 'what', 'nobody', 'everyone', 'most', 'wrong', 'stop', 'fail',
    'failed', 'rich', 'free', 'first', 'only', 'real', 'actually', 'important', 'love', 'hate', 'fear', 'dead',
    'никогда', 'всегда', 'секрет', 'ошибка', 'главный', 'лучший', 'худший', 'деньги', 'миллион', 'миллиард',
    'проблема', 'правда', 'почему', 'как', 'никто', 'все', 'неправильно', 'важно', 'единственный')}
_PAYOFF_WORDS = {_fold(w) for w in (
    'so', 'therefore', 'point', 'lesson', 'end', 'bottom', 'line', 'main', 'thing', 'key', 'why', 'that',
    'поэтому', 'итог', 'итоге', 'главное', 'смысл', 'вывод', 'короче', 'значит')}


# topic openers that announce a point (language data: English and Russian phrases, folded)
_TOPIC_OPENERS = [tuple(_fold(p).split()) for p in (
    "here's the thing", 'the thing is', 'the reason', 'the problem', 'the biggest', 'the truth', 'the secret',
    'the question', 'the point', 'one thing', 'one of the', 'what i', "what i'm", 'what we', 'what happens',
    'what most', 'let me', 'imagine', 'think about', 'if you', 'when you', 'the way', 'here is', 'so here',
    'i think', 'i believe', 'my favorite', 'the first', 'the key', 'the main', 'everyone', 'nobody', 'most people',
    'дело в том', 'проблема в том', 'главное', 'смотри', 'представь', 'вопрос в том', 'я думаю', 'самое')]
_SOFT_OPENERS = {_fold(w) for w in ('so', 'well', 'okay', 'ok', 'now', 'right', 'yeah', 'ну', 'так', 'вот')}
_POINTING_BACK = {_fold(w) for w in (
    'it', "it's", 'its', 'that', "that's", 'this', 'these', 'those', 'they', "they're", 'them', 'he', 'she', 'him',
    'her', 'there', 'such', 'same', 'это', 'этот', 'эта', 'эти', 'он', 'она', 'они', 'оно', 'там', 'такой')}


def setup_starts(words, end_t, min_s=6.0, max_s=25.0, env=None):
    """Where a talk clip that ends at end_t (s) should start: sentence starts (after sentence punctuation or a pause
    >= 0.6 s) between end_t - max_s and end_t - min_s, ranked -> [{"t", "text", "score", "why"}] best first.
    Favoured: a pause before it, a question (the setup its answer pays off), a topic opener ("the thing is", "what
    I'm seeing", "the reason"), a camera cut / speaker change right at it (env "cuts", "turns": [t]); penalised: a
    setup that does not stand on its own - a leading "and / but / because", a pronoun pointing back ("it", "that",
    "they" with nothing before it in the clip), a sentence the transcript starts in the middle of - and a start inside
    an env "avoid" span ([[t0, t1]]: a popup over the speaker, a black frame)."""
    ws = [w for w in _words_of(words) if w.get('t0') is not None and w.get('t1') is not None
          and str(w.get('w', '')).strip()]
    ws.sort(key=lambda w: w['t0'])
    env = env or {}
    cuts = sorted(float(t) for t in list(env.get('cuts') or []) + list(env.get('turns') or []))
    avoid = [(float(a), float(b)) for a, b in env.get('avoid') or []]
    out = []
    for i, w in enumerate(ws):
        t = float(w['t0'])
        if not end_t - max_s - 1e-6 <= t <= end_t - min_s + 1e-6:
            continue
        gap = t - ws[i - 1]['t1'] if i else 9.0
        if i and not (_SENT_RE.search(ws[i - 1]['w']) or gap >= 0.6):
            continue
        j = i                                                # the first sentence of the setup
        while j + 1 < len(ws) and ws[j + 1]['t0'] < end_t and not _SENT_RE.search(ws[j]['w']):
            j += 1
        toks = [norm_word(_fold(x['w'])) for x in ws[i:j + 1]]
        text = ' '.join(x['w'] for x in ws[i:j + 1])
        lg = _lang_of(ws, None)
        fl = FILLER_PHRASES.get(lg, set()) | FILLERS.get(lg, FILLERS['en'])['sure']
        k = 0                                                # a leading filler ("it's like", "you know") is skipped
        while k < len(toks) - 1:
            n_ = next((n_ for n_ in (3, 2, 1) if ' '.join(toks[k:k + n_]) in fl), 0)
            if not n_:
                break
            k += n_
        toks = toks[k:]
        score, why = 0.0, []
        if gap >= 0.25:
            score += min(gap, 1.2)
            why.append(f'after a {min(gap, 9.0):.1f} s pause' if i else 'the first words')
        if ws[j]['w'].rstrip('"»”)\'').endswith('?'):
            score += 1.5
            why.append('a question')
        lead = tuple(toks[:4])
        op = next((' '.join(p) for p in _TOPIC_OPENERS if lead[:len(p)] == p), None)
        if op:
            score += 0.8
            why.append(f'opens a topic ("{op}")')
        if toks and toks[0] in _SOFT_OPENERS:
            score -= 0.2                                     # "So how much ...": a discourse marker, mostly fine
        elif toks and toks[0] in _CONTEXT_OPENERS - _POINTING_BACK:
            score -= 1.0
            why.append(f'continues ("{toks[0]}")')
        back = [x for x in toks[:4] if x in _POINTING_BACK]
        if back:
            score -= 0.7
            why.append(f'points back ("{back[0]}")')
        first = str(w['w']).lstrip('"«“(\'')
        if first[:1].isalpha() and first[:1].islower() and first[:1] != first[:1].upper() and not i:
            score -= 1.5
            why.append('starts mid-sentence')
        elif first[:1].isalpha() and first[:1].islower() and first[:1] != first[:1].upper():
            score -= 0.5
            why.append('lower case: maybe mid-sentence')
        if any(t - 0.35 <= c <= t + 0.1 for c in cuts):
            score += 0.4
            why.append('a camera cut / speaker change at the start')
        if any(a - 1e-6 <= t < b for a, b in avoid):
            score -= 1.0
            why.append('inside an avoid span (popup / overlay)')
        elif any(a < t + 1.0 and b > t for a, b in avoid):
            score -= 0.4
            why.append('an avoid span in its first second')
        score += 0.3 * (end_t - t - min_s) / max(1e-6, max_s - min_s)     # a little more context
        out.append(dict(t=round(t, 3), text=text, score=round(score, 3), why=why))
    out.sort(key=lambda x: -x['score'])
    return out


def clip_candidates(words, media=None, min_s=15.0, max_s=60.0, n=10, lang=None, faces=None):
    """Moments for short clips from a long talk (podcast, interview, stream), from the transcript (+ audio).
    Windows of min_s..max_s seconds start at a sentence start that needs no earlier context (no "and/but/so", no
    "he/they/it" opener) and end at a sentence end followed by a pause or a reaction. Score = hook x payoff x
    density (x face visibility when `faces` = [[t0, t1, share], ...] is given): hook = question, number, strong
    words, loudness above the median (with media), speech-rate burst; payoff = pause >= 0.4 s / reaction after the
    line, summing-up words, a number. Overlapping windows (IoU > 0.3) keep the best.
    -> [{"t0", "t1", "i0", "i1", "score", "hook", "payoff", "density", "text", "first", "last"}] best first."""
    ws = [w for w in _words_of(words) if w.get('t0') is not None and str(w.get('w', '')).strip()]
    if not ws:
        return []
    groups = _sentences(ws, max_dur=12.0, pause=0.6)
    loud = None
    if media is not None:
        try:
            a0, a1 = ws[0]['t0'], ws[-1]['t1']
            audio = load_audio(media, t0=max(0.0, a0), dur=a1 - a0 + 0.1)
            env = _voice_env(audio, hop=0.05)
            loud = (max(0.0, a0), env, float(np.median(env)))
        except Exception:
            loud = None
    rate_all = len(ws) / max(1e-3, sum(w['t1'] - w['t0'] for w in ws))

    def sent_feats(a, b):
        toks = [norm_word(_fold(w['w'])) for w in ws[a:b + 1]]
        text = ' '.join(w['w'] for w in ws[a:b + 1])
        hook = 1.0
        if '?' in text:
            hook += 0.5
        if any(re.search(r'\d', w['w']) for w in ws[a:b + 1]) or any(t in _NUM_SCALES for t in toks):
            hook += 0.4
        hook += 0.15 * min(3, sum(1 for t in toks if t in _HOOK_WORDS))
        dur = ws[b]['t1'] - ws[a]['t0']
        if dur > 0.5 and (b - a + 1) / dur > 1.25 * rate_all:
            hook += 0.2
        if loud is not None:
            s0, env, med = loud
            k0, k1 = int((ws[a]['t0'] - s0) / 0.05), int((ws[b]['t1'] - s0) / 0.05)
            seg = env[max(0, k0):max(k0 + 1, k1)]
            if len(seg) and np.percentile(seg, 75) - med >= 2.0:
                hook += 0.3
        return hook, toks, text

    feats = [sent_feats(a, b) for a, b in groups]
    out = []
    for gi, (a, _) in enumerate(groups):
        first = feats[gi][1]
        if not first or first[0] in _CONTEXT_OPENERS:
            continue
        t0 = ws[a]['t0']
        for gj in range(gi, len(groups)):
            b = groups[gj][1]
            t1 = ws[b]['t1']
            dur = t1 - t0
            if dur > max_s:
                break
            if dur < min_s or not re.search(r'[.!?…]["»”)]*$', ws[b]['w']):
                continue
            nxt = groups[gj + 1] if gj + 1 < len(groups) else None
            pause = (ws[nxt[0]]['t0'] - t1) if nxt else 1.0
            payoff = 1.0
            if pause >= 0.4:
                payoff += 0.3
            if nxt and is_reaction(ws[nxt[0]:nxt[1] + 1]):
                payoff += 0.5
            last = feats[gj][1]
            if any(t in _PAYOFF_WORDS for t in last[:4]):
                payoff += 0.2
            if any(re.search(r'\d', w['w']) for w in ws[groups[gj][0]:b + 1]):
                payoff += 0.2
            speech = sum(w['t1'] - w['t0'] for w in ws[a:b + 1])
            density = min(1.0, speech / max(dur, 1e-3) / 0.85)
            vis = 1.0
            if faces:
                cov = sum(max(0.0, min(t1, f1) - max(t0, f0)) * s for f0, f1, s in faces)
                vis = 0.5 + 0.5 * min(1.0, cov / max(dur, 1e-3))
            length = 1.0 - 0.15 * abs((dur - 35.0) / 25.0)
            hook = feats[gi][0]
            sc = hook * payoff * density * vis * length
            out.append(dict(t0=_r(t0), t1=_r(t1), i0=a, i1=b, score=_r(sc), hook=_r(hook, 2), payoff=_r(payoff, 2),
                            density=_r(density, 2), text=join_words([w['w'] for w in ws[a:b + 1]]),
                            first=feats[gi][2], last=feats[gj][2]))
    out.sort(key=lambda c: -c['score'])
    keep = []
    for c in out:
        if all(min(c['t1'], k['t1']) - max(c['t0'], k['t0']) <= 0.3 * (max(c['t1'], k['t1']) - min(c['t0'], k['t0']))
               for k in keep):
            keep.append(c)
        if len(keep) >= n:
            break
    return keep


# ----------------------------------------------------------------------------------------------- CLI
def _load_words(p):
    d = json.loads(Path(p).read_text(encoding='utf-8'))
    return d


def main(argv=None):
    ap = argparse.ArgumentParser(description='ed_voice: speech recognition, subtitles, jump cuts, translation plans')
    sub = ap.add_subparsers(dest='cmd', required=True)
    t = sub.add_parser('transcribe', help='media -> words.json')
    t.add_argument('media')
    t.add_argument('--lang')
    t.add_argument('--model', default='auto', choices=['auto', 'omni'] + list(MODELS))
    t.add_argument('--timing', default='auto', choices=['auto', 'ctc', 'dtw'])
    t.add_argument('--prompt')
    t.add_argument('--text', help='file with the known script/lyrics (forced alignment)')
    t.add_argument('--srt', help='SRT file to align')
    t.add_argument('--out')
    t.add_argument('--srt-out')
    t.add_argument('--no-cache', action='store_true')
    t.add_argument('-v', '--verbose', action='store_true')
    s = sub.add_parser('subs', help='words.json -> ed_text layers / SRT / ASS')
    s.add_argument('words')
    s.add_argument('--kind', default='subtitle', choices=['subtitle', 'karaoke'])
    s.add_argument('--fps', type=float, default=30)
    s.add_argument('--max-chars', type=int)
    s.add_argument('--max-lines', type=int)
    s.add_argument('--horizontal', action='store_true')
    s.add_argument('--out')
    s.add_argument('--srt')
    s.add_argument('--ass')
    j = sub.add_parser('jumpcuts', help='words.json -> pauses/fillers/cuts/keep (+ EDL segments with --fps)')
    j.add_argument('words')
    j.add_argument('--min-pause', type=float, default=0.35)
    j.add_argument('--keep-pause', type=float, default=0.12)
    j.add_argument('--fillers', default='sure', choices=['sure', 'all', 'none'])
    j.add_argument('--fps', type=float)
    j.add_argument('--src', default='main')
    j.add_argument('--out')
    al = sub.add_parser('align', help='words.json + known text -> words with the known text')
    al.add_argument('words')
    al.add_argument('text')
    al.add_argument('--media', help='align acoustically against this media instead')
    al.add_argument('--out')
    pl = sub.add_parser('plan', help='words.json -> translation plan for Claude')
    pl.add_argument('words')
    pl.add_argument('--to', required=True)
    pl.add_argument('--fps', type=float, default=30)
    pl.add_argument('--horizontal', action='store_true')
    pl.add_argument('--out')
    m = sub.add_parser('models', help='list / download models')
    m.add_argument('--get', nargs='*', help='turbo small base tiny ctc vad')
    ph = sub.add_parser('phrase', help='words.json + phrase -> {t0, t1, i0, i1, score, text} (fuzzy, number formats)')
    ph.add_argument('words')
    ph.add_argument('text')
    ph.add_argument('--after', type=float)
    ph.add_argument('--before', type=float)
    ph.add_argument('--min-score', type=float, default=0.7)
    ph.add_argument('--all', action='store_true', help='every occurrence, best first')
    re_ = sub.add_parser('reaction', help='media + time -> end of the reaction after it (sigh, laugh, "wow")')
    re_.add_argument('media')
    re_.add_argument('t', type=float)
    re_.add_argument('--words')
    re_.add_argument('--max-s', type=float, default=4.0)
    cl = sub.add_parser('clips', help='words.json -> clip candidates (15-60 s windows, hook x payoff)')
    cl.add_argument('words')
    cl.add_argument('--media')
    cl.add_argument('--min-s', type=float, default=15.0)
    cl.add_argument('--max-s', type=float, default=60.0)
    cl.add_argument('-n', type=int, default=10)
    cl.add_argument('--out')
    a = ap.parse_args(argv)

    def dump(obj, path):
        s = json.dumps(obj, ensure_ascii=False, indent=1)
        if path:
            Path(path).write_text(s, encoding='utf-8')
            print(f'-> {path}')
        else:
            print(s)
    if a.cmd == 'transcribe':
        text = Path(a.text).read_text(encoding='utf-8') if a.text else None
        r = transcribe(a.media, lang=a.lang, model=a.model, timing=a.timing, prompt=a.prompt, text=text, srt=a.srt,
                       cache=not a.no_cache, verbose=a.verbose)
        if a.srt_out:
            to_srt(r, a.srt_out)
        if a.out:
            dump(r, a.out)
        print(f'{r["lang"]} {r["model"]} {r["timing"] if "timing" in r else ""} {len(r["words"])} words, '
              f'{r["stats"]["seconds"]}s; ' + ' '.join(w['w'] for w in r['words'])[:400])
    elif a.cmd == 'subs':
        d = _load_words(a.words)
        L = subtitle_chunks(d, kind=a.kind, fps=a.fps, max_chars=a.max_chars, max_lines=a.max_lines,
                            vertical=not a.horizontal)
        if a.srt:
            to_srt(L, a.srt)
        if a.ass:
            to_ass(L, a.ass, canvas=(1920, 1080) if a.horizontal else (1080, 1920))
        dump(L, a.out)
    elif a.cmd == 'jumpcuts':
        dump(speech_segments(_load_words(a.words), min_pause=a.min_pause, keep_pause=a.keep_pause, fillers=a.fillers,
                             fps=a.fps, src=a.src), a.out)
    elif a.cmd == 'align':
        d = _load_words(a.words)
        text = Path(a.text).read_text(encoding='utf-8')
        dump(align_text(d, text) if not a.media else transcribe(a.media, text=text)['words'], a.out)
    elif a.cmd == 'plan':
        dump(translate_plan(_load_words(a.words), a.to, fps=a.fps, vertical=not a.horizontal), a.out)
    elif a.cmd == 'phrase':
        d = _load_words(a.words)
        if a.all:
            dump(find_phrase_all(d, a.text, after=a.after, before=a.before, min_score=a.min_score), None)
        else:
            dump(find_phrase(d, a.text, after=a.after, before=a.before, min_score=a.min_score), None)
    elif a.cmd == 'reaction':
        t, info = reaction_end(a.media, a.t, _load_words(a.words) if a.words else None, max_s=a.max_s, detail=True)
        dump(info, None)
    elif a.cmd == 'clips':
        dump(clip_candidates(_load_words(a.words), media=a.media, min_s=a.min_s, max_s=a.max_s, n=a.n), a.out)
    elif a.cmd == 'models':
        for g in a.get or []:
            if g in MODELS:
                ensure_model(g, verbose=True)
            elif g == 'ctc':
                ensure_ctc(verbose=True)
            elif g == 'vad':
                ensure_vad()
        print(json.dumps(dict(cache=str(CACHE), installed=installed_models(),
                              ctc=(CACHE / CTC['dir'] / 'model.int8.onnx').exists(),
                              vad=(CACHE / VAD_FILE).exists()), indent=1))


if __name__ == '__main__':
    main()
