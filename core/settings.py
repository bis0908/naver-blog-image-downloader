"""
애플리케이션 설정 관리 모듈
사용자 설정을 JSON 파일로 저장하고 로드합니다.
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional


class AppSettings:
    """애플리케이션 설정 관리 클래스"""

    def __init__(self, config_filename: str = "app_settings.json"):
        """
        Args:
            config_filename: 설정 파일명 (실행 파일과 같은 디렉토리에 저장)
        """
        # 실행 파일 위치 기준으로 설정 파일 경로 결정
        if hasattr(Path, "cwd"):
            # 개발 환경
            self.config_path = Path.cwd() / config_filename
        else:
            # PyInstaller로 빌드된 환경
            import sys

            if getattr(sys, "frozen", False):
                # 실행 파일이 있는 디렉토리
                exe_dir = Path(sys.executable).parent
                self.config_path = exe_dir / config_filename
            else:
                # 스크립트 실행 환경
                self.config_path = Path(__file__).parent.parent / config_filename

        self.logger = logging.getLogger(__name__)

        # 기본 설정값
        self.default_settings = {
            "last_save_path": str(Path.home()),
            "last_url": "",
            "transform_options": {
                "random_size": True,
                "random_angle": True,
                "random_pixel": True,
                "add_outline": True,
            },
            "window_geometry": {"width": 538, "height": 292},
            "ui_settings": {
                "progress_update_interval": 100,  # ms
                "log_max_length": 20,  # 한글 기준 글자 수
                "auto_save_settings": True,
            },
        }

    def load_settings(self) -> Dict[str, Any]:
        """
        설정 파일에서 설정을 로드합니다.
        파일이 없거나 오류가 있으면 기본값을 반환합니다.

        Returns:
            설정 딕셔너리
        """
        try:
            if self.config_path.exists():
                with open(self.config_path, "r", encoding="utf-8") as f:
                    loaded_settings = json.load(f)

                # 기본값과 병합 (새로운 설정이 추가된 경우 대비)
                settings = self._merge_settings(
                    self.default_settings.copy(), loaded_settings
                )

                self.logger.info(f"설정 로드 성공: {self.config_path}")
                return settings
            else:
                self.logger.info("설정 파일이 없어 기본값을 사용합니다")
                return self.default_settings.copy()

        except Exception as e:
            self.logger.error(f"설정 로드 실패: {str(e)}")
            return self.default_settings.copy()

    def save_settings(self, settings: Dict[str, Any]) -> bool:
        """
        설정을 파일에 저장합니다.

        Args:
            settings: 저장할 설정 딕셔너리

        Returns:
            저장 성공 여부
        """
        try:
            # 디렉토리가 없으면 생성
            self.config_path.parent.mkdir(parents=True, exist_ok=True)

            # 설정 유효성 검사
            validated_settings = self._validate_settings(settings)

            with open(self.config_path, "w", encoding="utf-8") as f:
                json.dump(validated_settings, f, ensure_ascii=False, indent=2)

            self.logger.info(f"설정 저장 성공: {self.config_path}")
            return True

        except Exception as e:
            self.logger.error(f"설정 저장 실패: {str(e)}")
            return False

    def _merge_settings(
        self, default: Dict[str, Any], loaded: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        기본 설정과 로드된 설정을 병합합니다.
        새로운 설정 키가 추가되었을 때 기본값을 유지하면서 사용자 설정을 보존합니다.
        """
        result = default.copy()

        for key, value in loaded.items():
            if key in result:
                if isinstance(value, dict) and isinstance(result[key], dict):
                    # 중첩된 딕셔너리는 재귀적으로 병합
                    result[key] = self._merge_settings(result[key], value)
                else:
                    result[key] = value
            else:
                # 새로운 키는 그대로 추가
                result[key] = value

        return result

    def _validate_settings(self, settings: Dict[str, Any]) -> Dict[str, Any]:
        """
        설정값의 유효성을 검사하고 잘못된 값을 기본값으로 대체합니다.
        """
        validated = settings.copy()

        try:
            # 경로 유효성 검사
            if "last_save_path" in validated:
                save_path = Path(validated["last_save_path"])
                if not save_path.exists() or not save_path.is_dir():
                    validated["last_save_path"] = self.default_settings[
                        "last_save_path"
                    ]

            # 변형 옵션 유효성 검사
            if "transform_options" in validated:
                transform_opts = validated["transform_options"]
                default_transform = self.default_settings["transform_options"]

                for key, default_value in default_transform.items():
                    if key not in transform_opts or not isinstance(
                        transform_opts[key], bool
                    ):
                        transform_opts[key] = default_value

            # UI 설정 유효성 검사
            if "ui_settings" in validated:
                ui_opts = validated["ui_settings"]
                default_ui = self.default_settings["ui_settings"]

                for key, default_value in default_ui.items():
                    if key not in ui_opts:
                        ui_opts[key] = default_value
                    elif key == "progress_update_interval":
                        # 범위 제한 (50-1000ms)
                        ui_opts[key] = max(50, min(1000, ui_opts[key]))
                    elif key == "log_max_length":
                        # 범위 제한 (10-50자)
                        ui_opts[key] = max(10, min(50, ui_opts[key]))

        except Exception as e:
            self.logger.warning(f"설정 유효성 검사 중 오류: {str(e)}")

        return validated

    def get_current_directory(self) -> str:
        """
        현재 실행 디렉토리를 반환합니다.

        Returns:
            현재 디렉토리 경로 문자열
        """
        try:
            # PyInstaller 환경 고려
            import sys

            if getattr(sys, "frozen", False):
                # 실행 파일이 있는 디렉토리
                return str(Path(sys.executable).parent)
            else:
                # 개발 환경
                return str(Path.cwd())
        except Exception:
            return str(Path.home())

    def update_last_save_path(self, path: str) -> None:
        """
        마지막 저장 경로를 업데이트하고 설정을 저장합니다.

        Args:
            path: 새로운 저장 경로
        """
        try:
            settings = self.load_settings()
            settings["last_save_path"] = str(Path(path).absolute())
            self.save_settings(settings)
        except Exception as e:
            self.logger.error(f"마지막 저장 경로 업데이트 실패: {str(e)}")

    def update_transform_options(self, options: Dict[str, bool]) -> None:
        """
        이미지 변형 옵션을 업데이트하고 설정을 저장합니다.

        Args:
            options: 변형 옵션 딕셔너리
        """
        try:
            settings = self.load_settings()
            settings["transform_options"].update(options)
            self.save_settings(settings)
        except Exception as e:
            self.logger.error(f"변형 옵션 업데이트 실패: {str(e)}")

    def get_config_path(self) -> Path:
        """설정 파일 경로를 반환합니다."""
        return self.config_path

    def reset_to_defaults(self) -> bool:
        """
        설정을 기본값으로 초기화합니다.

        Returns:
            초기화 성공 여부
        """
        try:
            return self.save_settings(self.default_settings.copy())
        except Exception as e:
            self.logger.error(f"설정 초기화 실패: {str(e)}")
            return False
