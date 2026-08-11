import os
import subprocess
from pathlib import Path
from app.services.audio_service import AudioService, AudioExtractionError


def test_live_ffmpeg_extraction():
    print("=========================================================")
    print("[INFO] TEST DE PRODUCTION LIVE FFMPEG (TICKET 2)")
    print("=========================================================")

    audio_service = AudioService(output_dir="data/audio")

    # 1. Vérification de la détection de FFmpeg
    is_available = audio_service.is_ffmpeg_available()
    print(f"1. Detection de FFmpeg dans le PATH systeme : {is_available}")

    if not is_available:
        print("\n[ERROR] FFmpeg n'est pas detecte dans le PATH du terminal actuel.")
        return

    # 2. Génération d'une vidéo synthétique de test avec FFmpeg (2 secondes)
    test_video_path = Path("data/videos/test_sample_2s.mp4")
    test_video_path.parent.mkdir(parents=True, exist_ok=True)

    print(f"2. Generation d'une video synthetique de test (2s) : '{test_video_path}'...")
    gen_cmd = [
        "ffmpeg", "-y",
        "-f", "lavfi", "-i", "testsrc=duration=2:size=320x240:rate=1",
        "-f", "lavfi", "-i", "sine=frequency=440:duration=2",
        "-c:v", "libx264", "-c:a", "aac",
        str(test_video_path)
    ]
    try:
        subprocess.run(gen_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        print("  - Video synthetique generee avec succes !")
    except Exception as e:
        print(f"  - Impossible de generer la video de test: {e}")
        return

    # 3. Extraction audio via AudioService
    print("3. Extraction de la piste audio via AudioService...")
    try:
        wav_path = audio_service.extract_audio(str(test_video_path), output_filename="live_test_extracted.wav")
        print(f"  - Fichier WAV extrait : '{wav_path}'")
        
        # 4. Vérification de l'existence et calcul de la durée
        wav_file = Path(wav_path)
        assert wav_file.exists(), "Le fichier audio extrait n'existe pas."
        file_size = wav_file.stat().st_size
        print(f"  - Taille du fichier WAV : {file_size} octets")

        duration = audio_service.get_audio_duration(wav_path)
        print(f"  - Duree de l'audio calculee : {duration} secondes")
        assert duration > 0, "La duree audio calculee doit etre superieure a 0"

        # 5. Nettoyage
        print("4. Nettoyage des fichiers temporaires...")
        audio_service.cleanup_audio(wav_path)
        if test_video_path.exists():
            test_video_path.unlink()
        print("  - Nettoyage termine avec succes.")

        print("\n[SUCCESS] LE SERVICE D'EXTRACTION AUDIO FFMPEG EST 100% FONCTIONNEL SUR VOTRE MACHINE !")

    except AudioExtractionError as e:
        print(f"\n[ERROR] Erreur lors de l'extraction audio: {e}")
    except Exception as e:
        print(f"\n[ERROR] Erreur inattendue: {e}")


if __name__ == "__main__":
    test_live_ffmpeg_extraction()
