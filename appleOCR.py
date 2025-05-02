#!/usr/bin/env python3
import pathlib
import sys
from pdf2image import convert_from_path
from PIL import Image

import Quartz
import Vision
from Cocoa import NSURL
from Foundation import NSDictionary
from wurlitzer import pipes

def image_to_text(img_path, languages=["ko", "en-US"]):
    # 1) CIImage 로딩 (Quartz 로그 억제)
    input_url = NSURL.fileURLWithPath_(str(img_path))
    with pipes():
        ciimg = Quartz.CIImage.imageWithContentsOfURL_(input_url)

    # 2) RequestHandler 생성
    handler = Vision.VNImageRequestHandler.alloc() \
              .initWithCIImage_options_(ciimg, NSDictionary.dictionary())

    results = []

    # 3) Completion handler
    def _completion(req, err):
        if err:
            print("Vision error:", err)
        else:
            for obs in req.results():
                cand = obs.topCandidates_(1)[0]
                results.append((cand.string(), cand.confidence()))

    # 4) VNRecognizeTextRequest 초기화 (기본 init)
    req = Vision.VNRecognizeTextRequest.alloc() \
          .initWithCompletionHandler_(_completion)

    # 5) Revision 3 설정 → macOS/iOS Vision에서 한국어 인식 활성화 🔑
    req.setRevision_(Vision.VNRecognizeTextRequestRevision3)  # :contentReference[oaicite:0]{index=0}

    # 6) Accurate 모드 + 언어 + 교정 옵션
    req.setRecognitionLevel_(Vision.VNRequestTextRecognitionLevelAccurate)
    req.setRecognitionLanguages_(languages)
    req.setUsesLanguageCorrection_(True)

    # 7) OCR 수행
    handler.performRequests_error_([req], None)
    return results

def pdf_to_text(pdf_path, dpi=300, languages=["ko", "en-US"]):
    text_pages = []
    pages = convert_from_path(str(pdf_path), dpi=dpi)

    tmp_folder = pathlib.Path("/tmp/ocr_pages")
    tmp_folder.mkdir(exist_ok=True)

    for i, pil_img in enumerate(pages, start=1):
        img_path = tmp_folder / f"page_{i:03}.png"
        pil_img.save(img_path, format="PNG")

        annotations = image_to_text(img_path, languages=languages)
        text_pages.append({
            "page": i,
            "lines": [t for t,_ in annotations]
        })

        img_path.unlink()

    return text_pages

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("사용법: python appleOCR.py your_book.pdf")
        sys.exit(1)

    pdf = pathlib.Path(sys.argv[1])
    print(f"OCR 시작: {pdf.name}")

    pages = pdf_to_text(pdf, dpi=300, languages=["ko", "en-US"])

    out_txt = pathlib.Path("ocr_output.txt")
    with out_txt.open("w", encoding="utf-8") as f:
        for p in pages:
            f.write(f"--- page {p['page']} ---\n")
            f.write("\n".join(p["lines"]) + "\n\n")

    print(f"OCR 완료: {out_txt.resolve()}")

