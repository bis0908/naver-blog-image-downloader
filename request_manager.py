"""
네트워크 요청 관리를 위한 공통 유틸리티 모듈입니다.
정적 User-Agent 목록을 사용하여 외부 라이브러리 의존성을 제거했습니다.
"""

import time
import random
import requests
from typing import Dict, Any, Optional
from utils.utils import print_info, print_warning, print_error


class StaticRequestManager:
    """
    정적 User-Agent 목록을 사용하는 네트워크 요청 관리자입니다.
    외부 라이브러리에 의존하지 않아 exe 패키징에서 안정적으로 작동합니다.
    """

    def __init__(
        self,
        min_delay: float = 1.0,
        max_delay: float = 3.0,
        max_retries: int = 3,
        session_reset_interval: int = 10,
    ):
        """
        StaticRequestManager 초기화

        Args:
            min_delay: 최소 요청 간격 (초)
            max_delay: 최대 요청 간격 (초)
            max_retries: 최대 재시도 횟수
            session_reset_interval: 세션 초기화 간격 (요청 수)
        """
        self.min_delay = min_delay
        self.max_delay = max_delay
        self.max_retries = max_retries
        self.session_reset_interval = session_reset_interval

        # 정적 User-Agent 목록 (2024년 최신 브라우저 기준)
        self.user_agents = [
            # Chrome Windows
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
            # Chrome Mac
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
            # Chrome Linux
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
            # Firefox Windows
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:119.0) Gecko/20100101 Firefox/119.0",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
            # Firefox Mac
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:120.0) Gecko/20100101 Firefox/120.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:119.0) Gecko/20100101 Firefox/119.0",
            # Firefox Linux
            "Mozilla/5.0 (X11; Linux x86_64; rv:120.0) Gecko/20100101 Firefox/120.0",
            "Mozilla/5.0 (X11; Linux x86_64; rv:119.0) Gecko/20100101 Firefox/119.0",
            # Safari Mac
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Safari/605.1.15",
            # Edge Windows
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36 Edg/119.0.0.0",
            # Edge Mac
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0",
        ]

        # 세션 관리
        self.session = None
        self.request_count = 0
        self.last_request_time = 0

        # 세션 초기화
        self._reset_session()
        print_info("StaticRequestManager 초기화 완료 (정적 User-Agent 사용)")

    def _reset_session(self) -> None:
        """새로운 세션을 생성하고 헤더를 설정합니다."""
        if self.session:
            self.session.close()

        self.session = requests.Session()
        self.request_count = 0
        self._rotate_user_agent()
        print_info("새로운 세션이 생성되었습니다")

    def _rotate_user_agent(self) -> None:
        """User-Agent와 관련 헤더들을 로테이션합니다."""
        try:
            # 정적 목록에서 랜덤 선택
            user_agent = random.choice(self.user_agents)

            # 기본 헤더 설정
            headers = {
                "User-Agent": user_agent,
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
                "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7",
                "Accept-Encoding": "gzip, deflate, br",
                "DNT": "1",
                "Connection": "keep-alive",
                "Upgrade-Insecure-Requests": "1",
                "Sec-Fetch-Dest": "document",
                "Sec-Fetch-Mode": "navigate",
                "Sec-Fetch-Site": "none",
                "Cache-Control": "max-age=0",
            }

            self.session.headers.update(headers)
            print_info(f"User-Agent 로테이션 완료: {user_agent[:80]}...")

        except Exception as e:
            print_warning(f"User-Agent 로테이션 실패, 기본값 사용: {str(e)}")
            # 최종 폴백 User-Agent
            fallback_ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            self.session.headers.update({"User-Agent": fallback_ua})

    def _apply_delay(self) -> None:
        """요청 간격을 적용합니다."""
        current_time = time.time()
        elapsed = current_time - self.last_request_time

        delay = random.uniform(self.min_delay, self.max_delay)

        if elapsed < delay:
            sleep_time = delay - elapsed
            print_info(f"요청 간격 적용: {sleep_time:.2f}초 대기")
            time.sleep(sleep_time)

        self.last_request_time = time.time()

    def _exponential_backoff(self, attempt: int) -> float:
        """지수 백오프 딜레이를 계산합니다."""
        base_delay = 2**attempt
        jitter = random.uniform(0.1, 0.3)
        return base_delay + jitter

    def get(self, url: str, **kwargs) -> requests.Response:
        """
        GET 요청을 안전하게 수행합니다.

        Args:
            url: 요청할 URL
            **kwargs: requests.get에 전달할 추가 인수

        Returns:
            Response 객체

        Raises:
            requests.RequestException: 모든 재시도가 실패한 경우
        """
        return self._make_request("GET", url, **kwargs)

    def _make_request(self, method: str, url: str, **kwargs) -> requests.Response:
        """
        실제 요청을 수행합니다. 재시도 로직과 딜레이가 포함됩니다.

        Args:
            method: HTTP 메서드
            url: 요청할 URL
            **kwargs: 요청에 전달할 추가 인수

        Returns:
            Response 객체
        """
        # 세션 초기화 확인
        if self.request_count >= self.session_reset_interval:
            self._reset_session()

        last_exception = None

        for attempt in range(self.max_retries):
            try:
                # 요청 간격 적용
                self._apply_delay()

                # 매 요청마다 User-Agent 로테이션 (선택적)
                if self.request_count % 3 == 0:  # 3요청마다 로테이션
                    self._rotate_user_agent()

                # 요청 수행
                print_info(f"요청 시도 {attempt + 1}/{self.max_retries}: {url}")

                response = self.session.request(method, url, **kwargs)
                response.raise_for_status()

                self.request_count += 1
                print_info(f"요청 성공: {response.status_code}")

                return response

            except requests.exceptions.RequestException as e:
                last_exception = e
                print_warning(
                    f"요청 실패 (시도 {attempt + 1}/{self.max_retries}): {str(e)}"
                )

                if attempt < self.max_retries - 1:
                    # 지수 백오프 적용
                    backoff_delay = self._exponential_backoff(attempt)
                    print_info(f"재시도 전 대기: {backoff_delay:.2f}초")
                    time.sleep(backoff_delay)

                    # User-Agent 로테이션 (실패 시)
                    self._rotate_user_agent()

        # 모든 재시도 실패
        print_error(f"모든 요청 시도 실패: {url}")
        raise last_exception

    def close(self) -> None:
        """세션을 닫습니다."""
        if self.session:
            self.session.close()
            print_info("StaticRequestManager 세션이 종료되었습니다")

    def __enter__(self):
        """컨텍스트 매니저 진입"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """컨텍스트 매니저 종료"""
        self.close()


class NaverStaticRequestManager(StaticRequestManager):
    """
    네이버 특화 정적 요청 매니저입니다.
    네이버 서비스에 최적화된 헤더와 설정을 제공합니다.
    """

    def __init__(self, **kwargs):
        # 네이버 특화 설정
        kwargs.setdefault("min_delay", 2.0)  # 더 긴 딜레이
        kwargs.setdefault("max_delay", 5.0)
        kwargs.setdefault("max_retries", 3)
        kwargs.setdefault("session_reset_interval", 5)  # 더 자주 세션 초기화

        super().__init__(**kwargs)
        print_info("NaverStaticRequestManager 초기화 완료")

    def _rotate_user_agent(self) -> None:
        """네이버 최적화된 헤더를 설정합니다."""
        try:
            # 정적 목록에서 랜덤 선택
            user_agent = random.choice(self.user_agents)

            # 네이버 특화 헤더
            headers = {
                "User-Agent": user_agent,
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
                "Accept-Language": "ko-KR,ko;q=0.9",
                "Accept-Encoding": "gzip, deflate, br",
                "Cache-Control": "no-cache",
                "Pragma": "no-cache",
                "DNT": "1",
                "Connection": "keep-alive",
                "Upgrade-Insecure-Requests": "1",
                "Sec-Ch-Ua-Mobile": "?0",
                "Sec-Ch-Ua-Platform": '"Windows"',
                "Sec-Fetch-Dest": "iframe",
                "Sec-Fetch-Mode": "navigate",
                "Sec-Fetch-Site": "same-origin",
            }

            self.session.headers.update(headers)
            print_info(f"네이버 특화 User-Agent 설정: {user_agent[:80]}...")

        except Exception as e:
            print_warning(f"네이버 User-Agent 설정 실패: {str(e)}")
            super()._rotate_user_agent()


# 기존 클래스들과의 호환성을 위한 별칭
RequestManager = StaticRequestManager
NaverRequestManager = NaverStaticRequestManager
