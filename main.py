def main():

    # 인스턴스 생성하기

    try:
        # 인스턴스 실행하기
        # 오류 방지를 위한 임의 코드(완성후 삭제)
        1 + 1

    except KeyboardInterrupt:
        print("\n사용자 요청으로 프로그램을 종료합니다.")

    except EOFError:
        print("\n입력이 종료되어 프로그램을 종료합니다.")

    finally:
        # 인스턴스 실행중 오류 발생시 대처방안
        # 오류 방지를 위한 임의 코드(완성후 삭제)
        1 + 1


if __name__ == "__main__":
    """ 
    해당 파일이 직접 실행될때만 main 함수가 작동하도록 처리
    다른 파일에서 import 해도 해당 함수는 실행되지 않음
    """
    main()