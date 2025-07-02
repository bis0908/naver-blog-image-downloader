"""
네이버 블로그 이미지 다운로더를 위한 유틸리티 함수들입니다.
"""

import sys


def get_user_input(prompt: str) -> str:
    """
    주어진 프롬프트로 사용자 입력을 받습니다.
    
    Args:
        prompt: 사용자에게 표시할 프롬프트
        
    Returns:
        문자열로 된 사용자 입력
    """
    try:
        return input(prompt)
    except (EOFError, KeyboardInterrupt):
        print("\n사용자에 의해 작업이 취소되었습니다.")
        sys.exit(0)


def print_success(message: str) -> None:
    """성공 메시지를 녹색으로 출력합니다."""
    print(f"✓ {message}")


def print_error(message: str) -> None:
    """오류 메시지를 빨간색으로 출력합니다."""
    print(f"✗ 오류: {message}", file=sys.stderr)


def print_info(message: str) -> None:
    """정보 메시지를 출력합니다."""
    print(f"ℹ {message}")


def print_warning(message: str) -> None:
    """경고 메시지를 출력합니다."""
    print(f"⚠ 경고: {message}")