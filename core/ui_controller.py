"""
UI 컨트롤러 모듈
UI 이벤트 처리와 비즈니스 로직을 담당합니다.
"""

import logging
import threading
from pathlib import Path
from typing import Dict, Any, Callable, Optional, List
from urllib.parse import urlparse

from scraper.scraper import NaverBlogScraper
from utils.downloader import ImageDownloader
from image_processor import StreamingImageProcessor
from .settings import AppSettings


class UIController:
    """UI 비즈니스 로직 관리 클래스"""

    def __init__(
        self,
        progress_callback: Callable[[int], None],
        log_callback: Callable[[str], None],
        enable_buttons_callback: Callable[[bool, bool, bool], None],
    ):
        """
        Args:
            progress_callback: 진행률 업데이트 콜백 (0-100)
            log_callback: 로그 메시지 콜백 (한글 20자 제한)
            enable_buttons_callback: 버튼 활성화 콜백 (download, cancel, close)
        """
        self.progress_callback = progress_callback
        self.log_callback = log_callback
        self.enable_buttons_callback = enable_buttons_callback

        # 핵심 컴포넌트
        self.settings = AppSettings()
        self.scraper = NaverBlogScraper()
        self.image_processor = None

        # 상태 관리
        self._is_processing = False
        self._is_cancelled = False
        self._current_thread = None
        self._downloaded_images = []

        self.logger = logging.getLogger(__name__)

    def initialize_ui(self) -> Dict[str, Any]:
        """
        UI 초기화를 위한 설정값을 반환합니다.

        Returns:
            UI 초기 설정 딕셔너리
        """
        try:
            settings = self.settings.load_settings()

            return {
                "last_save_path": settings.get(
                    "last_save_path", self.settings.get_current_directory()
                ),
                "transform_options": settings.get("transform_options", {}),
                "current_directory": self.settings.get_current_directory(),
            }
        except Exception as e:
            self.logger.error(f"UI 초기화 실패: {str(e)}")
            return {
                "last_save_path": self.settings.get_current_directory(),
                "transform_options": self.settings.default_settings[
                    "transform_options"
                ].copy(),
                "current_directory": self.settings.get_current_directory(),
            }

    def validate_inputs(self, url: str, save_path: str) -> tuple:
        """
        사용자 입력값의 유효성을 검사합니다.

        Args:
            url: 네이버 블로그 URL
            save_path: 저장 경로

        Returns:
            (유효성 여부, 오류 메시지)
        """
        try:
            # URL 유효성 검사
            if not url.strip():
                return False, "URL을 입력해주세요"

            # 네이버 블로그 URL 형식 확인
            parsed = urlparse(url.strip())
            if not parsed.netloc or "blog.naver.com" not in parsed.netloc:
                return False, "네이버 블로그 URL이 아닙니다"

            # 저장 경로 유효성 검사
            if not save_path.strip():
                return False, "저장 경로를 입력해주세요"

            save_dir = Path(save_path.strip())
            if not save_dir.exists():
                try:
                    save_dir.mkdir(parents=True, exist_ok=True)
                except Exception:
                    return False, "저장 경로를 생성할 수 없습니다"

            if not save_dir.is_dir():
                return False, "유효한 디렉토리가 아닙니다"

            return True, ""

        except Exception as e:
            self.logger.error(f"입력값 검증 실패: {str(e)}")
            return False, "입력값 검증 중 오류 발생"

    def start_download_process(
        self, url: str, save_path: str, transform_options: Dict[str, bool]
    ) -> None:
        """
        다운로드 및 변형 프로세스를 시작합니다.

        Args:
            url: 네이버 블로그 URL
            save_path: 저장 경로
            transform_options: 이미지 변형 옵션
        """
        if self._is_processing:
            self.log_callback("이미 진행 중입니다")
            return

        # 입력값 검증
        is_valid, error_msg = self.validate_inputs(url, save_path)
        if not is_valid:
            self.log_callback(error_msg)
            return

        # 상태 초기화
        self._is_processing = True
        self._is_cancelled = False
        self._downloaded_images.clear()

        # UI 상태 업데이트
        self.enable_buttons_callback(
            False, True, False
        )  # download=False, cancel=True, close=False
        self.progress_callback(0)

        # 설정 저장
        self.settings.update_last_save_path(save_path)
        self.settings.update_transform_options(transform_options)

        # 별도 스레드에서 처리 시작
        self._current_thread = threading.Thread(
            target=self._process_workflow,
            args=(url.strip(), save_path.strip(), transform_options),
            daemon=True,
        )
        self._current_thread.start()

    def _process_workflow(
        self, url: str, save_path: str, transform_options: Dict[str, bool]
    ) -> None:
        """다운로드 및 변형 워크플로우를 실행합니다."""
        try:
            base_save_dir = Path(save_path)

            # 1단계: 포스팅 제목 추출 및 폴더 생성
            self.log_callback("포스팅 정보 추출 중...")
            self.progress_callback(5)

            if self._check_cancelled():
                return

            post_title = self.scraper.extract_post_title(url)
            final_save_dir = base_save_dir / post_title
            final_save_dir.mkdir(parents=True, exist_ok=True)

            # 2단계: 이미지 URL 추출
            self.log_callback("이미지 목록 추출 중...")
            self.progress_callback(10)

            if self._check_cancelled():
                return

            image_urls = self.scraper.extract_image_urls(url)

            if not image_urls:
                self.log_callback("이미지를 찾을 수 없습니다")
                self._finish_process()
                return

            # 3단계: 이미지 다운로드 (0% ~ 50%)
            self.log_callback(f"다운로드 시작: {len(image_urls)}개")

            download_success = self._download_images(image_urls, final_save_dir)

            if self._check_cancelled():
                return

            if not download_success:
                self.log_callback("다운로드에 실패했습니다")
                self._finish_process()
                return

            # 4단계: 이미지 변형 (50% ~ 100%)
            if self._downloaded_images:
                self._transform_images(
                    self._downloaded_images, final_save_dir, transform_options
                )

            if not self._check_cancelled():
                self.log_callback("모든 작업 완료!")
                self.progress_callback(100)

        except Exception as e:
            self.logger.error(f"워크플로우 실행 중 오류: {str(e)}")
            self.log_callback("처리 중 오류 발생")
        finally:
            self._finish_process()

    def _download_images(self, image_urls: List[str], save_dir: Path) -> bool:
        """이미지 다운로드를 실행합니다."""
        try:
            # blogfiles.pstatic.net URL 사전 필터링
            filtered_urls = [
                url for url in image_urls if "blogfiles.pstatic.net" not in url
            ]

            if not filtered_urls:
                self.log_callback("다운로드 가능한 이미지가 없습니다")
                return False

            # 필터링 결과 로그
            if len(filtered_urls) < len(image_urls):
                excluded_count = len(image_urls) - len(filtered_urls)
                self.log_callback(f"{excluded_count}개 이미지 제외됨")

            with ImageDownloader(save_dir) as downloader:
                total_images = len(filtered_urls)  # 실제 처리할 이미지 개수
                successful_downloads = 0

                for i, url in enumerate(filtered_urls):
                    if self._check_cancelled():
                        return False

                    # 진행률 계산 (0% ~ 50%) - 실제 처리할 이미지 기준
                    progress = int((i / total_images) * 50)
                    self.progress_callback(progress)
                    self.log_callback(f"다운로드 중: {i + 1}/{total_images}")

                    # 개별 이미지 다운로드
                    downloaded_file = downloader.download_single_image(
                        url, f"image_{i + 1:03d}"
                    )
                    if downloaded_file:
                        self._downloaded_images.append(downloaded_file)
                        successful_downloads += 1

                self.progress_callback(50)
                return successful_downloads > 0

        except Exception as e:
            self.logger.error(f"이미지 다운로드 실패: {str(e)}")
            return False

    def _transform_images(
        self,
        image_paths: List[Path],
        base_dir: Path,
        transform_options: Dict[str, bool],
    ) -> None:
        """이미지 변형을 실행합니다."""
        try:
            # 이미지 프로세서 초기화
            self.image_processor = StreamingImageProcessor(
                progress_callback=self._update_progress,
                cancel_callback=self._check_cancelled,
                log_callback=self.log_callback,
            )

            # 변형된 이미지 저장 디렉토리
            transformed_dir = base_dir / "transformed"

            # 스트리밍 방식으로 이미지 변형 처리
            result = self.image_processor.process_images_streaming(
                image_paths=image_paths,
                output_dir=transformed_dir,
                transform_options=transform_options,
                base_progress=50,
            )

            if result["cancelled"]:
                return

            # 결과 보고
            if result["fail_count"] > 0:
                self.log_callback(f"변형 완료! 실패: {result['fail_count']}개")
            else:
                self.log_callback("모든 변형 완료!")

        except Exception as e:
            self.logger.error(f"이미지 변형 실패: {str(e)}")
            self.log_callback("변형 중 오류 발생")

    def _update_progress(self, value: int, message: str = "") -> None:
        """진행률 업데이트 (메시지는 별도로 처리)"""
        self.progress_callback(value)
        if message:
            self.log_callback(message)

    def _check_cancelled(self) -> bool:
        """취소 상태를 확인합니다."""
        return self._is_cancelled

    def cancel_process(self) -> None:
        """현재 진행 중인 작업을 취소합니다."""
        if not self._is_processing:
            return

        self._is_cancelled = True
        self.log_callback("취소 요청됨...")

        # 이미지 프로세서 취소
        if self.image_processor:
            self.image_processor.cancel_processing()

        # 다운로드된 파일들 정리
        self._cleanup_files()

    def _cleanup_files(self) -> None:
        """취소 시 생성된 파일들을 정리합니다."""
        try:
            for file_path in self._downloaded_images:
                if file_path.exists():
                    file_path.unlink()
                    self.logger.info(f"파일 정리됨: {file_path}")
        except Exception as e:
            self.logger.warning(f"파일 정리 중 오류: {str(e)}")

    def _finish_process(self) -> None:
        """작업 완료 후 상태를 정리합니다."""
        self._is_processing = False
        self._current_thread = None

        # UI 상태 복원
        self.enable_buttons_callback(
            True, False, True
        )  # download=True, cancel=False, close=True

    def is_processing(self) -> bool:
        """현재 작업 진행 중인지 확인합니다."""
        return self._is_processing

    def truncate_log_message(self, message: str, max_length: int = 20) -> str:
        """
        로그 메시지를 지정된 길이로 자릅니다.

        Args:
            message: 원본 메시지
            max_length: 최대 길이 (한글 기준)

        Returns:
            잘린 메시지
        """
        if len(message) <= max_length:
            return message

        return message[: max_length - 3] + "..."

    def get_save_directory_suggestion(self) -> str:
        """저장 디렉토리 제안을 반환합니다."""
        settings = self.settings.load_settings()
        last_path = settings.get("last_save_path", "")

        if last_path and Path(last_path).exists():
            return last_path

        return self.settings.get_current_directory()
