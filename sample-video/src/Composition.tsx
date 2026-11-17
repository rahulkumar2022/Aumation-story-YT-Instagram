import React from "react";
import {
  Audio,
  CalculateMetadataFunction,
  Composition,
  Img,
  interpolate,
  Sequence,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";

type VideoProps = {
  durationInFrames?: number;
};

/* =========================================================================
   1. SHARED COMPONENTS
========================================================================= */

const TopProgressBar: React.FC<{ color?: string }> = ({ color = "#38bdf8" }) => {
  const frame = useCurrentFrame();
  const { durationInFrames } = useVideoConfig();
  const progress = (frame / durationInFrames) * 100;

  return (
    <div
      style={{
        position: "absolute",
        top: 0,
        left: 0,
        width: "100%",
        height: 10,
        backgroundColor: "rgba(255,255,255,0.2)",
        zIndex: 100,
      }}
    >
      <div
        style={{
          width: `${progress}%`,
          height: "100%",
          backgroundColor: color,
          boxShadow: `0 0 12px ${color}`,
        }}
      />
    </div>
  );
};

const SubtitleBadge: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <div
    style={{
      position: "absolute",
      bottom: 75,
      left: 0,
      right: 0,
      display: "flex",
      justifyContent: "center",
      zIndex: 50,
    }}
  >
    <div
      style={{
        backgroundColor: "rgba(10, 10, 18, 0.88)",
        backdropFilter: "blur(14px)",
        padding: "18px 44px",
        borderRadius: 9999,
        border: "1px solid rgba(255, 255, 255, 0.18)",
        boxShadow: "0 12px 35px rgba(0,0,0,0.7)",
        color: "#ffffff",
        fontSize: 34,
        fontWeight: 700,
        fontFamily: "system-ui, -apple-system, sans-serif",
        textAlign: "center",
        maxWidth: "80%",
        lineHeight: 1.3,
      }}
    >
      {children}
    </div>
  </div>
);

const Vignette: React.FC<{ intensity?: number }> = ({ intensity = 0.65 }) => (
  <div
    style={{
      position: "absolute",
      inset: 0,
      background: `radial-gradient(circle, rgba(0,0,0,0) 55%, rgba(0,0,0,${intensity}) 100%)`,
      pointerEvents: "none",
    }}
  />
);

const ChapterTag: React.FC<{ text: string; color?: string }> = ({
  text,
  color = "#38bdf8",
}) => (
  <div
    style={{
      position: "absolute",
      top: 45,
      left: 60,
      display: "flex",
      alignItems: "center",
      gap: 12,
      zIndex: 50,
    }}
  >
    <div
      style={{
        width: 10,
        height: 10,
        borderRadius: "50%",
        backgroundColor: color,
        boxShadow: `0 0 10px ${color}`,
      }}
    />
    <span
      style={{
        color: "rgba(255, 255, 255, 0.8)",
        fontSize: 20,
        fontWeight: 800,
        letterSpacing: "0.1em",
        textTransform: "uppercase",
        fontFamily: "system-ui, -apple-system, sans-serif",
      }}
    >
      {text}
    </span>
  </div>
);

/* =========================================================================
   2. REEL / SHORTS FORMAT (9:16 - 1080 x 1920, 30-60s)
========================================================================= */

const ShortScene1: React.FC = () => {
  const frame = useCurrentFrame();
  const scale = interpolate(frame, [0, 480], [1.0, 1.12], { extrapolateRight: "clamp" });

  return (
    <div style={{ position: "absolute", inset: 0, backgroundColor: "#000", overflow: "hidden" }}>
      <Img
        src={staticFile("short_p1.jpg")}
        style={{
          width: "100%",
          height: "100%",
          objectFit: "cover",
          transform: `scale(${scale})`,
          transformOrigin: "50% 60%",
        }}
      />
      <div
        style={{
          position: "absolute",
          inset: 0,
          background: "linear-gradient(to bottom, rgba(0,0,0,0.4) 0%, rgba(0,0,0,0) 25%, rgba(0,0,0,0) 70%, rgba(0,0,0,0.85) 100%)",
        }}
      />
      <div style={{ position: "absolute", top: 80, left: 0, right: 0, display: "flex", justifyContent: "center" }}>
        <div style={{ backgroundColor: "#dc2626", color: "#fff", padding: "8px 24px", borderRadius: 9999, fontSize: 22, fontWeight: 900, letterSpacing: "0.08em" }}>
          POV STORYTIME
        </div>
      </div>
      <div style={{ position: "absolute", bottom: 180, left: 48, right: 48, display: "flex", justifyContent: "center" }}>
        <div style={{ backgroundColor: "rgba(10, 10, 15, 0.90)", backdropFilter: "blur(16px)", padding: "26px 36px", borderRadius: 24, border: "1px solid rgba(255, 255, 255, 0.2)", color: "#fff", fontSize: 40, fontWeight: 800, textAlign: "center", lineHeight: 1.3 }}>
          Your brother brags at family dinner that he got approved for a <span style={{ color: "#facc15" }}>luxury penthouse</span>...
        </div>
      </div>
    </div>
  );
};

const ShortScene2: React.FC = () => {
  const frame = useCurrentFrame();
  const scale = interpolate(frame, [0, 400], [1.02, 1.13], { extrapolateRight: "clamp" });
  const fadeIn = interpolate(frame, [0, 10], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });

  return (
    <div style={{ position: "absolute", inset: 0, backgroundColor: "#000", overflow: "hidden", opacity: fadeIn }}>
      <Img
        src={staticFile("short_p2.jpg")}
        style={{
          width: "100%",
          height: "100%",
          objectFit: "cover",
          transform: `scale(${scale})`,
          transformOrigin: "50% 50%",
        }}
      />
      <div style={{ position: "absolute", inset: 0, background: "linear-gradient(to bottom, rgba(0,0,0,0.4) 0%, rgba(0,0,0,0) 25%, rgba(0,0,0,0) 70%, rgba(0,0,0,0.85) 100%)" }} />
      <div style={{ position: "absolute", top: 80, left: 0, right: 0, display: "flex", justifyContent: "center" }}>
        <div style={{ backgroundColor: "#2563eb", color: "#fff", padding: "8px 24px", borderRadius: 9999, fontSize: 22, fontWeight: 900, letterSpacing: "0.08em" }}>
          SPEAKERPHONE ON
        </div>
      </div>
      <div style={{ position: "absolute", bottom: 180, left: 48, right: 48, display: "flex", justifyContent: "center" }}>
        <div style={{ backgroundColor: "rgba(10, 10, 15, 0.90)", backdropFilter: "blur(16px)", padding: "26px 36px", borderRadius: 24, border: "1px solid rgba(255, 255, 255, 0.2)", color: "#fff", fontSize: 40, fontWeight: 800, textAlign: "center", lineHeight: 1.3 }}>
          He puts the property manager on <span style={{ color: "#38bdf8" }}>speakerphone</span> so everyone can hear...
        </div>
      </div>
    </div>
  );
};

const ShortScene3: React.FC = () => {
  const frame = useCurrentFrame();
  const scale = interpolate(frame, [0, 700], [1.0, 1.10], { extrapolateRight: "clamp" });
  const fadeIn = interpolate(frame, [0, 10], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const isTwistPart = frame > 280;

  return (
    <div style={{ position: "absolute", inset: 0, backgroundColor: "#000", overflow: "hidden", opacity: fadeIn }}>
      <Img
        src={staticFile("short_p3.jpg")}
        style={{
          width: "100%",
          height: "100%",
          objectFit: "cover",
          transform: `scale(${scale})`,
          transformOrigin: "50% 50%",
        }}
      />
      <div style={{ position: "absolute", inset: 0, background: "linear-gradient(to bottom, rgba(0,0,0,0.4) 0%, rgba(0,0,0,0) 25%, rgba(0,0,0,0) 70%, rgba(0,0,0,0.9) 100%)" }} />
      <div style={{ position: "absolute", top: 80, left: 0, right: 0, display: "flex", justifyContent: "center" }}>
        <div style={{ backgroundColor: isTwistPart ? "#16a34a" : "#dc2626", color: "#fff", padding: "8px 24px", borderRadius: 9999, fontSize: 22, fontWeight: 900, letterSpacing: "0.08em" }}>
          {isTwistPart ? "INSTANT KARMA" : "APPLICATION REJECTED"}
        </div>
      </div>
      <div style={{ position: "absolute", bottom: 180, left: 48, right: 48, display: "flex", justifyContent: "center" }}>
        {!isTwistPart ? (
          <div style={{ backgroundColor: "rgba(10, 10, 15, 0.92)", backdropFilter: "blur(16px)", padding: "26px 36px", borderRadius: 24, border: "1px solid rgba(239, 68, 68, 0.4)", color: "#fff", fontSize: 40, fontWeight: 800, textAlign: "center", lineHeight: 1.3 }}>
            Manager: &quot;Sorry sir, the building owner just <span style={{ color: "#ef4444" }}>personally rejected</span> your lease.&quot;
          </div>
        ) : (
          <div style={{ backgroundColor: "rgba(10, 10, 15, 0.92)", backdropFilter: "blur(16px)", padding: "26px 36px", borderRadius: 24, border: "1px solid rgba(34, 197, 94, 0.4)", color: "#fff", fontSize: 40, fontWeight: 800, textAlign: "center", lineHeight: 1.3 }}>
            He stares in disbelief... not knowing <span style={{ color: "#4ade80" }}>YOU own the building</span>.
          </div>
        )}
      </div>
    </div>
  );
};

export const DedicatedShortComponent: React.FC<VideoProps> = () => {
  const { durationInFrames } = useVideoConfig();
  const s1Duration = Math.floor(durationInFrames * 0.32);
  const s2Duration = Math.floor(durationInFrames * 0.28);
  const s3Duration = durationInFrames - s1Duration - s2Duration;

  return (
    <div style={{ flex: 1, backgroundColor: "#000", position: "relative" }}>
      <TopProgressBar color="#ef4444" />

      {/* 1. Main Voice Narration */}
      <Audio src={staticFile("short_narration.mp3")} volume={1.0} />

      {/* 2. Emotional Background Score (Escalating Cinematic Tension) */}
      <Audio
        src={staticFile("bgm_escalation.mp3")}
        volume={(f) =>
          interpolate(
            f,
            [0, s1Duration, s1Duration + s2Duration, durationInFrames],
            [0.18, 0.24, 0.14, 0.38],
            { extrapolateRight: "clamp" }
          )
        }
      />

      {/* 3. Emotional SFX: Phone Ring on Speakerphone Scene */}
      <Sequence from={s1Duration + 10} durationInFrames={90}>
        <Audio src={staticFile("sfx/phone_ring.wav")} volume={0.4} />
      </Sequence>

      {/* 4. Emotional SFX: Tension Riser before the Rejection */}
      <Sequence from={s1Duration + s2Duration - 110} durationInFrames={120}>
        <Audio src={staticFile("sfx/tension_riser.wav")} volume={0.35} />
      </Sequence>

      {/* 5. Emotional SFX: Cinematic Sub Boom / Drop on The Rejection Twist */}
      <Sequence from={s1Duration + s2Duration} durationInFrames={80}>
        <Audio src={staticFile("sfx/sub_boom.wav")} volume={0.8} />
      </Sequence>

      {/* Visual Sequences */}
      <Sequence durationInFrames={s1Duration + 10}>
        <ShortScene1 />
      </Sequence>
      <Sequence from={s1Duration} durationInFrames={s2Duration + 10}>
        <ShortScene2 />
      </Sequence>
      <Sequence from={s1Duration + s2Duration} durationInFrames={s3Duration}>
        <ShortScene3 />
      </Sequence>
    </div>
  );
};

/* =========================================================================
   3. LONG-FORM EPISODE (16:9 - 1920 x 1080, 8 - 20 MINUTES)
========================================================================= */

const LongScene: React.FC<{
  img: string;
  chapter: string;
  subtitle: React.ReactNode;
  color?: string;
  origin?: string;
}> = ({ img, chapter, subtitle, color = "#38bdf8", origin = "50% 50%" }) => {
  const frame = useCurrentFrame();
  const scale = interpolate(frame, [0, 450], [1.0, 1.08], { extrapolateRight: "clamp" });
  const fadeIn = interpolate(frame, [0, 12], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });

  return (
    <div style={{ position: "absolute", inset: 0, overflow: "hidden", backgroundColor: "#000", opacity: fadeIn }}>
      <Img src={staticFile(img)} style={{ width: "100%", height: "100%", objectFit: "cover", transform: `scale(${scale})`, transformOrigin: origin }} />
      <Vignette intensity={0.7} />
      <ChapterTag text={chapter} color={color} />
      <SubtitleBadge>{subtitle}</SubtitleBadge>
    </div>
  );
};

export const FullEpisodeLongComponent: React.FC<VideoProps> = () => {
  const { durationInFrames } = useVideoConfig();
  const chunk = Math.floor(durationInFrames / 5);

  return (
    <div style={{ flex: 1, backgroundColor: "#000", position: "relative" }}>
      {/* 1. Main Voice Narration */}
      <Audio src={staticFile("long_narration.mp3")} volume={1.0} />

      {/* 2. Emotional Cinematic Score */}
      <Audio
        src={staticFile("bgm_escalation.mp3")}
        volume={(f) =>
          interpolate(
            f,
            [0, chunk * 2, chunk * 3, chunk * 4, durationInFrames],
            [0.16, 0.22, 0.28, 0.12, 0.38],
            { extrapolateRight: "clamp" }
          )
        }
      />

      {/* 3. Emotional SFX: Phone Ring on Chapter 4 */}
      <Sequence from={chunk * 3 + 10} durationInFrames={90}>
        <Audio src={staticFile("sfx/phone_ring.wav")} volume={0.45} />
      </Sequence>

      {/* 4. Emotional SFX: Tension Riser leading into the climax */}
      <Sequence from={chunk * 4 - 110} durationInFrames={120}>
        <Audio src={staticFile("sfx/tension_riser.wav")} volume={0.35} />
      </Sequence>

      {/* 5. Emotional SFX: Sub Boom / Drop on Chapter 5 (The Reveal) */}
      <Sequence from={chunk * 4} durationInFrames={80}>
        <Audio src={staticFile("sfx/sub_boom.wav")} volume={0.85} />
      </Sequence>

      {/* Chapter 1: The Sunday Ritual */}
      <Sequence durationInFrames={chunk + 15}>
        <LongScene
          img="long_s1.jpg"
          chapter="Chapter 1: The Sunday Ritual"
          color="#facc15"
          origin="35% 50%"
          subtitle={<>Marcus pulls up in his leased Mercedes... <span style={{ color: "#facc15" }}>the golden child</span>.</>}
        />
      </Sequence>

      {/* Chapter 2: The Living Room Interrogation */}
      <Sequence from={chunk} durationInFrames={chunk + 15}>
        <LongScene
          img="long_s2.jpg"
          chapter="Chapter 2: The Family Dinner"
          color="#fb923c"
          origin="70% 45%"
          subtitle={<>Marcus boasts his promotion... your dad asks if you&apos;ve found a <span style={{ color: "#fb923c" }}>real job</span>.</>}
        />
      </Sequence>

      {/* Chapter 3: The Mailroom Offer */}
      <Sequence from={chunk * 2} durationInFrames={chunk + 15}>
        <LongScene
          img="long_s3.jpg"
          chapter="Chapter 3: The Mailroom Offer"
          color="#38bdf8"
          origin="55% 75%"
          subtitle={<>Marcus slides his card: <span style={{ color: "#38bdf8" }}>Senior Regional Director</span>. &quot;Maybe you can start in the mailroom.&quot;</>}
        />
      </Sequence>

      {/* Chapter 4: The Corporate Call */}
      <Sequence from={chunk * 3} durationInFrames={chunk + 15}>
        <LongScene
          img="long_s4.jpg"
          chapter="Chapter 4: The Corporate Call"
          color="#ef4444"
          origin="50% 85%"
          subtitle={<>His corporate phone rings with an <span style={{ color: "#ef4444" }}>urgent call</span>... put on speaker for all to hear.</>}
        />
      </Sequence>

      {/* Chapter 5 & 6: Checkmate & Reveal */}
      <Sequence from={chunk * 4} durationInFrames={durationInFrames - chunk * 4}>
        <LongScene
          img="long_s5.jpg"
          chapter="Chapter 5: Checkmate"
          color="#22c55e"
          origin="50% 60%"
          subtitle={<>Marcus turns pale. Your phone buzzes: <span style={{ color: "#22c55e", fontWeight: 800 }}>&quot;Acquisition Complete, Chairman.&quot;</span> Pass the salt.</>}
        />
      </Sequence>
    </div>
  );
};

/* =========================================================================
   COMPOSITION METADATA CALCULATORS & EXPORTS
========================================================================= */

const calculateMetadataLong: CalculateMetadataFunction<VideoProps> = ({ props }) => {
  return {
    durationInFrames: props.durationInFrames || 2102,
  };
};

const calculateMetadataShort: CalculateMetadataFunction<VideoProps> = ({ props }) => {
  return {
    durationInFrames: props.durationInFrames || 600,
  };
};

export const MyComposition = () => {
  return (
    <>
      <Composition
        id="FullEpisodeLong"
        component={FullEpisodeLongComponent}
        durationInFrames={2102}
        fps={30}
        width={1920}
        height={1080}
        calculateMetadata={calculateMetadataLong}
      />

      <Composition
        id="DedicatedShort"
        component={DedicatedShortComponent}
        durationInFrames={600}
        fps={30}
        width={1080}
        height={1920}
        calculateMetadata={calculateMetadataShort}
      />
    </>
  );
};
