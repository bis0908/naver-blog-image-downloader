#!/usr/bin/env python3
"""
네이버 블로그 이미지 다운로더 UI 버전
GUI 기반의 이미지 다운로드 및 변형 애플리케이션입니다.
"""

import sys
import logging
from pathlib import Path
from typing import Dict, Any

from PySide6.QtWidgets import QApplication, QDialog, QFileDialog, QMessageBox
from PySide6.QtCore import QTimer, Signal, QObject, QMetaObject, Qt
from PySide6.QtGui import QIcon

from ui.untitled_ui import Ui_N_image_downloader_and_image_transformer
from core import UIController, AppSettings


class MainWindow(QDialog):
    """메인 윈도우 클래스"""

    # 스레드 안전 UI 업데이트를 위한 시그널
    progress_updated = Signal(int)
    log_updated = Signal(str)
    buttons_state_updated = Signal(bool, bool, bool)

    def __init__(self):
        super().__init__()

        # UI 설정
        self.ui = Ui_N_image_downloader_and_image_transformer()
        self.ui.setupUi(self)

        # 윈도우 설정
        self.setWindowTitle("네이버 블로그 이미지 다운로더")
        self.setFixedSize(538, 292)  # 고정 크기

        # 핵심 컴포넌트 초기화
        self.controller = UIController(
            progress_callback=self._safe_update_progress,
            log_callback=self._safe_update_log,
            enable_buttons_callback=self._safe_set_buttons_enabled,
        )

        # 로깅 설정
        self._setup_logging()

        # 스레드 안전 시그널 연결
        self._connect_signals()

        # UI 초기화
        self._initialize_ui()

        # 이벤트 연결
        self._connect_events()

        # 타이머 설정 (진행률 업데이트용)
        self.progress_timer = QTimer()
        self.progress_timer.timeout.connect(self._update_ui_state)
        self.progress_timer.setSingleShot(False)  # 반복 실행

    def _setup_logging(self):
        """로깅 설정을 초기화합니다."""
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            handlers=[
                logging.FileHandler("app.log", encoding="utf-8"),
                logging.StreamHandler(sys.stdout),
            ],
        )
        self.logger = logging.getLogger(__name__)

    def _connect_signals(self):
        """스레드 안전 시그널들을 연결합니다."""
        self.progress_updated.connect(
            self._update_progress_bar, Qt.ConnectionType.QueuedConnection
        )
        self.log_updated.connect(
            self._update_log_text, Qt.ConnectionType.QueuedConnection
        )
        self.buttons_state_updated.connect(
            self._update_buttons_state, Qt.ConnectionType.QueuedConnection
        )

    def _initialize_ui(self):
        """UI 초기 상태를 설정합니다."""
        try:
            # 컨트롤러에서 초기 설정 로드
            init_settings = self.controller.initialize_ui()

            # 저장 경로 설정 (현재 디렉토리를 기본값으로)
            current_dir = init_settings.get("current_directory", str(Path.cwd()))
            self.ui.dir_path.setText(current_dir)

            # 이미지 변형 옵션 설정
            transform_options = init_settings.get("transform_options", {})
            self.ui.is_random_size.setChecked(
                transform_options.get("random_size", True)
            )
            self.ui.is_random_angle.setChecked(
                transform_options.get("random_angle", True)
            )
            self.ui.is_random_pixel.setChecked(
                transform_options.get("random_pixel", True)
            )
            self.ui.is_add_outline.setChecked(
                transform_options.get("add_outline", True)
            )

            # 프로그레스바 초기화
            self.ui.progressBar.setValue(0)
            self.ui.progressBar.setVisible(True)

            # 로그 초기화
            self.ui.simple_log.setText("준비 완료")

            # 버튼 상태 초기화
            self.set_buttons_enabled(
                True, False, True
            )  # download=True, cancel=False, close=True

        except Exception as e:
            self.logger.error(f"UI 초기화 실패: {str(e)}")
            self.ui.simple_log.setText("초기화 오류")

    def _connect_events(self):
        """UI 이벤트를 연결합니다."""
        try:
            # 버튼 이벤트 연결
            self.ui.buttonBox.button(
                self.ui.buttonBox.StandardButton.Yes
            ).clicked.connect(self._on_download_clicked)
            self.ui.buttonBox.button(
                self.ui.buttonBox.StandardButton.Cancel
            ).clicked.connect(self._on_cancel_clicked)
            self.ui.buttonBox.button(
                self.ui.buttonBox.StandardButton.Close
            ).clicked.connect(self._on_close_clicked)

            # 폴더 선택 버튼
            self.ui.load_dir.clicked.connect(self._on_folder_select_clicked)

            # 버튼 텍스트 변경
            self.ui.buttonBox.button(self.ui.buttonBox.StandardButton.Yes).setText(
                "다운로드"
            )

        except Exception as e:
            self.logger.error(f"이벤트 연결 실패: {str(e)}")

    def _on_download_clicked(self):
        """다운로드 버튼 클릭 이벤트"""
        try:
            # 입력값 수집
            url = self.ui.url_input.text().strip()
            save_path = self.ui.dir_path.text().strip()

            # 변형 옵션 수집
            transform_options = {
                "random_size": self.ui.is_random_size.isChecked(),
                "random_angle": self.ui.is_random_angle.isChecked(),
                "random_pixel": self.ui.is_random_pixel.isChecked(),
                "add_outline": self.ui.is_add_outline.isChecked(),
            }

            # 컨트롤러를 통해 다운로드 시작
            self.controller.start_download_process(url, save_path, transform_options)

            # UI 업데이트 타이머 시작
            self.progress_timer.start(200)  # 200ms마다 업데이트 (QPainter 오류 방지)

        except Exception as e:
            self.logger.error(f"다운로드 시작 실패: {str(e)}")
            self.update_log("다운로드 시작 실패")

    def _on_cancel_clicked(self):
        """취소 버튼 클릭 이벤트"""
        try:
            self.controller.cancel_process()
            self.progress_timer.stop()

        except Exception as e:
            self.logger.error(f"취소 처리 실패: {str(e)}")

    def _on_close_clicked(self):
        """닫기 버튼 클릭 이벤트"""
        try:
            # 진행 중인 작업이 있으면 확인
            if self.controller.is_processing():
                reply = QMessageBox.question(
                    self,
                    "확인",
                    "작업이 진행 중입니다. 정말 종료하시겠습니까?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                    QMessageBox.StandardButton.No,
                )

                if reply == QMessageBox.StandardButton.Yes:
                    self.controller.cancel_process()
                    self.close()
            else:
                self.close()

        except Exception as e:
            self.logger.error(f"종료 처리 실패: {str(e)}")
            self.close()

    def _on_folder_select_clicked(self):
        """폴더 선택 버튼 클릭 이벤트"""
        try:
            # 현재 경로를 기본값으로 설정
            current_path = self.ui.dir_path.text().strip()
            if not current_path or not Path(current_path).exists():
                current_path = self.controller.get_save_directory_suggestion()

            # 폴더 선택 다이얼로그
            selected_dir = QFileDialog.getExistingDirectory(
                self, "저장 폴더 선택", current_path, QFileDialog.Option.ShowDirsOnly
            )

            if selected_dir:
                self.ui.dir_path.setText(selected_dir)

        except Exception as e:
            self.logger.error(f"폴더 선택 실패: {str(e)}")

    # 스레드 안전 콜백 함수들
    def _safe_update_progress(self, value: int):
        """스레드 안전 프로그레스 업데이트"""
        self.progress_updated.emit(value)

    def _safe_update_log(self, message: str):
        """스레드 안전 로그 업데이트"""
        self.log_updated.emit(message)

    def _safe_set_buttons_enabled(self, download: bool, cancel: bool, close: bool):
        """스레드 안전 버튼 상태 업데이트"""
        self.buttons_state_updated.emit(download, cancel, close)

    # 실제 UI 업데이트 함수들 (메인 스레드에서만 실행)
    def _update_progress_bar(self, value: int):
        """프로그레스바를 업데이트합니다."""
        try:
            # 범위 제한 (0-100)
            value = max(0, min(100, value))
            self.ui.progressBar.setValue(value)
            # 강제 갱신
            self.ui.progressBar.repaint()

        except Exception as e:
            self.logger.error(f"프로그레스 업데이트 실패: {str(e)}")

    def _update_log_text(self, message: str):
        """로그 메시지를 업데이트합니다."""
        try:
            # 20자 제한 적용
            truncated_message = self.controller.truncate_log_message(message, 20)
            self.ui.simple_log.setText(truncated_message)
            # 강제 갱신
            self.ui.simple_log.repaint()

            # 콘솔에도 전체 메시지 출력
            self.logger.info(f"UI Log: {message}")

        except Exception as e:
            self.logger.error(f"로그 업데이트 실패: {str(e)}")

    def _update_buttons_state(self, download: bool, cancel: bool, close: bool):
        """버튼 활성화 상태를 설정합니다."""
        try:
            self.ui.buttonBox.button(self.ui.buttonBox.StandardButton.Yes).setEnabled(
                download
            )
            self.ui.buttonBox.button(
                self.ui.buttonBox.StandardButton.Cancel
            ).setEnabled(cancel)
            self.ui.buttonBox.button(self.ui.buttonBox.StandardButton.Close).setEnabled(
                close
            )

        except Exception as e:
            self.logger.error(f"버튼 상태 업데이트 실패: {str(e)}")

    # 호환성을 위한 기존 함수들 (deprecated)
    def update_progress(self, value: int):
        """프로그레스바를 업데이트합니다. (호환성용)"""
        self._safe_update_progress(value)

    def update_log(self, message: str):
        """로그 메시지를 업데이트합니다. (호환성용)"""
        self._safe_update_log(message)

    def set_buttons_enabled(self, download: bool, cancel: bool, close: bool):
        """버튼 활성화 상태를 설정합니다. (호환성용)"""
        self._safe_set_buttons_enabled(download, cancel, close)

    def _update_ui_state(self):
        """UI 상태를 주기적으로 업데이트합니다."""
        try:
            # 작업이 완료되면 타이머 중지
            if not self.controller.is_processing():
                self.progress_timer.stop()

        except Exception as e:
            self.logger.error(f"UI 상태 업데이트 실패: {str(e)}")

    def closeEvent(self, event):
        """윈도우 종료 이벤트 처리"""
        try:
            # 진행 중인 작업 정리
            if self.controller.is_processing():
                self.controller.cancel_process()
                # 잠시 대기하여 정리 작업 완료
                import time

                time.sleep(0.5)

            # 타이머 정리
            if self.progress_timer.isActive():
                self.progress_timer.stop()

            event.accept()

        except Exception as e:
            self.logger.error(f"종료 처리 실패: {str(e)}")
            event.accept()


def main():
    """메인 애플리케이션 실행 함수"""
    try:
        # QApplication 초기화
        app = QApplication(sys.argv)

        # 애플리케이션 정보 설정
        app.setApplicationName("네이버 블로그 이미지 다운로더")
        app.setApplicationVersion("2.0.0")
        app.setOrganizationName("NaverBlogImageDownloader")

        # 아이콘 설정 (선택사항)
        # app.setWindowIcon(QIcon("icon.png"))

        # 메인 윈도우 생성 및 표시
        window = MainWindow()
        window.show()

        # 이벤트 루프 시작
        sys.exit(app.exec())

    except Exception as e:
        print(f"애플리케이션 시작 실패: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
