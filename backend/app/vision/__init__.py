"""Image-input pipeline (Phase 4 — not yet implemented).

When this lands, expect:
- preprocess.py: OpenCV warp / deskew / Otsu / Sauvola
- segment.py:    formula-vs-text segmentation
- ocr_math.py:   pix2tex (default), Nougat (PDF), Mathpix (premium)
- ocr_text.py:   Tesseract / EasyOCR
- semantic.py:   Anthropic Claude as a *classifier only* (never resolver)
- pdf_loader.py: pdf2image
"""
