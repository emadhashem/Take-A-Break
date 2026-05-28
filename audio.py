import pygame
import threading

_initialized = False


def _ensure_init():
    global _initialized
    if not _initialized:
        pygame.mixer.init()
        _initialized = True


def play(path: str, volume: float = 0.8):
    if not path:
        return

    def _play():
        try:
            _ensure_init()
            pygame.mixer.music.load(path)
            pygame.mixer.music.set_volume(max(0.0, min(1.0, volume)))
            pygame.mixer.music.play()
        except Exception as e:
            print(f"[audio] playback error: {e}")

    threading.Thread(target=_play, daemon=True).start()


def stop():
    try:
        pygame.mixer.music.stop()
    except Exception:
        pass
