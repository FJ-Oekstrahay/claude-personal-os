---
name: Pillow JPEG/WEBP EXIF stripping — explicit empty bytes required
description: img.save() without exif parameter does NOT strip EXIF for JPEG/WEBP; must pass empty bytes
type: feedback
---

## Rule

When using Python Pillow to remove EXIF metadata from JPEG or WEBP images, calling `img.save(path)` without specifying the `exif` parameter will **not** strip EXIF data — it will preserve existing EXIF (or copy it from source).

To actually strip EXIF:

```python
from PIL import Image

img = Image.open('source.jpg')
# This DOES NOT strip EXIF:
img.save('output.jpg')

# This DOES strip EXIF:
img.save('output.jpg', exif=b'')
```

**Correct pattern for JPEG, WEBP, and PNG:**

```python
def strip_exif(input_path, output_path):
    """Remove all EXIF data from image."""
    img = Image.open(input_path)
    
    # Remove EXIF from JPEG/WEBP
    data = list(img.getdata())
    image_without_exif = Image.new(img.mode, img.size)
    image_without_exif.putdata(data)
    
    # For JPEG/WEBP, must pass exif=b'' to actually remove it
    image_without_exif.save(output_path, exif=b'')
```

## Why this matters

**Session context:** Session 2026-04-23 implemented OSD profile library with image export feature (save OSD preview as PNG/JPEG). Initial code used `img.save()` without `exif=b''`, meaning GPS coordinates and timestamps from uploaded images would remain embedded in exported previews.

**Risk:** Pilot uploads crash photo with GPS location (EXIF), exports OSD preview, shares preview on forum or Discord — GPS home location is now public. This is a privacy leak.

## How to apply

1. **File uploads:** When accepting image uploads (blackbox analysis, crash photos, etc.), always strip EXIF before storing:
   ```python
   def accept_upload(uploaded_file):
       img = Image.open(uploaded_file)
       # Remove EXIF
       img.save(
           f'/tmp/upload_{uuid}.jpg',
           exif=b''
       )
   ```

2. **Image exports:** When generating and exporting images, ensure EXIF is stripped:
   ```python
   def export_osd_preview(osd_config, output_path):
       # Generate OSD canvas
       canvas = generate_canvas(osd_config)
       # Save with EXIF stripped
       canvas.save(output_path, exif=b'')
   ```

3. **Testing:** Verify EXIF is gone:
   ```bash
   exiftool output.jpg | grep GPS
   # Should return nothing
   ```

4. **Code review:** When seeing `img.save()` in image handling code, always ask: "Is EXIF stripping needed here?" If the answer is yes or "maybe", add `exif=b''`.

## Edge cases

- **PNG:** Doesn't carry EXIF natively, but may carry other metadata. Pillow's PNG handling is cleaner; `img.save(path)` is safe for PNG.
- **GIF:** Doesn't support EXIF; safe.
- **WEBP:** Same as JPEG — requires `exif=b''` to strip.

## Related

- [[image_exif_stripping_pillow]] — older playbook with same content (consider consolidating)
