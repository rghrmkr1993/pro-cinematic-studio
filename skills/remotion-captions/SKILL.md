---
name: "remotion-captions"
description: "Transcribing, displaying and animating captions"
version: 4.0.534
---

Licence note: Remotion is free only for individuals and for-profit companies with 3 or fewer employees. The owner will not buy a Company License. Use Remotion only for the owner's own freelance or personal work, or if the owner confirms the client has 3 or fewer employees; otherwise use motion-reel or hyperframes (Apache-2.0) instead.

All captions must be processed in JSON. The captions must use the [`Caption`](https://www.remotion.dev/docs/captions/caption.md) type which is the following:

```ts
import type { Caption } from "@remotion/captions";
```

This is the definition:

```ts
type Caption = {
  text: string;
  startMs: number;
  endMs: number;
  timestampMs: number | null;
  confidence: number | null;
  pageBreakAfter?: boolean;
};
```

## Generating captions

To transcribe video and audio files to generate captions, load the [transcribe-captions.md](transcribe-captions.md) file for more instructions.

## Displaying captions

To display captions in your video, load the [display-captions.md](display-captions.md) file for more instructions.

## Importing captions

To import captions from a .srt file, load the [import-srt-captions.md](import-srt-captions.md) file for more instructions.

## Post-creation

After you're done, load this skill: Remotion Best Practices

If not alreay done, open the Remotion Studio, unless instructed otherwise.
