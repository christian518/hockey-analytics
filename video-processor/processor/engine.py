import cv2, numpy as np, asyncio, logging, os, httpx
from typing import Optional, List
from collections import deque
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)
BACKEND_URL = os.getenv("BACKEND_URL", "http://backend:8000")

@dataclass
class DetectedEvent:
    event_type: str
    timestamp: float
    confidence: float
    frame_number: int
    metadata: dict = field(default_factory=dict)

class MotionAnalyzer:
    def __init__(self, w, h):
        self.width, self.height = w, h
        self.left_goal = (0, int(h*0.3), int(w*0.22), int(h*0.72))
        self.right_goal = (int(w*0.78), int(h*0.3), w, int(h*0.72))
        self.motion_history = deque(maxlen=45)
        self.goal_motion_history = deque(maxlen=90)
        self.prev_gray = None
        self.bg_sub = cv2.createBackgroundSubtractorMOG2(history=120, varThreshold=40, detectShadows=False)

    def update(self, frame):
        gray = cv2.GaussianBlur(cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY), (21,21), 0)
        fg = self.bg_sub.apply(frame)
        total = np.sum(fg > 0) / (self.width * self.height)
        self.motion_history.append(total)
        lm = self._zone(fg, self.left_goal)
        rm = self._zone(fg, self.right_goal)
        gm = max(lm, rm)
        self.goal_motion_history.append(gm)
        flow_mag = 0.0
        if self.prev_gray is not None:
            try:
                flow = cv2.calcOpticalFlowFarneback(self.prev_gray, gray, None, 0.5, 2, 15, 2, 5, 1.1, 0)
                mag, _ = cv2.cartToPolar(flow[...,0], flow[...,1])
                flow_mag = float(np.mean(mag))
            except: pass
        self.prev_gray = gray
        return {
            "total_motion": total,
            "avg_motion": float(np.mean(self.motion_history)) if self.motion_history else 0,
            "goal_zone_motion": gm,
            "avg_goal_motion": float(np.mean(self.goal_motion_history)) if self.goal_motion_history else 0,
            "flow_magnitude": flow_mag,
            "left_goal_motion": lm,
            "right_goal_motion": rm,
        }

    def _zone(self, mask, zone):
        x1,y1,x2,y2 = zone
        roi = mask[y1:y2, x1:x2]
        return float(np.sum(roi > 0) / roi.size) if roi.size > 0 else 0.0

class EventDetector:
    SHOT_CD = 90
    PRESSURE_CD = 150
    GOAL_CD = 300

    def __init__(self):
        self.last_shot = -self.SHOT_CD
        self.last_pressure = -self.PRESSURE_CD
        self.last_goal = -self.GOAL_CD
        self.pressure_buf = deque(maxlen=90)
        self.post_shot = 0

    def analyze(self, m, frame, fps):
        events = []
        self.pressure_buf.append(m["goal_zone_motion"])
        s = self._shot(m, frame, fps)
        if s:
            events.append(s)
            self.post_shot = int(fps * 4)
        if self.post_shot > 0:
            self.post_shot -= 1
            g = self._goal(m, frame, fps)
            if g: events.append(g); self.post_shot = 0
        p = self._pressure(m, frame, fps)
        if p: events.append(p)
        return events

    def _shot(self, m, frame, fps):
        if frame - self.last_shot < self.SHOT_CD: return None
        if m["goal_zone_motion"] > 0.12 and m["flow_magnitude"] > 2.5 and m["avg_motion"] > 0.04:
            conf = min(1.0, m["goal_zone_motion"]*3.5 + min(m["flow_magnitude"]/8.0,0.4) + min(m["avg_motion"]*5,0.3))
            if conf > 0.45:
                self.last_shot = frame
                return DetectedEvent("shot", frame/fps, round(conf,3), frame, {"goal_zone_motion": round(m["goal_zone_motion"],4)})
        return None

    def _goal(self, m, frame, fps):
        if frame - self.last_goal < self.GOAL_CD: return None
        if m["goal_zone_motion"] > 0.20 and m["avg_motion"] > 0.10 and m["flow_magnitude"] > 4.0:
            conf = min(1.0, m["goal_zone_motion"]*2.5 + m["avg_motion"]*2.0)
            if conf > 0.55:
                self.last_goal = frame
                return DetectedEvent("goal", frame/fps, round(conf,3), frame, {"inferred": True})
        return None

    def _pressure(self, m, frame, fps):
        if frame - self.last_pressure < self.PRESSURE_CD: return None
        if len(self.pressure_buf) < 60: return None
        recent = list(self.pressure_buf)[-60:]
        ratio = sum(1 for v in recent if v > 0.08) / 60
        avg = np.mean(recent)
        if ratio > 0.65 and avg > 0.09:
            conf = min(1.0, ratio*0.7 + min(avg*4,0.4))
            if conf > 0.50:
                self.last_pressure = frame
                return DetectedEvent("pressure", frame/fps, round(conf,3), frame, {"ratio": round(ratio,3)})
        return None

class VideoProcessingEngine:
    def __init__(self, game_id, source_type, source):
        self.game_id = game_id
        self.source_type = source_type
        self.source = source
        self.running = False
        self.frame_count = 0

    async def run(self):
        self.running = True
        logger.info(f"[{self.game_id}] Processing: {self.source_type}")
        cap = self._open()
        if not cap or not cap.isOpened():
            logger.error(f"Cannot open: {self.source}")
            return
        fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
        w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        analyzer = MotionAnalyzer(w, h)
        detector = EventDetector()
        every = max(1, int(fps/15))
        async with httpx.AsyncClient(timeout=10.0) as client:
            while self.running:
                ret, frame = cap.read()
                if not ret:
                    if self.source_type in ("rtsp","webcam"):
                        await asyncio.sleep(1); cap = self._open(); continue
                    else: break
                self.frame_count += 1
                if self.frame_count % every != 0: continue
                try:
                    metrics = analyzer.update(frame)
                    for evt in detector.analyze(metrics, self.frame_count, fps):
                        clock = f"{int(evt.timestamp//60):02d}:{int(evt.timestamp%60):02d}"
                        logger.info(f"[{self.game_id}] {evt.event_type} @ {clock} conf={evt.confidence}")
                        await self._post(client, evt, clock)
                except Exception as e:
                    logger.error(f"Frame error: {e}")
                await asyncio.sleep(0)
        cap.release()

    def _open(self):
        try:
            if self.source_type == "rtsp": cap = cv2.VideoCapture(self.source, cv2.CAP_FFMPEG); cap.set(cv2.CAP_PROP_BUFFERSIZE,1)
            elif self.source_type == "webcam": cap = cv2.VideoCapture(int(self.source) if self.source.isdigit() else 0)
            else: cap = cv2.VideoCapture(self.source)
            return cap
        except Exception as e:
            logger.error(f"Open error: {e}"); return None

    async def _post(self, client, evt, clock):
        try:
            await client.post(f"{BACKEND_URL}/api/v1/events", json={
                "game_id": self.game_id, "event_type": evt.event_type,
                "timestamp": evt.timestamp, "game_clock": clock,
                "confidence": evt.confidence, "metadata": evt.metadata,
            })
        except Exception as e:
            logger.warning(f"Post failed: {e}")
