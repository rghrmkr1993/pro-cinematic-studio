---
name: "remotion-render"
description: "Export a Remotion video"
version: 4.0.534
---

Licence note: Remotion is free only for individuals and for-profit companies with 3 or fewer employees. The owner will not buy a Company License. Use Remotion only for the owner's own freelance or personal work, or if the owner confirms the client has 3 or fewer employees; otherwise use motion-reel or hyperframes (Apache-2.0) instead.

## General rendering strategy

Render a video using:

```
npx remotion render
```

Full list of options: https://www.remotion.dev/docs/cli/render.md

Render a still using:

```
npx remotion still
```

Full list of options: https://www.remotion.dev/docs/cli/still.md

To render several frames as images in one call, use `render --frames`:

```
npx remotion render [composition-id] out/frames --frames=0,30,90 --image-format=png
```

See https://www.remotion.dev/docs/cli/render.md#--frames for more options.

## Transparent videos

See [Transparent videos](./transparent-videos.md) for rendering out a video with transparency.
