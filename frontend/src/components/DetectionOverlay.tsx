'use client';

// Renders an image with normalized clothing-detection boxes overlaid. Boxes are
// [x0, y0, x1, y1] in [0, 1] relative to the top-left origin. Detections are
// uncertain evidence; labels and scores are shown so reviewers can judge them.

export type OverlayBox = { box: [number, number, number, number]; score: number; label: string };

export function DetectionOverlay({ src, alt, boxes }: { src: string; alt: string; boxes: OverlayBox[] }) {
  return (
    <div className="relative inline-block max-w-full overflow-hidden rounded-lg border border-slate-200">
      {/* eslint-disable-next-line @next/next/no-img-element -- authorized demo image served from the API, not a static asset */}
      <img src={src} alt={alt} className="block max-w-full h-auto" />
      {boxes.map(({ box, score, label }, index) => {
        const [x0, y0, x1, y1] = box;
        const style = {
          left: `${x0 * 100}%`,
          top: `${y0 * 100}%`,
          width: `${Math.max(0, x1 - x0) * 100}%`,
          height: `${Math.max(0, y1 - y0) * 100}%`,
        };
        return (
          <div key={`${label}-${index}`} className="absolute border-2 border-sky-400/90 bg-sky-400/10" style={style}>
            <span className="absolute -top-5 left-0 bg-sky-500 text-white text-[10px] font-semibold px-1.5 py-0.5 rounded whitespace-nowrap">
              {label} · {(score * 100).toFixed(0)}%
            </span>
          </div>
        );
      })}
    </div>
  );
}
