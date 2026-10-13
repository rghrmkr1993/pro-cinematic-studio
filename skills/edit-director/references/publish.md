# Publishing to TikTok via Higgsfield

Only at the user's request and only through the **confirmation form**: you prepare the post, the user checks and
submits the form themselves. Never call the submit tool (`tiktok_publish`) yourself. Publishing spends no credits,
but it is an action on the user's behalf — nothing goes out without their form.

## Steps

1. **The final render is checked** (QA) and meets the platform's requirements: MP4/WebM/MOV, ≤ 1 GB, 3–600 s, both sides
   ≥ 360 px, 23–60 fps. If it does not, re-encode it locally (`ffmpeg … -r 30 -c:v libx264 -crf 18 -c:a aac`).
2. **Upload to Higgsfield** — TikTok accepts only a file from a Higgsfield domain:
   `media_upload(filename="<project>_v<N>.mp4")` → run the returned PUT command (curl) from the sandbox →
   `media_confirm(media_id=…, type="video")` → a link to the file. Check in the tool's response which field of the `media_confirm` response `tiktok_prepare_publish(video_url)` takes.
3. **Account**: `tiktok_accounts` → the `connector_id` of the active account; no accounts — `tiktok_connect`;
   an account error — `tiktok_reconnect`.
4. **Preparation**: `tiktok_prepare_publish(connector_id, mode, media_type="VIDEO", video_url, title, description)`.
   - `mode`: `DIRECT_POST` — straight to the profile, `UPLOAD_TO_DRAFT` — to drafts; if not stated, ask (suggest
     a draft by default).
   - Pre-fill only what the user stated themselves: privacy, comments, duets, stitches, the ad disclosure.
     They will choose the rest in the form.
   - Title and description: suggest the text, but show it before the preparation.
   - **Generated shots.** If the video contains generated shots (`gen/provenance.json`), say so
     and suggest marking the video as AI-generated in the form (fill in `is_aigc` only if the user
     answered).
5. **The form** opens for the user: they check the preview, choose the settings and the platform's music (if needed)
   and submit it. The status after submission: `tiktok_publish_status`.

## What not to do

- Do not publish without an explicit request and without the form; do not bypass the form with other tools.
- Do not upload the user's source footage to Higgsfield without need — publishing needs only the final render.
- Do not promise reach. The "virality" estimate (`virality_predictor`) is a separate tool without a cost preview:
  treat it as paid and run it only via the edit-gen skill after an explicit "yes".
