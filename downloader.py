"""
이미지 다운로드 기능입니다.
"""

import requests
import re
from pathlib import Path
from urllib.parse import urlparse, unquote
from utils.utils import print_error, print_info, print_warning
from request_manager import RequestManager


class ImageDownloader:
    """URL에서 이미지 다운로드를 처리합니다."""

    def __init__(self, save_directory: Path):
        self.save_directory = Path(save_directory)
        # 이미지 다운로드용 설정 (더 빠른 간격)
        self.request_manager = RequestManager(
            min_delay=0.5, max_delay=2.0, max_retries=3, session_reset_interval=20
        )

    def download_images(self, image_urls: list[str]) -> int:
        """
        제공된 URL에서 이미지를 다운로드합니다.

        Args:
            image_urls: 다운로드할 이미지 URL 목록

        Returns:
            성공적으로 다운로드된 이미지 수
        """
        successful_downloads = 0

        for i, url in enumerate(image_urls, 1):
            try:
                # URL 다운로드 가능 여부 체크
                # if not self._is_downloadable_url(url):
                #     print_warning(f"{len(image_urls)}개 중 {i}번째 건너뜀 (blogfiles.pstatic.net URL): {url}")
                #     continue

                # URL 해상도 최적화
                optimized_url = self._optimize_image_url(url)
                if optimized_url != url:
                    print_info(f"URL 해상도 최적화: ?type=w3840으로 변경")

                filename = self._generate_filename(optimized_url, i)
                file_path = self.save_directory / filename

                print_info(f"{len(image_urls)}개 중 {i}번째 다운로드 중: {filename}")

                if self._download_single_image(optimized_url, file_path):
                    successful_downloads += 1

            except Exception as e:
                print_error(f"이미지 {i} 다운로드 오류: {str(e)}")

        return successful_downloads

    # def _is_downloadable_url(self, url: str) -> bool:
    #     """
    #     URL이 다운로드 가능한지 확인합니다.

    #     Args:
    #         url: 확인할 이미지 URL

    #     Returns:
    #         다운로드 가능하면 True, 아니면 False
    #     """
    #     if url.startswith('https://blogfiles.pstatic.net'):
    #         return False
    #     elif url.startswith('https://postfiles.pstatic.net'):
    #         return True
    #     else:
    #         return True  # 다른 URL들은 기본적으로 허용

    def _optimize_image_url(self, url: str) -> str:
        """
        이미지 URL의 해상도를 최대화합니다.

        Args:
            url: 원본 이미지 URL

        Returns:
            해상도가 최적화된 URL
        """
        if "?type=w" in url:
            # ?type=w(숫자) 패턴을 ?type=w3840으로 변경
            return re.sub(r"\?type=w\d+", "?type=w3840", url)
        return url

    def _download_single_image(self, url: str, file_path: Path) -> bool:
        """
        URL에서 파일 경로로 단일 이미지를 다운로드합니다.

        Args:
            url: 다운로드할 이미지 URL
            file_path: 이미지를 저장할 경로

        Returns:
            다운로드 성공 시 True, 실패 시 False
        """
        try:
            response = self.request_manager.get(url, timeout=30, stream=True)

            with open(file_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)

            return True

        except requests.RequestException as e:
            print_error(f"{url} 다운로드 실패: {str(e)}")
            return False
        except IOError as e:
            print_error(f"파일 {file_path} 저장 실패: {str(e)}")
            return False

    def _generate_filename(self, url: str, index: int) -> str:
        """
        다운로드된 이미지의 파일명을 생성합니다.

        Args:
            url: 이미지 URL
            index: 이미지의 순차 인덱스

        Returns:
            생성된 파일명
        """
        try:
            parsed_url = urlparse(url)
            # URL 디코딩으로 한글 문자 복원
            decoded_path = unquote(parsed_url.path, encoding="utf-8")
            original_filename = Path(decoded_path).name

            if original_filename and "." in original_filename:
                name, ext = original_filename.rsplit(".", 1)
                # 파일명이 너무 길면 잘라내기 (한글 고려)
                safe_name = name[:30] if len(name) > 30 else name
                return f"{index:03d}_{safe_name}.{ext}"
            else:
                return f"{index:03d}_image.jpg"

        except Exception as e:
            print_warning(f"파일명 생성 오류: {str(e)}, 기본 파일명 사용")
            return f"{index:03d}_image.jpg"

    def close(self):
        """리소스를 정리합니다."""
        self.request_manager.close()

    def __enter__(self):
        """컨텍스트 매니저 진입"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """컨텍스트 매니저 종료"""
        self.close()
