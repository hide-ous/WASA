import os
import json
import time
import shutil
import logging
from threading import Thread, Lock

from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from mutagen.id3 import ID3NoHeaderError

from mutagen.mp3 import MP3
from mutagen.flac import FLAC
from mutagen.oggvorbis import OggVorbis

# Libraries for filesystem monitoring and MusicBrainz
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import musicbrainzngs

# --- CONFIGURATION AND INITIALIZATION ---

# Environment variables (will be passed by docker-compose)
# Direttive per l'input e l'output
INPUT_DIR = os.environ.get('INPUT_DIR', '/app/input')
OUTPUT_DIR = os.environ.get('OUTPUT_DIR', '/app/output')
MUSICBRAINZ_USER_AGENT = os.environ.get('MUSICBRAINZ_USER_AGENT', 'MediaManagerApp/1.0 (studente.example@email.com)')

MUSIC_EXTENSIONS = ('.mp3', '.flac', '.ogg')
DEFAULT_NAMING_PATTERN = "{artist}/{album}/{track:02d} - {title}.{ext}"

# Global application state
user_files = {}
file_lock = Lock()
current_naming_pattern = DEFAULT_NAMING_PATTERN

# Logger configuration
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# MusicBrainz configuration
musicbrainzngs.set_useragent(MUSICBRAINZ_USER_AGENT, "1.0")
musicbrainzngs.set_rate_limit(True)

# Flask configuration
# STATIC_FOLDER is set to '.' to allow Flask to serve index.html from the /app root
app = Flask(__name__, static_folder='.', static_url_path='')
CORS(app)

# Ensure directories exist
os.makedirs(INPUT_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)
logger.info(f"Input Directory: {INPUT_DIR}, Output Directory: {OUTPUT_DIR}")


# --- UTILITY FUNCTIONS ---

def get_audio_object(filepath):
    """Returns the appropriate Mutagen audio object based on the extension."""
    ext = os.path.splitext(filepath)[1].lower()
    if ext == '.mp3':
        return MP3(filepath)
    elif ext == '.flac':
        return FLAC(filepath)
    elif ext == '.ogg':
        return OggVorbis(filepath)
    return None


def extract_metadata(filepath):
    """Extracts basic metadata and prepares it for the interface."""
    filename = os.path.basename(filepath)
    ext = os.path.splitext(filepath)[1].lower().lstrip('.')

    try:
        audio = get_audio_object(filepath)
        if audio is None:
            raise ValueError(f"Unsupported extension: {ext}")

        tags = audio.tags
        if tags is None and ext == 'mp3':
            try:
                # Try a re-read for ID3 tags
                audio = MP3(filepath)
                tags = audio.tags
            except:
                pass

        if tags is None:
            raise ID3NoHeaderError("No Mutagen tags found.")

        def get_tag_value(tag_key, default='Sconosciuto'):
            if ext == 'mp3':
                val = tags.get(tag_key.upper())
            else:
                # Vorbis comments use lowercase
                val = tags.get(tag_key.lower())

            if val:
                if isinstance(val, list):
                    v = str(val[0]).strip()
                else:
                    v = str(val).strip()

                if tag_key.lower() == 'track':
                    try:
                        # Handles '1/10' formats
                        return int(v.split('/')[0])
                    except:
                        return 0

                return v if v else default
            return default

        metadata = {
            'filepath': filepath,
            'filename': filename,
            'ext': ext,
            'status': 'Metadati estratti, pronto per MusicBrainz',
            'title': get_tag_value('title'),
            'artist': get_tag_value('artist'),
            'album': get_tag_value('album'),
            'track': get_tag_value('track')
        }

        if metadata['artist'] == 'Sconosciuto' and metadata['title'] == 'Sconosciuto':
            metadata['status'] = 'Metadati vuoti, ricerca MusicBrainz difficile'

        return metadata

    except (ID3NoHeaderError, Exception) as e:
        logger.error(f"Error extracting metadata for {filename}: {e}")
        return {
            'filepath': filepath,
            'filename': filename,
            'ext': ext,
            'status': f'Errore estrazione tag: {type(e).__name__}',
            'title': filename.split('.')[0],
            'artist': 'Sconosciuto',
            'album': 'Sconosciuto',
            'track': 0
        }


def search_musicbrainz(metadata):
    """Searches for the track on MusicBrainz using existing metadata."""
    try:
        query = f"artist:\"{metadata['artist']}\" AND track:\"{metadata['title']}\""
        result = musicbrainzngs.search_recordings(query=query, limit=10)

        if result['recording-list']:
            recording = result['recording-list'][0]
            new_metadata = {
                'title': recording.get('title', metadata['title']),
                'artist': recording.get('artist-credit-phrase', metadata['artist']),
                'match_score': recording.get('score', 0)
            }

            # Try to find album and track number
            if 'release-list' in recording and recording['release-list']:
                release = recording['release-list'][0]
                new_metadata['album'] = release.get('title', metadata['album'])

                # If track number is missing, try to find it in the release details
                if metadata['track'] == 0:
                    for medium in release.get('medium-list', []):
                        for track in medium.get('track-list', []):
                            if track.get('recording') and track['recording']['id'] == recording['id']:
                                try:
                                    new_metadata['track'] = int(track.get('position', 0))
                                except:
                                    new_metadata['track'] = metadata['track']
                                break

            enriched_metadata = {**metadata, **new_metadata}
            enriched_metadata['status'] = f"MusicBrainz Trovato: {enriched_metadata['match_score']}%"
            return enriched_metadata

        else:
            metadata['status'] = 'MusicBrainz: Nessun risultato trovato.'
            return metadata

    except Exception as e:
        logger.error(f"MusicBrainz API Error: {e}")
        metadata['status'] = f'MusicBrainz: Errore API'
        return metadata


def rename_and_move_file(metadata, pattern):
    """Renames and moves the file to OUTPUT_DIR using the given pattern."""

    # Make metadata safe for directory names (replace invalid characters)
    # Rendi i metadati sicuri per i nomi di file/directory
    safe_metadata = {k: str(v).replace('/', '_').replace('\\', '_').replace(':', ' -') for k, v in metadata.items()}
    # Ensure track is an integer for formatting
    safe_metadata['track'] = int(metadata.get('track', 0))

    try:
        # Create the new relative and absolute path
        new_relative_path = pattern.format(**safe_metadata)
        new_abs_path = os.path.join(OUTPUT_DIR, new_relative_path)
        target_dir = os.path.dirname(new_abs_path)

        # Create the destination folder if it doesn't exist
        os.makedirs(target_dir, exist_ok=True)
        # Move the file
        shutil.move(metadata['filepath'], new_abs_path)

        return new_abs_path

    except KeyError as e:
        # Handle cases where the pattern contains an undefined variable
        raise ValueError(f"Missing variable in pattern: {e}. Available metadata keys: {safe_metadata.keys()}")
    except Exception as e:
        # Handle general move/rename errors
        raise Exception(f"Error during move/rename operation: {e}")


# --- WATCHDOG MONITORING ---

class MediaFileHandler(FileSystemEventHandler):
    """Watchdog event handler for file monitoring."""

    def on_created(self, event):
        """Handles the creation of a new file."""
        if not event.is_directory and event.src_path.lower().endswith(MUSIC_EXTENSIONS):
            Thread(target=self.process_new_file, args=(event.src_path,)).start()

    def process_new_file(self, filepath):
        """Logic for metadata extraction and adding to state."""
        filename = os.path.basename(filepath)
        # Wait a moment to ensure file writing is complete
        time.sleep(1)

        logger.info(f"New file detected: {filename}")
        metadata = extract_metadata(filepath)

        with file_lock:
            user_files[filename] = metadata

        logger.info(f"Metadata extracted for {filename}: {metadata}")


def start_file_monitoring():
    """Initializes Watchdog Observer."""
    print(INPUT_DIR)
    print(os.listdir(INPUT_DIR))
    print(os.getcwd())
    print(os.listdir())
    # Initial scan of existing files
    for filename in os.listdir(INPUT_DIR):
        filepath = os.path.join(INPUT_DIR, filename)
        if os.path.isfile(filepath) and filename.lower().endswith(MUSIC_EXTENSIONS):
            MediaFileHandler().process_new_file(filepath)

    # Start the Watchdog Observer
    event_handler = MediaFileHandler()
    observer = Observer()
    observer.schedule(event_handler, INPUT_DIR, recursive=False)
    observer.start()

    logger.info(f"Filesystem monitoring started on {INPUT_DIR}")

    try:
        # Keep the main monitoring thread alive
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()


# --- API ENDPOINTS ---

@app.route('/')
def serve_frontend():
    """Main route to serve the frontend HTML file."""
    # Serve index.html from the root directory (which is /app in the container)
    return send_from_directory('.', 'index.html')


@app.route('/api/status', methods=['GET'])
def get_status():
    """Returns the application and file status."""
    with file_lock:
        file_list = list(user_files.values())

    return jsonify({
        'processor_status': 'Monitoraggio Watchdog Attivo',
        'input_dir': INPUT_DIR,
        'output_dir': OUTPUT_DIR,
        'naming_pattern': current_naming_pattern,
        'total_files': len(file_list),
        'files': file_list
    })


@app.route('/api/rename', methods=['POST'])
def process_file_api():
    """API to execute the complete operation: MusicBrainz + Rename/Move."""
    data = request.json
    filename_to_process = data.get('filename')
    new_pattern = data.get('pattern')

    if not filename_to_process or not new_pattern:
        return jsonify({"success": False, "message": "Nome file o pattern mancante."}), 400

    with file_lock:
        metadata = user_files.get(filename_to_process)
        if not metadata:
            return jsonify(
                {"success": False, "message": f"File {filename_to_process} non trovato o già processato."}), 404

        global current_naming_pattern
        current_naming_pattern = new_pattern

    # Start MusicBrainz search (may take time)
    logger.info(f"Starting MusicBrainz search for {filename_to_process}")
    enriched_metadata = search_musicbrainz(metadata)

    with file_lock:
        # Update the state with enriched metadata
        user_files[filename_to_process] = enriched_metadata

    try:
        # Rename and move the file
        new_path = rename_and_move_file(enriched_metadata, new_pattern)

        # Remove the file from state upon success
        with file_lock:
            del user_files[filename_to_process]

        logger.info(f"File processed and moved successfully to: {new_path}")
        return jsonify({"success": True, "message": f"Successo! Spostato in {new_path}"})

    except Exception as e:
        logger.error(f"Critical error during processing of {filename_to_process}: {e}")
        # Update status for the error
        with file_lock:
            if filename_to_process in user_files:
                user_files[filename_to_process]['status'] = f"ERRORE CRITICO: {str(e)}"

        return jsonify({"success": False, "message": str(e)}), 500


# --- APPLICATION STARTUP ---

if __name__ == '__main__':
    # Start filesystem monitoring in a separate thread
    monitor_thread = Thread(target=start_file_monitoring, daemon=True)
    monitor_thread.start()

    # Start the Flask server
    app.run(host='0.0.0.0', port=5000)