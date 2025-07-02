"""
이미지 변형 처리 모듈
랜덤 변형과 3겹 레이어 이미지 생성 기능을 제공합니다.
"""

import random
from pathlib import Path
from typing import Dict, Any, Tuple
from PIL import Image, ImageDraw, ImageFilter
import logging


class ImageTransformer:
    """이미지 변형 처리 클래스"""

    # 변형 관련 상수들
    BORDER_WIDTH = 5  # 테두리 두께 (픽셀)
    SIZE_VARIATION_RANGE = (0.95, 1.05)  # 크기 변형 범위 (±5%)
    ROTATION_RANGE = (-3, 3)  # 회전 각도 범위 (±3도)
    RANDOM_PIXEL_COUNT_RANGE = (3, 5)  # 랜덤 픽셀 개수 범위
    RANDOM_PIXEL_COLOR_RANGE = (100, 255)  # 랜덤 픽셀 밝기 범위
    BORDER_COLOR_RANGE = (50, 200)  # 테두리 색상 범위

    # 배경 이미지 배치 관련 상수들
    BACKGROUND_MARGIN_NEAR = 1 / 6  # 중앙에서 가까운 위치 (16.7%)
    BACKGROUND_MARGIN_CENTER = 1 / 2  # 중앙 위치 (50%)
    BACKGROUND_MARGIN_FAR = 5 / 6  # 중앙에서 조금 먼 위치 (83.3%)
    CANVAS_MARGIN = 0.2  # 전체 캔버스 여백 (20%)

    # 이미지 크기 관련 상수들
    MAX_WIDTH = 1500  # 최대 폭 (픽셀)

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def _resize_to_max_width(self, image: Image.Image) -> Image.Image:
        """
        이미지 폭을 최대 크기 이하로 비율을 유지하면서 축소합니다.

        Args:
            image: 원본 PIL Image 객체

        Returns:
            축소된 PIL Image 객체 (필요한 경우)
        """
        try:
            current_width = image.width

            # 폭이 최대 크기 이하인 경우 그대로 반환
            if current_width <= self.MAX_WIDTH:
                self.logger.debug(f"이미지 크기 유지: {current_width}x{image.height}")
                return image

            # 비율 계산 및 새로운 크기 결정
            scale_ratio = self.MAX_WIDTH / current_width
            new_width = self.MAX_WIDTH
            new_height = int(image.height * scale_ratio)

            # 고품질 리샘플링으로 축소
            resized_image = image.resize(
                (new_width, new_height), Image.Resampling.LANCZOS
            )

            self.logger.info(
                f"이미지 축소: {current_width}x{image.height} → {new_width}x{new_height} "
                f"(비율: {scale_ratio:.3f})"
            )

            return resized_image

        except Exception as e:
            self.logger.error(f"이미지 크기 조정 중 오류: {str(e)}")
            return image  # 오류 시 원본 반환

    def apply_random_transforms(
        self, image: Image.Image, options: Dict[str, bool]
    ) -> Image.Image:
        """
        이미지에 랜덤 변형을 적용합니다.
        순서: 크기 조정 → 테두리 추가 → 회전 → 랜덤 픽셀 추가

        Args:
            image: 원본 PIL Image 객체
            options: 변형 옵션 딕셔너리
                - random_size: 랜덤 비율 조정 (±5%)
                - random_angle: 랜덤 기울기 (±3도)
                - random_pixel: 랜덤 픽셀 추가 (3~5개)
                - add_outline: 테두리 추가

        Returns:
            변형된 PIL Image 객체
        """
        try:
            transformed_image = image.copy()

            # 1. 랜덤 비율 조정 (±5%)
            if options.get("random_size", False):
                scale_factor = random.uniform(*self.SIZE_VARIATION_RANGE)
                new_width = int(transformed_image.width * scale_factor)
                new_height = int(transformed_image.height * scale_factor)
                transformed_image = transformed_image.resize(
                    (new_width, new_height), Image.Resampling.LANCZOS
                )

            # 2. 테두리 추가 (회전 전에 추가하여 테두리도 함께 회전되도록)
            if options.get("add_outline", False):
                transformed_image = self._add_border(transformed_image)

            # 3. 랜덤 기울기 (±3도) - 테두리와 함께 회전
            if options.get("random_angle", False):
                angle = random.uniform(*self.ROTATION_RANGE)
                transformed_image = transformed_image.rotate(
                    angle, expand=True, fillcolor="white"
                )

            # 4. 랜덤 픽셀 추가 (마지막에 추가하여 회전으로 인한 손실 방지)
            if options.get("random_pixel", False):
                transformed_image = self._add_random_pixels(transformed_image)

            return transformed_image

        except Exception as e:
            self.logger.error(f"이미지 변형 중 오류 발생: {str(e)}")
            return image  # 오류 시 원본 반환

    def _add_random_pixels(self, image: Image.Image) -> Image.Image:
        """이미지에 랜덤 픽셀을 추가합니다."""
        try:
            # RGB 모드로 변환 (필요한 경우)
            if image.mode != "RGB":
                image = image.convert("RGB")

            draw = ImageDraw.Draw(image)
            pixel_count = random.randint(*self.RANDOM_PIXEL_COUNT_RANGE)

            for _ in range(pixel_count):
                x = random.randint(0, image.width - 1)
                y = random.randint(0, image.height - 1)
                # 랜덤 색상 (밝은 색상 우선)
                color = (
                    random.randint(*self.RANDOM_PIXEL_COLOR_RANGE),
                    random.randint(*self.RANDOM_PIXEL_COLOR_RANGE),
                    random.randint(*self.RANDOM_PIXEL_COLOR_RANGE),
                )
                draw.point((x, y), fill=color)

            return image

        except Exception as e:
            self.logger.error(f"랜덤 픽셀 추가 중 오류: {str(e)}")
            return image

    def _add_border(self, image: Image.Image) -> Image.Image:
        """이미지에 고정 두께의 랜덤 색상 테두리를 추가합니다."""
        try:
            # 고정 테두리 두께 사용
            border_width = self.BORDER_WIDTH

            # 랜덤 테두리 색상
            border_color = (
                random.randint(*self.BORDER_COLOR_RANGE),
                random.randint(*self.BORDER_COLOR_RANGE),
                random.randint(*self.BORDER_COLOR_RANGE),
            )

            # 새로운 크기로 이미지 생성
            new_width = image.width + (border_width * 2)
            new_height = image.height + (border_width * 2)

            # 테두리 색상으로 채운 새 이미지 생성
            bordered_image = Image.new("RGB", (new_width, new_height), border_color)

            # 원본 이미지를 중앙에 붙이기
            bordered_image.paste(image, (border_width, border_width))

            self.logger.debug(f"테두리 추가: {border_width}px, 색상: {border_color}")
            return bordered_image

        except Exception as e:
            self.logger.error(f"테두리 추가 중 오류: {str(e)}")
            return image

    def create_layered_image(
        self,
        original_image: Image.Image,
        transform_options: Dict[str, bool],
        available_images: list = None,
    ) -> Image.Image:
        """
        메인 이미지와 같은 폴더의 랜덤 이미지 2개를 겹쳐서 최종 이미지를 생성합니다.

        Args:
            original_image: 메인 PIL Image 객체
            transform_options: 변형 옵션
            available_images: 같은 폴더의 다른 이미지 경로 리스트

        Returns:
            3겹으로 레이어된 최종 PIL Image 객체 (100% 불투명도)
        """
        try:
            # 메인 이미지 전처리: RGB 변환 및 크기 축소
            if original_image.mode != "RGB":
                original_image = original_image.convert("RGB")
                self.logger.debug("메인 이미지를 RGB 모드로 변환")

            # 메인 이미지 크기 축소 (1500px 미만으로)
            original_image = self._resize_to_max_width(original_image)

            # 메인 이미지에 변형 적용 (배경 이미지와 동일한 처리)
            main_transformed = self.apply_random_transforms(
                original_image, transform_options
            )
            self.logger.debug("메인 이미지 변형 완료")

            # 배경 이미지들 준비
            background_images = []

            if available_images and len(available_images) >= 2:
                # 같은 폴더에서 랜덤하게 2개 이미지 선택
                random_images = random.sample(
                    available_images, min(2, len(available_images))
                )

                self.logger.debug(
                    f"선택된 배경 이미지: {[Path(img).name for img in random_images]}"
                )

                for img_path in random_images:
                    try:
                        bg_img = Image.open(img_path)

                        # 배경 이미지 전처리: RGB 변환 및 크기 축소
                        if bg_img.mode != "RGB":
                            bg_img = bg_img.convert("RGB")

                        # 배경 이미지도 크기 축소 적용
                        bg_img = self._resize_to_max_width(bg_img)

                        # 배경 이미지에도 변형 적용
                        bg_transformed = self.apply_random_transforms(
                            bg_img, transform_options
                        )
                        background_images.append(bg_transformed)
                        bg_img.close()  # 메모리 절약
                        self.logger.debug(
                            f"배경 이미지 처리 완료: {Path(img_path).name}"
                        )
                    except Exception as e:
                        self.logger.warning(
                            f"배경 이미지 로드 실패: {img_path}, 오류: {str(e)}"
                        )
                        continue
            else:
                self.logger.warning(
                    f"사용 가능한 배경 이미지 부족: {len(available_images) if available_images else 0}개"
                )

            # 배경 이미지가 부족한 경우 메인 이미지의 변형된 버전으로 채우기
            initial_bg_count = len(background_images)
            while len(background_images) < 2:
                # 메인 이미지 복사본 생성 (이미 전처리된 상태)
                main_copy = original_image.copy()

                bg_variant = self.apply_random_transforms(main_copy, transform_options)
                background_images.append(bg_variant)
                self.logger.debug(
                    f"메인 이미지 변형본을 배경으로 추가: {len(background_images)}/2"
                )

            if initial_bg_count < 2:
                self.logger.info(
                    f"배경 이미지 부족으로 메인 이미지 변형본 {2 - initial_bg_count}개 사용"
                )

            # 모든 이미지들의 최대 크기 계산
            all_images = background_images + [main_transformed]
            max_width = max(img.width for img in all_images)
            max_height = max(img.height for img in all_images)

            # 캔버스 여백 추가
            final_width = int(max_width * (1 + self.CANVAS_MARGIN))
            final_height = int(max_height * (1 + self.CANVAS_MARGIN))

            # 흰색 배경으로 최종 이미지 생성
            final_image = Image.new("RGB", (final_width, final_height), "white")
            self.logger.debug(f"최종 캔버스 크기: {final_width}x{final_height}")

            # 배경 이미지들을 중앙 근처에 배치 (후방)
            for i, bg_img in enumerate(background_images):
                max_x = final_width - bg_img.width
                max_y = final_height - bg_img.height

                if max_x > 0 and max_y > 0:
                    # 배경 이미지들을 중앙 근처에 분산 배치
                    if i == 0:
                        # 첫 번째 배경: 좌상단 중앙 근처 (1/6 ~ 1/2 영역)
                        x = random.randint(
                            int(max_x * self.BACKGROUND_MARGIN_NEAR),
                            int(max_x * self.BACKGROUND_MARGIN_CENTER),
                        )
                        y = random.randint(
                            int(max_y * self.BACKGROUND_MARGIN_NEAR),
                            int(max_y * self.BACKGROUND_MARGIN_CENTER),
                        )
                        position_desc = "좌상단 중앙 근처"
                    else:
                        # 두 번째 배경: 우하단 중앙 근처 (1/2 ~ 5/6 영역)
                        x = random.randint(
                            int(max_x * self.BACKGROUND_MARGIN_CENTER),
                            int(max_x * self.BACKGROUND_MARGIN_FAR),
                        )
                        y = random.randint(
                            int(max_y * self.BACKGROUND_MARGIN_CENTER),
                            int(max_y * self.BACKGROUND_MARGIN_FAR),
                        )
                        position_desc = "우하단 중앙 근처"

                    # 100% 불투명도로 배치
                    final_image.paste(bg_img, (x, y))
                    self.logger.debug(
                        f"배경 이미지 {i + 1} {position_desc} 배치: ({x}, {y})"
                    )

            # 메인 이미지를 정확히 중앙에 배치 (최상단)
            main_x = (final_width - main_transformed.width) // 2
            main_y = (final_height - main_transformed.height) // 2

            # 메인 이미지도 100% 불투명도로 배치
            final_image.paste(main_transformed, (main_x, main_y))
            self.logger.debug(f"메인 이미지 중앙 배치: ({main_x}, {main_y})")
            self.logger.info(f"레이어드 이미지 생성 완료: {final_width}x{final_height}")

            # 최종 이미지가 MAX_WIDTH를 초과하는 경우 다시 축소
            if final_image.width > self.MAX_WIDTH:
                self.logger.info(
                    f"최종 이미지 폭이 {self.MAX_WIDTH}px 초과: {final_image.width}px"
                )
                final_image = self._resize_to_max_width(final_image)
                self.logger.info(
                    f"최종 이미지 크기 조정 완료: {final_image.width}x{final_image.height}"
                )

            return final_image

        except Exception as e:
            self.logger.error(f"레이어 이미지 생성 중 오류: {str(e)}")
            # 오류 시 단순 변형 이미지 반환
            return self.apply_random_transforms(original_image, transform_options)

    def save_transformed_image(
        self, image: Image.Image, output_path: Path, quality: int = 95
    ) -> bool:
        """
        변형된 이미지를 저장합니다.

        Args:
            image: 저장할 PIL Image 객체
            output_path: 저장 경로
            quality: JPEG 품질 (1-100)

        Returns:
            저장 성공 여부
        """
        try:
            # 디렉토리가 존재하지 않으면 생성
            output_path.parent.mkdir(parents=True, exist_ok=True)

            # 파일 확장자에 따라 저장 형식 결정
            if output_path.suffix.lower() in [".jpg", ".jpeg"]:
                image.save(output_path, "JPEG", quality=quality, optimize=True)
            elif output_path.suffix.lower() == ".png":
                image.save(output_path, "PNG", optimize=True)
            else:
                # 기본적으로 JPEG로 저장
                image.save(
                    output_path.with_suffix(".jpg"),
                    "JPEG",
                    quality=quality,
                    optimize=True,
                )

            return True

        except Exception as e:
            self.logger.error(f"이미지 저장 중 오류: {str(e)}")
            return False
