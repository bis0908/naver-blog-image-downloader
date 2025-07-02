#!/usr/bin/env python3
"""
네이버 블로그 이미지 다운로더 CLI
애플리케이션의 메인 진입점입니다.
"""

import os
from pathlib import Path
from scraper.scraper import NaverBlogScraper
from downloader import ImageDownloader
from utils.utils import get_user_input, print_success, print_error


def _clear_terminal():
    """터미널 화면을 초기화합니다."""
    os.system("cls" if os.name == "nt" else "clear")


def _ask_continue() -> bool:
    """재작업 여부를 묻고 사용자 선택을 반환합니다."""
    print("\n" + "=" * 50)
    while True:
        choice = (
            input("다른 블로그 포스팅을 다운로드하시겠습니까? (y/n): ").strip().lower()
        )
        if choice in ["y", "yes"]:
            return True
        elif choice in ["n", "no"]:
            return False
        else:
            print("y 또는 n을 입력해주세요.")


def _run_download_process():
    """단일 다운로드 프로세스를 실행합니다."""
    try:
        # 사용자 입력 받기
        url = get_user_input(
            "네이버 블로그 URL을 입력하세요 (예: https://blog.naver.com/블로그id/포스팅번호)\n입력: "
        ).strip()
        if not url:
            print_error("URL은 비어있을 수 없습니다.")
            return

        save_path = get_user_input(
            "이미지 저장 경로를 입력하세요 (예: C:\\Users\\pc\\OneDrive\\photos)\n입력: "
        ).strip()
        if not save_path:
            print_error("저장 경로는 비어있을 수 없습니다.")
            return

        # 기본 저장 디렉토리 유효성 검사 및 생성
        base_save_dir = Path(save_path)
        base_save_dir.mkdir(parents=True, exist_ok=True)

        print(f"\n처리 중인 URL: {url}")
        print(f"기본 저장 디렉토리: {base_save_dir.absolute()}\n")

        # 스크래퍼 인스턴스 생성
        scraper = NaverBlogScraper()

        # 포스팅 제목 추출 및 폴더 생성
        post_title = scraper.extract_post_title(url)
        final_save_dir = base_save_dir / post_title
        final_save_dir.mkdir(parents=True, exist_ok=True)

        print(f"최종 저장 디렉토리: {final_save_dir.absolute()}\n")

        # 블로그에서 이미지 스크래핑
        image_urls = scraper.extract_image_urls(url)

        if not image_urls:
            print_error("지정된 클래스에서 이미지를 찾을 수 없습니다.")
            return

        print(f"다운로드할 {len(image_urls)}개의 이미지를 발견했습니다.\n")

        # 이미지 다운로드 (제목 폴더에 저장)
        with ImageDownloader(final_save_dir) as downloader:
            successful_downloads = downloader.download_images(image_urls)

        # 결과 보고
        if successful_downloads == len(image_urls):
            print_success(
                f"모든 {successful_downloads}개의 이미지를 성공적으로 다운로드했습니다!"
            )
            print_success(f"저장 위치: {final_save_dir.absolute()}")
        elif successful_downloads > 0:
            print_success(
                f"{len(image_urls)}개 중 {successful_downloads}개의 이미지를 다운로드했습니다."
            )
            print_success(f"저장 위치: {final_save_dir.absolute()}")
            print_error(
                f"{len(image_urls) - successful_downloads}개의 이미지 다운로드에 실패했습니다."
            )
        else:
            print_error("이미지 다운로드에 실패했습니다.")

    except KeyboardInterrupt:
        print("\n\n사용자에 의해 작업이 취소되었습니다.")
    except Exception as e:
        print_error(f"예상치 못한 오류가 발생했습니다: {str(e)}")


def main():
    """메인 CLI 애플리케이션 로직입니다."""
    _clear_terminal()

    while True:
        print("=== 네이버 블로그 이미지 다운로더 ===\n")

        # 다운로드 프로세스 실행
        _run_download_process()

        # 재작업 여부 확인
        if not _ask_continue():
            break

        # 터미널 초기화 후 재시작
        _clear_terminal()

    # 프로그램 종료 메시지
    print("\n" + "=" * 50)
    print("프로그램을 종료합니다.")


if __name__ == "__main__":
    main()
