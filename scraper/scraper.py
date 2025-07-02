"""
네이버 블로그 이미지를 위한 HTML 스크래핑 기능입니다.
"""

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import re
from utils.utils import print_error, print_info, print_success, print_warning
from request_manager import NaverRequestManager

TARGET_CLASSES = [
    "se-section-image",
    "se-section-imageGroup",
    "se-imageStrip-container",
]
IMAGE_EXTENSIONS = (".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp")
TITLE_CLASS = "se-title-text"


class NaverBlogScraper:
    """네이버 블로그 페이지 스크래핑을 처리합니다."""

    def __init__(self):
        self.request_manager = NaverRequestManager()

    def extract_post_title(self, url: str) -> str:
        """
        네이버 블로그 포스팅에서 제목을 추출하고 폴더명으로 사용 가능하도록 정리합니다.

        Args:
            url: 스크래핑할 블로그 URL

        Returns:
            폴더명으로 사용 가능한 정리된 제목 (실패시 기본 제목 반환)
        """
        try:
            # 네이버 블로그 URL 파싱
            blog_id, log_no = self._parse_naver_blog_url(url)
            if not blog_id or not log_no:
                print_error("유효하지 않은 네이버 블로그 URL 형식입니다")
                return "네이버블로그_포스팅"

            # PostView.naver 엔드포인트로 요청 구성
            postview_url = self._build_postview_url(blog_id, log_no)
            print_info("블로그 페이지에서 제목을 추출하는 중...")

            response = self.request_manager.get(postview_url, timeout=30)
            soup = BeautifulSoup(response.content, "html.parser")

            # se-title-text 클래스에서 제목 추출
            title_element = soup.find(class_=TITLE_CLASS)
            if not title_element:
                print_warning("제목을 찾을 수 없습니다. 기본 제목을 사용합니다.")
                return "네이버블로그_포스팅"

            # 제목 텍스트 추출
            raw_title = title_element.get_text(strip=True)
            if not raw_title:
                print_warning("제목이 비어있습니다. 기본 제목을 사용합니다.")
                return "네이버블로그_포스팅"

            # 제목 정리
            cleaned_title = self._clean_title_for_folder(raw_title)
            print_success(f"추출된 제목: '{raw_title}' → 폴더명: '{cleaned_title}'")

            return cleaned_title

        except Exception as e:
            print_error(f"제목 추출 오류: {str(e)}")
            return "네이버블로그_포스팅"

    def _clean_title_for_folder(self, title: str) -> str:
        """
        제목을 폴더명으로 사용 가능하도록 정리합니다.

        Args:
            title: 원본 제목

        Returns:
            폴더명으로 사용 가능한 정리된 제목
        """
        # 1. HTML 주석 제거 (<!-- -->)
        title = re.sub(r"<!--.*?-->", "", title, flags=re.DOTALL)

        # 2. 윈도우에서 사용할 수 없는 문자 제거
        # 금지 문자: < > : " / \ | ? *
        title = re.sub(r'[<>:"/\\|?*]', "", title)

        # 3. 공백을 '_'로 치환 (연속된 공백도 하나의 '_'로)
        title = re.sub(r"\s+", "_", title)

        # 4. 앞뒤 '_' 제거
        title = title.strip("_")

        # 5. 빈 문자열 방지
        if not title:
            title = "네이버블로그_포스팅"

        # 6. 길이 제한 (255자는 윈도우 경로 제한)
        if len(title) > 100:  # 여유롭게 100자로 제한
            title = title[:100].rstrip("_")

        return title

    def extract_image_urls(self, url: str) -> list[str]:
        """
        네이버 블로그 페이지에서 이미지 URL을 추출합니다.

        Args:
            url: 스크래핑할 블로그 URL

        Returns:
            지정된 클래스에서 찾은 이미지 URL 목록
        """
        try:
            # 네이버 블로그 URL 파싱
            blog_id, log_no = self._parse_naver_blog_url(url)
            if not blog_id or not log_no:
                print_error("유효하지 않은 네이버 블로그 URL 형식입니다")
                return []

            print_info(f"URL 파싱 완료 - 블로그ID: {blog_id}, 로그번호: {log_no}")

            # PostView.naver 엔드포인트로 요청 구성
            postview_url = self._build_postview_url(blog_id, log_no)
            print_info(f"PostView URL: {postview_url}")

            print_info("블로그 페이지를 가져오는 중...")
            response = self.request_manager.get(postview_url, timeout=30)

            # DOM 가져오기 확인
            print_info(f"응답 상태: {response.status_code}")
            print_info(f"응답 헤더: {dict(response.headers)}")
            print_info(f"콘텐츠 길이: {len(response.content)} 바이트")
            print_info(
                f"콘텐츠 타입: {response.headers.get('content-type', '알 수 없음')}"
            )

            print_info("HTML 콘텐츠 파싱 중...")
            soup = BeautifulSoup(response.content, "html.parser")

            # HTML 파싱 확인
            print_info(
                f"파싱된 HTML 제목: {soup.title.string if soup.title else '제목 없음'}"
            )
            print_info(f"전체 HTML 요소 수: {len(soup.find_all())}")

            # 찾을 대상 클래스들
            target_classes = TARGET_CLASSES
            image_urls = []

            print_info("=== 클래스별 검색 시작 ===")

            for class_name in target_classes:
                print_info(f"\n--- 클래스 '{class_name}' 검색 중 ---")

                # 대상 클래스를 가진 모든 요소 찾기
                sections = soup.find_all(class_=class_name)
                print_info(f"클래스 '{class_name}'를 가진 {len(sections)}개 섹션 발견")

                # 찾은 섹션들의 상세 정보 출력
                for i, section in enumerate(sections):
                    print_info(f"  섹션 {i + 1}: {section.name} 태그")
                    print_info(f"    클래스: {section.get('class', [])}")
                    print_info(f"    ID: {section.get('id', 'ID 없음')}")

                    # 각 섹션 내의 모든 img 태그 찾기
                    img_tags = section.find_all("img")
                    print_info(f"    이 섹션에서 {len(img_tags)}개의 img 태그 발견")

                    for j, img in enumerate(img_tags):
                        print_info(f"      이미지 {j + 1}:")
                        print_info(
                            f"        data-lazy-src: {img.get('data-lazy-src', 'data-lazy-src 없음')}"
                        )
                        print_info(f"        class: {img.get('class', [])}")

                        # 우선순위: data-lazy-src > data-src > src
                        src = (
                            img.get("data-lazy-src")
                            or img.get("data-src")
                            or img.get("src")
                        )
                        if src:
                            print_info(f"        선택된 소스: {src}")
                            # 상대 URL을 절대 URL로 변환
                            absolute_url = urljoin(url, src)
                            print_info(f"        절대 URL: {absolute_url}")

                            if self._is_valid_image_url(absolute_url):
                                image_urls.append(absolute_url)
                                print_success("✓ 목록에 추가됨 (유효한 이미지 URL)")
                            else:
                                print_warning("건너뜀 (유효하지 않은 이미지 URL)")
                        else:
                            print_warning("건너뜀 (src, data-src, data-lazy-src 없음)")

            print_info("=== 클래스별 검색 완료 ===")

            # 순서를 유지하면서 중복 제거
            original_count = len(image_urls)
            image_urls = list(dict.fromkeys(image_urls))
            print_info(
                f"원본 URL 수: {original_count}, 중복 제거 후: {len(image_urls)}"
            )

            print_info("=== 최종 이미지 URL 목록 ===")
            for i, img_url in enumerate(image_urls):
                print_info(f"{i + 1}. {img_url}")

            print_info(f"{len(image_urls)}개의 고유한 이미지 발견")

            return image_urls

        except requests.RequestException as e:
            print_error(f"블로그 페이지 가져오기 실패: {str(e)}")
            return []
        except Exception as e:
            print_error(f"블로그 콘텐츠 파싱 오류: {str(e)}")
            import traceback

            print_error(f"전체 트레이스백: {traceback.format_exc()}")
            return []

    def _parse_naver_blog_url(self, url: str) -> tuple[str, str]:
        """
        네이버 블로그 URL을 파싱하여 blogId와 logNo를 추출합니다.

        Args:
            url: 네이버 블로그 URL (예: https://blog.naver.com/blogId/logNo)

        Returns:
            (blogId, logNo) 튜플
        """
        try:
            parsed = urlparse(url)

            # URL 형식 확인
            if "blog.naver.com" not in parsed.netloc:
                print_error("유효한 네이버 블로그 URL이 아닙니다")
                return "", ""

            # 경로에서 blogId와 logNo 추출
            path_parts = parsed.path.strip("/").split("/")

            if len(path_parts) >= 2:
                blog_id = path_parts[0]
                log_no = path_parts[1]
                print_info(f"경로에서 추출: blogId={blog_id}, logNo={log_no}")
                return blog_id, log_no

            # 쿼리 파라미터에서 추출 시도
            from urllib.parse import parse_qs

            query_params = parse_qs(parsed.query)

            blog_id = query_params.get("blogId", [""])[0]
            log_no = query_params.get("logNo", [""])[0]

            if blog_id and log_no:
                print_info(f"쿼리에서 추출: blogId={blog_id}, logNo={log_no}")
                return blog_id, log_no

            print_error("URL에서 blogId와 logNo를 추출할 수 없습니다")
            return "", ""

        except Exception as e:
            print_error(f"URL 파싱 오류: {str(e)}")
            return "", ""

    def _build_postview_url(self, blog_id: str, log_no: str) -> str:
        """
        필수 파라미터와 함께 PostView.naver URL을 구성합니다.

        Args:
            blog_id: 블로그 ID
            log_no: 로그 번호

        Returns:
            완전한 PostView URL
        """
        base_url = "https://blog.naver.com/PostView.naver"
        params = {
            "blogId": blog_id,
            "logNo": log_no,
            "redirect": "Dlog",
            "widgetTypeCall": "true",
            "noTrackingCode": "true",
            "directAccess": "false",
        }

        from urllib.parse import urlencode

        query_string = urlencode(params)
        return f"{base_url}?{query_string}"

    def _is_valid_image_url(self, url: str) -> bool:
        """
        URL이 유효한 이미지 URL인지 확인합니다.

        Args:
            url: 확인할 URL

        Returns:
            URL이 이미지로 보이면 True, 아니면 False
        """
        try:
            parsed = urlparse(url)
            if not parsed.scheme or not parsed.netloc:
                return False

            # 일반적인 이미지 확장자 확인
            path = parsed.path.lower()

            return any(path.endswith(ext) for ext in IMAGE_EXTENSIONS)

        except Exception:
            return False
