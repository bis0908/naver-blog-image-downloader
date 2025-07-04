"""
transformer.py와 batch_processor.py 테스트 모듈
test_image 폴더에서 랜덤 이미지를 선택하여 변형 처리를 테스트합니다.
"""

import random
import sys
import time
from pathlib import Path
from typing import List

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from image_processor.batch_processor import StreamingImageProcessor


class TransformerTester:
    """Transformer 테스트 클래스"""

    def __init__(self):
        self.test_image_dir = Path(__file__).parent / "test_image"
        self.output_dir = Path(__file__).parent / "test_output"
        self.output_dir.mkdir(exist_ok=True)

        # 테스트 상태
        self.is_cancelled = False

    def progress_callback(self, progress: int, message: str) -> None:
        """진행률 업데이트 콜백"""
        print(f"진행률: {progress}% - {message}")

    def cancel_callback(self) -> bool:
        """취소 상태 확인 콜백"""
        return self.is_cancelled

    def log_callback(self, message: str) -> None:
        """로그 메시지 콜백"""
        print(f"[LOG] {message}")

    def get_test_images(self) -> List[Path]:
        """테스트 이미지 파일 목록을 가져옵니다."""
        image_extensions = {".jpg", ".jpeg", ".png", ".bmp", ".tiff"}
        image_files = []

        for file_path in self.test_image_dir.glob("*"):
            if file_path.is_file() and file_path.suffix.lower() in image_extensions:
                image_files.append(file_path)

        return sorted(image_files)

    def test_single_image_transform(self):
        """단일 이미지 변형 테스트"""
        print("=" * 60)
        print("단일 이미지 변형 테스트 시작")
        print("=" * 60)

        # 1. 테스트 이미지 목록 가져오기
        available_images = self.get_test_images()

        if not available_images:
            print("❌ 테스트 이미지가 없습니다!")
            return False

        print(f"📁 사용 가능한 이미지: {len(available_images)}개")
        for img in available_images:
            print(f"   - {img.name}")

        # 2. 랜덤으로 메인 이미지 선택
        main_image = random.choice(available_images)
        print(f"\n🎯 선택된 메인 이미지: {main_image.name}")

        # 3. 모든 변형 옵션 활성화
        transform_options = {
            "random_size": True,  # 랜덤 크기 조정 (±5%)
            "random_angle": True,  # 랜덤 기울기 (±3도)
            "random_pixel": True,  # 랜덤 픽셀 추가 (3~5개)
            "add_outline": True,  # 테두리 추가
        }

        print("\n🔧 변형 옵션:")
        for option, enabled in transform_options.items():
            print(f"   - {option}: {'✅' if enabled else '❌'}")

        # 4. StreamingImageProcessor로 처리
        processor = StreamingImageProcessor(
            progress_callback=self.progress_callback,
            cancel_callback=self.cancel_callback,
            log_callback=self.log_callback,
        )

        print(f"\n🚀 이미지 처리 시작...")
        print(f"   입력: {main_image}")
        print(f"   출력: {self.output_dir}")

        start_time = time.time()

        try:
            # 메인 이미지만 처리 (배경용으로 다른 이미지들도 available로 전달)
            result = processor.process_images_streaming(
                image_paths=[main_image],
                output_dir=self.output_dir,
                transform_options=transform_options,
                base_progress=0,
            )

            end_time = time.time()
            processing_time = end_time - start_time

            # 결과 출력
            print(f"\n📊 처리 결과:")
            print(f"   처리 시간: {processing_time:.2f}초")
            print(f"   성공: {result['success_count']}개")
            print(f"   실패: {result['fail_count']}개")
            print(f"   취소됨: {'예' if result['cancelled'] else '아니오'}")

            if result["failed_files"]:
                print(f"   실패한 파일:")
                for failed_file in result["failed_files"]:
                    print(f"     - {failed_file}")

            # 출력 파일 확인
            output_files = list(self.output_dir.glob("*"))
            print(f"\n📁 생성된 파일: {len(output_files)}개")
            for output_file in output_files:
                file_size = output_file.stat().st_size / (1024 * 1024)  # MB
                print(f"   - {output_file.name} ({file_size:.2f}MB)")

            return result["success_count"] > 0

        except Exception as e:
            print(f"❌ 처리 중 오류 발생: {str(e)}")
            return False


def main():
    """메인 테스트 함수"""
    tester = TransformerTester()

    try:
        print("🧪 단일 이미지 변형 테스트 시작")
        print(f"📁 테스트 이미지 디렉토리: {tester.test_image_dir}")
        print(f"📁 출력 디렉토리: {tester.output_dir}")

        success = tester.test_single_image_transform()

        if success:
            print("\n🎉 테스트가 성공적으로 완료되었습니다!")
            return 0
        else:
            print("\n⚠️  테스트가 실패했습니다.")
            return 1

    except KeyboardInterrupt:
        print("\n🛑 사용자에 의해 테스트가 중단되었습니다.")
        return 2
    except Exception as e:
        print(f"\n💥 예상치 못한 오류가 발생했습니다: {str(e)}")
        return 3


if __name__ == "__main__":
    exit(main())
