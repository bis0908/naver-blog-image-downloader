# 네이버 블로그 이미지 다운로더 & 변형 도구

네이버 블로그 포스트에서 이미지를 다운로드하고 고급 변형 처리를 수행하는 통합 도구입니다.

## 주요 기능

### 🔍 이미지 다운로드

- 네이버 블로그 포스트에서 이미지 자동 추출
- `se-section-image` 및 `se-section-imageGroup` 클래스 대상
- 절대/상대 URL 모두 처리 가능
- 순차적 파일명으로 충돌 방지
- 상세한 진행상황 피드백

### 🎨 고급 이미지 변형

- **3겹 레이어 합성**: 메인 이미지 + 랜덤 배경 2개
- **조화로운 색상 시스템**: 자연스러운 테두리 색상 팔레트
- **개별 회전각도**: 이미지 유형별 최적화된 회전 범위
- **9구역 배치 시스템**: 정교한 배경 이미지 배치
- **깊이 효과**: 배경 이미지 크기 변화로 자연스러운 깊이감
- **투명도 처리**: 회전 시 자연스러운 배경 노출
- **스트리밍 처리**: 메모리 효율적인 배치 처리

### 🖥️ 사용자 인터페이스

- GUI 인터페이스 지원
- 실시간 진행상황 표시
- 변형 옵션 개별 선택 가능

## 설치 방법

### 요구사항

- Python 3.8 이상
- UV 패키지 매니저 (권장)

### 의존성 설치

UV 사용 (권장):

```bash
uv install
```

PIP 사용:

```bash
pip install -r requirements.txt
```

## 사용 방법

### 1. 기본 실행

```bash
python main.py
```

### 2. GUI 실행

```bash
python main_ui.py
```

### 3. 단일 실행 파일 빌드

PyInstaller를 사용하여 단일 실행 파일 생성:

```bash
# GUI 버전 빌드
pyinstaller --onefile --windowed --name "네이버블로그이미지변형도구" main_ui.py

# CLI 버전 빌드  
pyinstaller --onefile --name "naver-blog-image-tool" main.py

# 추가 리소스 포함 (필요한 경우)
pyinstaller --onefile --windowed --add-data "ui/*;ui" --name "네이버블로그이미지변형도구" main_ui.py
```

빌드된 실행 파일은 `dist/` 폴더에 생성됩니다.

## 사용 예시

### CLI 모드

```
=== 네이버 블로그 이미지 다운로더 & 변형 도구 ===

블로그 URL 입력: https://blog.naver.com/example/post  
이미지 저장 경로: ./downloaded_images

URL 처리 중: https://blog.naver.com/example/post
저장 디렉토리: /path/to/downloaded_images

ℹ 블로그 페이지 가져오는 중...
ℹ HTML 내용 분석 중...
ℹ 'se-section-image' 클래스 섹션 2개 발견
ℹ 'se-section-imageGroup' 클래스 섹션 1개 발견  
ℹ 고유 이미지 5개 발견
다운로드할 이미지 5개 발견.

ℹ 다운로드 중 1/5: 001_example_image.jpg
ℹ 다운로드 중 2/5: 002_photo.png
...

✓ 모든 이미지 다운로드 완료!

=== 이미지 변형 처리 ===
변형 옵션 선택:
- 랜덤 크기 조정 (±5%)
- 랜덤 회전 (±3도)  
- 테두리 추가
- 랜덤 픽셀 효과

변형 작업 시작: 5개
변형 중: 1/5
변형 중: 2/5
...
원본 파일들을 정리 중...
원본 파일 5개 정리 완료
✓ 모든 변형 완료!
```

### GUI 모드

- 직관적인 버튼 인터페이스
- 실시간 진행률 표시
- 변형 옵션 체크박스로 선택
- 로그 창에서 상세 진행상황 확인

## 프로젝트 구조

```
naver-blog-image-downloader/
├── main.py                  # CLI 진입점
├── main_ui.py              # GUI 진입점  
├── core/                   # 핵심 설정 및 제어
│   ├── settings.py         # 설정 관리
│   └── ui_controller.py    # UI 제어 로직
├── scraper/               # 웹 스크래핑
│   └── scraper.py         # HTML 분석 및 이미지 추출
├── utils/                 # 유틸리티
│   ├── downloader.py      # 이미지 다운로드
│   ├── request_manager.py # HTTP 요청 관리
│   └── utils.py          # 공통 유틸리티
├── image_processor/       # 이미지 변형 처리
│   ├── transformer.py     # 이미지 변형 엔진
│   └── batch_processor.py # 배치 처리 관리
├── ui/                   # GUI 인터페이스
│   ├── untitled.ui       # Qt UI 파일
│   └── untitled_ui.py    # UI 코드
└── test/                 # 테스트 파일
    ├── test_image/       # 테스트 이미지
    ├── test_output/      # 테스트 결과
    └── test_transformer.py # 변형 테스트
```

## 변형 옵션 상세

### 기본 변형

- **랜덤 크기 조정**: ±5% 비율 변경
- **랜덤 회전**: 이미지 유형별 최적화된 각도
  - 일반 이미지: ±3도
  - 특정 유형별 개별 설정 가능
- **테두리 추가**: 조화로운 색상 팔레트 기반
- **랜덤 픽셀**: 3-5개 밝은 색상 픽셀 추가

### 고급 합성

- **3겹 레이어**: 메인 + 배경 2개 자동 합성
- **9구역 배치**: 정교한 배경 이미지 위치 제어
- **깊이 효과**: 배경 이미지 크기 조정으로 입체감 연출
- **투명도 처리**: 회전된 영역의 자연스러운 배경 노출

## 기술 스택

- **Python 3.8+**: 메인 언어
- **PIL/Pillow**: 이미지 처리
- **Requests**: HTTP 통신  
- **BeautifulSoup4**: HTML 파싱
- **PyQt5**: GUI 인터페이스
- **UV**: 패키지 관리 (권장)

## 성능 최적화

- 스트리밍 방식 배치 처리로 메모리 효율성
- 고품질 LANCZOS 리샘플링
- 비동기 처리 지원
- 취소 가능한 장시간 작업
- 자동 메모리 정리

## 라이센스

이 프로젝트는 개인 사용 목적으로 제작되었습니다.

## 문제 해결

### 일반적인 문제

1. **의존성 오류**: `uv install` 또는 `pip install -r requirements.txt` 재실행
2. **GUI 실행 오류**: PyQt5 설치 확인
3. **빌드 오류**: PyInstaller 최신 버전 사용
4. **메모리 부족**: 대용량 이미지 처리 시 배치 크기 조정

### 연락처

문제 발생 시 이슈를 등록해 주세요.
