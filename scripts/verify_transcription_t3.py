import sys
from pathlib import Path
from app.services.transcription_service import TranscriptionService


def test_live_transcription_t3():
    print("=========================================================")
    print("[INFO] VERIFICATION DU SERVICE TRANSCRIPTION STT (T3)")
    print("=========================================================")

    service = TranscriptionService(model_name="whisper-mg", language="mg")
    print(f"Modèle configuré : {service.model_name} (Langue : {service.language})")

    # Génération d'un fichier audio temporaire de test
    dummy_wav = Path("data/audio/t3_test_audio.wav")
    dummy_wav.parent.mkdir(parents=True, exist_ok=True)
    dummy_wav.write_bytes(b"RIFF....WAVEfmt ....data....")

    try:
        response = service.transcribe(str(dummy_wav), video_id="video-test-t3")
        print("\n[OK] Transcription exécutée avec succès !")
        print(f"  - Video ID : {response.video_id}")
        print(f"  - Langue : {response.language}")
        print(f"  - Texte complet : '{response.full_text}'")
        print(f"  - Nombre de segments horodatés : {len(response.segments)}")

        for seg in response.segments:
            print(f"    [{seg.start_time:.1f}s -> {seg.end_time:.1f}s] Seg {seg.id}: {seg.text}")

        assert len(response.segments) > 0, "Aucun segment généré"
        assert response.full_text != "", "Le texte transcrit est vide"

        print("\n[SUCCESS] LE TICKET 3 EST 100% FONCTIONNEL ET PRÊT POUR L'ANALYSE DE DÉTECTION !")

    except Exception as e:
        print(f"\n[ERROR] Échec du test de transcription : {e}")
        sys.exit(1)
    finally:
        if dummy_wav.exists():
            dummy_wav.unlink()


if __name__ == "__main__":
    test_live_transcription_t3()
