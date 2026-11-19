
"""
Mini NPU Simulator
프로그램 실행 및 사용자 메뉴 관리
"""

from mini_npu_simulator import MiniNPUSimulator


def main():
    """프로그램 실행 진입점"""

    # 시뮬레이터 객체 생성
    simulator = MiniNPUSimulator()

    while True:
        print("\n===================================")
        print("       Mini NPU Simulator")
        print("===================================")
        print("1. 수동 입력 모드")
        print("2. JSON 자동 분석 모드")
        print("0. 프로그램 종료")
        print("===================================")

        try:
            menu = input("메뉴를 선택하세요: ").strip()

            if menu == "1":
                print("\n[수동 입력 모드]")
                simulator.run_manual_mode()

            elif menu == "2":
                print("\n[JSON 자동 분석 모드]")
                simulator.run_json_test_mode()

            elif menu == "0":
                print("\n프로그램을 종료합니다.")
                break

            else:
                print("\n잘못된 메뉴입니다. 다시 선택해주세요.")

        except KeyboardInterrupt:
            print("\n\n사용자 요청으로 프로그램을 종료합니다.")
            break

        except Exception as e:
            print(f"\n오류가 발생했습니다: {e}")


if __name__ == "__main__":
    main()
