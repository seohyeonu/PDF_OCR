from pdf2image import convert_from_path
import pytesseract

# Windows 사용자는 poppler 경로를 명시해야 할 수도 있음
# poppler_path = r'C:\path\to\poppler\bin'
# pages = convert_from_path('example.pdf', poppler_path=poppler_path)

# macOS, Linux의 경우 간단히 호출 가능
pages = convert_from_path('Mutimedia-연습문제.pdf', dpi=300)

full_text = ""
for page_number, page in enumerate(pages, start=1):
    text = pytesseract.image_to_string(page, lang='eng+kor')  # 영어, 한국어 OCR 지원
    full_text += f"--- Page {page_number} ---\n{text}\n"

# OCR 결과 저장
with open("output.txt", "w", encoding="utf-8") as file:
    file.write(full_text)

print("OCR 완료, 결과는 output2.txt 파일에 저장되었습니다.")

