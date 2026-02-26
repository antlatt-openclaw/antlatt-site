# Remotion Composition Patterns

## Project Structure

```
my-video/
├── src/
│   ├── index.ts           # registerRoot entry point
│   ├── Root.tsx           # <Composition> declarations
│   └── MyVideo/
│       ├── index.tsx      # Main component
│       └── styles.ts      # Optional styles
├── public/                # Static assets (images, fonts, audio)
├── remotion.config.ts     # Remotion config
├── package.json
└── tsconfig.json
```

## Basic Composition (Root.tsx)

```tsx
import { Composition } from "remotion";
import { MyVideo } from "./MyVideo";

export const RemotionRoot = () => (
  <>
    <Composition
      id="MyVideo"
      component={MyVideo}
      durationInFrames={300}  // 10s at 30fps
      fps={30}
      width={1920}
      height={1080}
      defaultProps={{
        title: "Hello World",
      }}
    />
  </>
);
```

## Common Aspect Ratios

- **16:9 landscape (YouTube)**: 1920x1080 or 1280x720
- **9:16 vertical (Reels/TikTok/Shorts)**: 1080x1920
- **4:5 Instagram feed**: 1080x1350
- **1:1 square**: 1080x1080

## Key Remotion APIs

```tsx
import {
  useCurrentFrame,    // Current frame number
  useVideoConfig,     // { fps, width, height, durationInFrames }
  interpolate,        // Map frame ranges to values
  spring,             // Physics-based spring animation
  Sequence,           // Time-offset children
  AbsoluteFill,       // Full-frame container
  Img,                // Image component (preloads)
  Audio,              // Audio component
  Video,              // Video component
  staticFile,         // Reference files in public/
  delayRender,        // Hold render until async ready
  continueRender,     // Resume after delayRender
} from "remotion";
```

## Animation Example

```tsx
import { useCurrentFrame, interpolate, spring, useVideoConfig, AbsoluteFill } from "remotion";

export const FadeInText: React.FC<{ text: string }> = ({ text }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const opacity = interpolate(frame, [0, 30], [0, 1], {
    extrapolateRight: "clamp",
  });

  const scale = spring({ frame, fps, config: { damping: 200 } });

  return (
    <AbsoluteFill className="items-center justify-center bg-black">
      <h1
        style={{ opacity, transform: `scale(${scale})` }}
        className="text-white text-7xl font-bold"
      >
        {text}
      </h1>
    </AbsoluteFill>
  );
};
```

## Sequences (Timing)

```tsx
<AbsoluteFill>
  <Sequence from={0} durationInFrames={60}>
    <Intro />
  </Sequence>
  <Sequence from={60} durationInFrames={120}>
    <MainContent />
  </Sequence>
  <Sequence from={180}>
    <Outro />
  </Sequence>
</AbsoluteFill>
```

## Input Props (Dynamic Data)

Pass data via `--props` flag or `defaultProps`:

```tsx
// Component
export const MyVideo: React.FC<{ title: string; items: string[] }> = ({
  title,
  items,
}) => { ... };

// Render with props
// npx remotion render MyVideo --props='{"title":"Demo","items":["a","b"]}'
```

## Audio

```tsx
import { Audio, staticFile, Sequence } from "remotion";

<Sequence from={0}>
  <Audio src={staticFile("bgm.mp3")} volume={0.5} />
</Sequence>
```

## Fetching Data (delayRender)

```tsx
const [data, setData] = useState(null);
const [handle] = useState(() => delayRender());

useEffect(() => {
  fetch("https://api.example.com/data")
    .then((r) => r.json())
    .then((d) => {
      setData(d);
      continueRender(handle);
    });
}, []);
```

## TailwindCSS

Remotion supports Tailwind out of the box when scaffolded with `--tailwind`. Use `className` as normal on any element.

## Main Video Component

```tsx
import {
  AbsoluteFill,
  Sequence,
  useCurrentFrame,
  useVideoConfig,
  Audio,
  staticFile,
} from "remotion";
import { IntroScene } from "./scenes/IntroScene";
import { FeatureScene } from "./scenes/FeatureScene";
import { CtaScene } from "./scenes/CtaScene";
import { AnimatedBackground } from "./components/AnimatedBackground";

export const MyVideo = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  return (
    <AbsoluteFill className="bg-gray-900">
      {/* Background audio - persists across scenes */}
      <Audio src={staticFile("audio/bg-music.mp3")} volume={0.3} />

      {/* Persistent animated background - OUTSIDE sequences */}
      <AnimatedBackground frame={frame} />

      {/* Scene sequences with overlap for smooth transitions */}
      <Sequence from={0} durationInFrames={90}>
        <IntroScene />
      </Sequence>

      <Sequence from={70} durationInFrames={120}>
        {/* Starts 20 frames before intro ends */}
        <FeatureScene />
      </Sequence>

      <Sequence from={170} durationInFrames={130}>
        <CtaScene />
      </Sequence>
    </AbsoluteFill>
  );
};
```

## Scene Component Pattern

```tsx
import { AbsoluteFill, useCurrentFrame, useVideoConfig, interpolate, spring } from "remotion";
import { TextReveal } from "../components/TextReveal";
import { CTAButton } from "../components/CTAButton";

export const IntroScene = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const titleOpacity = interpolate(frame, [0, 20], [0, 1], {
    extrapolateRight: "clamp",
  });

  const titleY = interpolate(frame, [0, 20], [50, 0], {
    extrapolateRight: "clamp",
  });

  return (
    <AbsoluteFill className="flex flex-col items-center justify-center gap-8">
      <h1
        style={{ opacity: titleOpacity, transform: `translateY(${titleY}px)` }}
        className="text-8xl font-black text-white text-center"
      >
        Welcome
      </h1>

      <TextReveal
        text="Build amazing videos with code"
        frame={frame - 15}
        fps={fps}
      />

      <CTAButton text="Get Started" frame={frame - 40} fps={fps} />
    </AbsoluteFill>
  );
};
```

## Multi-Column Layout

```tsx
import { AbsoluteFill, Sequence, useCurrentFrame, useVideoConfig } from "remotion";
import { FeatureCard } from "../components/FeatureCard";
import { Zap, Shield, Rocket } from "lucide-react";

export const FeatureScene = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const features = [
    { icon: Zap, title: "Fast", description: "Render in seconds" },
    { icon: Shield, title: "Secure", description: "Enterprise ready" },
    { icon: Rocket, title: "Scalable", description: "Grow without limits" },
  ];

  return (
    <AbsoluteFill className="flex items-center justify-center">
      <div className="grid grid-cols-3 gap-8 px-20">
        {features.map((feature, i) => (
          <FeatureCard
            key={i}
            icon={feature.icon}
            title={feature.title}
            description={feature.description}
            delay={i * 10}
          />
        ))}
      </div>
    </AbsoluteFill>
  );
};
```

## Wipe Transition

```tsx
import { AbsoluteFill, useCurrentFrame, interpolate } from "remotion";

export const WipeTransition = ({
  children,
  frame,
  direction = "left",
  color = "#000",
}: {
  children: React.ReactNode;
  frame: number;
  direction?: "left" | "right" | "up" | "down";
  color?: string;
}) => {
  const wipeProgress = interpolate(frame, [0, 20], [0, 100], {
    extrapolateRight: "clamp",
  });

  const transforms = {
    left: `translateX(-${100 - wipeProgress}%)`,
    right: `translateX(${100 - wipeProgress}%)`,
    up: `translateY(-${100 - wipeProgress}%)`,
    down: `translateY(${100 - wipeProgress}%)`,
  };

  return (
    <AbsoluteFill style={{ overflow: "hidden" }}>
      <div
        style={{
          position: "absolute",
          inset: 0,
          transform: transforms[direction],
          background: color,
          zIndex: 10,
        }}
      />
      <div style={{ opacity: wipeProgress > 50 ? 1 : 0 }}>{children}</div>
    </AbsoluteFill>
  );
};
```

## Clip Path Reveal

```tsx
import { AbsoluteFill, useCurrentFrame, interpolate } from "remotion";

export const CircleReveal = ({
  children,
  frame,
}: {
  children: React.ReactNode;
  frame: number;
}) => {
  const clipProgress = interpolate(frame, [0, 30], [0, 150], {
    extrapolateRight: "clamp",
  });

  return (
    <AbsoluteFill
      style={{
        clipPath: `circle(${clipProgress}% at 50% 50%)`,
      }}
    >
      {children}
    </AbsoluteFill>
  );
};
```

## Staggered Children Animation

```tsx
import { useCurrentFrame, interpolate, spring, useVideoConfig } from "remotion";

export const StaggeredList = ({ items }: { items: string[] }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  return (
    <div className="flex flex-col gap-4">
      {items.map((item, i) => {
        const delay = i * 5;
        const localFrame = frame - delay;

        const scale = spring({
          frame: localFrame,
          fps,
          config: { damping: 12, stiffness: 200 },
        });

        const opacity = interpolate(localFrame, [0, 10], [0, 1], {
          extrapolateRight: "clamp",
        });

        return (
          <div
            key={i}
            style={{
              transform: `scale(${scale})`,
              opacity,
            }}
            className="text-white text-2xl font-semibold"
          >
            {item}
          </div>
        );
      })}
    </div>
  );
};
```

## Calculating Duration from Scenes

```tsx
const SCENES = [
  { name: "intro", duration: 3 },    // 3 seconds
  { name: "features", duration: 5 }, // 5 seconds
  { name: "cta", duration: 2 },      // 2 seconds
];

const FPS = 30;

const calculateDuration = (scenes: typeof SCENES) => {
  return scenes.reduce((acc, scene) => acc + scene.duration * FPS, 0);
};

// Usage in Root.tsx
<Composition
  id="MyVideo"
  component={MyVideo}
  durationInFrames={calculateDuration(SCENES)}
  fps={FPS}
  width={1920}
  height={1080}
/>
```

## Responsive Sizing

```tsx
import { useVideoConfig } from "remotion";

export const ResponsiveText = ({
  children,
  baseSize = 64,
}: {
  children: React.ReactNode;
  baseSize?: number;
}) => {
  const { width } = useVideoConfig();

  // Scale text based on 1920px base
  const scale = width / 1920;
  const fontSize = baseSize * scale;

  return <span style={{ fontSize }}>{children}</span>;
};
```