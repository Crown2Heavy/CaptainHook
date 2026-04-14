import os
import asyncio
try:
    import sounddevice as sd
except Exception as e:
    sd = None
import numpy as np
import io
import wave
import discord
from src.client.core.cache import OfflineCache
from datetime import datetime

class SirenEngine:
    def __init__(self, bot):
        self.bot = bot
        self.offline_cache = OfflineCache()
        self.is_recording_offline = False
        self.is_streaming = False
        self.stream = None
        self.sample_rate = 48000
        self.channels = 2
        self.buffer_size = 1024
        self.available = sd is not None

    def get_input_devices(self):
        """List all available audio input devices."""
        if not self.available:
             return "Audio hardware/drivers not available."
        return sd.query_devices()

    async def stream_to_voice(self, voice_client):
        """Capture system/mic audio and stream it directly to a Discord voice channel."""
        if not voice_client or not self.available:
            return

        self.is_streaming = True
        
        def callback(indata, frames, time, status):
            if status:
                print(f"Audio Status: {status}")
            if self.is_streaming:
                # Convert float32 to int16 for Discord (PCM)
                pcm_data = (indata * 32767).astype(np.int16).tobytes()
                # Note: This is a simplification. Discord requires Opus encoding.
                # discord.py's VoiceClient.send_audio_packet expects encoded opus data.
                # We usually use discord.PCMAudio(io.BytesIO(pcm_data)) or similar.
                pass

        # This requires more complex logic to integrate with discord.py's AudioSource
        pass

    async def start_offline_ears(self, duration_per_clip=60):
        """Continuously record audio in chunks and save to encrypted cache when offline."""
        if self.is_recording_offline or not self.available:
            return
            
        self.is_recording_offline = True
        print("Siren: Offline Ears activated.")
        
        while self.is_recording_offline:
            # Check if we are still offline
            if self.bot.is_connected:
                print("Siren: Connection restored. Deactivating Offline Ears.")
                self.is_recording_offline = False
                break
                
            try:
                # Record a chunk
                fs = 44100
                recording = sd.rec(int(duration_per_clip * fs), samplerate=fs, channels=1, dtype='float32')
                
                # We need to wait without blocking the whole bot
                # sd.wait() is blocking, so we'll use a loop with asyncio.sleep
                start_time = asyncio.get_event_loop().time()
                while asyncio.get_event_loop().time() - start_time < duration_per_clip:
                    if not self.is_recording_offline:
                        sd.stop()
                        break
                    await asyncio.sleep(1)
                
                if not self.is_recording_offline:
                    break

                # Save to buffer
                buffer = io.BytesIO()
                with wave.open(buffer, 'wb') as wf:
                    wf.setnchannels(1)
                    wf.setsampwidth(2) # 16-bit
                    wf.setframerate(fs)
                    # Convert to int16 before saving
                    wf.writeframes((recording * 32767).astype(np.int16).tobytes())
                
                # Encrypt and save to cache
                self.offline_cache.save_data("audio_ambient", buffer.getvalue(), is_binary=True)
                print(f"Siren: Cached ambient audio clip ({duration_per_clip}s)")
                
            except Exception as e:
                print(f"Siren Error: {e}")
                await asyncio.sleep(10) # Wait before retry

    def stop_offline_ears(self):
        self.is_recording_offline = False
        if self.available:
            sd.stop()

