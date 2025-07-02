"""
이미지 배치 처리 모듈
스트리밍 방식으로 이미지 변형을 처리하고 진행상황을 실시간으로 보고합니다.
"""

import threading
import time
from pathlib import Path
from typing import List, Dict, Callable, Any, Optional
from PIL import Image
import logging

from .transformer import ImageTransformer


class StreamingImageProcessor:
    """스트리밍 방식 이미지 배치 처리 클래스"""

    def __init__(
        self,
        progress_callback: Callable[[int, str], None],
        cancel_callback: Callable[[], bool],
        log_callback: Callable[[str], None],
    ):
        """
        Args:
            progress_callback: 진행률 업데이트 콜백 (progress_value, message)
            cancel_callback: 취소 상태 확인 콜백 (returns bool)
            log_callback: 로그 메시지 콜백
        """
        self.progress_callback = progress_callback
        self.cancel_callback = cancel_callback
        self.log_callback = log_callback

        self.transformer = ImageTransformer()
        self.logger = logging.getLogger(__name__)

        # 처리 상태
        self._is_cancelled = False
        self._current_thread = None

    def process_images_streaming(
        self,
        image_paths: List[Path],
        output_dir: Path,
        transform_options: Dict[str, bool],
        base_progress: int = 50,
    ) -> Dict[str, Any]:
        """
        이미지들을 스트리밍 방식으로 변형 처리합니다.

        Args:
            image_paths: 처리할 이미지 파일 경로 리스트
            output_dir: 변형된 이미지 저장 디렉토리
            transform_options: 이미지 변형 옵션
            base_progress: 시작 진행률 (0-100)

        Returns:
            처리 결과 딕셔너리
            {
                'success_count': int,
                'fail_count': int,
                'failed_files': List[str],
                'cancelled': bool
            }
        """
        self._is_cancelled = False

        # 결과 초기화
        result = {
            "success_count": 0,
            "fail_count": 0,
            "failed_files": [],
            "cancelled": False,
        }

        if not image_paths:
            self.log_callback("처리할 이미지가 없습니다")
            return result

        total_images = len(image_paths)
        self.log_callback(f"변형 작업 시작: {total_images}개")

        # 출력 디렉토리 생성
        output_dir.mkdir(parents=True, exist_ok=True)

        try:
            for i, image_path in enumerate(image_paths):
                # 취소 확인
                if self.cancel_callback() or self._is_cancelled:
                    result["cancelled"] = True
                    self.log_callback("작업이 취소되었습니다")
                    break

                # 진행률 계산 (base_progress부터 100%까지)
                progress = base_progress + int(
                    (i / total_images) * (100 - base_progress)
                )

                try:
                    # 이미지 로드
                    self.log_callback(f"변형 중: {i + 1}/{total_images}")
                    self.progress_callback(progress, f"변형 중: {i + 1}/{total_images}")

                    original_image = Image.open(image_path)

                    # 같은 폴더의 다른 이미지들 준비 (현재 처리 중인 이미지 확실히 제외)
                    current_image_absolute = image_path.resolve()
                    available_images = []

                    for img_path in image_paths:
                        img_absolute = img_path.resolve()
                        # 절대경로로 비교하여 현재 이미지 제외
                        if img_absolute != current_image_absolute and img_path.exists():
                            available_images.append(str(img_path))

                    # 디버깅: 사용 가능한 배경 이미지 개수 로그
                    self.logger.debug(f"현재 이미지: {current_image_absolute.name}")
                    self.logger.debug(
                        f"사용 가능한 배경 이미지: {len(available_images)}개"
                    )

                    # 배경 이미지가 부족한 경우 경고
                    if len(available_images) < 2:
                        self.logger.warning(
                            f"배경 이미지 부족: {len(available_images)}개 (현재 이미지 제외)"
                        )

                    # 이미지 변형 (메인 이미지 + 랜덤 배경 2개)
                    transformed_image = self.transformer.create_layered_image(
                        original_image, transform_options, available_images
                    )

                    # 파일명 생성 (원본명_transformed)
                    output_filename = (
                        f"{image_path.stem}_transformed{image_path.suffix}"
                    )
                    output_path = output_dir / output_filename

                    # 변형된 이미지 저장
                    if self.transformer.save_transformed_image(
                        transformed_image, output_path
                    ):
                        result["success_count"] += 1

                        # 메모리 절약을 위해 이미지 객체 삭제
                        del original_image
                        del transformed_image

                        # 원본 파일 삭제 (스트리밍 처리)
                        try:
                            image_path.unlink()
                            self.logger.info(f"원본 파일 삭제됨: {image_path}")
                        except Exception as e:
                            self.logger.warning(
                                f"원본 파일 삭제 실패: {image_path}, 오류: {str(e)}"
                            )
                    else:
                        result["fail_count"] += 1
                        result["failed_files"].append(str(image_path))

                except Exception as e:
                    self.logger.error(f"이미지 처리 실패: {image_path}, 오류: {str(e)}")
                    result["fail_count"] += 1
                    result["failed_files"].append(str(image_path))

                # CPU 사용률 조절을 위한 짧은 대기
                time.sleep(0.01)

            # 완료 처리
            if not result["cancelled"]:
                self.progress_callback(100, "변형 완료!")

                if result["fail_count"] > 0:
                    self.log_callback(f"완료! 실패: {result['fail_count']}개")
                else:
                    self.log_callback("모든 변형 완료!")

        except Exception as e:
            self.logger.error(f"배치 처리 중 예상치 못한 오류: {str(e)}")
            self.log_callback("처리 중 오류 발생")
            result["fail_count"] = total_images - result["success_count"]

        return result

    def process_images_async(
        self,
        image_paths: List[Path],
        output_dir: Path,
        transform_options: Dict[str, bool],
        completion_callback: Optional[Callable[[Dict[str, Any]], None]] = None,
        base_progress: int = 50,
    ) -> threading.Thread:
        """
        이미지 처리를 별도 스레드에서 비동기로 실행합니다.

        Args:
            image_paths: 처리할 이미지 파일 경로 리스트
            output_dir: 변형된 이미지 저장 디렉토리
            transform_options: 이미지 변형 옵션
            completion_callback: 완료 시 호출할 콜백 함수
            base_progress: 시작 진행률

        Returns:
            실행 중인 스레드 객체
        """

        def worker():
            try:
                result = self.process_images_streaming(
                    image_paths, output_dir, transform_options, base_progress
                )
                if completion_callback:
                    completion_callback(result)
            except Exception as e:
                self.logger.error(f"비동기 처리 중 오류: {str(e)}")
                if completion_callback:
                    completion_callback(
                        {
                            "success_count": 0,
                            "fail_count": len(image_paths),
                            "failed_files": [str(p) for p in image_paths],
                            "cancelled": False,
                        }
                    )

        self._current_thread = threading.Thread(target=worker, daemon=True)
        self._current_thread.start()
        return self._current_thread

    def cancel_processing(self) -> None:
        """현재 진행 중인 처리를 취소합니다."""
        self._is_cancelled = True
        self.log_callback("취소 요청됨...")

    def is_processing(self) -> bool:
        """현재 처리 중인지 확인합니다."""
        return self._current_thread is not None and self._current_thread.is_alive()

    def wait_for_completion(self, timeout: Optional[float] = None) -> bool:
        """
        처리 완료까지 대기합니다.

        Args:
            timeout: 대기 시간 제한 (초, None이면 무제한)

        Returns:
            정상 완료 여부 (timeout 발생시 False)
        """
        if self._current_thread and self._current_thread.is_alive():
            self._current_thread.join(timeout)
            return not self._current_thread.is_alive()
        return True

    def cleanup_failed_files(self, failed_files: List[str]) -> None:
        """실패한 파일들을 정리합니다."""
        for file_path in failed_files:
            try:
                path = Path(file_path)
                if path.exists():
                    path.unlink()
                    self.logger.info(f"실패한 파일 정리됨: {file_path}")
            except Exception as e:
                self.logger.warning(f"파일 정리 실패: {file_path}, 오류: {str(e)}")
