# Animation Rules

## Motion Principles

- Motion is functional feedback, not decoration. It should clarify working, selected, loading, or time-passing states.
- Use stepped pixel motion for game-room elements. Avoid smooth floating, bokeh, blur-heavy, or web-hero animation.
- Respect reduced-motion users before adding new motion: gate nonessential loops with `@media (prefers-reduced-motion: reduce)`.

## Existing Motion

- Working workstation bob:
  - Selector pattern: `.station-scene.working` or fallback `.station-art.working`.
  - Keyframe: `bob`, `1.2s`, `steps(2)`, infinite.
  - Movement: `translateY(-3px)` at 50%.
- Clock:
  - `#clock` updates every second while `state.paused === false`.
  - `#pauseTime` toggles between `Pause Time` and `Resume Time`.
- Toast:
  - `#toast.show` appears immediately and hides after 4200ms.

## Allowed New Motion

- `working`: subtle two-step bob or monitor flicker, max 3px movement.
- `selected`: instant outline, glow, or plate highlight; no layout shift.
- `loading`: small meter shimmer or dot pulse, max 1.5s loop.
- `success/failure`: one short flash under 500ms, then settle into persistent chip color.

## Prohibited Motion

- Continuous camera movement, parallax, bouncing panels, or scrolling marquees.
- Motion that changes panel size, lane width, card height, or grid placement.
- Hover effects that move text enough to cause wrapping.
- Animations on live queue cards that make counts or titles hard to read.

## Implementation Checklist

- All animated elements must have stable width, height, and absolute or grid placement.
- Use `transform` and `opacity` only for animation where possible.
- Add a reduced-motion override that disables infinite loops:

```css
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 0.001ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.001ms !important;
  }
}
```

